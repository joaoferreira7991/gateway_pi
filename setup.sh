#!/bin/bash

# This script is used to create the python virtual environment needed for the program to run.

echo "--Deleting old environment--"
rm -r -f ./virtual/

echo "--Making environment--"
python3.8 -m venv virtual
source ./virtual/bin/activate


echo "--Installing modules--"
# Resolve dependencies
sudo apt-get update
sudo apt install libpq-dev
sudo apt-get install pigpio
sudo apt install libgpiod2


python -m pip install --upgrade pip
python -m pip install $(cat requirements.txt)
