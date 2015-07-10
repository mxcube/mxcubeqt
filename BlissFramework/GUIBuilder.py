import os
import re
import sys
import imp
import types
import weakref
import logging
import subprocess

import qt

import BlissFramework
from BlissFramework import Icons
from BlissFramework.Utils import PropertyEditor
from BlissFramework.Utils import ConnectionEditor
from BlissFramework.Bricks import LogViewBrick
from BlissFramework import Configuration
from BlissFramework.BaseLayoutItems import ContainerCfg
from BlissFramework.Utils import GUIDisplay

try:
    from HardwareRepository import HardwareRepository
except ImportError:
    logging.getLogger().warning("no Hardware Repository client module could be found")
else:
    print "rework HardwareRepositoryBrowser"
    #from HardwareRepository import HardwareRepositoryBrowser   
 

class HorizontalSpacer(qt.QWidget):
    """Helper class to have a horizontal spacer widget"""
    def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)
        
        h_size = kwargs.get("size", None)
    
        if h_size is not None:
            self.setFixedWidth(h_size)
            self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        else:
            self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)


def _moveToLast(newItem, parentItem):
    """Put newItem as the last child of parentItem"""
    last = parentItem.firstChild()
    
    if last:
        while last.nextSibling():
            last = last.nextSibling()
            
        newItem.moveItem(last)


class MyListView(qt.QListView):
    class ListViewToolTip(qt.QToolTip):
        def __init__(self, parent):
            qt.QToolTip.__init__(self, parent.viewport())

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
        qt.QListView.__init__(self, *args)

        self.__tooltip = MyListView.ListViewToolTip(self)
        self.setVScrollBarMode(qt.QScrollView.Auto)
        self.setSelectionMode(qt.QListView.Single)
        

    def addToolTip(self, item, text):
        self.__tooltip.add(item, text)



class GUIListView(qt.QListView):
    def __init__(self, *args):
        qt.QListView.__init__(self, *args)

        self._presspos = None
        self._mousePressed = False

        self.setSorting(-1) #disable sorting
        self.addColumn("Element")
        self.addColumn("Type")
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setSelectionMode(qt.QListView.Single)


    def eventFilter(self, o, e):
        if o is not None and e is not None:
            if e.type() == qt.QEvent.MouseButtonPress and e.button() == qt.Qt.LeftButton:
                p = qt.QPoint(e.pos())            

                if self.itemAt(p):
                    self._presspos = e.pos()
                    self._mousePressed = True
            elif e.type() == qt.QEvent.MouseButtonRelease:
                self._mousePressed = False
                if e.button() == qt.Qt.RightButton:
                    item = self.itemAt(e.pos())
                    self.emit(qt.PYSIGNAL('contextMenuRequested'), (item, ))
            elif e.type() == qt.QEvent.MouseMove:
                if self._mousePressed:
                    self._mousePressed = False

                    item = self.itemAt(self._presspos)
                    if item and item.dragEnabled():
                        td = qt.QTextDrag(str(item.text(0)), self)
                        td.dragCopy()
                        self.startDrag()

        return qt.QListView.eventFilter(self, o, e)


    def contentsDropEvent(self, event):
        item = self.itemAt(self.contentsToViewport(event.pos()))

        if item and item.dropEnabled() and qt.QTextDrag.canDecode(event):
            t = qt.QString()
            qt.QTextDrag.decode(event, t)
            self.emit(qt.PYSIGNAL("dragdrop"), (str(t), str(item.text(0))))

        event.accept()
      
            
class ToolboxWindow(qt.QWidget):
    def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)
       
        self.setCaption("Toolbox")
        self.bricksTab = {}
        self.bricks = {}
      
        topPanel = qt.QFrame(self)
        self.cmdRefresh = qt.QToolButton(topPanel)
        self.cmdRefresh.setIconSet(qt.QIconSet(Icons.load("reload")))
        qt.QToolTip.add(self.cmdRefresh, "refresh bricks list")
        qt.QHBoxLayout(topPanel)
        topPanel.layout().addWidget(qt.QLabel("Available bricks", topPanel), 0, qt.Qt.AlignLeft)
        topPanel.layout().addWidget(self.cmdRefresh, 0, qt.Qt.AlignRight)
        qt.QObject.connect(self.cmdRefresh, qt.SIGNAL("clicked()"), self.refresh)

        self.bricksToolbox = qt.QToolBox(self)
        
        qt.QVBoxLayout(self, 5, 5)
        self.layout().addWidget(topPanel)
        self.layout().addWidget(self.bricksToolbox)
        

    def addBrickTab(self, name):
        """Add a new brick tab called 'name'"""
        newBricksList = MyListView(self.bricksToolbox)
        newBricksList.addColumn("")
        newBricksList.header().hide()
        
        qt.QObject.connect(newBricksList, qt.SIGNAL("doubleClicked(QListViewItem *)"), self.brickSelected)

        self.bricksToolbox.addItem(newBricksList, name)
        
        self.bricksTab[name] = newBricksList

        return newBricksList
        

    def refresh(self):
        """Refresh bricks window"""
        while self.bricksToolbox.currentItem():
            self.bricksToolbox.removeItem(self.bricksToolbox.currentItem())
       
        self.bricks = {}
        self.bricksTab = {}
            
        self.addBrickTab("General")
        # bricks without category fall into 'General'
        self.bricksTab[""] = self.bricksTab["General"]
       
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
                newBrick = qt.QListViewItem(bricksListWidget, self.brickTextLabel(brickName))
                bricksListWidget.addToolTip(newBrick, description)
                self.bricks[id(newBrick)] = (dirname, brickName)


    def brickSelected(self, item):
        dirname, brickName = self.bricks[id(item)]
        
        self.emit(qt.PYSIGNAL("addBrick"), (brickName, ))
        

class PropertyEditorWindow(qt.QWidget):
    def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)
 
        self.setCaption("Properties")

        self.propertiesTable = PropertyEditor.ConfigurationTable(self)
        self.__property_changed_cb = weakref.WeakKeyDictionary()

        qt.QObject.connect(self.propertiesTable, qt.PYSIGNAL("propertyChanged"), self.propertyChanged)

        qt.QHBoxLayout(self)
        self.layout().addWidget(self.propertiesTable)


    def editProperties(self, propertyBag):
        #print 'setting property bag (%d)' % id(propertyBag)
        self.propertiesTable.setPropertyBag(propertyBag)


    def propertyChanged(self, *args):
        #print "property changed", map(id, self.__property_changed_cb.keys())
        
        try:
            #print 'property changed', args
            #print id(self.propertiesTable.propertyBag)
            cb = self.__property_changed_cb[self.propertiesTable.propertyBag]
            #print cb
        except KeyError, err:
            #print 'key error', err
            return
        else:
            cb(*args)
            
      
    def addProperties(self, propertyBag, property_changed_cb):
        #print 'adding', id(propertyBag)
        self.__property_changed_cb[propertyBag] = property_changed_cb
        #print "properties =", map(id, self.__property_changed_cb.keys())
        self.editProperties(propertyBag)
    

class ToolButton(qt.QToolButton):
    def __init__(self, parent, icon, text=None, callback=None, tooltip=None):
        qt.QToolButton.__init__(self, parent)

        self.setIconSet(qt.QIconSet(Icons.load(icon)))

        if type(text) != types.StringType:
            tooltip = callback
            callback = text
        else:
            self.setTextLabel(text)
            self.setTextPosition(qt.QToolButton.BesideIcon)
            self.setUsesTextLabel(True)

        if callback is not None:
            qt.QObject.connect(self, qt.SIGNAL("clicked()"), callback)

        if tooltip is not None:
            qt.QToolTip.add(self, tooltip)

        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)


class GUIEditorWindow(qt.QWidget):
    def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)

        self.configuration = Configuration.Configuration()
      
        self.setCaption("GUI Editor")

        tb = qt.QHBox(self)
        toolsBox = qt.QGrid(6, tb)
        HorizontalSpacer(tb)
        toolsBox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self.cmdAddWindow = ToolButton(toolsBox, "window_new", self.addWindow, "add a new window (container)")
        self.cmdAddTab=ToolButton(toolsBox, "tab", self.addTab, "add a new tab (container)")
        self.cmdAddHBox=ToolButton(toolsBox, "add_hbox", self.addHBox, "add a new horizontal box (container)")
        self.cmdAddVBox=ToolButton(toolsBox, "add_vbox", self.addVBox, "add a new vertical box (container)")
        self.cmdAddHGroupBox=ToolButton(toolsBox, "hgroupbox", self.addHGroupBox, "add a new horizontal group box (container)")
        self.cmdAddVGroupBox=ToolButton(toolsBox, "vgroupbox", self.addVGroupBox, "add a new vertical group box (container)")
        self.cmdAddHSpacer=ToolButton(toolsBox, "add_hspacer", self.addHSpacer, "add a new horizontal spacer")
        self.cmdAddVSpacer=ToolButton(toolsBox, "add_vspacer", self.addVSpacer, "add a new vertical spacer")
        self.cmdAddHSplitter=ToolButton(toolsBox, "hsplitter", self.addHSplitter, "add a new horizontal splitter (container)")
        self.cmdAddVSplitter=ToolButton(toolsBox, "vsplitter", self.addVSplitter, "add a new vertical splitter (container)")
        self.cmdAddIcon=ToolButton(toolsBox, "icon", self.addIcon, "add a new icon")
        self.cmdAddLabel=ToolButton(toolsBox, "label", self.addLabel, "add a new label")
        treeHandlingBox = qt.QHBox(self)
        treeHandlingBox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self.cmdShowConnections=ToolButton(treeHandlingBox, "connect_creating", self.showConnections, "manage connections between items")
        HorizontalSpacer(treeHandlingBox,size=20)
        self.cmdMoveUp=ToolButton(treeHandlingBox, "Up2", self.moveUp, "move an item up")
        self.cmdMoveDown=ToolButton(treeHandlingBox, "Down2", self.moveDown, "move an item down")
        HorizontalSpacer(treeHandlingBox, size=10)
        self.cmdRemoveItem=ToolButton(treeHandlingBox, "delete_small", self.removeItem, "delete an item")
        HorizontalSpacer(treeHandlingBox)
        
        self.treeLayout = GUIListView(self)
        self.rootElement = qt.QListViewItem(self.treeLayout, "GUI tree", "")
        self.rootElement.setOpen(True)

        qt.QObject.connect(self.treeLayout, qt.SIGNAL('selectionChanged(QListViewItem *)'), self.itemSelected)
        qt.QObject.connect(self.treeLayout, qt.SIGNAL('doubleClicked(QListViewItem *, const QPoint &, int)'), self.itemDoubleClicked)
        qt.QObject.connect(self.treeLayout, qt.SIGNAL('itemRenamed(QListViewItem *, int)'), self.itemRenamed)
        qt.QObject.connect(self.treeLayout, qt.PYSIGNAL('dragdrop'), self.itemDragDropped)
        qt.QObject.connect(self.treeLayout, qt.PYSIGNAL('contextMenuRequested'), self.itemRightClicked)
     
        qt.QVBoxLayout(self, 0, 10)
        self.layout().addWidget(tb)
        self.layout().addWidget(treeHandlingBox)
        self.layout().addWidget(self.treeLayout)
    

    def setConfiguration(self, configuration):
        self.configuration = configuration
        #print 'configuration id is', id(configuration)

        self.treeLayout.blockSignals(True)
        self.treeLayout.takeItem(self.rootElement)
        self.rootElement = qt.QListViewItem(self.treeLayout, "GUI tree", "")
        self.rootElement.setOpen(True)
        
        self.emit(qt.PYSIGNAL('hideProperties'), ())

        def addChildren(children, parentItem):
            parent_name = str(parentItem.text(0))
            parent = self.configuration.findContainer(parent_name)
            
            for child in children:
                #print child["name"]
                if self.configuration.isContainer(child):
                    #print 'is container'
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon=child["type"])
                    addChildren(child["children"], new_list_item)
                    self.configuration.items[child["name"]].updateSlots()
                elif self.configuration.isSpacer(child):
                    #print 'is spacer'
                    new_list_item = self.appendItem(parentItem, child["name"], "spacer", icon=child["type"])
                elif self.configuration.isBrick(child):
                    #print 'is brick'
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon="brick")
                else:
                    #print 'is icon or label'
                    new_list_item = self.appendItem(parentItem, child["name"], child["type"], icon=child["type"])
                self.connectItem(parent, child, new_list_item)

        for window in self.configuration.windows_list:
            parentWindowItem = self.appendItem(self.rootElement, window.name, "window", icon="window_small")
            self.connectItem(None, window, parentWindowItem)
            
            addChildren(window["children"], parentWindowItem)

        self.treeLayout.blockSignals(False)
        self.treeLayout.triggerUpdate()

        self.treeLayout.setSelected(self.rootElement.itemBelow(),1)
        self.emit(qt.PYSIGNAL('showProperties'), ())
        
        
    def showConnections(self):
        connectionEditorWindow = ConnectionEditor.ConnectionEditor(self.configuration)
        w = qt.qApp.desktop().width()
        h = qt.qApp.desktop().height()
        connectionEditorWindow.resize(0.85*w, 0.7*h)

        connectionEditorWindow.exec_loop()


    def updateProperties(self, item_cfg):
        #print 'updating properties : property bag id is', id(item_cfg["properties"])
        self.emit(qt.PYSIGNAL("editProperties"), (item_cfg["properties"], ))
        

    def _getParentWindowName(self, item): 
        while item:
            if str(item.text(1)) == "window":
                return str(item.text(0))
            else:
                item = item.parent()
    
            
    def appendItem(self, parentItem, column1_text, column2_text, icon=None):
        newListItem = qt.QListViewItem(parentItem, column1_text, column2_text)
        _moveToLast(newListItem, parentItem)

        newListItem.setDragEnabled(True)
        newListItem.setDropEnabled(True)
        
        if icon is not None:
            newListItem.setPixmap(0, Icons.load(icon))

        #qt.QObject.disconnect(self.treeLayout, qt.SIGNAL('selectionChanged(QListViewItem *)'), self.itemSelected)
        self.treeLayout.setCurrentItem(newListItem)
        self.treeLayout.ensureItemVisible(newListItem)
        #qt.QObject.connect(self.treeLayout, qt.SIGNAL('selectionChanged(QListViewItem *)'), self.itemSelected)
        
        return newListItem
        

    def removeItem(self):
        currentItem = self.treeLayout.currentItem()

        if currentItem:
            item_parent_name = str(currentItem.parent().text(0))
            
            item_name = str(currentItem.text(0))
            children = currentItem.childCount()

            if children > 0:
                if qt.QMessageBox.warning(self, "Please confirm",
                                          "Are you sure you want to remove %s ?\nRemoving item will remove its %d children." % (item_name, children),
                                          qt.QMessageBox.Yes, qt.QMessageBox.No) == qt.QMessageBox.No:
                    return
            
            if self.configuration.remove(item_name):
                currentItem.parent().takeItem(currentItem)

                self.updateWindowPreview(item_parent_name)
            

    def updateWindowPreview(self, container_name, container_cfg=None, selected_item=""):
        container_item = self.treeLayout.findItem(container_name, 0)
        container_type = str(container_item.text(1))
        window_id = None

        if container_type == "window":
            window_id = id(container_item)
        else:
            # find parent window
            parent = container_item.parent()
            while (parent):
                if str(parent.text(1)) == "window":
                    window_id = id(parent)
                    break
                parent = parent.parent()
         
        if container_type != "window" and container_item.childCount() == 0:
            container_item = container_item.parent()
            container_name = str(container_item.text(0))
            container_cfg = None

        if container_cfg is None:
            container_cfg = self.configuration.findItem(container_name)
            
        def getContainerIds(item):
            containerIds = [id(item)]

            item = item.firstChild()
            
            while item:
                item_type = str(item.text(1))
                
                try:
                    klass = Configuration.Configuration.classes[item_type]
                except KeyError:
                    pass
                else:
                    if issubclass(klass, ContainerCfg):
                        containerIds += getContainerIds(item)
                        
                item = item.nextSibling()

            return containerIds

        container_ids = getContainerIds(container_item)

        #print 'updating', container_cfg["name"], "window id", window_id, "container ids", container_ids
        self.emit(qt.PYSIGNAL("updatePreview"), (container_cfg, window_id, container_ids, selected_item))
 

    def connectItem(self, parent, new_item, new_list_item):
        if self.configuration.isBrick(new_item):
            self.emit(qt.PYSIGNAL("newItem"), (new_item["brick"].propertyBag, new_item["brick"]._propertyChanged))
        else:
            if parent is not None:
                parentref=weakref.ref(parent)
            else:
                parentref=None
            
            def property_changed_cb(property, old_value, new_value, itemref=weakref.ref(new_list_item), parentref=parentref):
                item = itemref()
                if item is None:
                    #print 'NONE !'
                    return

                item_name = str(item.text(0))
                item_type = str(item.text(1))
                #print item_type
                #print Configuration.Configuration.classes
                
                try:
                    klass = Configuration.Configuration.classes[item_type]
                except KeyError:
                    self.updateWindowPreview(item_name)
                else:
                    if issubclass(klass, ContainerCfg):
                        # we should update the container itself,
                        # not just its contents so we trigger an
                        # update of the parent instead
                        if parentref is not None:
                            parent = parentref()
                            if parent is not None:
                                self.updateWindowPreview(parent["name"], parent)
                    else:
                        self.updateWindowPreview(item_name)

                if parentref is not None:
                    parent = parentref()
                    if parent is None:
                        return        
                    parent.childPropertyChanged(item_name, property, old_value, new_value)

            self.emit(qt.PYSIGNAL("newItem"), (new_item["properties"], property_changed_cb))
                  

    def addWindow(self):
        self._addItem(self.rootElement, "window")
    

    def _addItem(self, parentListItem, item_type, *args):
        parent_name = str(parentListItem.text(0))
        parent = self.configuration.findContainer(parent_name)
        new_item = None
        new_list_item = None
        
        try:
            qt.qApp.setOverrideCursor(qt.QCursor(qt.Qt.WaitCursor))

            if item_type == "window":
                new_item = self.configuration.addWindow()

                if type(new_item) == types.StringType:
                    qt.QMessageBox.warning(self, "Cannot add", new_item, qt.QMessageBox.Ok)
                else:
                    new_item["properties"].getProperty("w").setValue(qt.qApp.desktop().width())
                    new_item["properties"].getProperty("h").setValue(qt.qApp.desktop().height())
                    
                    new_list_item = self.appendItem(parentListItem, new_item["name"], "window", icon="window_small")
            elif item_type == "brick":
                brick_type = args[0]
                
                new_item = self.configuration.addBrick(brick_type, parent)

                if type(new_item) == types.StringType:
                    qt.QMessageBox.warning(self, "Cannot add", new_item, qt.QMessageBox.Ok)
                else:
                    brick_name = new_item["name"]
                    brick = new_item["brick"]
                    
                    new_list_item = self.appendItem(parentListItem, brick_name, brick_type, icon="brick")
            elif item_type == "tab":
                new_item = self.configuration.addItem(item_type, parent)

                if type(new_item) == types.StringType:
                    qt.QMessageBox.warning(self, "Cannot add", new_item, qt.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]

                    new_list_item = self.appendItem(parentListItem, item_name, item_type, icon=item_type)
            else:
                item_subtype = args[0]
                
                new_item = self.configuration.addItem(item_subtype, parent)

                if type(new_item) == types.StringType:
                    qt.QMessageBox.warning(self, "Cannot add", new_item, qt.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]
                    
                    new_list_item = self.appendItem(parentListItem, item_name, item_type, icon=item_subtype)
                        
            if type(new_item) != types.StringType and new_item is not None:
                self.connectItem(parent, new_item, new_list_item)
        finally:
            qt.qApp.restoreOverrideCursor()


    def addBrick(self, brick_type):
        self.addItem("brick", brick_type)


    def addContainer(self, container_type, container_subtype=None):
        self.addItem(container_type, container_subtype)

    
    def addItem(self, item_type, item_subtype):
        currentItem = self.treeLayout.currentItem()

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
                qt.QMessageBox.warning(self, "Cannot add %s" % item_type, "Please select a suitable parent container", qt.QMessageBox.Ok)
    
    
                    
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
        item = self.treeLayout.findItem(item_name, 0)

        if item:
            self.treeLayout.setSelected(item, 1)
            self.treeLayout.ensureItemVisible(item)   


    def itemDoubleClicked(self, item, where, column):
        if item:
            item_name = str(item.text(0))
            item_cfg = self.configuration.findItem(item_name)

            if item_cfg:
                item.setRenameEnabled(0, True)
                item.startRename(0)
   

    def itemSelected(self, item):
        if item == self.rootElement:
            return

        item_name = str(item.text(0))
        item_cfg = self.configuration.findItem(item_name)

        self.updateWindowPreview(item_name, item_cfg, selected_item=item_name)
        
        self.updateProperties(item_cfg)
        #self.emit(qt.PYSIGNAL('showPreview'), ())
        self.emit(qt.PYSIGNAL('showProperties'), ())
       

    def itemRenamed(self, item, col):
        item.setRenameEnabled(0,False)
        item_parent_name = str(item.parent().text(0))
        new_item_name = str(item.text(0))

        i = 0
        child = item.parent().firstChild()
        while child and id(child) != id(item):
            child = child.nextSibling()
            i += 1

        old_name = self.configuration.rename(item_parent_name, i, new_item_name)

        if old_name is not None:
            # cancel renaming
            item.setText(0, old_name)
            qt.QMessageBox.warning(self, "Cannot rename item", "New name %s conflicts\nwith another item name." % new_item_name, qt.QMessageBox.Ok)
            

    def itemRightClicked(self, item):
        #print 'right clicked on', item.text(0)
        item_name = str(item.text(0))

        item_cfg = self.configuration.findItem(item_name)

        if self.configuration.isBrick(item_cfg):
            popup_menu = qt.QPopupMenu()

            def _itemRightClicked(id, item_name=item_name):
                item_cfg=self.configuration.reload_brick(item_name)
                item = self.treeLayout.findItem(item_name, 0)
                #print 'emitting newItem'
                self.emit(qt.PYSIGNAL("newItem"), (item_cfg["brick"].propertyBag, item_cfg["brick"]._propertyChanged))
                #print 'itemSelected'
                self.itemSelected(item)
                
            qt.QObject.connect(popup_menu, qt.SIGNAL("activated(int)"), _itemRightClicked)
                
            popup_menu.insertItem("reload brick", 0)
            popup_menu.exec_loop(qt.QCursor.pos())

            #self.treeLayout.setSelected(item, True)


    def itemDragDropped(self, dragged_item_name, dropped_on_item_name):
        #print "item dragged and dropped from %s to %s" % (dragged_item_name, dropped_on_item_name)
        source_item = self.treeLayout.findItem(dragged_item_name, 0)
        target_item = self.treeLayout.findItem(dropped_on_item_name, 0)
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
        if common_ancestor != self.rootElement:
            common_ancestor_name = str(common_ancestor.text(0))
        else:
            common_ancestor_name = ""
        #print "common ancestor =", common_ancestor_name

        # move item in configuration
        if not self.configuration.moveItem(dragged_item_name, dropped_on_item_name):
            self.treeLayout.setSelected(source_item, True)
            self.treeLayout.setCurrentItem(source_item)
            return

        # move item in the GUI tree
        source_item.parent().takeItem(source_item)
        
        target_cfg_item = self.configuration.findItem(dropped_on_item_name)

        if self.configuration.isContainer(target_cfg_item):
            # have to insert in the container
            target_item.insertItem(source_item)
        else:
            target_item.parent().insertItem(source_item)
            source_item.moveItem(target_item)

        #if source_item_parent_name != target_item_parent_name:
        #    self.updateWindowPreview(source_item_parent_name)
        if len(common_ancestor_name):
            self.updateWindowPreview(common_ancestor_name)

        #source_item.setSelected(True)
        self.treeLayout.setSelected(source_item, True)
        self.treeLayout.setCurrentItem(source_item)
        self.treeLayout.ensureItemVisible(source_item)


    def moveItem(self, direction):
        item = self.treeLayout.currentItem()

        if item:
            item_name = str(item.text(0))
            oldParentItem = item.parent()
            
            if direction == "up":
                newParent = self.configuration.moveUp(item_name)

                if newParent is not None:
                    newParentItem = self.treeLayout.findItem(newParent, 0)

                    if newParentItem == oldParentItem:
                        itemAbove = item.itemAbove()
                        while (itemAbove.parent() != newParentItem):
                            itemAbove=itemAbove.itemAbove()
                        itemAbove.moveItem(item)
                    else:
                        oldParentItem.takeItem(item)
                        newParentItem.insertItem(item)
                        item.moveItem(oldParentItem.itemAbove())
            else:
                newParent = self.configuration.moveDown(item_name)
            
                if newParent is not None:
                    newParentItem = self.treeLayout.findItem(newParent, 0)

                    if newParentItem == oldParentItem:
                        item.moveItem(item.nextSibling())
                    else:
                        oldParentItem.takeItem(item)
                        newParentItem.insertItem(item)

            if newParent is not None:
                 self.updateWindowPreview(newParent)
                 
            self.treeLayout.ensureItemVisible(item)
            item.setSelected(True)
            #self.itemSelected(item)
                

    def moveUp(self):
        self.moveItem("up")

        
    def moveDown(self):
        self.moveItem("down")
    

class GUIPreviewWindow(qt.QWidget):
   def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)
       
        self.setCaption("GUI Preview")

        self.windowPreviewBox = qt.QVGroupBox("Window preview", self)
        self.windowPreview = GUIDisplay.WindowDisplayWidget(self.windowPreviewBox)

        qt.QObject.connect(self.windowPreview, qt.PYSIGNAL("itemClicked"), self.previewItemClicked)

        qt.QVBoxLayout(self)
        self.layout().addWidget(self.windowPreviewBox)

        # set arbitrary default size
        self.resize(640,480)


   def renew(self):
       self.windowPreviewBox.close(True)

       self.windowPreviewBox = qt.QVGroupBox("Window preview", self)
       self.windowPreview = GUIDisplay.WindowDisplayWidget(self.windowPreviewBox)

       qt.QObject.connect(self.windowPreview, qt.PYSIGNAL("itemClicked"), self.previewItemClicked)

       self.layout().addWidget(self.windowPreviewBox)

       self.windowPreviewBox.show()
       

   def previewItemClicked(self, item_name):
       self.emit(qt.PYSIGNAL("previewItemClicked"), (item_name, ))


   def drawWindow(self, container_cfg, window_id, container_ids, selected_item):
       #print container_cfg, type(container_cfg), container_ids
       if container_cfg["type"] == "window":
           caption = container_cfg["properties"]["caption"]
           s = caption and " - %s" % caption or ""
           self.windowPreviewBox.setTitle("Window preview: %s%s" % (container_cfg["name"], s))
       
       self.windowPreview.updatePreview(container_cfg, window_id, container_ids, selected_item)


class HWRWindow(qt.QWidget):
    def __init__(self, *args, **kwargs):
        qt.QWidget.__init__(self, *args)

        self.setCaption("Hardware Repository browser")
        
        tb = qt.QHBox(self)
        self.cmdRefresh = qt.QToolButton(tb)
        self.cmdRefresh.setIconSet(qt.QIconSet(Icons.load("reload")))
        qt.QToolTip.add(self.cmdRefresh, "refresh HWR objects tree")
        self.cmdClose = qt.QToolButton(tb)
        self.cmdClose.setIconSet(qt.QIconSet(Icons.load("button_cancel")))
        qt.QToolTip.add(self.cmdClose, "close HWR browser")
        HorizontalSpacer(tb)
        tb.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)

        qt.QObject.connect(self.cmdRefresh, qt.SIGNAL("clicked()"), self.refresh)
        qt.QObject.connect(self.cmdClose, qt.SIGNAL("clicked()"), self.close)

        qt.QVBoxLayout(self)
        self.layout().addWidget(tb)
        self.add_hwr_browser()
        

    def add_hwr_browser(self):
        print "add_hwr_browser - rework to be compatible with qt3/qt4"

        return 
        try:
            #_hwr_widget = HardwareRepositoryBrowser.HardwareRepositoryBrowser
            print "add_hwr_browser - rework"
        except AttributeError:
            logging.getLogger().error("No Hardware Repository client found")
        else:
            self.hwr_widget = _hwr_widget(self)
            self.layout().addWidget(self.hwr_widget)
            self.hwr_widget.show()
            
                
    def refresh(self):
        self.hwr_widget.close(True)
        self.add_hwr_browser()



class GUIBuilder(qt.QMainWindow):
    def __init__(self, *args, **kwargs):
        qt.QMainWindow.__init__(self, *args)

        self.filename = None
        
        self.setCaption("GUI Builder")

        toolbar = qt.QToolBar(self)
        self.cmdNew = ToolButton(toolbar, "new", self.newClicked, "create a new GUI")
        self.cmdOpen = ToolButton(toolbar, "open", self.openClicked, "open an existing GUI file")
        self.cmdSave = ToolButton(toolbar, "save", self.saveClicked, "save current GUI")
        HorizontalSpacer(toolbar, size=20)
        self.cmdLaunchGUI = ToolButton(toolbar, "launch", self.launchGUIClicked, "launch GUI (as a separate process)")
        HorizontalSpacer(toolbar, size=20)
        self.cmdViewPropertyEditor = ToolButton(toolbar, "Draw", self.showProperties, "show properties window")
        self.cmdViewGuiPreview = ToolButton(toolbar, "window_preview", self.showGuiPreview, "show GUI preview")
        self.cmdViewLog = ToolButton(toolbar, "Inform", self.showLog, "show log messages window")
        self.cmdViewHWR = ToolButton(toolbar, "view_tree", self.showHWR, "show Hardware Repository")
        HorizontalSpacer(toolbar)
        
        vbox = qt.QVBox(self)
        self.setCentralWidget(vbox) #vsplitter)
         
        hbox = qt.QSplitter(qt.Qt.Horizontal, vbox)
        self.statusbar = self.statusBar()
        self.guiEditorWindow = GUIEditorWindow(hbox)
        self.toolboxWindow = ToolboxWindow(hbox)
        
        self.logWindow = LogViewBrick.LogViewBrick(None)
        self.logWindow.setCaption("Log window")
        sw = qt.QApplication.desktop().screen().width()
        sh = qt.QApplication.desktop().screen().height()
        self.logWindow.resize(qt.QSize(sw*0.8, sh*0.2))
        self.propertyEditorWindow = PropertyEditorWindow(None)
        self.guiPreviewWindow = GUIPreviewWindow(None)
        self.hwrWindow = HWRWindow(None)

        self.configuration = self.guiEditorWindow.configuration
        
        #
        # build File menu
        #
        fileMenu = qt.QPopupMenu(self)
        fileMenu.insertItem('New', self.newClicked)
        fileMenu.insertSeparator()
        fileMenu.insertItem('Open', self.openClicked)
        fileMenu.insertSeparator()
        fileMenu.insertItem('Save', self.saveClicked)
        fileMenu.insertItem('Save as', self.saveAsClicked)
        fileMenu.insertSeparator()
        fileMenu.insertItem('Quit', self.quitClicked)
        viewMenu = qt.QPopupMenu(self)
        viewMenu.insertItem('Property Editor', self.showProperties)
        viewMenu.insertItem('GUI Preview', self.showGuiPreview)
        viewMenu.insertItem('Log window', self.showLog)
        
        #
        # build menu bar
        #
        mainMenu = self.menuBar()
        mainMenu.insertItem('File', fileMenu)
        mainMenu.insertItem('View', viewMenu)

        #
        # connections
        #
        qt.QObject.connect(self.toolboxWindow, qt.PYSIGNAL("addBrick"), self.guiEditorWindow.addBrick)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("editProperties"), self.propertyEditorWindow.editProperties)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("newItem"), self.propertyEditorWindow.addProperties)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("updatePreview"), self.guiPreviewWindow.drawWindow)
        qt.QObject.connect(self.guiPreviewWindow, qt.PYSIGNAL("previewItemClicked"), self.guiEditorWindow.selectItem)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("showProperties"), self.showProperties)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("hideProperties"), self.hideProperties)
        qt.QObject.connect(self.guiEditorWindow, qt.PYSIGNAL("showPreview"), self.showGuiPreview)

        #
        # finish GUI
        #
        self.toolboxWindow.refresh()

        self.guiPreviewWindow.show()
        

    def newClicked(self, filename = None):
        self.configuration = Configuration.Configuration()
        self.filename = filename

        if self.filename:
            self.setCaption("GUI Builder - %s" % filename)
        else:
            self.setCaption("GUI Builder")

        self.guiPreviewWindow.renew()
        self.guiEditorWindow.setConfiguration(self.configuration)
        

    def openClicked(self):
        filename = str(qt.QFileDialog.getOpenFileName(os.environ["HOME"],
                                                      "GUI file (*.gui)",
                                                      self,
                                                      "Save file",
                                                      "Choose a GUI file to open"))

        if len(filename) > 0:
            try:
                f = open(filename)
            except:
                logging.getLogger().exception("Cannot open file %s", filename)
                qt.QMessageBox.warning(self, "Error", "Could not open file %s !" % filename, qt.QMessageBox.Ok)
            else:
                try:
                    raw_config = eval(f.read())

                    try:
                        new_config = Configuration.Configuration(raw_config)
                    except:
                        logging.getLogger().exception("Cannot read configuration from file %s", filename)
                        qt.QMessageBox.warning(self, "Error", "Could not read configuration\nfrom file %s" % filename, qt.QMessageBox.Ok)
                    else:
                        self.filename = filename
                        self.configuration = new_config
                        self.setCaption("GUI Builder - %s" % filename)
                        self.guiPreviewWindow.renew()
                        self.guiEditorWindow.setConfiguration(new_config)
                finally:
                    f.close()
                

    def saveClicked(self):
        try:
            qt.qApp.setOverrideCursor(qt.QCursor(qt.Qt.WaitCursor))
            
            if self.filename is not None:
                if os.path.exists(self.filename):
                    should_create_startup_script=False
                else:
                    should_create_startup_script=True
                    
                if self.configuration.save(self.filename):
                    self.setCaption("GUI Builder - %s" % self.filename)
                    qt.qApp.restoreOverrideCursor()
                    qt.QMessageBox.information(self, "Success", "Configuration have been saved successfully to\n%s" % self.filename, qt.QMessageBox.Ok)

                    if should_create_startup_script:
                        if qt.QMessageBox.question(self, "Launch script",
                                                   "Do you want to create a startup script for the new GUI ?",
                                                   qt.QMessageBox.Yes, qt.QMessageBox.No) == qt.QMessageBox.Yes:
                            try:
                                hwr_server = HardwareRepository.HardwareRepository().serverAddress
                            except:
                                hwr_server = ""
                            else:
                                pid = subprocess.Popen("newGUI --just-script %s %s" % (self.filename, hwr_server), shell=True).pid
                    return True
                else:
                    qt.qApp.restoreOverrideCursor()
                    qt.QMessageBox.warning(self, "Error", "Could not save configuration to file %s !" % self.filename, qt.QMessageBox.Ok)

                    return False
            else:
                qt.qApp.restoreOverrideCursor()
                self.saveAsClicked()
        finally:
            qt.qApp.restoreOverrideCursor()


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
            if qt.QMessageBox.warning(self, "Please confirm",
                                      "Are you sure you want to quit ?\nYour changes will be lost.",
                                      qt.QMessageBox.Yes, qt.QMessageBox.No) == qt.QMessageBox.No:
                return
            
        self.close()


    def showProperties(self):
        self.propertyEditorWindow.raiseW()
        self.propertyEditorWindow.show()


    def hideProperties(self):
        self.propertyEditorWindow.close()


    def showGuiPreview(self):
        self.guiPreviewWindow.raiseW()
        self.guiPreviewWindow.show()


    def showLog(self):
        self.logWindow.raiseW()
        self.logWindow.show()


    def showHWR(self):
        self.hwrWindow.raiseW()
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
    app = qt.QApplication([])

    mainwin = GUIBuilder()

    app.setMainWidget(mainwin)

    mainwin.show()

    app.exec_loop()


