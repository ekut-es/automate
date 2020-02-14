# Automate

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
	
Edit '~/.automate.yml' to change value of key metadata to the subdirectory 
metadata of repository checkout. 
 
List available boards

    automate list

View Documentation 

    inv doc


