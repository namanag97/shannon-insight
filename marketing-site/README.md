# Shannon Insight Marketing Site

A standalone marketing website for [Shannon Insight](https://github.com/namanag97/shannon-insight) -- a multi-signal codebase analysis tool using information theory, graph algorithms, and spectral analysis.

## Tech Stack

- **HTML5** with semantic markup and ARIA labels
- **CSS3** with custom properties, grid, flexbox
- **Vanilla JS** (no framework, no build step)
- **Google Fonts**: Inter + JetBrains Mono

No bundler, no npm, no build process. Open `index.html` and go.

## File Structure

```
marketing-site/
├── index.html           Landing page
├── docs.html            Documentation portal
├── css/
│   ├── styles.css       Main styles (~950 lines)
│   └── animations.css   Scroll animations (~130 lines)
├── js/
│   └── main.js          Scroll observer, nav, mobile menu (~160 lines)
├── images/
│   ├── logo.svg         Logo mark
│   ├── hero-diagram.svg Hero visual (dependency graph)
│   └── screenshots/     Placeholder for dashboard screenshots
└── README.md            This file
```

Total size: ~80KB (excluding external fonts).

## Local Development

No build step required. Open the site in any browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Or use any local server
python -m http.server 8000
# Then visit http://localhost:8000
```

## Deploy to GitHub Pages

1. Copy the `marketing-site/` contents to the root of a `gh-pages` branch:

```bash
git checkout --orphan gh-pages
git rm -rf .
cp -r marketing-site/* .
git add -A
git commit -m "Deploy marketing site"
git push origin gh-pages
```

2. In the repository settings, enable GitHub Pages from the `gh-pages` branch.
3. The site will be available at `https://namanag97.github.io/shannon-insight/`.

## Deploy to Vercel

```bash
cd marketing-site
vercel --prod
```

No configuration needed. Vercel auto-detects static sites.

## Deploy to Netlify

Option A: Drag and drop the `marketing-site/` folder at [app.netlify.com/drop](https://app.netlify.com/drop).

Option B: CLI:

```bash
cd marketing-site
netlify deploy --prod --dir .
```

## Design Decisions

- **Dark theme** matches the CLI/dashboard aesthetic
- **Inter font** for readability; JetBrains Mono for code
- **Blue/purple gradient** accent (#3b82f6 to #8b5cf6)
- **Intersection Observer** for scroll animations (no scroll event listeners)
- **Reduced motion** respected via `prefers-reduced-motion` media query
- **Mobile-first** responsive with breakpoints at 640px and 1024px
- **No JavaScript framework** -- the site is simple enough for vanilla JS
- **All documentation links** point to GitHub (single source of truth)

## Customization

### Colors

All colors are defined as CSS custom properties in `css/styles.css`:

```css
:root {
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --bg-primary: #0a0e1a;
  /* ... */
}
```

### Content

- Edit `index.html` for landing page content
- Edit `docs.html` for documentation portal
- SVG diagrams are inline or in `images/`

## License

MIT -- same as the Shannon Insight project.
