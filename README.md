# DPN Python Utils

A collection of python utils used by the DPN.

Target minimum python version: `3.8.x`

## High-level Design Notes

To be broadly compatible with running in synchronous or asynchronous mode, the methods
are designed to run in a synchronous fashion.

The principles behind the modules are to:

- Be dependable and provide least surprise
- Fail safe and raise informative exceptions
- Optimise code for readability and maintainability
- Design for intended eventual backwards compatibility

Major versions of dpn_pyutils releases track major Python versions in general
availability, and follow [semver](https://semver.org/) versioning

## Modules

| Module Name  | Module Description                                      |
| ------------ | :------------------------------------------------------ |
| `cli`        | Methods relating to commandline input and output        |
| `common`     | Methods relating to logging and shared system services  |
| `crypto`     | Methods relating to cryptography and encoding           |
| `exceptions` | Exception classes for all modules                       |
| `file`       | Methods relating to file and path operations            |
| `http`       | Methods relating to general HTTP/REST                   |
| `money`      | Methods relating to money, transactions, and formatting |
| `time`       | Methods relating to time management                     |

## Getting Started

The fastest way to get start is with a [pyenv](https://realpython.com/intro-to-pyenv/).

With pyenv installed on the system, check the latest version of the target python version.

```bash
pyenv update && pyenv install -l | grep 3.8
```

### Install

Install with pip using:

```bash
pip install dpn_pyutils
```

### Install manually

Install the target python version into pyenv and set up the virtualenv

```bash
pyenv install 3.8.11
pyenv virtualenv 3.8.11 dpn_pyutils
pyenv activate dpn_pyutils
pip install --upgrade pip
pip install -r requirements.txt
```

### Upgrade versions

Upgrading is done by uninstalling the package and installing the upgraded version

```bash
pip uninstall dpn_pyutils
pip install dpn_pyutils
```

## Building

Building dpn_pyutils can be done with python 3, setuptools and wheel.

```bash
python -m pip install --upgrade build
python -m build
```

The distribution-ready files will be in the `dist/` directory.

## Packaging

Packaging after changes need the following to be executed:

```bash
pip freeze > requirements.txt
req2lock -f requirements.txt
git commit -am"Updated requirements, pyproject, and poetry lockfile"
```

Update the version number in:

1. pyproject.toml
2. setup.cfg

```bash
git commit -am"Bumping version number for release"
```
