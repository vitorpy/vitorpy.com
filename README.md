# vitorpy.com

A dependency-free static website. [`index.html`](index.html) is the landing page. [`rclone.html`](rclone.html) describes the personal Google Drive app and links to its separate [`privacy.html`](privacy.html) policy.

## Preview

```sh
python3 -m http.server
```

## Deployment

Pushes to `main` run [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), stage only the three HTML files, and publish them to GitHub Pages.

Do not push GitHub `main` without explicit confirmation: it triggers production deployment.
