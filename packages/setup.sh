#!/bin/bash

git clone https://github.com/hoodmane/pyodide-recipes.git -b langchain --depth 1

ln -s pyodide-recipes/packages packages

# rust is required for building some wheels
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

sudo apt install -y pkg-config

sudo apt install gfortran sqlite3 f2c swig libreadline-dev

python3 -m venv .venv
source .venv/bin/activate
pip install pyodide-build

pip install boto3 cython requests
python pyodide-recipes/tools/install_and_patch_emscripten.py
