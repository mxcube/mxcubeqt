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
import re
import sys
import imp
import types
import weakref
import logging
import subprocess

from PyQt4 import QtCore
from PyQt4 import QtGui

import BlissFramework
from BlissFramework import Qt4_Configuration
from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_PropertyEditor
from BlissFramework.Utils import Qt4_ConnectionEditor
from BlissFramework.Bricks import Qt4_LogViewBrick
from BlissFramework.Qt4_BaseLayoutItems import ContainerCfg
from BlissFramework.Utils import Qt4_GUIDisplay

try:
    from HardwareRepository import HardwareRepository
except ImportError:
    logging.getLogger().warning("no Hardware Repository client module could be found")
#else:
#    from HardwareRepository import HardwareRepositoryBrowser   
 

class HorizontalSpacer(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, *args)
        
        h_size = kwargs.get("size", None)
    
        if h_size is not None:
            self.setFixedWidth(h_size)
            self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        else:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)


class MyListView(QtGui.QListWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        QtGui.QListView.__init__(self, *args)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def addToolTip(self, item, text):
        """
        Descript. :
        """
        self.setToolTip(text)


class GUITreeWidget(QtGui.QTreeWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        QtGui.QTreeWidget.__init__(self, *args)

        self._presspos = None
        self._mousePressed = False

        self.setColumnCount(2)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.setHeaderLabels(["Element", "Type"])
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setItemsExpandable(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 

        self.drag_source_item = None
        self.drag_target_item = None

    def dragEnterEvent(self, event):
        """
        Descript. :
        """
        self.drag_source_item = self.itemAt(event.pos())
        event.accept() 

    def dropEvent(self, event):
        """
        Descript. :
        """
        self.drag_target_item = self.itemAt(event.pos())
        if self.drag_source_item and self.drag_target_item:
            self.emit(QtCore.SIGNAL("dragdrop"), self.drag_source_item, self.drag_target_item)
        event.accept()

            
class ToolboxWindow(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, *args)
       
        # Internal variables --------------------------------------------------
        self.bricks_tab_dict = {}
        self.bricks_dict = {}
      
        # Graphic elements ----------------------------------------------------
        _top_frame = QtGui.QFrame(self)
        _refresh_toolbutton = QtGui.QToolButton(_top_frame)
        _refresh_toolbutton.setIcon(QtGui.QIcon(Qt4_Icons.load("reload")))
        self.setToolTip("refresh bricks list")  
        self._bricks_toolbox = QtGui.QToolBox(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout()
        _main_vlayout.addWidget(QtGui.QLabel("Available bricks", _top_frame))
        _main_vlayout.addWidget(_refresh_toolbutton)
        _main_vlayout.addWidget(self._bricks_toolbox) 
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0,0,0,0) 
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------
        
        # Qt signal/slot connections ------------------------------------------
        _refresh_toolbutton.clicked.connect(self.refresh_clicked) 

        # Other ---------------------------------------------------------------
        self.setWindowTitle("Toolbox") 
        
    def addBrickTab(self, name):
        """
        Descript. : Add a new brick tab called 'name'
        """
        newBricksList = MyListView(self._bricks_toolbox)
        newBricksList.itemDoubleClicked.connect(self.brick_selected)
        self._bricks_toolbox.addItem(newBricksList, name)
        self.bricks_tab_dict[name] = newBricksList
        return newBricksList
        
    def refresh_clicked(self):
        """
        Descript. : Refresh bricks window
        """
        while self._bricks_toolbox.currentWidget():
            self._bricks_toolbox.removeItem(self._bricks_toolbox.currentIndex())
       
        self.bricks_dict = {}
        self.bricks_tab_dict = {}
        map(self.addBricks, (BlissFramework.getStdBricksPath(), ) + \
             tuple(BlissFramework.getCustomBricksDirs()))

    def brickTextLabel(self, brickName):
        """
        Descript. :
        """
        if brickName.endswith("Brick"):
            brickTextLabel = brickName[:-5]
        else:
            brickTextLabel = brickName

        for i in range(len(brickTextLabel)):
            if brickTextLabel[i].isalpha() or brickTextLabel[i].isdigit():
                if i > 0 and brickTextLabel[i].isupper() and brickTextLabel[i-1].islower():
                    brickTextLabel = brickTextLabel[0:i] + " " + brickTextLabel[i].lower() + brickTextLabel[i+1:]
            else:
                brickTextLabel=brickTextLabel[0:i]+" "+brickTextLabel[i+1:]
  
        return brickTextLabel
        

    def addBricks(self, brickDir):
        """
        Descript. : Add the bricks found in the 'brickDir' directory to the 
                    bricks tab widget"""
        findCategoryRE = re.compile("^__category__\s*=\s*['\"](.*)['\"]$", re.M)
        findDocstringRE = re.compile('^"""(.*?)"""?$', re.M | re.S)
        
        full_filenames = []
        for fileordir in os.listdir(brickDir) :
            full_path = os.path.join(brickDir,fileordir)
            if os.path.isdir(full_path) :
                path_with_trunk = os.path.join(full_path,'trunk') # SVN structure
                if os.path.isdir(path_with_trunk) :
                    full_path = path_with_trunk
                filesNames = [os.path.join(full_path,filename) for filename in os.listdir(full_path)]
                full_filenames.extend(filesNames)
            else:
                full_filenames.append(full_path)
                
        full_filenames.sort()
        
        processedBricks = []
        bricksCategories = {}

        for full_filename in full_filenames:
            filename = os.path.basename(full_filename)
            
            if filter(lambda x: filename.endswith(x), [x[0] for x in imp.get_suffixes()]):
                brickName = filename[:filename.rfind('.')]
                if (not brickName == '__init__' and 
                    brickName.startswith('Qt4') and
                    not brickName in processedBricks):
                    processedBricks.append(brickName)
                    dirname = os.path.dirname(full_filename)
                    brick_module_file = None

                    try:
                        brick_module_file, path, description = imp.find_module(brickName, [dirname])
                    except:
                        if brick_module_file:
                            brick_module_file.close()
                        continue

                    moduleContents = brick_module_file.read()

                    checkIfItsBrick = re.compile('^\s*class\s+%s.+?:\s*$' % brickName,re.M)
                    if not checkIfItsBrick.search(moduleContents) : continue

                    match = findCategoryRE.search(moduleContents)
                    if match is None:
                        category = ""
                    else:
                        category = match.group(1)

                    match = findDocstringRE.search(moduleContents)
                    if match is None:
                        description = ""
                    else:
                        description = match.group(1)


                    try:
                        bricksCategories[category].append( (brickName, dirname, description) )
                    except KeyError:
                        bricksCategories[category] = [ (brickName, dirname, description) ]

        if len(bricksCategories) == 0:
            return

        categoryKeys = bricksCategories.keys()
        categoryKeys.sort()

        for category in categoryKeys:
            bricksList = bricksCategories[category]

            try:
                bricksListWidget = self.bricks_tab_dict[category]
            except KeyError:
                bricksListWidget = self.addBrickTab(category)
            
            for brickName, dirname, description in bricksList:
                newBrick = QtGui.QListWidgetItem(QtCore.QString(self.brickTextLabel(brickName)), bricksListWidget)
                bricksListWidget.addToolTip(newBrick, description)
                self.bricks_dict[id(newBrick)] = (dirname, brickName)

    def brick_selected(self, item):
        """
        Descript. :
        """
        dir_name, brick_name = self.bricks_dict[id(item)]
        self.emit(QtCore.SIGNAL("addBrick"), brick_name)
        

class Qt4_PropertyEditorWindow(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, *args)
 
        self.setWindowTitle("Properties")

        self.properties_table = Qt4_PropertyEditor.Qt4_ConfigurationTable(self)
        self.__property_changed_cb = weakref.WeakKeyDictionary()

        QtCore.QObject.connect(self.properties_table, QtCore.SIGNAL("propertyChanged"), self.property_changed)

        _main_vlayout = QtGui.QHBoxLayout()
        _main_vlayout.addWidget(self.properties_table)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0,0,0,0)
        self.setLayout(_main_vlayout)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def editProperties(self, property_bag):
        """
        Descript. :
        """
        self.properties_table.setPropertyBag(property_bag)

    def property_changed(self, *args):
        """
        Descript. :
        """
        try:
            cb = self.__property_changed_cb[self.properties_table.propertyBag]
        except KeyError, err:
            return
        else:
            cb(*args)
            
    def addProperties(self, propertyBag, property_changed_cb):
        """
        Descript. :
        """
        self.__property_changed_cb[propertyBag] = property_changed_cb
        self.editProperties(propertyBag)
    

class ToolButton(QtGui.QToolButton):
    """
    Descript. :
    """

    def __init__(self, parent, icon, text = None, callback = None, tooltip = None):
        """
        Descript. :
        """
        QtGui.QToolButton.__init__(self, parent)

        self.setIcon(QtGui.QIcon(Qt4_Icons.load(icon)))

        if type(text) != types.StringType:
            tooltip = callback
            callback = text
        else:
            self.setTextLabel(text)
            self.setTextPosition(qt.QToolButton.BesideIcon)
            self.setUsesTextLabel(True)

        if callback is not None:
            self.clicked.connect(callback)

        if tooltip is not None:
            self.setToolTip(tooltip) 
            #QtGui.QToolTip.add(self, tooltip)

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)


class GUIEditorWindow(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """

        QtGui.QWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.configuration = Qt4_Configuration.Configuration()

        # Graphic elements ----------------------------------------------------
        _tools_widget = QtGui.QWidget(self)
        _add_window_toolbutton = ToolButton(_tools_widget, "window_new", \
             self.add_window_clicked, "add a new window (container)")
        _add_tab_toolbutton = ToolButton(_tools_widget, "tab", \
             self.add_tab_clicked, "add a new tab (container)")
        _add_hbox_toolbutton = ToolButton(_tools_widget, "add_hbox", \
             self.add_hbox_clicked, "add a new horizontal box (container)")
        _add_vbox_toolbutton = ToolButton(_tools_widget, "add_vbox", \
             self.add_vbox_clicked, "add a new vertical box (container)")
        _add_hgroupbox_toolbutton = ToolButton(_tools_widget, "hgroupbox", \
             self.add_hgroupbox_clicked, "add a new horizontal group box (container)")
        _add_vgroupbox_toolbutton = ToolButton(_tools_widget, "vgroupbox", \
             self.add_vgroupbox_clicked, "add a new vertical group box (container)")
        _add_hspacer_toolbutton = ToolButton(_tools_widget, "add_hspacer", \
             self.add_hspacer_clicked, "add a new horizontal spacer")
        _add_vspacer_toolbutton = ToolButton(_tools_widget, "add_vspacer", \
             self.add_vspacer_clicked, "add a new vertical spacer")
        _add_hsplitter_toolbutton = ToolButton(_tools_widget, "hsplitter", \
             self.add_hsplitter_clicked, "add a new horizontal splitter (container)")
        _add_vsplitter_toolbutton = ToolButton(_tools_widget, "vsplitter", \
             self.add_vsplitter_clicked, "add a new vertical splitter (container)")
        _add_icon_toolbutton = ToolButton(_tools_widget, "icon", \
             self.add_icon_clicked, "add a new icon")
        _add_label_toolbutton = ToolButton(_tools_widget, "label", \
             self.add_label_clicked, "add a new label")

        _tree_handling_widget = QtGui.QWidget(self)
        _show_connections_toolbutton = ToolButton(_tree_handling_widget, "connect_creating", \
              self.show_connections_clicked, "manage connections between items")
        _move_up_toolbutton = ToolButton(_tree_handling_widget, "Up2", \
              self.move_up_clicked, "move an item up")
        _move_down_toolbutton = ToolButton(_tree_handling_widget, "Down2", \
              self.move_down_clicked, "move an item down")
        _remove_item_toolbutton = ToolButton(_tree_handling_widget, "delete_small", \
                self.remove_item_clicked, "delete an item")

        self.tree_widget = GUITreeWidget(self)
        self.root_element = QtGui.QTreeWidgetItem(self.tree_widget)
        self.root_element.setText(0, QtCore.QString("GUI tree"))
        self.root_element.setExpanded(True)

        # Layout --------------------------------------------------------------
        _toolbox_hlayout = QtGui.QHBoxLayout()
        _toolbox_hlayout.addWidget(_add_window_toolbutton)
        _toolbox_hlayout.addWidget(_add_tab_toolbutton)
        _toolbox_hlayout.addWidget(_add_hbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_vbox_toolbutton)        
        _toolbox_hlayout.addWidget(_add_hgroupbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_vgroupbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_hspacer_toolbutton)
        _toolbox_hlayout.addWidget(_add_vspacer_toolbutton)
        _toolbox_hlayout.addWidget(_add_hsplitter_toolbutton)
        _toolbox_hlayout.addWidget(_add_vsplitter_toolbutton)
        _toolbox_hlayout.addWidget(_add_icon_toolbutton)
        _toolbox_hlayout.addWidget(_add_label_toolbutton)
        _toolbox_hlayout.addStretch(0)
        _toolbox_hlayout.setSpacing(2)
        _toolbox_hlayout.setContentsMargins(2, 2, 2, 2)
        _tools_widget.setLayout(_toolbox_hlayout)

        _tree_handling_widget_hlayout = QtGui.QHBoxLayout()
        _tree_handling_widget_hlayout.addWidget(_show_connections_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_move_up_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_move_down_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_remove_item_toolbutton)
        _tree_handling_widget_hlayout.addStretch(0)
        _tree_handling_widget_hlayout.setSpacing(2)
        _tree_handling_widget_hlayout.setContentsMargins(2, 2, 2, 2)
        _tree_handling_widget.setLayout(_tree_handling_widget_hlayout)
       
        _main_vlayout = QtGui.QVBoxLayout()  
        _main_vlayout.addWidget(_tools_widget)
        _main_vlayout.addWidget(_tree_handling_widget)
        _main_vlayout.addWidget(self.tree_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2,2,2,2)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------
        _tools_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------
        self.tree_widget.itemSelectionChanged.connect(self.item_selected)
        self.tree_widget.itemDoubleClicked.connect(self.item_double_clicked)
        self.tree_widget.itemChanged.connect(self.item_changed)
        self.connect(self.tree_widget, QtCore.SIGNAL('dragdrop'), 
                     self.item_drag_dropped)
        self.connect(self.tree_widget, QtCore.SIGNAL('contextMenuRequested'), 
                     self.item_right_clicked)

        # Other --------------------------------------------------------------- 
        self.item_rename_started = None
        self.setWindowTitle("GUI Editor")

    def create_action(self, text, slot = None, shortcut = None, icon = None, 
                      tip = None, checkable = False, signal = "triggered()"):
        """
        Descript. :
        """
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(Qt4_Icons.load(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        """
        Descript. :
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def set_configuration(self, configuration):
        """
        Descript. :
        """
        self.configuration = configuration
        self.tree_widget.blockSignals(True)
        self.emit(QtCore.SIGNAL('hidePropertyEditorWindow'), ())

        def addChildren(children, parentItem):
            parent_name = str(parentItem.text(0))
            parent = self.configuration.findContainer(parent_name)
            
            for child in children:
                if self.configuration.isContainer(child):
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon=child["type"])
                    addChildren(child["children"], new_list_item)
                    self.configuration.items[child["name"]].updateSlots()
                elif self.configuration.isSpacer(child):
                    new_list_item = self.appendItem(parentItem, child["name"], "spacer", icon=child["type"])
                elif self.configuration.isBrick(child):
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon="brick")
                else:
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon=child["type"])
                self.connectItem(parent, child, new_list_item)

        for window in self.configuration.windows_list:
            parentWindowItem = self.appendItem(self.root_element, window.name, "window", icon="window_small")
            self.connectItem(None, window, parentWindowItem)
            
            addChildren(window["children"], parentWindowItem)

        self.tree_widget.blockSignals(False)
        #self.tree_widget.triggerUpdate()
        self.tree_widget.update()        

        self.tree_widget.setCurrentItem(self.root_element.child(0))
        self.emit(QtCore.SIGNAL('showProperyEditorWindow'), ())

    def show_connections_clicked(self):
        """
        Descript. :
        """
        self.connection_editor_window = Qt4_ConnectionEditor.Qt4_ConnectionEditor(self.configuration)
        width = QtGui.QApplication.desktop().width()
        height = QtGui.QApplication.desktop().height()
        #self.connection_editor_window.resize(0.85 * width, 0.7 * height)
        self.connection_editor_window.show()

    def updateProperties(self, item_cfg):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("editProperties"), item_cfg["properties"])
        
    def _getParentWindowName(self, item): 
        """
        Descript. :
        """
        while item:
            if str(item.text(1)) == "window":
                return str(item.text(0))
            else:
                item = item.parent()
    
    def appendItem(self, parentItem, column1_text, column2_text, icon = None):
        """
        Descript. :
        """
        newListItem = QtGui.QTreeWidgetItem(parentItem)  
        newListItem.setText(0, QtCore.QString(str(column1_text)))
        newListItem.setText(1, QtCore.QString(str(column2_text))) 
        newListItem.setExpanded(True)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
 
        if isinstance(icon, str):
            newListItem.setIcon(0, QtGui.QIcon(Qt4_Icons.load(icon)))
        self.tree_widget.setCurrentItem(newListItem)
        self.tree_widget.scrollToItem(newListItem, QtGui.QAbstractItemView.EnsureVisible)

        return newListItem
        
    def remove_item_clicked(self):
        """
        Descript. :
        """
        currentItem = self.tree_widget.currentItem()
        if currentItem:
            item_parent_name = str(currentItem.parent().text(0))
            item_name = str(currentItem.text(0))
            children = currentItem.childCount()
            if children > 0:
                if QtGui.QMessageBox.warning(self, "Please confirm",
                                          "Are you sure you want to remove %s ?\nRemoving item will remove its %d children." % (item_name, children),
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    return

            item_cfg = self.configuration.findItem(item_name)

            children_name_list = []
            for child in item_cfg['children']:  
                 children_name_list.append(child['name'])

            self.emit(QtCore.SIGNAL("removeWidget"), item_name, children_name_list)

            if self.configuration.remove(item_name):
                root = self.tree_widget.invisibleRootItem()
                for item in self.tree_widget.selectedItems():
                    (item.parent() or root).removeChild(item)               
            
    def draw_window_preview(self):
        """
        Descript. :
        """
        container_name = self.root_element.child(0).text(0)
        container_cfg, window_id, container_ids, selected_item = \
             self.prepare_window_preview(container_name, None, "")
        self.emit(QtCore.SIGNAL("drawPreview"), container_cfg, window_id, container_ids, selected_item)

    def update_window_preview(self, container_name, container_cfg = None, selected_item = ""): 
        """
        Descript. :
        """
        upd_container_cfg, upd_window_id, upd_container_ids, upd_selected_item = \
             self.prepare_window_preview(container_name, container_cfg, selected_item)
        self.emit(QtCore.SIGNAL("updatePreview"), upd_container_cfg, upd_window_id, upd_container_ids, selected_item)

    def prepare_window_preview(self, item_name, item_cfg = None, selected_item = ""):
        """
        Descript. :
        """
        item_list = self.tree_widget.findItems(QtCore.QString(item_name), QtCore.Qt.MatchRecursive, 0)
        item = item_list[0]
        item_type = str(item.text(1))

        window_id = None
        if item_type == "window":
            window_id = str(item.text(0))
        else:
            # find parent window
            parent = item.parent()
            while (parent):
                if str(parent.text(1)) == "window":
                    window_id = str(parent.text(0))
                    break
                parent = parent.parent()
         
        if item_type != "window" and item.childCount() == 0:
            item = item.parent()
            item_name = str(item.text(0))
            item_cfg = None

        if item_cfg is None:
            item_cfg = self.configuration.findItem(item_name)
      
        item_ids = [] 
        current_item = self.root_element
        while self.tree_widget.itemBelow(current_item):
               current_item = self.tree_widget.itemBelow(current_item)
               item_ids.append(str(current_item.text(0)))
                
        return item_cfg, window_id, item_ids, selected_item

    def connectItem(self, parent, new_item, new_list_item):
        """
        Descript. :
        """
        if self.configuration.isBrick(new_item):
            self.emit(QtCore.SIGNAL("newItem"), new_item["brick"].propertyBag, new_item["brick"]._propertyChanged)
        else:
            if parent is not None:
                parentref = weakref.ref(parent)
            else:
                parentref=None
            
            def property_changed_cb(property, old_value, new_value, itemref=weakref.ref(new_list_item), parentref=parentref):
                item = itemref()
                if item is None:
                    return

                item_name = str(item.text(0))
                item_type = str(item.text(1))
                
                try:
                    klass = Qt4_Configuration.Configuration.classes[item_type]
                except KeyError:
                    self.update_window_preview(item_name)
                else:
                    if issubclass(klass, ContainerCfg):
                        # we should update the container itself,
                        # not just its contents so we trigger an
                        # update of the parent instead
                        if parentref is not None:
                            parent = parentref()
                            if parent is not None:
                                self.update_window_preview(parent["name"], parent)
                    else:
                        self.update_window_preview(item_name)

                if parentref is not None:
                    parent = parentref()
                    if parent is None:
                        return        
                    parent.childPropertyChanged(item_name, property, old_value, new_value)
            self.emit(QtCore.SIGNAL("newItem"), new_item["properties"], property_changed_cb)
                  
    def add_window_clicked(self):
        """
        Descript. :
        """
        self._addItem(self.root_element, "window")

    def _addItem(self, parentListItem, item_type, *args):
        """
        Descript. :
        """
        parent_name = str(parentListItem.text(0))

        parent = self.configuration.findContainer(parent_name)
        new_item = None
        new_list_item = None
       

     
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            if item_type == "window":
                new_item = self.configuration.addWindow()

                if type(new_item) == types.StringType:
                    QtGui.QMessageBox.warning(self, "Cannot add", new_item, QtGui.QMessageBox.Ok)
                else:
                    new_item["properties"].getProperty("w").setValue(QtGui.QApplication.desktop().width())
                    new_item["properties"].getProperty("h").setValue(QtGui.QApplication.desktop().height())
                    
                    new_list_item = self.appendItem(parentListItem, new_item["name"], "window", icon="window_small")
            elif item_type == "brick":
                brick_type = args[0]
               
                new_item = self.configuration.addBrick(brick_type, parent)

                if type(new_item) == types.StringType:
                    QtGui.QMessageBox.warning(self, "Cannot add", new_item, QtGui.QMessageBox.Ok)
                else:
                    brick_name = new_item["name"]
                    brick = new_item["brick"]
                    new_list_item = self.appendItem(parentListItem, brick_name, brick_type, icon="brick")
            elif item_type == "tab":
                new_item = self.configuration.addItem(item_type, parent)

                if type(new_item) == types.StringType:
                    QtGui.QMessageBox.warning(self, "Cannot add", new_item, QtGui.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]
                    new_list_item = self.appendItem(parentListItem, item_name, item_type, icon=item_type)
            else:
                item_subtype = args[0]
                new_item = self.configuration.addItem(item_subtype, parent)

                if type(new_item) == types.StringType:
                    QtGui.QMessageBox.warning(self, "Cannot add", new_item, QtGui.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]
                    new_list_item = self.appendItem(parentListItem, item_name, item_type, icon=item_subtype)
                        
            if type(new_item) != types.StringType and new_item is not None:
                self.connectItem(parent, new_item, new_list_item)
                self.emit(QtCore.SIGNAL("addWidget"), new_item, parent)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def addBrick(self, brick_type):
        """
        Descript. :
        """
        self.addItem("brick", brick_type)

    def addContainer(self, container_type, container_subtype=None):
        """
        Descript. :
        """
        self.addItem(container_type, container_subtype)

    def addItem(self, item_type, item_subtype):
        """
        Descript. :
        """
        currentItem = self.tree_widget.currentItem()
        if currentItem:
            item_cfg = self.configuration.findItem(str(currentItem.text(0)))

            try:
                if self.configuration.isContainer(item_cfg):
                    self._addItem(currentItem, item_type, item_subtype)
                else:
                    # try to add to parent instead
                    parentItem = currentItem.parent()
                
                    self._addItem(parentItem, item_type, item_subtype)
            except:
                QtGui.QMessageBox.warning(self, "Cannot add %s" % item_type, "Please select a suitable parent container", QtGui.QMessageBox.Ok)
    
    def add_hbox_clicked(self):
        """
        Descript. :
        """
        self.addContainer("hbox", "hbox")

    def add_vbox_clicked(self):
        """
        Descript. :
        """
        self.addContainer("vbox", "vbox")
       
    def add_hgroupbox_clicked(self):
        """
        Descript. :
        """
        self.addContainer("hgroupbox", "hgroupbox")

    def add_vgroupbox_clicked(self):
        """
        Descript. :
        """
        self.addContainer("vgroupbox", "vgroupbox")

    def add_hspacer_clicked(self):
        """
        Descript. :
        """
        self.addItem("hspacer", "hspacer")

    def add_vspacer_clicked(self):
        """
        Descript. :
        """
        self.addItem("vspacer", "vspacer")

    def add_tab_clicked(self):
        """
        Descript. :
        """
        self.addContainer("tab")

    def add_vsplitter_clicked(self):
        """
        Descript. :
        """
        self.addContainer("vsplitter", "vsplitter")

    def add_hsplitter_clicked(self):
        """
        Descript. :
        """
        self.addContainer("hsplitter", "hsplitter")
        
    def add_icon_clicked(self):
        """
        Descript. :
        """
        self.addItem("icon", "icon")

    def add_label_clicked(self):
        """
        Descript. :
        """
        self.addItem("label", "label")

    def selectItem(self, item_name):
        """
        Descript. :
        """
        item = self.tree_widget.findItems(QtCore.QString(item_name), 
                    QtCore.Qt.MatchRecursive, 0)
        if item is not None:
            self.tree_widget.setCurrentItem(item[0])
            self.tree_widget.scrollToItem(item[0], QtGui.QAbstractItemView.EnsureVisible)
            
    def item_double_clicked(self, item, column):
        """
        Descript. :
        """
        if item and column == 0:
            item_name = str(item.text(0))
            item_cfg = self.configuration.findItem(item_name)
            if item_cfg:
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled |
                              QtCore.Qt.ItemIsEditable)
                self.item_rename_started = True
                self.tree_widget.editItem(item)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)

    def item_selected(self):
        """
        Descript. :
        """
        self.item_rename_started = None
        item = self.tree_widget.currentItem()      
        if not item == self.root_element:
            item_name = str(item.text(0))
            item_cfg = self.configuration.findItem(item_name) 
            self.update_window_preview(item_name, item_cfg, selected_item=item_name)
            self.updateProperties(item_cfg)
            self.emit(QtCore.SIGNAL('showProperyEditorWindow'), ())
       

    def item_changed(self, item, col):
        """
        Descript. : Item changed even. Used when item text in column 0 
                    has been changed
        """ 
        if self.item_rename_started:
            item_parent_name = str(item.parent().text(0))
            new_item_name = str(item.text(0))
            old_name = self.configuration.rename(item_parent_name, item.parent().indexOfChild(item), new_item_name)
            if old_name is not None:
                item.setText(0, old_name)
                QtGui.QMessageBox.warning(self, "Cannot rename item", 
                                          "New name %s conflicts\nwith another item name." % \
                                          new_item_name, QtGui.QMessageBox.Ok)

    def item_right_clicked(self, item):
        """
        Descript. :
        """
        item_name = str(item.text(0))
        item_cfg = self.configuration.findItem(item_name)
        if self.configuration.isBrick(item_cfg):
            popup_menu = QtGui.QPopupMenu()

            def _itemRightClicked(id, item_name=item_name):
                item_cfg=self.configuration.reload_brick(item_name)
                item = self.tree_widget.findItem(item_name, 0)
                self.emit(QtCore.SIGNAL("newItem"), (item_cfg["brick"].propertyBag, item_cfg["brick"]._propertyChanged))
                self.item_selected(item)
                
            QtCore.QObject.connect(popup_menu, QtCore.SIGNAL("activated(int)"), _itemRightClicked)
                
            popup_menu.insertItem("reload brick", 0)
            popup_menu.exec_loop(QtCore.QCursor.pos())


    def item_drag_dropped(self, source_item, target_item):
        """
        Descript. :
        """
        dragged_item_name = source_item.text(0) 
        dropped_on_item_name = target_item.text(0)

        source_item_parent_name = str(source_item.parent().text(0)) 
        target_item_parent_name = str(target_item.parent().text(0))

        # find common ancestor
        target_item_ancestors = [target_item.parent()]
        source_item_ancestors = [source_item.parent()]
        while target_item_ancestors[0]:
            target_item_ancestors.insert(0, target_item_ancestors[0].parent())
        while source_item_ancestors[0]:
            source_item_ancestors.insert(0, source_item_ancestors[0].parent()) 
        common_ancestor = zip(target_item_ancestors, source_item_ancestors)[-1][0]
        if common_ancestor != self.root_element:
            common_ancestor_name = str(common_ancestor.text(0))
        else:
            common_ancestor_name = ""

        # move item in configuration
        if not self.configuration.moveItem(dragged_item_name, dropped_on_item_name):
            #self.tree_widget.setSelected(source_item, True)
            source_item.setSelected(True)
            self.tree_widget.setCurrentItem(source_item)
            return

        # move item in the GUI tree
 
        #source_item.parent().takeItem(source_item)
        source_item.parent().takeChild(source_item.parent().indexOfChild(source_item)) 
        

        target_cfg_item = self.configuration.findItem(dropped_on_item_name)

        if self.configuration.isContainer(target_cfg_item):
            # have to insert in the container
            target_item.addChild(source_item)
        else:
            target_item.parent().addChild(source_item)
            #source_item.moveItem(target_item)

        #if source_item_parent_name != target_item_parent_name:
        #    self.update_window_preview(source_item_parent_name)
        if len(common_ancestor_name):
            self.update_window_preview(common_ancestor_name)

        #source_item.setSelected(True)
        source_item.setSelected(True)
        self.tree_widget.setCurrentItem(source_item)
        self.tree_widget.scrollToItem(source_item, QtGui.QAbstractItemView.EnsureVisible)
 
    def move_item(self, direction):
        """
        Descript. :
        """
        item = self.tree_widget.currentItem()

        if item:
            item_name = str(item.text(0))
            oldParentItem = item.parent()
            
            if direction == "up":
                newParent = self.configuration.moveUp(item_name)

                if newParent is not None:
                    new_parent_item_list = self.tree_widget.findItems(QtCore.QString(newParent), QtCore.Qt.MatchRecursive, 0)
                    new_parent_item = new_parent_item_list[0]

                    item_index = oldParentItem.indexOfChild(item)
                    oldParentItem.takeChild(item_index)
                    if new_parent_item == oldParentItem:
                        item_index -= 1
                        oldParentItem.insertChild(item_index, item)
                    else:
                        new_parent_item.insertChild(0, item)
            else:
                newParent = self.configuration.moveDown(item_name)
            
                if newParent is not None:
                    new_parent_item_list = self.tree_widget.findItems(QtCore.QString(newParent), QtCore.Qt.MatchRecursive, 0)
                    new_parent_item = new_parent_item_list[0]

                    item_index = oldParentItem.indexOfChild(item) 
                    oldParentItem.takeChild(item_index)
                    if new_parent_item == oldParentItem:
                        item_index += 1
                        oldParentItem.insertChild(item_index, item)
                    else:
                        new_parent_item.addChild(item)

            if newParent is not None:
                 self.update_window_preview(newParent)
                 
            #item.setSelected(True)
            self.tree_widget.setCurrentItem(item)
            self.tree_widget.scrollToItem(item, QtGui.QAbstractItemView.EnsureVisible)
            self.emit(QtCore.SIGNAL("moveWidget"), item_name, direction)

    def move_up_clicked(self):
        """
        Descript. :
        """
        self.move_item("up")

    def move_down_clicked(self):
        """
        Descript. :
        """
        self.move_item("down")
    

class GUIPreviewWindow(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, *args)
       
        self.setWindowTitle("GUI Preview")
        self.window_preview_box = QtGui.QGroupBox("Preview window", self)
        self.window_preview = Qt4_GUIDisplay.WindowDisplayWidget(self.window_preview_box)

        self.window_preview_box_layout = QtGui.QVBoxLayout()
        self.window_preview_box_layout.addWidget(self.window_preview)
        self.window_preview_box.setLayout(self.window_preview_box_layout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.window_preview_box) 
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(2) 

        QtCore.QObject.connect(self.window_preview, QtCore.SIGNAL("itemClicked"), self.preview_item_clicked) 
        self.resize(630,480)

    def renew(self):
        """
        Descript. :
        """
        return
        self.window_preview_box.close()
        self.window_preview_box = QtGui.QGroupBox("Preview window", self)
        self.window_preview = Qt4_GUIDisplay.WindowDisplayWidget(self.window_preview_box)

        self.window_preview_box_layout = QtGui.QVBoxLayout()
        self.window_preview_box_layout.addWidget(self.window_preview)
        self.window_preview_box.setLayout(self.window_preview_box_layout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.window_preview_box)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(0)
        QtCore.QObject.connect(self.window_preview, QtCore.SIGNAL("itemClicked"), self.preview_item_clicked)

        self.resize(650,480)
        self.window_preview_box.show()

    def preview_item_clicked(self, item_name):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("previewItemClicked"), item_name)

    def drawWindow(self, container_cfg, window_id, container_ids, selected_item):
        """
        Descript. :
        """
        if container_cfg["type"] == "window":
            caption = container_cfg["properties"]["caption"]
            s = caption and " - %s" % caption or ""
            self.window_preview_box.setTitle("Window preview: %s%s" % (container_cfg["name"], s))

        self.window_preview.drawPreview(container_cfg, window_id, container_ids, selected_item)

    def updateWindow(self, container_cfg, window_id, container_ids, selected_item):
        """
        Descript. :
        """
        if container_cfg["type"] == "window":
            caption = container_cfg["properties"]["caption"]
            s = caption and " - %s" % caption or ""
            self.window_preview_box.setTitle("Window preview: %s%s" % (container_cfg["name"], s))

        self.window_preview.updatePreview(container_cfg, window_id, container_ids, selected_item)

    def add_window_widget(self, window_cfg):
        """
        Descript. :
        """
        self.window_preview.add_window(window_cfg)
 
    def remove_item_widget(self, item_widget, children_name_list):
        """
        Descript. :
        """
        self.window_preview.remove_widget(item_widget, children_name_list)

    def add_item_widget(self, item_widget, parent_widget):
        """
        Descript. :
        """
        self.window_preview.add_widget(item_widget, parent_widget)

    def move_item_widget(self, item_widget, direction):
        """
        Descript. :
        """
        self.window_preview.move_widget(item_widget, direction)

class HWRWindow(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """

        QtGui.QWidget.__init__(self, *args)

        self.setWindowTitle("Hardware Repository browser")
        
        tb = QtGui.QWidget(self)
        tb_layout = QtGui.QHBoxLayout()

        _refresh_toolbutton = QtGui.QToolButton(tb)
        _refresh_toolbutton.setIcon(QtGui.QIcon(Qt4_Icons.load("reload")))
        _refresh_toolbutton.setToolTip("refresh HWR objects tree")

        _close_toolbutton = QtGui.QToolButton(tb)
        _close_toolbutton.setIcon(QtGui.QIcon(Qt4_Icons.load("button_cancel")))
        _close_toolbutton.setToolTip("close HWR browser")
        horizontal_spacer = HorizontalSpacer(tb)
        tb_layout.addWidget(_refresh_toolbutton)
        tb_layout.addWidget(_close_toolbutton)
        tb_layout.addWidget(horizontal_spacer) 
        tb.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        tb.setLayout(tb_layout)

        QtCore.QObject.connect(_refresh_toolbutton, QtCore.SIGNAL("clicked()"), self.refresh)
        QtCore.QObject.connect(_close_toolbutton, QtCore.SIGNAL("clicked()"), self.close)

        _main_vlayout = QtGui.QVBoxLayout()
        _main_vlayout.addWidget(tb)
        self.setLayout(_main_vlayout)
        self.add_hwr_browser()
        
    def add_hwr_browser(self):
        """
        Descript. :
        """
        return
        """try:
            _hwr_widget = HardwareRepositoryBrowser.HardwareRepositoryBrowser
        except AttributeError:
            logging.getLogger().error("No Hardware Repository client found")
        else:
            self.hwr_widget = _hwr_widget(self)
            self.layout().addWidget(self.hwr_widget)
            self.hwr_widget.show()"""
                
    def refresh(self):
        """
        Descript. :
        """
        self.hwr_widget.close(True)
        self.add_hwr_browser()


class GUIBuilder(QtGui.QMainWindow):
    """
    Descript. :
    """

    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """

        QtGui.QMainWindow.__init__(self, *args)

        self.filename = None
        self.setWindowTitle("GUI Builder")

        self.main_widget = QtGui.QSplitter(self)
        self.setCentralWidget(self.main_widget)

        self.statusbar = self.statusBar()
        self.gui_editor_window = GUIEditorWindow(self.main_widget)
        self.toolbox_window = ToolboxWindow(self.main_widget)
        
        self.log_window = Qt4_LogViewBrick.Qt4_LogViewBrick(None)
        self.log_window.setWindowTitle("Log window")
        sw = QtGui.QApplication.desktop().screen().width()
        sh = QtGui.QApplication.desktop().screen().height()
        self.log_window.resize(QtCore.QSize(sw * 0.8, sh * 0.2))
        self.property_editor_window = Qt4_PropertyEditorWindow(None)
        self.gui_preview_window = GUIPreviewWindow(None)
        self.hwr_window = HWRWindow(None)

        self.configuration = self.gui_editor_window.configuration
        
        file_new_action = self.create_action("&New...", 
                               self.new_clicked, QtGui.QKeySequence.New, 
                               None, "Create new GUI")
        file_open_action = self.create_action("&Open...", 
                                self.open_clicked, QtGui.QKeySequence.Open, 
                                None, "Open an existing GUI file")
        file_save_action = self.create_action("&Save", 
                                self.save_clicked, QtGui.QKeySequence.Save,  
                                None, "Save the gui file")
        file_save_as_action = self.create_action("Save &As...",
                                   self.save_as_clicked, 
                                   None, tip = "Save the gui file using a new name")
        file_quit_action = self.create_action("&Quit", 
                                self.quit_clicked, "Ctrl+Q", 
                                None, "Close the application")

        self.fileMenu = self.menuBar().addMenu("&File")
        self.file_menu_actions = (file_new_action, 
                                  file_open_action, 
                                  file_save_action, 
                                  file_save_as_action, 
                                  file_quit_action)

        self.add_actions(self.fileMenu, self.file_menu_actions)

        show_propery_editor_windowAction = self.create_action("Properties", 
                                                 self.show_property_editor_window,
                                                 tip = "Show properties")
        show_gui_preview_action = self.create_action("GUI preview", 
                                       self.show_gui_preview_window,
                                       tip = "GUI preview")
        show_log_windowAction = self.create_action(
                                     "Log", self.show_log_window, tip = "Show log")
        show_gui_action = self.create_action("Launch GUI",
                               self.launch_gui_cicked,
                               tip = "launch GUI (as a separate process)")
        show_hwr_window = self.create_action("HWR",
                               self.show_hwr_window,
                               tip = "Show Hardware Repository")

        window_menu = self.menuBar().addMenu("&Window")
        window_menu_actions = (show_propery_editor_windowAction, 
                               show_gui_preview_action, 
                               show_log_windowAction, 
                               show_gui_action, 
                               show_hwr_window)
        self.add_actions(window_menu, window_menu_actions[:-1]) 

        self.connect(self.toolbox_window, QtCore.SIGNAL("addBrick"), 
                     self.gui_editor_window.addBrick)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("editProperties"), 
                     self.property_editor_window.editProperties)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("newItem"), 
                     self.property_editor_window.addProperties)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("drawPreview"), 
                     self.gui_preview_window.drawWindow)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("updatePreview"), 
                     self.gui_preview_window.updateWindow)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("addWidget"), 
                     self.gui_preview_window.add_item_widget)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("removeWidget"), 
                     self.gui_preview_window.remove_item_widget)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("moveWidget"),
                     self.gui_preview_window.move_item_widget)
        self.connect(self.gui_preview_window, QtCore.SIGNAL("previewItemClicked"), 
                     self.gui_editor_window.selectItem)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("showProperyEditorWindow"), 
                     self.show_property_editor_window)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("hidePropertyEditorWindow"), 
                     self.hide_property_editor_window)
        self.connect(self.gui_editor_window, QtCore.SIGNAL("showPreview"), 
                     self.show_gui_preview_window)

        self.toolbox_window.refresh_clicked()

        self.gui_preview_window.show()
        self.resize(480, 800)

    def create_action(self, text, slot = None, shortcut = None, icon = None,
                      tip = None, checkable = False, signal = "triggered()"):
        """
        Descript. :
        """
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(icon)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        """
        Descript. :
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
        
    def new_clicked(self, filename = None):
        """
        Descript. :
        """
        self.configuration = Qt4_Configuration.Configuration()
        self.filename = filename

        if self.filename:
            self.setWindowTitle("GUI Builder - %s" % filename)
        else:
            self.setWindowTitle("GUI Builder")

        self.gui_preview_window.renew()
        self.gui_editor_window.set_configuration(self.configuration)

    def open_clicked(self):
        """
        Descript. :
        """
        filename = str(QtGui.QFileDialog.getOpenFileName(os.environ["HOME"],
                       "GUI file (*.gui)", self, "Save file", "Choose a GUI file to open"))

        if len(filename) > 0:
            try:
                f = open(filename)
            except:
                logging.getLogger().exception("Cannot open file %s", filename)
                QtGui.QMessageBox.warning(self, "Error", "Could not open file %s !" % \
                                          filename, QtGui.QMessageBox.Ok)
            else:
                try:
                    raw_config = eval(f.read())
                    try:
                        new_config = Qt4_Configuration.Configuration(raw_config)
                    except:
                        logging.getLogger().exception("Cannot read configuration from file %s", filename)
                        QtGui.QMessageBox.warning(self, "Error", "Could not read configuration\nfrom file %s" % \
                                                  filename, QtGui.QMessageBox.Ok)
                    else:
                        self.filename = filename
                        self.configuration = new_config
                        self.setCaption("GUI Builder - %s" % filename)
                        self.gui_preview_window.renew()
                        self.gui_editor_window.set_configuration(new_config)
                finally:
                    f.close()
                

    def save_clicked(self):
        """
        Descript. :
        """
        if True: #try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            
            if self.filename is not None:
                if os.path.exists(self.filename):
                    should_create_startup_script=False
                else:
                    should_create_startup_script=True
                    
                if self.configuration.save(self.filename):
                    self.setWindowTitle("GUI Builder - %s" % self.filename)
                    QtGui.QApplication.restoreOverrideCursor()
                    QtGui.QMessageBox.information(self, "Success", "Qt4_Configuration have been saved successfully to\n%s" % self.filename, QtGui.QMessageBox.Ok)

                    if should_create_startup_script:
                        if QtGui.QMessageBox.question(self, "Launch script",
                                                   "Do you want to create a startup script for the new GUI ?",
                                                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                            try:
                                hwr_server = HardwareRepository.HardwareRepository().serverAddress
                            except:
                                hwr_server = ""
                            else:
                                pid = subprocess.Popen("newGUI --just-script %s %s" % (self.filename, hwr_server), shell=True).pid
                    return True
                else:
                    QtGui.QApplication.restoreOverrideCursor()
                    QtGui.QMessageBox.warning(self, "Error", "Could not save configuration to file %s !" % self.filename, QtGui.QMessageBox.Ok)

                    return False
            else:
                QtGui.QApplication.restoreOverrideCursor()
                self.save_as_clicked()
        #finally:
        #    QtGui.QApplication.restoreOverrideCursor()


    def save_as_clicked(self):
        """
        Descript. :
        """
        f = self.filename
        self.filename = str(QtGui.QFileDialog.getSaveFileName(self, os.environ["HOME"],
             "GUI file (*.gui)", "Save file", "Choose a filename to save under"))

        if len(self.filename) == 0:
            self.filename = f
            return
        elif not self.filename.endswith(os.path.extsep+"gui"):
            self.filename += os.path.extsep + 'gui'

        return self.save_clicked()
                                                    
    def quit_clicked(self):
        """
        Descript. :
        """
        if self.gui_editor_window.configuration.hasChanged:
            if QtGui.QMessageBox.warning(self, "Please confirm",
                     "Are you sure you want to quit ?\nYour changes will be lost.",
                     QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                return
        exit(0) 

    def show_property_editor_window(self):
        """
        Descript. :
        """
        self.property_editor_window.show()

    def hide_property_editor_window(self):
        """
        Descript. :
        """
        self.property_editor_window.close()

    def show_gui_preview_window(self):
        """
        Descript. :
        """
        self.gui_preview_window.show()

    def show_log_window(self):
        """
        Descript. :
        """
        self.log_window.show()

    def show_hwr_window(self):
        """
        Descript. :
        """
        self.hwr_window.show()

    def closeEvent(self,event):
        """
        Descript. :
        """
        event.ignore()
        self.quit_clicked() 

    def launch_gui_cicked(self):
        """
        Descript. :
        """
        if self.gui_editor_window.configuration.hasChanged or self.filename is None:
            if QtGui.QMessageBox.warning(self, "GUI file not saved yet",
                     "Before starting the GUI, the file needs to be saved.\nContinue ?",
                     QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGUi.QMessageBox.No:
                return
            
            self.save_clicked()
            
        terminal = os.environ["TERM"] or "xterm"

        try:
            hwr_server = HardwareRepository.HardwareRepository().serverAddress
        except:
            logging.getLogger().error("Sorry, could not find Hardware Repository server")
        else:
            customBricksDirs = os.path.pathsep.join(BlissFramework.getCustomBricksDirs())
            pid = subprocess.Popen("%s -title %s -e startGUI --bricksDirs=%s %s%s" % (terminal,os.path.basename(self.filename),customBricksDirs, (hwr_server and "--hardwareRepository=%s " % hwr_server or ""), self.filename), shell=True).pid
            
            logging.getLogger().debug("GUI launched, pid is %d", pid)
        
        
if __name__ == '__main__':
    app = GtGui.QApplication([])
    mainwin = GUIBuilder()
    app.setMainWidget(mainwin)
    mainwin.show()
    app.exec_loop()


