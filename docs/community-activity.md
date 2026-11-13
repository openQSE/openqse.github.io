# Community activity widget

The shared community section is rendered by Jekyll from a JSON snapshot.
It works without JavaScript, browser API calls or a separate service. Only the
website repository changes; the six watched repositories are read-only inputs.

## Update the numbers

Use Python 3.9 or newer. There are no extra Python packages to install:

```bash
python3 scripts/update_community_activity.py
python3 scripts/update_community_activity.py --check
python3 -m unittest discover -s tests -p 'test_community_activity.py' -v
bundle exec jekyll build
bundle exec jekyll build --baseurl /previews/local
```

The collector uses `GITHUB_TOKEN` if set. Anonymous requests also work, subject
to GitHub's lower rate limit. Do not put a token in the configuration or browser.

The production deployment workflow runs daily at **08:23 UTC**, on pushes to
`main`, and on manual dispatch. It refreshes the snapshot in the build workspace
before Jekyll renders it, then uses the existing Pages deployment. It does not
create automated commits on `main`. GitHub may delay scheduled jobs; the page
shows the last successful collection time, rather than the build time.

PR checks and previews use the checked-in snapshot so they work offline and
remain reproducible. Refresh and commit that snapshot when changing the
configuration or when current preview numbers are useful. Production refreshes
do not flow back into the source snapshot automatically.

If the API fails, `--allow-stale` retains the complete previous snapshot and
emits a workflow warning, provided it still matches the configuration. It never
publishes partial counts or replaces a failed repository with zero. A changed
configuration without a matching usable snapshot fails the build instead.

## Configure repositories and credits

Edit `_data/community_activity_config.json`:

- `since` is an inclusive timestamp with timezone. The initial window begins
  July 1, 2026, matching the community slide.
- Each repository has an explicit `repository`, `branch` and short description.
  DEFw uses `master`; the others initially use `main`.
- `include_merge_commits` and `exclude_bot_commits` define the count policy.
  Initially, totals include merge and bot-authored commits.
- `people` holds reviewed name, institution, alias and exclusion overrides.
  Keys are `github:login` (lowercase), or an unlinked identity's internal key.
  For example, `"github:example": {"name": "Example Person", "institution":
  "Example Lab", "aliases": ["public-commit-email@example.org"]}`. Aliases
  should come from verified, already-public commit attribution. Display names
  alone are not used to merge people. `"exclude": true` omits a non-human
  identity from the contributor list without changing commit counts.
- `institutions` is an editorial acknowledgement list, initially transcribed
  from the November 12, 2026 community slide. It is separate from the activity
  window and is not automatically inferred from author email domains or GitHub
  company fields. It does not imply institutional endorsement.

Run the collector after configuration edits to regenerate the matching snapshot.

## Counting rules

The collector paginates GitHub's commits endpoint for each configured branch.
Counts include commits reachable through that branch, using the Git committer
date within the collection window. A merged branch's commits therefore count;
they do not need to have been committed directly on `main`.

A SHA is counted once within a repository. Shared history can appear in more
than one repository, so the headline is the sum of repository counts, not a
deduplicated cross-repository commit total. Squash merging changes the count.

People come from the original commit author and `Co-authored-by` trailers, not
the person who clicked Merge. Linked GitHub accounts and recognized GitHub
noreply addresses provide account identities; other authors remain unlinked
unless explicitly reconciled. Bot accounts are omitted from the people list.
Each identity gets at most one credit per commit, so individual credits can sum
to more than the commit total. No raw author emails are emitted in the snapshot.

The eight bars on each repository card represent consecutive seven-day groups
ending today. Recent counts use seven UTC calendar days including today.

## Presentation

The include `_includes/community-activity.html` owns the section, and its CSS is
scoped in `assets/css/community-activity.css`. Set the
`community_activity: true` front matter flag on every page that renders the
widget so the shared stylesheet loads. The homepage layout includes the widget
automatically; other pages can place `{% include community-activity.html %}` at
the desired location. Jekyll's `relative_url` filter keeps the stylesheet
working under PR preview paths. Contributor details use native disclosure
elements, with keyboard focus and reduced-motion styles.

The initial committed snapshot was collected from GitHub on November 13, 2026;
its numbers are real, rather than placeholders. The collector, configuration,
snapshot, template and stylesheet can be refined independently in this PR.
