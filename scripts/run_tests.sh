#!/bin/bash

. ./build-env/bin/activate

python3 -m unittest discover
