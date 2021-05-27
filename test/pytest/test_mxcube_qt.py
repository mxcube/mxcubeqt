#!/usr/bin/env python
import sys
import os
import gevent

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))
MXCUBE_GUI_FILE = os.path.join(
        ROOT_DIR,
        "mxcube/mxcubeqt/example_config.yml"
        )
MXCUBE_CORE_CONFIG_PATH = "%s:%s" % (
        os.path.join(
            ROOT_DIR,
            "mxcubecore/mxcubecore/configuration/mockup"
            ),
        os.path.join(
            ROOT_DIR,
            "mxcubecore/mxcubecore/configuration/mockup/test"
            )
        )


def close_app():
    sys.exit(0)


from mxcubeqt import create_app

gevent.spawn_later(10, close_app)
app = create_app(MXCUBE_GUI_FILE, MXCUBE_CORE_CONFIG_PATH)
