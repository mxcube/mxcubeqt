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

import logging
import pprint
import types
import os
import sys
import new
import time
import operator
import weakref
import gc

from PyQt4 import QtCore
from PyQt4 import QtGui

from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import HardwareObject
from BlissFramework.Utils import PropertyBag
from BlissFramework.Utils import Connectable
from BlissFramework.Utils import Qt4_ProcedureWidgets
from BlissFramework.Utils import Qt4_widget_colors
import BlissFramework

try:
  from louie import dispatcher
  from louie import saferef
except ImportError:
  from pydispatch import dispatcher
  from pydispatch import saferef
  saferef.safe_ref = saferef.safeRef

_emitterCache = weakref.WeakKeyDictionary()


class _QObject(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QtCore.QObject.__init__(self, *args)

        try:
            self.__ho = weakref.ref(kwargs.get("ho"))
        except:
            self.__ho = None

def emitter(ob):
    """
    Descript. : Returns a QObject surrogate for *ob*, to use in Qt signaling. 
                This function enables you to connect to and emit signals 
                from (almost) any python object with having to subclass QObject.
    """
    if ob not in _emitterCache:
        _emitterCache[ob] = _QObject(ho=ob)
    return _emitterCache[ob]


class InstanceEventFilter(QtCore.QObject):
    def eventFilter(self, w, e):
        """
        Descript. :
        """
        obj=w
        while obj is not None:
            if isinstance(obj,BlissWidget):
                if isinstance(e, QtGui.QContextMenuEvent):
                    #if obj.shouldFilterEvent():
                    return True
                elif isinstance(e, QtGui.QMouseEvent):
                    if e.button() == QtCore.Qt.RightButton:
                        return True
                    elif obj.shouldFilterEvent():
                        return True
                elif isinstance(e, QtGui.QKeyEvent) or isinstance(e, QtGui.QFocusEvent):
                    if obj.shouldFilterEvent():
                        return True
                return QtCore.QObject.eventFilter(self, w, e)
            try:
                obj = obj.parent()
            except:
                obj=None
        return QtCore.QObject.eventFilter(self, w, e)


class WeakMethodBound:
    def __init__(self , f):
        """
        Descript. :
        """
        self.f = weakref.ref(f.im_func)
        self.c = weakref.ref(f.im_self)

    def __call__(self , *args):
        """
        Descript. :
        """
        obj = self.c()
        if obj is None:
            return None
        else:
            f = self.f()
            return f.__get__(obj)


class WeakMethodFree:
    def __init__(self , f):
        """
        Descript. :
        """
        self.f = weakref.ref(f)
    def __call__(self, *args):
        """
        Descript. :
        """
        return self.f()


def WeakMethod(f):
    """
    Descript. :
    """
    try:
        f.im_func
    except AttributeError :
        return WeakMethodFree(f)
    return WeakMethodBound(f)


class SignalSlotFilter:
    def __init__(self, signal, slot, should_cache):
        """
        Descript. :
        """
        self.signal = signal
        self.slot = WeakMethod(slot)
        self.should_cache = should_cache

    def __call__(self, *args):
        """
        Descript. :
        """
        if (BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_SLAVE and 
            BlissWidget._instanceMirror == BlissWidget.INSTANCE_MIRROR_PREVENT):
           if self.should_cache:
               BlissWidget._eventsCache[self.slot]=(time.time(), self.slot, args)
               return

        s = self.slot()
        if s is not None:
            s(*args)


class BlissWidget(QtGui.QFrame, Connectable.Connectable):
    (INSTANCE_ROLE_UNKNOWN, INSTANCE_ROLE_SERVER, INSTANCE_ROLE_SERVERSTARTING,
     INSTANCE_ROLE_CLIENT, INSTANCE_ROLE_CLIENTCONNECTING) = (0, 1, 2, 3, 4)
    (INSTANCE_MODE_UNKNOWN, INSTANCE_MODE_MASTER, INSTANCE_MODE_SLAVE) = (0, 1, 2)
    (INSTANCE_LOCATION_UNKNOWN, INSTANCE_LOCATION_LOCAL, 
     INSTANCE_LOCATION_INHOUSE,INSTANCE_LOCATION_INSITE,
     INSTANCE_LOCATION_EXTERNAL) = (0,1,2,3,4)
    (INSTANCE_USERID_UNKNOWN, INSTANCE_USERID_LOGGED, INSTANCE_USERID_INHOUSE,
     INSTANCE_USERID_IMPERSONATE) = (0,1,2,3)
    (INSTANCE_MIRROR_UNKNOWN, INSTANCE_MIRROR_ALLOW, INSTANCE_MIRROR_PREVENT) = (0,1,2)

    _runMode = False
    _instanceRole = INSTANCE_ROLE_UNKNOWN
    _instanceMode = INSTANCE_MODE_UNKNOWN
    _instanceLocation = INSTANCE_LOCATION_UNKNOWN
    _instanceUserId = INSTANCE_USERID_UNKNOWN
    _instanceMirror = INSTANCE_MIRROR_UNKNOWN
    _filterInstalled = False
    _eventsCache = {}
    _menuBackgroundColor = None
    _menuBar = None

    _applicationEventFilter=InstanceEventFilter(None)
    
    @staticmethod
    def setRunMode(mode):
        """
        Descript. :
        """
        if mode:
            BlissWidget._runMode = True
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    w.__run()
                    try:
                        w.set_expert_mode(False)
                    except:
                        logging.getLogger().exception("Could not set %s to user mode", w.name())

        else:
            BlissWidget._runMode = False
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    w.__stop()
                    try:
                        w.set_expert_mode(True)
                    except:
                        logging.getLogger().exception("Could not set %s to expert mode", w.name())

    @staticmethod
    def isRunning():
        """
        Descript. :
        """
        return BlissWidget._runMode

    @staticmethod
    def updateMenuBarColor(enable_checkbox=None):
        """
        Descript. : Not a direct way how to change menubar color
                    it is now done by changing stylesheet
        """
        color=None
        if BlissWidget._menuBar is not None:
            if BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_MASTER:
                if BlissWidget._instanceUserId == BlissWidget.INSTANCE_USERID_IMPERSONATE:
                    color = "lightBlue"
                else:
                    color = "rgb(204,255,204)"
            elif BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_SLAVE:
                if BlissWidget._instanceRole == BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING:
                    color = "rgb(255,204,204)"
                elif BlissWidget._instanceUserId == BlissWidget.INSTANCE_USERID_UNKNOWN:
                    color = "rgb(255, 165, 0)"
                else:
                    color = "yellow"

        if color is not None:
            BlissWidget._menuBar.set_color(color)

    @staticmethod
    def setInstanceMode(mode):
        """
        Descript. :
        """
        BlissWidget._instanceMode = mode
        for w in QtGui.QApplication.allWidgets():
            if isinstance(w, BlissWidget):
                try:
                    w._instanceModeChanged(mode)
                except:
                    pass
        if BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_MASTER:
            if BlissWidget._filterInstalled:
                QtGui.QApplication.instance().removeEventFilter(BlissWidget._applicationEventFilter)
                BlissWidget._filterInstalled = False
                BlissWidget.synchronizeWithCache() # why?
        else:
            if not BlissWidget._filterInstalled:
                QtGui.QApplication.instance().installEventFilter(BlissWidget._applicationEventFilter)
                BlissWidget._filterInstalled = True

        BlissWidget.updateMenuBarColor(BlissWidget._instanceMode == \
                    BlissWidget.INSTANCE_MODE_MASTER)

    def shouldFilterEvent(self):
        """
        Descript. :
        """
        if BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_MASTER:
            return False
        try:
            allow_always = self['instanceAllowAlways']
        except KeyError:
            return False
        if not allow_always:
            try:
                allow_connected = self['instanceAllowConnected']
            except KeyError:
                return False

            connected = BlissWidget._instanceRole in (BlissWidget.INSTANCE_ROLE_SERVER,BlissWidget.INSTANCE_ROLE_CLIENT)
            if allow_connected and connected:
                return False
            return True

        return False

    def connectGroupBox(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        self.connect(widget, QtCore.SIGNAL('toggled(bool)'), lambda \
             s:BlissWidget.widgetGroupBoxToggled(brick_name, \
             widget_name, master_sync,s))

    def connectComboBox(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        self.connect(widget, QtCore.SIGNAL('activated(int)'),lambda \
             i:BlissWidget.widgetComboBoxActivated(brick_name, \
             widget_name, widget, master_sync, i))

    def connectLineEdit(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        self.connect(widget, QtCore.SIGNAL('textChanged(const QString &)'), lambda \
             t:BlissWidget.widgetLineEditTextChanged(brick_name, widget_name, \
             master_sync, t))

    def connectSpinBox(self,widget,widget_name,master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        self.connect(widget, QtCore.SIGNAL('editorTextChanged'), lambda \
             t:BlissWidget.widgetSpinBoxTextChanged(brick_name, widget_name, \
             master_sync, t))

    def connectGenericWidget(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        self.connect(widget, QtCore.SIGNAL('widgetSynchronize'), lambda \
             state:BlissWidget.widgetGenericChanged(brick_name, widget_name, \
             master_sync, state))

    def _instanceModeChanged(self,mode):
        """
        Descript. :
        """
        for widget, widget_name, master_sync in self._widgetEvents:
            if isinstance(widget, QtGui.QGroupBox):
                self.connectGroupBox(widget, widget_name, master_sync)
            elif isinstance(widget,QtGui.QComboBox):
                self.connectComboBox(widget, widget_name, master_sync)
            elif isinstance(widget, QtGui.QLineEdit):
                self.connectLineEdit(widget, widget_name, master_sync)
            elif isinstance(widget, QtGui.QSpinBox):
                self.connectSpinBox(widget, widget_name, master_sync)
            else:
                ### verify if widget has the widgetSynchronize method!!!
                self.connectGenericWidget(widget, widget_name, master_sync)
        self._widgetEvents = []

        if self.shouldFilterEvent():
            self.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        self.instanceModeChanged(mode)

    def instanceModeChanged(self, mode):
        """
        Descript. :
        """
        pass

    @staticmethod
    def isInstanceModeMaster():
        """
        Descript. :
        """
        return BlissWidget._instanceMode==BlissWidget.INSTANCE_MODE_MASTER

    @staticmethod
    def isInstanceModeSlave():
        """
        Descript. :
        """
        return BlissWidget._instanceMode==BlissWidget.INSTANCE_MODE_SLAVE

    @staticmethod
    def isInstanceRoleUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceRole==BlissWidget.INSTANCE_ROLE_UNKNOWN

    @staticmethod
    def isInstanceRoleClient():
        """
        Descript. :
        """
        return BlissWidget._instanceRole==BlissWidget.INSTANCE_ROLE_CLIENT

    @staticmethod
    def isInstanceRoleServer():
        """
        Descript. :
        """
        return BlissWidget._instanceRole==BlissWidget.INSTANCE_ROLE_SERVER

    @staticmethod
    def isInstanceUserIdUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId==BlissWidget.INSTANCE_USERID_UNKNOWN

    @staticmethod
    def isInstanceUserIdLogged():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId==BlissWidget.INSTANCE_USERID_LOGGED

    @staticmethod
    def isInstanceUserIdInhouse():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId==BlissWidget.INSTANCE_USERID_INHOUSE

    @staticmethod
    def setInstanceRole(role):
        """
        Descript. :
        """
        if role==BlissWidget._instanceRole:
            return
        BlissWidget._instanceRole = role
        for w in QtGui.QApplication.allWidgets():
            if isinstance(w, BlissWidget):
                #try:
                w.instanceRoleChanged(role)
                #except:
                #    pass

    @staticmethod
    def setInstanceLocation(location):
        """
        Descript. :
        """
        if location==BlissWidget._instanceLocation:
            return
        BlissWidget._instanceLocation = location
        for w in QtGui.QApplication.allWidgets():
            if isinstance(w, BlissWidget):
                #try:
                w.instanceLocationChanged(location)
                #except:
                #    pass

    @staticmethod
    def setInstanceUserId(user_id):
        """
        Descript. :
        """
        if user_id==BlissWidget._instanceUserId:
            return
        BlissWidget._instanceUserId = user_id

        for w in QtGui.QApplication.allWidgets():
            if isinstance(w, BlissWidget):
                #try:
                w.instanceUserIdChanged(user_id)
                #except:
                #    pass
        BlissWidget.updateMenuBarColor()

    @staticmethod
    def setInstanceMirror(mirror):
        """
        Descript. :
        """
        if mirror==BlissWidget._instanceMirror:
            return
        BlissWidget._instanceMirror = mirror

        if mirror==BlissWidget.INSTANCE_MIRROR_ALLOW:
            BlissWidget.synchronizeWithCache()

        for w in QtGui.QApplication.allWidgets():
            if isinstance(w, BlissWidget):
                #try:
                w.instanceMirrorChanged(mirror)
                #except:
                #    pass

    def instanceMirrorChanged(self,mirror):
        """
        Descript. :
        """
        pass
    
    def instanceLocationChanged(self,location):
        """
        Descript. :
        """
        pass

    @staticmethod
    def isInstanceLocationUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceLocation==BlissWidget.INSTANCE_LOCATION_UNKNOWN

    @staticmethod
    def isInstanceLocationLocal():
        """
        Descript. :
        """
        return BlissWidget._instanceLocation==BlissWidget.INSTANCE_LOCATION_LOCAL

    @staticmethod
    def isInstanceMirrorAllow():
        """
        Descript. :
        """
        return BlissWidget._instanceMirror==BlissWidget.INSTANCE_MIRROR_ALLOW

    def instanceUserIdChanged(self,user_id):
        """
        Descript. :
        """
        pass

    def instanceRoleChanged(self,role):
        """
        Descript. :
        """
        pass

    @staticmethod
    def updateWhatsThis():
        """
        Descript. :
        """
        for widget in QtGui.QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                msg = "%s (%s)\n%s" % (widget.objectName(), 
                                       widget.__class__.__name__, 
                                       widget.getHardwareObjectsInfo())
                widget.setWhatsThis(msg)
        QtGui.QWhatsThis.enterWhatsThisMode()

    @staticmethod
    def updateWidget(brick_name,widget_name,method_name,method_args,master_sync):
        """
        Descript. :
        """
        #somehow active window is None
        #TODO fix this
        for widget in QtGui.QApplication.topLevelWidgets():
            if hasattr(widget, "configuration"):
               top_level_widget = widget

        if not master_sync or BlissWidget._instanceMode==BlissWidget.INSTANCE_MODE_MASTER:
            top_level_widget.emit(QtCore.SIGNAL('applicationBrickChanged'), 
                  brick_name, widget_name, method_name, method_args, master_sync)

    @staticmethod
    def updateTabWidget(tab_name,tab_index):
        """
        Descript. :
        """
        if BlissWidget._instanceMode==BlissWidget.INSTANCE_MODE_MASTER:
            #TODO fixt this, by removing if
            if QtGui.QApplication.activeWindow():
                QtGui.QApplication.activeWindow().emit(\
                   QtCore.SIGNAL('applicationTabChanged'),
                   tab_name, tab_index)

    @staticmethod
    def widgetGroupBoxToggled(brick_name,widget_name,master_sync,state):
        """
        Descript. :
        """
        BlissWidget.updateWidget(brick_name,widget_name,"setChecked",(state,),master_sync)

    @staticmethod
    def widgetComboBoxActivated(brick_name, widget_name,widget,master_sync,index):
        """
        Descript. :
        """
        lines=[]
        if widget.editable():
            for i in range(widget.count()):
                lines.append(str(widget.text(i)))
        BlissWidget.updateWidget(brick_name,widget_name,"activated",(index,lines),master_sync)

    @staticmethod
    def widgetLineEditTextChanged(brick_name,widget_name,master_sync,text):
        """
        Descript. :
        """
        BlissWidget.updateWidget(brick_name,widget_name,"setText",(str(text),),master_sync)

    @staticmethod
    def widgetSpinBoxTextChanged(brick_name,widget_name,master_sync,text):
        """
        Descript. :
        """
        BlissWidget.updateWidget(brick_name,widget_name,"setEditorText",(str(text),), master_sync)

    @staticmethod
    def widgetGenericChanged(brick_name,widget_name,master_sync,state):
        """
        Descript. :
        """
        BlissWidget.updateWidget(brick_name,widget_name,"widgetSynchronize",(state,),master_sync)

    def instanceForwardEvents(self,widget_name,master_sync):
        """
        Descript. :
        """
        if widget_name=="":
            widget=self
        else:
            widget=getattr(self, widget_name)
        if isinstance(widget, QtGui.QComboBox):
            widget.activated = new.instancemethod(ComboBoxActivated,widget,widget.__class__)
        elif isinstance(widget, QtGui.QSpinBox):
            widget.setEditorText = new.instancemethod(SpinBoxSetEditorText,widget,widget.__class__)
            widget.editorTextChanged = new.instancemethod(SpinBoxEditorTextChanged,widget,widget.__class__)
            self.connect(widget.lineEdit(), QtCore.SIGNAL('textChanged(const QString &)'), widget.editorTextChanged)

        self._widgetEvents.append((widget, widget_name, master_sync))

    def instanceSynchronize(self,*args, **kwargs):
        """
        Descript. :
        """
        for widget_name in args:
            self.instanceForwardEvents(widget_name, kwargs.get("master_sync", True))

    @staticmethod
    def shouldRunEvent():
        """
        Descript. :
        """
        return BlissWidget._instanceMirror==BlissWidget.INSTANCE_MIRROR_ALLOW

    @staticmethod
    def addEventToCache(timestamp,method,*args):
        """
        Descript. :
        """
        try:
            m = WeakMethod(method)
        except TypeError:
            m = method
        BlissWidget._eventsCache[m]=(timestamp, m, args)

    @staticmethod
    def synchronizeWithCache():
        """
        Descript. :
        """
        events=BlissWidget._eventsCache.values()
        ordered_events=sorted(events,key=operator.itemgetter(0))
        for event_timestamp,event_method,event_args in ordered_events:
            try:
                m = event_method()
                if m is not None:
                  m(*event_args)
            except:
                pass
        BlissWidget._eventsCache={}

    def __init__(self, parent = None, widgetName = ''):       
        """
        Descript. :
        """
        Connectable.Connectable.__init__(self)
        QtGui.QFrame.__init__(self, parent)
        self.setObjectName(widgetName)
        self.propertyBag = PropertyBag.PropertyBag()
                
        self.__enabledState = True #saved enabled state
        self.__loadedHardwareObjects = []
        self._signalSlotFilters = {}
        self._widgetEvents = []
 
        #
        # add what's this help
        #
        self.setWhatsThis("%s (%s)\n" % (widgetName, self.__class__.__name__))
        #WhatsThis.add(self, "%s (%s)\n" % (widgetName, self.__class__.__name__))
        
        #
        # add properties shared by all BlissWidgets
        #
        self.addProperty('fontSize', 'string', str(self.font().pointSize()))
        self.addProperty('frame', 'boolean', False)
        self.addProperty('instanceAllowAlways', 'boolean', False)#, hidden=True)
        self.addProperty('instanceAllowConnected', 'boolean', False)#, hidden=True)
        self.addProperty('fixedWidth', 'integer', '-1')
        self.addProperty('fixedHeight', 'integer', '-1')
        #
        # connect signals / slots
        #
        dispatcher.connect(self.__hardwareObjectDiscarded, 
                           'hardwareObjectDiscarded', 
                           HardwareRepository.HardwareRepository())
        self.defineSlot('enable_widget', ())

    def __run(self):
        """
        Descript. :
        """
        self.setAcceptDrops(False)
        self.blockSignals(False)
        
        self.setEnabled(self.__enabledState)
 
        try:        
            self.run()
        except:
            logging.getLogger().exception("Could not set %s to run mode", self.objectName())

    def __stop(self):
        """
        Descript. :
        """
        self.blockSignals(True)
        
        try:
            self.stop()       
        except:
            logging.getLogger().exception("Could not stop %s", self.objectName())

        #self.setAcceptDrops(True)
        self.__enabledState = self.isEnabled()
        QtGui.QWidget.setEnabled(self, True)
       
    def __repr__(self):
        """
        Descript. :
        """
        return repr("<%s: %s>" % (self.__class__, self.objectName()))

    def connectSignalSlotFilter(self,sender,signal,slot,should_cache):
        """
        Descript. :
        """
        uid=(sender, signal, hash(slot))
	signalSlotFilter = SignalSlotFilter(signal, slot, should_cache)
        self._signalSlotFilters[uid]=signalSlotFilter

	QtCore.QObject.connect(sender, signal, signalSlotFilter)

    def connect(self, sender, signal, slot, instanceFilter=False, shouldCache=True):
        """
        Descript. :
        """
	signal = str(signal)
        if signal[0].isdigit():
          pysignal = signal[0]=='9'
          signal=signal[1:]
        else:
          pysignal=True

        if not isinstance(sender, QtCore.QObject):
          if isinstance(sender, HardwareObject):
            #logging.warning("You should use %s.connect instead of using %s.connect", sender, self)
            sender.connect(signal, slot) 
            return
          else:
            _sender = emitter(sender)
        else:
	    _sender = sender

        if instanceFilter:
            self.connectSignalSlotFilter(_sender, pysignal and PYSIGNAL(signal) or SIGNAL(signal), slot, shouldCache)
        else:
            QtCore.QObject.connect(_sender, pysignal and QtCore.SIGNAL(signal) or QtCore.SIGNAL(signal), slot)

        # workaround for PyQt lapse
        if hasattr(sender, "connectNotify"):
            sender.connectNotify(QtCore.SIGNAL(signal))
    
    def disconnect(self, sender, signal, slot):
        """
        Descript. :
        """
	signal = str(signal)
        if signal[0].isdigit():
          pysignal = signal[0]=='9'
          signal=signal[1:]
        else:
          pysignal=True

        if isinstance(sender, HardwareObject):
          #logging.warning("You should use %s.disconnect instead of using %s.connect", sender,self)
          sender.disconnect(signal, slot)
          return

        # workaround for PyQt lapse
        if hasattr(sender, "disconnectNotify"):
            sender.disconnectNotify(signal)

        if not isinstance(sender, QObject):
            sender = emitter(sender)
           
            try:
                uid=(sender, pysignal and QtCore.SIGNAL(signal) or QtCore.SIGNAL(signal), hash(slot))
                signalSlotFilter=self._signalSlotFilters[uid]
            except KeyError:
                QtCore.QObject.disconnect(sender, pysignal and QtCore.SIGNAL(signal) or QtCore.SIGNAL(signal), slot)
            else:
                QtCore.QObject.disconnect(sender, pysignal and QtCore.SIGNAL(signal) or QtCore.SIGNAL(signal), signalSlotFilter)
                del self._signalSlotFilters[uid]
        else:
            QtCore.QObject.disconnect(sender, pysignal and QtCore.SIGNAL(signal) or QtCore.SIGNAL(signal), signalSlotFilter)

    def reparent(self, widget_to):
        """
        Descript. :
        """
        savedEnabledState = self.isEnabled()
        if self.parent() is not None:
            self.parent().layout().removeWidget(self)
        if widget_to is not None:
            widget_to.layout().addWidget(self)
            self.setEnabled(savedEnabledState)
        
    def blockSignals(self, block):
        """
        Descript. :
        """
        for child in self.children():
            child.blockSignals(block)
            
    def run(self):
        """
        Descript. :
        """
        pass

    def stop(self):
        """
        Descript. :
        """
        pass

    def restart(self):
        """
        Descript. :
        """
        self.stop()
        self.run()

    def loadUIFile(self, filename):
        """
        Descript. :
        """
        for path in [BlissFramework.getStdBricksPath()]+BlissFramework.getCustomBricksDirs():
            #modulePath = sys.modules[self.__class__.__module__].__file__
            #path = os.path.dirname(modulePath)
            if os.path.exists(os.path.join(path, filename)):
                return qtui.QWidgetFactory.create(os.path.join(path, filename))

    def createGUIFromUI(self, UIFile):
        """
        Descript. :
        """
        widget = self.loadUIFile(UIFile)
        if widget is not None:
            children = self.children() or []
            for child in children:
                self.removeChild(child) # remove all children first
                
            layout = QtGui.QGridLayout(self, 1, 1)
            widget.reparent(self)
            widget.show()
            layout.addWidget(widget, 0, 0)
            self.setLayout(layout)
            return widget

    def setPersistentPropertyBag(self, persistentPropertyBag):
        """
        Descript. :
        """
        if id(persistentPropertyBag) != id(self.propertyBag):
            for property in persistentPropertyBag:
                #
                # persistent properties are set
                # 
                if property.getName() in self.propertyBag.properties:
                    self.propertyBag.getProperty(property.getName()).setValue(property.getUserValue())
                elif property.hidden:
                    self.propertyBag[property.getName()] = property
        
        self.readProperties()
                            
    def readProperties(self):
        """
        Descript. :
        """
        for prop in self.propertyBag:
            self._propertyChanged(prop.getName(), None, prop.getUserValue())
        
    """
    def editProperties(self):
        if not self.propertyBag.isEmpty():
            editor = self.propertyBag.editor()
            self.connect(editor, PYSIGNAL('propertyChanged'), self._propertyChanged)
            editor.exec_loop()
    """

    def addProperty(self, *args, **kwargs):
        """
        Descript. :
        """
        self.propertyBag.addProperty(*args, **kwargs)
               
    def getProperty(self, property_name):
        """
        Descript. :
        """
        return self.propertyBag.getProperty(property_name)

    def showProperty(self, property_name):
        """
        Descript. :
        """
        return self.propertyBag.showProperty(property_name)

    def hideProperty(self, property_name):
        """
        Descript. :
        """
        return self.propertyBag.hideProperty(property_name)

    def delProperty(self, property_name):
        """
        Descript. :
        """
        return self.propertyBag.delProperty(property_name)
    
    def getHardwareObject(self, hardware_object_name):
        """
        Descript. :
        """
        if not hardware_object_name in self.__loadedHardwareObjects:
            self.__loadedHardwareObjects.append(hardware_object_name)

        ho = HardwareRepository.HardwareRepository().getHardwareObject(hardware_object_name)
    
        return ho
        
    def __hardwareObjectDiscarded(self, hardware_object_name):
        """
        Descript. :
        """
        if hardware_object_name in self.__loadedHardwareObjects:
            # there is a high probability we need to reload this hardware object...
            self.readProperties() #force to read properties

    def getHardwareObjectsInfo(self):
        """
        Descript. :
        """
        d = {}
        for ho_name in self.__loadedHardwareObjects:
            info = HardwareRepository.HardwareRepository().getInfo(ho_name)
            
            if len(info) > 0:
                d[ho_name] = info

        if len(d):
            return "Hardware Objects:\n\n%s" % pprint.pformat(d)
        else:
            return ""
        
    def __getitem__(self, property_name):
        """
        Descript. : Direct access tp properties values
        """
        return self.propertyBag[property_name]
        
    def __setitem__(self, property_name, value):
        """
        Descript. :
        """
        p = self.propertyBag.getProperty(property_name)
        oldValue = p.getValue()
        p.setValue(value)

        self._propertyChanged(property_name, oldValue, p.getUserValue())
    
    def _propertyChanged(self, property_name, old_value, new_value):
        #import time; t0=time.time()   
        if property_name == 'fontSize':
            try:
                s = int(new_value)
            except:
                self.getProperty('fontSize').setValue(self.font().pointSize())
            else:
                f = self.font()
                f.setPointSize(s)
                self.setFont(f)

                #for brick in self.queryList("QWidget"):
                for brick in self.children():
                    if isinstance(brick, BlissWidget):
                        brick["fontSize"] = s
                
                self.update()
        elif property_name == 'frame':
            try:
               if new_value:  
                   self.setFrameStyle(QtGui.QFrame.StyledPanel)
               else:
                   self.setFrameStyle(QtGui.QFrame.NoFrame)
            except:
               pass
            self.update()
        elif property_name == 'fixedWidth': 
            if new_value > -1:
                self.setFixedWidth(new_value)
        elif property_name == 'fixedHeight':
            if new_value > -1:
                self.setFixedHeight(new_value)
        else:
            try:
                self.propertyChanged(property_name, old_value, new_value)
            except:
                logging.getLogger().exception('Error while setting property %s for %s (details in log file).', property_name, str(self.objectName()))

        #if not BlissWidget.isRunning():
        #    self.blockSignals(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        pass

    def set_expert_mode(self, expert):
        """
        Descript. :
        """
        pass
    
    def enable_widget(self, state):
        """
        Descript. :
        """
        if state:
            self.setEnabled(True)
        else:
            self.setDisabled(True)
  

class NullBrick(BlissWidget):

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        self.propertyBag = PropertyBag.PropertyBag()

    """
    def setShelf(self, shelf):
        persistentPropertyBag = PropertyBag.unpickleFromShelf(shelf, self.objectName())

        if not persistentPropertyBag.isEmpty():       
            for property in persistentPropertyBag:
                #
                # persistent properties are set
                # 
                self.propertyBag[property.getName()] = property
    """
    def setPersistentPropertyBag(self, persistentPropertyBag):
        """
        Descript. :
        """
        self.propertyBag = persistentPropertyBag
        
    def sizeHint(self):
        """
        Descript. :
        """
        return QtCore.QSize(100, 100)  

    def run(self):
        """
        Descript. :
        """
        self.hide()

    def stop(self):
        """
        Descript. :
        """
        self.show()

    def paintEvent(self, event):
        """
        Descript. :
        """
        if not self.isRunning():
            p = QtGui.QPainter(self)
            p.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            p.drawLine(0, 0, self.width(), self.height())
            p.drawLine(0, self.height(), self.width(), 0)
  
class ProcedureBrick(BlissWidget):
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        self.__pages = []

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('equipment', 'string', '')

        #
        # create GUI elements
        #
        from BlissFramework.Utils.RunStopPanel import RunStopPanel
        self.procedureTab = QTabWidget(self)
        self.runStopPanel = RunStopPanel(self)
     
        #
        # configure GUI elements
        #
        self.procedureTab.setTabShape(QTabWidget.Triangular)

        #
        # connect signals / slots
        #
        self.connect(self.runStopPanel, PYSIGNAL('launch'), self.launchProcedure)
        self.connect(self.runStopPanel, PYSIGNAL('stop'), self.stopProcedure)

        #
        # layout
        #
        ##self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        QVBoxLayout(self, 10, 10)
        self.layout().addWidget(self.procedureTab, 0)
        self.layout().addWidget(self.runStopPanel, 0, Qt.AlignRight | Qt.AlignBottom)        

    def setMnemonic(self, mne):
        """
        Descript. :
        """
        self.getProperty('mnemonic').setValue(mne)

 	proc = HardwareRepository.HardwareRepository().getProcedure(mne)

	self.__setProcedure(proc)

    def __setProcedure(self, proc):
        """
        Descript. :
        """
        for p in self.__pages:
            p.setProcedure(proc)

        self.setProcedure(proc)
        
    def setProcedure(self, proc):
        """
        Descript. :
        """
        pass

    def setEquipmentMnemonic(self, mne):
        """
        Descript. :
        """
        self.getProperty('equipment').setValue(mne)
        
        e = self.getHardwareObject(mne)
        
        self.setEquipment(e)

    def setEquipment(self, equipment):
        """
        Descript. :
        """
        pass
        
    def launchProcedure(self):
        """
        Descript. :
        """
        pass

    def stopProcedure(self):
        """
        Descript. :
        """
        pass

    def dataFileChanged(self, filename):
        """
        Descript. :
        """
        pass
    
    def addPage(self, pageName):
        """
        Descript. :
        """
        self.__pages.append(Qt4_ProcedureWidgets.ProcedurePanel(self))
        self.__pages[-1].setProcedure(HardwareRepository.HardwareRepository().\
             getProcedure(self['mnemonic']))
        self.procedureTab.addTab(self.__pages[-1], pageName)

        return self.__pages[-1]

    def showPage(self, page):
        """
        Descript. :
        """
        self.procedureTab.showPage(page)
        
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'mnemonic':
       	    self.setMnemonic(new_value) #Procedure(HardwareRepository.HardwareRepository().getHardwareObject(newValue))
        elif property_name == 'equipment':
            self.setEquipment(self.getHardwareObject(new_value))


def ComboBoxActivated(self, index, lines):
    """
    Descript. :
    """
    if self.editable():
        #lines=state[1]
        last=self.count()
        if index>=last:
            i=index
            while True:
                try:
                    line=lines[i]
                except:
                    break
                else:
                    self.insertItem(line)
                    self.setCurrentItem(i)
                    self.emit(QtCore.SIGNAL('activated(const QString &)'), line)
                    self.emit(QtCore.SIGNAL('activated(int)'), i)
                i+=1
    self.setCurrentItem(index)
    self.emit(QtCore.SIGNAL('activated(const QString &)'), self.currentText())
    self.emit(QtCore.SIGNAL('activated(int)'), index)

def SpinBoxEditorTextChanged(self, t):
    """
    Descript. :
    """
    self.emit(QtCore.SIGNAL('editorTextChanged'), str(t))

def SpinBoxSetEditorText(self, t):
    """
    Descript. :
    """
    self.editor().setText(t)
