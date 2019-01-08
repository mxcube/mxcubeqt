#!/usr/bin/env python

#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""MXCuBE main application"""

import gevent
import fcntl
import tempfile
import sys
import os
import logging
import platform

from QtImport import *

import BlissFramework
from BlissFramework import Qt4_GUISupervisor
from BlissFramework.Utils import Qt4_ErrorHandler, Qt4_GUILogHandler, Qt4_GUITest

#from BlissFramework.Utils import terminal_server

from HardwareRepository import HardwareRepository

_logger = logging.getLogger()
_GUIhdlr = Qt4_GUILogHandler.GUILogHandler()
_logger.addHandler(_GUIhdlr)


__credits__ = ["MXCuBE colaboration"]

test_ready_event = gevent.event.Event()

def do_gevent():
    """Can't call gevent.run inside inner event loops (message boxes...)
    """

    if QEventLoop():
        try:
            gevent.wait(timeout=0.01)
        except AssertionError:
            pass
    else:
        # all that I tried with gevent here fails! => seg fault
        pass

class MyCustomEvent(QEvent):
    """Custom event"""

    def __init__(self, event_type, data):
        """init"""

        QEvent.__init__(self, event_type)
        self.data = data
    
def run_test(gui_config_file=None):
    """Main run method"""

    user_file_dir = os.path.join(os.environ["HOME"], ".mxcube")
    hwr_server = os.environ.get('HARDWARE_REPOSITORY_SERVER')

    try:
        if not os.path.exists(user_file_dir):
            os.makedirs(user_file_dir)
    except:
        logging.getLogger().exception(\
          "Unable to create user files directory: %s" % user_file_dir)

    main_application = QApplication([])
    # configure modules
    HardwareRepository.setHardwareRepositoryServer(hwr_server)
    HardwareRepository.setUserFileDirectory(user_file_dir)

    # log startup details
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().info("=================================================================================")
    logging.getLogger().info("Starting MXCuBE v%s" % "2.3.0")
    logging.getLogger().info("GUI file: %s" % (gui_config_file or "unnamed"))
    logging.getLogger().info("Hardware repository: %s" % hwr_server)
    logging.getLogger().info("System info:")
    logging.getLogger().info("    - Python %s on %s" %(platform.python_version(), platform.system()))
    logging.getLogger().info("    - Qt %s - %s %s" % \
                  ("%d.%d.%d" % tuple(qt_version_no), qt_variant, "%d.%d.%d" % tuple(pyqt_version_no)) )
    if mpl_imported:
        logging.getLogger().info("    - Matplotlib %s" % "%d.%d.%d" % tuple(mpl_version_no))
    else:
        logging.getLogger().info("    - Matplotlib not available")
    logging.getLogger().info("---------------------------------------------------------------------------------")

    QApplication.setDesktopSettingsAware(False)

    main_application.lastWindowClosed.connect(main_application.quit)
    supervisor = Qt4_GUISupervisor.GUISupervisor(design_mode=False,
        show_maximized=False, no_border=False)
    supervisor.set_user_file_directory(user_file_dir)
    # post event for GUI creation
    main_application.postEvent(supervisor,
        MyCustomEvent(Qt4_GUISupervisor.LOAD_GUI_EVENT, gui_config_file))

    gevent.spawn_later(10, Qt4_GUITest.run_test)

    # redirect errors to logger
    Qt4_ErrorHandler.enableStdErrRedirection()

    gevent_timer = QTimer()
    gevent_timer.timeout.connect(do_gevent)
    gevent_timer.start(0)

    palette = main_application.palette()
    palette.setColor(QPalette.ToolTipBase, QColor(255, 241, 204))
    palette.setColor(QPalette.ToolTipText, Qt.black)
    main_application.setPalette(palette)

    main_application.setOrganizationName("MXCuBE")
    main_application.setOrganizationDomain("https://github.com/mxcube")
    main_application.setApplicationName("MXCuBE")
    #app.setWindowIcon(QIcon("images/icon.png"))
    main_application.exec_()

    supervisor.finalize()

if __name__ == '__main__':
    run()
