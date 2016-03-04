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

import os
import new
import logging
import weakref
import platform
import webbrowser

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseLayoutItems import BrickCfg, SpacerCfg, LabelCfg, WindowCfg, ContainerCfg, TabCfg
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework import Qt4_Icons


__version__ = '2.2'


class CustomMenuBar(QtGui.QMenuBar):
    """
    Descript. :
    """
    viewToolBarSignal = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        """
        Descript. : parent *must* be the window ; it contains a centralWidget 
                    in its viewport
        """
        QtGui.QMenuBar.__init__(self)

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
        self.expert_mode_action = self.file_menu.addAction("Expert mode", 
             self.expert_mode_clicked)
        self.expert_mode_action.setCheckable(True)  
        self.file_menu.addAction("Quit", self.quit_clicked)

        self.view_menu = self.addMenu("View")
        self.view_toolbar_action = self.view_menu.addAction("Toolbar", 
             self.view_toolbar_clicked)
        self.view_toolbar_action.setCheckable(True)
 
        #self.view_graphics_manager_action = self.view_menu.addAction(\
        #     "Graphics manager", self.view_graphics_manager_clicked)
        #self.view_graphics_manager_action.setCheckable(True)

        self.expert_mode_action.setCheckable(True) 
        self.help_menu = self.addMenu("Help") 
        self.info_for_developers_action =  self.help_menu.addAction(\
             "Information for developers", self.info_for_developers_clicked)
        self.info_for_developers_action.setEnabled(False)
        self.help_menu.addAction("User manual", self.user_manual_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("Whats this", self.whats_this_clicked)
        self.help_menu.addSeparator()
        self.help_menu.addAction("About", self.about_clicked) 

        # Layout --------------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)


        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.expert_mode_checkboxStdColor=None
        self.menu_items = [self.file_menu,
                           self.view_menu,
                           self.help_menu]
        #self.setwindowIcon(Qt4_Icons.load_icon("desktop_icon"))

    def insert_menu(self, new_menu, position):
        self.clear()
        for index in range(len(self.menu_items)):
            if index == position:
               self.addMenu(new_menu) 
            self.addMenu(self.menu_items[index])

    def get_menu_bar(self):
        """
        Returns. : current menu bar. Method used by other widgets that
                   inserts action in menu bar
        """
        return self.menubar

    def configure(self, menu_data, expert_pwd, execution_mode):
        """
        Descript. :
        """
        self.menu_data = menu_data
        self.expert_pwd = expert_pwd
        self.execution_mode = execution_mode

    def expert_mode_clicked(self):
        """
        Descript. :
        """
        if not self.original_style:
            #This should be based on instance connection
            # restore colour if master/client/etc
            self.original_style =  self.styleSheet() 
        if self.expert_mode_action.isChecked():
            res = QtGui.QInputDialog.getText(self, 
                                             "Switch to expert mode",
                                             "Please enter the password:", 
                                             QtGui.QLineEdit.Password)
            if res[1]:
                if str(res[0]) == self.expert_pwd:
                    #Qt4_widget_colors.set_widget_color(self.expert_mode_action,
                    #                                   Qt4_widget_colors.LIGHT_YELLOW)
                    self.set_exp_mode(True)
                    self.expert_mode_action.setChecked(True)
                else:
                    self.expert_mode_action.setChecked(False)
                    QtGui.QMessageBox.critical(self, 
                                               "Switch to expert mode", 
                                               "Wrong password!",
                                               QtGui.QMessageBox.Ok)
            else:
                 self.expert_mode_action.setChecked(False)
        else:
             #    Qt4_widget_colors.set_widget_color(self.expert_mode_action,
             #    Qt4_widget_colors.LINE_EDIT_ORIGINAL)
             self.set_exp_mode(False)

    def set_exp_mode(self, state):
        """
        Descript. :
        """
        if not self.execution_mode:
            return

        self.info_for_developers_action.setEnabled(state)
               
        if state:
            # switch to expert mode
            QtCore.QObject.emit(self.parent, QtCore.SIGNAL("enableExpertMode"), True)
            # go through all bricks and execute the method
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    try:
                        w.set_expert_mode(True)
                    except:
                        logging.getLogger().exception("Could not set %s to expert mode", w.objectName())
            self.set_color("orange")
        else:
            # switch to user mode
            QtCore.QObject.emit(self.parent, QtCore.SIGNAL("enableExpertMode"), False)

            # go through all bricks and execute the method
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    w.setWhatsThis("")
                    #QtGui.QWhatsThis.remove(w)
                    try:
                        w.set_expert_mode(False)
                    except:
                        logging.getLogger().exception("Could not set %s to user mode", w.objectName())
            if self.original_style:
                self.setStyleSheet(self.original_style)

    def whats_this_clicked(self):
        """
        Descript. :
        """
        if self.execution_mode:
            BlissWidget.updateWhatsThis()

    def about_clicked(self):
        about_msg_box = QtGui.QMessageBox.about(self, 
             "About MXCuBE",
             """<b>MXCuBE v %s </b> 
                 <p>Macromolecular Xtallography Customized Beamline Environment<p>
                 Python %s - Qt %s - PyQt %s on %s"""%(__version__, 
              platform.python_version(),
              QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))

    def quit_clicked(self):
        """
        Descript. :
        """
        if self.execution_mode:
            QtGui.QApplication.quit()

    def info_for_developers_clicked(self):
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
        path_list = os.path.dirname(__file__).split(os.sep)
        filename = os.path.join(*path_list[:-2]) 
        filename = os.path.join(os.sep, filename, "docs/build/user_manual.html")
        if os.path.exists(filename):
            webbrowser.open(filename)
        else:
            logging.getLogger().error("Could not find html file %s" % filename)

    def set_color(self, color):
        if color:  
            style_string = """QMenuBar {background-color: %s;}""" % color
            style_string += """QMenuBar::item {background: %s;}""" %color
            style_string += """QMenuBar {color: black;}"""
            self.setStyleSheet(style_string)

    def view_toolbar_clicked(self):
        self.viewToolBarSignal.emit(self.view_toolbar_action.isChecked())

    def view_graphics_manager_clicked(self): 
        pass

class CustomToolBar(QtGui.QToolBar):
    """
    Descript. :
    """

    def __init__(self, parent):
        """
        Descript. : parent *must* be the window ; it contains a centralWidget 
                    in its viewport
        """
        QtGui.QToolBar.__init__(self)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.Fixed)

class WindowDisplayWidget(QtGui.QScrollArea):
    """
    Descript. :
    """

    class Spacer(QtGui.QFrame):
        """
        Descript. :
        """

        def __init__(self, *args, **kwargs):
            """
            Descript. :
            """
            QtGui.QFrame.__init__(self, args[0])
            self.setObjectName(args[1])

            self.orientation = kwargs.get("orientation", "horizontal")
            self.execution_mode = kwargs.get("executionMode", False)

            self.setFixedSize(-1)

            if self.orientation == "horizontal":
                self.main_layout = QtGui.QHBoxLayout()
            else:
                self.main_layout = QtGui.QVBoxLayout() 
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(0,0,0,0)
            self.setLayout(self.main_layout)

        def setFixedSize(self, fixed_size):
            """
            Descript. :
            """
            if fixed_size >= 0:
                hor_size_policy = self.orientation == "horizontal" and \
                                  QtGui.QSizePolicy.Fixed or QtGui.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == QtGui.QSizePolicy.Fixed and \
                                  QtGui.QSizePolicy.MinimumExpanding or QtGui.QSizePolicy.Fixed
                
                if self.orientation == "horizontal":
                    self.setFixedWidth(fixed_size)
                else:
                    self.setFixedHeight(fixed_size)
            else:
                hor_size_policy = self.orientation == "horizontal" and \
                                  QtGui.QSizePolicy.Expanding or QtGui.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == QtGui.QSizePolicy.Expanding and \
                                  QtGui.QSizePolicy.MinimumExpanding or QtGui.QSizePolicy.Expanding
            self.setSizePolicy(hor_size_policy, ver_size_policy)
            
        def paintEvent(self, event):
            """
            Descript. :
            """
            QtGui.QFrame.paintEvent(self, event)

            if self.execution_mode:
                return

            p = QtGui.QPainter(self)
            p.setPen(QtGui.QPen(QtCore.Qt.black, 3))

            if self.orientation == 'horizontal':
                h = self.height() / 2
                p.drawLine(0, h, self.width(), h)
                p.drawLine(0, h, 5, h - 5)
                p.drawLine(0, h, 5, h + 5)
                p.drawLine(self.width(), h, self.width() - 5, h - 5)
                p.drawLine(self.width(), h, self.width() - 5, h + 5)
            else:
                w = self.width() / 2
                p.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
                p.drawLine(w, 0, w - 5, 5)
                p.drawLine(w, 0, w + 5, 5)
                p.drawLine(w, self.height(), w - 5, self.height() - 5)
                p.drawLine(w, self.height(), w + 5, self.height() - 5)

    def verticalSpacer(*args, **kwargs):
        """
        Descript. :
        """
        kwargs["orientation"]="vertical"
        return WindowDisplayWidget.Spacer(*args, **kwargs)

    def horizontalSpacer(*args, **kwargs):
        """
        Descript. :
        """
        kwargs["orientation"]="horizontal"
        return WindowDisplayWidget.Spacer(*args, **kwargs)

    def horizontalSplitter(*args, **kwargs):
        """
        Descript. :
        """
        return QtGui.QSplitter(QtCore.Qt.Horizontal, *args)

    def verticalSplitter(*args, **kwargs):
        """
        Descript. :
        """
        return QtGui.QSplitter(QtCore.Qt.Vertical, *args)
    
    def verticalBox(*args, **kwargs):
        """
        Descript. :
        """
        executionMode = kwargs.get('executionMode', False)

        frame = QtGui.QFrame(args[0])
        frame.setObjectName(args[1])
        #frame.setFrameStyle(QtGui.QFrame.Box)
        if not executionMode:
            frame.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        #frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        frame_layout = QtGui.QVBoxLayout(frame) 
        frame_layout.setSpacing(0) 
        frame_layout.setContentsMargins(0,0,0,0)
 
        return frame

    def horizontalBox(*args, **kwargs):
        """
        Descript. :
        """
        executionMode = kwargs.get('executionMode', False)

        frame = QtGui.QFrame(args[0])
        frame.setObjectName(args[1])

        #frame.setFrameStyle(QtGui.QFrame.Box)
        if not executionMode:
            frame.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        #frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        frame_layout = QtGui.QHBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        return frame
       
    def horizontalGroupBox(*args, **kwargs):
        """
        Descript. :
        """
        executionMode = kwargs.get('executionMode', False)
       
        groupbox = QtGui.QGroupBox(args[0])
        groupbox.setObjectName(args[1])      
        groupbox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
 
        group_box_layout = QtGui.QHBoxLayout(groupbox)
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0, 0, 0, 0)

        return groupbox

    def verticalGroupBox(*args, **kwargs):
        """
        Descript. :
        """
        executionMode = kwargs.get('executionMode', False)

        groupbox = QtGui.QGroupBox(args[0])
        groupbox.setObjectName(args[1])
        groupbox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        group_box_layout = QtGui.QVBoxLayout(groupbox)
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0, 0, 0, 0)

        return groupbox        

    class CustomTabWidget(QtGui.QTabWidget):
        """
        Descript. :
        """

        def __init__(self, *args, **kwargs):
            """
            Descript. :
            """

            QtGui.QTabWidget.__init__(self, args[0])
            self.setObjectName(args[1])
            self.close_tab_button = None

            #self.tab_widgets = []
            self.countChanged = {}
            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            self.currentChanged.connect(self._pageChanged)

        def _pageChanged(self, index):
            """
            Descript. :
            """
            page = self.widget(index)
            self.countChanged[index]=False

            tab_label=str(self.tabText(index))
            label_list=tab_label.split()
            found=False
            try:
                count=label_list[-1]
                try:
                    found=count[0]=="("
                except:
                    pass
                else:
                    try:
                        found=count[-1]==")"
                    except:
                        pass
            except:
                pass
            if found:
                orig_label=" ".join(label_list[0:-1])
            else:
                orig_label=" ".join(label_list)
            self.emit(QtCore.SIGNAL("notebookPageChanged"), orig_label)
            QtGui.QApplication.emit(self, QtCore.SIGNAL('tab_changed'), index, page)

            tab_name = self.objectName()
            BlissWidget.updateTabWidget(tab_name,index)


        def hasCountChanged(self,tab_index):
            """
            Descript. :
            """
            try:
                changed=self.countChanged[tab_index]
            except KeyError:
                changed=False
            return changed


        def add_tab(self, page_widget, label, icon = ""):
            """
            Descript. :
            """
            scroll_area = page_widget
            self.addTab(scroll_area, label) 

            slotName = "showPage_%s" % label
            def tab_slot(self, page_index = self.indexOf(scroll_area)):
                self.setCurrentIndex(page_index)
            try:
                self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))
            slotName = "hidePage_%s" % label
            def tab_slot(self, hide=True, page = {"widget" : scroll_area, \
                         "label": self.tabText(self.indexOf(scroll_area)), 
                         "index" : self.indexOf(scroll_area), 
                         "icon": icon, "hidden" : False}):
                if hide:
                  if not page["hidden"]:
                    self.removeTab(self.indexOf(page["widget"]))
                    self.repaint()
                    page["hidden"] = True
                else:
                  if page["hidden"]:
                    if icon:
                      pixmap = Qt4_Icons.load(icon)
                      self.insertTab(page["widget"], QtGui.QIcon(pixmap,pixmap), label, page["index"])
                    else:
                      self.insertTab(page["index"], page["widget"], page["label"])
                    self.showPage(page["widget"])
                    page["hidden"] = False
                  else:
                    self.showPage(page["widget"])
            try:
              self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
            except: 
              logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName())) 
        
            # add 'enable page' slot
            slotName = "enablePage_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.page(page_index).setEnabled(enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # add 'enable tab' slot
            slotName = "enableTab_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.setTabEnabled(page_index, enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # add 'tab reset count' slot
            slotName = "resetTabCount_%s" % label
            def tab_slot(self, erase_count, page_index=self.indexOf(scroll_area)):
                tab_label=str(self.tabLabel(self.page(page_index)))
                label_list=tab_label.split()
                found=False
                try:
                    count=label_list[-1]
                    try:
                        found=count[0]=="("
                    except:
                        pass
                    else:
                        try:
                            found=count[-1]==")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num=int(count[1:-1])
                    except:
                        pass
                    else:
                        new_label=" ".join(label_list[0:-1])
                        if not erase_count:
                            new_label+=" (0)"
                        self.countChanged[page_index]=False
                        self.setTabLabel(self.page(page_index),new_label)
                else:
                    if not erase_count:
                        new_label=" ".join(label_list)
                        new_label+=" (0)"
                        self.countChanged[page_index]=False
                        self.setTabLabel(self.page(page_index),new_label)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'tab increase count' slot
            slotName = "incTabCount_%s" % label
            def tab_slot(self, delta, only_if_hidden, page_index=self.indexOf(scroll_area)):
                if only_if_hidden and page_index==self.currentPageIndex():
                    return
                tab_label=str(self.tabLabel(self.page(page_index)))
                label_list=tab_label.split()
                found=False
                try:
                    count=label_list[-1]
                    try:
                        found=count[0]=="("
                    except:
                        pass
                    else:
                        try:
                            found=count[-1]==")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num=int(count[1:-1])
                    except:
                        pass
                    else:
                        new_label=" ".join(label_list[0:-1])
                        new_label+=" (%d)" % (num+delta)
                        self.countChanged[page_index]=True
                        self.setTabLabel(self.page(page_index),new_label)
                else:
                    new_label=" ".join(label_list)
                    new_label+=" (%d)" % delta
                    self.countChanged[page_index]=True
                    self.setTabLabel(self.page(page_index),new_label)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # that's the real page
            return scroll_area


    class label(QtGui.QLabel):
        """
        Descript. :
        """

        def __init__(self, *args, **kwargs):
            """
            Descript. :
            """
            QtGui.QLabel.__init__(self, args[0])
            self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
 
    items = { "vbox": verticalBox,
              "hbox": horizontalBox,
              "vgroupbox": verticalGroupBox,
              "hgroupbox": horizontalGroupBox,
              "vspacer": verticalSpacer,
              "hspacer": horizontalSpacer,
              "icon": label,
              "label": label,
              "tab": CustomTabWidget,
              "hsplitter": horizontalSplitter,
              "vsplitter": verticalSplitter }


    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QScrollArea.__init__(self, args[0])

        self.additionalWindows = {}
        self.__putBackColors = None
        self.execution_mode=kwargs.get('executionMode', False)
        self.preview_items = []
        self.currentWindow = None
        self.setWindowTitle("GUI preview")
 
        self.central_widget = QtGui.QWidget(self.widget())
        #self.central_widget.setObjectName("deee")
        self.central_widget_layout = QtGui.QVBoxLayout() 
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget.show()

        self.toolbar = CustomToolBar(self)
        self.toolbar.hide()
        self.menubar = CustomMenuBar(self)
        self.menubar.hide()
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.hide()

        _main_vlayout = QtGui.QVBoxLayout()
        _main_vlayout.addWidget(self.menubar)
        _main_vlayout.addWidget(self.toolbar)
        _main_vlayout.addWidget(self.central_widget)
        _main_vlayout.addWidget(self.statusbar) 
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_main_vlayout)

        self.menubar.viewToolBarSignal.connect(self.view_toolbar_toggled)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(Qt4_Icons.load_icon("desktop_icon")) 

    def view_toolbar_toggled(self, state):
        if state:
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def set_menu_bar(self, menu_data, exp_pwd, execution_mode):
        """
        Descript. :
        """
        self.menubar.configure(menu_data, exp_pwd, execution_mode)
        self.menubar.show()
        BlissWidget._menuBar = self.menubar
        BlissWidget._toolBar = self.toolbar

    def set_status_bar(self):
        """
        Descript. :
        """
        self.statusbar.show()	

    def show(self, *args):
        """
        Descript. :
        """
        ret = QtGui.QWidget.show(self)
        self.emit(QtCore.SIGNAL("isShown"), ())
        return ret

    def hide(self, *args):
        """
        Descript. :
        """
        ret = QtGui.QWidget.hide(self)
        self.emit(QtCore.SIGNAL("isHidden"), ())
        return ret
    
    def setCaption(self, *args):
        """
        Descript. :
        """
        ret = QtGui.QWidget.setWindowTitle(self, *args)
        return ret

    def exitExpertMode(self, *args):
        """
        Descript. :
        """
        if len(args) > 0:
            if args[0]:
                return
        self.menubar.set_exp_mode(False)

    def add_item(self, item_cfg, parent):
        """
        Descript. :
        """
        item_type = item_cfg["type"]
        item_name = item_cfg["name"]
        newItem = None

        try:
            klass = WindowDisplayWidget.items[item_type]
        except KeyError:
            newItem = item_cfg["brick"]
        else:
            newItem = klass(parent, item_cfg["name"], executionMode=self.execution_mode)
            if item_type in ("vbox", "hbox", "vgroupbox", "hgroupbox"):
                if item_cfg["properties"]["color"] is not None:
                    try:
                        qtcolor = QtGui.QColor(item_cfg["properties"]["color"])
                        newItem_palette = newItem.palette()
                        newItem_palette.setColor(QtGui.QPalette.Background, 
                                                 QtGui.QColor(qtcolor.red(),
                                                 qtcolor.green(),
                                                 qtcolor.blue())) 
                        newItem.setPalette(newItem_palette)
                    except:
                        logging.getLogger().exception("Could not set color on item %s", item_cfg["name"])

                if item_type.endswith("groupbox"):
                    newItem.setTitle(item_cfg["properties"]["label"])
            
                newItem.layout().setSpacing(item_cfg["properties"]["spacing"])
                newItem.layout().setMargin(item_cfg["properties"]["margin"])
                frame_style = QtGui.QFrame.NoFrame
                if item_cfg["properties"]["frameshape"]!="default":
                    frame_style = getattr(QtGui.QFrame, item_cfg["properties"]["frameshape"])
                if item_cfg["properties"]["shadowstyle"]!="default":
                    frame_style = frame_style | getattr(QtGui.QFrame, item_cfg["properties"]["shadowstyle"].capitalize())
                if frame_style != QtGui.QFrame.NoFrame:
                    try:
                        newItem.setFrameStyle(frame_style)
                    except:
                        logging.getLogger().exception("Could not set frame style on item %s", item_cfg["name"])
                if item_cfg["properties"]["fixedwidth"] > -1: 
                    newItem.setFixedWidth(item_cfg["properties"]["fixedwidth"])
                if item_cfg["properties"]["fixedheight"] > -1: 
                    newItem.setFixedHeight(item_cfg["properties"]["fixedheight"])
            elif item_type == "icon":
                img = QtGui.QPixmap()
                if img.load(item_cfg["properties"]["filename"]):
                    newItem.setPixmap(img)
            elif item_type == "label":
                newItem.setText(item_cfg["properties"]["text"])
            elif item_type == "tab":
                item_cfg.widget = newItem
                newItem.close_tab_button = QtGui.QToolButton(newItem)
                newItem.close_tab_button.setIcon(QtGui.QIcon(Qt4_Icons.load('delete_small')))
                newItem.setCornerWidget(newItem.close_tab_button)
                newItem.close_tab_button.hide()
                def close_current_page():
                  tab=newItem
                  slot_name = "hidePage_%s" % str(tab.tabText(tab.currentIndex()))
                  slot_name = slot_name.replace(" ", "_")
                  getattr(tab, slot_name)()
                  #QtGui.QApplication.emit(QtCore.SIGNAL('tab_closed'), tab, slotName)
                def current_page_changed(index):
                  item_cfg.notebookPageChanged(newItem.tabText(index))
 
                newItem._close_current_page_cb = close_current_page
                newItem.currentChanged.connect(current_page_changed)
                newItem.close_tab_button.clicked.connect(close_current_page)
            elif item_type == "vsplitter" or type == "hsplitter":
                pass
                
            newItem.show()
                                                                             
        return newItem
 
    def make_item(self, item_cfg, parent):
        """
        Descript. :
        """
        previewItemsList = []
        if isinstance(item_cfg, ContainerCfg):
            self.containerNum += 1
        for child in item_cfg["children"]:
            try:
                new_item = self.add_item(child, parent)
            except:
                logging.getLogger().exception("Cannot add item %s", child["name"])
            else:
                if not self.execution_mode:
                    new_item.installEventFilter(self)
            if parent.__class__ == WindowDisplayWidget.items["tab"]:
                newTab = parent.add_tab(new_item, child["properties"]["label"], 
                                        child["properties"]["icon"])
                newTab.item_cfg = child
                self.preview_items.append(new_item)
            else:
                if isinstance(child, ContainerCfg):
                    new_item.setSizePolicy(self.getSizePolicy(child["properties"]["hsizepolicy"], 
                                                              child["properties"]["vsizepolicy"]))                 
                if not isinstance(child, BrickCfg):
                    if child["properties"].hasProperty("fontSize"):
                        f = new_item.font()
                        if child["properties"]["fontSize"] <= 0:
                            child["properties"].getProperty("fontSize").setValue(f.pointSize())
                        else:
                            f.setPointSize(int(child["properties"]["fontSize"]))
                            new_item.setFont(f)

                if hasattr(parent, "_preferred_layout"):
                    layout = parent._preferred_layout
                else:
                    layout = parent.layout()

                if layout is not None:
                    # layout can be none if parent is a Splitter for example
                    if not isinstance(child, BrickCfg):
                        alignment_flags = self.getAlignmentFlags(child["properties"]["alignment"])
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
                        layout.addWidget(new_item, stretch, QtCore.Qt.Alignment(alignment_flags))
                    else:
                        layout.addWidget(new_item, stretch)
           
            self.make_item(child, new_item)


    def drawPreview(self, container_cfg, window_id, container_ids = [], selected_item=""):
        """
        Descript. :
        """
        for (w, m) in self.additionalWindows.itervalues():
            w.close()
        # reset colors
        if callable(self.__putBackColors):
            self.__putBackColors()
            self.__putBackColors = None

        if self.currentWindow is not None and self.currentWindow != window_id:
            # remove all bricks and destroy all other items
            #previewItems = self.preview_items[self.currentWindow]
            #self.preview_items = []
            self.central_widget.close()
            self.central_widget = QtGui.QWidget(self.viewport())
            self.central_widget_layout = QtGui.QVBoxLayout()
            self.central_widget.setLayout(self.central_widget_layout)
            self.central_widget.show()

        self.currentWindow = window_id
        self.containerNum = -1
        
        try:
            parent = previewItems[container_ids[0]][0]
        except:
            parent = self.central_widget
        else:
            pass

        #self.preview_items.append(self.central_widget)
        
        # reparent bricks to prevent them from being deleted,
        # and remove them from the previewItems list 
        self.setObjectName(container_cfg["name"])
        self.preview_items.append(self)

        if isinstance(container_cfg, WindowCfg):
            previewItems = {}
            self.setObjectName(container_cfg["name"])
            # update menubar ?
            if container_cfg.properties["menubar"]:

                self.set_menu_bar(container_cfg.properties["menudata"],
                                  container_cfg.properties["expertPwd"],
                                  self.execution_mode)  

                """if not window_id in self.additionalWindows:
                    menubar = MenuBar(self, container_cfg.properties["menudata"],\
                                      container_cfg.properties["expertPwd"],\
                                      executionMode = self.execution_mode)
                    BlissWidget._menuBar = menubar
                    self.additionalWindows[window_id] = (container_cfg.menuEditor(), menubar)"""

            else:
                try:
                    self.additionalWindows[window_id][1].hide()
                except:
                    pass
        else:
            try:
                del previewItems[container_ids[0]][1:]
            except KeyError:
                # preview items does not exist, no need to delete it
                pass

        self.make_item(container_cfg, parent)

        if isinstance(container_cfg, WindowCfg):
            if container_cfg.properties["statusbar"]:
                self.set_status_bar()

    def remove_widget(self, item_name, child_name_list):
        """
        Descript. :
        """
        remove_item_list = child_name_list
        remove_item_list.append(item_name)
        for name in remove_item_list:
            for item_widget in self.preview_items:
                if item_widget.objectName() == name:
                    self.preview_items.remove(item_widget) 
                    #item_widget.setParent(None)
                    item_widget.deleteLater()

    def add_widget(self, child, parent):
        """
        Descript. :
        """
        if parent is None:
            self.drawPreview(child, 0, [])
        else:
            for item in self.preview_items:
                if item.objectName() == parent.name:
                    parent_item = item
            newItem = self.add_item(child, parent_item)
            if isinstance(parent, TabCfg):
                newTab = parent_item.add_tab(newItem, child["properties"]["label"], child["properties"]["icon"])
                newTab.item_cfg = child
            else:   
                parent_item.layout().addWidget(newItem)
            self.preview_items.append(newItem)

    def move_widget(self, item_name, direction):
        """
        Descript. : moves widget in the parent layout up or down
        """ 
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

            if (new_index <> current_index and \
                new_index > -1 and \
                new_index < parent_layout.count()):
                parent_layout.removeWidget(item)
                parent_layout.insertWidget(new_index, item)            

    def updatePreview(self, container_cfg, window_id, container_ids = [], selected_item=""):
        """
        Descript. : function to select widget in the gui
        """
        if callable(self.__putBackColors):
            self.__putBackColors()
            self.__putBackColors = None
        if (len(selected_item) and 
            len(self.preview_items) > 0):
            for item in self.preview_items:
                if item.objectName() == selected_item:
                    self.selectWidget(item)
                    return

    def selectWidget(self, widget):
        """
        Descript. :
        Arguments : widget - widget which 
        Return    : None
        """
        if callable(self.__putBackColors):
            self.__putBackColors()
        widget_palette = widget.palette()
        orig_bkgd_color = widget_palette.color(QtGui.QPalette.Window)
        r = orig_bkgd_color.red()
        g = orig_bkgd_color.green()
        b = orig_bkgd_color.blue()
        bkgd_color = widget_palette.color(QtGui.QPalette.Window)
        bkgd_color2 = QtGui.QColor()
        bkgd_color2.setRgb(150,150,200)
        widget_palette.setColor(QtGui.QPalette.Background, bkgd_color2)         
        widget.setAutoFillBackground(True)
        widget.setPalette(widget_palette)

        def putBackColors(wref=weakref.ref(widget), bkgd_color=(r,g,b)):
            widget = wref()
            if widget is not None:
                widget.setAutoFillBackground(False)
                widget_palette = widget.palette()
                widget_palette.setColor(QtGui.QPalette.Background, QtGui.QColor(*bkgd_color))
                widget.setPalette(widget_palette)
        self.__putBackColors = putBackColors

    def eventFilter(self, widget, event):
        """
        Descript. :
        """
        if widget is not None and event is not None:
            if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                self.emit(QtCore.SIGNAL("itemClicked"), widget.objectName())
                return True
        
        return QtGui.QScrollArea.eventFilter(self, widget, event)

    def getAlignmentFlags(self, alignment_directives_string):
        """
        Descript. :
        """
        if alignment_directives_string is None:
            alignment_directives = ['none']
        else:
            alignment_directives =  alignment_directives_string.split()
        alignment_flags = 0

        if "none" in alignment_directives:
            return alignment_flags

        if "hcenter" in alignment_directives:
            return QtCore.Qt.AlignHCenter

        if "vcenter" in alignment_directives:
            return QtCore.Qt.AlignVCenter
        
        if "top" in alignment_directives:
            alignment_flags = QtCore.Qt.AlignTop
        if "bottom" in alignment_directives:
            alignment_flags = QtCore.Qt.AlignBottom
        if "center" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtCore.Qt.AlignCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignHCenter
        if "left" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignLeft
        if "right" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignRight
        return alignment_flags

    def getSizePolicy(self, hsizepolicy, vsizepolicy):
        """
        Descript. :
        """
        def _getSizePolicyFlag(policy_flag):
            if policy_flag == "expanding":
                return QtGui.QSizePolicy.Expanding
            elif policy_flag == "fixed":
                return QtGui.QSizePolicy.Fixed
            else:
                # default
                return QtGui.QSizePolicy.Preferred

        return QtGui.QSizePolicy(_getSizePolicyFlag(hsizepolicy), _getSizePolicyFlag(vsizepolicy))


def display(configuration, noBorder=False):
    """
    Descript. :
    """
    windows = []
    for window in configuration.windows_list:
        display = WindowDisplayWidget(None, window["name"], executionMode=True, noBorder=noBorder)
        windows.append(display)
        display.setCaption(window["properties"]["caption"])
        display.drawPreview(window, id(display))
        if window["properties"]["show"]:
            display._show=True
        else:
            display._show=False
        display.hide()
        restoreSizes(configuration, window, display)
    return windows

def restoreSizes(configuration, window, display, configurationSuffix="",moveWindowFlag = True):
    """
    Descript. :
    """
    splitters = configuration.findAllChildrenWType("splitter", window)
    
    if len(splitters):
        for sw in display.queryList("QSplitter"):
            try:
                splitter = splitters[sw.name()]
                sw.setSizes(eval(splitter["properties"]["sizes%s" % configurationSuffix]))
            except KeyError:
                continue

    if(window["properties"]["x%s" % configurationSuffix] + 
       window["properties"]["y%s" % configurationSuffix] +
       window["properties"]["w%s" % configurationSuffix] +
       window["properties"]["h%s" % configurationSuffix] > 0):
        if moveWindowFlag: display.move(window["properties"]["x%s" % configurationSuffix], 
                                        window["properties"]["y%s" % configurationSuffix])
        display.resize(QtCore.QSize(window["properties"]["w%s" % configurationSuffix], 
                                    window["properties"]["h%s" % configurationSuffix]))
    
   
