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
import time
import types
import logging
import weakref
import platform
import webbrowser
import collections
from functools import partial

from gui.utils import Icons, Colors, PropertyEditor, QtImport
from gui.BaseComponents import BaseWidget
from gui.BaseLayoutItems import BrickCfg, SpacerCfg, WindowCfg, ContainerCfg, TabCfg

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__status__ = "Production"

class CustomLabel(QtImport.QLabel):
    """Label"""

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QLabel.__init__(self, args[0])
        self.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)


class CustomMenuBar(QtImport.QMenuBar):
    """MenuBar displayed on the top of the window"""

    viewToolBarSignal = QtImport.pyqtSignal(bool)
    saveConfigSignal = QtImport.pyqtSignal()

    def __init__(self, parent):
        """Parent *must* be the window
           It contains a centralWidget in its viewport
        """

        QtImport.QMenuBar.__init__(self)

        # Internal values -----------------------------------------------------
        self.parent = parent
        self.menu_data = None
        self.expert_pwd = None
        self.execution_mode = None
        self.menu_items = []
        self.original_style = None
        self.preview_windows = {}

        # Graphic elements ----------------------------------------------------
        # self.menubar = QtGui.QMenuBar(self)
        self.file_menu = self.addMenu("File")
        self.expert_mode_action = self.file_menu.addAction(
            "Expert mode", self.expert_mode_clicked
        )
        self.expert_mode_action.setCheckable(True)
        self.reload_hwr_action = self.file_menu.addAction(
            "Reload hardware objects", self.reload_hwr_clicked
        )
        self.reload_hwr_action.setEnabled(False)
        self.brick_properties_action = self.file_menu.addAction(
            "Edit brick properties", self.edit_brick_properties
        )
        self.file_menu.addAction("Quit", self.quit_clicked)

        self.view_menu = self.addMenu("View")
        self.view_toolbar_action = self.view_menu.addAction(
            "Graphics toolbar", self.view_toolbar_clicked
        )
        self.view_toolbar_action.setCheckable(True)
        self.view_menu.addSeparator()

        self.view_windows_menu = self.view_menu.addMenu("Windows")
        self.view_windows_menu.setEnabled(False)

        self.view_maximize_action = self.view_menu.addAction(
            "Show maximized window", self.view_max_clicked
        )
        self.view_normal_action = self.view_menu.addAction(
            "Show normal window", self.view_normal_clicked
        )
        self.view_minimize_action = self.view_menu.addAction(
            "Minimize window", self.view_min_clicked
        )

        self.expert_mode_action.setCheckable(True)
        self.help_menu = self.addMenu("Help")
        self.info_for_developers_action = self.help_menu.addAction(
            "Information for developers", self.info_for_developers_clicked
        )
        self.info_for_developers_action.setEnabled(False)
        self.help_menu.addAction("User manual", self.user_manual_clicked)
        self.help_menu.addAction("Shortcuts", self.shortcuts_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("Whats this", self.whats_this_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("About", self.about_clicked)

        self.bricks_properties_editor = BricksPropertiesEditor()
        self.bricks_properties_editor.close()

        # Layout --------------------------------------------------------------
        self.setSizePolicy(
            QtImport.QSizePolicy.MinimumExpanding, QtImport.QSizePolicy.Fixed
        )

        # Qt signal/slot connections ------------------------------------------
        self.bricks_properties_editor.propertyEditedSignal.connect(self.property_edited)

        # Other ---------------------------------------------------------------
        self.menu_items = [self.file_menu, self.view_menu, self.help_menu]
        # self.setwindowIcon(Icons.load_icon("desktop_icon"))
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                self.bricks_properties_editor.add_brick(widget.objectName(), widget)
        self.bricks_properties_editor.bricks_listwidget.sortItems(
            QtImport.Qt.AscendingOrder
        )

    def insert_menu(self, new_menu_item, position):
        """Inserts item in menu"""
        for menu_item in self.menu_items:
            if new_menu_item.title() == menu_item.title():
                return

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
            # This should be based on instance connection
            # restore colour if master/client/etc
            self.original_style = self.styleSheet()
        if self.expert_mode_action.isChecked():
            res = QtImport.QInputDialog.getText(
                self,
                "Switch to expert mode",
                "Please enter the password:",
                QtImport.QLineEdit.Password,
            )
            if res[1]:
                if str(res[0]) == self.expert_pwd:
                    self.set_exp_mode(True)
                    self.expert_mode_action.setChecked(True)
                else:
                    self.expert_mode_action.setChecked(False)
                    QtImport.QMessageBox.critical(
                        self,
                        "Switch to expert mode",
                        "Wrong password!",
                        QtImport.QMessageBox.Ok,
                    )
            else:
                self.expert_mode_action.setChecked(False)
        else:
            self.set_exp_mode(False)

    def set_exp_mode(self, state):
        """Set widgets in expert mode"""

        if not self.execution_mode:
            return

        self.info_for_developers_action.setEnabled(state)
        self.brick_properties_action.setEnabled(state)
        self.reload_hwr_action.setEnabled(state)

        if state:
            # switch to expert mode
            # QObject.emit(self.parent,
            #                    SIGNAL("enableExpertMode"),
            #                    True)
            self.parent.enableExpertModeSignal.emit(True)
            # go through all bricks and execute the method
            for widget in QtImport.QApplication.allWidgets():
                if hasattr(widget, "set_expert_mode"):
                    widget.set_expert_mode(True)
                if isinstance(widget, BaseWidget):
                    try:
                        widget.set_expert_mode(True)
                    except BaseException:
                        logging.getLogger().exception(
                            "Could not set %s to expert mode" % widget.objectName()
                        )
            self.set_color("orange")
        else:
            # switch to user mode
            self.parent.enableExpertModeSignal.emit(False)
            # go through all bricks and execute the method
            for widget in QtImport.QApplication.allWidgets():
                try:
                    if hasattr(widget, "set_expert_mode"):
                        # if isinstance(widget, BaseWidget):
                        widget.setWhatsThis("")
                        try:
                            widget.set_expert_mode(False)
                        except BaseException:
                            logging.getLogger().exception(
                                "Could not set %s to user mode" % widget.objectName()
                            )
                except NameError:
                    logging.getLogger().warning("Widget {} has no attribute {}"
                                                .format(widget, "set_expert_mode"))
            if self.original_style:
                self.setStyleSheet(self.original_style)

    def reload_hwr_clicked(self):
        """Reloads hardware objects"""
        hwr = HWR.getHardwareRepository()
        hwr.reloadHardwareObjects()

    def edit_brick_properties(self):
        """Opens dialog that allows to edit propeties of gui bricks"""
        self.bricks_properties_editor.show()

    def property_edited(self):
        self.saveConfigSignal.emit()

    def whats_this_clicked(self):
        """Whats this"""

        if self.execution_mode:
            BaseWidget.update_whats_this()

    def about_clicked(self):
        """Display dialog with info about mxcube"""

        QtImport.QMessageBox.about(
            self,
            "About MXCuBE",
            """<b>MXCuBE v %s </b>
               <p>Macromolecular Xtallography Customized Beamline Environment<p>
               Python %s - Qt %s - PyQt %s on %s"""
            % (
                "2x",
                platform.python_version(),
                QtImport.qt_version_no,
                QtImport.pyqt_version_no,
                platform.system(),
            ),
        )

    def shortcuts_clicked(self):
        shortcuts_text = """<b>Ctrl + 1</b>   : start 3 click centering<br>
              <b>Ctrl + 2</b>   : save new centering point<br>
              <b>Ctrl + 3</b>   : create new helical line<br>
              <b>Ctrl + 4</b>   : start grid drawing<br><br>
              <b>Ctrl + a</b>   : select all centering points<br>
              <b>Ctrl + d</b>   : deselect all graphical items<br>
              <b>Ctrl + x</b>   : delete all graphical items<br><br>
              <b>Ctrl + +/-</b> : zoom in/out<br><br>
              <b>Mouse wheel +/-</b> : rotate sample
           """
        QtImport.QMessageBox.about(self, "Available shortcuts", shortcuts_text)

    def quit_clicked(self):
        """Exit mxcube"""

        if self.execution_mode:
            QtImport.QApplication.quit()

    def info_for_developers_clicked(self):
        """Opens webpage with documentation"""

        path_list = os.path.dirname(__file__)
        filename = os.path.join(*path_list[:-2])
        filename = os.path.join(os.sep, filename, "docs/build/index.html")
        if os.path.exists(filename):
            webbrowser.open(filename)
        else:
            logging.getLogger().error(
                "Could not find html file %s. "
                + "Use sphinx to build documentation (in doc dir execute "
                + "'sphinx-build source build')" % filename
            )

    def user_manual_clicked(self):
        """Opens user manual"""

        path_list = os.path.dirname(__file__).split(os.sep)
        filename = os.path.join(*path_list[:-2])
        filename = os.path.join(os.sep, filename, "docs/build/user_manual.html")
        if os.path.exists(filename):
            webbrowser.open(filename)
        else:
            logging.getLogger().error("Could not find html file %s" % filename)

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

        QtImport.QApplication.activeWindow().showMaximized()

    def view_normal_clicked(self):
        """Show normal window"""

        QtImport.QApplication.activeWindow().showNormal()

    def view_min_clicked(self):
        """Show minimized window"""

        QtImport.QApplication.activeWindow().showMinimized()

    def append_windows_links(self, windows_list):
        """If there are more than one window then appends names
           of available windows to the menu Windows
        """
        if len(windows_list) > 1:
            self.view_windows_menu.setEnabled(True)
            self.preview_windows = {}
            for window in windows_list:
                self.preview_windows[window.base_caption] = window
                self.view_windows_menu.addAction(
                    window.base_caption, partial(self.view_window, window.base_caption)
                )

    def view_window(self, window_caption):
        """Displays selected window"""
        self.preview_windows[window_caption].show()
        self.preview_windows[window_caption].activateWindow()


class CustomToolBar(QtImport.QToolBar):
    """Custom toolbar"""

    def __init__(self, parent):
        """Parent *must* be the window
           It contains a centralWidget in its viewport
        """

        QtImport.QToolBar.__init__(self)

        self.setSizePolicy(
            QtImport.QSizePolicy.MinimumExpanding, QtImport.QSizePolicy.Fixed
        )


class CustomGroupBox(QtImport.QGroupBox):
    def __init__(self, *args, **kwargs):
        QtImport.QGroupBox.__init__(self, args[0])
        self.setObjectName(args[1])
        self.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding
        )

        if kwargs["layout"] == "horizontal":
            __group_box_layout = QtImport.QHBoxLayout(self)
        else:
            __group_box_layout = QtImport.QVBoxLayout(self)
        __group_box_layout.setSpacing(0)
        __group_box_layout.setContentsMargins(0, 0, 0, 0)

        self.toggled.connect(self.set_checked)

    def set_checked(self, state):
        for child in self.children():
            if hasattr(child, "setVisible"):
                child.setVisible(state)

class Spacer(QtImport.QFrame):
    """Spacer widget"""

    def __init__(self, *args, **kwargs):
        """init"""
        QtImport.QFrame.__init__(self, args[0])
        self.setObjectName(args[1])

        self.orientation = kwargs.get("orientation", "horizontal")
        self.execution_mode = kwargs.get("execution_mode", False)

        self.setFixedSize(-1)

        if self.orientation == "horizontal":
            self.main_layout = QtImport.QHBoxLayout(self)
        else:
            self.main_layout = QtImport.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def setFixedSize(self, fixed_size):
        """Sets fixed size"""

        if fixed_size >= 0:
            hor_size_policy = (
                self.orientation == "horizontal"
                and QtImport.QSizePolicy.Fixed
                or QtImport.QSizePolicy.MinimumExpanding
            )
            ver_size_policy = (
                hor_size_policy == QtImport.QSizePolicy.Fixed
                and QtImport.QSizePolicy.MinimumExpanding
                or QtImport.QSizePolicy.Fixed
            )

            if self.orientation == "horizontal":
                self.setFixedWidth(fixed_size)
            else:
                self.setFixedHeight(fixed_size)
        else:
            hor_size_policy = (
                self.orientation == "horizontal"
                and QtImport.QSizePolicy.Expanding
                or QtImport.QSizePolicy.MinimumExpanding
            )
            ver_size_policy = (
                hor_size_policy == QtImport.QSizePolicy.Expanding
                and QtImport.QSizePolicy.MinimumExpanding
                or QtImport.QSizePolicy.Expanding
            )
        self.setSizePolicy(hor_size_policy, ver_size_policy)

    def paintEvent(self, event):
        """Paints the widgets"""

        QtImport.QFrame.paintEvent(self, event)

        if self.execution_mode:
            return
        painter = QtImport.QPainter(self)
        painter.setPen(QtImport.QPen(QtImport.Qt.black, 3))

        if self.orientation == "horizontal":
            height = self.height() / 2
            painter.drawLine(0, height, self.width(), height)
            painter.drawLine(0, height, 5, height - 5)
            painter.drawLine(0, height, 5, height + 5)
            painter.drawLine(self.width(), height, self.width() - 5, height - 5)
            painter.drawLine(self.width(), height, self.width() - 5, height + 5)
        else:
            width = self.width() / 2
            painter.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
            painter.drawLine(width, 0, width - 5, 5)
            painter.drawLine(width, 0, width + 5, 5)
            painter.drawLine(width, self.height(), width - 5, self.height() - 5)
            painter.drawLine(width, self.height(), width + 5, self.height() - 5)

class CustomFrame(QtImport.QFrame):
    def __init__(self, *args, **kwargs):
        """init"""
        QtImport.QFrame.__init__(self, args[0])

        self.setObjectName(args[1])
        self.pinned = True
        self.dialog = None
        self.origin_parent = self.parent()
        self.origin_index = None
        execution_mode = kwargs.get("execution_mode", False)

        if not execution_mode:
            self.setFrameStyle(QtImport.QFrame.Box | QtImport.QFrame.Plain)

        if kwargs.get("layout") == "vertical":
            __frame_layout = QtImport.QVBoxLayout(self)
        else:
            __frame_layout = QtImport.QHBoxLayout(self)

        self.open_in_dialog_button = QtImport.QPushButton(
            Icons.load_icon("UnLock"), ""
        )
        self.open_in_dialog_button.setFixedWidth(30)
        # self.open_in_dialog_button.setObjectName("pin")
        self.open_in_dialog_button.setVisible(False)

        self.dialog = QtImport.QDialog(self.parent())
        self.dialog_layout = QtImport.QVBoxLayout(self.dialog)

        __frame_layout.addWidget(self.open_in_dialog_button)
        __frame_layout.setSpacing(0)
        __frame_layout.setContentsMargins(0, 0, 0, 0)

        self.open_in_dialog_button.clicked.connect(self.show_in_dialog_toggled)

    def show_in_dialog_toggled(self):
        if self.pinned:
            self.pinned = False
            self.open_in_dialog_button.setIcon(Icons.load_icon("Lock"))
            self.origin_index = self.origin_parent.layout().indexOf(self)
            self.origin_parent.layout().removeWidget(self)
            self.dialog_layout.addWidget(self)
            self.dialog.show()
        else:
            self.pinned = True
            self.open_in_dialog_button.setIcon(Icons.load_icon("UnLock"))
            self.dialog_layout.removeWidget(self)
            self.origin_parent.layout().insertWidget(self.origin_index, self)
            self.dialog.close()

    def set_background_color(self, color):
        Colors.set_widget_color(self, color, QtImport.QPalette.Background)

    def set_expert_mode(self, expert_mode):
        self.open_in_dialog_button.setVisible(expert_mode)

class CustomTabWidget(QtImport.QTabWidget):
    """Tab widget"""

    # notebookPageChangedSignal = pyqtSignal(str)
    tabChangedSignal = QtImport.pyqtSignal(int, object)

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QTabWidget.__init__(self, args[0])
        self.setObjectName(args[1])
        self.open_in_dialog_button = None
        self.close_tab_button = None
        self.pinned = True

        # self.tab_widgets = []
        self.count_changed = {}
        self.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding
        )
        self.currentChanged.connect(self._page_changed)

        self.dialog = QtImport.QDialog(self.parent())
        self.dialog_layout = QtImport.QVBoxLayout(self.dialog)

    def _page_changed(self, index):
        """Page changed event"""

        page = self.widget(index)
        self.count_changed[index] = False

        self.tabChangedSignal.emit(index, page)

        tab_name = self.objectName()
        BaseWidget.update_tab_widget(tab_name, index)

    def add_tab(self, page_widget, label, icon=""):
        """Add tab"""

        scroll_area = page_widget
        self.addTab(scroll_area, label)

        slot_name = "showPage_%s" % label

        def tab_show_slot(self, page_index=self.indexOf(scroll_area)):
            self.setCurrentIndex(page_index)

        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                tab_show_slot, self
            )
        except BaseException:
            logging.getLogger().exception(
               "Could not add slot %s " % slot_name + "in %s" % self.objectName()
            )
        slot_name = "hidePage_%s" % label

        def tab_hide_slot(
            self,
            hide=True,
            page={
                "widget": scroll_area,
                "label": label,
                "index": self.indexOf(scroll_area),
                "icon": icon,
                "hidden": False,
            },
        ):

            if hide:
                if not page["hidden"]:
                    self.removeTab(self.indexOf(page["widget"]))
                    self.repaint()
                    page["hidden"] = True
            else:
                if page["hidden"]:
                    if icon:
                        self.insertTab(
                            page["index"],
                            page["widget"],
                            Icons.load_icon(icon),
                            label,
                        )
                    else:
                        self.insertTab(page["index"], page["widget"], page["label"])
                    slot_name = "showPage_%s" % page["label"].replace(" ", "_")
                    getattr(self, slot_name)()
                    page["hidden"] = False
                else:
                    slot_name = "showPage_%s" % page["label"].replace(" ", "_")
                    getattr(self, slot_name)()
                self.setCurrentWidget(page["widget"])
        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                tab_hide_slot, self
            )
        except BaseException:
            logging.getLogger().exception(
                "Could not add slot %s " % slot_name
                 + "in %s" % str(self.objectName())
            )

        # add 'enable page' slot
        slot_name = "enablePage_%s" % label

        def enable_page_slot(self, enable, page_index=self.indexOf(scroll_area)):
            self.page(page_index).setEnabled(enable)

        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                enable_page_slot, self
            )
        except BaseException:
            logging.getLogger().exception(
                "Could not add slot %s " % slot_name
                + "in %s" % str(self.objectName())
            )

        # add 'enable tab' slot
        slot_name = "enableTab_%s" % label

        def tab_enable_slot(self, enable, page_index=self.indexOf(scroll_area)):
            self.setTabEnabled(page_index, enable)

        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                tab_enable_slot, self
                )
        except BaseException:
            logging.getLogger().exception(
                "Could not add slot %s " % slot_name
                + "in %s" % str(self.objectName())
            )

        # add 'tab reset count' slot
        slot_name = "resetTabCount_%s" % label

        def tab_reset_count_slot(
            self, erase_count, page_index=self.indexOf(scroll_area)
        ):
            tab_label = str(self.tabLabel(self.page(page_index)))
            label_list = tab_label.split()
            found = False
            try:
                count = label_list[-1]
                try:
                    found = count[0] == "("
                except BaseException:
                    pass
                else:
                    try:
                        found = count[-1] == ")"
                    except BaseException:
                        pass
            except BaseException:
                pass
            if found:
                try:
                    int(count[1:-1])
                except BaseException:
                    pass
                else:
                    new_label = " ".join(label_list[0:-1])
                    if not erase_count:
                        new_label += " (0)"
                    self.count_changed[page_index] = False
                    self.setTabLabel(self.page(page_index), new_label)
            else:
                if not erase_count:
                    new_label = " ".join(label_list)
                    new_label += " (0)"
                    self.count_changed[page_index] = False
                    self.setTabLabel(self.page(page_index), new_label)
        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                tab_reset_count_slot, self
            )
        except BaseException:
            logging.getLogger().exception(
                "Could not add slot %s " % slot_name + "in %s" % str(self.name())
            )

        # add 'tab increase count' slot
        slot_name = "incTabCount_%s" % label

        def tab_inc_count_slot(
            self, delta, only_if_hidden, page_index=self.indexOf(scroll_area)
        ):
            if only_if_hidden and page_index == self.currentPageIndex():
                return
            tab_label = str(self.tabLabel(self.page(page_index)))
            label_list = tab_label.split()
            found = False
            try:
                count = label_list[-1]
                try:
                    found = count[0] == "("
                except BaseException:
                    pass
                else:
                    try:
                        found = count[-1] == ")"
                    except BaseException:
                        pass
            except BaseException:
                pass
            if found:
                try:
                    num = int(count[1:-1])
                except BaseException:
                    pass
                else:
                    new_label = " ".join(label_list[0:-1])
                    new_label += " (%d)" % (num + delta)
                    self.count_changed[page_index] = True
                    self.setTabLabel(self.page(page_index), new_label)
            else:
                new_label = " ".join(label_list)
                new_label += " (%d)" % delta
                self.count_changed[page_index] = True
                self.setTabLabel(self.page(page_index), new_label)

        try:
            self.__dict__[slot_name.replace(" ", "_")] = types.MethodType(
                tab_inc_count_slot, self
            )
        except BaseException:
            logging.getLogger().exception(
                "Could not add slot %s " % slot_name
                + "in %s" % str(self.objectName())
            )

        # that's the real page
        return scroll_area

def get_vertical_spacer(*args, **kwargs):
    """Vertical spacer"""
    kwargs["orientation"] = "vertical"
    return Spacer(*args, **kwargs)

def get_horizontal_spacer(*args, **kwargs):
    """Horizontal spacer"""

    kwargs["orientation"] = "horizontal"
    return Spacer(*args, **kwargs)

def get_horizontal_splitter(*args, **kwargs):
    """Horizontal splitter"""

    return QtImport.QSplitter(QtImport.Qt.Horizontal, *args)

def get_vertical_splitter(*args, **kwargs):
    """Vertical splitter"""

    return QtImport.QSplitter(QtImport.Qt.Vertical, *args)

def get_vertical_box(*args, **kwargs):
    """Vertical box"""
    kwargs["layout"] = "vertical"
    return CustomFrame(*args, **kwargs)

def get_horizontal_box(*args, **kwargs):
    """Horizontal box"""

    kwargs["layout"] = "horizontal"
    return CustomFrame(*args, **kwargs)

def get_horizontal_groupbox(*args, **kwargs):
    """Horizontal group box"""

    kwargs["layout"] = "horizontal"
    return CustomGroupBox(*args, **kwargs)

def get_vertical_groupbox(*args, **kwargs):
    """Vertical group box"""

    kwargs["layout"] = "vertical"
    return CustomGroupBox(*args, **kwargs)

class WindowDisplayWidget(QtImport.QScrollArea):
    """Main widget"""

    items = {
        "vbox": get_vertical_box,
        "hbox": get_horizontal_box,
        "vgroupbox": get_vertical_groupbox,
        "hgroupbox": get_horizontal_groupbox,
        "vspacer": get_vertical_spacer,
        "hspacer": get_horizontal_spacer,
        "icon": CustomLabel,
        "label": CustomLabel,
        "tab": CustomTabWidget,
        "hsplitter": get_horizontal_splitter,
        "vsplitter": get_vertical_splitter,
    }

    brickChangedSignal = QtImport.pyqtSignal(str, str, str, tuple, bool)
    tabChangedSignal = QtImport.pyqtSignal(str, int)
    enableExpertModeSignal = QtImport.pyqtSignal(bool)
    windowClosedSignal = QtImport.pyqtSignal()
    isShownSignal = QtImport.pyqtSignal()
    isHiddenSignal = QtImport.pyqtSignal()
    itemClickedSignal = QtImport.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """__init__ of WindowDisplayWidget"""

        QtImport.QScrollArea.__init__(self, args[0])

        self.additional_windows = {}
        self.__put_back_colors = None
        self.execution_mode = kwargs.get("execution_mode", False)
        self.preview_items = []
        self.current_window = None
        self.base_caption = ""
        self.close_on_exit = False
        self.setWindowTitle("GUI preview")
        self.progress_dialog_base_label = ""

        self.central_widget = QtImport.QWidget(self.widget())
        # self.central_widget.setObjectName("deee")
        self.central_widget_layout = QtImport.QVBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.show()

        self._toolbar = CustomToolBar(self)
        self._toolbar.hide()
        self._menubar = CustomMenuBar(self)
        self._menubar.hide()
        self._statusbar = QtImport.QStatusBar(self)
        self._statusbar.hide()

        self._keep_open_checkbox = QtImport.QCheckBox("Keep window open")
        self._keep_open_checkbox.hide() 

        self._statusbar_user_label = QtImport.QLabel("-")
        self._statusbar_state_label = QtImport.QLabel(" <b>State: -</b>")
        self._statusbar_diffractometer_label = QtImport.QLabel(
            " <b>Diffractometer: -</b>"
        )
        self._statusbar_sc_label = QtImport.QLabel(" <b>Sample changer: -</b>")
        self._statusbar_last_collect_label = QtImport.QLabel(" <b>Last collect: -</b>")
        self._progress_bar = QtImport.QProgressBar()
        # TODO make it via property
        self._progress_bar.setEnabled(False)
        self._progress_bar.setVisible(False)

        self._file_system_status_label = QtImport.QLabel("File system")
        self._edna_status_label = QtImport.QLabel("EDNA")
        self._ispyb_status_label = QtImport.QLabel("ISPyB")

        self._warning_box = QtImport.QMessageBox(
             QtImport.QMessageBox.Question,
             "Warning",
             "-",
             QtImport.QMessageBox.Ok
        )
        self._warning_box.setModal(True)

        self._statusbar.addWidget(self._statusbar_user_label)
        self._statusbar.addWidget(self._statusbar_state_label)
        self._statusbar.addWidget(self._statusbar_diffractometer_label)
        self._statusbar.addWidget(self._statusbar_sc_label)
        self._statusbar.addWidget(self._progress_bar)
        self._statusbar.addWidget(self._statusbar_last_collect_label)

        self._statusbar.addPermanentWidget(self._file_system_status_label)
        self._statusbar.addPermanentWidget(self._edna_status_label)
        self._statusbar.addPermanentWidget(self._ispyb_status_label)

        self._progress_dialog = QtImport.QProgressDialog(self)
        self._progress_dialog.setWindowFlags(
            QtImport.Qt.Window
            | QtImport.Qt.WindowTitleHint
            | QtImport.Qt.CustomizeWindowHint
        )
        new_palette = QtImport.QPalette()
        new_palette.setColor(QtImport.QPalette.Highlight, Colors.DARK_GREEN)
        self._progress_dialog.setPalette(new_palette)

        self._progress_dialog.setWindowTitle("Please wait...")
        self._progress_dialog.setCancelButton(None)
        self._progress_dialog.setModal(True)
        self._progress_dialog.close()

        # _statusbar_hlayout = QtGui.QHBoxLayout(self.statusbar)
        # _statusbar_hlayout.setSpacing(2)
        # _statusbar_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._menubar)
        _main_vlayout.addWidget(self._keep_open_checkbox)
        _main_vlayout.addWidget(self._toolbar)
        _main_vlayout.addWidget(self.central_widget)
        _main_vlayout.addWidget(self._statusbar)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self._menubar.viewToolBarSignal.connect(self.view_toolbar_toggled)

        self.setWindowFlags(self.windowFlags() | QtImport.Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(Icons.load_icon("desktop_icon"))

        self._menubar.saveConfigSignal.connect(self.save_config_requested)

    def set_keep_open(self, keep_open):
        if keep_open:
            self._keep_open_checkbox.show()

    def save_config_requested(self):
        pass
        # print self.central_widget.parent().parent()

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
        BaseWidget._menubar = self._menubar
        BaseWidget._toolbar = self._toolbar

    def show_statusbar(self):
        """Sets statusbar"""
        self._statusbar.show()
        BaseWidget._statusbar = self._statusbar

    #def set_progress_dialog(self):
    #    BaseWidget._progress_dialog = self._progress_dialog

    def show_warning_box(self, warning_msg):
        self._warning_box.setText(warning_msg)
        self._warning_box.show()

    def update_status_info(self, info_type, info_message, info_state="ready"):
        """Updates status info"""

        if info_message == "":
            info_message = "Ready"

        msg = None
        selected_label = None

        if info_type == "user":
            selected_label = self._statusbar_user_label
            msg = info_message
        elif info_type == "status":
            selected_label = self._statusbar_state_label
            msg = " <b>State: </b> %s" % info_message
        elif info_type == "diffractometer":
            selected_label = self._statusbar_diffractometer_label
            msg = " <b>Diffractometer: </b>%s" % info_message
        elif info_type == "sc":
            selected_label = self._statusbar_sc_label
            msg = " <b>Sample changer: </b> %s" % info_message
        elif info_type == "collect":
            selected_label = self._statusbar_last_collect_label
            msg = " <b>Last collect: </b> %s (%s)" % (
                info_message,
                time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        elif info_type == "file_system":
            selected_label = self._file_system_status_label
        elif info_type == "edna":
            selected_label = self._edna_status_label
        elif info_type == "ispyb":
            selected_label = self._ispyb_status_label

        if msg:
            selected_label.setText(msg)
        if selected_label in (
            None,
            self._statusbar_user_label,
            self._statusbar_last_collect_label,
        ):
            return

        if info_state:
            info_state = info_state.lower()

        if info_state in ("ready", "success") or info_message.lower() == "ready":
            Colors.set_widget_color(selected_label, Colors.LIGHT_GREEN)
        elif info_state == "action_req":
            Colors.set_widget_color(selected_label, Colors.LIGHT_ORANGE)
        elif info_state == "error" or "alarm" in info_message.lower():
            Colors.set_widget_color(selected_label, Colors.LIGHT_RED)
        else:
            Colors.set_widget_color(selected_label, Colors.LIGHT_YELLOW)

    def init_progress_bar(self, progress_type, number_of_steps):
        self._progress_bar.setEnabled(True)
        self._progress_bar.reset()
        self._progress_bar.setMaximum(number_of_steps)

    def set_progress_bar_step(self, step):
        self._progress_bar.set_value(step)

    def stop_progress_bar(self):
        self._progress_bar.reset()
        self._progress_bar.setEnabled(False)

    def open_progress_dialog(self, msg, max_steps):
        QtImport.QApplication.setOverrideCursor(
            QtImport.QCursor(QtImport.Qt.BusyCursor)
        )
        self.progress_dialog_base_label = msg
        self._progress_dialog.setWindowTitle(msg)
        self._progress_dialog.setLabelText(msg)
        self._progress_dialog.setMaximum(max_steps)
        self._progress_dialog.show()

    def set_progress_dialog_step(self, step, msg):
        self._progress_dialog.setValue(step)
        if msg:
            self._progress_dialog.setLabelText(msg)

    def close_progress_dialog(self):
        QtImport.QApplication.setOverrideCursor(
            QtImport.QCursor(QtImport.Qt.ArrowCursor)
        )
        self._progress_dialog.close()

    def show(self, *args):
        """Show"""

        ret = QtImport.QWidget.show(self)
        self.isShownSignal.emit()
        # self.emit(SIGNAL("isShown"), ())
        return ret

    def closeEvent(self, event):
        event.accept()
        if self.close_on_exit:
            QtImport.QApplication.exit(0)

    def hide(self, *args):
        """Hide"""
        if not self._keep_open_checkbox.isChecked():
            ret = QtImport.QWidget.hide(self)
            self.isHiddenSignal.emit()
            # self.emit(SIGNAL("isHidden"), ())
            return ret

    def set_caption(self, caption):
        """Set caption"""
        ret = QtImport.QWidget.setWindowTitle(self, caption)
        self.base_caption = caption
        return ret

    def update_instance_caption(self, instance_caption):
        """Update caption if instance mode (master,slave) changed"""

        QtImport.QWidget.setWindowTitle(self, self.base_caption + instance_caption)

    def exitExpertMode(self, *args):
        """Exit expert mode"""

        if len(args) > 0:
            if args[0]:
                return
        self._menubar.set_exp_mode(False)

    def add_item(self, item_cfg, parent):
        """Adds item to the gui"""

        item_type = item_cfg["type"]
        new_item = None

        try:
            klass = WindowDisplayWidget.items[item_type]
        except KeyError:
            new_item = item_cfg["brick"]
        else:
            new_item = klass(
                parent, item_cfg["name"], execution_mode=self.execution_mode
            )
            if item_type in ("vbox", "hbox", "vgroupbox", "hgroupbox"):
                if item_cfg["properties"]["color"] is not None:
                    qtcolor = QtImport.QColor(item_cfg["properties"]["color"])
                    Colors.set_widget_color(new_item, qtcolor)

                if item_type.endswith("groupbox"):
                    new_item.setTitle(item_cfg["properties"]["label"])
                    if item_cfg["properties"]["checkable"]:
                        new_item.setCheckable(True)
                        new_item.set_checked(item_cfg["properties"]["setCheckable"])

                new_item.layout().setSpacing(item_cfg["properties"]["spacing"])
                if hasattr(new_item.layout(), "setContentsMargins"):
                    new_item.layout().setContentsMargins(
                        item_cfg["properties"]["margin"],
                        item_cfg["properties"]["margin"],
                        item_cfg["properties"]["margin"],
                        item_cfg["properties"]["margin"],
                    )
                elif hasattr(new_item.layout(), "setMargins"):
                    new_item.layout().setMargin(item_cfg["properties"]["margin"])
                frame_style = QtImport.QFrame.NoFrame
                if item_cfg["properties"]["frameshape"] != "default":
                    frame_style = getattr(
                        QtImport.QFrame, item_cfg["properties"]["frameshape"]
                    )
                if item_cfg["properties"]["shadowstyle"] != "default":
                    frame_style = frame_style | getattr(
                        QtImport.QFrame,
                        item_cfg["properties"]["shadowstyle"].capitalize(),
                    )
                if frame_style != QtImport.QFrame.NoFrame:
                    try:
                        new_item.setFrameStyle(frame_style)
                    except BaseException:
                        logging.getLogger().exception(
                            "Could not set frame style on " + "item %s",
                            item_cfg["name"],
                        )
                if item_cfg["properties"]["fixedwidth"] > -1:
                    new_item.setFixedWidth(item_cfg["properties"]["fixedwidth"])
                if item_cfg["properties"]["fixedheight"] > -1:
                    new_item.setFixedHeight(item_cfg["properties"]["fixedheight"])
            elif item_type == "icon":
                img = QtImport.QPixmap()
                if img.load(item_cfg["properties"]["filename"]):
                    new_item.setPixmap(img)
            elif item_type == "label":
                new_item.setText(item_cfg["properties"]["text"])
            elif item_type == "tab":
                item_cfg.widget = new_item
                button_widget = QtImport.QWidget(new_item)

                new_item.open_in_dialog_button = QtImport.QToolButton(button_widget)
                new_item.open_in_dialog_button.setIcon(Icons.load_icon("Frames2"))
                new_item.open_in_dialog_button.setFixedSize(22, 22)

                new_item.close_tab_button = QtImport.QToolButton(button_widget)
                new_item.close_tab_button.setIcon(Icons.load_icon("delete_small"))
                new_item.close_tab_button.setFixedSize(22, 22)

                __button_widget_vlayout = QtImport.QHBoxLayout(button_widget)
                __button_widget_vlayout.addWidget(new_item.open_in_dialog_button)
                __button_widget_vlayout.addWidget(new_item.close_tab_button)
                __button_widget_vlayout.setSpacing(2)
                __button_widget_vlayout.setContentsMargins(0, 0, 0, 0)

                new_item.setCornerWidget(button_widget)
                new_item.open_in_dialog_button.hide()
                new_item.close_tab_button.hide()

                def close_current_page():
                    tab = new_item
                    slot_name = "hidePage_%s" % str(tab.tabText(tab.currentIndex()))
                    slot_name = slot_name.replace(" ", "_")
                    getattr(tab, slot_name)()

                def open_in_dialog():
                    if new_item.pinned:
                        new_item.pinned = False
                        new_item.open_in_dialog_button.setIcon(Icons.load_icon("Lock"))
                        current_widget = new_item.currentWidget()
                        new_item.removeTab(new_item.currentIndex())
                        new_item.dialog_layout.addWidget(current_widget)
                        new_item.dialog.show()
                    else:
                        new_item.pinned = True
                        new_item.open_in_dialog_button.setIcon(
                            Icons.load_icon("UnLock")
                        )
                        # self.dialog_layout.removeWidget(self)
                        # self.origin_parent.layout().insertWidget(self.origin_index, self)
                        new_item.dialog.close()

                def current_page_changed(index):
                    item_cfg.notebook_page_changed(new_item.tabText(index))

                new_item._close_current_page_cb = close_current_page
                new_item.currentChanged.connect(current_page_changed)
                new_item.close_tab_button.clicked.connect(close_current_page)
                new_item.open_in_dialog_button.clicked.connect(open_in_dialog)

            elif item_type == "vsplitter" or type == "hsplitter":
                pass

            new_item.show()

        return new_item

    def make_item(self, item_cfg, parent):
        """Make item"""
        for child in item_cfg["children"]:
            try:
                new_item = self.add_item(child, parent)
            except BaseException:
                logging.getLogger().exception("Cannot add item %s" % child["name"])
            else:
                if not self.execution_mode:
                    new_item.installEventFilter(self)
            if parent.__class__ == WindowDisplayWidget.items["tab"]:
                new_tab = parent.add_tab(
                    new_item, child["properties"]["label"], child["properties"]["icon"]
                )
                new_tab.item_cfg = child
                self.preview_items.append(new_item)
            else:
                if isinstance(child, ContainerCfg):
                    new_item.setSizePolicy(
                        self.getSizePolicy(
                            child["properties"]["hsizepolicy"],
                            child["properties"]["vsizepolicy"],
                        )
                    )
                if not isinstance(child, BrickCfg):
                    if child["properties"].has_property("fontSize"):
                        font = new_item.font()
                        if int(child["properties"]["fontSize"]) <= 0:
                            child["properties"].get_property("fontSize").set_value(
                                font.pointSize()
                            )
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
                        alignment_flags = self.getAlignmentFlags(
                            child["properties"]["alignment"]
                        )
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
                        layout.addWidget(
                            new_item, stretch, QtImport.Qt.Alignment(alignment_flags)
                        )
                    else:
                        layout.addWidget(new_item, stretch)
            self.make_item(child, new_item)

    def draw_preview(self, container_cfg, window_id):
        """Draw preview"""

        for (window, m) in self.additional_windows.values():
            window.close()

        # reset colors
        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
            self.__put_back_colors = None

        if self.current_window is not None and self.current_window != window_id:
            # remove all bricks and destroy all other items
            self.central_widget.close()
            self.central_widget = QtImport.QWidget(self.viewport())
            self.central_widget_layout = QtImport.QVBoxLayout(self.central_widget)
            self.central_widget.show()

        self.current_window = window_id

        parent = self.central_widget

        self.setObjectName(container_cfg["name"])
        self.preview_items.append(self)

        if isinstance(container_cfg, WindowCfg):
            self.setObjectName(container_cfg["name"])
            if container_cfg.properties["menubar"]:
                self.set_menu_bar(
                    container_cfg.properties["menudata"],
                    container_cfg.properties["expertPwd"],
                    self.execution_mode,
                )
            else:
                try:
                    self.additional_windows[window_id][1].hide()
                except BaseException:
                    pass

        self.make_item(container_cfg, parent)

        if isinstance(container_cfg, WindowCfg):
            if container_cfg.properties["statusbar"]:
                self.show_statusbar()

        #self.set_progress_dialog()
        BaseWidget._progress_dialog = self._progress_dialog
        BaseWidget._warning_box = self._warning_box

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
                    # item_widget.deleteLater()

    def add_widget(self, child, parent):
        """Add widget"""

        if parent is None:
            self.draw_preview(child, 0)
        else:
            for item in self.preview_items:
                if item.objectName() == parent.name:
                    parent_item = item
            new_item = self.add_item(child, parent_item)
            if isinstance(parent, TabCfg):
                new_tab = parent_item.add_tab(
                    new_item, child["properties"]["label"], child["properties"]["icon"]
                )
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

            if (
                new_index != current_index
                and new_index > -1
                and new_index < parent_layout.count()
            ):
                parent_layout.removeWidget(item)
                parent_layout.insertWidget(new_index, item)

    def update_preview(self, selected_item):
        """Method selects a widget in the gui"""

        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
            self.__put_back_colors = None
        if len(selected_item) and len(self.preview_items) > 0:
            for item in self.preview_items:
                if item.objectName() == selected_item:
                    self.select_widget(item)
                    return

    def select_widget(self, widget):
        """Colors selected widget"""

        if isinstance(self.__put_back_colors, collections.Callable):
            self.__put_back_colors()
        original_color = widget.palette().color(QtImport.QPalette.Window)
        selected_color = QtImport.QColor(150, 150, 200)
        Colors.set_widget_color(widget, selected_color, QtImport.QPalette.Background)

        def put_back_colors(wref=weakref.ref(widget), bkgd_color=original_color):
            widget = wref()
            if widget is not None:
                Colors.set_widget_color(
                    widget, bkgd_color, QtImport.QPalette.Background
                )

        self.__put_back_colors = put_back_colors

    def eventFilter(self, widget, event):
        """Even filter"""

        if widget is not None and event is not None:
            if (
                event.type() == QtImport.QEvent.MouseButtonRelease
                and event.button() == QtImport.Qt.LeftButton
            ):
                self.itemClickedSignal.emit(widget.objectName())
                return True

        return QtImport.QScrollArea.eventFilter(self, widget, event)

    def getAlignmentFlags(self, alignment_directives_string):
        """Returns alignment flags"""

        if alignment_directives_string is None:
            alignment_directives = ["none"]
        else:
            alignment_directives = alignment_directives_string.split()
        alignment_flags = 0

        if "none" in alignment_directives:
            return alignment_flags
        if "hcenter" in alignment_directives:
            return QtImport.Qt.AlignHCenter
        if "vcenter" in alignment_directives:
            return QtImport.Qt.AlignVCenter
        if "top" in alignment_directives:
            alignment_flags = QtImport.Qt.AlignTop
        if "bottom" in alignment_directives:
            alignment_flags = QtImport.Qt.AlignBottom
        if "center" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtImport.Qt.AlignCenter
            else:
                alignment_flags = alignment_flags | QtImport.Qt.AlignHCenter
        if "left" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtImport.Qt.AlignLeft | QtImport.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtImport.Qt.AlignLeft
        if "right" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtImport.Qt.AlignRight | QtImport.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtImport.Qt.AlignRight
        return alignment_flags

    def getSizePolicy(self, hsizepolicy, vsizepolicy):
        """Returns size policy"""

        def _get_size_policy_flag(policy_flag):
            if policy_flag == "expanding":
                return QtImport.QSizePolicy.Expanding
            elif policy_flag == "fixed":
                return QtImport.QSizePolicy.Fixed
            else:
                return QtImport.QSizePolicy.Preferred

        return QtImport.QSizePolicy(
            _get_size_policy_flag(hsizepolicy), _get_size_policy_flag(vsizepolicy)
        )

    def append_windows_links(self, window_list):
        self._menubar.append_windows_links(window_list)

    def set_font_size(self, font_size):
        for widget in self.children():
            if hasattr(widget, "font"):
                font = widget.font()
                font.setPointSize(font_size)
                widget.setFont(font)


class BricksPropertiesEditor(QtImport.QWidget):

    propertyEditedSignal = QtImport.pyqtSignal()

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QWidget.__init__(self, *args)

        self.bricks_dict = {}
        self.selected_brick = None
        self.property_edited = False

        self.bricks_listwidget = QtImport.QListWidget()
        self.properties_table = PropertyEditor.ConfigurationTable(self)

        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.bricks_listwidget)
        _main_vlayout.addWidget(self.properties_table)
        # _main_vlayout.setSpacing(2)
        # _main_vlayout.setContentsMargins(2, 2, 6, 6)

        self.bricks_listwidget.itemClicked.connect(self.bricks_listwidget_item_clicked)

        self.properties_table.propertyChangedSignal.connect(self.property_changed)
        # QtCore.QObject.connect(self.properties_table,
        # QtCore.SIGNAL("propertyChanged"),
        # self.property_changed)

        self.bricks_listwidget.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.MinimumExpanding
        )
        # self.properties_table.setSizePolicy(QSizePolicy.Expanding,
        #                                    QSizePolicy.MinimumExpanding)
        # self.properties_table.horizontalHeader().setStretchLastSection(True)

        self.setWindowTitle("Bricks properties")

    def add_brick(self, name, brick):
        if name != "":
            self.bricks_dict[name] = brick
            self.bricks_listwidget.addItem(name)

    def bricks_listwidget_item_clicked(self, listwidget_item):
        brick_name = listwidget_item.text()
        self.selected_brick = self.bricks_dict[brick_name]
        self.properties_table.set_property_bag(
            self.bricks_dict[brick_name].property_bag
        )

    def property_changed(self, property_name, old_value, new_value):
        self.selected_brick._propertyChanged(property_name, old_value, new_value)
        self.selected_brick.propertyChanged(property_name, old_value, new_value)
        self.property_edited = True

    def closeEvent(self, event):
        if self.property_edited:
            self.propertyEditedSignal.emit()
        self.property_edited = False
        event.accept()
