# Development

To get a common development environment this project uses [poetry](https://poetry.eustace.io/)

To get started just run:

    :::bash
	poetry install
    poetry shell


To add a dependency use:

    :::bash
    poetry add $package
	
To add a development dependency use:

    :::bash
    poetry add --dev $package
	
To update the package dependencies use:

    :::bash
    poetry up

For automation of common development tasks (testing, deployment, ..) we use [pyinvoke](https://pyinvoke.org) . 

The complete list of currently defined tasks can be shown by running

    :::bash
    inv --list

## Test Suite

To run the integration tests use: 

    :::bash
    inv test

## Static Type Hints

Where applicable this project uses type hints to allow, 
static type checking and error detection. 

The typechecking is invoked through:

    :::bash
    inv mypy

Additionally static type information can be derived from the 
unittest suite using monkeytype. 

    :::bash
    inv monkeytype
   
This command executes the test suite and derives traces dynamically used
types. 

Then you can use monkeytype to automatically annotate the modules with type 
information using:

    :::bash
    monkeytype list-modules
	monkeytype stub $module
	monkeytype apply $module



## Codestyle

This project uses black to enforce a common codestyle throughout the project.

Reformatting can be invoked through:

    :::bash
    inv black

It is recommended to configure your editor to autmatically reload changed files 

## Pre-Commit Hooks

Static Typechecking, and blackening can be run as pre-commit hooks.
These are installed using:

    :::bash
    inv pre-commit
