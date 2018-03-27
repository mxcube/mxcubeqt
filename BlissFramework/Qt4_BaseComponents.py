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
import os
import sys
import time
import operator
import weakref

from QtImport import *

import BlissFramework
from BlissFramework.Utils import Qt4_widget_colors

from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import HardwareObject
from BlissFramework.Utils import PropertyBag
from BlissFramework.Utils import Connectable
from BlissFramework import get_splash_screen

try:
    from louie import dispatcher
    from louie import saferef
except ImportError:
    from pydispatch import dispatcher
    from pydispatch import saferef
    saferef.safe_ref = saferef.safeRef


_emitterCache = weakref.WeakKeyDictionary()


class _QObject(QObject):
    def __init__(self, *args, **kwargs):
        """
        Descript. :
        """
        QObject.__init__(self, *args)

        try:
            self.__ho = weakref.ref(kwargs.get("ho"))
        except:
            self.__ho = None

def emitter(ob):
    """Returns a QObject surrogate for *ob*, to use in Qt signaling.
       This function enables you to connect to and emit signals
       from (almost) any python object with having to subclass QObject.
    """
    if ob not in _emitterCache:
        _emitterCache[ob] = _QObject(ho=ob)
    return _emitterCache[ob]


class InstanceEventFilter(QObject):
    def eventFilter(self, widget, event):
        """
        Descript. :
        """
        obj = widget
        while obj is not None:
            if isinstance(obj, BlissWidget):
                if isinstance(event, QContextMenuEvent):
                    #if obj.shouldFilterEvent():
                    return True
                elif isinstance(event, QMouseEvent):
                    if event.button() == Qt.RightButton:
                        return True
                    elif obj.shouldFilterEvent():
                        return True
                elif isinstance(event, QKeyEvent) \
                or isinstance(event, QFocusEvent):
                    if obj.shouldFilterEvent():
                        return True
                return QObject.eventFilter(self, widget, event)
            try:
                obj = obj.parent()
            except:
                obj = None
        return QObject.eventFilter(self, widget, event)

class WeakMethodBound:
    def __init__(self, f):
        """
        Descript. :
        """
        self.f = weakref.ref(f.__func__)
        self.c = weakref.ref(f.__self__)

    def __call__(self, *args):
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
    def __init__(self, f):
        """Descript. : """
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
        f.__func__
    except AttributeError:
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
                BlissWidget._eventsCache[self.slot] = \
                    (time.time(), self.slot, args)
                return

        s = self.slot()
        if s is not None:
            s(*args)


class BlissWidget(Connectable.Connectable, QFrame):
    (INSTANCE_ROLE_UNKNOWN, INSTANCE_ROLE_SERVER, INSTANCE_ROLE_SERVERSTARTING,
     INSTANCE_ROLE_CLIENT, INSTANCE_ROLE_CLIENTCONNECTING) = (0, 1, 2, 3, 4)
    (INSTANCE_MODE_UNKNOWN, INSTANCE_MODE_MASTER, INSTANCE_MODE_SLAVE) = (0, 1, 2)
    (INSTANCE_LOCATION_UNKNOWN, INSTANCE_LOCATION_LOCAL,
     INSTANCE_LOCATION_INHOUSE, INSTANCE_LOCATION_INSITE,
     INSTANCE_LOCATION_EXTERNAL) = (0, 1, 2, 3, 4)
    (INSTANCE_USERID_UNKNOWN, INSTANCE_USERID_LOGGED, INSTANCE_USERID_INHOUSE,
     INSTANCE_USERID_IMPERSONATE) = (0, 1, 2, 3)
    (INSTANCE_MIRROR_UNKNOWN, INSTANCE_MIRROR_ALLOW, INSTANCE_MIRROR_PREVENT) = (0, 1, 2)

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
    _statusBar = None
    _progressBar = None

    _applicationEventFilter = InstanceEventFilter(None)

    widgetSynchronizeSignal = pyqtSignal([])

    @staticmethod
    def setRunMode(mode):
        """
        Descript. :
        """
        if mode:
            BlissWidget._runMode = True
            for widget in QApplication.allWidgets():
                if isinstance(widget, BlissWidget):
                    widget.__run()
                    try:
                        widget.set_expert_mode(False)
                    except:
                        logging.getLogger().exception(\
                           "Could not set %s to user mode", widget.name())

        else:
            BlissWidget._runMode = False
            for widget in QApplication.allWidgets():
                if isinstance(widget, BlissWidget):
                    widget.__stop()
                    try:
                        widget.set_expert_mode(True)
                    except:
                        logging.getLogger().exception(\
                           "Could not set %s to expert mode", widget.name())

    @staticmethod
    def isRunning():
        """
        Descript. :
        """
        return BlissWidget._runMode

    @staticmethod
    def update_menu_bar_color(enable_checkbox=None):
        """
        Descript. : Not a direct way how to change menubar color
                    it is now done by changing stylesheet
        """
        color = None
        if BlissWidget._menuBar is not None:
            BlissWidget._menuBar.parent.update_instance_caption("")
            if BlissWidget._instanceMode == \
               BlissWidget.INSTANCE_MODE_MASTER:
                if BlissWidget._instanceUserId == \
                   BlissWidget.INSTANCE_USERID_IMPERSONATE:
                    color = "lightBlue"
                else:
                    color = "rgb(204,255,204)"
            elif BlissWidget._instanceMode == \
                 BlissWidget.INSTANCE_MODE_SLAVE:
                BlissWidget._menuBar.parent.update_instance_caption(\
                    " : slave instance (all controls are disabled)")
                if BlissWidget._instanceRole == \
                   BlissWidget.INSTANCE_ROLE_CLIENTCONNECTING:
                    color = "rgb(255,204,204)"
                elif BlissWidget._instanceUserId == \
                     BlissWidget.INSTANCE_USERID_UNKNOWN:
                    color = "rgb(255, 165, 0)"
                else:
                    color = "yellow"

        if color is not None:
            BlissWidget._menuBar.set_color(color)

    @staticmethod
    def set_instance_mode(mode):
        """
        Descript. :
        """
        BlissWidget._instanceMode = mode
        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                #try:
                if True:
                    widget._instanceModeChanged(mode)
                    if widget['instanceAllowAlways']:
                        widget.setEnabled(True)
                    else:
                        widget.setEnabled(\
                          mode == BlissWidget.INSTANCE_MODE_MASTER)
                #except:
                #    pass
        if BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_MASTER:
            if BlissWidget._filterInstalled:
                QApplication.instance().removeEventFilter(\
                     BlissWidget._applicationEventFilter)
                BlissWidget._filterInstalled = False
                BlissWidget.synchronize_with_cache() # why?
        else:
            if not BlissWidget._filterInstalled:
                QApplication.instance().installEventFilter(\
                     BlissWidget._applicationEventFilter)
                BlissWidget._filterInstalled = True

        BlissWidget.update_menu_bar_color(BlissWidget._instanceMode == \
                    BlissWidget.INSTANCE_MODE_MASTER)

    @staticmethod
    def set_status_info(info_type, info_message, info_status=""):
        """Updates status bar"""
        if BlissWidget._statusBar:
            BlissWidget._statusBar.parent().update_status_info(\
                 info_type, info_message, info_status)

    @staticmethod
    def init_progress_bar(progress_type, number_of_steps):
        """Updates status bar"""
        if BlissWidget._statusBar:
            BlissWidget._statusBar.parent().init_progress_bar(progress_type, number_of_steps)

    @staticmethod
    def set_progress_bar_step(step):
        """Updates status bar"""
        if BlissWidget._statusBar:
            BlissWidget._statusBar.parent().set_progress_bar_step(step)

    @staticmethod
    def stop_progress_bar():
        """Updates status bar"""
        if BlissWidget._statusBar:
            BlissWidget._statusBar.parent().stop_progress_bar()

    @staticmethod
    def open_progress_dialog(msg, max_steps):
        if BlissWidget._progressDialog:
            BlissWidget._progressDialog.parent().open_progress_dialog(msg, max_steps)

    @staticmethod
    def set_progress_dialog_step(step, msg):
        if BlissWidget._progressDialog:
            BlissWidget._progressDialog.parent().set_progress_dialog_step(step, msg)

    @staticmethod
    def close_progress_dialog():
        if BlissWidget._progressDialog:
            BlissWidget._progressDialog.parent().close_progress_dialog()

    @staticmethod
    def set_user_file_directory(user_file_directory):
        BlissWidget.user_file_directory = user_file_directory

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

            connected = BlissWidget._instanceRole in (\
                  BlissWidget.INSTANCE_ROLE_SERVER,
                  BlissWidget.INSTANCE_ROLE_CLIENT)
            if allow_connected and connected:
                return False
            return True

        return False

    def connect_group_box(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.toggled.connect(lambda \
             s: BlissWidget.widgetGroupBoxToggled(brick_name, \
             widget_name, master_sync, s))

    def connect_combobox(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.activated.connect(lambda \
             i: BlissWidget.widget_combobox_activated(brick_name, \
             widget_name, widget, master_sync, i))

    def connect_line_edit(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.textChanged.connect(lambda \
             t: BlissWidget.widget_line_edit_text_changed(\
             brick_name, widget_name, master_sync, t))

    def connect_spinbox(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.valueChanged.connect(lambda \
             t: BlissWidget.widget_spinbox_value_changed(\
             brick_name, widget_name, master_sync, t))

    def connect_double_spinbox(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.valueChanged.connect(lambda \
             t: BlissWidget.widget_double_spinbox_value_changed(\
             brick_name, widget_name, master_sync, t))

    def connect_generic_widget(self, widget, widget_name, master_sync):
        """
        Descript. :
        """
        brick_name = self.objectName()
        widget.widgetSynchronize.connect(lambda \
             state: BlissWidget.widgetGenericChanged(brick_name, widget_name, \
             master_sync, state))

    def _instanceModeChanged(self, mode):
        """
        Descript. :
        """
        for widget, widget_name, master_sync in self._widget_events:
            if isinstance(widget, QGroupBox):
                self.connect_group_box(widget, widget_name, master_sync)
            elif isinstance(widget, QComboBox):
                self.connect_combobox(widget, widget_name, master_sync)
            elif isinstance(widget, QLineEdit):
                self.connect_line_edit(widget, widget_name, master_sync)
            elif isinstance(widget, QSpinBox):
                self.connect_spinbox(widget, widget_name, master_sync)
            elif isinstance(widget, QDoubleSpinBox):
                self.connect_double_spinbox(widget, widget_name, master_sync)
            else:
                ### verify if widget has the widgetSynchronize method!!!
                self.connect_generic_widget(widget, widget_name, master_sync)
        self._widget_events = []

        if self.shouldFilterEvent():
            self.setCursor(QCursor(Qt.ForbiddenCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    @staticmethod
    def isInstanceModeMaster():
        """
        Descript. :
        """
        return BlissWidget._instanceMode == \
               BlissWidget.INSTANCE_MODE_MASTER

    @staticmethod
    def isInstanceModeSlave():
        """
        Descript. :
        """
        return BlissWidget._instanceMode == \
               BlissWidget.INSTANCE_MODE_SLAVE

    @staticmethod
    def isInstanceRoleUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceRole == \
               BlissWidget.INSTANCE_ROLE_UNKNOWN

    @staticmethod
    def isInstanceRoleClient():
        """
        Descript. :
        """
        return BlissWidget._instanceRole == \
               BlissWidget.INSTANCE_ROLE_CLIENT

    @staticmethod
    def isInstanceRoleServer():
        """
        Descript. :
        """
        return BlissWidget._instanceRole == \
               BlissWidget.INSTANCE_ROLE_SERVER

    @staticmethod
    def isInstanceUserIdUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId == \
               BlissWidget.INSTANCE_USERID_UNKNOWN

    @staticmethod
    def isInstanceUserIdLogged():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId == \
               BlissWidget.INSTANCE_USERID_LOGGED

    @staticmethod
    def isInstanceUserIdInhouse():
        """
        Descript. :
        """
        return BlissWidget._instanceUserId == \
               BlissWidget.INSTANCE_USERID_INHOUSE

    @staticmethod
    def set_instance_role(role):
        """
        Descript. :
        """
        if role == BlissWidget._instanceRole:
            return
        BlissWidget._instanceRole = role
        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                #try:
                widget.instanceRoleChanged(role)
                #except:
                #    pass

    @staticmethod
    def setInstanceLocation(location):
        """
        Descript. :
        """
        if location == BlissWidget._instanceLocation:
            return
        BlissWidget._instanceLocation = location
        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                #try:
                widget.instanceLocationChanged(location)
                #except:
                #    pass

    @staticmethod
    def setInstanceUserId(user_id):
        """
        Descript. :
        """
        if user_id == BlissWidget._instanceUserId:
            return
        BlissWidget._instanceUserId = user_id

        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                #try:
                widget.instanceUserIdChanged(user_id)
                #except:
                #    pass
        BlissWidget.update_menu_bar_color()

    @staticmethod
    def set_instance_mirror(mirror):
        """
        Descript. :
        """
        if mirror == BlissWidget._instanceMirror:
            return
        BlissWidget._instanceMirror = mirror

        if mirror == BlissWidget.INSTANCE_MIRROR_ALLOW:
            BlissWidget.synchronize_with_cache()

        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                widget.instanceMirrorChanged(mirror)

    def instanceMirrorChanged(self, mirror):
        """
        Descript. :
        """
        pass

    def instanceLocationChanged(self, location):
        """
        Descript. :
        """
        pass

    @staticmethod
    def isInstanceLocationUnknown():
        """
        Descript. :
        """
        return BlissWidget._instanceLocation == \
               BlissWidget.INSTANCE_LOCATION_UNKNOWN

    @staticmethod
    def isInstanceLocationLocal():
        """
        Descript. :
        """
        return BlissWidget._instanceLocation == \
               BlissWidget.INSTANCE_LOCATION_LOCAL

    @staticmethod
    def isInstanceMirrorAllow():
        """
        Descript. :
        """
        return BlissWidget._instanceMirror == \
               BlissWidget.INSTANCE_MIRROR_ALLOW

    def instanceUserIdChanged(self, user_id):
        """
        Descript. :
        """
        pass

    def instanceRoleChanged(self, role):
        """
        Descript. :
        """
        pass

    @staticmethod
    def updateWhatsThis():
        """
        Descript. :
        """
        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                msg = "%s (%s)\n%s" % (widget.objectName(),
                                       widget.__class__.__name__,
                                       widget.getHardwareObjectsInfo())
                widget.setWhatsThis(msg)
        QWhatsThis.enterWhatsThisMode()

    @staticmethod
    def update_widget(brick_name, widget_name, method_name,
                      method_args, master_sync):
        """Updates widget
        """
        for widget in QApplication.allWidgets():
            if hasattr(widget, "configuration"):
                top_level_widget = widget
                break
        if not master_sync or BlissWidget._instanceMode == \
                              BlissWidget.INSTANCE_MODE_MASTER:
            top_level_widget.brickChangedSignal.emit(brick_name,
                                                     widget_name,
                                                     method_name,
                                                     method_args,
                                                     master_sync)

    @staticmethod
    def update_tab_widget(tab_name, tab_index):
        """
        Descript. :
        """
        if BlissWidget._instanceMode == BlissWidget.INSTANCE_MODE_MASTER:
            for widget in QApplication.allWidgets():
                if hasattr(widget, "configuration"):
                    widget.tabChangedSignal.emit(tab_name, tab_index)

    @staticmethod
    def widgetGroupBoxToggled(brick_name, widget_name, master_sync, state):
        """
        Descript. :
        """
        BlissWidget.updateWidget(brick_name,
                                 widget_name,
                                 "setChecked",
                                 (state,),
                                 master_sync)

    @staticmethod
    def widget_combobox_activated(brick_name, widget_name, widget, master_sync, index):
        """
        Descript. :
        """
        lines = []
        if widget.isEditable():
            for index in range(widget.count()):
                lines.append(str(widget.itemText(index)))
        BlissWidget.update_widget(brick_name,
                                  widget_name,
                                  "setCurrentIndex",
                                  (index, ),
                                  master_sync)

    @staticmethod
    def widget_line_edit_text_changed(brick_name, widget_name, master_sync, text):
        """
        Descript. :
        """
        BlissWidget.update_widget(brick_name,
                                  widget_name,
                                  "setText",
                                  (text, ),
                                  master_sync)

    @staticmethod
    def widget_spinbox_value_changed(brick_name, widget_name, master_sync, text):
        """
        Descript. :
        """
        BlissWidget.update_widget(brick_name,
                                  widget_name,
                                  "setValue",
                                  (int(text), ),
                                  master_sync)

    @staticmethod
    def widget_double_spinbox_value_changed(brick_name, widget_name, master_sync, text):
        """
        Descript. :
        """
        BlissWidget.update_widget(brick_name,
                                  widget_name,
                                  "setValue",
                                  (float(text), ),
                                  master_sync)

    @staticmethod
    def widgetGenericChanged(brick_name, widget_name, master_sync, state):
        """
        Descript. :
        """
        BlissWidget.update_widget(brick_name,
                                 widget_name,
                                 "widget_synchronize",
                                 (state,),
                                 master_sync)

    def instance_forward_events(self, widget_name, master_sync):
        """
        Descript. :
        """
        if widget_name == "":
            widget = self
        else:
            widget = getattr(self, widget_name)
        self._widget_events.append((widget, widget_name, master_sync))

    def instance_synchronize(self, *args, **kwargs):
        """
        Descript. :
        """
        for widget_name in args:
            self.instance_forward_events(widget_name,
                                         kwargs.get("master_sync", True))

    @staticmethod
    def shouldRunEvent():
        """
        Descript. :
        """
        return BlissWidget._instanceMirror == \
               BlissWidget.INSTANCE_MIRROR_ALLOW

    @staticmethod
    def addEventToCache(timestamp, method, *args):
        """
        Descript. :
        """
        try:
            method_to_add = WeakMethod(method)
        except TypeError:
            methos_to_add = method
        BlissWidget._eventsCache[m] = (timestamp, methos_to_add, args)

    @staticmethod
    def synchronize_with_cache():
        """
        Descript. :
        """
        events = list(BlissWidget._eventsCache.values())
        ordered_events = sorted(events, key=operator.itemgetter(0))
        for event_timestamp, event_method, event_args in ordered_events:
            try:
                method = event_method()
                if method is not None:
                    method(*event_args)
            except:
                pass
        BlissWidget._eventsCache = {}

    @staticmethod
    def set_gui_enabled(enabled):
        for widget in QApplication.allWidgets():
            if isinstance(widget, BlissWidget):
                widget.setEnabled(enabled)

    def __init__(self, parent=None, widget_name=''):
        """
        Descript. :
        """
        Connectable.Connectable.__init__(self)
        QFrame.__init__(self, parent)
        self.setObjectName(widget_name)
        self.property_bag = PropertyBag.PropertyBag()

        self.__enabledState = True
        self.__loaded_hardware_objects = []
        self.__failed_to_load_hwobj = False
        self.__use_progress_dialog = False
        self._signal_slot_filters = {}
        self._widget_events = []

        self.setWhatsThis("%s (%s)\n" % (widget_name, self.__class__.__name__))

        self.addProperty('fontSize',
                         'string',
                         str(self.font().pointSize()))
        self.addProperty('frame',
                         'boolean',
                         False,
                         comment="Draw a frame around the widget")
        self.addProperty('instanceAllowAlways',
                         'boolean',
                         False,
                         comment="Allow to control brick in all modes")
        self.addProperty('instanceAllowConnected',
                         'boolean',
                         False,
                         comment="Allow to control brick in slave mode")
        self.addProperty('fixedWidth',
                         'integer',
                         '-1',
                         comment="Set fixed width in pixels")
        self.addProperty('fixedHeight',
                         'integer',
                         '-1',
                         comment="Set fixed height in pixels")
        self.addProperty('hide',
                         'boolean',
                         False,
                         comment="Hide widget")

        dispatcher.connect(self.__hardwareObjectDiscarded,
                           'hardwareObjectDiscarded',
                           HardwareRepository.HardwareRepository())
        self.defineSlot('enable_widget', ())
        self.defineSlot('disable_widget', ())

        #If PySide used then connect method was not overriden
        #This solution of redirecting methods works...

        self.connect = self.connect_hwobj
        self.diconnect = self.disconnect_hwobj
        #self.run_mode = QPushButton("Run mode", self)

    def __run(self):
        """
        Descript. :
        """
        self.setAcceptDrops(False)
        self.blockSignals(False) 
        self.setEnabled(self.__enabledState)
        #self.run_mode_pushbutton = QPushButton("Simulation", self)

        try:
            self.run()
        except:
            logging.getLogger().exception(\
               "Could not set %s to run mode", self.objectName())

    def __stop(self):
        """
        Descript. :
        """
        self.blockSignals(True)

        try:
            self.stop()
        except:
            logging.getLogger().exception(\
               "Could not stop %s", self.objectName())

        #self.setAcceptDrops(True)
        self.__enabledState = self.isEnabled()
        QWidget.setEnabled(self, True)

    def __repr__(self):
        """
        Descript. :
        """
        return repr("<%s: %s>" % (self.__class__, self.objectName()))

    def connectSignalSlotFilter(self, sender, signal, slot, should_cache):
        """
        Descript. :
        """
        uid = (sender, signal, hash(slot))
        signal_slot_filter = SignalSlotFilter(signal, slot, should_cache)
        self._signal_slot_filters[uid] = signal_slot_filter

        QObject.connect(sender, signal, signal_slot_filter)

    def connect_hwobj(self, sender, signal, slot, instanceFilter=False, shouldCache=True):
        """
        Descript. :
        """
        if sys.version_info > (3, 0):
            signal = str(signal.decode('utf8') if \
                     type(signal) == bytes else signal)
        else:
            signal = str(signal)

        if signal[0].isdigit():
            pysignal = signal[0] == '9'
            signal = signal[1:]
        else:
            pysignal = True

        if not isinstance(sender, QObject):
            if isinstance(sender, HardwareObject):
                sender.connect(signal, slot)
                return
            else:
                _sender = emitter(sender)
        else:
            _sender = sender

        if instanceFilter:
            self.connectSignalSlotFilter(_sender,
                                         pysignal and \
                                         SIGNAL(signal) or \
                                         SIGNAL(signal),
                                         slot, shouldCache)
        else:
            #Porting to Qt5
            getattr(_sender, signal).connect(slot)

            #QtCore.QObject.connect(_sender,
            #                       pysignal and \
            #                       QtCore.SIGNAL(signal) or \
            #                       QtCore.SIGNAL(signal),
            #                       slot)

        # workaround for PyQt lapse
        print "TODO workaround for PyQt lapse" 
        #if hasattr(sender, "connectNotify"):
        #    sender.connectNotify(QtCore.pyqtSignal(signal))

    def disconnect_hwobj(self, sender, signal, slot):
        """
        Descript. :
        """
        signal = str(signal)
        if signal[0].isdigit():
            pysignal = signal[0] == '9'
            signal = signal[1:]
        else:
            pysignal = True

        if isinstance(sender, HardwareObject):
            sender.disconnect(sender, signal, slot)
            return

        # workaround for PyQt lapse
        if hasattr(sender, "disconnectNotify"):
            sender.disconnectNotify(signal)

        if not isinstance(sender, QObject):
            sender = emitter(sender)

            try:
                uid = (sender, pysignal and QtCore.SIGNAL(signal) or \
                       QtCore.SIGNAL(signal), hash(slot))
                signalSlotFilter = self._signal_slot_filters[uid]
            except KeyError:
                QtCore.QObject.disconnect(sender,
                                          pysignal and \
                                          QtCore.SIGNAL(signal) or \
                                          QtCore.SIGNAL(signal),
                                          slot)
            else:
                QtCore.QObject.disconnect(sender,
                                          pysignal and \
                                          QtCore.SIGNAL(signal) or \
                                          QtCore.SIGNAL(signal),
                                          signalSlotFilter)
                del self._signal_slot_filters[uid]
        else:
            QtCore.QObject.disconnect(sender,
                                      pysignal and \
                                      QtCore.SIGNAL(signal) or \
                                      QtCore.SIGNAL(signal),
                                      signalSlotFilter)

    """
    def get_signals(self):
        signals = []
        for name in dir(self):
            if isinstance(getattr(self, name),  pyqtSignal):
                signals.append(name)
        return signals

    def get_slots(self):
        slots = []
        cls = self if isinstance(self, type) else type(self)
        slot = type(pyqtSignal())
        for name in dir(self):
            if isinstance(getattr(cls, name), slot):
                slots.append(name)
        return slots
    """

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
        for path in [BlissFramework.getStdBricksPath()] + \
                     BlissFramework.getCustomBricksDirs():
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
                self.removeChild(child)

            layout = QGridLayout(self, 1, 1)
            widget.reparent(self)
            widget.show()
            layout.addWidget(widget, 0, 0)
            self.setLayout(layout)
            return widget

    def setPersistentPropertyBag(self, persistent_property_bag):
        """
        Descript. :
        """
        if id(persistent_property_bag) != id(self.property_bag):
            for prop in persistent_property_bag:
                if hasattr(prop, "getName"):
                    if prop.getName() in self.property_bag.properties:
                        self.property_bag.getProperty(prop.getName()).\
                             setValue(prop.getUserValue())
                    elif prop.hidden:
                        self.property_bag[prop.getName()] = prop
                else:
                    if prop["name"] in self.property_bag.properties:
                        self.property_bag.getProperty(prop["name"]).\
                             setValue(prop["value"])
                    elif prop["hidden"]:
                        self.property_bag[prop["name"]] = prop

        self.readProperties()

    def readProperties(self):
        """
        Descript. :
        """
        for prop in self.property_bag:
            self._propertyChanged(prop.getName(), None, prop.getUserValue())

    def addProperty(self, *args, **kwargs):
        """
        Descript. :
        """
        self.property_bag.addProperty(*args, **kwargs)

    def getProperty(self, property_name):
        """
        Descript. :
        """
        return self.property_bag.getProperty(property_name)

    def showProperty(self, property_name):
        """
        Descript. :
        """
        return self.property_bag.showProperty(property_name)

    def hideProperty(self, property_name):
        """
        Descript. :
        """
        return self.property_bag.hideProperty(property_name)

    def delProperty(self, property_name):
        """
        Descript. :
        """
        return self.property_bag.delProperty(property_name)

    def getHardwareObject(self, hardware_object_name, optional=False):
        """
        Descript. :
        """
        if not hardware_object_name in self.__loaded_hardware_objects:
            self.__loaded_hardware_objects.append(hardware_object_name)

        hwobj = HardwareRepository.HardwareRepository().\
                   getHardwareObject(hardware_object_name)

        if hwobj is not None: 
            self.connect(hwobj,
                         "progressInit",
                         self.progress_init)
            self.connect(hwobj,
                         'progressStep',
                         self.progress_step)
            self.connect(hwobj,
                         'progressStop',
                         self.progress_stop)

        if hwobj is None and not optional:
            logging.getLogger("GUI").error(\
               "Unable to initialize hardware: %s.xml. " % hardware_object_name[1:] + \
               "If the restarting of MXCuBE do not help, " + \
               "please contact your local support.")
            self.set_background_color(Qt4_widget_colors.LIGHT_RED)
            self.__failed_to_load_hwobj = True
            self.setDisabled(True)

        return hwobj
            

    def progress_init(self, progress_type, number_of_steps, use_dialog=False):
        self.__use_progress_dialog = use_dialog
        if self.__use_progress_dialog:
            BlissWidget.open_progress_dialog(progress_type, number_of_steps)

    def progress_step(self, step, msg=None):
        if self.__use_progress_dialog:
            BlissWidget.set_progress_dialog_step(step, msg)

    def progress_stop(self):
        if self.__use_progress_dialog:
            BlissWidget.close_progress_dialog()

    def __hardwareObjectDiscarded(self, hardware_object_name):
        """
        Descript. :
        """
        if hardware_object_name in self.__loaded_hardware_objects:
            # there is a high probability we need to reload this hardware object...
            self.readProperties() #force to read properties

    def getHardwareObjectsInfo(self):
        """
        Descript. :
        """
        d = {}
        for ho_name in self.__loaded_hardware_objects:
            info = HardwareRepository.HardwareRepository().getInfo(ho_name)

            if len(info) > 0:
                d[ho_name] = info

        if len(d):
            return "Hardware Objects:\n\n%s" % pprint.pformat(d)
        else:
            return ""

    def __getitem__(self, property_name):
        """Direct access to properties values
        """
        return self.property_bag[property_name]

    def __setitem__(self, property_name, value):
        """
        Descript. :
        """
        property_bag = self.property_bag.getProperty(property_name)
        old_value = property_bag.getValue()
        property_bag.setValue(value)

        self._propertyChanged(property_name,
                              old_value,
                              property_bag.getUserValue())

    def _propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'fontSize':
            try:
                font_size = int(new_value)
            except:
                self.getProperty('fontSize').setValue(self.font().pointSize())
            else:
                font = self.font()
                font.setPointSize(font_size)
                self.setFont(font)

                for brick in self.children():
                    if isinstance(brick, BlissWidget):
                        brick["fontSize"] = font_size
                self.update()
        elif property_name == 'frame':
            try:
                if new_value:
                    self.setFrameStyle(QFrame.StyledPanel)
                else:
                    self.setFrameStyle(QFrame.NoFrame)
            except:
                pass
            self.update()
        elif property_name == 'fixedWidth':
            if new_value > -1:
                self.setFixedWidth(new_value)
        elif property_name == 'fixedHeight':
            if new_value > -1:
                self.setFixedHeight(new_value)
        elif property_name == 'hide':
            if new_value:
                self.setHidden(True)
        else:
            try:
                self.propertyChanged(property_name, old_value, new_value)
            except:
                logging.getLogger().exception(
                     "Error while setting property %s " % property_name + \
                     "for %s (details in log file)." % str(self.objectName()))

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
        if self.__failed_to_load_hwobj:
            state = False       
 
        if state:
            self.setEnabled(True)
        else:
            self.setDisabled(True)

    def disable_widget(self, state):
        """
        Descript. :
        """
        if self.__failed_to_load_hwobj:
            state = True 

        if state:
            self.setDisabled(True)
        else:
            self.setEnabled(True)

    def get_window_display_widget(self):
        for widget in QApplication.allWidgets():
            if hasattr(widget, "configuration"):
                return widget

    def set_background_color(self, color):
        Qt4_widget_colors.set_widget_color(self,
                                           color,
                                           QPalette.Background)

class NullBrick(BlissWidget):

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        self.property_bag = PropertyBag.PropertyBag()

    def setPersistentPropertyBag(self, persistent_property_bag):
        """
        Descript. :
        """
        self.property_bag = persistent_property_bag

    def sizeHint(self):
        """
        Descript. :
        """
        return QSize(100, 100)

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
            painter = QPainter(self)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)

def ComboBoxActivated(self, index, lines):
    """
    Descript. :
    """
    if self.editable():
        #lines=state[1]
        last = self.count()
        if index >= last:
            i = index
            while True:
                try:
                    line = lines[i]
                except:
                    break
                else:
                    self.insertItem(line)
                    self.setCurrentItem(i)
                    self.activated[str].emit(line)
                    self.activated[int].emit(i)
                i += 1
    self.setCurrentItem(index)
    self.activated[str].emit(self.currentText())
    self.activated[int].emit(index)

def SpinBoxEditorTextChanged(self, text):
    """
    Descript. :
    """
    self.editorTextChanged.emit(str(text))

def SpinBoxSetEditorText(self, text):
    """
    Descript. :
    """
    self.editor().setText(text)
