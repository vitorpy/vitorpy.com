# vitorpy.com

A single-page static website. The complete site is [`index.html`](index.html).

## Preview

```sh
python3 -m http.server
```

## Deployment

Pushes to `main` run `.github/workflows/deploy.yml`, stage only `index.html`,
and publish it to GitHub Pages.

Do not push GitHub `main` without explicit confirmation: it triggers production deployment.
