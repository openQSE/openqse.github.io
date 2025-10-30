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

### Main Deployment
- `main` branch → Deploys to `gh-pages` branch root → `openqse.org`
- Workflow: `.github/workflows/jekyll.yml`

### PR Previews
- PR branches → Deploy to `gh-pages/previews/pr-X/` subdirectories → `https://openqse.org/previews/pr-X/`
- Workflow: `.github/workflows/pr-preview.yml`
- Bot comments on PR with preview URL
- Auto-updates on new commits
- Auto-cleans up when PR closes
- **Note:** Previews are accessible via the custom domain once main site is deployed

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
2. Merge the PR to `main`
3. The main workflow deploys to production at `https://openqse.org`
4. The PR preview is automatically cleaned up

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
