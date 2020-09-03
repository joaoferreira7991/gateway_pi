#!/bin/bash

# This script is used to create the python virtual environment needed for the program to run.

echo "--Deleting old environment--"
rm -r -f ./virtual/

echo "--Making environment--"
python3.8 -m venv virtual
source ./virtual/bin/activate


echo "--Installing modules--"
python -m pip install --upgrade pip
python -m pip install $(cat requirements.txt)
