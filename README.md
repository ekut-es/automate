# Automate



[![pipeline status](https://atreus.informatik.uni-tuebingen.de/ties/timing/schrank/automate/badges/master/pipeline.svg)](https://atreus.informatik.uni-tuebingen.de/ties/timing/schrank/automate/commits/master)
[![coverage report](https://atreus.informatik.uni-tuebingen.de/ties/timing/schrank/automate/badges/master/coverage.svg)](https://atreus.informatik.uni-tuebingen.de/ties/timing/schrank/automate/commits/master)

## Getting Started

To get started:
  
Update submodules:

    git submodule update --init --recursive
  
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


