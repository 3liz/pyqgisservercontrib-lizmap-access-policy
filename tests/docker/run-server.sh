#!/bin/bash

set -e

# Qgis need a HOME
export HOME=/home/qgis

if [ "$(id -u)" = '0' ]; then

echo "Installing python packages..."
pip3 install -U -q setuptools
pip3 install --no-warn-script-location -q --prefer-binary -r requirements.tests
pip3 install --no-warn-script-location -q --prefer-binary -r requirements.txt 

pip3 install -e ./ 

echo "Installed contributions: $(pip list -l | grep pyqgiservercontrib)"

mkdir -p $HOME
chown -R $BECOME_USER:$BECOME_USER $HOME

exec gosu $BECOME_USER:$BECOME_USER  "$BASH_SOURCE" $@

fi

echo "-- HOME is $HOME"

export QGIS_DISABLE_MESSAGE_HOOKS=1
export QGIS_NO_OVERRIDE_IMPORT=1

export FAKEREDIS=yes

# Run new tests
exec wpsserver -w $WORKERS -p 8080 --chdir tests/unittests

