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

import re
import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget


__category__ = "General"


class DuoStateBrick(BaseWidget):

    STATES = {
        "unknown": (Colors.LIGHT_GRAY, True, True, False, False),
        "disabled": (Colors.LIGHT_GRAY, False, False, False, False),
        "noperm": (Colors.LIGHT_GRAY, False, False, False, False),
        "error": (Colors.LIGHT_RED, False, False, False, False),
        "out": (Colors.LIGHT_GREEN, True, False, False, True),
        "closed": (Colors.LIGHT_GREEN, True, True, False, True),
        "moving": (Colors.LIGHT_YELLOW, False, False, None, None),
        "in": (Colors.LIGHT_GREEN, False, True, True, False),
        "opened": (Colors.LIGHT_GREEN, True, True, True, False),
        "automatic": (Colors.WHITE, True, True, False, False),
    }

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.wrapper_hwobj = None

        # Internal values -----------------------------------------------------
        self.__expertMode = False

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("forceNoControl", "boolean", False)
        self.add_property("expertModeControlOnly", "boolean", False)
        self.add_property("icons", "string", "")
        self.add_property("in", "string", "in")
        self.add_property("out", "string", "out")
        self.add_property("setin", "string", "Set in")
        self.add_property("setout", "string", "Set out")
        self.add_property("username", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("allowControl", ())

        # Graphic elements ----------------------------------------------------
        self.main_gbox = QtImport.QGroupBox("none", self)
        self.main_gbox.setAlignment(QtImport.Qt.AlignCenter)
        self.state_ledit = QtImport.QLineEdit("unknown", self.main_gbox)

        self.buttons_widget = QtImport.QWidget(self.main_gbox)
        self.set_in_button = QtImport.QPushButton("Set in", self.buttons_widget)
        self.set_in_button.setCheckable(True)
        self.set_out_button = QtImport.QPushButton("Set out", self.buttons_widget)
        self.set_out_button.setCheckable(True)

        # Layout --------------------------------------------------------------
        _buttons_widget_hlayout = QtImport.QHBoxLayout(self.buttons_widget)
        _buttons_widget_hlayout.addWidget(self.set_in_button)
        _buttons_widget_hlayout.addWidget(self.set_out_button)
        _buttons_widget_hlayout.setSpacing(0)
        _buttons_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_gbox_vlayout = QtImport.QVBoxLayout(self.main_gbox)
        _main_gbox_vlayout.addWidget(self.state_ledit)
        _main_gbox_vlayout.addWidget(self.buttons_widget)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.set_in_button.toggled.connect(self.set_in)
        self.set_out_button.toggled.connect(self.set_out)

        # Other ---------------------------------------------------------------
        self.state_ledit.setAlignment(QtImport.Qt.AlignCenter)
        self.state_ledit.setToolTip("Shows the current control state")
        self.state_ledit.setFrame(False)
        bold_font = self.state_ledit.font()
        bold_font.setBold(True)
        self.state_ledit.setFont(bold_font)
        self.state_ledit.setFixedHeight(24)

        self.set_in_button.setToolTip("Changes the control state")
        self.set_out_button.setToolTip("Changes the control state")

        self.instance_synchronize("state_ledit")

    def setExpertMode(self, expert):
        self.__expertMode = expert
        self.buttons_widget.show()

        if not expert and self["expertModeControlOnly"]:
            self.buttons_widget.hide()

    def set_in(self, state):
        if state:
            self.set_in_button.setEnabled(False)
            self.wrapper_hwobj.setIn()
        else:
            self.set_in_button.blockSignals(True)
            # self.set_in_button.setState(QtGui.QPushButton.On)
            self.set_in_button.setDown(True)
            self.set_in_button.blockSignals(False)

    def set_out(self, state):
        if state:
            self.set_out_button.setEnabled(False)
            self.wrapper_hwobj.setOut()
        else:
            self.set_out_button.blockSignals(True)
            self.set_out_button.setDown(False)
            # self.set_out_button.setState(QtGui.QPushButton.On)
            self.set_out_button.blockSignals(False)

    def updateLabel(self, label):
        self.main_gbox.setTitle(label)

    def stateChanged(self, state, state_label=""):
        self.setEnabled(True)
        state = str(state)
        try:
            color = self.STATES[state][0]
        except KeyError:
            state = "unknown"
            color = self.STATES[state][0]
        if color is None:
            color = Colors.GROUP_BOX_GRAY

        Colors.set_widget_color(self.state_ledit, color, QtImport.QPalette.Base)
        # self.state_ledit.setPaletteBackgroundColor(QColor(color))
        if len(state_label) > 0:
            self.state_ledit.setText("%s" % state_label)
        else:
            label_str = state
            if state == "in":
                prop_label = self["in"].strip()
                if len(prop_label.strip()):
                    label_str = prop_label
            if state == "out":
                prop_label = self["out"].strip()
                if prop_label:
                    label_str = prop_label
            self.state_ledit.setText("%s" % label_str)

        if state in self.STATES:
            in_enable = self.STATES[state][1]
            out_enable = self.STATES[state][2]
        else:
            in_enable = False
            out_enable = False

        self.set_in_button.setEnabled(in_enable)
        self.set_out_button.setEnabled(out_enable)

        if state in self.STATES:
            in_state = self.STATES[state][3]
            out_state = self.STATES[state][4]
        else:
            in_state = True
            out_state = False
        if in_state is not None:
            self.set_in_button.blockSignals(True)
            self.set_in_button.setChecked(in_state)
            self.set_in_button.blockSignals(False)
        if out_state is not None:
            self.set_out_button.blockSignals(True)
            self.set_out_button.setChecked(out_state)
            self.set_out_button.blockSignals(False)

        """
        if state=='in':
            self.duoStateBrickMovingSignal.emit(False)
            self.duoStateBrickInSignal.emit(True)
        elif state=='out':
            self.duoStateBrickMovingSignal.emit(False)
            self.duoStateBrickOutSignal.emit(True)
        elif state=='moving':
            self.duoStateBrickMovingSignal.emit(True)
        elif state=='error' or state=='unknown' or state=='disabled':
            self.duoStateBrickMovingSignal.emit(False)
            self.duoStateBrickInSignal.emit(False)
            self.duoStateBrickOutSignal.emit(False)
        """

    def allowControl(self, enable):
        if self["forceNoControl"]:
            return
        if enable:
            self.buttons_widget.show()
        else:
            self.buttons_widget.hide()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.wrapper_hwobj is not None:
                self.wrapper_hwobj.duoStateChangedSignal.disconnect(self.stateChanged)

            h_obj = self.get_hardware_object(new_value)
            if h_obj is not None:
                self.wrapper_hwobj = WrapperHO(h_obj)
                self.main_gbox.show()

                if self["username"] == "":
                    self["username"] = self.wrapper_hwobj.username

                help_text = self["setin"] + " the " + self["username"].lower()
                self.set_in_button.setToolTip(help_text)
                help_text = self["setout"] + " the " + self["username"].lower()
                self.set_out_button.setToolTip(help_text)
                self.main_gbox.setTitle(self["username"])
                self.wrapper_hwobj.duoStateChangedSignal.connect(self.stateChanged)
                self.wrapper_hwobj.get_state()
            else:
                self.wrapper_hwobj = None
                # self.main_gbox.hide()
        elif property_name == "expertModeControlOnly":
            if new_value:
                if self.__expertMode:
                    self.buttons_widget.show()
                else:
                    self.buttons_widget.hide()
            else:
                self.buttons_widget.show()
        elif property_name == "forceNoControl":
            if new_value:
                self.buttons_widget.hide()
            else:
                self.buttons_widget.show()
        elif property_name == "icons":
            w = self.fontMetrics().width("Set out")
            icons_list = new_value.split()
            try:
                self.set_in_button.setIcon(Icons.load_icon(icons_list[0]))
            except IndexError:
                self.set_in_button.setText(self["setin"])
                # self.set_in_button.setMinimumWidth(w)
            try:
                self.set_out_button.setIcon(Icons.load_icon(icons_list[1]))
            except IndexError:
                self.set_out_button.setText(self["setout"])
                # self.set_out_button.setMinimumWidth(w)

        # elif property_name=='in':
        #    if self.wrapper_hwobj is not None:
        #        self.stateChanged(self.wrapper_hwobj.get_state())

        # elif property_name=='out':
        #    if self.wrapper_hwobj is not None:
        #        self.stateChanged(self.wrapper_hwobj.get_state())

        elif property_name == "setin":
            icons = self["icons"]
            # w=self.fontMetrics().width("Set out")
            icons_list = icons.split()
            try:
                i = icons_list[0]
            except IndexError:
                self.set_in_button.setText(new_value)
                # self.set_in_button.setMinimumWidth(w)
            help_text = new_value + " the " + self["username"].lower()
            self.set_in_button.setToolTip(help_text)
            self.set_in_button.setText(self["setin"])

        elif property_name == "setout":
            icons = self["icons"]
            # w=self.fontMetrics().width("Set out")
            icons_list = icons.split()
            try:
                i = icons_list[1]
            except IndexError:
                self.set_out_button.setText(new_value)
                # self.set_out_button.setMinimumWidth(w)
            help_text = new_value + " the " + self["username"].lower()
            self.set_out_button.setToolTip(help_text)
            self.set_out_button.setText(self["setout"])

        elif property_name == "username":
            if new_value == "":
                if self.wrapper_hwobj is not None:
                    name = self.wrapper_hwobj.username
                    if name != "":
                        self["username"] = name
                        return
            help_text = self["setin"] + " the " + new_value.lower()
            self.set_in_button.setToolTip(help_text)
            help_text = self["setout"] + " the " + new_value.lower()
            self.set_out_button.setToolTip(help_text)
            self.main_gbox.setTitle(self["username"])

        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)


###
# Wrapper around different hardware objects, to make them have the
# same behavior to the brick
###


class WrapperHO(QtImport.QObject):
    DEVICE_MAP = {
        "Device": "Procedure",
        "SOLEILGuillotine": "Shutter",
        "SoleilSafetyShutter": "Shutter",
        "TangoShutter": "Shutter",
        "ShutterEpics": "Shutter",
        "MD2v4_FastShutter": "Shutter",
        "TempShutter": "Shutter",
        "EMBLSafetyShutter": "Shutter",
        "MDFastShutter": "Shutter",
        "WagoPneu": "WagoPneu",
        "Shutter": "WagoPneu",
        "SpecMotorWSpecPositions": "WagoPneu",
        "Procedure": "WagoPneu",
    }

    WAGO_STATE = {"in": "in", "out": "out", "unknown": "unknown"}

    SHUTTER_STATE = {
        "fault": "error",
        "opened": "in",
        "noperm": "noperm",
        "closed": "out",
        "unknown": "unknown",
        "moving": "moving",
        "automatic": "automatic",
        "disabled": "disabled",
        "error": "error",
    }
    DOOR_INTERLOCK_STATE = {
        "locked": "out",
        "unlocked": "disabled",
        "locked_active": "out",
        "locked_inactive": "disabled",
        "error": "error",
    }

    MOTOR_WPOS = ("out", "in")
    MOTOR_WSTATE = ("disabled", "error", None, "moving", "moving", "moving")

    STATES = (
        "unknown",
        "disabled",
        "closed",
        "error",
        "out",
        "moving",
        "in",
        "automatic",
        "noperm",
    )

    duoStateChangedSignal = QtImport.pyqtSignal(str, str)

    def __init__(self, hardware_obj):
        QtImport.QObject.__init__(self)

        # self.setIn = new.instancemethod(lambda self: None, self)
        self.setIn = lambda self: None
        self.setOut = self.setIn
        # self.get-State = new.instancemethod(lambda self: "unknown", self)
        self.get_state = lambda self: "unknown"
        self.dev = hardware_obj
        try:
            sClass = str(self.dev.__class__)
            i, j = re.search("'.*'", sClass).span()
        except BaseException:
            dev_class = sClass
        else:
            dev_class = sClass[i + 1 : j - 1]
        self.devClass = dev_class.split(".")[-1]

        self.devClass = WrapperHO.DEVICE_MAP.get(self.devClass, "Shutter")

        initFunc = getattr(self, "init%s" % self.devClass)
        initFunc()
        self.setIn = getattr(self, "setIn%s" % self.devClass)
        self.setOut = getattr(self, "setOut%s" % self.devClass)
        self.get_state = getattr(self, "getState%s" % self.devClass)

    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict["setIn"]
        del dict["setOut"]
        del dict["getState"]
        return dict

    def __setstate__(self, dict):
        self.__dict__ = dict.copy()
        try:
            # Python2
            import new

            self.setIn = new.instancemethod(lambda self: None, self)
            self.setOut = self.setIn
            self.get_state = new.instancemethod(lambda self: "unknown", self)
        except ImportError:
            import types

            self.setIn = types.MethodType(lambda self: None, self)
            self.setOut = self.setIn
            self.get_state = types.MethodType(lambda self: "unknown", self)

    def userName(self):
        return self.dev.username

    # WagoPneu HO methods
    def initWagoPneu(self):
        self.dev.connect(self.dev, "wagoStateChanged", self.stateChangedWagoPneu)

    def setInWagoPneu(self):
        self.duoStateChangedSignal.emit("moving")
        self.dev.wagoIn()

    def setOutWagoPneu(self):
        self.duoStateChangedSignal.emit("moving")
        self.dev.wagoOut()

    def stateChangedWagoPneu(self, state):
        try:
            state = WrapperHO.WAGO_STATE[state]
        except KeyError:
            state = "error"
        self.duoStateChangedSignal.emit(state)

    def getStateWagoPneu(self):
        state = self.dev.getWagoState()
        try:
            state = WrapperHO.WAGO_STATE[state]
        except KeyError:
            state = "error"
        return state

    # Shutter HO methods
    def initShutter(self):
        self.dev.connect(self.dev, "shutterStateChanged", self.stateChangedShutter)

    def setInShutter(self):
        self.dev.openShutter()

    def setOutShutter(self):
        self.dev.closeShutter()

    def stateChangedShutter(self, state, state_label=None):
        state = WrapperHO.SHUTTER_STATE.get(state, "unknown")
        if not state_label:
            state_label = ""
        self.duoStateChangedSignal.emit(state, state_label)

    def getStateShutter(self):
        state = self.dev.getShutterState()
        try:
            state = WrapperHO.SHUTTER_STATE[state]
        except KeyError:
            state = "error"
        return state

    # SpecMotorWSpecPositions HO methods
    def initSpecMotorWSpecPositions(self):
        self.positions = None
        self.dev.connect(
            self.dev,
            "predefinedPositionChanged",
            self.position_changed_spec_motor_wspec_positions,
        )
        self.dev.connect(
            self.dev, "stateChanged", self.stateChangedSpecMotorWSpecPositions
        )
        self.dev.connect(
            self.dev,
            "newPredefinedPositions",
            self.new_predefined_spec_motor_wspec_positions,
        )

    def setInSpecMotorWSpecPositions(self):
        if self.positions is not None:
            self.dev.moveToPosition(self.positions[1])

    def setOutSpecMotorWSpecPositions(self):
        if self.positions is not None:
            self.dev.moveToPosition(self.positions[0])

    def stateChangedSpecMotorWSpecPositions(self, state):
        # logging.info("stateChangedSpecMotorWSpecPositions %s" % state)
        try:
            state = WrapperHO.MOTOR_WSTATE[state]
        except IndexError:
            state = "error"
        if state is not None:
            self.duoStateChangedSignal.emit(state)

    def position_changed_spec_motor_wspec_positions(self, pos_name, pos):
        if self.dev.get_state() != self.dev.READY:
            return
        state = "error"
        if self.positions is not None:
            for i in range(len(self.positions)):
                if pos_name == self.positions[i]:
                    state = WrapperHO.MOTOR_WPOS[i]
        self.duoStateChangedSignal.emit(state)

    def get_state_spec_motor_wspec_positions(self):
        if self.positions is None:
            return "error"
        curr_pos = self.dev.get_current_position_name()
        if curr_pos is None:
            state = self.dev.get_state()
            try:
                state = WrapperHO.MOTOR_WSTATE[state]
            except IndexError:
                state = "error"
            return state
        else:
            for i in range(len(self.positions)):
                if curr_pos == self.positions[i]:
                    return WrapperHO.MOTOR_WPOS[i]
        return "error"

    def new_predefined_spec_motor_wspec_positions(self):
        self.positions = self.dev.getPredefinedPositionsList()
        self.position_changed_spec_motor_wspec_positions(
            self.dev.get_current_position_name(), self.dev.get_value()
        )

    # Procedure HO methods
    def init_procedure(self):
        cmds = self.dev.get_commands()

        self.set_in_cmd = None
        self.set_out_cmd = None

        try:
            channel = self.dev.get_channel_object("dev_state")
        except KeyError:
            channel = None
        self.stateChannel = channel
        if self.stateChannel is not None:
            self.state_dict = {
                "OPEN": "in",
                "CLOSED": "out",
                "ERROR": "error",
                "1": "in",
                "0": "out",
            }
            self.stateChannel.connectSignal("update", self.channel_update)
        else:
            self.state_dict = {}

        for cmd in cmds:
            if cmd.name() == "set in":
                self.set_in_cmd = cmd
                if self.stateChannel is not None:
                    self.set_in_cmd.connectSignal(
                        "commandReplyArrived", self.procedureSetInEnded
                    )
                    self.set_in_cmd.connectSignal(
                        "commandBeginWaitReply", self.procedure_started
                    )
                    self.set_in_cmd.connectSignal(
                        "commandFailed", self.procedure_aborted
                    )
                    self.set_in_cmd.connectSignal(
                        "commandAborted", self.procedure_aborted
                    )
            elif cmd.name() == "set out":
                self.set_out_cmd = cmd
                if self.stateChannel is not None:
                    self.set_out_cmd.connectSignal(
                        "commandReplyArrived", self.procedure_set_out_ended
                    )
                    self.set_out_cmd.connectSignal(
                        "commandBeginWaitReply", self.procedure_started
                    )
                    self.set_out_cmd.connectSignal(
                        "commandFailed", self.procedure_aborted
                    )
                    self.set_out_cmd.connectSignal(
                        "commandAborted", self.procedure_aborted
                    )

    def channel_update(self, value):
        try:
            key = self.dev.statekey
        except AttributeError:
            pass
        else:
            try:
                state = value[key]
            except TypeError:
                state = "error"
        try:
            state = self.state_dict[state]
        except KeyError:
            pass
        self.duoStateChangedSignal.emit(state)

    def set_in_procedure(self):
        if self.set_in_cmd is not None:
            self.set_in_cmd()

    def set_out_procedure(self):
        if self.set_out_cmd is not None:
            self.set_out_cmd()

    """
    def stateChangedProcedure(self,state):
        pass
    """

    def get_state_procedure(self):
        if self.stateChannel is not None:
            try:
                state = self.stateChannel.getValue()
            except BaseException:
                state = "error"
            else:
                try:
                    key = self.dev.statekey
                except AttributeError:
                    pass
                else:
                    try:
                        state = state[key]
                    except TypeError:
                        state = "error"
            try:
                state = self.state_dict[state]
            except KeyError:
                pass
            return state
        return "unknown"

    def procedureSetInEnded(self, *args):
        self.duoStateChangedSignal.emit("in")

    def procedure_set_out_ended(self, *args):
        self.duoStateChangedSignal.emit("out")

    def procedure_started(self, *args):
        self.duoStateChangedSignal.emit("moving")

    def procedure_aborted(self, *args):
        self.duoStateChangedSignal.emit("error")
