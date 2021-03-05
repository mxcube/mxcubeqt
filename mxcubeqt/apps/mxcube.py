#!/usr/bin/env python
import sys
import os

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))
# print('MXCUBE_ROOT: %s' % MXCUBE_ROOT)

MXCUBE_GUI_FILE = os.environ.get('MXCUBE_GUI_FILE')
if not MXCUBE_GUI_FILE:
    MXCUBE_GUI_FILE = os.path.join(MXCUBE_ROOT,
                                   "mxcubeqt/examples/example_mxcube_gui.yml")

if not os.environ.get('HARDWARE_REPOSITORY_SERVER'):
    hr_server = "%s%s%s" % (
        os.path.join(MXCUBE_ROOT, "HardwareRepository/configuration/mockup/qt"),
        os.path.pathsep,
        os.path.join(MXCUBE_ROOT, "HardwareRepository/configuration/mockup/")
    )
    os.environ['HARDWARE_REPOSITORY_SERVER'] = hr_server

# print('MXCUBE_GUI_FILE: %s' % MXCUBE_GUI_FILE)


def run():
    from mxcubeqt import create_app
    app = create_app(MXCUBE_GUI_FILE)


if __name__ == '__main__':
    run()