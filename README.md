# DPN Python Utils

A collection of python utils used by the DPN.

Minimum python version: ```3.7```

## High-level Design Notes

To be broadly compatible with running in synchronous or asynchronous mode, the methods
are designed to run in a synchronous fashion for all modules excluding ```async```.
The ```async``` module or other projects can utilise the methods in either fashion.

The principles behind the modules are to:
 * Be dependable and provide least surprise
 * Fail safe and raise informative exceptions
 * Optimise for readability and maintainability
 * Design for intended eventual backwards compatibility

The code targets python versions in general availability.

## Modules

| Module Name      | Module Description                                     |
| ---------------- | :----------------------------------------------------- |
| async            | Methods relating to async and event loop               |
| ```cli```        | Methods relating to commandline input and output       |
| ```common```     | Methods relating to logging and shared system services |
| ```crypto```     | Methods relating to cryptography and encoding          |
| ```exceptions``` | Exception classes for all modules                      |
| ```file```       | Methods relating to file and path operations           |
| ```http```       | Methods relating to general HTTP/REST                  |
| mq               | Methods relating to message queing protocols           |


