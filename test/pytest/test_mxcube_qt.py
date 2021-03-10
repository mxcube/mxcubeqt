#!/usr/bin/env python
import sys
import os
import gevent

MXCUBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
MXCUBE_GUI_FILE = os.path.join(MXCUBE_ROOT,
                               "mxcubeqt/example_config.yml")
def close_app():
    sys.exit(0)


from mxcubeqt import create_app

gevent.spawn_later(10, close_app)
app = create_app(MXCUBE_GUI_FILE)
