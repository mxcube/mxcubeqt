#!/usr/bin/env python

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
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from HardwareRepository import HardwareRepository
from gui.utils import GUILogHandler
from gui.utils import ErrorHandler
from gui import GUISupervisor
import gui
from QtImport import *
from optparse import OptionParser

"""MXCuBE main application"""

import gevent
import fcntl
import tempfile
import sys
import os
import logging
import platform

import gevent.monkey

gevent.monkey.patch_all(thread=False)


# from gui.Utils import terminal_server


_logger = logging.getLogger()
_GUIhdlr = GUILogHandler.GUILogHandler()
_logger.addHandler(_GUIhdlr)


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"
__version__ = 2


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


def run(gui_config_file=None):
    """Main run method"""

    default_hwr_server = "localhost:hwr"
    # path to user's home dir. (works on Win2K, XP, Unix, Mac...)
    parser = OptionParser(usage="usage: %prog <GUI definition file> [options]")
    parser.add_option(
        "",
        "--logFile",
        action="store",
        type="string",
        help="Log file",
        dest="logFile",
        metavar="FILE",
        default="",
    )
    parser.add_option(
        "",
        "--logLevel",
        action="store",
        type="string",
        help="Log level",
        dest="logLevel",
        default="INFO",
    )
    parser.add_option(
        "",
        "--logTemplate",
        action="store",
        type="string",
        help="Log template",
        dest="logTemplate",
        default="",
    )
    parser.add_option(
        "",
        "--bricksDirs",
        action="store",
        type="string",
        help="Additional directories for bricks search "
        + "path (you can also use the CUSTOM_BRICKS_PATH "
        + "environment variable)",
        dest="bricksDirs",
        metavar="dir1" + os.path.pathsep + "dir2...dirN",
        default="",
    )
    parser.add_option(
        "",
        "--hardwareRepository",
        action="store",
        type="string",
        help="Hardware Repository Server host:port (default"
        + " to %s) (you can also use " % default_hwr_server
        + "HARDWARE_REPOSITORY_SERVER the environment variable)",
        metavar="HOST:PORT",
        dest="hardwareRepositoryServer",
        default="",
    )
    parser.add_option(
        "",
        "--hardwareObjectsDirs",
        action="store",
        type="string",
        help="Additional directories for "
        + "Hardware Objects search path (you can also use "
        + "the CUSTOM_HARDWARE_OBJECTS_PATH environment "
        + "variable)",
        dest="hardwareObjectsDirs",
        metavar="dir1" + os.path.pathsep + "dir2...dirN",
        default="",
    )
    parser.add_option(
        "-d",
        "",
        action="store_true",
        dest="designMode",
        default=False,
        help="start GUI in Design mode",
    )
    parser.add_option(
        "-m",
        "",
        action="store_true",
        dest="showMaximized",
        default=False,
        help="maximize main window",
    )
    parser.add_option(
        "",
        "--no-border",
        action="store_true",
        dest="noBorder",
        default=False,
        help="does not show borders on main window",
    )
    parser.add_option(
        "",
        "--style",
        action="store",
        type="string",
        help="Visual style of the application (windows, motif,"
        + "cde, plastique, windowsxp, or macintosh)",
        dest="appStyle",
        default=None,
    )
    parser.add_option(
        "",
        "--userFileDir",
        action="store",
        type="string",
        help="User settings file stores application related settings "
        + "(window size and position). If not defined then user home "
        + "directory is used",
        dest="userFileDir",
        default=None,
    )

    parser.add_option("", "--pyqt4", action="store_true", default=None)
    parser.add_option("", "--pyqt5", action="store_true", default=None)
    parser.add_option("", "--pyside", action="store_true", default=None)

    (opts, args) = parser.parse_args()

    # get config from arguments
    logFile = opts.logFile
    log_template = opts.logTemplate
    hwobj_directories = opts.hardwareObjectsDirs.split(os.path.pathsep)
    custom_bricks_directories = opts.bricksDirs.split(os.path.pathsep)
    if opts.userFileDir:
        user_file_dir = opts.userFileDir
    else:
        user_file_dir = os.path.join(os.environ["HOME"], ".mxcube")

    app_style = opts.appStyle

    if opts.hardwareRepositoryServer:
        hwr_server = opts.hardwareRepositoryServer
    else:
        # try to set Hardware Repository server from environment
        hwr_server = os.environ.get("HARDWARE_REPOSITORY_SERVER")
        if hwr_server is None:
            hwr_server = default_hwr_server

    # add bricks directories and hardware objects directories from environment
    try:
        custom_bricks_directories += os.environ.get("CUSTOM_BRICKS_PATH", "").split(
            os.path.pathsep
        )
    except KeyError:
        pass

    try:
        hwobj_directories += os.environ.get("CUSTOM_HARDWARE_OBJECTS_PATH", "").split(
            os.path.pathsep
        )
    except KeyError:
        pass

    try:
        if not os.path.exists(user_file_dir):
            os.makedirs(user_file_dir)
    except BaseException:
        logging.getLogger().exception(
            "Unable to create user files directory: %s" % user_file_dir
        )

    custom_bricks_directories = [
        _directory for _directory in custom_bricks_directories if _directory
    ]
    hwobj_directories = [_directory for _directory in hwobj_directories if _directory]

    main_application = QApplication([])
    if app_style:
        main_application.setStyle(app_style)
    lockfile = None

    if len(args) >= 1:
        if len(args) == 1:
            gui_config_file = os.path.abspath(args[0])
        else:
            parser.error("Too many arguments.")
            sys.exit(1)

    if (
        len(
            os.popen(
                "ps -aef | grep 'python' -i | grep 'hardwareRepository'  | grep -v 'grep' | awk '{ print $3 }'"
            )
            .read()
            .strip()
            .split("\n")
        )
        > 1
    ):
        QMessageBox.warning(
            None,
            "Warning",
            "Another instance of MXCuBE is running.\n"
            + "Please close it and start MXCuBE again.",
            QMessageBox.Ok,
        )
        sys.exit(1)

    # configure modules
    HardwareRepository.setHardwareRepositoryServer(hwr_server)
    HardwareRepository.setUserFileDirectory(user_file_dir)
    if hwobj_directories:
        HardwareRepository.addHardwareObjectsDirs(hwobj_directories)
    if custom_bricks_directories:
        gui.addCustomBricksDirs(custom_bricks_directories)

    # set log name and log file
    if gui_config_file:
        gui.set_logging_name(os.path.basename(gui_config_file), log_template)

    log_lockfile = None
    if len(logFile) > 0:
        log_lock_filename = os.path.join(
            tempfile.gettempdir(), ".%s.lock" % os.path.basename(logFile)
        )

        log_ok = True
        try:
            log_lockfile = open(log_lock_filename, "w")
        except BaseException:
            log_ok = False
        else:
            try:
                os.chmod(log_lock_filename, 0o666)
            except BaseException:
                pass
            try:
                fcntl.lockf(log_lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BaseException:
                log_ok = False
                try:
                    log_lockfile.close()
                except BaseException:
                    pass

        if not log_ok:
            index = 1
            logfile_details = os.path.splitext(logFile)
            logFile = ""
            while index < 10:
                logFile2 = "%s.%d%s" % (logfile_details[0], index, logfile_details[1])
                log_lock_filename2 = os.path.join(
                    tempfile.gettempdir(), ".%s.lock" % os.path.basename(logFile2)
                )
                try:
                    log_lockfile = open(log_lock_filename2, "w")
                except BaseException:
                    pass
                else:
                    try:
                        os.chmod(log_lock_filename2, 0o666)
                    except BaseException:
                        pass
                    try:
                        fcntl.lockf(
                            log_lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB
                        )
                    except BaseException:
                        pass
                    else:
                        log_ok = True
                if log_ok:
                    logFile = logFile2
                    break
            index += 1

        if len(logFile) > 0:
            gui.setLogFile(logFile)

    # log startup details
    log_level = getattr(logging, opts.logLevel)
    logging.getLogger().setLevel(log_level)
    # logging.getLogger().info("\n\n\n\n")
    logging.getLogger().info(
        "================================================================================="
    )
    logging.getLogger().info("Starting MXCuBE v%s" % str(__version__))
    logging.getLogger().info("GUI file: %s" % (gui_config_file or "unnamed"))
    logging.getLogger().info("Hardware repository: %s" % hwr_server)
    logging.getLogger().info("User file directory: %s" % user_file_dir)
    if len(logFile) > 0:
        logging.getLogger().info("Log file: %s" % logFile)
    logging.getLogger().info("System info:")
    logging.getLogger().info(
        "    - Python %s on %s" % (platform.python_version(), platform.system())
    )
    logging.getLogger().info(
        "    - Qt %s - %s %s"
        % (
            "%d.%d.%d" % tuple(qt_version_no),
            qt_variant,
            "%d.%d.%d" % tuple(pyqt_version_no),
        )
    )
    if mpl_imported:
        logging.getLogger().info(
            "    - Matplotlib %s" % "%d.%d.%d" % tuple(mpl_version_no)
        )
    else:
        logging.getLogger().info("    - Matplotlib not available")
    logging.getLogger().info(
        "---------------------------------------------------------------------------------"
    )

    QApplication.setDesktopSettingsAware(False)

    main_application.lastWindowClosed.connect(main_application.quit)
    supervisor = GUISupervisor.GUISupervisor(
        design_mode=opts.designMode,
        show_maximized=opts.showMaximized,
        no_border=opts.noBorder,
    )
    supervisor.set_user_file_directory(user_file_dir)
    # post event for GUI creation
    main_application.postEvent(
        supervisor, MyCustomEvent(GUISupervisor.LOAD_GUI_EVENT, gui_config_file)
    )

    # redirect errors to logger
    ErrorHandler.enableStdErrRedirection()

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
    # app.setWindowIcon(QIcon("images/icon.png"))
    main_application.exec_()

    supervisor.finalize()

    if log_lockfile is not None:
        filename = log_lockfile.name
        try:
            log_lockfile.close()
            os.unlink(filename)
        except BaseException:
            logging.getLogger().exception("Problem removing the log lock file")


if __name__ == "__main__":
    run()
