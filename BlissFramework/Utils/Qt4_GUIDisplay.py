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

"""GUIDisplay"""

import os
# LNLS
# python2.7
#import new
# python3.4
import sys
import time
import types
import logging
import weakref
import platform
import webbrowser
import collections

import BlissFramework

from QtImport import *
#if BlissFramework.get_gui_version() == "QT5":
#    from PyQt5 import QtCore
#    from PyQt5.QtGui import QColor, QPalette
#    from PyQt5.QtWidgets import *
#    StringList = list
#else:
#    from PyQt4 import QtCore
#    from PyQt4.QtGui import *
#
#    if sys.version_info > (3, 0):
#        StringList = list
#    else:
#        StringList = QStringList

from functools import partial

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Qt4_BaseLayoutItems import BrickCfg, SpacerCfg, WindowCfg, ContainerCfg, TabCfg

from HardwareRepository import HardwareRepository


__version__ = '2.2'


class CustomMenuBar(QMenuBar):
    """MenuBar"""

    viewToolBarSignal = pyqtSignal(bool)

    def __init__(self, parent):
        """Parent *must* be the window
           It contains a centralWidget in its viewport
        """

        QMenuBar.__init__(self)

        # Internal values -----------------------------------------------------
        self.parent = parent
        self.menu_data = None
        self.expert_pwd = None
        self.execution_mode = None
        self.menu_items = []
        self.original_style = None

        # Graphic elements ----------------------------------------------------
        #self.menubar = QtGui.QMenuBar(self)
        self.file_menu = self.addMenu("File")
        self.expert_mode_action = self.file_menu.addAction(\
             "Expert mode", self.expert_mode_clicked)
        self.expert_mode_action.setCheckable(True)
        self.reload_hwr_action = self.file_menu.addAction(\
             "Reload hardware objects", self.reload_hwr_clicked)
        #self.reload_hwr_action.setEnabled(False)
        self.file_menu.addAction("Quit", self.quit_clicked)

        self.view_menu = self.addMenu("View")
        self.view_toolbar_action = self.view_menu.addAction(\
             "Graphics toolbar", self.view_toolbar_clicked)
        self.view_toolbar_action.setCheckable(True)
        self.view_menu.addSeparator()
        
        self.view_windows_menu = self.view_menu.addMenu("Windows")
        self.view_windows_menu.setEnabled(False)

        self.view_maximize_action = self.view_menu.addAction(\
             "Show maximized window", self.view_max_clicked)
        self.view_normal_action = self.view_menu.addAction(\
             "Show normal window", self.view_normal_clicked)
        self.view_minimize_action = self.view_menu.addAction(\
             "Minimize window", self.view_min_clicked)

        self.expert_mode_action.setCheckable(True)
        self.help_menu = self.addMenu("Help")
        self.info_for_developers_action = self.help_menu.addAction(\
             "Information for developers", self.info_for_developers_clicked)
        self.info_for_developers_action.setEnabled(False)
        self.help_menu.addAction("User manual", self.user_manual_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("Whats this", self.whats_this_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("About", self.about_clicked)

        # Layout --------------------------------------------------------------
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.expert_mode_checkboxStdColor = None
        self.menu_items = [self.file_menu,
                           self.view_menu,
                           self.help_menu]
        #self.setwindowIcon(Qt4_Icons.load_icon("desktop_icon"))

    def insert_menu(self, new_menu_item, position):
        """Inserts item in menu"""

        self.clear()
        self.menu_items.insert(position, new_menu_item)
        for menu_item in self.menu_items:
            self.addMenu(menu_item)

    def get_menu_bar(self):
        """Returns current menu bar. Method used by other widgets that
           inserts action in menu bar
        """

        return self.menubar

    def configure(self, menu_data, expert_pwd, execution_mode):
        """Configure"""

        self.menu_data = menu_data
        self.expert_pwd = expert_pwd
        self.execution_mode = execution_mode

    def expert_mode_clicked(self):
        """Ask for expert mode password"""

        if not self.original_style:
            #This should be based on instance connection
            # restore colour if master/client/etc
            self.original_style = self.styleSheet()
        if self.expert_mode_action.isChecked():
            res = QInputDialog.getText(self,
                "Switch to expert mode", "Please enter the password:",
                QLineEdit.Password)
            if res[1]:
                if str(res[0]) == self.expert_pwd:
                    self.set_exp_mode(True)
                    self.expert_mode_action.setChecked(True)
                else:
                    self.expert_mode_action.setChecked(False)
                    QMessageBox.critical(self,
                         "Switch to expert mode", "Wrong password!",
                         QMessageBox.Ok)
            else:
                self.expert_mode_action.setChecked(False)
        else:
            self.set_exp_mode(False)

    def set_exp_mode(self, state):
        """Set widgets in expert mode"""

        if not self.execution_mode:
            return

        self.info_for_developers_action.setEnabled(state)

        if state:
            # switch to expert mode
            #QObject.emit(self.parent,
            #                    SIGNAL("enableExpertMode"),
            #                    True)
            self.parent.enableExpertModeSignal.emit(True)
            # go through all bricks and execute the method
            for widget in QApplication.allWidgets():
                if isinstance(widget, BlissWidget):
                    try:
                        widget.set_expert_mode(True)
                    except:
                        logging.getLogger().exception(\
                           "Could not set %s to expert mode" % \
                           widget.objectName())
            self.set_color("orange")
        else:
            # switch to user mode
            self.parent.enableExpertModeSignal.emit(False)
            # go through all bricks and execute the method
            for widget in QApplication.allWidgets():
                if isinstance(widget, BlissWidget):
                    widget.setWhatsThis("")
                    try:
                        widget.set_expert_mode(False)
                    except:
                        logging.getLogger().exception(\
                            "Could not set %s to user mode" % \
                            widget.objectName())
            if self.original_style:
                self.setStyleSheet(self.original_style)

    def reload_hwr_clicked(self):
        """Reloads hardware objects"""

        #TODO: in development
        hwr = HardwareRepository.HardwareRepository()
        import reimport
        for hwr_obj in hwr.hardwareObjects:

            connections = hwr.hardwareObjects[hwr_obj].connect_dict
            for sender in connections:
                hwr.hardwareObjects[hwr_obj].disconnect(\
                    sender, connections[sender]["signal"], connections[sender]["slot"])

            #reload(hwr.hardwareObjects[hwr_obj].__class__)

        from HardwareRepository import BaseHardwareObjects
        import Qt4_VideoMockup
        reimport.reimport(BaseHardwareObjects)
        reimport.reimport(Qt4_VideoMockup)

        for hwr_obj in hwr.hardwareObjects:
            for sender in connections:
                hwr.hardwareObjects[hwr_obj].connect(\
                    sender, connections[sender]["signal"], connections[sender]["slot"])

    def whats_this_clicked(self):
        """Whats this"""

        if self.execution_mode:
            BlissWidget.updateWhatsThis()

    def about_clicked(self):
        """Display dialog with info about mxcube"""

        about_msg_box = QMessageBox.about(self,
             "About MXCuBE",
             """<b>MXCuBE v %s </b>
                <p>Macromolecular Xtallography Customized Beamline Environment<p>
                Python %s - Qt %s - PyQt %s on %s"""%(__version__,
              platform.python_version(), QT_VERSION_STR,
              PYQT_VERSION_STR, platform.system()))

    def quit_clicked(self):
        """Exit mxcube"""

        if self.execution_mode:
            QApplication.quit()

    def info_for_developers_clicked(self):
        """Opens webpage with documentation"""

        path_list = os.path.dirname(__file__)
        filename = os.path.join(*path_list[:-2])
        filename = os.path.join(os.sep, filename, "docs/build/index.html")
        if os.path.exists(filename):
            webbrowser.open(filename)
        else:
            logging.getLogger().error("Could not find html file %s. " + \
               "Use sphinx to build documentation (in doc dir execute " + \
               "'sphinx-build source build')" % filename)

    def user_manual_clicked(self):
        """Opens user manual"""

        path_list = os.path.dirname(__file__).split(os.sep)
        filename = os.path.join(*path_list[:-2])
        filename = os.path.join(os.sep, filename,
                                "docs/build/user_manual.html")
        if os.path.exists(filename):
            webbrowser.open(filename)
        else:
            logging.getLogger().error(\
                "Could not find html file %s" % filename)

    def set_color(self, color):
        """Sets menubar color"""

        if color:
            style_string = """QMenuBar {background-color: %s;}""" % color
            style_string += """QMenuBar::item {background: %s;}""" % color
            style_string += """QMenuBar {color: black;}"""
            self.setStyleSheet(style_string)

    def view_toolbar_clicked(self):
        """View toolbar"""

        self.viewToolBarSignal.emit(self.view_toolbar_action.isChecked())

    def view_max_clicked(self):
        """Show maximized"""

        QApplication.activeWindow().showMaximized()

    def view_normal_clicked(self):
        """Show normal window"""

        QApplication.activeWindow().showNormal()

    def view_min_clicked(self):
        """Show minimized window"""

        QApplication.activeWindow().showMinimized()

    def append_windows_links(self, windows_list):
        """If there are more than one window then appends names
           of available windows to the menu Windows
        """
        if len(windows_list) > 1:
            self.view_windows_menu.setEnabled(True)
            self.preview_windows = {}
            for window in windows_list:
                self.preview_windows[window.base_caption] = window
                temp_menu = self.view_windows_menu.addAction(window.base_caption, 
                           partial(self.view_window, window.base_caption))
            
    def view_window(self, window_caption):
        """Displays selected window"""
        self.preview_windows[window_caption].show()
        self.preview_windows[window_caption].activateWindow()


class CustomToolBar(QToolBar):
    """Custom toolbar"""

    def __init__(self, parent):
        """Parent *must* be the window
           It contains a centralWidget in its viewport
        """

        QToolBar.__init__(self)

        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.Fixed)

class WindowDisplayWidget(QScrollArea):
    """Main widget"""

    brickChangedSignal = pyqtSignal(str, str, str, tuple, bool)
    tabChangedSignal = pyqtSignal(str, int)
    enableExpertModeSignal = pyqtSignal(bool)

    class Spacer(QFrame):
        """Spacer widget"""

        def __init__(self, *args, **kwargs):
            """init"""

            QFrame.__init__(self, args[0])
            self.setObjectName(args[1])

            self.orientation = kwargs.get("orientation", "horizontal")
            self.execution_mode = kwargs.get("execution_mode", False)

            self.setFixedSize(-1)

            if self.orientation == "horizontal":
                self.main_layout = QHBoxLayout()
            else:
                self.main_layout = QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.main_layout)

        def setFixedSize(self, fixed_size):
            """Sets fixed size"""

            if fixed_size >= 0:
                hor_size_policy = self.orientation == "horizontal" and \
                    QSizePolicy.Fixed or \
                    QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == \
                    QSizePolicy.Fixed and \
                    QSizePolicy.MinimumExpanding or \
                    QSizePolicy.Fixed

                if self.orientation == "horizontal":
                    self.setFixedWidth(fixed_size)
                else:
                    self.setFixedHeight(fixed_size)
            else:
                hor_size_policy = self.orientation == "horizontal" and \
                    QSizePolicy.Expanding or \
                    QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == \
                    QSizePolicy.Expanding and \
                    QSizePolicy.MinimumExpanding or \
                    QSizePolicy.Expanding
            self.setSizePolicy(hor_size_policy, ver_size_policy)

        def paintEvent(self, event):
            """Paints the widgets"""

            QFrame.paintEvent(self, event)

            if self.execution_mode:
                return
            painter = QPainter(self)
            painter.setPen(QPen(Qt.black, 3))

            if self.orientation == 'horizontal':
                height = self.height() / 2
                painter.drawLine(0, height, self.width(), height)
                painter.drawLine(0, height, 5, height - 5)
                painter.drawLine(0, height, 5, height + 5)
                painter.drawLine(self.width(), height,
                                 self.width() - 5, height - 5)
                painter.drawLine(self.width(), height,
                                 self.width() - 5, height + 5)
            else:
                width = self.width() / 2
                painter.drawLine(self.width() / 2, 0,
                                 self.width() / 2, self.height())
                painter.drawLine(width, 0, width - 5, 5)
                painter.drawLine(width, 0, width + 5, 5)
                painter.drawLine(width, self.height(),
                                 width - 5, self.height() - 5)
                painter.drawLine(width, self.height(),
                                 width + 5, self.height() - 5)

    def verticalSpacer(*args, **kwargs):
        """Vertical spacer"""

        kwargs["orientation"] = "vertical"
        return WindowDisplayWidget.Spacer(*args, **kwargs)

    def horizontalSpacer(*args, **kwargs):
        """Horizontal spacer"""

        kwargs["orientation"] = "horizontal"
        return WindowDisplayWidget.Spacer(*args, **kwargs)

    def horizontalSplitter(*args, **kwargs):
        """Horizontal splitter"""

        return QSplitter(Qt.Horizontal, *args)

    def verticalSplitter(*args, **kwargs):
        """Vertical splitter"""

        return QSplitter(Qt.Vertical, *args)

    def verticalBox(*args, **kwargs):
        """Vertical box"""

        execution_mode = kwargs.get('execution_mode', False)

        frame = QFrame(args[0])
        frame.setObjectName(args[1])
        if not execution_mode:
            frame.setFrameStyle(QFrame.Box | QFrame.Plain)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        return frame

    def horizontalBox(*args, **kwargs):
        """Horizontal box"""

        execution_mode = kwargs.get('execution_mode', False)

        frame = QFrame(args[0])
        frame.setObjectName(args[1])

        if not execution_mode:
            frame.setFrameStyle(QFrame.Box | QFrame.Plain)

        frame_layout = QHBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        return frame

    def horizontalGroupBox(*args, **kwargs):
        """Horizontal group box"""

        groupbox = QGroupBox(args[0])
        groupbox.setObjectName(args[1])
        groupbox.setSizePolicy(QSizePolicy.Expanding,
                               QSizePolicy.Expanding)

        group_box_layout = QHBoxLayout(groupbox)
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0, 0, 0, 0)

        return groupbox

    def verticalGroupBox(*args, **kwargs):
        """Vertical group box"""

        groupbox = QGroupBox(args[0])
        groupbox.setObjectName(args[1])
        groupbox.setSizePolicy(QSizePolicy.Expanding,
                               QSizePolicy.Expanding)

        group_box_layout = QVBoxLayout(groupbox)
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0, 0, 0, 0)

        return groupbox

    class CustomTabWidget(QTabWidget):
        """Tab widget"""

        notebookPageChangedSignal = pyqtSignal(str)
        tabChangedSignal = pyqtSignal(int, 'PyQt_PyObject')
        

        def __init__(self, *args, **kwargs):
            """init"""

            QTabWidget.__init__(self, args[0])
            self.setObjectName(args[1])
            self.close_tab_button = None

            #self.tab_widgets = []
            self.countChanged = {}
            self.setSizePolicy(QSizePolicy.Expanding,
                               QSizePolicy.Expanding)
            self.currentChanged.connect(self._page_changed)

        def _page_changed(self, index):
            """Page changed event"""

            page = self.widget(index)
            self.countChanged[index] = False

            tab_label = str(self.tabText(index))
            label_list = tab_label.split()
            found = False
            try:
                count = label_list[-1]
                try:
                    found = count[0] == "("
                except:
                    pass
                else:
                    try:
                        found = count[-1] == ")"
                    except:
                        pass
            except:
                pass
            if found:
                orig_label = " ".join(label_list[0:-1])
            else:
                orig_label = " ".join(label_list)
            self.notebookPageChangedSignal.emit(orig_label)
            self.tabChangedSignal.emit(index, page)

            tab_name = self.objectName()
            BlissWidget.update_tab_widget(tab_name, index)

        def add_tab(self, page_widget, label, icon=""):
            """Add tab"""

            scroll_area = page_widget
            self.addTab(scroll_area, label)

            slot_name = "showPage_%s" % label

            def tab_slot(self, page_index=self.indexOf(scroll_area)):
                self.setCurrentIndex(page_index)

            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                     types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                     "Could not add slot %s " % slot_name + \
                     "in %s" % self.objectName())
            slot_name = "hidePage_%s" % label

            def tab_slot(self, hide=True, page={"widget" : scroll_area, \
                         "label": self.tabText(self.indexOf(scroll_area)),
                         "index": self.indexOf(scroll_area),
                         "icon": icon, "hidden": False}):
                if hide:
                    if not page["hidden"]:
                        self.removeTab(self.indexOf(page["widget"]))
                        self.repaint()
                        page["hidden"] = True
                else:
                    if page["hidden"]:
                        if icon:
                            self.insertTab(page["widget"],
                                           Qt4_Icons.load_icon(icon),
                                           label,
                                           page["index"])
                        else:
                            self.insertTab(page["index"],
                                           page["widget"],
                                           page["label"])
                        slot_name = "showPage_%s" % page["label"].replace(' ', '_')
                        getattr(self, slot_name)()
                        page["hidden"] = False
                        self.setCurrentWidget(page["widget"])
                    else:
                        slot_name = "showPage_%s" % page["label"].replace(' ', '_')
                        getattr(self, slot_name)()
                        self.setCurrentWidget(page["widget"])
            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                     types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                     "Could not add slot %s " % slot_name + \
                     "in %s" % str(self.objectName()))

            # add 'enable page' slot
            slot_name = "enablePage_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.page(page_index).setEnabled(enable)

            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                     types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                     "Could not add slot %s " % slot_name + \
                     "in %s" % str(self.objectName()))

            # add 'enable tab' slot
            slot_name = "enableTab_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.setTabEnabled(page_index, enable)
            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                     types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                     "Could not add slot %s " % slot_name + \
                     "in %s" % str(self.objectName()))

            # add 'tab reset count' slot
            slot_name = "resetTabCount_%s" % label
            def tab_slot(self, erase_count, page_index=self.indexOf(scroll_area)):
                tab_label = str(self.tabLabel(self.page(page_index)))
                label_list = tab_label.split()
                found = False
                try:
                    count = label_list[-1]
                    try:
                        found = count[0] == "("
                    except:
                        pass
                    else:
                        try:
                            found = count[-1] == ")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num = int(count[1: -1])
                    except:
                        pass
                    else:
                        new_label = " ".join(label_list[0: -1])
                        if not erase_count:
                            new_label += " (0)"
                        self.countChanged[page_index] = False
                        self.setTabLabel(self.page(page_index), new_label)
                else:
                    if not erase_count:
                        new_label = " ".join(label_list)
                        new_label += " (0)"
                        self.countChanged[page_index] = False
                        self.setTabLabel(self.page(page_index), new_label)
            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                    types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                    "Could not add slot %s " % slot_name + \
                    "in %s" % str(self.name()))

            # add 'tab increase count' slot
            slot_name = "incTabCount_%s" % label
            def tab_slot(self, delta, only_if_hidden, page_index=self.indexOf(scroll_area)):
                if only_if_hidden and page_index == self.currentPageIndex():
                    return
                tab_label = str(self.tabLabel(self.page(page_index)))
                label_list = tab_label.split()
                found = False
                try:
                    count = label_list[-1]
                    try:
                        found = count[0] == "("
                    except:
                        pass
                    else:
                        try:
                            found = count[-1] == ")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num = int(count[1: -1])
                    except:
                        pass
                    else:
                        new_label = " ".join(label_list[0: -1])
                        new_label += " (%d)" % (num+delta)
                        self.countChanged[page_index] = True
                        self.setTabLabel(self.page(page_index), new_label)
                else:
                    new_label = " ".join(label_list)
                    new_label += " (%d)" % delta
                    self.countChanged[page_index] = True
                    self.setTabLabel(self.page(page_index), new_label)
            try:
                # LNLS
                # python2.7
                #self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
                # python3.4
                self.__dict__[slot_name.replace(" ", "_")] = \
                    types.MethodType(tab_slot, self)
            except:
                logging.getLogger().exception(\
                    "Could not add slot %s " % slot_name + \
                    "in %s" % str(self.objectName()))

            # that's the real page
            return scroll_area


    class label(QLabel):
        """Label"""

        def __init__(self, *args, **kwargs):
            """init"""

            QLabel.__init__(self, args[0])
            self.setSizePolicy(QSizePolicy.Fixed,
                               QSizePolicy.Fixed)

    items = {"vbox": verticalBox,
             "hbox": horizontalBox,
             "vgroupbox": verticalGroupBox,
             "hgroupbox": horizontalGroupBox,
             "vspacer": verticalSpacer,
             "hspacer": horizontalSpacer,
             "icon": label,
             "label": label,
             "tab": CustomTabWidget,
             "hsplitter": horizontalSplitter,
             "vsplitter": verticalSplitter}

    isShownSignal = pyqtSignal()
    isHiddenSignal = pyqtSignal()
    itemClickedSignal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """__init__ of WindowDisplayWidget"""

        QScrollArea.__init__(self, args[0])

        self.additional_windows = {}
        self.__put_back_colors = None
        self.execution_mode = kwargs.get('execution_mode', False)
        self.preview_items = []
        self.current_window = None
        self.base_caption = ""
        self.setWindowTitle("GUI preview")

        self.central_widget = QWidget(self.widget())
        #self.central_widget.setObjectName("deee")
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.show()

        self._toolbar = CustomToolBar(self)
        self._toolbar.hide()
        self._menubar = CustomMenuBar(self)
        self._menubar.hide()
        self._statusbar = QStatusBar(self)
        self._statusbar.hide()

        #_statusbar_hlayout = QtGui.QHBoxLayout(self.statusbar)
        #_statusbar_hlayout.setSpacing(2)
        #_statusbar_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self._menubar)
        _main_vlayout.addWidget(self._toolbar)
        _main_vlayout.addWidget(self.central_widget)
        _main_vlayout.addWidget(self._statusbar)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self._menubar.viewToolBarSignal.connect(self.view_toolbar_toggled)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(Qt4_Icons.load_icon("desktop_icon"))

    def view_toolbar_toggled(self, state):
        """Toggle toolbar visibility"""

        if state:
            self._toolbar.show()
        else:
            self._toolbar.hide()

    def set_menu_bar(self, menu_data, exp_pwd, execution_mode):
        """Sets menu bar"""

        self._menubar.configure(menu_data, exp_pwd, execution_mode)
        self._menubar.show()
        BlissWidget._menuBar = self._menubar
        BlissWidget._toolBar = self._toolbar

    def set_status_bar(self):
        """Sets statusbar"""
 
        self._statusbar_user_label = QLabel("-")
        self._statusbar_state_label = QLabel(" <b>State: </b>")
        self._statusbar_diffractometer_label = QLabel(" <b>Diffractometer: </b>")
        self._statusbar_sc_label = QLabel(" <b>Sample changer: </b>")
        self._statusbar_action_label = QLabel(" <b>Last collect: </b>")
        
        self._statusbar.addWidget(self._statusbar_user_label)
        self._statusbar.addWidget(self._statusbar_state_label)
        self._statusbar.addWidget(self._statusbar_diffractometer_label)
        self._statusbar.addWidget(self._statusbar_sc_label)
        self._statusbar.addWidget(self._statusbar_action_label)
         
        self._statusbar.show()
        BlissWidget._statusBar = self._statusbar

    def update_status_info(self, info_type, info_message):
        """Updates status info"""

        if info_message == "":
            info_message = "Ready"

        if info_type == "user":
            self._statusbar_user_label.setText(info_message)
        elif info_type == "status":
            self._statusbar_state_label.setText(\
                " <b>State: </b> %s" % info_message)
        elif info_type == "diffractometer":
            self._statusbar_diffractometer_label.setText(\
                " <b>Diffractometer: </b>%s" % info_message)
        elif info_type == "sc":
            self._statusbar_sc_label.setText(\
                " <b>Sample changer: </b> %s" % info_message)
        elif info_type == "action":
            self._statusbar_action_label.setText(\
                " <b>Last collect: </b> %s (%s)" % \
                (info_message, time.strftime("%Y-%m-%d %H:%M:%S")))

    def show(self, *args):
        """Show"""

        ret = QWidget.show(self)
        self.isShownSignal.emit()
        #self.emit(SIGNAL("isShown"), ())
        return ret

    def hide(self, *args):
        """Hide"""

        ret = QWidget.hide(self)
        self.isHiddenSignal.emit()
        #self.emit(SIGNAL("isHidden"), ())
        return ret

    def set_caption(self, caption):
        """Set caption"""
        ret = QWidget.setWindowTitle(self, caption)
        self.base_caption = caption
        return ret

    def update_instance_caption(self, instance_caption):
        """Update caption if instance mode (master,slave) changed"""

        QWidget.setWindowTitle(self, self.base_caption + \
                                     instance_caption)

    def exitExpertMode(self, *args):
        """Exit expert mode"""

        if len(args) > 0:
            if args[0]:
                return
        self._menubar.set_exp_mode(False)

    def add_item(self, item_cfg, parent):
        """Adds item to the gui"""

        item_type = item_cfg["type"]
        item_name = item_cfg["name"]
        new_item = None

        try:
            klass = WindowDisplayWidget.items[item_type]
        except KeyError:
            new_item = item_cfg["brick"]
        else:
            new_item = klass(parent, item_cfg["name"], execution_mode=self.execution_mode)
            if item_type in ("vbox", "hbox", "vgroupbox", "hgroupbox"):
                if item_cfg["properties"]["color"] is not None:
                    qtcolor = QColor(item_cfg["properties"]["color"])
                    Qt4_widget_colors.set_widget_color(new_item,
                                                        qtcolor)

                if item_type.endswith("groupbox"):
                    new_item.setTitle(item_cfg["properties"]["label"])

                new_item.layout().setSpacing(item_cfg["properties"]["spacing"])
                if hasattr(new_item.layout(), "setContentsMargins"):
                    new_item.layout().setContentsMargins(item_cfg["properties"]["margin"],
                                                         item_cfg["properties"]["margin"],
                                                         item_cfg["properties"]["margin"],
                                                         item_cfg["properties"]["margin"])
                elif hasattr(new_item.layout(), "setMargins"):
                    new_item.layout().setMargin(item_cfg["properties"]["margin"])
                frame_style = QFrame.NoFrame
                if item_cfg["properties"]["frameshape"] != "default":
                    frame_style = getattr(QFrame,
                        item_cfg["properties"]["frameshape"])
                if item_cfg["properties"]["shadowstyle"] != "default":
                    frame_style = frame_style | getattr(QFrame,
                        item_cfg["properties"]["shadowstyle"].capitalize())
                if frame_style != QFrame.NoFrame:
                    try:
                        new_item.setFrameStyle(frame_style)
                    except:
                        logging.getLogger().exception(\
                             "Could not set frame style on " + \
                             "item %s", item_cfg["name"])
                if item_cfg["properties"]["fixedwidth"] > -1:
                    new_item.setFixedWidth(\
                        item_cfg["properties"]["fixedwidth"])
                if item_cfg["properties"]["fixedheight"] > -1:
                    new_item.setFixedHeight(\
                        item_cfg["properties"]["fixedheight"])
            elif item_type == "icon":
                img = QPixmap()
                if img.load(item_cfg["properties"]["filename"]):
                    new_item.setPixmap(img)
            elif item_type == "label":
                new_item.setText(item_cfg["properties"]["text"])
            elif item_type == "tab":
                item_cfg.widget = new_item
                new_item.close_tab_button = QToolButton(new_item)
                new_item.close_tab_button.setIcon(\
                     Qt4_Icons.load_icon('delete_small'))
                new_item.setCornerWidget(new_item.close_tab_button)
                new_item.close_tab_button.hide()
                def close_current_page():
                    tab = new_item
                    slot_name = "hidePage_%s" % str(tab.tabText(tab.currentIndex()))
                    slot_name = slot_name.replace(" ", "_")
                    getattr(tab, slot_name)()

                def current_page_changed(index):
                    item_cfg.notebookPageChanged(new_item.tabText(index))

                new_item._close_current_page_cb = close_current_page
                new_item.currentChanged.connect(current_page_changed)
                new_item.close_tab_button.clicked.connect(close_current_page)
            elif item_type == "vsplitter" or type == "hsplitter":
                pass

            new_item.show()

        return new_item

    def make_item(self, item_cfg, parent):
        """Make item"""

        if isinstance(item_cfg, ContainerCfg):
            self.container_num += 1
        for child in item_cfg["children"]:
            try:
                new_item = self.add_item(child, parent)
            except:
                logging.getLogger().exception("Cannot add item %s" % \
                                              child["name"])
            else:
                if not self.execution_mode:
                    new_item.installEventFilter(self)
            if parent.__class__ == WindowDisplayWidget.items["tab"]:
                new_tab = parent.add_tab(new_item, child["properties"]["label"],
                     child["properties"]["icon"])
                new_tab.item_cfg = child
                self.preview_items.append(new_item)
            else:
                if isinstance(child, ContainerCfg):
                    new_item.setSizePolicy(self.getSizePolicy(\
                        child["properties"]["hsizepolicy"],
                        child["properties"]["vsizepolicy"]))
                if not isinstance(child, BrickCfg):
                    if child["properties"].hasProperty("fontSize"):
                        font = new_item.font()
                        if int(child["properties"]["fontSize"]) <= 0:
                            child["properties"].getProperty("fontSize").\
                               setValue(font.pointSize())
                        else:
                            font.setPointSize(int(child["properties"]["fontSize"]))
                            new_item.setFont(font)

                if hasattr(parent, "_preferred_layout"):
                    layout = parent._preferred_layout
                else:
                    layout = parent.layout()

                if layout is not None:
                    # layout can be none if parent is a Splitter for example
                    if not isinstance(child, BrickCfg):
                        alignment_flags = self.getAlignmentFlags(\
                           child["properties"]["alignment"])
                    else:
                        alignment_flags = 0
                    if isinstance(child, SpacerCfg):
                        stretch = 1

                        if child["properties"]["fixed_size"]:
                            new_item.setFixedSize(child["properties"]["size"])
                    else:
                        stretch = 0
                    self.preview_items.append(new_item)
                    if alignment_flags is not None:
                        layout.addWidget(new_item, stretch,
                             Qt.Alignment(alignment_flags))
                    else:
                        layout.addWidget(new_item, stretch)
            self.make_item(child, new_item)

    def draw_preview(self, container_cfg, window_id,
                     container_ids=[], selected_item=""):
        """Draw preview"""

        for (window, m) in self.additional_windows.values():
            window.close()

        # reset colors
        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
            self.__put_back_colors = None

        if self.current_window is not None and \
           self.current_window != window_id:
            # remove all bricks and destroy all other items
            self.central_widget.close()
            self.central_widget = QWidget(self.viewport())
            self.central_widget_layout = QVBoxLayout(self.central_widget)
            self.central_widget.show()

        self.current_window = window_id
        self.container_num = -1

        parent = self.central_widget

        self.setObjectName(container_cfg["name"])
        self.preview_items.append(self)

        if isinstance(container_cfg, WindowCfg):
            self.setObjectName(container_cfg["name"])
            if container_cfg.properties["menubar"]:
                self.set_menu_bar(container_cfg.properties["menudata"],
                                  container_cfg.properties["expertPwd"],
                                  self.execution_mode)
            else:
                try:
                    self.additional_windows[window_id][1].hide()
                except:
                    pass

        self.make_item(container_cfg, parent)

        if isinstance(container_cfg, WindowCfg):
            if container_cfg.properties["statusbar"]:
                self.set_status_bar()

    def remove_widget(self, item_name, child_name_list):
        """Remove widget"""

        remove_item_list = child_name_list
        remove_item_list.append(item_name)
        for name in remove_item_list:
            for item_widget in self.preview_items:
                if item_widget.objectName() == name:
                    self.preview_items.remove(item_widget)
                    item_widget.hide()
                    # To avoid some problems with accessing not existing
                    # widget we do not delet it. Hidding is enough
                    # Anyway the widget config is deleted before and
                    # deleted widget is not created at the load
                    #item_widget.deleteLater()

    def add_widget(self, child, parent):
        """Add widget"""

        if parent is None:
            self.draw_preview(child, 0, [])
        else:
            for item in self.preview_items:
                if item.objectName() == parent.name:
                    parent_item = item
            new_item = self.add_item(child, parent_item)
            if isinstance(parent, TabCfg):
                new_tab = parent_item.add_tab(new_item,
                                              child["properties"]["label"],
                                              child["properties"]["icon"])
                new_tab.item_cfg = child
            else:
                parent_item.layout().addWidget(new_item)
            self.preview_items.append(new_item)

    def move_widget(self, item_name, direction):
        """Moves widget in the parent layout up or down"""

        for preview_item in self.preview_items:
            if preview_item.objectName() == item_name:
                item = preview_item
        if item:
            parent_layout = item.parent().layout()
            current_index = parent_layout.indexOf(item)

            if direction == "up":
                new_index = current_index - 1
            else:
                new_index = current_index + 1

            if (new_index != current_index and \
               new_index > -1 and \
               new_index < parent_layout.count()):
                parent_layout.removeWidget(item)
                parent_layout.insertWidget(new_index, item)

    def update_preview(self, container_cfg, window_id,
                       container_ids=[], selected_item=""):
        """Method selects a widget in the gui"""

        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
            self.__put_back_colors = None
        if (len(selected_item) and \
            len(self.preview_items) > 0):
            for item in self.preview_items:
                if item.objectName() == selected_item:
                    self.select_widget(item)
                    return

    def select_widget(self, widget):
        """Colors selected widget"""

        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
        original_color = widget.palette().color(QPalette.Window)
        selected_color = QColor(150, 150, 200)
        Qt4_widget_colors.set_widget_color(widget,
                                           selected_color,
                                           QPalette.Background)

        def put_back_colors(wref=weakref.ref(widget),
                            bkgd_color=original_color):
            widget = wref()
            if widget is not None:
                Qt4_widget_colors.set_widget_color(widget,
                                                   bkgd_color,
                                                   QPalette.Background)
        self.__put_back_colors = put_back_colors

    def eventFilter(self, widget, event):
        """Even filter"""

        if widget is not None and event is not None:
            if event.type() == QEvent.MouseButtonRelease and \
               event.button() == Qt.LeftButton:
                self.itemClickedSignal.emit(widget.objectName())
                return True

        return QScrollArea.eventFilter(self, widget, event)

    def getAlignmentFlags(self, alignment_directives_string):
        """Returns alignment flags"""

        if alignment_directives_string is None:
            alignment_directives = ['none']
        else:
            alignment_directives = alignment_directives_string.split()
        alignment_flags = 0

        if "none" in alignment_directives:
            return alignment_flags
        if "hcenter" in alignment_directives:
            return Qt.AlignHCenter
        if "vcenter" in alignment_directives:
            return Qt.AlignVCenter
        if "top" in alignment_directives:
            alignment_flags = Qt.AlignTop
        if "bottom" in alignment_directives:
            alignment_flags = Qt.AlignBottom
        if "center" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = Qt.AlignCenter
            else:
                alignment_flags = alignment_flags | Qt.AlignHCenter
        if "left" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = Qt.AlignLeft | Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | Qt.AlignLeft
        if "right" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = Qt.AlignRight | Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | Qt.AlignRight
        return alignment_flags

    def getSizePolicy(self, hsizepolicy, vsizepolicy):
        """Returns size policy"""

        def _get_size_policy_flag(policy_flag):
            if policy_flag == "expanding":
                return QSizePolicy.Expanding
            elif policy_flag == "fixed":
                return QSizePolicy.Fixed
            else:
                return QSizePolicy.Preferred

        return QSizePolicy(_get_size_policy_flag(hsizepolicy),
                           _get_size_policy_flag(vsizepolicy))

    def append_windows_links(self, window_list):
        self._menubar.append_windows_links(window_list)

def display(configuration, no_border=False):
    """Display window"""

    windows = []
    for window in configuration.windows_list:
        BlissWidget.set_status_info("status", window["name"])
        display = WindowDisplayWidget(None, window["name"],
            execution_mode=True, no_border=no_border)
        windows.append(display)
        display.set_caption(window["properties"]["caption"])
        display.draw_preview(window, id(display))
        if window["properties"]["show"]:
            display._show = True
        else:
            display._show = False
        display.hide()
        restoreSizes(configuration, window, display)

    for window in windows:
        window.append_windows_links(windows)

    return windows

def restoreSizes(configuration, window, display, configuration_suffix="", move_window_flag=True):
    """
    Descript. :
    """
    splitters = configuration.find_all_children_by_type("splitter", window)

    if len(splitters):
        for sw in display.queryList("QSplitter"):
            try:
                splitter = splitters[sw.name()]
                sw.setSizes(eval(splitter["properties"]["sizes%s" % configuration_suffix]))
            except KeyError:
                continue

    if (window["properties"]["x%s" % configuration_suffix] +
        window["properties"]["y%s" % configuration_suffix] +
        window["properties"]["w%s" % configuration_suffix] +
        window["properties"]["h%s" % configuration_suffix] > 0):
        if move_window_flag:
            display.move(window["properties"]["x%s" % configuration_suffix],
                         window["properties"]["y%s" % configuration_suffix])
        display.resize(QSize(\
             window["properties"]["w%s" % configuration_suffix],
             window["properties"]["h%s" % configuration_suffix]))
