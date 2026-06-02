#!/usr/bin/env bash
# Creates a virtual environment, installs dependencies, and activates it.
# Usage: source setup.sh

if [ ! -d "./venv/bin" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv

    echo "Installing dependencies ..."
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r venv/requirements.txt
fi

echo "Activating virtual environment ..."
source venv/bin/activate

echo "Done!"
