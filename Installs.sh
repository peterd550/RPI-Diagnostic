#!/bin/bash -xe

sudo apt update
sudo apt install -y python3-full wireless-tools


python3 -m venv rpidiag
source rpidiag/bin/activate

pip install -r requirements.txt


python3 ./RPI-Diagnostic.py
