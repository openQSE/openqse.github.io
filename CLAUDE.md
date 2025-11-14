# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the openQSE Initiative website built using Jekyll static site generator. The site serves as a unified platform for the quantum software ecosystem community, bringing together vendors, collaborators, labs, and universities.

**Note:** The main branch now uses a custom Tailwind CSS implementation. Previous versions used the Beautiful Jekyll theme.

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
- **Styling**: Custom Tailwind CSS implementation
  - Main CSS: `assets/css/tailwind.min.css`
  - Custom overrides: `assets/css/style.css`
  - No Bootstrap or jQuery dependencies
- **Timezone**: America/New_York
- **Permalink structure**: `/:year-:month-:day-:title/`

### Key Design Features
- Custom Tailwind CSS implementation
- Simplified layouts without Bootstrap dependencies
- Gradient hero header with SVG wave divider on homepage
- Custom navigation with mobile toggle (vanilla JavaScript)
- Blue color scheme for links (`text-blue-600`) with hover states
- Responsive grid layouts using Tailwind utility classes

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
- `default.html`: Base layout that includes header, content, and footer
- `page.html`: Standard page layout for static pages
- `post.html`: Blog post layout with date, author, and metadata
- `meeting.html`: Custom layout that lists all meetings collection items with excerpts
- `home.html`: Homepage layout (used for index)

**Layout hierarchy:** All layouts inherit from `default.html`, which includes `_includes/head.html`, `_includes/header.html`, and `_includes/footer.html`.

### Configuration (_config.yml)

Key customizations:
- **Site identity**: Title "openQSE", author "openQSE Initiative"
- **Navigation**: Defined in `_config.yml` for reference, but **actual menu is hardcoded in `_includes/menu.html`**
- **Collections**: Custom `meetings` collection defined for meeting notes
- **Features enabled**: RSS feed, sitemap, SEO tags
- **Defaults**: Posts have comments/social-share disabled by default
- **Plugins**: jekyll-sitemap, jekyll-feed, jekyll-seo-tag, jekyll-paginate

### Key Files and Directories
- `_includes/`: Reusable HTML partials
  - `head.html`: Meta tags, CSS includes, favicon
  - `header.html`: Main hero header with gradient background and navigation
  - `header_page.html`: Simplified header for non-homepage pages
  - `menu.html`: **Navigation menu items (hardcoded - see Navigation section below)**
  - `footer.html`: Site footer with social links
- `assets/`: Static assets
  - `assets/css/tailwind.min.css`: Tailwind CSS framework
  - `assets/css/style.css`: Custom CSS overrides
  - `assets/css/pygment_highlights.css`: Syntax highlighting for code blocks
  - `assets/img/openQSE-logo.png`: Primary site logo
  - `assets/js/mermaid-init.js`: Mermaid diagram initialization

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
- Syntax highlighting with Rouge using triple backticks or `{% highlight %}` tags
- Excerpt length: 50 words (configurable)
- Date format: "%B %-d, %Y" (e.g., "September 16, 2025")
- Mermaid diagrams supported via `assets/js/mermaid-init.js`

## Deployment and Build

- Built site is generated in `_site/` directory (gitignored)
- Exclude list in `_config.yml` prevents CLAUDE.md, README.md, Gemfile, docs/, backup directories from being built
- Plugins: `jekyll-sitemap`, `jekyll-feed`, `jekyll-seo-tag`, `jekyll-paginate` (5 posts per page)
- RSS feed generated at `/feed.xml` with project description
- Use `make build` or `bundle exec jekyll build` to verify builds before committing

## Important Considerations

### Navigation Configuration

**⚠️ CRITICAL: Navigation links are hardcoded in `_includes/menu.html`**

Unlike typical Jekyll themes where navigation is generated from `_config.yml`, this site's navigation menu is **manually defined** in the HTML template.

**To add or modify navigation links:**
1. Edit `_includes/menu.html` directly
2. Add/remove/modify `<li>` elements in the menu structure
3. Changes take effect immediately with Jekyll's live reload (no restart needed)

**Example - Adding a simple link:**
```html
<li class="mr-3">
    <a class="inline-block py-2 px-4 text-white no-underline hover:text-blue-500 toggleColour"
       href="{{ '/your-page' | relative_url }}">Your Link</a>
</li>
```

**Example - Adding a dropdown menu:**
```html
<li class="mr-3 relative">
    <a class="inline-block py-2 px-4 text-white no-underline hover:text-blue-500 toggleColour cursor-pointer"
       onclick="toggleDropdown(event, 'dropdown-id')">Dropdown ▾</a>
    <ul id="dropdown-id" class="absolute hidden bg-white text-gray-800 shadow-lg mt-2 py-2 rounded z-50">
        <li><a class="block px-4 py-2 hover:bg-gray-100" href="URL">Item</a></li>
    </ul>
</li>
```

**Note:** While `_config.yml` contains a `navbar-links` section for reference, it is **not used** to generate the navigation menu in this implementation.

### Styling and Customization
- Site uses Tailwind CSS utility classes throughout
- Custom CSS overrides go in `assets/css/style.css`
- Color scheme: Blue links (`text-blue-600`) with hover states
- Gradient header with purple-to-blue gradient on homepage
- Mobile navigation uses vanilla JavaScript toggle (no jQuery)

### Collections System
- The `meetings` collection is defined in `_config.yml` with `output: true`
- Meeting posts go in `_meetings/` directory
- Both posts and meetings use similar front matter but different permalinks
- Meeting index page uses special `meeting.html` layout that lists all meetings