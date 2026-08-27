# Project-Specific Instructions

## CRITICAL: DO NOT AUTO-PUSH TO PRODUCTION

**NEVER push to GitHub `main` without explicit user confirmation.**

This repository has automatic deployment enabled. A push to GitHub `main` runs
`.github/workflows/deploy.yml` and publishes the site through GitHub Pages.

**Before pushing:**
1. Preview and validate `index.html` locally
2. Verify that the deployment artifact contains only `index.html`
3. Wait for user confirmation before pushing GitHub `main`
4. NEVER assume it is safe to push automatically

**Only push when the user explicitly asks you to push.**

## Static site

- `index.html` is the sole website source and the only file published.
- Keep the page dependency-free: inline CSS, no generated assets, and no build step.
- `.github/workflows/deploy.yml` stages `index.html` into a temporary `public/`
  directory before deploying it through GitHub Pages.
