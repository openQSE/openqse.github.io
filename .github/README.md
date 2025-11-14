# GitHub Actions Workflows

## TL;DR

**To update openqse.org:**
1. Make changes in a branch
2. Push to GitHub
3. Merge to `main`
4. ✅ Auto-deploys to openqse.org

**PR Previews:**
- Open a PR → Get preview at `https://openqse.org/previews/pr-123/`
- Review changes live before merging
- Preview auto-cleans up when PR is closed

---

## How It Works

### Workflows Overview

#### Build Workflow (Shared)
- **Workflow:** `.github/workflows/build-jekyll.yml`
- Reusable workflow that builds the Jekyll site with configurable baseurl
- Used by both PR checks and production deployment to ensure consistency

#### PR Status Checks
- **Workflow:** `.github/workflows/pr-checks.yml`
- Runs on every PR (opened, updated, reopened) - does NOT run on label changes for efficiency
- Two-stage validation:
  1. **Build Stage:** Validates Jekyll build succeeds
  2. **Merge Check Stage:** Runs only after build succeeds, checks for DO-NOT-MERGE label
- Blocks merge if:
  - Jekyll build fails (build-test job), OR
  - PR has `DO-NOT-MERGE` label (check-merge-status job depends on build-test)
- **Note:** Label check runs on next push, not immediately when label is added/removed
- Uses shared build workflow to validate changes

#### PR Previews
- **Workflow:** `.github/workflows/pr-preview.yml`
- PR branches → Deploy to `gh-pages/previews/pr-X/` subdirectories → `https://openqse.org/previews/pr-X/`
- Bot comments on PR with preview URL
- Auto-updates on new commits
- Auto-cleans up when PR closes
- **Note:** Previews are accessible via the custom domain once main site is deployed

#### Main Deployment
- **Workflow:** `.github/workflows/deploy-jekyll.yml`
- `main` branch → Deploys to `gh-pages` branch root → `openqse.org`
- Uses shared build workflow, then deploys artifact to production
- Keeps PR preview directories intact (`keep_files: true`)

---

## One-Time Setup Required

### 1. Create the gh-pages branch

```bash
git checkout --orphan gh-pages
git rm -rf .
echo "# PR Previews" > README.md
git add README.md
git commit -m "Initialize gh-pages for PR previews"
git push origin gh-pages
git checkout main
```

### 2. Configure GitHub Pages

In repository **Settings** → **Pages**:
- **Build and deployment**:
  - **Source:** Deploy from a branch
  - **Branch:** `gh-pages` / `(root)`
- Click **Save**

**Full path:** Settings → Pages → Build and deployment → Source → Deploy from a branch

### 3. Enable Workflow Permissions

In repository **Settings** → **Actions** → **General**:
- Under "Workflow permissions":
  - ✅ Select **Read and write permissions**
  - ✅ Check **Allow GitHub Actions to create and approve pull requests**
- Click **Save**

---

## Usage

### Creating a PR
1. Create a branch and push your changes
2. Open a pull request
3. The workflow automatically builds your site and deploys to `https://openqse.org/previews/pr-{number}/`
4. A bot comment appears on your PR with the preview URL

### Updating a PR
- Push new commits to your PR branch
- The preview automatically rebuilds and updates
- The bot comment updates with the new commit hash

### Merging to Production
1. Review your changes at the PR preview URL
2. Ensure PR checks pass (build succeeds, no DO-NOT-MERGE label)
3. Merge the PR to `main`
4. The deployment workflow deploys to production at `https://openqse.org`
5. The PR preview is automatically cleaned up

### Using DO-NOT-MERGE Label
- Add `DO-NOT-MERGE` label to a PR to prevent accidental merging
- PR checks will fail while this label is present
- Remove the label when the PR is ready to merge

---

## Troubleshooting

**Preview URL returns 404:**
- Wait 2-3 minutes after the workflow completes for GitHub Pages to update
- Verify the workflow succeeded in the Actions tab
- Check that `gh-pages` branch exists

**Workflow fails:**
- Check Settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is enabled

**openqse.org doesn't work after setup:**
- Verify the CNAME file contains `openqse.org`
- Check Settings → Pages shows "Custom domain: openqse.org"
- DNS settings should already be correct (no changes needed)

---

## Site Maintenance

This document covers **deployment workflows**. For **site content and maintenance** (adding pages, navigation links, blog posts, etc.), see:

**→ [MAINTAINERS.md](../MAINTAINERS.md)** - Quick reference guide for common site maintenance tasks

**→ [CLAUDE.md](../CLAUDE.md)** - Comprehensive technical documentation for site architecture
