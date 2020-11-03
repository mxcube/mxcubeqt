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

import os
import sys
import types
import fcntl
import string
import logging
import tempfile
import platform
from optparse import OptionParser

import gevent
import gevent.monkey
gevent.monkey.patch_all(thread=False)

from gui.gui_supervisor import GUISupervisor, LOAD_GUI_EVENT
from gui.utils import gui_log_handler, ErrorHandler, QtImport
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"



STD_BRICKS_LOCATION = "gui.bricks"
BRICKS_DIR_LIST = []
LOG_FORMATTER = logging.Formatter(
    '%(asctime)s |%(name)-5s|%(levelname)-7s| %(message)s'
    )

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
HWR_LOGGER = logging.getLogger("HWR")

for handler in HWR_LOGGER.handlers:
    HWR_LOGGER.removeHandler(handler)

GUI_LOG_HANDLER = gui_log_handler.GUILogHandler()
LOGGER.addHandler(GUI_LOG_HANDLER)


HWR_LOG_HANDLER = logging.StreamHandler(sys.stdout)
HWR_LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(HWR_LOG_HANDLER)

mpl_logger = logging.getLogger("matplotlib")
mpl_logger.setLevel(logging.WARNING)

SPLASH_SCREEN = None

LOGGING_NAME = ""

mxcube_root = os.path.dirname(__file__)
sys.path.insert(0, mxcube_root)


def get_base_bricks_path():
    std_bricks_pkg = __import__(STD_BRICKS_LOCATION, globals(), locals(), [""])
    return os.path.dirname(std_bricks_pkg.__file__)

def add_custom_bricks_dirs(bricks_dirs):

    global BRICKS_DIR_LIST

    if isinstance(bricks_dirs, list):
        new_bricks_dirs = list(
            filter(os.path.isdir, list(map(os.path.abspath, bricks_dirs)))
        )

        for new_brick_dir in reversed(new_bricks_dirs):
            if not new_brick_dir in sys.path:
                # print 'inserted in sys.path = %s' % new_brick_dir
                sys.path.insert(0, new_brick_dir)

        BRICKS_DIR_LIST += new_bricks_dirs

base_bricks_path = get_base_bricks_path()
sys.path.insert(0, base_bricks_path)
# add 'EMBL' 'ESRF' 'ALBA' ... subfolders to path
for root, dirs, files in os.walk(base_bricks_path):
    if root[root.rfind("/"):] != "/__pycache__" and root != base_bricks_path:
        sys.path.insert(0, root)

def get_custom_bricks_dirs():
    return BRICKS_DIR_LIST

def set_logging_name(name, logging_formatter=""):
    global LOG_FORMATTER, HWR_LOG_HANDLER, LOGIN_NAME
    logging_formatter.replace(" ", "")
    if logging_formatter == "":
        logging_formatter = LOG_FORMATTER
    _formatter = logging.Formatter(logging_formatter)
    HWR_LOG_HANDLER.setFormatter(LOG_FORMATTER)
    LOGIN_NAME = name

def set_log_file(filename):
    global HWR_LOG_HANDLER
    from logging.handlers import TimedRotatingFileHandler

    LOGGER.info("Logging to file %s" % filename)

    LOGGER.removeHandler(HWR_LOG_HANDLER)
    # _hdlr = RotatingFileHandler(filename, 'a', 1048576, 10) #1 MB by file,
    # 10 files max.
    HWR_LOG_HANDLER = TimedRotatingFileHandler(
        filename,
        when="midnight",
        backupCount=1)
    os.chmod(filename, 0o666)
    HWR_LOG_HANDLER.setFormatter(LOG_FORMATTER)
    LOGGER.addHandler(HWR_LOG_HANDLER)


def do_gevent():
    """Can't call gevent.run inside inner event loops (message boxes...)
    """

    if QtImport.QEventLoop():
        try:
            gevent.wait(timeout=0.01)
        except AssertionError:
            pass
    else:
        # all that I tried with gevent here fails! => seg fault
        pass

class MyCustomEvent(QtImport.QEvent):
    """Custom event"""

    def __init__(self, event_type, data):
        """init"""

        QtImport.QEvent.__init__(self, event_type)
        self.data = data


def create_app(gui_config_file=None, run_mode='prod'):
    """Main run method"""

    default_configuration_path = "localhost:hwr"
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
        + " to %s) (you can also use " % default_configuration_path
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

    parser.add_option(
        "",
        "--pyqt4",
        action="store_true",
        default=None
        )
    parser.add_option(
        "",
        "--pyqt5",
        action="store_true",
        default=None
        )
    parser.add_option(
        "",
        "--pyside",
        action="store_true",
        default=None
        )

    (opts, args) = parser.parse_args()

    log_file = start_log(opts.logFile, opts.logLevel)

    # get config from arguments
    log_template = opts.logTemplate
    hwobj_directories = opts.hardwareObjectsDirs.split(os.path.pathsep)
    custom_bricks_directories = opts.bricksDirs.split(os.path.pathsep)
    if opts.userFileDir:
        user_file_dir = opts.userFileDir
    else:
        user_file_dir = os.path.join(os.environ["HOME"], ".mxcube")

    app_style = opts.appStyle

    if opts.hardwareRepositoryServer:
        configuration_path = opts.hardwareRepositoryServer
    else:
        # try to set Hardware Repository server from environment
        configuration_path = os.environ.get("HARDWARE_REPOSITORY_SERVER")
        if configuration_path is None:
            configuration_path = default_configuration_path

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
        HWR_LOGGER.exception(
            "Unable to create user files directory: %s" % user_file_dir
        )

    custom_bricks_directories = [
        _directory for _directory in custom_bricks_directories if _directory
    ]
    hwobj_directories = [_directory for _directory in hwobj_directories if _directory]

    main_application = QtImport.QApplication([])
    if app_style:
        main_application.setStyle(app_style)

    if len(args) >= 1:
        if len(args) == 1:
            gui_config_file = os.path.abspath(args[0])
        else:
            parser.error("Too many arguments.")
            sys.exit(1)

    if (
            len(
                os.popen(
                    "ps -aef | grep 'python' -i | grep 'hardwareRepository'" +\
                    "  | grep -v 'grep' | awk '{ print $3 }'"
                )
                .read()
                .strip()
                .split("\n")
            )
            > 1
    ):
        QtImport.QMessageBox.warning(
            None,
            "Warning",
            "Another instance of MXCuBE is running.\n",
            QtImport.QMessageBox.Ok,
        )
        #sys.exit(1)

    # configure modules
    if hwobj_directories:
        # Must be done before init_hardware_repository
        HWR.add_hardware_objects_dirs(hwobj_directories)
    HWR.init_hardware_repository(configuration_path)
    HWR.set_user_file_directory(user_file_dir)
    if custom_bricks_directories:
        add_custom_bricks_dirs(custom_bricks_directories)

    log_lockfile = None

    if len(log_file) > 0:
        if gui_config_file:
            set_logging_name(os.path.basename(gui_config_file), log_template)

        log_lock_filename = os.path.join(
            tempfile.gettempdir(), ".%s.lock" % os.path.basename(log_file)
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
            logfile_details = os.path.splitext(log_file)
            log_file = ""
            while index < 10:
                log_file2 = "%s.%d%s" % (logfile_details[0], index, logfile_details[1])
                log_lock_filename2 = os.path.join(
                    tempfile.gettempdir(), ".%s.lock" % os.path.basename(log_file2)
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
                    log_file = log_file2
                    break
            index += 1

        set_log_file(log_file)

    HWR_LOGGER.info(
        "=============================================================================="
    )
    HWR_LOGGER.info("Starting MXCuBE Qt")


    # log startup details
    # logging.getLogger().info("\n\n\n\n")
    HWR_LOGGER.info("Starting to load gui...")
    HWR_LOGGER.info("GUI file: %s" % (gui_config_file or "unnamed"))
    if len(log_file) > 0:
        HWR_LOGGER.info("Log file: %s" % log_file)
    HWR_LOGGER.info("User file directory: %s" % user_file_dir)
    HWR_LOGGER.info("System info:")
    HWR_LOGGER.info(
        "    - Python %s on %s" % (platform.python_version(), platform.system())
    )
    HWR_LOGGER.info(
        "    - Qt %s - %s %s"
        % (
            "%d.%d.%d" % tuple(QtImport.qt_version_no),
            QtImport.qt_variant,
            "%d.%d.%d" % tuple(QtImport.pyqt_version_no),
        )
    )
    if QtImport.mpl_imported:
        HWR_LOGGER.info(
            "    - Matplotlib %s" % "%d.%d.%d" % tuple(QtImport.mpl_version_no)
        )
    else:
        HWR_LOGGER.info("    - Matplotlib not available")
    HWR_LOGGER.info(
        "------------------------------------------------------------------------------"
    )

    QtImport.QApplication.setDesktopSettingsAware(False)

    main_application.lastWindowClosed.connect(main_application.quit)
    supervisor = GUISupervisor(
        design_mode=opts.designMode,
        show_maximized=opts.showMaximized,
        no_border=opts.noBorder,
    )

    supervisor.set_user_file_directory(user_file_dir)
    # post event for GUI creation
    main_application.postEvent(
        supervisor,
        MyCustomEvent(
            LOAD_GUI_EVENT,
            gui_config_file
            )
    )

    # redirect errors to logger
    ErrorHandler.enable_std_err_redirection()

    gevent_timer = QtImport.QTimer()
    gevent_timer.timeout.connect(do_gevent)
    gevent_timer.start(0)

    palette = main_application.palette()
    palette.setColor(QtImport.QPalette.ToolTipBase, QtImport.QColor(255, 241, 204))
    palette.setColor(QtImport.QPalette.ToolTipText, QtImport.Qt.black)
    main_application.setPalette(palette)

    main_application.setOrganizationName("MXCuBE")
    main_application.setOrganizationDomain("https://github.com/mxcube")
    main_application.setApplicationName("MXCuBE")
    # app.setWindowIcon(QtImport.QIcon("images/icon.png"))
    
    supervisor.finalize()
    #main_application.exec_()

    
    """
    if log_lockfile is not None:
        filename = log_lockfile.name
        try:
            log_lockfile.close()
            os.unlink(filename)
        except BaseException:
            logging.getLogger().exception("Problem removing the log lock file")
    """
    
    return main_application


def start_log(logfile, loglevel):
    if not logfile:
        logfile = os.environ.get("MXCUBE_LOG_FILE", "")

    log_level = getattr(logging, loglevel)
    logging.getLogger().setLevel(log_level)

    return logfile


if __name__ == "__main__":
    app = create_app()
    app.exec_()