#!/bin/bash

# Run with source command
# Moving project
echo "--Making environment--"
python3.8 -m venv virtual
source ./virtual/bin/activate

# Install new modules, if needed add more here.
echo "--Installing modules--"
python -m pip install --upgrade pip
python -m pip install $(cat requirements.txt)
