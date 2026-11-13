#!/usr/bin/env python3
"""Collect public default-branch history for the homepage. Standard library only."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
COAUTHOR = re.compile(r'^Co-authored-by:\s*(.+?)\s*<([^<>]+)>\s*$', re.I | re.M)
NOREPLY = re.compile(r'^(?:\d+\+)?([a-z0-9-]+)@users\.noreply\.github\.com$', re.I)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return parsed.astimezone(timezone.utc)


def fingerprint(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def validate_config(config):
    timestamp(config['since'])
    names = [item['repository'] for item in config['repositories']]
    if not names or len(set(names)) != len(names):
        raise ValueError('Configure at least one repository, without duplicates')
    for item in config['repositories']:
        if not re.fullmatch(r'[\w.-]+/[\w.-]+', item['repository']) or not item['branch']:
            raise ValueError('Each repository needs an owner/name and an explicit branch')
    for flag in ('include_merge_commits', 'exclude_bot_commits'):
        if not isinstance(config[flag], bool):
            raise ValueError(f'{flag} must be true or false')


class GitHub:
    def __init__(self, token=None):
        self.token = token

    def commits(self, repository, branch, since, until):
        for page in range(1, 10001):
            query = urlencode(dict(sha=branch, since=since, until=until, per_page=100, page=page))
            headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'openQSE-community-activity',
                       'X-GitHub-Api-Version': '2022-11-28'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
            request = Request(f'https://api.github.com/repos/{repository}/commits?{query}', headers=headers)
            try:
                with urlopen(request, timeout=30) as response:
                    records = json.load(response)
            except HTTPError as error:
                raise RuntimeError(f'GitHub returned HTTP {error.code} for {repository}; check access and rate limits') from None
            if not isinstance(records, list):
                raise ValueError(f'Unexpected commits response for {repository}')
            yield from records
            if len(records) < 100:
                return
        raise RuntimeError(f'Pagination limit reached for {repository}; snapshot was not replaced')


def identity(name, email, account, people):
    name, email = name or '', email or ''
    login = (account or {}).get('login')
    match = NOREPLY.fullmatch(email)
    if not login and match:
        login = match[1]
    if (account or {}).get('type') == 'Bot' or (login and login.lower().endswith('[bot]')):
        return None
    key = 'github:' + login.lower() if login else 'unlinked:' + hashlib.sha256((email.lower() or name).encode()).hexdigest()[:20]
    # Aliases are explicit: a display name alone is not proof that two authors
    # are the same person. No email addresses are published in the snapshot.
    for canonical, person in people.items():
        aliases = [alias.lower() for alias in person.get('aliases', [])]
        if key == canonical.lower() or email.lower() in aliases:
            key = canonical
            if key.startswith('github:'):
                login = key.removeprefix('github:')
            break
    override = people.get(key, {})
    if override.get('exclude'):
        return None
    return key, {
        'name': override.get('name') or name or login or 'Unlinked author',
        'login': login,
        'url': f'https://github.com/{login}' if login else None,
        'avatar_url': f'https://github.com/{login}.png?size=80' if login else None,
        'institution': override.get('institution'),
    }


def collect(config, github, now=None):
    validate_config(config)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    since = timestamp(config['since'])
    if since > now:
        raise ValueError('The starting date must not be in the future')
    until = now.isoformat(timespec='seconds').replace('+00:00', 'Z')
    first_day = now.date() - timedelta(days=55)
    recent_day = now.date() - timedelta(days=6)
    people = {}
    repositories = []
    for item in config['repositories']:
        count = recent = 0
        authors, seen = set(), set()
        weeks = [0] * 8
        for record in github.commits(item['repository'], item['branch'], config['since'], until):
            if record['sha'] in seen:
                continue
            seen.add(record['sha'])
            commit = record['commit']
            date = timestamp(commit['committer']['date'])
            if not since <= date <= now:
                continue
            if not config['include_merge_commits'] and len(record.get('parents', [])) > 1:
                continue
            account = record.get('author') or {}
            if config['exclude_bot_commits'] and (account.get('type') == 'Bot' or account.get('login', '').endswith('[bot]')):
                continue
            count += 1
            recent += date.date() >= recent_day
            day = (date.date() - first_day).days
            if 0 <= day < 56:
                weeks[day // 7] += 1
            primary = commit['author']
            credits = [(primary.get('name', ''), primary.get('email', ''), account)]
            credits += [(name, email, None) for name, email in COAUTHOR.findall(commit['message'])]
            credited, credited_emails = set(), set()
            for name, email, linked in credits:
                if email and email.lower() in credited_emails:
                    continue
                person = identity(name, email, linked, config.get('people', {}))
                if person is None or person[0] in credited:
                    continue
                key, details = person
                credited.add(key)
                if email:
                    credited_emails.add(email.lower())
                authors.add(key)
                if key not in people:
                    people[key] = dict(details, commits=0, repositories=set())
                people[key]['commits'] += 1
                people[key]['repositories'].add(item['repository'].split('/')[1])
        peak = max(weeks) or 1
        repositories.append(dict(
            name=item['repository'].split('/')[1], full_name=item['repository'],
            url=f'https://github.com/{item["repository"]}', branch=item['branch'],
            description=item.get('description', ''), commits=count, contributors=len(authors),
            commits_last_7_days=recent,
            activity=[{'count': number, 'height': round(number / peak * 32) + 2} for number in weeks]))
    contributors = [dict(person, repositories=sorted(person['repositories'])) for person in people.values()]
    contributors.sort(key=lambda person: (-person['commits'], person['name'].casefold()))
    return dict(schema_version=1, config_sha256=fingerprint(config), generated_at=until,
                since=config['since'], repositories=repositories, contributors=contributors,
                summary=dict(commits=sum(repo['commits'] for repo in repositories),
                             contributors=len(contributors), repositories=len(repositories),
                             commits_last_7_days=sum(repo['commits_last_7_days'] for repo in repositories)))


def validate_snapshot(snapshot, config):
    if snapshot.get('schema_version') != 1 or snapshot.get('config_sha256') != fingerprint(config):
        raise ValueError('Snapshot does not match the current community configuration; refresh it')
    timestamp(snapshot['generated_at'])
    if [repo['full_name'] for repo in snapshot['repositories']] != [repo['repository'] for repo in config['repositories']]:
        raise ValueError('Snapshot repository list does not match configuration')
    summary = snapshot['summary']
    for repo in snapshot['repositories']:
        for field in ('commits', 'contributors', 'commits_last_7_days'):
            if type(repo[field]) is not int or repo[field] < 0:
                raise ValueError('Snapshot contains an invalid count')
    if summary != dict(commits=sum(repo['commits'] for repo in snapshot['repositories']),
                       contributors=len(snapshot['contributors']), repositories=len(snapshot['repositories']),
                       commits_last_7_days=sum(repo['commits_last_7_days'] for repo in snapshot['repositories'])):
        raise ValueError('Snapshot totals are inconsistent')


def write_snapshot(path, snapshot):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(snapshot, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / '_data/community_activity_config.json')
    parser.add_argument('--output', type=Path, default=ROOT / '_data/community_activity.json')
    parser.add_argument('--check', action='store_true', help='Validate the checked-in snapshot without network access')
    parser.add_argument('--allow-stale', action='store_true', help='Keep a valid matching snapshot if GitHub is unavailable')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    validate_config(config)
    if args.check:
        validate_snapshot(json.loads(args.output.read_text()), config)
        print('PASS: community activity snapshot matches its configuration')
        return
    try:
        snapshot = collect(config, GitHub(os.environ.get('GITHUB_TOKEN')))
        validate_snapshot(snapshot, config)
    except (OSError, URLError, ValueError, RuntimeError) as error:
        if not args.allow_stale:
            raise
        cached = json.loads(args.output.read_text())
        validate_snapshot(cached, config)
        print(f'::warning::Community refresh failed ({error}); retaining snapshot from {cached["generated_at"]}', file=sys.stderr)
        return
    write_snapshot(args.output, snapshot)
    print(f'Updated {len(snapshot["repositories"])} repositories: {snapshot["summary"]["commits"]} commits')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f'ERROR: {error}') from None
