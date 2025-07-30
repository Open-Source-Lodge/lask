# How to make a release
Generally, this repo follows gitflow, or githubflow.

## Run linting and formatting
´uv run ruff check --fix´
´uv run ruff format´

## Make a Pull Request
Create your feature on a new branch. Make a PR from this branch to the main branch.


## Get the PR reviewed (if you are not maintainer) and merged
The maintainer must review the code before we can take it in.

## When the PR is merged, update version number and tag
Checkout main branch, push a version update to pyproject.toml and uv.lock (`$ uv sync`), create tag, push tag. Then on Github, make a new release from the https://github.com/Open-Source-Lodge/lask/releases page.

Ideally, the version number would be auto-generated, and I did some research regarding that with python-semantic-release, but not sure I got that fully working.

## Manually bumping the version number
In the file `pyproject.toml`, update the version number. The format is `MAJOR.MINOR.PATCH`. For example, if the current version is `1.0.0`, you might change it to `1.0.1` for a patch, or `1.1.0` for a minor update.

Then do `$ uv sync` to update the verion in the uv.lock file
