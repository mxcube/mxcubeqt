#
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

"""GUISupervisor"""

import os
import stat
import pickle
import logging
import collections

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework import Qt4_Configuration
from BlissFramework import Qt4_GUIBuilder
from BlissFramework.Utils import Qt4_GUIDisplay
from BlissFramework.Qt4_BaseComponents import BlissWidget

from BlissFramework import set_splash_screen

from HardwareRepository import HardwareRepository

LOAD_GUI_EVENT = QEvent.MaxUser


class BlissSplashScreen(QSplashScreen):
    """Splash screen when mxcube is loading"""

    def __init__(self, pixmap):
        """init"""

        QSplashScreen.__init__(self, pixmap)

        self._message = ""
        self.gui_name = None
        self.repaint()

    def set_gui_name(self, name):
        """Sets gui name"""

        self.gui_name = str(name)
        if len(self.gui_name) == 0:
            self.gui_name = ' '
        self.repaint()

    def set_message(self, message):
        self._message = message
        self.repaint()

    def drawContents(self, painter):
        """draws splash screen"""

        top_x = 10
        top_y = 334
        right_x = 390
        bot_y = 334 + painter.fontMetrics().height()
        pxsize = 12

        painter.font().setPixelSize(pxsize)
        painter.setPen(QPen(Qt.black))
        painter.drawText(QRect(QPoint(top_x, top_y),
                         QPoint(right_x, bot_y)),
                         Qt.AlignLeft | Qt.AlignTop,
                         "Loading MXCuBE")
        painter.font().setPixelSize(pxsize * 2.5)
        painter.font().setPixelSize(pxsize)

        top_y = bot_y
        bot_y += 2 + painter.fontMetrics().height()
        painter.drawText(QRect(QPoint(top_x, top_y),
                         QPoint(right_x, bot_y)),
                         Qt.AlignLeft | Qt.AlignBottom,
                         "Please wait...")

        top_y = bot_y
        bot_y += 2 + painter.fontMetrics().height()
        painter.drawText(QRect(QPoint(top_x, top_y),
                         QPoint(right_x, bot_y)),
                         Qt.AlignLeft | Qt.AlignBottom,
                         self._message)


class GUISupervisor(QWidget):
    """GUI supervisor"""

    brickChangedSignal = pyqtSignal(str, str, str, tuple, bool)
    tabChangedSignal = pyqtSignal(str, int)

    def __init__(self, design_mode=False, show_maximized=False, no_border=False):
        """init"""

        QWidget.__init__(self)

        self.framework = None
        self.gui_config_file = None
        self.configuration = None

        self.launch_in_design_mode = design_mode
        self.hardware_repository = HardwareRepository.HardwareRepository()
        self.show_maximized = show_maximized
        self.no_border = no_border
        self.windows = []
        self.splash_screen = BlissSplashScreen(Qt4_Icons.load_pixmap('splash'))

        set_splash_screen(self.splash_screen)
        self.splash_screen.show()

        self.timestamp = 0

    def load_gui(self, gui_config_file):
        """Loads gui"""

        self.configuration = Qt4_Configuration.Configuration()
        self.gui_config_file = gui_config_file

        if self.gui_config_file:
            if hasattr(self, "splash_screen"):
                self.splash_screen.set_gui_name(os.path.splitext(\
                     os.path.basename(gui_config_file))[0])

            if os.path.exists(gui_config_file):
                filestat = os.stat(gui_config_file)
                self.timestamp = filestat[stat.ST_MTIME]

                if filestat[stat.ST_SIZE] == 0:
                    return self.new_gui()

                try:
                    gui_file = open(gui_config_file)
                except:
                    logging.getLogger().exception("Cannot open file %s",
                                                  gui_config_file)
                    QMessageBox.warning(self, "Error",
                           "Could not open file %s !" % gui_config_file,
                           QMessageBox.Ok)
                else:
                    # find mnemonics to speed up loading
                    # (using the 'require' feature from Hardware Repository)

                    def __get_mnemonics(items_list):
                        """Gets mnemonics"""

                        mne_list = []

                        for item in items_list:
                            if "brick" in item:
                                try:
                                    props = pickle.loads(item["properties"])
                                    #props = pickle.loads(item["properties"].encode('utf8'))
                                except:
                                    logging.getLogger().exception(\
                                        "Could not load properties for %s" % \
                                        item["name"])
                                else:
                                    item["properties"] = props
                                    try:
                                        for prop in props:
                                            prop_value = prop.getValue()
                                            if type(prop_value) == type('') and \
                                               prop_value.startswith("/"):
                                                mne_list.append(prop_value)
                                    except:
                                        logging.exception("Could not " + \
                                          "build list of required " + \
                                          "hardware objects")

                                continue

                            mne_list += __get_mnemonics(item["children"])

                        return mne_list

                    failed_msg = "Cannot read configuration from file %s. " % \
                                 gui_config_file
                    failed_msg += "Starting in designer mode with clean GUI."

                    try:
                        raw_config = eval(gui_file.read())
                    except:
                        logging.getLogger().exception(failed_msg)

                    self.splash_screen.set_message("Gathering H/O info...")
                    mnemonics = __get_mnemonics(raw_config)
                    self.hardware_repository.require(mnemonics)
                    gui_file.close()

                    try:
                        self.splash_screen.set_message("Building GUI configuration...")
                        config = Qt4_Configuration.Configuration(raw_config)
                    except:
                        logging.getLogger().exception(failed_msg)
                        QMessageBox.warning(self, "Error", failed_msg,
                                            QMessageBox.Ok)
                    else:
                        self.configuration = config

                    if len(self.configuration.windows) == 0:
                        return self.new_gui()

                    if self.launch_in_design_mode:
                        self.framework = Qt4_GUIBuilder.GUIBuilder()

                        QApplication.setActiveWindow(self.framework)

                        self.framework.filename = gui_config_file
                        self.framework.configuration = config
                        self.framework.setWindowTitle("GUI Builder - %s" % \
                                                      gui_config_file)
                        self.framework.gui_editor_window.\
                             set_configuration(config)
                        self.framework.gui_editor_window.draw_window_preview()
                        self.framework.show()

                        return self.framework
                    else:
                        main_window = self.execute(self.configuration)
                        return main_window

        return self.new_gui()

    def new_gui(self):
        """Starts new gui"""

        self.timestamp = 0
        self.launch_in_design_mode = True

        self.framework = Qt4_GUIBuilder.GUIBuilder()

        QApplication.setActiveWindow(self.framework)
        self.framework.show()
        self.framework.new_clicked(self.gui_config_file)

        return self.framework

    def execute(self, config):
        """Start in execution mode"""

        self.windows = Qt4_GUIDisplay.display(config,
                                              no_border=self.no_border)

        self.splash_screen.set_message("Executing configuration...")

        main_window = None

        if len(self.windows) > 0:
            main_window = self.windows[0]
            main_window.configuration = config
            QApplication.setActiveWindow(main_window)
            if self.no_border:
                main_window.move(0, 0)
                width = QApplication.desktop().width()
                height = QApplication.desktop().height()
                main_window.resize(QSize(width, height))

            # make connections
            widgets_dict = dict([(isinstance(w.objectName, \
                collections.Callable) and str(w.objectName()) or None, w) \
                for w in QApplication.allWidgets()])

            def make_connections(items_list):
                """Creates connections"""

                for item in items_list:
                    try:
                        sender = widgets_dict[item["name"]]
                    except KeyError:
                        logging.getLogger().error(\
                            "Could not find receiver widget %s" % \
                            item["name"])
                    else:
                        for connection in item["connections"]:
                            _receiver = connection["receiver"] or \
                                connection["receiverWindow"]
                            try:
                                receiver = widgets_dict[_receiver]
                            except KeyError:
                                logging.getLogger().error("Could not find " + \
                                   "receiver widget %s", _receiver)
                            else:
                                try:
                                    slot = getattr(receiver, connection["slot"])
                                    #etattr(sender, connection["signal"]).connect(slot)
                                except AttributeError:
                                    logging.getLogger().error(\
                                       "No slot '%s' " % connection["slot"] + \
                                       "in receiver %s" % _receiver)
                                else:
                                    getattr(sender, connection["signal"]).connect(slot)
                                    #sender.connect(sender,
                                    #    QtCore.SIGNAL(connection["signal"]),
                                    #    slot)
                    make_connections(item["children"])

            self.splash_screen.set_message("Connecting bricks...")
            make_connections(config.windows_list)

            # set run mode for every brick
            self.splash_screen.set_message("Setting run mode...")
            BlissWidget.setRunMode(True)

            if self.show_maximized:
                main_window.showMaximized()
            else:
                main_window.show()

            for window in self.windows:
                if window._show:
                    window.show()

        if BlissWidget._menuBar:
            BlissWidget._menuBar.set_exp_mode(False)

        return main_window

    def finalize(self):
        """Finalize gui load"""

        BlissWidget.setRunMode(False) # call .stop() for each brick

        self.hardware_repository.close()

        QApplication.sendPostedEvents()
        QApplication.processEvents()

        self.save_size()

    def save_size(self, configuration_suffix=''):
        """Saves window size and coordinates in the gui file"""

        if not self.launch_in_design_mode:
            # save windows positions
            for window in self.windows:
                window_cfg = self.configuration.windows[str(window.objectName())]

                window_cfg["properties"].getProperty(\
                    "x%s" % configuration_suffix).setValue(window.x())
                window_cfg["properties"].getProperty(\
                    "y%s" % configuration_suffix).setValue(window.y())
                window_cfg["properties"].getProperty(\
                    "w%s" % configuration_suffix).setValue(window.width())
                window_cfg["properties"].getProperty(\
                    "h%s" % configuration_suffix).setValue(window.height())

                splitters = self.configuration.find_all_children_by_type(\
                    "splitter", window_cfg)
                if len(splitters):
                    for widget in window.queryList("QSplitter"):
                        try:
                            splitter = splitters[widget.name()]
                            splitter["properties"].getProperty("sizes%s" % \
                               configuration_suffix).setValue(widget.sizes())
                        except KeyError:
                            continue

            # save GUI file only if it is not more recent
            # (to prevent overwritting file if it has been modified in the meantime)
            if self.gui_config_file and os.path.exists(self.gui_config_file):
                ts = os.stat(self.gui_config_file)[stat.ST_MTIME]
                if ts <= self.timestamp:
                    if configuration_suffix == '':
                        logging.getLogger().debug("Saving configuration " + \
                            "file to keep windows pos. and sizes")
                    self.configuration.save(self.gui_config_file)

    def finish_init(self, gui_config_file):
        """Finalize gui init"""

        while True:
            try:
                self.hardware_repository.connect()
            except:
                logging.getLogger().exception("Timeout while trying to " + \
                    "connect to Hardware Repository server.")
                message = \
                   "Timeout while connecting to Hardware " + \
                   "Repository server.\nMake sure the Hardware " + \
                   "Repository Server is running on host:\n%s." % \
                   str(self.hardware_repository.serverAddress).split(':')[0]
                if QMessageBox.warning(self,
                       "Cannot connect to Hardware Repository", message,
                       QMessageBox.Retry | QMessageBox.Cancel | \
                       QMessageBox.NoButton) == \
                   QMessageBox.Cancel:
                    logging.getLogger().warning("Gave up trying to " + \
                       "connect to Hardware Repository server.")
                    break
            else:
                logging.getLogger().info("Connected to Hardware " + \
                    "Repository server %s" % \
                    self.hardware_repository.serverAddress)
                break

        try:
            main_widget = None
            main_widget = self.load_gui(gui_config_file)
            if main_widget:
                set_splash_screen(None)
                self.splash_screen.finish(main_widget)
            del self.splash_screen
        except:
            logging.getLogger().exception("exception while loading GUI file")
            QApplication.exit()

    def customEvent(self, event):
        """Custom event"""

        self.finish_init(event.data)
