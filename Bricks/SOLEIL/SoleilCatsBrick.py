import string
import logging
import time
import qt
import traceback
import sys
import sample_changer.GenericSampleChanger as SampleChanger


from BlissFramework import BaseComponents 
from widgets.catswidget import CatsWidget


__category__ = "SOLEIL"

    
class SoleilCatsBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)
        
        self.addProperty("hwobj", "string", "")
        
        self.widget = CatsWidget(self)
        qt.QHBoxLayout(self)
        self.layout().addWidget(self.widget)
        
        qt.QObject.connect(self.widget.btLoadSample,qt.SIGNAL('clicked()'),self._loadSample)        
        #qt.QObject.connect(self.widget.btLoadSample,qt.SIGNAL('clicked()'),self.onMenuLoad)        
        qt.QObject.connect(self.widget.btUnloadSample,qt.SIGNAL('clicked()'),self._unloadSample)
        qt.QObject.connect(self.widget.btAbort,qt.SIGNAL('clicked()'),self._abort)                     
                
        self.device=None
        self.phase = "Unknown"
        self.state = "Unknown"
        
        self.list = self.widget.lvSC   
        #self.list.setSelectionMode(QListView::NoSelection)
        qt.QObject.connect(self.list,qt.SIGNAL('selectionChanged()'),self.onListSelected)
        qt.QObject.connect(self.list,qt.SIGNAL('contextMenuRequested(QListViewItem*,const QPoint&,int)'),self.onListPopupMenu)
        
        self.widget.ckShowEmptySlots.setChecked(False)
        qt.QObject.connect(self.widget.ckShowEmptySlots,qt.SIGNAL('clicked()'),self.onShowEmptySlots)

        self._clearTable()
        
    def propertyChanged(self, property, oldValue, newValue):
        logging.getLogger("user_level_log").info("Property Changed: " + str(property) + " = " + str(newValue))
        if property == 'hwobj':
            if self.device is not None:
                self.disconnect(self.device, self.device.STATE_CHANGED_EVENT, self.onStateChanged)
                self.disconnect(self.device, self.device.STATUS_CHANGED_EVENT, self.onSatusChanged)
                self.disconnect(self.device, self.device.INFO_CHANGED_EVENT, self.onInfoChanged)
                self.disconnect(self.device, self.device.LOADED_SAMPLE_CHANGED_EVENT, self.onLoadedSampleChanged)
                self.disconnect(self.device, self.device.SELECTION_CHANGED_EVENT, self.onSelectionChanged)
                self.disconnect(self.device, self.device.TASK_FINISHED_EVENT, self.onTaskFinished)
                
            self.device = self.getHardwareObject(newValue)                                    

            if self.device is not None:
                self.connect(self.device, self.device.STATE_CHANGED_EVENT, self.onStateChanged)
                self.connect(self.device, self.device.STATUS_CHANGED_EVENT, self.onStatusChanged)
                self.connect(self.device, self.device.INFO_CHANGED_EVENT, self.onInfoChanged)
                self.connect(self.device, self.device.LOADED_SAMPLE_CHANGED_EVENT, self.onLoadedSampleChanged)
                self.connect(self.device, self.device.SELECTION_CHANGED_EVENT, self.onSelectionChanged)
                self.connect(self.device, self.device.TASK_FINISHED_EVENT, self.onTaskFinished)
                self.onStateChanged(self.device.getState(),None)
                self.onStatusChanged(self.device.getStatus())
                self._createTable()       
            else:
                self.onStateChanged(SampleChanger.SampleChangerState.Unknown,None)
                self.onStatusChanged("")
                self._clearTable()
   
    def onStateChanged(self, state,former):
        former_state=self.state
        self.state=string.lower(str(state))
        logging.getLogger("user_level_log").info( "State = " + str(state) )
        self._updateButtons()        
        self.emit(qt.PYSIGNAL("stateChanged"), (state, ))
        
    def onStatusChanged(self, status):
        self.widget.txtState.setText(str(status))
        
    def onInfoChanged(self):
        if self._changedStructure(self.root):
            self._createTable()
        else:                        
            self._updateTable()
        self._updateButtons() 

    def onLoadedSampleChanged(self,sample):
        self._updateButtons()

    def onSelectionChanged(self):
        self._updateButtons()        
        #self.list.repaint()
        self.list.repaintContents()

    def onTaskFinished(self,task,ret,exception):
        pass

    def onShowEmptySlots(self):        
        #self._createTable()
        if self.root is not None:
            self._checkVisibility(self.root,self.widget.ckShowEmptySlots.isOn())            
            
    def onListSelected(self):
        #import pdb; pdb.set_trace()
        item = self.list.selectedItem()
        
        if item is None:
            pass 
        elif item==self.root:
            pass            
        else:
            element = self.device.getComponentByAddress(item.text(0))
            self.onMenuSelect()

    def onListPopupMenu(self, item, point, col):
        component = self._getSelectedComponent()
        ready = (self.device.getState() == SampleChanger.SampleChangerState.Ready)
        if col==0 and (component is not None):
            menu = qt.QPopupMenu(self.list,"Popup Menu")
            font = menu.font()
            font.setPointSize(11)
            menu.setFont(font)            
            if component == self.device:
                menu.setItemEnabled(menu.insertItem( "Set ID",  self.onMenuSetID),component.isTransient())
            menu.setItemEnabled(menu.insertItem( "Scan",  self.onMenuScan),component.isScannable())            
            menu.popup(point) 
            #menu.exec_(self.view.mapToGlobal(point))
             
    def onMenuSetID(self):
        try:  
            (text,ok) = qt.QInputDialog.getText("ID", "Enter new  ID:", qt.QLineEdit.Normal,self._getElementID(self.device).strip(),  self )
            if ok:
                self.device.setToken(str(text).strip())
                self._updateTable()
        except:
            qt.QMessageBox.warning ( self, "Error",str(sys.exc_info()[1]))
        
        
    def onMenuScan(self):
        #import pdb; pdb.set_trace()
        try:
            component = self._getSelectedComponent()
            if component is not None:
                if component.isScannable():
                    self.device.scan(component,recursive=True,wait=False)
                else:
                    qt.QMessageBox.information( self, "Scan","Component is not scannable")
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
                
    def onMenuLoad(self):
        try:
            component = self._getSelectedSample()
            if component is not None:
                self.device.load(component,wait=False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def onMenuUnload(self):
        try:
            component = self._getSelectedSample()
            if component is not None:
                self.device.unload(component,wait=False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))
    
    def onMenuSelect(self):
        try:
            component = self._getSelectedComponent()
            if component is not None:
                self.device.select(component,wait=False)
        except:
            qt.QMessageBox.warning( self, "Error",str(sys.exc_info()[1]))

    def _getSelectedComponent(self):
        item = self.list.selectedItem()
        if (item is not None):
            if item==self.root:
                return self.device
            element = self.device.getComponentByAddress(item.text(0))
            return element
        
    def _getSelectedSample(self):
        c=self._getSelectedComponent()
        if (c is not None) and (c != self.device) and (c.isLeaf()):
            return c

    def _updateButtons(self):
        sample_selected = (self._getSelectedSample() is not None)
        item = self.list.selectedItem()
        if item is not None:
            element = self.device.getComponentByAddress(item.text(0))
            element
        if self.device is None or not self.device.isReady():
            self.widget.btLoadSample.setEnabled(False) 
            self.widget.btUnloadSample.setEnabled(False)
            self.widget.btAbort.setEnabled(False)
        else:
            charging = (self.device.getState() == SampleChanger.SampleChangerState.Charging)
            ready = (self.device.getState() == SampleChanger.SampleChangerState.Ready)
            standby = (self.device.getState() == SampleChanger.SampleChangerState.StandBy)
            moving = (self.device.getState() in [SampleChanger.SampleChangerState.Moving, SampleChanger.SampleChangerState.Loading, SampleChanger.SampleChangerState.Unloading])
            self.widget.btLoadSample.setEnabled(ready and not charging and (self._getSelectedSample() is not None)) 
            self.widget.btUnloadSample.setEnabled(ready and not charging and self.device.hasLoadedSample())
        self.widget.btAbort.setEnabled(self.device is not None and not self.device.isReady())

    def _abort(self):
        logging.getLogger("user_level_log").info("Abort")
        if self.device is not None:
            self.device.abort()
            
    def _loadSample(self):
        if self.device is not None:
            self.device.load(wait=False)
            
    def _unloadSample(self):
        if self.device is not None:
            self.device.unload(wait=False)

    def _clearTable(self):
        self.root=None
        while self.list.columns() > 0:
            self.list.removeColumn(0)

    def _addElement(self,parent,element):  
        #if not self._show_empty_slots and not element.isPresent():
        #    return
        class MyListViewItem(qt.QListViewItem):    
            def paintCell (self, painter, color_group, column, width, align):        
                if column == 0:     
                    element = self.device.getComponentByAddress(self.text(0))
                    if (element.isSelected()):
                        font = painter.font()
                        font.setBold(True)
                        painter.setFont(font)
                qt.QListViewItem.paintCell(self,painter,color_group,column,width,align)
        
        args = self._getElementProperties(element)
        item = MyListViewItem(parent, element.getAddress(), self._getElementStatus(element), self._getElementID(element), *args)
        item.device=self.device
        if  not element.isLeaf():
            for e in reversed(element.getComponents()):
                self._addElement(item,e)
    
    def _getElementProperties(self,e):
        args = []
        if e.isLeaf():
            for prop_name in self.device.getSampleProperties():
                prop = e.getProperty(str(prop_name))
                if prop is None: 
                    prop = ""
                args.append(str(prop)) 
        return args
        
    def _getElementStatus(self,e):
        if e.isLeaf():
            if e.isLoaded():
                return "Loaded"
            if e.hasBeenLoaded():
                return "Used"
        #if e.isScanned():
        #    return "Scanned"
        if e.isPresent():
            return "Present"            
        return ""
                
    def _getElementID(self,e):
        if e == self.device:
            if self.device.getToken() is not None:
                return self.device.getToken() 
        else:
            if e.getID() is not None:
                return  e.getID()
        return ""
    
    def _getRootID(self):
        if self.device.getToken() is not None:
            return self.device.getToken()
        return ""           
        
    def _createTable(self):
        self._clearTable()        
        if  self.device is not None:            
            #self._show_empty_slots = self.widget.ckShowEmptySlots.isOn()
            self.list.setRootIsDecorated(True) 
            self.list.setSorting(-1)
            self.list.addColumn( "Element" , 150);
            self.list.addColumn( "Status" , 60);
            self.list.addColumn( "ID" , 60);
            for prop in self.device.getSampleProperties():
                self.list.addColumn(str(prop),60)
            #How can we align the header?
            #for i in range (1,self.list.columns()):
            #    self.list.setColumnAlignment(i,qt.Qt.AlignHCenter)
             
            #self.list.setColumnWidthMode (0,qt.QListView.Maximum) 
            root_name = self.device.getAddress()
            self.root = qt.QListViewItem( self.list,root_name,"",self._getRootID())
            for element in reversed(self.device.getComponents()):
                self._addElement(self.root,element)
                                
            self.root.setOpen(True)
            self._checkVisibility(self.root,self.widget.ckShowEmptySlots.isOn())

    def _checkVisibility(self,item, show_empty_slots):    
        if item!=self.root:
            element = self.device.getComponentByAddress(item.text(0))
            if element is not None:           
                if element.isLeaf():
                    item.setVisible (show_empty_slots or element.isPresent())
                else:
                    item.setVisible ( show_empty_slots or not element.isEmpty())
        child = item.firstChild()
        while child is not None:
            self._checkVisibility(child,show_empty_slots)
            child = child.nextSibling()             
        
            #for c in element.getComponents():
            #    self._checkVisibility(element,show_empty_slots)
                    
    def _updateItem(self,item):    
        if item is not None:
            if item==self.root:
                item.setText(2,self._getRootID())                
            else:
                element = self.device.getComponentByAddress(item.text(0))
                if element is not None:               
                    item.setText(1,self._getElementStatus(element))
                    item.setText(2,self._getElementID(element))      
                    props = self._getElementProperties(element)
                    i=3
                    for p in props:
                        item.setText(i,p)
                        i=i+1
            child = item.firstChild()
            while child is not None:
                self._updateItem(child)
                child = child.nextSibling()             
    
    def _getChildItem(self, item, address):
        child = item.firstChild()
        while child is not None:
            if child.text(0)==address:
                return True
            child = child.nextSibling()             

    def _changedStructure(self,item):    
        if item is not None:
            if item==self.root:
                item.setText(2,self._getRootID())
            else:                
                element = self.device.getComponentByAddress(item.text(0))
                if element is None:
                    return True
                if not element.isLeaf():
                    for c in element.getComponents():
                        if self._getChildItem(item,c.getAddress()) is None:
                            return True 
            child = item.firstChild()
            while child is not None:
                if self._changedStructure(child):
                    return True
                child = child.nextSibling()
            
    def _updateTable(self):
        if self.root is not None:                                                      
            self._updateItem(self.root)            
            self._checkVisibility(self.root,self.widget.ckShowEmptySlots.isOn())

