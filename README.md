# Workers Pyodide Build System

This repository contains scripts and GitHub Actions which can be used to generate the build artifacts needed to run Python Workers on Cloudflare's Workers Runtime. These scripts operate on the [Cloudflare Pyodide fork](https://github.com/cloudflare/pyodide).

There are two components of this repo. You can read more on usage in each component's README.md file.

- `packages/` is responsible for building the package bundle and index.
- `pyodide/` is responsible for building the Pyodide interpreter itself, then modifying ("linking") it to run within workerd.
