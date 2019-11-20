#!/bin/bash -e

python_version=$(python3 -V)

echo "Setting up environment for python version ${python_version}"

if [ ! -e venv ]; then
    python3 -m virtualenv der_schrank
fi
    
source env.sh 

echo ""
echo "Installing required packages"
pip install -r requirements_dev.txt

echo ""
echo "Doing development install of automate"
pip install -e .


echo ""
echo "Installing pre-commit-hooks"
pre-commit install

echo ""
echo "Dependency installation finshed"
echo "To setup environment source env.sh or env.csh depending on your shell type"
