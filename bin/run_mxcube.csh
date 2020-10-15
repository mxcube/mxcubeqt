#!/bin/csh -f

set SCRIPT_DIR = `dirname $0`
set MXCUBE_DIR = `cd $SCRIPT_DIR && pwd | sed 's/bin$//'`

set CONFIG_DIR = ${MXCUBE_DIR}HardwareRepository/configuration/;${MXCUBE_DIR}/HardwareRepository/configuration/qt

python $MXCUBE_DIR/bin/mxcube --hardwareRepository=$CONFIG_DIR $argv
