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
pip install pyodide-build

pip install boto3 cython requests

pyodide xbuildenv install $PYODIDE_TAG
pyodide xbuildenv use $PYODIDE_TAG

# Workaround for https://github.com/pyodide/pyodide-build/issues/140
PYODIDE_BUILD_VERSION=$(python -c 'from importlib.metadata import version; print(version("pyodide-build"))')
NUMPY_CORE=.pyodide-xbuildenv-$PYODIDE_BUILD_VERSION/$PYODIDE_TAG/xbuildenv/pyodide-root/packages/.artifacts/lib/python3.12/site-packages/numpy/core/
mkdir -p $NUMPY_CORE/include/numpy
mkdir -p $NUMPY_CORE/lib/numpy
