#!/usr/bin/env python
import sys
import os

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

print("MXCuBE root: %s" % MXCUBE_ROOT)

sys.path.insert(0, MXCUBE_ROOT)
MXCUBE_GUI_FILE = os.path.join(MXCUBE_ROOT,
                               "ExampleFiles/example_mxcube_qt4.yml")
hr_server = os.path.join(MXCUBE_ROOT,
                         "HardwareRepository/configuration/xml-qt")
os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server

from BlissFramework import Qt4_startGUI
Qt4_startGUI.run(MXCUBE_GUI_FILE)
