#!/bin/bash

virtualenv build-env -p python${PY_VER}
. ./build-env/bin/activate

python --version
pip --version

pip install "devpi-client>=2.3.0"

pip download -r requirements.txt -d build-env/reqs
pip install -r requirements.txt

