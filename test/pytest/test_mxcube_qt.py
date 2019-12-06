#!/usr/bin/env python
import sys
import os
import gevent

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

print("MXCuBE root: %s" % MXCUBE_ROOT)

sys.path.insert(0, MXCUBE_ROOT)
MXCUBE_GUI_FILE = os.path.join(MXCUBE_ROOT,
                               "configuration/example_mxcube_gui.yml")
hr_server = os.path.join(MXCUBE_ROOT,
                         "HardwareRepository/configuration/xml-qt")
os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server

def close_app():
    sys.exit(0)

gevent.spawn_later(30, close_app)

from gui import startGUI
print("MXCuBE gui file: %s" % MXCUBE_GUI_FILE)
startGUI.run(MXCUBE_GUI_FILE)

