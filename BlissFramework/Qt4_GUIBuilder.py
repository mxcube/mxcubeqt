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
else:
    from HardwareRepository import HardwareRepositoryBrowser   
 

class HorizontalSpacer(QtGui.QWidget):
    """Helper class to have a horizontal spacer widget"""
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)
        
        h_size = kwargs.get("size", None)
    
        if h_size is not None:
            self.setFixedWidth(h_size)
            self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        else:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)


class MyListView(QtGui.QListWidget):
    class ListViewToolTip(QtGui.QToolTip):
        def __init__(self, parent):
            QtGui.QToolTip.__init__(self, parent.viewport())

            self.parent = weakref.ref(parent)
        
            self.tooltips = weakref.WeakKeyDictionary()


        def add(self, item, text):
            self.tooltips[item] = text
        

        def maybeTip(self, pos):
            parent = self.parent()

            if parent is None:
                return
            
            item = parent.itemAt(pos)

            try:
                text = self.tooltips[item]
            except (KeyError,TypeError):
                return

            if item:
                itemRect = parent.itemRect(item)
           
                self.tip(itemRect, text)


    def __init__(self, *args):
        QtGui.QListView.__init__(self, *args)

        #self.__tooltip = MyListView.ListViewToolTip(self)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #self.setVScrollBarMode(QtGui.QScrollView.Auto)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        

    def addToolTip(self, item, text):
        self.setToolTip(text)
        #self.__tooltip.add(item, text)



class GUITreeWidget(QtGui.QTreeWidget):
    def __init__(self, *args):
        QtGui.QTreeWidget.__init__(self, *args)

        self._presspos = None
        self._mousePressed = False

        #self.setSorting(-1) #disable sorting
        #self.addColumn("Element")
        #self.addColumn("Type")
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
        self.drag_source_item = self.itemAt(event.pos())
        event.accept() 

    def dropEvent(self, event):
        self.drag_target_item = self.itemAt(event.pos())
        if self.drag_source_item and self.drag_target_item:
            self.emit(QtCore.SIGNAL("dragdrop"), self.drag_source_item, self.drag_target_item)
        event.accept()
            
class ToolboxWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)
       
        self.setWindowTitle("Toolbox")
        self.bricksTab = {}
        self.bricks = {}
      
        topPanel = QtGui.QFrame(self)
        self.cmdRefresh = QtGui.QToolButton(topPanel)
        self.cmdRefresh.setIcon(QtGui.QIcon(Qt4_Icons.load("reload")))
        self.setToolTip("refresh bricks list")  
        self.bricksToolbox = QtGui.QToolBox(self)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(QtGui.QLabel("Available bricks", topPanel))
        main_layout.addWidget(self.cmdRefresh)
        main_layout.addWidget(self.bricksToolbox) 
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0) 
        self.setLayout(main_layout)
        
        QtCore.QObject.connect(self.cmdRefresh, QtCore.SIGNAL("clicked()"), self.refresh) 
        

    def addBrickTab(self, name):
        """Add a new brick tab called 'name'"""
        newBricksList = MyListView(self.bricksToolbox)
        #newBricksList.addColumn("")
        #newBricksList.header().hide()
        QtCore.QObject.connect(newBricksList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.brickSelected)
        self.bricksToolbox.addItem(newBricksList, name)
        self.bricksTab[name] = newBricksList

        return newBricksList
        

    def refresh(self):
        """Refresh bricks window"""
        while self.bricksToolbox.currentWidget():
            self.bricksToolbox.removeItem(self.bricksToolbox.currentIndex())
       
        self.bricks = {}
        self.bricksTab = {}
            
        #self.addBrickTab("General")
        # bricks without category fall into 'General'
        #self.bricksTab[""] = self.bricksTab["General"]
       
        map(self.addBricks, (BlissFramework.getStdBricksPath(), ) + tuple(BlissFramework.getCustomBricksDirs()))


    def brickTextLabel(self, brickName):
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
        """Add the bricks found in the 'brickDir' directory to the bricks tab widget"""
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
                if not brickName == '__init__' and not brickName in processedBricks:
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
                bricksListWidget = self.bricksTab[category]
            except KeyError:
                bricksListWidget = self.addBrickTab(category)
            
            for brickName, dirname, description in bricksList:
                newBrick = QtGui.QListWidgetItem(QtCore.QString(self.brickTextLabel(brickName)), bricksListWidget)
                bricksListWidget.addToolTip(newBrick, description)
                self.bricks[id(newBrick)] = (dirname, brickName)


    def brickSelected(self, item):
        dirname, brickName = self.bricks[id(item)]
        self.emit(QtCore.SIGNAL("addBrick"), brickName)
        

class Qt4_PropertyEditorWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)
 
        self.setWindowTitle("Properties")

        self.propertiesTable = Qt4_PropertyEditor.Qt4_ConfigurationTable(self)
        self.__property_changed_cb = weakref.WeakKeyDictionary()

        QtCore.QObject.connect(self.propertiesTable, QtCore.SIGNAL("propertyChanged"), self.propertyChanged)

        self.setLayout(QtGui.QHBoxLayout())
        #qt.QHBoxLayout(self)
        self.layout().addWidget(self.propertiesTable)


    def editProperties(self, propertyBag):
        self.propertiesTable.setPropertyBag(propertyBag)

    def propertyChanged(self, *args):
        try:
            cb = self.__property_changed_cb[self.propertiesTable.propertyBag]
        except KeyError, err:
            return
        else:
            cb(*args)
            
      
    def addProperties(self, propertyBag, property_changed_cb):
        self.__property_changed_cb[propertyBag] = property_changed_cb
        self.editProperties(propertyBag)
    

class ToolButton(QtGui.QToolButton):
    def __init__(self, parent, icon, text=None, callback=None, tooltip=None):
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
            QtCore.QObject.connect(self, QtCore.SIGNAL("clicked()"), callback)

        if tooltip is not None:
            self.setToolTip(tooltip) 
            #QtGui.QToolTip.add(self, tooltip)

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)


class GUIEditorWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)

        self.configuration = Qt4_Configuration.Configuration()
        #self.connection_editor_window = Qt4_ConnectionEditor.Qt4_ConnectionEditor(self.configuration)
      
        self.setWindowTitle("GUI Editor")

        toolsBox = QtGui.QWidget(self)
        toolsBox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        self.cmdAddWindow = ToolButton(toolsBox, "window_new", self.addWindow, "add a new window (container)")
        self.cmdAddTab = ToolButton(toolsBox, "tab", self.addTab, "add a new tab (container)")
        self.cmdAddHBox = ToolButton(toolsBox, "add_hbox", self.addHBox, "add a new horizontal box (container)")
        self.cmdAddVBox = ToolButton(toolsBox, "add_vbox", self.addVBox, "add a new vertical box (container)")
        self.cmdAddHGroupBox = ToolButton(toolsBox, "hgroupbox", self.addHGroupBox, "add a new horizontal group box (container)")
        self.cmdAddVGroupBox = ToolButton(toolsBox, "vgroupbox", self.addVGroupBox, "add a new vertical group box (container)")
        self.cmdAddHSpacer = ToolButton(toolsBox, "add_hspacer", self.addHSpacer, "add a new horizontal spacer")
        self.cmdAddVSpacer = ToolButton(toolsBox, "add_vspacer", self.addVSpacer, "add a new vertical spacer")
        self.cmdAddHSplitter = ToolButton(toolsBox, "hsplitter", self.addHSplitter, "add a new horizontal splitter (container)")
        self.cmdAddVSplitter = ToolButton(toolsBox, "vsplitter", self.addVSplitter, "add a new vertical splitter (container)")
        self.cmdAddIcon = ToolButton(toolsBox, "icon", self.addIcon, "add a new icon")
        self.cmdAddLabel = ToolButton(toolsBox, "label", self.addLabel, "add a new label")

        toolBoxLayout = QtGui.QHBoxLayout()
        toolBoxLayout.addWidget(self.cmdAddWindow)
        toolBoxLayout.addWidget(self.cmdAddTab)
        toolBoxLayout.addWidget(self.cmdAddHBox)
        toolBoxLayout.addWidget(self.cmdAddVBox)        
        toolBoxLayout.addWidget(self.cmdAddHGroupBox)
        toolBoxLayout.addWidget(self.cmdAddVGroupBox)
        toolBoxLayout.addWidget(self.cmdAddHSpacer)
        toolBoxLayout.addWidget(self.cmdAddVSpacer)
        toolBoxLayout.addWidget(self.cmdAddHSplitter)
        toolBoxLayout.addWidget(self.cmdAddVSplitter)
        toolBoxLayout.addWidget(self.cmdAddIcon)
        toolBoxLayout.addWidget(self.cmdAddLabel)
        toolBoxLayout.addStretch(0)
        toolBoxLayout.setSpacing(2)
        toolBoxLayout.setContentsMargins(2,2,2,2)
        toolsBox.setLayout(toolBoxLayout)
       

        treeHandlingBox = QtGui.QWidget(self)

        self.cmdShowConnections=ToolButton(treeHandlingBox, "connect_creating", 
                                           self.showConnections, "manage connections between items")
        self.cmdMoveUp=ToolButton(treeHandlingBox, "Up2", self.moveUp, "move an item up")
        self.cmdMoveDown=ToolButton(treeHandlingBox, "Down2", self.moveDown, "move an item down")
        self.cmdRemoveItem=ToolButton(treeHandlingBox, "delete_small", self.removeItem, "delete an item")

        treeHandlingBoxLayout = QtGui.QHBoxLayout()
        treeHandlingBoxLayout.addWidget(self.cmdShowConnections)
        treeHandlingBoxLayout.addWidget(self.cmdMoveUp)
        treeHandlingBoxLayout.addWidget(self.cmdMoveDown)
        treeHandlingBoxLayout.addWidget(self.cmdRemoveItem)
        treeHandlingBoxLayout.addStretch(0)
        treeHandlingBoxLayout.setSpacing(2)
        treeHandlingBoxLayout.setContentsMargins(2,2,2,2)
        treeHandlingBox.setLayout(treeHandlingBoxLayout) 
        
        self.tree_widget = GUITreeWidget(self)

        self.root_element = QtGui.QTreeWidgetItem(self.tree_widget)
        self.root_element.setText(0, QtCore.QString("GUI tree")) 
        self.root_element.setExpanded(True)

        self.connect(self.tree_widget, QtCore.SIGNAL('itemSelectionChanged()'), self.item_selected)
        self.connect(self.tree_widget, QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'), self.item_double_clicked)
        self.connect(self.tree_widget, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.item_changed)
        self.connect(self.tree_widget, QtCore.SIGNAL('dragdrop'), self.item_drag_dropped)
        self.connect(self.tree_widget, QtCore.SIGNAL('contextMenuRequested'), self.itemRightClicked)
    
        main_layout = QtGui.QVBoxLayout()  
        main_layout.addWidget(toolsBox)
        main_layout.addWidget(treeHandlingBox)
        main_layout.addWidget(self.tree_widget)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2,2,2,2)
        self.setLayout(main_layout)

        self.item_rename_started = None

    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
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

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def set_configuration(self, configuration):
        self.configuration = configuration

        self.tree_widget.blockSignals(True)
        #self.tree_widget.takeTopLevelItem(0)
        #self.tree_widget.takeItem(self.root_element)
        #self.tree_widget.itemAt(0,0)
        #self.root_element = QtGui.QTreeWidgetItem(self.tree_widget)
        #self.root_element.setText(0, QtCore.QString("GUI tree"))
        #self.root_element.setOpen(True)
        
        self.emit(QtCore.SIGNAL('hideProperties'), ())

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
        self.emit(QtCore.SIGNAL('showProperties'), ())

    def showConnections(self):
        self.connection_editor_window = Qt4_ConnectionEditor.Qt4_ConnectionEditor(self.configuration)
        width = QtGui.QApplication.desktop().width()
        height = QtGui.QApplication.desktop().height()
        self.connection_editor_window.resize(0.85 * width, 0.7 * height)

        self.connection_editor_window.show()


    def updateProperties(self, item_cfg):
        self.emit(QtCore.SIGNAL("editProperties"), item_cfg["properties"])
        

    def _getParentWindowName(self, item): 
        while item:
            if str(item.text(1)) == "window":
                return str(item.text(0))
            else:
                item = item.parent()
    
            
    def appendItem(self, parentItem, column1_text, column2_text, icon=None):
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
        
    def removeItem(self):
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
        container_name = self.root_element.child(0).text(0)
        container_cfg, window_id, container_ids, selected_item = \
             self.prepare_window_preview(container_name, None, "")
        self.emit(QtCore.SIGNAL("drawPreview"), container_cfg, window_id, container_ids, selected_item)

    def update_window_preview(self, container_name, container_cfg=None, selected_item=""): 
        upd_container_cfg, upd_window_id, upd_container_ids, upd_selected_item = \
             self.prepare_window_preview(container_name, container_cfg, selected_item)
        self.emit(QtCore.SIGNAL("updatePreview"), upd_container_cfg, upd_window_id, upd_container_ids, selected_item)

    def prepare_window_preview(self, item_name, item_cfg = None, selected_item = ""):
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
                  

    def addWindow(self):
        self._addItem(self.root_element, "window")

    def _addItem(self, parentListItem, item_type, *args):
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
        self.addItem("brick", brick_type)

    def addContainer(self, container_type, container_subtype=None):
        self.addItem(container_type, container_subtype)

    
    def addItem(self, item_type, item_subtype):
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
    
    def addHBox(self):
        self.addContainer("hbox", "hbox")
       

    def addVBox(self):
        self.addContainer("vbox", "vbox")
       

    def addHGroupBox(self):
        self.addContainer("hgroupbox", "hgroupbox")


    def addVGroupBox(self):
        self.addContainer("vgroupbox", "vgroupbox")


    def addHSpacer(self):
        self.addItem("hspacer", "hspacer")
    

    def addVSpacer(self):
        self.addItem("vspacer", "vspacer")


    def addTab(self):
         self.addContainer("tab")


    def addVSplitter(self):
        self.addContainer("vsplitter", "vsplitter")


    def addHSplitter(self):
        self.addContainer("hsplitter", "hsplitter")
        

    def addIcon(self):
        self.addItem("icon", "icon")


    def addLabel(self):
        self.addItem("label", "label")


    def selectItem(self, item_name):
        item = self.tree_widget.findItems(QtCore.QString(item_name), QtCore.Qt.MatchRecursive, 0)
        if item is not None:
            self.tree_widget.setCurrentItem(item[0])
            self.tree_widget.scrollToItem(item[0], QtGui.QAbstractItemView.EnsureVisible)
            
    def item_double_clicked(self, item, column):
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
        self.item_rename_started = None
        item = self.tree_widget.currentItem()      
        if not item == self.root_element:
            item_name = str(item.text(0))
            item_cfg = self.configuration.findItem(item_name) 
            self.update_window_preview(item_name, item_cfg, selected_item=item_name)
            self.updateProperties(item_cfg)
            self.emit(QtCore.SIGNAL('showProperties'), ())
       

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

    def itemRightClicked(self, item):
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

            #self.tree_widget.setSelected(item, True)


    def item_drag_dropped(self, source_item, target_item):
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
            self.tree_widget.setSelected(source_item, True)
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
 

    def moveItem(self, direction):
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
                        oldParentItem.insertChild(item_index - 1, item)
                        """itemAbove = self.tree_widget.itemAbove(item)
                        while (itemAbove.parent() != new_parent_item):
                            itemAbove=itemAbove.itemAbove()
                        itemAbove.moveItem(item)"""
                    else:
                        new_parent_item.insertChild(0, item)
                        """oldParentItem.takeItem(item)
                        new_parent_item.insertItem(item)
                        item.moveItem(oldParentItem.itemAbove())"""
            else:
                newParent = self.configuration.moveDown(item_name)
            
                if newParent is not None:
                    new_parent_item_list = self.tree_widget.findItems(QtCore.QString(newParent), QtCore.Qt.MatchRecursive, 0)
                    new_parent_item = new_parent_item_list[0]

                    item_index = oldParentItem.indexOfChild(item) 
                    oldParentItem.takeChild(item_index)
                    if new_parent_item == oldParentItem:
                        oldParentItem.insertChild(item_index + 1, item)
                        #item.moveItem(item.nextSibling())
                    else:
                        #oldParentItem.takeItem(item)
                        new_parent_item.addChild(item)

            if newParent is not None:
                 self.update_window_preview(newParent)
                 
            #item.setSelected(True)
            self.tree_widget.setCurrentItem(item)
            self.tree_widget.scrollToItem(item, QtGui.QAbstractItemView.EnsureVisible)
            #self.item_selected(item)
                

    def moveUp(self):
        self.moveItem("up")

        
    def moveDown(self):
        self.moveItem("down")
    

class GUIPreviewWindow(QtGui.QWidget):
   def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)
       
        self.setWindowTitle("GUI Preview")

        self.window_preview_box = QtGui.QGroupBox("Preview window", self)
        self.window_preview = Qt4_GUIDisplay.WindowDisplayWidget(self.window_preview_box)
        

        self.window_preview_box_layout = QtGui.QVBoxLayout()
        self.window_preview_box_layout.addWidget(self.window_preview)
        self.window_preview_box.setLayout(self.window_preview_box_layout)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addWidget(self.window_preview_box) 
        self.setLayout(self.main_layout)

        QtCore.QObject.connect(self.window_preview, QtCore.SIGNAL("itemClicked"), self.preview_item_clicked) 

        self.resize(630,480)

   def renew(self):
       return
       self.window_preview_box.close()
       self.window_preview_box = QtGui.QGroupBox("Preview window", self)
       self.window_preview = Qt4_GUIDisplay.WindowDisplayWidget(self.window_preview_box)

       self.window_preview_box_layout = QtGui.QVBoxLayout()
       self.window_preview_box_layout.addWidget(self.window_preview)
       self.window_preview_box.setLayout(self.window_preview_box_layout)

       self.main_layout = QtGui.QVBoxLayout()
       self.main_layout.addWidget(self.window_preview_box)
       self.setLayout(self.main_layout)
       QtCore.QObject.connect(self.window_preview, QtCore.SIGNAL("itemClicked"), self.preview_item_clicked)

       self.resize(650,480)
       self.window_preview_box.show()

   def preview_item_clicked(self, item_name):
       self.emit(QtCore.SIGNAL("previewItemClicked"), item_name)

   def drawWindow(self, container_cfg, window_id, container_ids, selected_item):
       if container_cfg["type"] == "window":
           caption = container_cfg["properties"]["caption"]
           s = caption and " - %s" % caption or ""
           self.window_preview_box.setTitle("Window preview: %s%s" % (container_cfg["name"], s))
       self.window_preview.drawPreview(container_cfg, window_id, container_ids, selected_item)

   def updateWindow(self, container_cfg, window_id, container_ids, selected_item):
       if container_cfg["type"] == "window":
           caption = container_cfg["properties"]["caption"]
           s = caption and " - %s" % caption or ""
           self.window_preview_box.setTitle("Window preview: %s%s" % (container_cfg["name"], s))
       self.window_preview.updatePreview(container_cfg, window_id, container_ids, selected_item)

   def add_window_widget(self, window_cfg):
       self.window_preview.add_window(window_cfg)

   def remove_item_widget(self, item_widget, children_name_list):
       self.window_preview.remove_widget(item_widget, children_name_list)

   def add_item_widget(self, item_widget, parent_widget):
       self.window_preview.add_widget(item_widget, parent_widget)

class HWRWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args)

        self.setWindowTitle("Hardware Repository browser")
        
        tb = QtGui.QWidget(self)
        #tb = qt.QHBox(self)
        tb_layout = QtGui.QHBoxLayout()

        self.cmdRefresh = QtGui.QToolButton(tb)
        self.cmdRefresh.setIcon(QtGui.QIcon(Qt4_Icons.load("reload")))
        self.cmdRefresh.setToolTip("refresh HWR objects tree")
        #qt.QToolTip.add(self.cmdRefresh, "refresh HWR objects tree")

        self.cmdClose = QtGui.QToolButton(tb)
        self.cmdClose.setIcon(QtGui.QIcon(Qt4_Icons.load("button_cancel")))
        self.cmdClose.setToolTip("close HWR browser")
        #qt.QToolTip.add(self.cmdClose, "close HWR browser")
        horizontal_spacer = HorizontalSpacer(tb)
        tb_layout.addWidget(self.cmdRefresh)
        tb_layout.addWidget(self.cmdClose)
        tb_layout.addWidget(horizontal_spacer) 
        tb.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        tb.setLayout(tb_layout)

        QtCore.QObject.connect(self.cmdRefresh, QtCore.SIGNAL("clicked()"), self.refresh)
        QtCore.QObject.connect(self.cmdClose, QtCore.SIGNAL("clicked()"), self.close)

        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)
        #qt.QVBoxLayout(self)
        self.layout().addWidget(tb)
        self.add_hwr_browser()
        

    def add_hwr_browser(self):
        try:
            _hwr_widget = HardwareRepositoryBrowser.HardwareRepositoryBrowser
        except AttributeError:
            logging.getLogger().error("No Hardware Repository client found")
        else:
            self.hwr_widget = _hwr_widget(self)
            self.layout().addWidget(self.hwr_widget)
            self.hwr_widget.show()
            
                
    def refresh(self):
        self.hwr_widget.close(True)
        self.add_hwr_browser()



class GUIBuilder(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, *args)

        self.filename = None
        
        self.setWindowTitle("GUI Builder")

        self.main_widget = QtGui.QSplitter(self)
        self.setCentralWidget(self.main_widget)
        #self.splitter = QtGui.QSplitter(self.main_widget)  

        self.statusbar = self.statusBar()
        self.guiEditorWindow = GUIEditorWindow(self.main_widget)
        self.toolboxWindow = ToolboxWindow(self.main_widget)
        
        self.logWindow = Qt4_LogViewBrick.LogViewBrick(None)
        self.logWindow.setWindowTitle("Log window")
        sw = QtGui.QApplication.desktop().screen().width()
        sh = QtGui.QApplication.desktop().screen().height()
        self.logWindow.resize(QtCore.QSize(sw*0.8, sh*0.2))
        self.propertyEditorWindow = Qt4_PropertyEditorWindow(None)
        self.guiPreviewWindow = GUIPreviewWindow(None)
        self.hwrWindow = HWRWindow(None)

        self.configuration = self.guiEditorWindow.configuration
        
        #
        # build File menu
        #
        fileNewAction = self.createAction("&New...", 
                                          self.newClicked,
                                          QtGui.QKeySequence.New, 
                                          None, 
                                          "Create new GUI")
        fileOpenAction = self.createAction("&Open...", 
                                           self.openClicked,
                                           QtGui.QKeySequence.Open, 
                                           None,
                                           "Open an existing GUI file")
        fileSaveAction = self.createAction("&Save", 
                                           self.saveClicked,
                                           QtGui.QKeySequence.Save,  
                                           None, 
                                           "Save the gui file")
        fileSaveAsAction = self.createAction("Save &As...",
                                             self.saveAsClicked, 
                                             None,
                                             tip = "Save the gui file using a new name")
        fileQuitAction = self.createAction("&Quit", 
                                           self.quitClicked,
                                           "Ctrl+Q", 
                                           None, 
                                           "Close the application")

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewAction, fileOpenAction, fileSaveAction, fileSaveAsAction, fileQuitAction)
        self.addActions(self.fileMenu, self.fileMenuActions)

        showPropertiesAction = self.createAction("Properties", 
                                                 self.showProperties,
                                                 tip = "Show properties")
        showGUIPreviewAction = self.createAction("GUI preview", 
                                           self.showGuiPreview,
                                           tip = "GUI preview")
        showLogAction = self.createAction("Log", 
                                          self.showLog,
                                          tip = "Show log")
        showGUIAction = self.createAction("Launch GUI",
                                          self.launchGUIClicked,
                                          tip = "launch GUI (as a separate process)")
        showHWR = self.createAction("HWR",
                                    self.showHWR,
                                    tip = "Show Hardware Repository")

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenuActions = (showPropertiesAction, showGUIPreviewAction, showLogAction, showGUIAction, showHWR)
        self.addActions(self.windowMenu, self.windowMenuActions[:-1]) 

        #
        # connections
        #
        self.connect(self.toolboxWindow, QtCore.SIGNAL("addBrick"), self.guiEditorWindow.addBrick)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("editProperties"), self.propertyEditorWindow.editProperties)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("newItem"), self.propertyEditorWindow.addProperties)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("drawPreview"), self.guiPreviewWindow.drawWindow)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("updatePreview"), self.guiPreviewWindow.updateWindow)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("addWidget"), self.guiPreviewWindow.add_item_widget)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("removeWidget"), self.guiPreviewWindow.remove_item_widget)
        self.connect(self.guiPreviewWindow, QtCore.SIGNAL("previewItemClicked"), self.guiEditorWindow.selectItem)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("showProperties"), self.showProperties)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("hideProperties"), self.hideProperties)
        self.connect(self.guiEditorWindow, QtCore.SIGNAL("showPreview"), self.showGuiPreview)

        #
        # finish GUI
        #
        self.toolboxWindow.refresh()

        self.guiPreviewWindow.show()
        self.resize(480, 800)

    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
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

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
        

    def newClicked(self, filename = None):
        self.configuration = Qt4_Configuration.Configuration()
        self.filename = filename

        if self.filename:
            self.setWindowTitle("GUI Builder - %s" % filename)
        else:
            self.setWindowTitle("GUI Builder")

        self.guiPreviewWindow.renew()
        self.guiEditorWindow.set_configuration(self.configuration)
        

    def openClicked(self):
        filename = str(QtGui.QFileDialog.getOpenFileName(os.environ["HOME"],
                                                      "GUI file (*.gui)",
                                                      self,
                                                      "Save file",
                                                      "Choose a GUI file to open"))

        if len(filename) > 0:
            try:
                f = open(filename)
            except:
                logging.getLogger().exception("Cannot open file %s", filename)
                QtGui.QMessageBox.warning(self, "Error", "Could not open file %s !" % filename, QtGui.QMessageBox.Ok)
            else:
                try:
                    raw_config = eval(f.read())

                    try:
                        new_config = Qt4_Configuration.Configuration(raw_config)
                    except:
                        logging.getLogger().exception("Cannot read configuration from file %s", filename)
                        qt.QMessageBox.warning(self, "Error", "Could not read configuration\nfrom file %s" % filename, qt.QMessageBox.Ok)
                    else:
                        self.filename = filename
                        self.configuration = new_config
                        self.setCaption("GUI Builder - %s" % filename)
                        self.guiPreviewWindow.renew()
                        self.guiEditorWindow.set_configuration(new_config)
                finally:
                    f.close()
                

    def saveClicked(self):
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
                    QtGui.QMessageBox.warning(self, "Error", "Could not save configuration to file %s !" % self.filename, qt.QMessageBox.Ok)

                    return False
            else:
                QtGui.QApplication.restoreOverrideCursor()
                self.saveAsClicked()
        #finally:
        #    QtGui.QApplication.restoreOverrideCursor()


    def saveAsClicked(self):
        f = self.filename
        self.filename = str(qt.QFileDialog.getSaveFileName(os.environ["HOME"],
                                                           "GUI file (*.gui)",
                                                           self,
                                                           "Save file",
                                                           "Choose a filename to save under"))

        if len(self.filename) == 0:
            self.filename = f
            return
        elif not self.filename.endswith(os.path.extsep+"gui"):
            self.filename += os.path.extsep + 'gui'

        return self.saveClicked()
                                                    

    def quitClicked(self):
        if self.guiEditorWindow.configuration.hasChanged:
            if QtGui.QMessageBox.warning(self, "Please confirm",
                                      "Are you sure you want to quit ?\nYour changes will be lost.",
                                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                return
            
        self.close()


    def showProperties(self):
        #self.propertyEditorWindow.raise()
        self.propertyEditorWindow.show()


    def hideProperties(self):
        self.propertyEditorWindow.close()


    def showGuiPreview(self):
        #self.guiPreviewWindow.raiseW()
        self.guiPreviewWindow.show()


    def showLog(self):
        #self.logWindow.raiseW()
        self.logWindow.show()


    def showHWR(self):
        #self.hwrWindow.raiseW()
        self.hwrWindow.show()


    def launchGUIClicked(self):
        if self.guiEditorWindow.configuration.hasChanged or self.filename is None:
            if qt.QMessageBox.warning(self, "GUI file not saved yet",
                                      "Before starting the GUI, the file needs to be saved.\nContinue ?",
                                      qt.QMessageBox.Yes, qt.QMessageBox.No) == qt.QMessageBox.No:
                return
            
            self.saveClicked()
            
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


