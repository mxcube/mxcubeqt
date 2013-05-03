from qt import *
import qttable
import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import os
import copy
import DataCollectBrick2
import DataCollectParametersBrick
import types
import pprint
import gevent
import gevent.event
import time

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

queue_external_feeding_list = list()
external_event = gevent.event.Event()
server = None

# Simple XMPRPC server for handling exiernal requests for the workflow
# Added by Olof (2013/04/24)
class MxCuBEXMLRPCServer(SimpleXMLRPCServer):

    def __init__(self, parent, addr, **params):
        SimpleXMLRPCServer.__init__(self, addr, **params)
        self.parent = parent 
        self.register_introspection_functions()
        self.register_function(self.load_queue)
        self.register_function(self.start_queue)
        self.register_function(self.queue_status)
        self.register_function(self.grid_info)
        # Added new xmlrpc methods for workflow logging and html page (Olof 2013/04/24)
        self.register_function(self.log_message)
        self.register_function(self.new_html_page)

    def load_queue(self, data_collect_list):
        queue_external_feeding_list.append(("load", data_collect_list))
        external_event.set()
        return True

    def queue_status(self):
        result = gevent.event.AsyncResult()
        queue_external_feeding_list.append(("status", result))
        external_event.set()
        return result.get()
 
    def start_queue(self):
        queue_external_feeding_list.append(("start", None))
        external_event.set()
        return True

    def grid_info(self):
        result = gevent.event.AsyncResult()
        queue_external_feeding_list.append(("grid_info", result))
        external_event.set()
        return result.get()

    def log_message(self, message, log_level=logging.INFO):
        logging.getLogger().log(log_level, message)
        return True

    def new_html_page(self, html_path, imagePrefix, lRunN):
        self.parent.emit(PYSIGNAL('new_html'), (html_path, imagePrefix, int(lRunN)))
        return True


__category__ = 'mxCuBE'


"""
optionalDoubleValidator
    Description: 
    Type       : class (qt.QDoubleValidator)
"""
class optionalDoubleValidator(QDoubleValidator):
    def validate(self,string,pos):
        if len(str(string)):
            return QDoubleValidator.validate(self,string,pos)
        return QDoubleValidator.validate(self,"0.0",pos)

"""
optionalIntValidator
    Description: 
    Type       : class (qt.QIntValidator)
"""
class optionalIntValidator(QIntValidator):
    def validate(self,string,pos):
        if len(str(string)):
            return QIntValidator.validate(self,string,pos)
        return QIntValidator.validate(self,"1",pos)

"""
directoryValidator
    Description: 
    Type       : class (qt.QIntValidator)
    API        : setSpecificValidator
"""
class directoryValidator(QIntValidator):
    def setSpecificValidator(self,prop):
        self.proposalCode=prop[0]
        self.proposalNumber=prop[1]
    def validate(self,string,pos):
        try:
            prop_code=self.proposalCode
            prop_number=self.proposalNumber
        except AttributeError:
            valid=False
        else:
            dirs=str(string).split(os.path.sep)
            try:
                dirs.index("%s%s" % (self.proposalCode,self.proposalNumber))
            except ValueError:
                valid=False
            else:
                valid=True
        if valid:
            return QIntValidator.validate(self,"0",pos)
        return QIntValidator.validate(self,"a",pos)

# PK 18/01/11 - allow for other combo items in table

class AbstractComboItem(qttable.QComboTableItem):
    def setQueueItemValue(self,value):
        try:
            value_index=self.VALUES.index(value)
        except ValueError:
            pass
        else:
            self.setCurrentItem(value_index)
    def getQueueItemValue(self):
        return self.VALUES[self.currentItem()]

# FIXME! These hardware configuration properties should be discovered
# by querying the hardware server
    
class comboItem(AbstractComboItem):
    VALUES=["Software binned","Unbinned","Hardware binned", "disable"]
    
class axisComboItem(AbstractComboItem):
    VALUES=["Phi", "Omega"]
    
class spacegroupComboItem(AbstractComboItem):
    VALUES=DataCollectParametersBrick.XTAL_SPACEGROUPS
                 
"""
centredStatusItem
    Description: 
    Type       : class (qttable.QCheckTableItem)
    API        : setQueueItemValue
                 getQueueItemValue
"""
class centredStatusItem(qttable.QCheckTableItem):
    def setQueueItemValue(self,value):
        self.centredStatus=value
        try:
            accepted=self.centredStatus["accepted"]
        except:
            accepted=False
        self.setEnabled(accepted)
        self.setChecked(accepted)
    def getQueueItemValue(self):
        if self.isChecked():
            self.centredStatus["goto"]=True
            return self.centredStatus
        return None

"""
editItem
    Description: 
    Type       : class (qttable.QTableItem)
    API        : setQueueItemValue
                 getQueueItemValue
"""
class editItem(qttable.QTableItem):
    def setQueueItemValue(self,value):
        try:
            float(value)
        except:
            self.setText(str(value))
        else:
            if str(value).isdigit():
              self.setText(str(value))
            else:
              self.setText("%0.4f" % float(value))
    def getQueueItemValue(self):
        return str(self.text())
    def setContentFromEditor(self,w):
        qttable.QTableItem.setContentFromEditor(self,w)
        if self.myLineEdit is not None and self.myLineEdit.validator() is not None:
            if self.myLineEdit.hasAcceptableInput():
                self.myLineEdit.setPaletteBackgroundColor(DataCollectBrick2.DataCollectBrick2.PARAMETER_STATE["OK"])
    def createEditor(self):
        if not self.isEnabled():
            self.myLineEdit=None
            return None
        self.myLineEdit=qttable.QTableItem.createEditor(self)
        try:
            self.myLineEdit.setValidator(self.myValidator)
        except AttributeError:
            pass
        else:
            self.myLineEdit.setAlignment(self.myAlign)
        QObject.connect(self.myLineEdit,SIGNAL('textChanged ( const QString & )'),self.lineEditChanged)
        try:
            QObject.connect(self.myLineEdit,PYSIGNAL('inputValid'),self.processValidFun)
        except AttributeError:
            pass
        return self.myLineEdit
    def setValidator(self,validator):
        self.myAlign=QWidget.AlignRight
        self.myValidator=validator
    def lineEditChanged(self,text):
        valid=None
        if self.myLineEdit.validator() is not None:
            if self.myLineEdit.hasAcceptableInput():
                valid=True
                self.myLineEdit.setPaletteBackgroundColor(DataCollectBrick2.DataCollectBrick2.PARAMETER_STATE["WARNING"])
            else:
                valid=False
                self.myLineEdit.setPaletteBackgroundColor(DataCollectBrick2.DataCollectBrick2.PARAMETER_STATE["INVALID"])
        if valid is not None:
            self.myLineEdit.emit(PYSIGNAL("inputValid"),(self,valid,))
    def connectInputValid(self,process_valid_fun):
        self.processValidFun=process_valid_fun

"""
directoryItem
    Description: 
    Type       : class (editItem)
"""
class directoryItem(editItem):
    pass

"""
boolEditItem
    Description: 
    Type       : class (editItem)
"""
class boolEditItem(qttable.QCheckTableItem):
    def setQueueItemValue(self,value):
        if type(value) is tuple:
            self.setChecked(value[0]=='True')
        elif type(value) is bool:
            self.setChecked(value)
        elif type(value) is str:
            try:
                self.setChecked(value == 'True')
            except Exception,msg:
                logging.getLogger().error("Unable to set boolean value in queue parameters %s" % msg)
                self.setChecked(False)
            
    def getQueueItemValue(self):
        text=str(self.isChecked())
        return text
    def setValidator(self,validator):
        self.myAlign=QWidget.AlignRight
        self.myValidator=validator
    def connectInputValid(self,process_valid_fun):
        self.processValidFun=process_valid_fun

"""
HorizontalSpacer
    Description: Widget that expands itself horizontally.
    Type       : class (qt.QWidget)
"""
class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

"""
DataCollectQueueBrick
    Type       : class (BlissWidget)
    (please see file and method headers for details)
"""
class DataCollectQueueBrick(BlissWidget):
    DETECTOR_MODE_ITEMS = ( "software", "unbinned", "hardware" )
    
    DEFAULT_PARAMETER_LIST=[{'comments': 'Image created for EDNA charcterisation', \
              'dark': 1, 'phi': 0.0, \
              'exposure_time': 1.0, \
              'start_image_number': 1, 'number_of_images': 1, \
               'overlap': -0.0, 'osc_start': 0.0, \
               'osc_range': 1.0, 'number_passes': 1,\
                'write_input_files': 0, \
                'gshg': 2.0, 'gsvg': 2.0, \
                'tth': 0.0, 'kap': 0.0, 'kth': 0.0, \
                'wavelength': 1.0, \
                'directory': None ,'prefix': 'edna_', 'run_number': 1, \
                 'sub_directory': 'edna', 'suffix':'mccd', \
                'resolution': 1.0, 'dezinger': 1}]

    SCAN_AXIS_FIXED = True
    DETECTOR_MODE_ITEMS = ( "software", "unbinned", "hardware", "disable" )
    """ Fields      index    Heading        editable    dunno                            type                width """
    PARAMETERS = {
        "run_number":       (0, "Run",          None, [editItem,qttable.QTableItem.Always], (QIntValidator,0),          40),\
        "prefix":           (1, "Prefix",       None, [editItem,qttable.QTableItem.Always], None,                       70),\
        "osc_start":        (2, "Start",        None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,),        40),\
        "osc_range":        (3, "Range",        None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,),        45),\
        "number_images":    (4, "#images",      None, [editItem,qttable.QTableItem.Always], (QIntValidator,1),          55),\
        "overlap":          (5, "Overlap",      None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,),        55),\
        "exposure_time":    (6, "Time",         None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     40),\
        "number_passes":    (7, "Passes",       None, [editItem,qttable.QTableItem.Always], (QIntValidator,1),          50),\
        "transmission":     (8, "Trans",        None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     50),\
        "resolution":       (9, "Reso",         None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     50),\
        "energy":           (10, "Energy",      None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     50),\
        "detector_mode":    (11, "Det.Bin",     None, [comboItem,None],                     None,                       65),\
        "first_image":      (12, "From img",    None, [editItem,qttable.QTableItem.Always], (QIntValidator,0),          60),\
        "comments":         (13, "Comments",    None, [editItem,qttable.QTableItem.Always], None,                      310),\
        "directory":        (14, "Directory",   None, [directoryItem,qttable.QTableItem.Always], [directoryValidator,None,None],310),\
        "processing":       (15, "Process",     None, [boolEditItem,QString("")],(optionalIntValidator,1),              50),\
        "residues":         (16, "residues",    None, [editItem,qttable.QTableItem.Always], (QIntValidator,1),          50),\
        "anomalous":        (17, "anomal",      None, [boolEditItem,QString("")],(optionalIntValidator,1),              50),\
        "spacegroup":       (18, "Xtal.SG",     None, [spacegroupComboItem,None], None,    50),\
        "cell":             (19, "Cell dim.",   None, [editItem,qttable.QTableItem.Always], None,                       60),\
        "barcode":          (20, "Barcode",     True, [editItem,qttable.QTableItem.Always], None,                       50),\
        "location":         (21, "Location",    True, [editItem,qttable.QTableItem.Always], None,                       50),\
        "centring_status":  (22, "Use centred pos.",None,[centredStatusItem,"if valid"],    None,                       50),\
        "inverse_beam":     (23, "InvBeam",     None, [boolEditItem,QString("")],(optionalIntValidator,1),50),\
        "inv_interval":     (24, "Interval",    None, [editItem,qttable.QTableItem.Always], (QIntValidator,1),          60),\
        "phi":              (25, "Phi",         None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "tth":              (26, "Two Theta",   None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "kap":              (27, "Kappa",       None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "kth":              (28, "Omega",       None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "gshg":             (29, "GSHG",        None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "gsvg":             (30, "GSVG",        None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0),     30),\
        "axis":             (31, "Axis", SCAN_AXIS_FIXED, [axisComboItem,None],  None ),\
        "do_inducedraddam": (32, "Radiation Damage", True, [boolEditItem,QString("")],(optionalIntValidator,1),              50),\
        }

    """
    __init__
        Description : Initializes the brick: defines the BlissFramework properties, signals and
                      slots; sets internal attribute to None; creates the brick's widgets and
                      layout.
        Type        : instance constructor
        Arguments   : *args (not used; just passed to the super class)
    """
    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        self.external_feeding_monitor = gevent.spawn(self.handle_external_request)
        self.oscillationFailed = None

        self.addProperty('disableDetectorMode','boolean',False)
        self.addProperty('icons','string','')
        self.addProperty('dataCollect','string','')
        self.addProperty('site','string','')
        self.addProperty('testQueue','boolean',False)
        self.addProperty('XML-RPC server port', 'integer', 56045)

        self.defineSlot('setSession',())
        self.defineSlot('setBeamlineConfiguration',())
        self.defineSlot('addOscillation',())
        self.defineSlot('clearQueue',())

        self.defineSignal('collectOscillations',())
        self.defineSignal('resetQueueCount',())
        self.defineSignal('incQueueCount',())
        # New signal created for displaying html pages from the XML RPC server (Olof 2013/04/25)
        self.defineSignal('new_html',())

        self.lastReady = False
        self.collectObj = None

        self.queueList = []
        self.grid_info = {}
        self.queueCount = 0
        self.table=qttable.QTable(0, len(self.__class__.PARAMETERS), self)
        
        self.table.setLeftMargin(0)
        #self.table.setColumnMovingEnabled(True)
        #self.table.setRowMovingEnabled(True)
        
        self.connect(self.table,SIGNAL('contextMenuRequested ( int, int, const QPoint & )'),self.queueContextMenu)
        
        self.failedOscillations=0

        self.validDict = {}
        self.lastValid = True

        self.buttonsContainer=QHBox(self)
        
        # PK 18/01/11
        self.loadQueueButton=QToolButton(self.buttonsContainer)
        self.loadQueueButton.setUsesTextLabel(True)
        self.loadQueueButton.setTextPosition(QToolButton.BesideIcon)
        self.loadQueueButton.setTextLabel("Load queue")
        self.loadQueueButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.loadQueueButton.setEnabled(True)
        QObject.connect(self.loadQueueButton,SIGNAL('clicked()'),self.loadQueueFile)
        
        self.saveQueueButton=QToolButton(self.buttonsContainer)
        self.saveQueueButton.setUsesTextLabel(True)
        self.saveQueueButton.setTextPosition(QToolButton.BesideIcon)
        self.saveQueueButton.setTextLabel("Save queue")
        self.saveQueueButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.saveQueueButton.setEnabled(True)
        QObject.connect(self.saveQueueButton,SIGNAL('clicked()'),self.saveQueueFile)
        
        HorizontalSpacer(self.buttonsContainer)
        
        self.collectButton=QToolButton(self.buttonsContainer)
        self.collectButton.setUsesTextLabel(True)
        self.collectButton.setTextPosition(QToolButton.BesideIcon)
        self.collectButton.setTextLabel("Collect queue")
        self.collectButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.collectButton.setEnabled(False)
        QObject.connect(self.collectButton,SIGNAL('clicked()'),self.collectQueue)
        
        det_mode_list=QStringList()
        DataCollectQueueBrick.PARAMETERS["detector_mode"][3][1] = det_mode_list
 
        DataCollectQueueBrick.PARAMETERS["axis"][3][1] = QStringList()        
        # FIXME! This should be sorted out by querying the hardware server
        for a in axisComboItem.VALUES:
            DataCollectQueueBrick.PARAMETERS["axis"][3][1].append(a)
       
        DataCollectQueueBrick.PARAMETERS["spacegroup"][3][1] = QStringList()
        for sg in DataCollectParametersBrick.XTAL_SPACEGROUPS:
            DataCollectQueueBrick.PARAMETERS["spacegroup"][3][1].append(sg)
 
        for param_name in DataCollectQueueBrick.PARAMETERS:
            param=DataCollectQueueBrick.PARAMETERS[param_name]
            param_index=param[0]
            param_label=param[1]
            param_readonly=param[2]
            param_type=param[3]
            self.table.horizontalHeader().setLabel(param_index,param_label)        
            if param_readonly:
                self.table.setColumnReadOnly(param_index,True)

        self.table.setLeftMargin(4*self.table.leftMargin())

        QVBoxLayout(self,1,2)
        self.layout().addWidget(self.table)
        self.layout().addWidget(self.buttonsContainer)

    def handle_external_request(self):
        while True:
          external_event.wait()
          external_event.clear()
          action, param = queue_external_feeding_list.pop()   
  
          if action == "load":
            self.clearQueue(0)
            try:
              self._loadQueue(eval(param))
            except:
              logging.exception("Could not add to list")
          elif action == "start":
            self.collectQueue("external")
          elif action == "grid_info":
            param.set(self.grid_info)
          elif action == "status":
            try:
              self.collectObj.data_collect_task
            except:
              param.set("not started")
              return
            try:  
              if self.collectObj.data_collect_task.ready():
                status = "failed" if self.oscillationFailed else "successful" 
              else:
                status = "running"
            except:
              if self.collectObj.data_collect_task is None:
                status = "not started"
              else:
                # should never go here
                status = "unknown"
            
            param.set(status)

    """
    propertyChanged
        Description: BlissFramework callback, when a property is set during initialization time
                     (or in edit mode).
        Type       : callback
        Arguments  : propertyName (string; property name)
                     oldValue     (?/defined in addProperty; previous property value)
                     newValue     (?/defined in addProperty; new property value)
        Returns    : nothing
    """
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'dataCollect':
            if self.collectObj is not None:
                self.disconnect(self.collectObj,PYSIGNAL('collectReady'),self.collectReady)
                self.disconnect(self.collectObj,PYSIGNAL('collectOscillationFinished'),self.collectOscillationFinished)
                self.disconnect(self.collectObj,PYSIGNAL('collectOscillationFailed'),self.collectOscillationFailed)
            self.collectObj=self.getHardwareObject(newValue)
            if self.collectObj is not None:
                self.connect(self.collectObj,PYSIGNAL('collectReady'),self.collectReady)
                self.connect(self.collectObj,PYSIGNAL('collectOscillationFinished'),self.collectOscillationFinished)
                self.connect(self.collectObj,PYSIGNAL('collectOscillationFailed'),self.collectOscillationFailed)

        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.collectButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
        elif propertyName == 'disableDetectorMode':
            if newValue:
                self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["detector_mode"][0],True)
        elif propertyName == "site":
            if newValue == "maxlab":
                for index in [9,10,16,17,18]:
                    self.table.hideColumn(index)
            elif newValue == "esrf":
                for index in [23,24,25,26,27,28]:
                    self.table.hideColumn(index)
            else:
                pass
        elif propertyName == "testQueue":
            if newValue == True:
                self.addOscillation(self.DEFAULT_PARAMETER_LIST)
                self.addOscillation(self.DEFAULT_PARAMETER_LIST)
                self.addOscillation(self.DEFAULT_PARAMETER_LIST)
        elif propertyName == 'XML-RPC server port':
            global server
            try:
                # Replaced vanilla simple XMLRPC server with the one dedicated to MxCuBE (Olof 2013/04/24)
                #server = SimpleXMLRPCServer(("", newValue),logRequests=False)
                server = MxCuBEXMLRPCServer(self, ("", newValue), logRequests=False)
                if server is not None:
                    self.xmlrpcServerGreenlet = gevent.spawn(server.serve_forever)
            except:
                # port already in use? can be remote version of mxCuBE...
                # let's ignore this error
                pass
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    """
    run
        Description: Called when the brick is set to run mode.
        Type       : callback (BlissFramework)
        Arguments  : none
        Returns    : nothing
        Signals    : resetQueueCount(False)
    """
    def run(self):
        if self.collectObj is not None:
            self.collectReady(self.collectObj.isReady())
        else:
            self.collectReady(False)
        self.updateLength()
        self.emit(PYSIGNAL("resetQueueCount"),(False,))

    """
    setSession
        Description: Sets whoever is logged (or not logged...) in the application: proposal
                     code, number, etc.
        Type       : slot (brick)
        Arguments  : session_id      (int/None/string; None if nobody is logged, if logged and
                                      using the database, int for the session id, empty string
                                      if logged but not using the database: local user)
                     prop_code       (string; proposal code, empty "" for the local user)
                     prop_number     (int/string; proposal number, empty string "" for the local
                                      user, not used)
                     prop_id         (int; proposal database id, not currently used)
                     expiration_time (float; not currently used)
        Returns    : nothing
    """
    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        self.clearEntireQueue()
        if prop_code is None:
            validator=None
        else:
            validator=(prop_code,prop_number)
        DataCollectQueueBrick.PARAMETERS["directory"][4][2] = validator

    """
    setBeamlineConfiguration
        Description: Stores the detector image extension and the default number of passes. Emits a
                     signal with the given beamline configuration.
        Type       : slot (brick)
        Arguments  : beamline_conf (dict; beamline configuration, from the data collect h.o.)
        Returns    : nothing
    """
    def setBeamlineConfiguration(self,beamline_conf):
        try:
            detector_type=str(beamline_conf["detector_type"])
        except (KeyError,ValueError,TypeError):
            pass
        else:
            if detector_type=='adsc':
                for s in DataCollectQueueBrick.DETECTOR_MODE_ITEMS:
                    DataCollectQueueBrick.PARAMETERS["detector_mode"][3][1].append(s)
            else:
                self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["detector_mode"][0],True)

    """
    contextMenuEvent
        Description: 
        Type       : 
        Arguments  : ev
        Returns    : nothing
    """
    def contextMenuEvent(self,ev):
        count=len(self.queueList)
        if count>0:
            menu=QPopupMenu(self)
            label=QLabel('<nobr><b>Data Collection queue</b></nobr>',menu)
            label.setAlignment(Qt.AlignCenter)
            menu.insertItem(label)
            menu.insertSeparator()
            menu.insertItem("Clear entire queue",0)
            menu.insertItem("Remove this data collection",1)
            QObject.connect(menu,SIGNAL('activated(int)'),self.clearQueue)
            menu.popup(QCursor.pos())

    """
    clearEntireQueue
        Description: 
        Type       : method, slot (widget)
        Arguments  : none
        Returns    : nothing
    """
    def clearQueue(self,index):
        if index == 1:
            self.removeOscillation(self.table.currentRow())
        else:
            self.clearEntireQueue()
        
    def clearEntireQueue(self):
        self.queueList=[]
        self.table.setNumRows(0)
        self.validDict={}
        self.currentValid=True
        self.updateLength()
        self.emit(PYSIGNAL("resetQueueCount"),(False,))

    """
    removeOscillation
        Description: 
        Type       : slot (widget)
        Arguments  : row
        Returns    : nothing
    """
    def removeOscillation(self,row):
        redo_valid=False
        for i in range(self.table.numCols()):
            item=self.table.item(row,i)
            try:
                self.validDict.pop(item)
            except KeyError:
                pass
            else:
                redo_valid=True
        if redo_valid:
            current_valid=True
            for wid in self.validDict:
                if not self.validDict[wid]:
                    current_valid=False
            if current_valid!=self.lastValid:
                self.lastValid=current_valid
                self.collectButton.setEnabled(self.lastReady and self.lastValid)

        self.table.removeRow(row)
        self.queueList.pop(row)
        l=self.updateLength()
        if l==0:
            self.emit(PYSIGNAL("resetQueueCount"),(False,))
        else:
            self.emit(PYSIGNAL("incQueueCount"),(-1,False))

    """
    queueContextMenu
        Description: 
        Type       : slot (widget)
        Arguments  : row
                     col
                     point
        Returns    : nothing
    """
    def queueContextMenu(self,row,col,point):
        #print "queueContextMenu",row,col,point
        if row==-1:
            return self.contextMenuEvent(None)

        menu=QPopupMenu(self)
        title=str(self.table.text(row,0))
        label=QLabel('<nobr><b>%s</b></nobr>' % title,menu)
        label.setAlignment(Qt.AlignCenter)
        menu.insertItem(label)
        menu.insertSeparator()
        menu.insertItem("Remove this oscillation",row)
        QObject.connect(menu,SIGNAL('activated(int)'),self.removeOscillation)
        menu.popup(QCursor.pos())

    """
    addParamDict
        Description: 
        Type       : method
        Arguments  : collect_params
        Returns    : nothing
    """
    def addParamDict(self,collect_params):
        #print "DataCollectQueueBrick.addParamDict",collect_params
        try:
            centred_images=collect_params['centring_status']['images']
        except:
            centred_images=None
        else:
            collect_params['centring_status'].pop('images')
        try:
          motors = collect_params.pop("motors")
        except:
          motors={}
        collect_params2=copy.deepcopy(collect_params)
        collect_params2["motors"]=motors
        if centred_images is not None:
            collect_params2['centring_status']['images']=centred_images
        try:
            collect_params2['centring_status']['valid']
        except:
            collect_params2['centring_status']={'valid':False}

        try:
            collect_params2['energy']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["energy"][0],True)
            try:
                fixed_energy=collect_params2["fixed_energy"]
            except:
                pass
            else:
                collect_params2['energy']=fixed_energy
        else:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["energy"][0],False)

        try:
            collect_params2['transmission']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["transmission"][0],True)
            try:
                fixed_transmission=collect_params2["fixed_transmission"]
            except:
                pass
            else:
                collect_params2['transmission']=fixed_transmission
        else:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["transmission"][0],False)

        try:
            collect_params2['resolution']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["resolution"][0],True)
        else:
            self.table.setColumnReadOnly(DataCollectQueueBrick.PARAMETERS["resolution"][0],False)

        collect_params2["spacegroup"]=""
        collect_params2["cell"] = ""
        try:
            sample_info=collect_params2["sample_info"]
        except:
            sample_info=None
        else:
            if type(sample_info) == types.TupleType:
              collect_params2["spacegroup"] = sample_info[1]["crystal_space_group"]
              collect_params2["cell"] = sample_info[1]["cell"]
            
        self.queueList.append(collect_params2)

        row=self.table.numRows()
        self.table.insertRows(row)

        # Make sure that we know in advance which axis is the selected scan axis
        scan_axis_value = None
        if 'axis' in collect_params2:
            scan_axis_value = collect_params2['axis']
       
        for param_name in collect_params2:
            param_value=collect_params2[param_name]
            logging.info("%s : %s", param_name, param_value)
            try:
                param_index=DataCollectQueueBrick.PARAMETERS[param_name][0]
            except KeyError:
                pass
            except:
                pass
            else:
                #print "addParamDict",param_index,param_name,param_value,self.table.isColumnReadOnly(param_index)
                param_type=DataCollectQueueBrick.PARAMETERS[param_name][3]
                if param_type is not None:
                    param_class=param_type[0]
                    try:
                        param_par=param_type[1]
                    except IndexError:
                        param_obj=param_class(self.table)
                    else:
                        if self.__class__.SCAN_AXIS_FIXED and self.__class__.PARAMETERS[param_name][1] == scan_axis_value\
                                     and isinstance(param_obj, qttable.QTableItem) :
                            # PK - lock scan axis value if we have disabled choosing the scan axis in the queue tab
                            param_obj = param_class(self.table, qttable.QTableItem.Never)
                        else:
                            param_obj=param_class(self.table,param_par)

                    param_validator=DataCollectQueueBrick.PARAMETERS[param_name][4]
                    if param_validator is not None:
                        class_validator=param_validator[0]
                        obj_validator=class_validator(None)
                        try:
                            param_class_validator=param_validator[1]
                        except IndexError:
                            pass
                        else:
                            if param_class_validator is not None:
                                obj_validator.setBottom(param_class_validator)
                        try:
                            param_class_validator2=param_validator[2]
                        except IndexError:
                            pass
                        else:
                            if param_class_validator2 is not None:
                                obj_validator.setSpecificValidator(param_class_validator2)
                        param_obj.setValidator(obj_validator)
                        param_obj.connectInputValid(self.isInputValid)

                    param_obj.setQueueItemValue(param_value)
                    if self.table.isColumnReadOnly(param_index):
                        param_obj.setEnabled(False)
                    self.table.setItem(row,param_index,param_obj)
                else:
                    #try:
                    #    self.table.setText(row,param_index,str(param_value))
                    #except Exception,diag:
                    #    pass
                    self.table.setText(row,param_index,str(param_value))

        if sample_info is not None:
            try:
                barcode=sample_info[1]["code"]
            except KeyError:
                pass
            else:
                param_index=DataCollectQueueBrick.PARAMETERS["barcode"][0]
                self.table.setText(row,param_index,barcode)

            try:
                basket=sample_info[1]["basket"]
            except KeyError:
                pass
            else:
                try:
                    vial=sample_info[1]["vial"]
                except KeyError:
                    pass
                else:
                    location="%d:%02d" % (basket,vial)
                    param_index=DataCollectQueueBrick.PARAMETERS["location"][0]
                    self.table.setText(row,param_index,location)

    """
    isInputValid
        Description: 
        Type       : slot (widget)
        Arguments  : input_widget
                     valid
        Returns    : nothing
        Signals    : parametersValid(current_valid<bool>)
    """
    def isInputValid(self,input_widget,valid):
        #print "IS INPUT VALID",input_widget,valid

        self.validDict[input_widget]=valid
        current_valid=True
        for wid in self.validDict:
            if not self.validDict[wid]:
                current_valid=False
        if current_valid!=self.lastValid:
            self.lastValid=current_valid
            self.collectButton.setEnabled(self.lastReady and self.lastValid)

    """
    addOscillation
        Description: 
        Type       : slot (brick)
        Arguments  : collect_params
        Returns    : 
        Signals    : incQueueCount(len<int>,False)
    """
    def addOscillation(self,collect_paramDict_list):
        if type(collect_paramDict_list) == types.DictType:
          # this is grid information
          self.grid_info = collect_paramDict_list
        else:
          for collect_paramDict in collect_paramDict_list:
              self.addParamDict(collect_paramDict)
              self.queueCount += 1

          self.updateLength()
          self.emit(PYSIGNAL("incQueueCount"),(len(collect_paramDict_list),False))

    """
    updateLength
        Description: 
        Type       : method
        Arguments  : none
        Returns    : 
    """
    def updateLength(self):
        count=len(self.queueList)
        self.collectButton.setEnabled(self.lastReady and count>0 and self.lastValid)
        if count > 0:
            if not self.lastReady:
                logging.getLogger().warning("Collection is not ready, maybe spec is not connected or busy with an ongoing data collection, collect not enabled")
            if not self.lastValid:
                logging.getLogger().warning("Collection is not valid, maybe a parameter is not correct, collect not enabled")
        return count

    # PK - split old collectQueue method into two, to allow self.queueList to be updated
    # from user-edited values in self.table independently from launching a collection.
    def collectQueue(self, owner=None): 
        if owner is None:
            owner = str(DataCollectQueueBrick)
        self.populateQueueListFromTable()
        self.failedOscillations=0
        self.emit(PYSIGNAL("collectOscillations"),(owner, self.queueList))
        
    # PK - guts of old collectQueue method. Latest version of collectQueue is slightly different
    # from this: maybe worth patching?
    def populateQueueListFromTable(self):
        count=len(self.queueList)
        for row in range(count):
            for param_name in DataCollectQueueBrick.PARAMETERS:
                param=DataCollectQueueBrick.PARAMETERS[param_name]
                param_index=param[0]

                #if not self.table.isColumnReadOnly(param_index):
                param_type=DataCollectQueueBrick.PARAMETERS[param_name][3]
                if param_type is not None:
                    try:
                        text=self.table.item(row,param_index).getQueueItemValue()
                    except Exception, msg:
                        # last resort, try just reading the text
                        text = str(self.table.text(row,param_index))
                #else:
                #    text=str(self.table.text(row,param_index))
                if param_name == "spacegroup":
                    self.queueList[row].setdefault("sample_info", (None,{}))[1]["crystal_space_group"]=text
                elif param_name == "cell":
                    self.queueList[row].setdefault("sample_info", (None,{}))[1]["cell"]=text
                else:
                    self.queueList[row][param_name]=text
                self.queueList[row]["in_queue"]=1
            self.queueList[row]["process_directory"]=self.queueList[row]["directory"].replace("RAW_DATA","PROCESSED_DATA")

        self.failedOscillations=0
        self.queueList[-1]["in_queue"] = 0
        
    """
    collectReady
        Description: 
        Type       : slot (h.o.)
        Arguments  : state (bool; )
        Returns    : nothing
    """
    def collectReady(self,state):
        count=len(self.queueList)
        self.lastReady=state
        self.collectButton.setEnabled(self.lastReady and count>0 and self.lastValid)

    """
    collectOscillationFinished
        Description: Called when the data collect h.o. finishes an oscillation. Emits a signal to the
                     BlissFramework to update the number of oscillations in the tab.
        Type       : slot (h.o.)
        Arguments  : owner (string?; the owner of the finished data collection)
                     state (None/bool; the finished state, should always be True)
                     msg   (successful message)
        Returns    : nothing
        Signals    : collectOscillationFinished(owner<string?>,state<None/bool=False,message<string>,col_id<int>,oscillation_id<int>)
    """
    def collectOscillationFinished(self,owner,state,message,col_id,oscillation_id,*args):
        self.oscillationFailed = False
        if owner in ("external", str(DataCollectQueueBrick)):
            self.table.removeRow(self.failedOscillations)
            self.queueList.pop(self.failedOscillations)
            if len(self.queueList)==0:
                self.emit(PYSIGNAL("resetQueueCount"),(False,))
            else:
                self.emit(PYSIGNAL("incQueueCount"),(-1,False))

    """
    collectOscillationFailed
        Description: Called when the data collect h.o. failed to do an oscillation.
        Type       : slot (h.o.)
        Arguments  : owner          (string?; the owner of the failed data collection)
                     state          (None/bool; the failed state: None for stopped, False for aborted)
                     msg            (stopped/aborted/error message)
                     col_id         (int; entry id in the Collection database table)
                     oscillation_id (int; the oscillation id internal to the data collect h.o.)
        Returns    : nothing
        Signals    : collectOscillationFailed(owner<string >,state<bool=True,message<string>,col_id<int>,oscillation_id<int>)
    """
    def collectOscillationFailed(self,owner,state,message,col_id,oscillation_id,*args):
        self.oscillationFailed = True
        if owner in ("external", str(DataCollectQueueBrick)):
            if state is None:
                self.failedOscillations+=1

       
    def _loadQueue(self, queue_entries):
        if isinstance(queue_entries, list):
                    # Check that we have a list of dictionaries before we start doing anything else
                    is_queue_ok = True
                    for e in range(len(queue_entries)):
                        if isinstance(queue_entries[e], dict):
                           missing_keys = [ k for k in self.__class__.PARAMETERS.keys() if k not in queue_entries[e] ]
                           if len(missing_keys) > 0:
                               is_queue_ok = False
                               logging.error("Queue entry %s is missing key(s): %s", e, missing_keys)
                        else:
                            is_queue_ok = False
                            logging.error("Queue entry %s is not a valid Python dictionary", e)

                    if is_queue_ok:
                        self.addOscillation(queue_entries)
                        self.collectReady(True)
         
    # PK 18/01/11
    def loadQueueFile(self):
        queue_file_name = self.selectQueueFile(False)
        if queue_file_name:
            queue_file_name = str(queue_file_name)
            try:
                queue_file = open(queue_file_name, "r")
                queue_entries = eval(queue_file.read())
                queue_file.close()
               
                self._loadQueue(queue_entries) 
            except:
                logging.exception("Failed to load queue file %s", queue_file_name)

    # PK 18/01/11
    def saveQueueFile(self):
        queue_file_name = self.selectQueueFile(True)
        if queue_file_name:
          queue_file_name = str(queue_file_name) #QString=>str
          suffix = os.path.extsep + "mxq"
          if not queue_file_name.endswith(suffix):
            queue_file_name += suffix

          try:
              self.populateQueueListFromTable()
              queue_file = open(queue_file_name, "w")
              queue_file.write( pprint.pformat(self.queueList) )
              queue_file.close()
          except:
              logging.exception("Could not save queue file %s", queue_file_name)
                            
                                        
    # PK 18/01/11
    def selectQueueFile(self, save):
        get_file=QFileDialog(self)
        s=self.font().pointSize()
        f = get_file.font()
        f.setPointSize(s)
        get_file.setFont(f)
        get_file.updateGeometry()
        if save:
            fn = get_file.getSaveFileName(".", "mxCuBE queue file (*.mxq)", self, "Select a file","Choose a file to save to")
        else:
            fn = get_file.getOpenFileName(".", "mxCuBE queue file (*.mxq)", self, "Select a file","Choose a file to load from")
           
        return fn
