#!/bin/csh -f

set SCRIPT_DIR = `dirname $0`
set MXCUBE_DIR = `cd $SCRIPT_DIR && pwd | sed 's/bin$//'`

python3 $MXCUBE_DIR/bin/mxcube --hardwareRepository=$MXCUBE_DIR/HardwareRepository/configuration/xml-qt $argv
