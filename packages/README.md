# Pyodide Packages Generator

Here are instructions for how to generate a Pyodide package index & bundle and configure workerd/Edgeworker to build against them.

A package index is hosted on an HTTPS service, and is defined by a `pyodide-lock.json` file that points to a set of *wheels* (essentially zip files), one for each package. The wheels live in the same directory as the lock file. Workerd local dev is configured to use a package index.

A package bundle is used during deployment, and contains all the packages unzipped in a special directory structure. This directory structure is transformed at run-time depending on the packages the user requests.

## How do I add more packages to the index/bundle?

First, make sure that the `cloudflare/pyodide` repo contains all the necessary recipes for the packages you need (and their dependencies). It doesn't necessarily need to be on the `main` branch.

Now, add the packages you want to support in `required_packages.txt`. (No need to specify their dependencies).

Finally, build a new index/bundle according to the instructions in the next section.

## How do I build a new index/bundle?

First, navigate to the "Actions" page on this GitHub repo. Click on "Build & Public Pyodide Package Bundle". There should be a banner that says "This workflow has a `workflow_dispatch` event trigger". On the right of the banner there should be a button that says "Run Workflow". Click that.

There are a few options you may specify:

- Version Tag: This is the version number of the package bundle you're about to build. Usually this is just the current date in YYYYMMDD format.
- Branch or tag of cloudflare/pyodide to get recipes from: This is usually `main` but if you haven't merged the changes into `main` yet for some reason you can change that here.

The other options are usually fine to leave as-is.

Now, once the workflow has finished running, there should be a new Release bearing the name of the version number you picked. You should only need to download one file, `pyodide_bucket.bzl`. This file is located within the `build` directory of the workerd repo and is used by both workerd and Edgeworker at build-time.

Replace this file in the workerd repo, then upstream your changes to Edgeworker, and you should be done!
