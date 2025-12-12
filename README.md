# Readable Science Markup (RSM)

[![tests](https://github.com/leotrs/rsm/actions/workflows/test.yml/badge.svg)](https://github.com/leotrs/rsm/actions/workflows/test.yml)
[![docs](https://readthedocs.org/projects/rsm-markup/badge/?version=latest)](https://rsm-markup.readthedocs.io/en/latest/?badge=latest)

The web-first authoring software for scientific manuscripts.

RSM is a suite of tools that aims to change the way scientific manuscripts are published
and shared using modern web technology. Currently, most scientific publications are made
with LaTeX and published in PDF format. While the capabilities of LaTeX and related
software are undeniable, there are many pitfalls. RSM aims to cover this gap by allowing
authors to create web-first manuscripts that enjoy the benefits of the modern web.

One of the main aims of the RSM suite is to provide scientists with tools to author
scientific manuscripts in a format that is web-ready in a transparent, native way that
is both easy to use and easy to learn.  In particular, RSM is a suite of tools that
allow the user to write a plain text file (in a special `.rsm` format) and convert the
file into a web page (i.e. a set of .html, .css, and .js files).  These files can then
be opened natively by any web browser on any device.

+ Learn more in the [official website](https://www.write-rsm.org).
+ Try it out in the [online editor](https://lets.write-rsm.org).
+ Get started with the [docs](https://docs.write-rsm.org).


## Contributing

This project is under constant development and contributions are *very much* welcome!
Please develop your feature or fix in a branch and submit a PR.


### Rebuilding the Standalone JS Bundle

The file `rsm/static/rsm-standalone.js` is a pre-built bundle of all RSM JavaScript
for standalone HTML files (files that can be opened directly from `file://` URLs).

If you modify any JS files in `rsm/static/`, you must regenerate this bundle:

```bash
npx esbuild rsm/static/onload.js --bundle --format=iife --global-name=RSM --outfile=rsm/static/rsm-standalone.js
```

This bundles `onload.js` and all its dependencies into a single IIFE that exposes
`RSM.onload()` and `RSM.onrender()`. The bundle is committed to the repo so there's
no runtime dependency on esbuild.


## Publishing

This project uses `poetry`. Releasing a new version to PyPI is as easy as executing
`poetry publish`.
