## Dependency management

You need to have [virtualenv](https://docs.python.org/3/tutorial/venv.html) installed globally. In case you don't, run:

```bash
pip install virtualenv
```

Create and activate a **_virtualenv_** (name it `.venv`).

```bash
python -m venv .venv
source .venv/bin/activate
```

> You should now see the prefix `(.venv)` in your terminal prompt. This means the virtualenv is active.

## Install locally

Install default and test requirements (assure `.venv` is active).

```shell
pip install -e .[test]
```

Run tests.

```shell
python -m pytest
```

## Publish to [Pypi](https://pypi.org/project/pyauth0/)

A [GitHub Action](https://github.com/svaponi/pyauth0/actions/workflows/publish-to-pypi.yml) will publish the package
whenever a new git tag is pushed to origin.

Run the following command to roll out a new `patch|minor|major` version and push it to origin.

```shell
./rollout.sh
```

> When prompt `Push changes?`, type `y`.
