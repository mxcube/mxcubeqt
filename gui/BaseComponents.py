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

import logging
import pprint
import os
import sys
import time
import operator
import weakref

import gui
from gui.utils import PropertyBag, Connectable, Colors, QtImport

from HardwareRepository import HardwareRepository as HWR
from HardwareRepository.BaseHardwareObjects import HardwareObject

try:
    from louie import dispatcher
    from louie import saferef
except ImportError:
    from pydispatch import dispatcher
    from pydispatch import saferef

    saferef.safe_ref = saferef.safeRef


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


_emitter_cache = weakref.WeakKeyDictionary()


class _QObject(QtImport.QObject):
    def __init__(self, *args, **kwargs):
        QtImport.QObject.__init__(self, *args)

        try:
            self.__ho = weakref.ref(kwargs.get("ho"))
        except BaseException:
            self.__ho = None


def emitter(ob):
    """Returns a QObject surrogate for *ob*, to use in Qt signaling.
       This function enables you to connect to and emit signals
       from (almost) any python object with having to subclass QObject.
    """
    if ob not in _emitter_cache:
        _emitter_cache[ob] = _QObject(ho=ob)
    return _emitter_cache[ob]


class InstanceEventFilter(QtImport.QObject):
    def eventFilter(self, widget, event):
        obj = widget
        while obj is not None:
            if isinstance(obj, BaseWidget):
                if isinstance(event, QtImport.QContextMenuEvent):
                    # if obj.should_filter_event():
                    return True
                elif isinstance(event, QtImport.QMouseEvent):
                    if event.button() == QtImport.Qt.RightButton:
                        return True
                    elif obj.should_filter_event():
                        return True
                elif isinstance(event, (QtImport.QKeyEvent, QtImport.QFocusEvent)):
                    if obj.should_filter_event():
                        return True

                return QtImport.QObject.eventFilter(self, widget, event)
            try:
                obj = obj.parent()
            except BaseException:
                obj = None
        return QtImport.QObject.eventFilter(self, widget, event)


class WeakMethodBound:
    def __init__(self, f):
        self.f = weakref.ref(f.__func__)
        self.c = weakref.ref(f.__self__)

    def __call__(self, *args):
        obj = self.c()
        if obj is None:
            return None
        else:
            f = self.f()
            return f.__get__(obj)


class WeakMethodFree:
    def __init__(self, f):
        self.f = weakref.ref(f)

    def __call__(self, *args):
        return self.f()


def WeakMethod(f):
    try:
        f.__func__
    except AttributeError:
        return WeakMethodFree(f)
    return WeakMethodBound(f)


class SignalSlotFilter:
    def __init__(self, signal, slot, should_cache):
        self.signal = signal
        self.slot = WeakMethod(slot)
        self.should_cache = should_cache

    def __call__(self, *args):
        if (
                BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_SLAVE
                and BaseWidget._instance_mirror == BaseWidget.INSTANCE_MIRROR_PREVENT
           ):
            if self.should_cache:
                BaseWidget._events_cache[self.slot] = (time.time(), self.slot, args)
                return

        s = self.slot()
        if s is not None:
            s(*args)


class BaseWidget(Connectable.Connectable, QtImport.QFrame):
    """Base class for MXCuBE bricks"""

    (
        INSTANCE_ROLE_UNKNOWN,
        INSTANCE_ROLE_SERVER,
        INSTANCE_ROLE_SERVERSTARTING,
        INSTANCE_ROLE_CLIENT,
        INSTANCE_ROLE_CLIENTCONNECTING,
    ) = (0, 1, 2, 3, 4)
    (INSTANCE_MODE_UNKNOWN, INSTANCE_MODE_MASTER, INSTANCE_MODE_SLAVE) = (0, 1, 2)
    (
        INSTANCE_LOCATION_UNKNOWN,
        INSTANCE_LOCATION_LOCAL,
        INSTANCE_LOCATION_INHOUSE,
        INSTANCE_LOCATION_INSITE,
        INSTANCE_LOCATION_EXTERNAL,
    ) = (0, 1, 2, 3, 4)
    (
        INSTANCE_USERID_UNKNOWN,
        INSTANCE_USERID_LOGGED,
        INSTANCE_USERID_INHOUSE,
        INSTANCE_USERID_IMPERSONATE,
    ) = (0, 1, 2, 3)
    (INSTANCE_MIRROR_UNKNOWN, INSTANCE_MIRROR_ALLOW, INSTANCE_MIRROR_PREVENT) = (
        0,
        1,
        2,
    )

    _run_mode = False
    _instance_role = INSTANCE_ROLE_UNKNOWN
    _instance_mode = INSTANCE_MODE_UNKNOWN
    _instance_location = INSTANCE_LOCATION_UNKNOWN
    _instance_user_id = INSTANCE_USERID_UNKNOWN
    _instance_mirror = INSTANCE_MIRROR_UNKNOWN
    _filter_installed = False
    _events_cache = {}
    _menu_background_color = None
    _menubar = None
    _toolbar = None
    _statusbar = None
    _warning_box = None
    _progressbar = None
    _progress_dialog = None

    _application_event_filter = InstanceEventFilter(None)

    widgetSynchronizeSignal = QtImport.pyqtSignal([])

    @staticmethod
    def set_run_mode(mode):
        if mode:
            BaseWidget._run_mode = True
            for widget in QtImport.QApplication.allWidgets():
                if isinstance(widget, BaseWidget):
                    widget.__run()
                    try:
                        widget.set_expert_mode(False)
                    except BaseException:
                        logging.getLogger().exception(
                            "Could not set %s to user mode", widget.name()
                        )

        else:
            BaseWidget._run_mode = False
            for widget in QtImport.QApplication.allWidgets():
                if isinstance(widget, BaseWidget):
                    widget.__stop()
                    try:
                        widget.set_expert_mode(True)
                    except Exception as ex:
                        logging.getLogger().exception(
                            "Could not set %s to expert mode: %s"
                            % (str(widget), str(ex))
                        )

    @staticmethod
    def is_running():
        return BaseWidget._run_mode

    @staticmethod
    def update_menu_bar_color(enable_checkbox=None):
        """Not a direct way how to change menubar color
           It is now done by changing stylesheet
        """
        color = None
        if BaseWidget._menubar is not None:
            BaseWidget._menubar.parent.update_instance_caption("")
            if BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER:
                if (
                    BaseWidget._instance_user_id
                    == BaseWidget.INSTANCE_USERID_IMPERSONATE
                ):
                    color = "lightBlue"
                else:
                    color = "rgb(204,255,204)"
            elif BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_SLAVE:
                BaseWidget._menubar.parent.update_instance_caption(
                    " : slave instance (all controls are disabled)"
                )
                if (
                    BaseWidget._instance_role
                    == BaseWidget.INSTANCE_ROLE_CLIENTCONNECTING
                ):
                    color = "rgb(255,204,204)"
                elif BaseWidget._instance_user_id == BaseWidget.INSTANCE_USERID_UNKNOWN:
                    color = "rgb(255, 165, 0)"
                else:
                    color = "yellow"

        if color is not None:
            BaseWidget._menubar.set_color(color)

    @staticmethod
    def set_instance_mode(mode):
        BaseWidget._instance_mode = mode
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                widget._instance_mode_changed(mode)
                if widget["instanceAllowAlways"]:
                    widget.setEnabled(True)
                else:
                    widget.setEnabled(mode == BaseWidget.INSTANCE_MODE_MASTER)
        if BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER:
            if BaseWidget._filter_installed:
                QtImport.QApplication.instance().removeEventFilter(
                    BaseWidget._application_event_filter
                )
                BaseWidget._filter_installed = False
                BaseWidget.synchronize_with_cache()  # why?
        else:
            if not BaseWidget._filter_installed:
                QtImport.QApplication.instance().installEventFilter(
                    BaseWidget._application_event_filter
                )
                BaseWidget._filter_installed = True

        BaseWidget.update_menu_bar_color(
            BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER
        )

    @staticmethod
    def set_status_info(info_type, info_message, info_status=""):
        """Updates status bar"""
        if BaseWidget._statusbar:
            BaseWidget._statusbar.parent().update_status_info(
                info_type, info_message, info_status
            )

    @staticmethod
    def set_warning_box(warning_msg):
        """Updates status bar"""
        if BaseWidget._warning_box:
            BaseWidget._warning_box.parent().show_warning_box(warning_msg)

    @staticmethod
    def init_progress_bar(progress_type, number_of_steps):
        """Updates status bar"""
        if BaseWidget._statusbar:
            BaseWidget._statusbar.parent().init_progress_bar(
                progress_type, number_of_steps
            )

    @staticmethod
    def set_progress_bar_step(step):
        """Updates status bar"""
        if BaseWidget._statusbar:
            BaseWidget._statusbar.parent().set_progress_bar_step(step)

    @staticmethod
    def stop_progress_bar():
        """Updates status bar"""
        if BaseWidget._statusbar:
            BaseWidget._statusbar.parent().stop_progress_bar()

    @staticmethod
    def open_progress_dialog(msg, max_steps):
        if BaseWidget._progress_dialog:
            BaseWidget._progress_dialog.parent().open_progress_dialog(msg, max_steps)

    @staticmethod
    def set_progress_dialog_step(step, msg):
        if BaseWidget._progress_dialog:
            BaseWidget._progress_dialog.parent().set_progress_dialog_step(step, msg)

    @staticmethod
    def close_progress_dialog():
        if BaseWidget._progress_dialog:
            BaseWidget._progress_dialog.parent().close_progress_dialog()

    @staticmethod
    def set_user_file_directory(user_file_directory):
        BaseWidget.user_file_directory = user_file_directory

    def should_filter_event(self):
        if BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER:
            return False
        try:
            allow_always = self["instanceAllowAlways"]
        except KeyError:
            return False
        if not allow_always:
            try:
                allow_connected = self["instanceAllowConnected"]
            except KeyError:
                return False

            connected = BaseWidget._instance_role in (
                BaseWidget.INSTANCE_ROLE_SERVER,
                BaseWidget.INSTANCE_ROLE_CLIENT,
            )
            if allow_connected and connected:
                return False
            return True

        return False

    def connect_group_box(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.toggled.connect(
            lambda s: BaseWidget.widget_groupbox_toggled(
                brick_name, widget_name, master_sync, s
            )
        )

    def connect_combobox(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.activated.connect(
            lambda i: BaseWidget.widget_combobox_activated(
                brick_name, widget_name, widget, master_sync, i
            )
        )

    def connect_line_edit(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.textChanged.connect(
            lambda t: BaseWidget.widget_line_edit_text_changed(
                brick_name, widget_name, master_sync, t
            )
        )

    def connect_spinbox(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.valueChanged.connect(
            lambda t: BaseWidget.widget_spinbox_value_changed(
                brick_name, widget_name, master_sync, t
            )
        )

    def connect_double_spinbox(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.valueChanged.connect(
            lambda t: BaseWidget.widget_double_spinbox_value_changed(
                brick_name, widget_name, master_sync, t
            )
        )

    def connect_generic_widget(self, widget, widget_name, master_sync):
        brick_name = self.objectName()
        widget.widgetSynchronize.connect(
            lambda state: BaseWidget.widget_generic_changed(
                brick_name, widget_name, master_sync, state
            )
        )

    def _instance_mode_changed(self, mode):
        for widget, widget_name, master_sync in self._widget_events:
            if isinstance(widget, QtImport.QGroupBox):
                self.connect_group_box(widget, widget_name, master_sync)
            elif isinstance(widget, QtImport.QComboBox):
                self.connect_combobox(widget, widget_name, master_sync)
            elif isinstance(widget, QtImport.QLineEdit):
                self.connect_line_edit(widget, widget_name, master_sync)
            elif isinstance(widget, QtImport.QSpinBox):
                self.connect_spinbox(widget, widget_name, master_sync)
            elif isinstance(widget, QtImport.QDoubleSpinBox):
                self.connect_double_spinbox(widget, widget_name, master_sync)
            else:
                # verify if widget has the widgetSynchronize method!!!
                self.connect_generic_widget(widget, widget_name, master_sync)
        self._widget_events = []

        if self.should_filter_event():
            self.setCursor(QtImport.QCursor(QtImport.Qt.ForbiddenCursor))
        else:
            self.setCursor(QtImport.QCursor(QtImport.Qt.ArrowCursor))

    @staticmethod
    def is_instance_mode_master():
        return BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER

    @staticmethod
    def is_instance_mode_slave():
        return BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_SLAVE

    @staticmethod
    def is_istance_role_unknown():
        return BaseWidget._instance_role == BaseWidget.INSTANCE_ROLE_UNKNOWN

    @staticmethod
    def is_instance_role_client():
        return BaseWidget._instance_role == BaseWidget.INSTANCE_ROLE_CLIENT

    @staticmethod
    def is_instance_role_server():
        return BaseWidget._instance_role == BaseWidget.INSTANCE_ROLE_SERVER

    @staticmethod
    def is_instance_user_id_unknown():
        return BaseWidget._instance_user_id == BaseWidget.INSTANCE_USERID_UNKNOWN

    @staticmethod
    def is_instance_user_id_logged():
        return BaseWidget._instance_user_id == BaseWidget.INSTANCE_USERID_LOGGED

    @staticmethod
    def is_instance_user_id_inhouse():
        return BaseWidget._instance_user_id == BaseWidget.INSTANCE_USERID_INHOUSE

    @staticmethod
    def set_instance_role(role):
        if role == BaseWidget._instance_role:
            return
        BaseWidget._instance_role = role
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                # try:
                widget.instance_role_changed(role)
                # except:
                #    pass

    @staticmethod
    def set_instance_location(location):
        if location == BaseWidget._instance_location:
            return
        BaseWidget._instance_location = location
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                # try:
                widget.instance_location_changed(location)
                # except:
                #    pass

    @staticmethod
    def set_instance_user_id(user_id):
        if user_id == BaseWidget._instance_user_id:
            return
        BaseWidget._instance_user_id = user_id

        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                # try:
                widget.instance_user_id_changed(user_id)
                # except:
                #    pass
        BaseWidget.update_menu_bar_color()

    @staticmethod
    def set_instance_mirror(mirror):
        if mirror == BaseWidget._instance_mirror:
            return
        BaseWidget._instance_mirror = mirror

        if mirror == BaseWidget.INSTANCE_MIRROR_ALLOW:
            BaseWidget.synchronize_with_cache()

        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                widget.instance_mirror_changed(mirror)

    def instance_mirror_changed(self, mirror):
        pass

    def instance_location_changed(self, location):
        pass

    @staticmethod
    def is_instance_location_unknown():
        return BaseWidget._instance_location == BaseWidget.INSTANCE_LOCATION_UNKNOWN

    @staticmethod
    def is_instance_location_local():
        return BaseWidget._instance_location == BaseWidget.INSTANCE_LOCATION_LOCAL

    @staticmethod
    def is_instance_mirror_allow():
        return BaseWidget._instance_mirror == BaseWidget.INSTANCE_MIRROR_ALLOW

    def instance_user_id_changed(self, user_id):
        pass

    def instance_role_changed(self, role):
        pass

    @staticmethod
    def update_whats_this():
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                msg = "%s (%s)\n%s" % (
                    widget.objectName(),
                    widget.__class__.__name__,
                    widget.get_hardware_objects_info(),
                )
                widget.setWhatsThis(msg)
        QtImport.QWhatsThis.enterWhatsThisMode()

    @staticmethod
    def update_widget(brick_name, widget_name, method_name, method_args, master_sync):
        for widget in QtImport.QApplication.allWidgets():
            if hasattr(widget, "configuration"):
                top_level_widget = widget
                break
        if (
            not master_sync
            or BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER
        ):
            top_level_widget.brickChangedSignal.emit(
                brick_name, widget_name, method_name, method_args, master_sync
            )

    @staticmethod
    def update_tab_widget(tab_name, tab_index):
        if BaseWidget._instance_mode == BaseWidget.INSTANCE_MODE_MASTER:
            for widget in QtImport.QApplication.allWidgets():
                if hasattr(widget, "configuration"):
                    widget.tabChangedSignal.emit(tab_name, tab_index)

    @staticmethod
    def widget_groupbox_toggled(brick_name, widget_name, master_sync, state):
        BaseWidget.update_widget(
            brick_name, widget_name, "setChecked", (state,), master_sync
        )

    @staticmethod
    def widget_combobox_activated(
        brick_name, widget_name, widget, master_sync, item_index
    ):
        lines = []
        if widget.isEditable():
            for index in range(widget.count()):
                lines.append(str(widget.itemText(index)))
        BaseWidget.update_widget(
            brick_name, widget_name, "setCurrentIndex", (item_index,), master_sync
        )

    @staticmethod
    def widget_line_edit_text_changed(brick_name, widget_name, master_sync, text):
        BaseWidget.update_widget(
            brick_name, widget_name, "setText", (text,), master_sync
        )

    @staticmethod
    def widget_spinbox_value_changed(brick_name, widget_name, master_sync, text):
        BaseWidget.update_widget(
            brick_name, widget_name, "setValue", (int(text),), master_sync
        )

    @staticmethod
    def widget_double_spinbox_value_changed(brick_name, widget_name, master_sync, text):
        BaseWidget.update_widget(
            brick_name, widget_name, "setValue", (float(text),), master_sync
        )

    @staticmethod
    def widget_generic_changed(brick_name, widget_name, master_sync, state):
        BaseWidget.update_widget(
            brick_name, widget_name, "widget_synchronize", (state,), master_sync
        )

    def instance_forward_events(self, widget_name, master_sync):
        if widget_name == "":
            widget = self
        else:
            widget = getattr(self, widget_name)
        self._widget_events.append((widget, widget_name, master_sync))

    def instance_synchronize(self, *args, **kwargs):
        for widget_name in args:
            self.instance_forward_events(widget_name, kwargs.get("master_sync", True))

    @staticmethod
    def should_run_event():
        return BaseWidget._instance_mirror == BaseWidget.INSTANCE_MIRROR_ALLOW

    @staticmethod
    def add_event_to_cache(timestamp, method, *args):
        try:
            method_to_add = WeakMethod(method)
        except TypeError:
            method_to_add = method
        BaseWidget._events_cache[method_to_add] = (timestamp, method_to_add, args)

    @staticmethod
    def synchronize_with_cache():
        events = list(BaseWidget._events_cache.values())
        ordered_events = sorted(events, key=operator.itemgetter(0))
        for event_timestamp, event_method, event_args in ordered_events:
            try:
                method = event_method()
                if method is not None:
                    method(*event_args)
            except BaseException:
                pass
        BaseWidget._events_cache = {}

    @staticmethod
    def set_gui_enabled(enabled):
        for widget in QtImport.QApplication.allWidgets():
            if isinstance(widget, BaseWidget):
                widget.setEnabled(enabled)

    def __init__(self, parent=None, widget_name=""):

        Connectable.Connectable.__init__(self)
        QtImport.QFrame.__init__(self, parent)
        self.setObjectName(widget_name)
        self.property_bag = PropertyBag.PropertyBag()

        self.__enabled_state = True
        self.__loaded_hardware_objects = []
        self.__failed_to_load_hwobj = False
        self.__use_progress_dialog = False
        self._signal_slot_filters = {}
        self._widget_events = []

        self.setWhatsThis("%s (%s)\n" % (widget_name, self.__class__.__name__))

        self.add_property("fontSize", "string", str(self.font().pointSize()))
        self.add_property(
            "frame", "boolean", False, comment="Draw a frame around the widget"
        )
        self.add_property(
            "instanceAllowAlways",
            "boolean",
            False,
            comment="Allow to control brick in all modes",
        )
        self.add_property(
            "instanceAllowConnected",
            "boolean",
            False,
            comment="Allow to control brick in slave mode",
        )
        self.add_property(
            "fixedWidth", "integer", "-1", comment="Set fixed width in pixels"
        )
        self.add_property(
            "fixedHeight", "integer", "-1", comment="Set fixed height in pixels"
        )
        self.add_property("hide", "boolean", False, comment="Hide widget")

        dispatcher.connect(
            self.__hardware_object_discarded,
            "hardwareObjectDiscarded",
            HWR.getHardwareRepository(),
        )
        self.define_slot("enable_widget", ())
        self.define_slot("disable_widget", ())

        # If PySide used then connect method was not overriden
        # This solution of redirecting methods works...

        self.connect = self.connect_hwobj
        self.disconnect = self.disconnect_hwobj
        # self.run_mode = QPushButton("Run mode", self)

    def __run(self):
        self.setAcceptDrops(False)
        self.blockSignals(False)
        self.setEnabled(self.__enabled_state)
        # self.run_mode_pushbutton = QPushButton("Simulation", self)

        try:
            self.run()
        except BaseException:
            logging.getLogger().exception(
                "Could not set %s to run mode", self.objectName()
            )

    def __stop(self):
        self.blockSignals(True)

        try:
            self.stop()
        except BaseException:
            logging.getLogger().exception("Could not stop %s", self.objectName())

        # self.setAcceptDrops(True)
        self.__enabled_state = self.isEnabled()
        QtImport.QWidget.setEnabled(self, True)

    def __repr__(self):
        return repr("<%s: %s>" % (self.__class__, self.objectName()))

    def connect_signal_slot_filter(self, sender, signal, slot, should_cache):
        uid = (sender, signal, hash(slot))
        signal_slot_filter = SignalSlotFilter(signal, slot, should_cache)
        self._signal_slot_filters[uid] = signal_slot_filter

        signal.connect(signal_slot_filter)
        # QtImport.QObject.connect(sender, signal, signal_slot_filter)

    def connect_hwobj(
        self, sender, signal, slot, instance_filter=False, should_cache=True
    ):
        if sys.version_info > (3, 0):
            signal = str(signal.decode("utf8") if isinstance(signal, bytes) else signal)
        else:
            signal = str(signal)

        if signal[0].isdigit():
            pysignal = signal[0] == "9"
            signal = signal[1:]
        else:
            pysignal = True

        if not isinstance(sender, QtImport.QObject):
            if isinstance(sender, HardwareObject):
                sender.connect(signal, slot)
                return
            else:
                _sender = emitter(sender)
        else:
            _sender = sender

        if instance_filter:
            self.connect_signal_slot_filter(
                _sender,
                pysignal and QtImport.pyqtSignal(signal) or QtImport.pyqtSignal(signal),
                slot,
                should_cache,
            )
        else:
            # Porting to Qt5
            getattr(_sender, signal).connect(slot)

            # QtCore.QObject.connect(_sender,
            #                       pysignal and \
            #                       QtCore.SIGNAL(signal) or \
            #                       QtCore.SIGNAL(signal),
            #                       slot)

        # workaround for PyQt lapse
        # if hasattr(sender, "connectNotify"):
        #    sender.connectNotify(QtCore.pyqtSignal(signal))

    def disconnect_hwobj(self, sender, signal, slot):
        signal = str(signal)
        if signal[0].isdigit():
            pysignal = signal[0] == "9"
            signal = signal[1:]
        else:
            pysignal = True

        if isinstance(sender, HardwareObject):
            sender.disconnect(sender, signal, slot)
            return

        # workaround for PyQt lapse
        if hasattr(sender, "disconnectNotify"):
            sender.disconnectNotify(signal)

        if not isinstance(sender, QtImport.QObject):
            sender = emitter(sender)

            try:
                uid = (
                    sender,
                    pysignal
                    and QtImport.QtCore.SIGNAL(signal)
                    or QtImport.QtCore.SIGNAL(signal),
                    hash(slot),
                )
                signal_slot_filter = self._signal_slot_filters[uid]
            except KeyError:
                getattr(sender, signal).disconnect(slot)
                # QtImport.QObject.disconnect(sender,
                #                            pysignal and
                #                            QtImport.QtCore.SIGNAL(signal) or
                #                            QtImport.QtCore.SIGNAL(signal),
                #                            slot)
            else:
                getattr(sender, signal).disconnect(signal_slot_filter)
                # QtImport.QObject.disconnect(sender,
                #                            pysignal and
                #                            QtImport.SIGNAL(signal) or
                #                            QtImport.SIGNAL(signal),
                #                            signal_slot_filter)
                del self._signal_slot_filters[uid]
        else:
            getattr(sender, signal).disconnect(signal_slot_filter)
            # QtImport.QObject.disconnect(sender,
            #                            pysignal and
            #                            QtImport.SIGNAL(signal) or
            #                            QtImport.SIGNAL(signal),
            #                            signal_slot_filter)

    def reparent(self, widget_to):
        saved_enabled_state = self.isEnabled()
        if self.parent() is not None:
            self.parent().layout().removeWidget(self)
        if widget_to is not None:
            widget_to.layout().addWidget(self)
            self.setEnabled(saved_enabled_state)

    def blockSignals(self, block):
        for child in self.children():
            child.blockSignals(block)

    def run(self):
        pass

    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.run()

    def load_ui_file(self, filename):
        for path in [gui.get_base_bricks_path()] + gui.get_custom_bricks_dirs():
            if os.path.exists(os.path.join(path, filename)):
                return QtImport.QWidgetFactory.create(os.path.join(path, filename))

    def create_gui_from_ui(self, ui_filename):
        widget = self.loadUIFile(ui_filename)
        if widget is not None:
            children = self.children() or []
            for child in children:
                self.removeChild(child)

            layout = QtImport.QGridLayout(self, 1, 1)
            widget.reparent(self)
            widget.show()
            layout.addWidget(widget, 0, 0)
            self.setLayout(layout)
            return widget

    def set_persistent_property_bag(self, persistent_property_bag):
        if id(persistent_property_bag) != id(self.property_bag):
            for prop in persistent_property_bag:
                if hasattr(prop, "get_name"):
                    if prop.get_name() in self.property_bag.properties:
                        self.property_bag.get_property(prop.get_name()).set_value(
                            prop.get_user_value()
                        )
                    elif prop.hidden:
                        self.property_bag[prop.get_name()] = prop
                else:
                    if prop["name"] in self.property_bag.properties:
                        self.property_bag.get_property(prop["name"]).set_value(
                            prop["value"]
                        )
                    elif prop["hidden"]:
                        self.property_bag[prop["name"]] = prop

        self.read_properties()

    def read_properties(self):
        for prop in self.property_bag:
            self._property_changed(prop.get_name(), None, prop.get_user_value())

    def add_property(self, *args, **kwargs):
        self.property_bag.add_property(*args, **kwargs)

    def get_property(self, property_name):
        return self.property_bag.get_property(property_name)

    def show_property(self, property_name):
        return self.property_bag.show_property(property_name)

    def hide_property(self, property_name):
        return self.property_bag.hide_property(property_name)

    def del_property(self, property_name):
        return self.property_bag.del_property(property_name)

    def get_hardware_object(self, hardware_object_name, optional=False):
        splash_screen = gui.get_splash_screen()
        if splash_screen:
            splash_screen.set_message(
                "Loading hardware object defined in %s.xml" % hardware_object_name
            )

        if not hardware_object_name in self.__loaded_hardware_objects:
            if splash_screen:
                splash_screen.inc_progress_value()
            self.__loaded_hardware_objects.append(hardware_object_name)

        hwobj = HWR.getHardwareRepository().getHardwareObject(
            hardware_object_name
        )

        if hwobj is not None:
            self.connect(hwobj, "progressInit", self.progress_init)
            self.connect(hwobj, "progressStep", self.progress_step)
            self.connect(hwobj, "progressStop", self.progress_stop)
            self.connect(hwobj, "statusMessage", self.status_message_changed)
            self.connect(hwobj, "showWarning", self.show_warning)

        if hwobj is None and not optional:
            logging.getLogger("GUI").error(
                "%s: Unable to initialize hardware object defined in %s.xml"
                % (self.objectName(), hardware_object_name[1:])
            )
            self.set_background_color(Colors.LIGHT_RED)
            self.__failed_to_load_hwobj = True
            self.setDisabled(True)

        return hwobj

    def progress_init(self, progress_type, number_of_steps, use_dialog=False):
        self.__use_progress_dialog = use_dialog
        if self.__use_progress_dialog:
            BaseWidget.open_progress_dialog(progress_type, number_of_steps)

    def progress_step(self, step, msg=None):
        if self.__use_progress_dialog:
            BaseWidget.set_progress_dialog_step(step, msg)

    def progress_stop(self):
        if self.__use_progress_dialog:
            BaseWidget.close_progress_dialog()

    def status_message_changed(self, info_type, message, state):
        BaseWidget.set_status_info(info_type, message, state)

    def show_warning(self, warning_msg):
        BaseWidget.set_warning_box(warning_msg)

    def __hardware_object_discarded(self, hardware_object_name):
        if hardware_object_name in self.__loaded_hardware_objects:
            # there is a high probability we need to reload this hardware object...
            self.readProperties()  # force to read properties

    def get_hardware_objects_info(self):
        info_dict = {}
        for ho_name in self.__loaded_hardware_objects:
            info = HWR.getHardwareRepository().getInfo(ho_name)

            if len(info) > 0:
                info_dict[ho_name] = info

        if len(info_dict):
            return "Hardware Objects:\n\n%s" % pprint.pformat(info_dict)
        else:
            return ""

    def __getitem__(self, property_name):
        return self.property_bag[property_name]

    def __setitem__(self, property_name, value):
        property_bag = self.property_bag.get_property(property_name)
        old_value = property_bag.get_value()
        property_bag.set_value(value)

        self._property_changed(property_name, old_value, property_bag.get_user_value())

    def _property_changed(self, property_name, old_value, new_value):
        if property_name == "fontSize":
            try:
                font_size = int(new_value)
            except BaseException:
                self.get_property("fontSize").set_value(self.font().pointSize())
            else:
                font = self.font()
                font.setPointSize(font_size)
                self.setFont(font)

                for brick in self.children():
                    if isinstance(brick, BaseWidget):
                        brick["fontSize"] = font_size
                self.update()
        elif property_name == "frame":
            try:
                if new_value:
                    self.setFrameStyle(QtImport.QFrame.StyledPanel)
                else:
                    self.setFrameStyle(QtImport.QFrame.NoFrame)
            except BaseException:
                pass
            self.update()
        elif property_name == "fixedWidth":
            if new_value > -1:
                self.setFixedWidth(new_value)
        elif property_name == "fixedHeight":
            if new_value > -1:
                self.setFixedHeight(new_value)
        elif property_name == "hide":
            if new_value:
                self.setHidden(True)
            #else:
            #    self.setVisible(True)
        else:
            try:
                self.property_changed(property_name, old_value, new_value)
            except BaseException:
                logging.getLogger().exception(
                    "Error while setting property %s " % property_name
                    + "for %s (details in log file)." % str(self.objectName())
                )

    def property_changed(self, property_name, old_value, new_value):
        pass

    def set_expert_mode(self, expert):
        pass

    def enable_widget(self, state):
        if self.__failed_to_load_hwobj:
            state = False

        if state:
            self.setEnabled(True)
        else:
            self.setDisabled(True)

    def disable_widget(self, state):
        if self.__failed_to_load_hwobj:
            state = True

        if state:
            self.setDisabled(True)
        else:
            self.setEnabled(True)

    def get_window_display_widget(self):
        for widget in QtImport.QApplication.allWidgets():
            if hasattr(widget, "configuration"):
                return widget

    def set_background_color(self, color):
        Colors.set_widget_color(self, color, QtImport.QPalette.Background)


class NullBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.property_bag = PropertyBag.PropertyBag()

    def set_persistent_property_bag(self, persistent_property_bag):
        self.property_bag = persistent_property_bag

    def sizeHint(self):
        return QtImport.QSize(100, 100)

    def run(self):
        self.hide()

    def stop(self):
        self.show()

    def paintEvent(self, event):
        if not self.is_running():
            painter = QtImport.QPainter(self)
            painter.setPen(QtImport.QPen(QtImport.Qt.black, 1))
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)
