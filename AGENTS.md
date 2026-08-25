# Project-Specific Instructions

## CRITICAL: DO NOT AUTO-PUSH TO PRODUCTION

**NEVER push to GitHub `main` without explicit user confirmation.**

This repository has automatic deployment enabled. A push to GitHub `main` runs
`.github/workflows/deploy.yml` and publishes the site through GitHub Pages.

**Before pushing:**
1. Build and test locally: `./scripts/build`
2. Verify the expected pages and SVG math assets in `public/`
3. Wait for user confirmation before pushing GitHub `main`
4. NEVER assume it is safe to push automatically

**Only push when the user explicitly asks you to push.**

## LaTeX2HTML pipeline

- Public source documents live below `site/pages/` and are named `index.tex`.
- The source directory maps directly to the URL directory.
- Shared LaTeX fragments live in `site/includes/`.
- `site/drafts/` is deliberately excluded from builds.
- `site/special/404.tex` produces the root-level `404.html` page.
- Never edit generated files in `public/`; change the corresponding TeX source.
- `scripts/bootstrap-latex2html` pins and installs the converter below ignored `.tools/`.
- The production build command is `./scripts/build`.
