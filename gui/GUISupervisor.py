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

"""GUISupervisor"""

import os
import stat
import json
import pickle
import logging
import collections

try:
    import ruamel.yaml as yaml
except ImportError:
    import yaml

from gui import set_splash_screen
from gui import Configuration, GUIBuilder
from gui.utils import GUIDisplay, Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget, NullBrick

from HardwareRepository import HardwareRepository as HWR

LOAD_GUI_EVENT = QtImport.QEvent.MaxUser


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class SplashScreen(QtImport.QSplashScreen):
    """Splash screen when mxcube is loading"""

    def __init__(self, pixmap):
        """Builds a splash screen with a image and a progressbar"""

        QtImport.QSplashScreen.__init__(self, pixmap)

        self._message = ""
        self.gui_name = None

        self.top_x = 10
        self.top_y = 430
        self.right_x = 390
        self.pxsize = 11

        self.progress_bar = QtImport.QProgressBar(self)

        new_palette = QtImport.QPalette()
        new_palette.setColor(QtImport.QPalette.Highlight, Colors.DARK_GREEN)
        self.progress_bar.setPalette(new_palette)

        _vlayout = QtImport.QVBoxLayout(self)
        _vlayout.addWidget(self.progress_bar)

        self.repaint()

    def set_gui_name(self, name):
        """Sets gui name"""

        self.gui_name = str(name)
        if len(self.gui_name) == 0:
            self.gui_name = " "
        self.repaint()

    def set_message(self, message):
        """Adds a message to the splash screen and redraws the canvas"""
        self._message = message
        self.repaint()

    def set_progress_value(self, value):
        """Sets the progress bar value"""
        self.progress_bar.setValue(value)

    def inc_progress_value(self):
        """Increments progressbar value by 1"""
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def drawContents(self, painter):
        """draws splash screen"""

        bot_y = self.top_y + painter.fontMetrics().height()

        painter.font().setPixelSize(self.pxsize)
        painter.setPen(QtImport.QPen(QtImport.Qt.black))
        painter.drawText(
            QtImport.QRect(
                QtImport.QPoint(self.top_x, self.top_y),
                QtImport.QPoint(self.right_x, bot_y)
            ),
            QtImport.Qt.AlignLeft | QtImport.Qt.AlignTop,
            "Starting MXCuBE. Please wait...",
        )
        painter.font().setPixelSize(self.pxsize * 2.5)
        painter.font().setPixelSize(self.pxsize)

        top_y = bot_y
        bot_y += 2 + painter.fontMetrics().height()
        painter.drawText(
            QtImport.QRect(
                QtImport.QPoint(self.top_x, top_y),
                QtImport.QPoint(self.right_x, bot_y)
            ),
            QtImport.Qt.AlignLeft | QtImport.Qt.AlignBottom,
            self._message,
        )
        self.progress_bar.setGeometry(10, self.top_y + 50, self.right_x, 20)

class GUISupervisor(QtImport.QWidget):
    """GUI supervisor"""

    brickChangedSignal = QtImport.pyqtSignal(str, str, str, tuple, bool)
    tabChangedSignal = QtImport.pyqtSignal(str, int)

    def __init__(self, design_mode=False, show_maximized=False, no_border=False):
        """Main mxcube gui widget"""

        QtImport.QWidget.__init__(self)

        self.framework = None
        self.gui_config_file = None
        self.user_file_dir = None
        self.configuration = None
        self.user_settings = None

        self.launch_in_design_mode = design_mode
        self.hardware_repository = HWR.getHardwareRepository()
        self.show_maximized = show_maximized
        self.no_border = no_border
        self.windows = []

        self.splash_screen = SplashScreen(Icons.load_pixmap("splash"))

        set_splash_screen(self.splash_screen)
        self.splash_screen.show()

        self.time_stamp = 0

    def set_user_file_directory(self, user_file_directory):
        """Sets user file directory"""
        self.user_file_dir = user_file_directory
        BaseWidget.set_user_file_directory(user_file_directory)

    def load_gui(self, gui_config_file):
        """Loads gui"""
        self.configuration = Configuration.Configuration()
        self.gui_config_file = gui_config_file
        load_from_dict = gui_config_file.endswith(".json") or gui_config_file.endswith(
            ".yml"
        )

        if self.gui_config_file:
            if hasattr(self, "splash_screen"):
                self.splash_screen.set_gui_name(
                    os.path.splitext(os.path.basename(gui_config_file))[0]
                )

            if os.path.exists(gui_config_file):
                filestat = os.stat(gui_config_file)
                self.time_stamp = filestat[stat.ST_MTIME]

                if filestat[stat.ST_SIZE] == 0:
                    return self.new_gui()

                try:
                    gui_file = open(gui_config_file)
                except BaseException:
                    logging.getLogger().exception(
                        "Cannot open file %s", gui_config_file
                    )
                    QtImport.QMessageBox.warning(
                        self,
                        "Error",
                        "Could not open file %s !" % gui_config_file,
                        QtImport.QMessageBox.Ok,
                    )
                else:
                    # find mnemonics to speed up loading
                    # (using the 'require' feature from Hardware Repository)

                    def __get_mnemonics(items_list):
                        """Gets mnemonics"""

                        mne_list = []

                        for item in items_list:
                            if "brick" in item:
                                try:
                                    if load_from_dict:
                                        props = item["properties"]
                                    else:
                                        props = pickle.loads(item["properties"])
                                except BaseException:
                                    logging.getLogger().exception(
                                        "Could not load properties for %s"
                                        % item["name"]
                                    )
                                else:
                                    item["properties"] = props
                                    try:
                                        for prop in props:
                                            if load_from_dict:
                                                prop_value = prop["value"]
                                            else:
                                                prop_value = prop.get_value()
                                            if isinstance(
                                                    prop_value, type("")
                                            ) and prop_value.startswith("/"):
                                                mne_list.append(prop_value)
                                    except BaseException:
                                        logging.exception(
                                            "Could not "
                                            + "build list of required "
                                            + "hardware objects"
                                        )

                                continue

                            mne_list += __get_mnemonics(item["children"])

                        return mne_list

                    failed_msg = (
                        "Cannot read configuration from file %s. " % gui_config_file
                    )
                    failed_msg += "Starting in designer mode with clean GUI."

                    try:
                        if gui_config_file.endswith(".json"):
                            raw_config = json.load(gui_file)
                        elif gui_config_file.endswith(".yml"):
                            raw_config = yaml.safe_load(gui_file)
                        else:
                            raw_config = eval(gui_file.read())
                    except BaseException:
                        logging.getLogger().exception(failed_msg)

                    self.splash_screen.set_message("Gathering H/O info...")
                    self.splash_screen.set_progress_value(10)
                    mnemonics = __get_mnemonics(raw_config)
                    self.hardware_repository.require(mnemonics)
                    gui_file.close()

                    try:
                        self.splash_screen.set_message("Building GUI configuration...")
                        self.splash_screen.set_progress_value(20)
                        config = Configuration.Configuration(raw_config)
                    except BaseException:
                        logging.getLogger("GUI").exception(failed_msg)
                        QtImport.QMessageBox.warning(
                            self, "Error", failed_msg, QtImport.QMessageBox.Ok
                        )
                    else:
                        self.configuration = config

                    try:
                        user_settings_filename = os.path.join(
                            self.user_file_dir, "settings.dat"
                        )
                        user_settings_file = open(user_settings_filename)
                        self.user_settings = eval(user_settings_file.read())
                    except BaseException:
                        self.user_settings = []
                        logging.getLogger().error(
                            "Unable to read user settings file: %s"
                            % user_settings_filename
                        )
                    else:
                        user_settings_file.close()

                    if len(self.configuration.windows) == 0:
                        return self.new_gui()

                    #self.hardware_repository.printReport()

                    if self.launch_in_design_mode:
                        self.framework = GUIBuilder.GUIBuilder()

                        QtImport.QApplication.setActiveWindow(self.framework)

                        self.framework.filename = gui_config_file
                        self.framework.configuration = config
                        self.framework.setWindowTitle(
                            "GUI Builder - %s" % gui_config_file
                        )
                        self.framework.gui_editor_window.set_configuration(config)
                        self.framework.gui_editor_window.draw_window_preview()
                        self.framework.show()

                        return self.framework
                    else:
                        main_window = self.execute(self.configuration)
                        return main_window

        return self.new_gui()

    def new_gui(self):
        """Starts new gui"""

        self.time_stamp = 0
        self.launch_in_design_mode = True

        self.framework = GUIBuilder.GUIBuilder()

        QtImport.QApplication.setActiveWindow(self.framework)
        self.framework.show()
        self.framework.new_clicked(self.gui_config_file)

        return self.framework

    def display(self):
        """Shows all defined windows"""
        self.windows = []
        for window in self.configuration.windows_list:
            display = GUIDisplay.WindowDisplayWidget(
                None, window["name"], execution_mode=True, no_border=self.no_border
            )
            self.windows.append(display)
            display.set_caption(window["properties"]["caption"])
            display.draw_preview(window, id(display))
            display.close_on_exit = window["properties"]["closeOnExit"]
            display.set_keep_open(window["properties"]["keepOpen"])
            display.set_font_size(window["properties"]["fontSize"])

            if window["properties"]["show"]:
                display._show = True
            else:
                display._show = False
            display.hide()

            for item in self.user_settings:
                if item["name"] == window["name"]:
                    display.move(item["posx"], item["posy"])
                    display.resize(item["width"], item["height"])

        for window in self.windows:
            window.append_windows_links(self.windows)

    def execute(self, config):
        """Start in execution mode"""
        self.splash_screen.set_message("Executing configuration...")
        self.splash_screen.set_progress_value(90)
        self.display()

        main_window = None

        if len(self.windows) > 0:
            main_window = self.windows[0]
            main_window.configuration = config
            QtImport.QApplication.setActiveWindow(main_window)
            if self.no_border:
                main_window.move(0, 0)
                width = QtImport.QApplication.desktop().width()
                height = QtImport.QApplication.desktop().height()
                main_window.resize(QtImport.QSize(width, height))

            # make connections
            widgets_dict = dict(
                [
                    (
                        isinstance(w.objectName, collections.Callable)
                        and str(w.objectName())
                        or None,
                        w,
                    )
                    for w in QtImport.QApplication.allWidgets()
                ]
            )

            def make_connections(items_list):
                """Creates connections"""

                for item in items_list:
                    try:
                        sender = widgets_dict[item["name"]]
                    except KeyError:
                        logging.getLogger().error(
                            "Could not find receiver widget %s" % item["name"]
                        )
                    else:
                        for connection in item["connections"]:
                            _receiver = (
                                connection["receiver"] or connection["receiverWindow"]
                            )
                            try:
                                receiver = widgets_dict[_receiver]
                            except KeyError:
                                logging.getLogger().error(
                                    "Could not find " + "receiver widget %s", _receiver
                                )
                            else:
                                try:
                                    slot = getattr(receiver, connection["slot"])
                                    # etattr(sender, connection["signal"]).connect(slot)
                                except AttributeError:
                                    logging.getLogger().error(
                                        "No slot '%s' " % connection["slot"]
                                        + "in receiver %s" % _receiver
                                    )
                                else:
                                    if not isinstance(sender, NullBrick):
                                        getattr(sender, connection["signal"]).connect(slot)
                                    # sender.connect(sender,
                                    #    QtCore.SIGNAL(connection["signal"]),
                                    #    slot)
                    make_connections(item["children"])

            self.splash_screen.set_progress_value(95)
            self.splash_screen.set_message("Connecting bricks...")
            make_connections(config.windows_list)

            # set run mode for every brick
            self.splash_screen.set_progress_value(100)
            self.splash_screen.set_message("Setting run mode...")
            BaseWidget.set_run_mode(True)

            if self.show_maximized:
                main_window.showMaximized()
            else:
                main_window.show()

            for window in self.windows:
                if window._show:
                    window.show()

        if BaseWidget._menubar:
            BaseWidget._menubar.set_exp_mode(False)

        return main_window

    def finalize(self):
        """Finalize gui load"""

        BaseWidget.set_run_mode(False)  # call .stop() for each brick

        self.hardware_repository.close()

        QtImport.QApplication.sendPostedEvents()
        QtImport.QApplication.processEvents()

        self.save_size()

    def save_size(self):
        """Saves window size and coordinates in the gui file"""
        display_config_list = []

        if not self.launch_in_design_mode:
            for window in self.windows:
                window_cfg = self.configuration.windows[str(window.objectName())]
                display_config_list.append(
                    {
                        "name": window_cfg.name,
                        "posx": window.x(),
                        "posy": window.y(),
                        "width": window.width(),
                        "height": window.height(),
                    }
                )
            try:
                user_settings_filename = os.path.join(
                    self.user_file_dir, "settings.dat"
                )
                user_settings_file = open(user_settings_filename, "w")
                user_settings_file.write(repr(display_config_list))
                os.chmod(user_settings_filename, 0o660)
            except BaseException:
                logging.getLogger().exception(
                    "Unable to save window position and size in "
                    + "configuration file: %s" % user_settings_filename
                )
            else:
                user_settings_file.close()

    def finish_init(self, gui_config_file):
        """Finalize gui init"""

        while True:
            try:
                self.hardware_repository.connect()
            except BaseException:
                logging.getLogger().exception(
                    "Timeout while trying to "
                    + "connect to Hardware Repository server."
                )
                message = (
                    "Timeout while connecting to Hardware "
                    + "Repository server.\nMake sure the Hardware "
                    + "Repository Server is running on host:\n%s."
                    % str(self.hardware_repository.serverAddress).split(":")[0]
                )
                if (
                    QtImport.QMessageBox.warning(
                        self,
                        "Cannot connect to Hardware Repository",
                        message,
                        QtImport.QMessageBox.Retry
                        | QtImport.QMessageBox.Cancel
                        | QtImport.QMessageBox.NoButton,
                    )
                    == QtImport.QMessageBox.Cancel
                ):
                    logging.getLogger().warning(
                        "Gave up trying to " + "connect to Hardware Repository server."
                    )
                    break
            else:
                logging.getLogger().info(
                    "Connected to Hardware "
                    + "Repository server %s" % self.hardware_repository.serverAddress
                )
                break

        try:
            main_widget = None
            main_widget = self.load_gui(gui_config_file)
            if main_widget:
                set_splash_screen(None)
                self.splash_screen.finish(main_widget)
            del self.splash_screen
        except BaseException:
            logging.getLogger().exception("exception while loading GUI file")
            QtImport.QApplication.exit()

    def customEvent(self, event):
        """Custom event"""

        self.finish_init(event.data)
