#!/bin/bash

set -e
set -x

devpi_server=http://fare-docker-reg.dock.studios:3141

for py_ver in 2 3
do
    virtualenv build-env -p python${py_ver}
    . ./build-env/bin/activate

    python --version
    pip --version

    pip install "devpi-client>=2.3.0"

    pip download -r requirements.txt -d build-env/reqs
    pip install -r requirements.txt

    python setup.py bdist_wheel -d build-env/dest

    if devpi use ${devpi_server}>/dev/null
    then
       devpi use ${devpi_server}/root/public --set-cfg \
        && devpi login root \
        && devpi upload --from-dir --formats='*' ./build-env/dest ./build-env/reqs
    else
        echo "No started devpi container found at ${devpi_server}"
    fi

    deactivate

    rm -rf build-env
done