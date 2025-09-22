#!/bin/bash
echo "Removing packages"
python3 -m pip uninstall -r requirements.txt

echo "Removing virtual environment"
if [ -d "venv" ]; then
    rm -rf venv
    echo "Virtual environment removed."
else
    echo "No virtual environment found."
fi

echo "Uninstalling Pip"
python3 -m pip uninstall pip

echo "Uninstalling Python3"
if command -v python3 &> /dev/null; then
    sudo apt-get remove --purge python3
    echo "Python uninstalled."
else
    echo "No Python installation found."
fi

