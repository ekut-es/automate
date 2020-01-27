# Automate


To get started:
  
Install poetry

    python3 -m pip install poetry --user

Install automate in development mode:

    poetry install 

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


