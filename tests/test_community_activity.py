"""Offline checks for counting, attribution, pagination, and snapshot retention."""
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('activity', ROOT / 'scripts/update_community_activity.py')
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
NOW = datetime(2026, 11, 13, 18, tzinfo=timezone.utc)


def commit(sha='one', name='Author', email='author@example.invalid', login='author',
           message='A change', date='2026-11-13T12:00:00Z', parents=1, kind='User'):
    return {'sha': sha, 'author': {'login': login, 'type': kind} if login else None,
            'parents': [{}] * parents,
            'commit': {'author': {'name': name, 'email': email},
                       'committer': {'date': date}, 'message': message}}


class FakeGitHub:
    def __init__(self, records):
        self.records = records
        self.requests = []

    def commits(self, *args):
        self.requests.append(args)
        return self.records


class CommunityActivityTests(unittest.TestCase):
    def setUp(self):
        self.config = {'since': '2026-07-01T00:00:00Z',
                       'include_merge_commits': True, 'exclude_bot_commits': False,
                       'repositories': [{'repository': 'openQSE/DEFw', 'branch': 'master'}],
                       'people': {'github:copilot': {'exclude': True}}}

    def test_coauthors_deduplicate_per_commit_and_never_publish_emails(self):
        records = [commit(message='Change\nCo-authored-by: Author <author@example.invalid>\n'
                         'Co-authored-by: Peer <12+peer@users.noreply.github.com>\n'
                         'Co-authored-by: Peer <12+peer@users.noreply.github.com>\n'
                         'Co-authored-by: Copilot <Copilot@users.noreply.github.com>')]
        client = FakeGitHub(records + records)
        snapshot = activity.collect(self.config, client, NOW)
        self.assertEqual(snapshot['summary']['commits'], 1)
        self.assertEqual(snapshot['summary']['contributors'], 2)
        self.assertEqual([p['commits'] for p in snapshot['contributors']], [1, 1])
        self.assertNotIn('example.invalid', json.dumps(snapshot))
        self.assertNotIn('Copilot', json.dumps(snapshot))
        self.assertEqual(client.requests[0][1], 'master')

    def test_dates_merge_and_bot_policies_are_explicit(self):
        records = [commit('old', date='2026-06-30T23:59:59Z'),
                   commit('future', date='2026-11-14T00:00:00Z'),
                   commit('merge', parents=2),
                   commit('bot', login='automation[bot]', kind='Bot'),
                   commit('regular')]
        snapshot = activity.collect(self.config, FakeGitHub(records), NOW)
        self.assertEqual(snapshot['summary']['commits'], 3)
        self.assertEqual(snapshot['summary']['contributors'], 1)
        self.config.update(include_merge_commits=False, exclude_bot_commits=True)
        snapshot = activity.collect(self.config, FakeGitHub(records), NOW)
        self.assertEqual(snapshot['summary']['commits'], 1)

    def test_cross_repository_people_are_unique_but_commit_totals_are_per_repo(self):
        self.config['repositories'].append({'repository': 'openQSE/QFw', 'branch': 'main'})
        snapshot = activity.collect(self.config, FakeGitHub([commit()]), NOW)
        self.assertEqual(snapshot['summary'], dict(commits=2, contributors=1,
                                                 repositories=2, commits_last_7_days=2))
        self.assertEqual(snapshot['contributors'][0]['repositories'], ['DEFw', 'QFw'])

    def test_recent_counts_and_weekly_chart_use_utc_commit_dates(self):
        records = [commit('today'), commit('six-days', date='2026-11-07T00:00:00Z'),
                   commit('seven-days', date='2026-11-06T23:59:59Z'),
                   commit('older', date='2026-07-01T00:00:00Z')]
        snapshot = activity.collect(self.config, FakeGitHub(records), NOW)
        self.assertEqual(snapshot['summary']['commits_last_7_days'], 2)
        self.assertEqual(sum(w['count'] for w in snapshot['repositories'][0]['activity']), 3)

    def test_aliases_are_explicit_and_affiliation_is_never_guessed(self):
        self.config['people']['github:author'] = {'name': 'Known Author', 'institution': 'Example Lab',
                                                 'aliases': ['second@example.invalid']}
        records = [commit(), commit('two', name='Different Name', email='second@example.invalid', login=None)]
        snapshot = activity.collect(self.config, FakeGitHub(records), NOW)
        person, = snapshot['contributors']
        self.assertEqual((person['name'], person['institution'], person['commits']), ('Known Author', 'Example Lab', 2))
        snapshot = activity.collect(self.config, FakeGitHub([commit(email='author@some-lab.invalid')]), NOW)
        self.assertEqual(snapshot['contributors'][0]['institution'], 'Example Lab')
        self.config['people'] = {}
        snapshot = activity.collect(self.config, FakeGitHub([commit(email='author@some-lab.invalid')]), NOW)
        self.assertIsNone(snapshot['contributors'][0]['institution'])

    def test_pagination_uses_explicit_branch_and_reads_all_pages(self):
        requests = []
        def fetch(request, timeout):
            requests.append(request.full_url)
            rows = [commit(str(i)) for i in range(100)] if len(requests) == 1 else [commit('last')]
            return io.BytesIO(json.dumps(rows).encode())
        with patch.object(activity, 'urlopen', fetch):
            rows = list(activity.GitHub().commits('openQSE/DEFw', 'master', self.config['since'], NOW.isoformat()))
        self.assertEqual(len(rows), 101)
        self.assertIn('sha=master', requests[0])
        self.assertIn('page=2', requests[1])

    def test_failed_refresh_retains_only_a_matching_valid_snapshot(self):
        snapshot = activity.collect(self.config, FakeGitHub([commit()]), NOW)
        with tempfile.TemporaryDirectory() as directory:
            config, output = Path(directory) / 'config.json', Path(directory) / 'stats.json'
            config.write_text(json.dumps(self.config))
            activity.write_snapshot(output, snapshot)
            original = output.read_bytes()
            args = ['collector', '--config', str(config), '--output', str(output), '--allow-stale']
            with patch.object(sys, 'argv', args), patch.object(activity, 'collect', side_effect=RuntimeError('rate limited')):
                with patch('sys.stderr', new_callable=io.StringIO) as error:
                    activity.main()
                self.assertIn('retaining snapshot', error.getvalue())
                self.assertEqual(output.read_bytes(), original)
                self.config['since'] = '2026-08-01T00:00:00Z'
                config.write_text(json.dumps(self.config))
                with self.assertRaisesRegex(ValueError, 'does not match'):
                    activity.main()

    def test_invalid_totals_and_duplicate_repositories_are_rejected(self):
        snapshot = activity.collect(self.config, FakeGitHub([commit()]), NOW)
        snapshot['summary']['commits'] = 100
        with self.assertRaisesRegex(ValueError, 'inconsistent'):
            activity.validate_snapshot(snapshot, self.config)
        self.config['repositories'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicates'):
            activity.collect(self.config, FakeGitHub([]), NOW)


if __name__ == '__main__':
    unittest.main()
