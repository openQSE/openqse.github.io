# openQSE Website - Maintainer's Guide

Quick reference guide for maintaining the openQSE Jekyll website.

## Critical Information

### Navigation Menu ⚠️

**The navigation menu is hardcoded in `_includes/menu.html` and is NOT generated from `_config.yml`.**

This is the most common "gotcha" when maintaining this site. Unlike many Jekyll themes that generate navigation from configuration files, this site requires manual HTML editing.

#### How to Add a Navigation Link

1. Open `_includes/menu.html`
2. Add your link in the appropriate position within the `<ul>` element
3. Save and refresh your browser (Jekyll live reload will pick it up)

**Simple link example:**
```html
<li class="mr-3">
    <a class="inline-block py-2 px-4 text-white no-underline hover:text-blue-500 toggleColour"
       href="{{ '/your-page' | relative_url }}">Your Link Text</a>
</li>
```

**Dropdown menu example (like Resources):**
```html
<li class="mr-3 relative">
    <a class="inline-block py-2 px-4 text-white no-underline hover:text-blue-500 toggleColour cursor-pointer"
       onclick="toggleDropdown(event, 'dropdown-yourname')">Your Dropdown ▾</a>
    <ul id="dropdown-yourname" class="absolute hidden bg-white text-gray-800 shadow-lg mt-2 py-2 rounded z-50" style="min-width: 150px;">
        <li><a class="block px-4 py-2 hover:bg-gray-100 hover:text-blue-500 no-underline text-gray-800"
               href="https://example.com" target="_blank" rel="noopener noreferrer">Link 1</a></li>
        <li><a class="block px-4 py-2 hover:bg-gray-100 hover:text-blue-500 no-underline text-gray-800"
               href="https://example.com" target="_blank" rel="noopener noreferrer">Link 2</a></li>
    </ul>
</li>
```

**Current menu structure:**
- Meetings → `/meetings`
- Resources (dropdown)
  - Github → `https://github.com/openQSE`
  - Slack → `https://openqse.slack.com`

## Common Tasks

### Adding a New Page

1. Create your page file (e.g., `about.html` or `about.md`) in the root directory
2. Add front matter:
   ```yaml
   ---
   layout: page
   title: About
   subtitle: Optional subtitle
   ---
   ```
3. Add content to the file
4. **Manually add navigation link** to `_includes/menu.html` (see above)
5. Test locally: `bundle exec jekyll serve`

### Adding a Blog Post

1. Create file in `_posts/` with naming convention: `YYYY-MM-DD-title.md`
2. Add front matter:
   ```yaml
   ---
   layout: post
   title: Post Title
   subtitle: Optional subtitle
   tags: [tag1, tag2]
   author: Your Name
   ---
   ```
3. Write content in Markdown
4. Posts automatically appear on the homepage

### Adding a Meeting Note

1. Create file in `_meetings/` with naming convention: `YYYY-MM-DD-meeting-name.md`
2. Add front matter:
   ```yaml
   ---
   layout: post
   title: Meeting Name
   subtitle: Meeting Description
   tags: [topic]
   author: Organizer Name
   ---
   ```
3. Write meeting notes in Markdown
4. Meeting appears on `/meetings` page

## Technical Details

### Technology Stack
- **Static Site Generator**: Jekyll 3.9.3+
- **CSS Framework**: Tailwind CSS (no Bootstrap)
- **JavaScript**: Vanilla JS (no jQuery)
- **Markdown Processor**: Kramdown with GFM mode
- **Syntax Highlighter**: Rouge

### Directory Structure
```
.
├── _includes/          # HTML partials (header, footer, menu)
│   └── menu.html       # ⚠️ Navigation menu (edit this!)
├── _layouts/           # Page layouts
├── _posts/             # Blog posts (YYYY-MM-DD-title.md)
├── _meetings/          # Meeting notes (YYYY-MM-DD-name.md)
├── assets/
│   ├── css/
│   │   ├── tailwind.min.css    # Tailwind framework
│   │   └── style.css           # Custom CSS overrides
│   ├── img/            # Images and logos
│   └── js/             # JavaScript files
├── _config.yml         # Jekyll configuration
├── index.html          # Homepage
└── meetings.html       # Meetings index page
```

### Key Files

| File | Purpose | Notes |
|------|---------|-------|
| `_includes/menu.html` | Navigation menu | **Edit this to change nav links** |
| `_includes/header.html` | Homepage hero header | Gradient background + logo |
| `_includes/header_page.html` | Non-homepage header | Simplified version |
| `_config.yml` | Jekyll configuration | Restart Jekyll after changes |
| `assets/css/style.css` | Custom CSS | Tailwind utility overrides |

### Development Workflow

```bash
# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve
# Visit: http://localhost:4000

# Build for production
bundle exec jekyll build
# Output: _site/

# Clean build artifacts
rm -rf _site .sass-cache
```

### Important Notes

1. **Config changes require restart**: Changes to `_config.yml` require stopping and restarting Jekyll
2. **Include changes auto-reload**: Changes to `_includes/*.html` work with live reload
3. **CSS changes auto-reload**: Changes to CSS files work with live reload
4. **Navigation is manual**: Must edit `_includes/menu.html` to add/remove menu items
5. **No Bootstrap/jQuery**: Site uses Tailwind CSS and vanilla JavaScript only

### Styling Guidelines

- Use Tailwind utility classes for styling
- Primary color scheme: Blues (`text-blue-600`, `hover:text-blue-500`)
- Navigation text: White with blue hover
- Custom CSS goes in `assets/css/style.css`
- Responsive classes: `lg:`, `md:`, `sm:` prefixes

### Mobile Navigation

- Mobile menu toggle is in `_includes/header.html`
- Button ID: `nav-toggle`
- Menu ID: `nav-content`
- Uses Tailwind responsive classes to hide/show
- Vanilla JavaScript for toggle functionality

## Troubleshooting

**Problem**: Navigation link doesn't appear after adding to `_config.yml`
**Solution**: Edit `_includes/menu.html` instead - config file is not used for navigation

**Problem**: Changes not showing up
**Solution**:
- For `_config.yml`: Restart Jekyll server
- For other files: Refresh browser (should auto-reload)
- Clear browser cache if needed

**Problem**: Jekyll serve fails
**Solution**:
- Check for syntax errors in front matter
- Ensure all required plugins are installed (`bundle install`)
- Check Jekyll error output for specific issues

## Resources

- **Full documentation**: See `CLAUDE.md` for comprehensive guidance
- **Jekyll docs**: https://jekyllrb.com/docs/
- **Tailwind CSS docs**: https://tailwindcss.com/docs
- **GitHub repo**: https://github.com/openQSE/openqse.github.io
