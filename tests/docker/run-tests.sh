#!/bin/bash

set -e

# Add /.local to path
export PATH=$PATH:/.local/bin

echo "-- HOME is $HOME"

echo "Installing python packages..."
pip3 install -U --user -q setuptools
pip3 install --no-warn-script-location --user --prefer-binary $PIP_OPTIONS -r requirements.tests
pip3 install --no-warn-script-location --user --prefer-binary $PIP_OPTIONS -r requirements.txt 

pip3 install --user -e ./ 

echo "Installed contributions: $(pip list -l | grep pyqgiservercontrib)"

export QGIS_DISABLE_MESSAGE_HOOKS=1
export QGIS_NO_OVERRIDE_IMPORT=1

export FAKEREDIS=yes

# Run new tests
cd tests/unittests && pytest -v $@

