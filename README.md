# Der Schrank Lab-Automation

## Getting Started

Setup virtual environment

    ./setup.sh
	
Depending on your shell

    source env.sh   #for bash, zsh
	source env.csh  #for (t)csh

## Repository-Layout

- metadata: Example metadata
  - boards
  - compilers
- automate: Test Automation Main module
  - model: Test Automation Metadata model
  - compiler: Cross-Compiler / Buildsystem Configuration
- tools: commandline interface
- examples: Usage examples
  - sh: examples for usage from bash
  - python: examples for usage from sh
  - notebooks: examples for usage from jupyter-notebooks

config.ini: Test/Example Configuration 

## Configuration File Format

## Compilers

## Boards

### automate

Section automate specifies the main configuration sections. 

Fields: 

- metadata: Metadata Directory to use 
- identity: ssh_id to use

### Logging

Logger is configured uses the standard logging functionality specified in:
https://docs.python.org/3.6/library/logging.config.html#configuration-file-format .


## Metadata Description


# TODO:

- Christoph Cross-Compilation flow
- Autojail Team:
  - Kernel Builds aufsetzen
  - Default Kernel mit kexec bauen und auf Boards installieren
- Konstantin
  - Hiwi mit SSH Key Management beauftragen
  - Abschlussarbeit für Arduino basierten Zugriff auf UARTS und GPIO ausschreiben
