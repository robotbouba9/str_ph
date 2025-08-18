#!/bin/bash

sudo apt-get update
sudo apt-get install -y \ 
  build-essential \ 
  python3-dev \ 
  libffi-dev \ 
  libcairo2 \ 
  libpango-1.0-0 \ 
  libpangocairo-1.0-0 \ 
  libgdk-pixbuf2.0-0 \ 
  shared-mime-info \ 
  libxml2-dev \ 
  libxslt1-dev \ 
  zlib1g-dev

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

