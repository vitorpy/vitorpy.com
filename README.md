# vitorpy.com

The site is authored as LaTeX and rendered to static HTML with
[LaTeX2HTML](https://github.com/latex2html/latex2html).

## Build

```sh
./scripts/build
```

The first build downloads and installs the pinned LaTeX2HTML revision under
the ignored `.tools/` directory. Git, Make, Perl, TeX Live, Ghostscript,
`pdftocairo` (from Poppler), and Python 3 must already be available. Generated
files are written to `public/`; the build also checks every local HTML reference
and parses every generated SVG.

Public source documents live under `site/pages/`; their directory maps directly
to the public URL. For example,
`site/pages/blog/example/index.tex` becomes `/blog/example/index.html`.
Documents under `site/drafts/` are not built.

Do not push GitHub `main` without explicit confirmation: it triggers production deployment.
