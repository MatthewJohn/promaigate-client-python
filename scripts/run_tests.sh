#!/bin/bash

. ./build-env/bin/activate

nosetests --with-xunit --xunit-file xunit.xml --with-coverage --cover-xml --cover-xml-file coverage.xml --cover-erase

