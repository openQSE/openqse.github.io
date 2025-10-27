# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the openQSE Initiative website built using Jekyll and the Beautiful Jekyll theme (v6.0.1). The site serves as a unified platform for the quantum software ecosystem community, bringing together vendors, collaborators, labs, and universities.

## Development Setup

### Installation and Dependencies
```bash
# Install Ruby dependencies
bundle install

# Serve the site locally with live reload
bundle exec jekyll serve

# Build the site for production
bundle exec jekyll build

# Remove generated files
rm -rf _site .sass-cache

# Alternatively, use Make commands
make install    # Install dependencies
make serve      # Serve locally
make build      # Build site
make clean      # Clean generated files
```

The built site will be in the `_site` directory (gitignored).

## Architecture

### Site Structure
- **Jekyll Static Site Generator**: Uses Jekyll 3.9.3+ with Kramdown markdown processor and Rouge syntax highlighter
- **Beautiful Jekyll Theme**: Pre-built responsive theme with customizations in `_config.yml`
- **Timezone**: America/New_York
- **Permalink structure**: `/:year-:month-:day-:title/`

### Content Organization

#### Collections
- **Posts** (`_posts/`): Blog posts with layout defaulting to "post"
  - Naming convention: `YYYY-MM-DD-title.md`
  - Front matter: layout, title, subtitle, tags, author, comments, mathjax

- **Meetings** (`_meetings/`): Custom collection for meeting notes and records
  - Naming convention: `YYYY-MM-DD-meeting-name.md`
  - Uses custom `meeting` layout that displays list of all meetings with excerpts
  - Accessed via the "Meetings" navbar link (`/meetings`)

#### Layouts (`_layouts/`)
- `base.html`: Base layout with HTML structure
- `default.html`: Default layout for most pages
- `page.html`: Standard page layout
- `post.html`: Blog post layout with date, author, and social sharing
- `meeting.html`: Custom layout that lists all meetings collection items with pagination support
- `home.html`: Homepage layout
- `minimal.html`: Minimal layout without header/footer

### Configuration (_config.yml)

Key customizations:
- **Site identity**: Title "openQSE", author "openQSE Initiative"
- **Navigation**: Docs, Current Efforts, Glossary, Meetings, Resources (Github, Mailing Lists)
- **Collections**: Custom `meetings` collection defined for meeting notes
- **Theme colors**: Custom color scheme with link color #007833
- **Features enabled**: Post search, edit page button, RSS feed
- **Defaults**: Posts have comments/social-share disabled by default

### Theme Files
- `_includes/`: Reusable HTML partials (nav, footer, comments, analytics, etc.)
- `_data/ui-text.yml`: UI text strings
- `assets/`: CSS, JavaScript, images
  - `/assets/img/avatar-icon.png`: Site logo in navbar
  - Custom CSS can be added via `site-css` in config

### Front Matter Examples

**Blog Post:**
```yaml
---
layout: post
title: Post Title
subtitle: Post Subtitle
tags: [tag1, tag2]
author: Author Name
comments: true
mathjax: true  # Enable LaTeX math rendering
---
```

**Meeting:**
```yaml
---
layout: post
title: Meeting Name
subtitle: Meeting Description
tags: [topic]
author: Organizer Name
---
```

## Content Authoring

- Markdown files use Kramdown (GFM input mode)
- MathJax available when `mathjax: true` in front matter
- Custom box styles: `.box-note`, `.box-warning`, `.box-error`
- Syntax highlighting with Rouge using triple backticks or `{% highlight %}` tags
- Excerpt length: 50 words (configurable)
- Date format: "%B %-d, %Y" (e.g., "September 16, 2025")

## Deployment Notes

- Exclude list in `_config.yml` prevents CHANGELOG.md, README.md, Gemfile, docs/, etc. from being built
- The site uses `jekyll-paginate` (5 posts per page) and `jekyll-sitemap` plugins
- RSS feed generated at `/feed.xml` with description from config