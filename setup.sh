#!/bin/bash

echo "--Deleting old environment--"
rm -r -f ./virtual/

echo "--Making environment--"
python3.8 -m venv virtual
source ./virtual/bin/activate


echo "--Installing modules--"
python -m pip install --upgrade pip
python -m pip install $(cat requirements.txt)
