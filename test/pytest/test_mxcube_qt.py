#!/usr/bin/env python
import sys
import os
import gevent

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
HWR_DIR = os.path.join(MXCUBE_ROOT, "mxcubecore")

print("MXCuBE root: %s" % MXCUBE_ROOT)

sys.path.insert(0, MXCUBE_ROOT)
MXCUBE_GUI_FILE = os.path.join(MXCUBE_ROOT,
                               "configuration/example_mxcube_gui.yml")
HWR_CONFIG = "%s%s%s" % (
    os.path.join(HWR_DIR, "configuration/mockup"),
    os.path.pathsep,
    os.path.join(HWR_DIR, "configuration/mockup/qt")
)
                               
os.environ['HARDWARE_REPOSITORY_SERVER'] = HWR_CONFIG

def close_app():
    sys.exit(0)

gevent.spawn_later(10, close_app)

from gui import create_app
print("MXCuBE gui file: %s" % MXCUBE_GUI_FILE)
app = create_app(MXCUBE_GUI_FILE)
