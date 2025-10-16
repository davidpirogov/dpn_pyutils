# DPN Python Utils

A collection of python utils used by the DPN.

Target minimum python version: `3.12.x`

## High-level Design Notes

To be broadly compatible with running in synchronous or asynchronous mode.

The principles behind the modules are to:

- Be dependable and provide least surprise
- Fail safe and raise informative exceptions
- Optimize code for readability and maintainability
- Design for backwards compatibility

Major versions of dpn_pyutils releases track major Python versions in general
availability

## Modules

| Module Name  | Module Description                                      |
| ------------ | :------------------------------------------------------ |
| `cli`        | Methods relating to command line input and output       |
| `logging`    | Methods relating to logging                             |
| `crypto`     | Methods relating to cryptography and encoding           |
| `exceptions` | Exception classes for all modules                       |
| `file`       | Methods relating to file and path operations            |
| `http`       | Methods relating to general HTTP/REST                   |
| `money`      | Methods relating to money, transactions, and formatting |
| `time`       | Methods relating to time management                     |

## Getting Started

The fastest way to get start is with [Astral uv](https://docs.astral.sh/uv/).

With uv installed on the system, create an environment

```bash
uv init
uv add dpn_pyutils
uv sync
```

This will create a virtual environment with dpn_pyutils installed.

### Upgrade versions

Upgrading is done by uninstalling the package and installing the upgraded version

```bash
uv sync --upgrade-package dpn_pyutils
```

## Testing

This project uses `uv` and `tox` via the [`tox-uv`](https://github.com/tox-dev/tox-uv) plugin. Set it up via:

```bash
uv tool install tox --with tox-uv
```

## Building

Building dpn_pyutils can be done with python 3 and poetry

```bash
uv run pytest tests/
uv build
```

The distribution-ready files will be in the `dist/` directory.

## Packaging and Distribution

Packaging after changes need the following to be executed:

### Update the version number

Bump the version number

- The MAJOR and MINOR versions should **always** match the minimum Python versions
- The PATCH version should be an incremental counter of library versions

```bash
uv lock
uv run bumpver update --dry --patch
uv run bumpver update --patch
git commit -am"Updated requirements, pyproject and bumping version number for release"
```

### Distribute

```bash
uv build
uv publish
```
