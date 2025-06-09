#!/bin/bash

git clone https://github.com/emscripten-core/emsdk
cd emsdk
./emsdk install $EMSDK_VERSION
./emsdk activate $EMSDK_VERSION
source ./emsdk_env.sh
cd ..

git clone https://github.com/cloudflare/pyodide.git
(cd pyodide && git checkout $PYODIDE_TAG)
ln -s pyodide/packages packages

# rust is required for building some wheels
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

sudo apt install -y pkg-config

sudo apt install gfortran sqlite3 f2c swig libreadline-dev

#todo: setup python3.12

python3.12 -m venv .venv
source .venv/bin/activate
pip install pyodide-build==0.29.2

pip install boto3 cython requests
