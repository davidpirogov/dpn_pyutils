# DPN Python Utils

A collection of python utils used by the DPN.

Target python version: ```3.8.x```

## High-level Design Notes

To be broadly compatible with running in synchronous or asynchronous mode, the methods
are designed to run in a synchronous fashion for all modules excluding ```async```.
The ```async``` module or other projects can utilise the methods in either fashion.

The principles behind the modules are to:
 * Be dependable and provide least surprise
 * Fail safe and raise informative exceptions
 * Optimise code for readability and maintainability
 * Design for intended eventual backwards compatibility

Major versions of dpn_pyutils releases track major Python versions in general
availability, and follow [semver](https://semver.org/) versioning

## Modules

| Module Name      | Module Description                                      |
| ---------------- | :------------------------------------------------------ |
| async            | Methods relating to async and event loop                |
| ```cli```        | Methods relating to commandline input and output        |
| ```common```     | Methods relating to logging and shared system services  |
| ```crypto```     | Methods relating to cryptography and encoding           |
| ```exceptions``` | Exception classes for all modules                       |
| ```file```       | Methods relating to file and path operations            |
| ```http```       | Methods relating to general HTTP/REST                   |
| mq               | Methods relating to message queing protocols            |
| ```money```      | Methods relating to money, transactions, and formatting |


## Getting Started

The fastest way to get start is via [pyenv](https://realpython.com/intro-to-pyenv/). 

With pyenv installed on the system, check the latest version of the target python version. 
```bash
pyenv update && pyenv install -l | grep 3.8
```

Install the target python version into pyenv and set up the virtualenv
```bash
pyenv install 3.8.11
pyenv virtualenv 3.8.11 dpn_pyutils
pyenv activate dpn_pyutils
pip install --upgrade pip
pip install -r requirements.txt
```

