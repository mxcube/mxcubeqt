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

# The version is updated automatically with bumpversion
# Do not update manually
__version__ = '0.0.1'

import os
import sys
import types
import fcntl
import string
import logging
from logging.handlers import TimedRotatingFileHandler
import tempfile
import platform
from optparse import OptionParser
from pkg_resources import resource_filename, resource_string

import gevent
import gevent.monkey

gevent.monkey.patch_all(thread=False)

from mxcubecore import HardwareRepository as HWR
from mxcubeqt.utils import gui_log_handler, error_handler, qt_import
from mxcubeqt.gui_supervisor import (
    GUISupervisor,
    LOAD_GUI_EVENT,
    get_splash_screen,
    set_splash_screen,
)

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


STD_BRICKS_LOCATION = "mxcubeqt.bricks"
BRICKS_DIR_LIST = []
LOG_FORMATTER = logging.Formatter(
    "%(asctime)s |%(name)-5s|%(levelname)-7s| %(message)s"
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


for logger_name in ("matplotlib", "PyMca5"):
    logging.getLogger(logger_name).setLevel(logging.WARNING)


SPLASH_SCREEN = None

LOGGING_NAME = ""

#MXCUBEQT_ROOT = os.path.dirname(__file__)
#sys.path.insert(0, MXCUBEQT_ROOT)

#MOCKUP_CONFIG_PATH = os.path.join(MXCUBEQT_ROOT, "example_config.yml")
MOCKUP_CONFIG_PATH = resource_filename('mxcubeqt', 'configuration/mockup.yml')

path = []
for p in ['configuration/mockup', 'configuration/mockup/qt']:
    path.append(resource_filename('mxcubecore', p))

MOCKUP_CORE_CONFIG_PATH = ":".join(path)

def get_splash():
    return get_splash_screen()


def set_splash(screen):
    set_splash_screen(screen)


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
    if root[root.rfind("/") :] != "/__pycache__" and root != base_bricks_path:
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
    LOGGER.info("Logging to file %s" % filename)

    LOGGER.removeHandler(HWR_LOG_HANDLER)
    # _hdlr = RotatingFileHandler(filename, 'a', 1048576, 10) #1 MB by file,
    # 10 files max.
    HWR_LOG_HANDLER = TimedRotatingFileHandler(filename, when="midnight", backupCount=1)
    os.chmod(filename, 0o666)
    HWR_LOG_HANDLER.setFormatter(LOG_FORMATTER)
    LOGGER.addHandler(HWR_LOG_HANDLER)


def do_gevent():
    """Can't call gevent.run inside inner event loops (message boxes...)"""

    if qt_import.QEventLoop():
        try:
            gevent.wait(timeout=0.01)
        except AssertionError:
            pass
    else:
        # all that I tried with gevent here fails! => seg fault
        pass


class MyCustomEvent(qt_import.QEvent):
    """Custom event"""

    def __init__(self, event_type, data):
        """init"""

        qt_import.QEvent.__init__(self, event_type)
        self.data = data


def create_app(gui_config_path=None, core_config_path=None):
    """Main run method"""

    parser = OptionParser(usage="usage: %prog <gui definition file> <core configuration paths> [options]")
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
        "--guiConfigPath",
        action="store",
        type="string",
        help="Path to the mxcube gui configuration file "
        + "Alternatively MXCUBE_GUI_CONFIG_PATH env variable"
        + "can be used",
        metavar="directory",
        dest="guiConfigPath",
        default="",
    )

    parser.add_option(
        "",
        "--coreConfigPath",
        action="store",
        type="string",
        help="Path to the directory containing mxcubecore "
        + "configuration files. "
        + "Alternatively MXCUBE_CORE_CONFIG_PATH env variable"
        + "can be used",
        dest="coreConfigPath",
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
        help="Start mxcube in design mode",
    )
    parser.add_option(
        "-m",
        "",
        action="store_true",
        dest="showMaximized",
        default=False,
        help="Maximize main window",
    )
    parser.add_option(
        "",
        "--no-border",
        action="store_true",
        dest="noBorder",
        default=False,
        help="Does not show borders on main window",
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
        "-v",
        "--version",
        action="store_true",
        default=False,
        dest="version",
        help="Shows version",
    )
    parser.add_option(
        "",
        "--mockupMode",
        action="store_true",
        default=False,
        dest="mockupMode",
        help="Runs MXCuBE with mockup configuration",
    )
    parser.add_option(
        "",
        "--pyqt4",
        action="store_true",
        default=None,
        help="Force to use PyQt4"
    )
    parser.add_option(
        "",
        "--pyqt5",
        action="store_true",
        default=None,
        help="Force to use PyQt5"
    )
    parser.add_option(
        "",
        "--pyside",
        action="store_true",
        default=None,
        help="Force to use PySide"
    )

    (opts, args) = parser.parse_args()

    if opts.version:
        from mxcubeqt import __version__
        print(__version__)
        exit(0)

    log_file = start_log(opts.logFile, opts.logLevel)
    log_template = opts.logTemplate
    hwobj_directories = opts.hardwareObjectsDirs.split(os.path.pathsep)
    custom_bricks_directories = opts.bricksDirs.split(os.path.pathsep)
    user_file_dir = opts.userFileDir or os.path.join(os.environ["HOME"], ".mxcube")
    app_style = opts.appStyle

    if not gui_config_path:
        if opts.guiConfigPath:
            gui_config_path = opts.guiConfigPath
        elif opts.mockupMode:
            gui_config_path = MOCKUP_CONFIG_PATH
        else:
            gui_config_path = os.environ.get("MXCUBE_GUI_CONFIG_PATH")

    if not core_config_path:
        if opts.coreConfigPath:
            core_config_path = opts.coreConfigPath
        elif opts.mockupMode:
            core_config_path = MOCKUP_CORE_CONFIG_PATH
        else:
            # try to set Hardware Repository server from environment
            core_config_path = os.environ.get("MXCUBE_CORE_CONFIG_PATH")

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

    main_application = qt_import.QApplication([])
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
                "ps -aef | grep 'python' -i | grep 'mxcubecore'"
                + "  | grep -v 'grep' | awk '{ print $3 }'"
            )
            .read()
            .strip()
            .split("\n")
        )
        > 1
    ):
        qt_import.QMessageBox.warning(
            None,
            "Warning",
            "Another instance of MXCuBE is running.\n",
            qt_import.QMessageBox.Ok,
        )
        # sys.exit(1)

    # configure modules
    if hwobj_directories:
        # Must be done before init_hardware_repository
        HWR.add_hardware_objects_dirs(hwobj_directories)
    HWR.init_hardware_repository(core_config_path)
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
    if opts.designMode:
        HWR_LOGGER.info("Starting MXCuBE Qt in designer mode...")
    else:
        HWR_LOGGER.info("Starting MXCuBE Qt...")
    HWR_LOGGER.info("GUI file: %s" % (gui_config_path or "unnamed"))
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
            "%d.%d.%d" % tuple(qt_import.qt_version_no),
            qt_import.qt_variant,
            "%d.%d.%d" % tuple(qt_import.pyqt_version_no),
        )
    )
    if qt_import.mpl_imported:
        HWR_LOGGER.info(
            "    - Matplotlib %s" % "%d.%d.%d" % tuple(qt_import.mpl_version_no)
        )
    else:
        HWR_LOGGER.info("    - Matplotlib not available")
    HWR_LOGGER.info(
        "------------------------------------------------------------------------------"
    )

    qt_import.QApplication.setDesktopSettingsAware(False)

    main_application.lastWindowClosed.connect(main_application.quit)
    supervisor = GUISupervisor(
        design_mode=opts.designMode,
        show_maximized=opts.showMaximized,
        no_border=opts.noBorder,
    )

    supervisor.set_user_file_directory(user_file_dir)
    # post event for GUI creation
    main_application.postEvent(
        supervisor, MyCustomEvent(LOAD_GUI_EVENT, gui_config_path)
    )

    # redirect errors to logger
    error_handler.enable_std_err_redirection()

    gevent_timer = qt_import.QTimer()
    gevent_timer.timeout.connect(do_gevent)
    gevent_timer.start(0)

    palette = main_application.palette()
    palette.setColor(qt_import.QPalette.ToolTipBase, qt_import.QColor(255, 241, 204))
    palette.setColor(qt_import.QPalette.ToolTipText, qt_import.Qt.black)
    main_application.setPalette(palette)

    main_application.setOrganizationName("MXCuBE")
    main_application.setOrganizationDomain("https://github.com/mxcube")
    main_application.setApplicationName("MXCuBE")
    # app.setWindowIcon(qt_import.QIcon("images/icon.png"))

    import logging
    log = logging.getLogger("HWR")

    try:
        main_application.exec_()
    except Exception:
        log.debug(" quitting on exception")
        import traceback
        traceback.print_exc()
    else:
        log.debug(" quitting on normal exit")

    supervisor.finalize()

    if log_lockfile is not None:
        filename = log_lockfile.name
        try:
            log_lockfile.close()
            os.unlink(filename)
        except BaseException:
            logging.getLogger().exception("Problem removing the log lock file")

    return main_application


def start_log(logfile, loglevel):
    if not logfile:
        logfile = os.environ.get("MXCUBE_LOG_FILE", "")

    log_level = getattr(logging, loglevel)
    logging.getLogger().setLevel(log_level)

    return logfile

if __name__ == "__main__":
    app = create_app()
