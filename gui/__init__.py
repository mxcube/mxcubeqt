#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import string
import types
import logging
import gevent.monkey

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


# Relative location of
STD_BRICKS_LOCATION = "gui.bricks"

SPLASH_SCREEN = None


def set_splash_screen(screen):
    global SPLASH_SCREEN
    SPLASH_SCREEN = screen


def get_splash_screen():
    global SPLASH_SCREEN
    return SPLASH_SCREEN


_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s |%(name)-5s|%(levelname)-7s| %(message)s')

#
# log to stdout
#
_hdlr = logging.StreamHandler(sys.stdout)
_hdlr.setFormatter(_formatter)
logging.getLogger().addHandler(_hdlr)


#
# add the GUI Handler
#
#from gui.utils import GUILogHandler
#_GUIhdlr = GUILogHandler.GUILogHandler()
#_logger.addHandler(_GUIhdlr)


#
# Add path to root gui directory
#
gui_path = os.path.dirname(__file__)
sys.path.insert(0, gui_path)

def get_base_bricks_path():
    std_bricks_pkg = __import__(STD_BRICKS_LOCATION, globals(), locals(), [""])
    return os.path.dirname(std_bricks_pkg.__file__)


_bricks_dirs = []


def add_custom_bricks_dirs(bricks_dirs):

    global _bricks_dirs

    if isinstance(bricks_dirs, list):
        new_bricks_dirs = list(
            filter(os.path.isdir, list(map(os.path.abspath, bricks_dirs)))
        )

        for new_brick_dir in reversed(new_bricks_dirs):
            if not new_brick_dir in sys.path:
                # print 'inserted in sys.path = %s' % new_brick_dir
                sys.path.insert(0, new_brick_dir)

        _bricks_dirs += new_bricks_dirs


base_bricks_path = get_base_bricks_path()
sys.path.insert(0, get_base_bricks_path())
# add 'EMBL' 'ESRF' 'ALBA' ... subfolders to path
for root, dirs, files in os.walk(base_bricks_path):
    if root[root.rfind("/"):] != "/__pycache__" and root != base_bricks_path:
        sys.path.insert(0, root)


def get_custom_bricks_dirs():
    return _bricks_dirs


def _framework_trace_function(frame, event, arg):
    print("EVENT %s" % event)
    print("  { FRAME INFO }")
    print("    - filename  %s" % frame.f_code.co_filename)
    print("    - line      %d" % frame.f_lineno)
    print("    - name      %s" % frame.f_code.co_name)


logging_name = ""


def set_logging_name(name, logging_formatter=""):
    global _formatter, _hdlr, logging_name
    logging_formatter.replace(" ", "")
    if logging_formatter == "":
        logging_formatter = "%(asctime)s |%(name)-7s|%(levelname)-7s| %(message)s"
    _formatter = logging.Formatter(logging_formatter)
    _hdlr.setFormatter(_formatter)
    logging_name = name


def set_log_file(filename):
    #
    # log to rotating files
    #
    global _hdlr
    from logging.handlers import TimedRotatingFileHandler

    logging.getLogger().info("Logging to file %s" % filename)

    _logger.removeHandler(_hdlr)
    # _hdlr = RotatingFileHandler(filename, 'a', 1048576, 10) #1 MB by file,
    # 10 files max.
    _hdlr = TimedRotatingFileHandler(filename, when="midnight", backupCount=1)
    os.chmod(filename, 0o666)
    _hdlr.setFormatter(_formatter)
    _logger.addHandler(_hdlr)


#
# general framework settings
#


def set_debug_mode(on):
    if on:
        sys.settrace(_framework_trace_function)
    else:
        sys.settrace(None)
