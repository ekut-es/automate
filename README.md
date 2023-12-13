# Automate



[![pipeline status](https://es-git.cs.uni-tuebingen.de/ties/timing/schrank/automate/badges/main/pipeline.svg)](https://es-git.cs.uni-tuebingen.de/ties/timing/schrank/automate/commits/main)
[![coverage report](https://es-git.cs.uni-tuebingen.de/ties/timing/schrank/automate/badges/main/coverage.svg)](https://es-git.cs.uni-tuebingen.de/ties/timing/schrank/automate/commits/main)

# Getting Started

## Installing from pypi

The software is available as a package from pypi. And installable via pip:


To install in your home directory use one of the following methods:

    pip install --user board-autoamte
    pip install --user 'board-automate[postgres]'

## Installing from sourc

To get started:
  
Install poetry

    python3 -m pip install poetry --user

Install automate in development mode:

    poetry install 

To enable experimental database support use:

    poetry install -E postgres

Start the development shell

    poetry shell


Copy the configuration file:

    cp automate.yml ~/.automate.yml
	
And adopt the settings of the configuration file. 

List available boards

    automate list

View Documentation 

    inv doc


