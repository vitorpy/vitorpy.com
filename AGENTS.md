# Project-Specific Instructions

## CRITICAL: DO NOT AUTO-PUSH TO PRODUCTION

**NEVER push to GitHub `main` without explicit user confirmation.**

This repository has automatic deployment enabled. A push to GitHub `main` runs
`.github/workflows/deploy.yml` and publishes the site through GitHub Pages.

**Before pushing:**
1. Preview and validate all published HTML files locally
2. Verify that the deployment artifact contains only `index.html`, `rclone.html`, and `privacy.html`
3. Wait for user confirmation before pushing GitHub `main`
4. NEVER assume it is safe to push automatically

**Only push when the user explicitly asks you to push.**

## Static site

- `index.html` is the landing page; keep it clean and separate from app policies.
- `rclone.html` describes the personal Google Drive app and links to `privacy.html`.
- `privacy.html` is the app's privacy policy.
- Keep the pages dependency-free: inline CSS, no generated assets, and no build step.
- `.github/workflows/deploy.yml` stages only the three HTML files into a temporary
  `public/` directory before deploying them through GitHub Pages.
