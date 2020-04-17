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

import sys
import math
import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"


class MotorSpinBoxBrick(BaseWidget):
    """STATE COLORS are based on the motor states:

    """

    STATE_COLORS = (
        Colors.DARK_GRAY,  # UNKNOWN
        Colors.LIGHT_ORANGE,  # WARNING
        Colors.LIGHT_YELLOW,  # BUSY
        Colors.LIGHT_GREEN,  # READY
        Colors.LIGHT_RED,  # FAULT
        Colors.LIGHT_GRAY,  # OFF
        Colors.LIGHT_YELLOW,  # MOVING
        Colors.LIGHT_GREEN,  # STANDBY
        Colors.DARK_GRAY,  # DISABLED
        Colors.DARK_GRAY,  # UNKNOWN
        Colors.LIGHT_RED,  # ALARM
        Colors.LIGHT_RED,  # FAULT
        Colors.LIGHT_RED,  # INVALID
        Colors.DARK_GRAY,  # OFFLINE
        Colors.LIGHT_RED,  # LOWLIMIT
        Colors.LIGHT_RED,  # HIGHLIMIT
        Colors.DARK_GRAY,
    )  # NOTINITIALIZED

    MAX_HISTORY = 20

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1
        self.demand_move = 0
        self.in_expert_mode = None
        self.position_history = []

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("formatString", "formatString", "+##.##")
        self.add_property("label", "string", "")
        self.add_property("showLabel", "boolean", True)
        self.add_property("showMoveButtons", "boolean", True)
        self.add_property("showSlider", "boolean", False)
        self.add_property("showStop", "boolean", True)
        self.add_property("showStep", "boolean", True)
        self.add_property("showStepList", "boolean", False)
        self.add_property("showPosition", "boolean", True)
        self.add_property("invertButtons", "boolean", False)
        self.add_property("oneClickPressButton", "boolean", False)
        self.add_property("delta", "string", "")
        self.add_property("decimals", "integer", 2)
        self.add_property("icons", "string", "")
        self.add_property("helpDecrease", "string", "")
        self.add_property("helpIncrease", "string", "")
        self.add_property("hideInUser", "boolean", False)
        self.add_property("defaultSteps", "string", "180 90 45 30 10")
        self.add_property("enableSliderTracking", "boolean", False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("toggle_enabled", ())

        # Graphic elements-----------------------------------------------------
        self.main_gbox = QtImport.QGroupBox(self)
        self.motor_label = QtImport.QLabel(self.main_gbox)
        self.motor_label.setFixedHeight(27)

        # Main controls
        self.move_left_button = QtImport.QPushButton(self.main_gbox)
        self.move_left_button.setIcon(Icons.load_icon("Left2"))
        self.move_left_button.setToolTip("Moves the motor down (while pressed)")
        self.move_left_button.setFixedSize(27, 27)
        self.move_left_button.setAutoRepeatDelay(500)
        self.move_left_button.setAutoRepeatInterval(500)
        self.move_right_button = QtImport.QPushButton(self.main_gbox)
        self.move_right_button.setIcon(Icons.load_icon("Right2"))
        self.move_right_button.setToolTip("Moves the motor up (while pressed)")
        self.move_right_button.setFixedSize(27, 27)
        self.move_right_button.setAutoRepeatDelay(500)
        self.move_right_button.setAutoRepeatInterval(500)
        self.position_spinbox = QtImport.QDoubleSpinBox(self.main_gbox)
        self.position_spinbox.setMinimum(-10000)
        self.position_spinbox.setMaximum(10000)
        self.position_spinbox.setFixedSize(75, 27)
        self.position_spinbox.setDecimals(3)
        self.position_spinbox.setToolTip(
            "Moves the motor to a specific "
            + "position or step by step; right-click for motor history"
        )
        self.position_spinbox.setContextMenuPolicy(QtImport.Qt.CustomContextMenu)

        # Extra controls
        self.stop_button = QtImport.QPushButton(self.main_gbox)
        self.stop_button.setIcon(Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stops the motor")
        self.stop_button.setFixedSize(27, 27)

        self.step_button = QtImport.QPushButton(self.main_gbox)
        self.step_button_icon = Icons.load_icon("TileCascade2")
        self.step_button.setIcon(self.step_button_icon)
        self.step_button.setToolTip("Changes the motor step")
        self.step_button.setFixedSize(27, 27)

        self.step_combo = QtImport.QComboBox(self.main_gbox)
        self.step_combo.setEditable(True)
        self.step_combo.setValidator(
            QtImport.QDoubleValidator(0, 360, 5, self.step_combo)
        )
        self.step_combo.setDuplicatesEnabled(False)
        self.step_combo.setFixedHeight(27)

        self.position_slider = QtImport.QDoubleSlider(
            QtImport.Qt.Horizontal, self.main_gbox
        )

        # Layout --------------------------------------------------------------
        self._gbox_hbox_layout = QtImport.QHBoxLayout(self.main_gbox)
        self._gbox_hbox_layout.addWidget(self.motor_label)
        self._gbox_hbox_layout.addWidget(self.position_spinbox)
        self._gbox_hbox_layout.addWidget(self.move_left_button)
        self._gbox_hbox_layout.addWidget(self.move_right_button)
        self._gbox_hbox_layout.addWidget(self.position_slider)
        self._gbox_hbox_layout.addWidget(self.stop_button)
        self._gbox_hbox_layout.addWidget(self.step_button)
        self._gbox_hbox_layout.addWidget(self.step_combo)
        self._gbox_hbox_layout.setSpacing(2)
        self._gbox_hbox_layout.setContentsMargins(2, 2, 2, 2)

        self._main_hbox_layout = QtImport.QVBoxLayout(self)
        self._main_hbox_layout.addWidget(self.main_gbox)
        self._main_hbox_layout.setSpacing(0)
        self._main_hbox_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicy (horizontal, vertical) -----------------------------------
        # self.setSizePolicy(QSizePolicy.Fixed,
        #                   QSizePolicy.Fixed)

        # Object events ------------------------------------------------------
        spinbox_event = SpinBoxEvent(self.position_spinbox)
        self.position_spinbox.installEventFilter(spinbox_event)
        spinbox_event.returnPressedSignal.connect(self.change_position)
        spinbox_event.contextMenuSignal.connect(self.open_history_menu)
        self.position_spinbox.lineEdit().textEdited.connect(self.position_value_edited)
        
        self.step_combo.activated.connect(self.go_to_step)
        self.step_combo.activated.connect(self.step_changed)
        self.step_combo.editTextChanged.connect(self.step_edited)

        self.stop_button.clicked.connect(self.stop_motor)
        self.step_button.clicked.connect(self.open_step_editor)

        self.move_left_button.pressed.connect(self.move_down)
        self.move_left_button.released.connect(self.stop_moving)
        self.move_right_button.pressed.connect(self.move_up)
        self.move_right_button.released.connect(self.stop_moving)

        self.position_slider.doubleValueChanged.connect(
            self.position_slider_double_value_changed
        )

        # Other ---------------------------------------------------------------
        self.instance_synchronize("position_spinbox", "step_combo")

    def set_expert_mode(self, expert):
        self.in_expert_mode = bool(expert)
        if self["hideInUser"]:
            if self.in_expert_mode:
                self.main_gbox.show()
            else:
                self.main_gbox.hide()

    def step_edited(self, step):
        Colors.set_widget_color(
            self.step_combo.lineEdit(),
            Colors.LINE_EDIT_CHANGED,
            QtImport.QPalette.Button,
        )

    def step_changed(self, step):
        Colors.set_widget_color(
            self.step_combo.lineEdit(), QtImport.Qt.white, QtImport.QPalette.Base
        )

    def toggle_enabled(self):
        self.setEnabled(not self.isEnabled())

    def run(self):
        if self.in_expert_mode is not None:
            self.set_expert_mode(self.in_expert_mode)

    def stop(self):
        self.main_gbox.show()

    def get_line_step(self):
        return self.position_spinbox.singleStep()

    def set_decimals(self, decimals):
        self.position_spinbox.setDecimals(decimals)

    def set_line_step(self, val):
        self.move_step = float(val)
        self.position_spinbox.setSingleStep(self.move_step)
        found = False
        for i in range(self.step_combo.count()):
            if float(str(self.step_combo.itemText(i))) == self.move_step:
                found = True
                self.step_combo.setItemIcon(i, self.step_button_icon)
        if not found:
            self.step_combo.addItem(self.step_button_icon, str(self.move_step))
            self.step_combo.setCurrentIndex(self.step_combo.count() - 1)

    def go_to_step(self, step_index):
        step = str(self.step_combo.currentText())
        if step != "":
            self.set_line_step(step)

    def set_step_button_icon(self, icon_name):
        self.step_button_icon = Icons.load_icon(icon_name)
        self.step_button.setIcon(self.step_button_icon)
        for i in range(self.step_combo.count()):
            # xt = self.step_combo.itemText(i)
            self.step_combo.setItemIcon(i, self.step_button_icon)
            # elf.step_cbox.changeItem(self.step_button_icon, txt, i)

    def stop_motor(self):
        self.motor_hwobj.stop()

    def stop_moving(self):
        self.demand_move = 0

    def move_up(self):
        # self.demand_move = 1
        self.update_gui()
        state = self.motor_hwobj.get_state()
        if state == self.motor_hwobj.STATES.READY:
            if self["invertButtons"]:
                self.really_move_down()
            else:
                self.really_move_up()

    def move_down(self):
        # self.demand_move = -1
        self.update_gui()
        state = self.motor_hwobj.get_state()
        if state == self.motor_hwobj.STATES.READY:
            if self["invertButtons"]:
                self.really_move_up()
            else:
                self.really_move_down()

    def really_move_up(self):
        step = 1.0
        if self.move_step is not None:
            step = self.move_step
        elif hasattr(self.motor_hwobj, "GUIstep"):
            if self.motor_hwobj.GUIstep is not None:
                step = self.motor_hwobj.GUIstep
        elif self["delta"] != "":
            step = float(self["delta"])

        if self.motor_hwobj.is_ready():
            self.set_position_spinbox_color(self.motor_hwobj.STATES.READY)
            self.motor_hwobj.set_value_relative(step)

    def really_move_down(self):
        step = 1.0
        if self.move_step is not None:
            step = self.move_step
        elif (
            hasattr(self.motor_hwobj, "GUIstep")
            and self.motor_hwobj.GUIstep is not None
        ):
            step = self.motor_hwobj.GUIstep
        elif self["delta"] != "" and self["delta"] is not None:
            step = float(self["delta"])

        if self.motor_hwobj.is_ready() and step:
            self.set_position_spinbox_color(self.motor_hwobj.STATES.READY)
            self.motor_hwobj.set_value_relative(-step)

    def update_gui(self):
        if self.motor_hwobj is not None:
            self.main_gbox.setEnabled(True)
            if self.motor_hwobj.is_ready():
                self.motor_hwobj.update_values()
        else:
            self.main_gbox.setEnabled(False)

    def limits_changed(self, limits):
        # limits = self.make_limits_bounded(limits)
        if limits and not None in limits:
            
            self.position_spinbox.blockSignals(True)
            self.position_spinbox.setMinimum(limits[0])
            self.position_spinbox.setMaximum(limits[1])
            self.position_spinbox.blockSignals(False)

            self.position_slider.blockSignals(True)
            self.position_slider.setMinimum(limits[0])
            self.position_slider.setMaximum(limits[1])
            self.position_slider.blockSignals(False)

            self.set_tool_tip(limits=limits)

    def make_limits_bounded(self, limits):
        return (
            limits[0]
            if not math.isinf(limits[0])
            else math.copysign(sys.maxsize, limits[0]),
            limits[1]
            if not math.isinf(limits[1])
            else math.copysign(sys.maxsize, limits[1]),
        )

    def open_history_menu(self):
        menu = QtImport.QMenu(self)
        for item in self.position_history:
            menu.addAction(item, self.go_to_history_pos)
        menu.popup(QtImport.QCursor.pos())

    def go_to_history_pos(self):
        self.motor_hwobj.set_value(float(self.sender().text()))

    def update_history(self, pos):
        pos = str(pos)
        if pos not in self.position_history:
            if len(self.position_history) == MotorSpinBoxBrick.MAX_HISTORY:
                del self.position_history[-1]
            self.position_history.insert(0, pos)

    def open_step_editor(self):
        if self.is_running():
            if self.step_editor is None:
                self.step_editor = StepEditorDialog(self)
            self.step_editor.set_motor(
                self.motor_hwobj, self, self["label"], self["default_steps"]
            )
            s = self.font().pointSize()
            f = self.step_editor.font()
            f.setPointSize(s)
            self.step_editor.setFont(f)
            self.step_editor.updateGeometry()
            self.step_editor.show()

    def position_changed(self, new_position):
        try:
            self.position_spinbox.blockSignals(True)
            self.position_slider.blockSignals(True)
            self.position_spinbox.setValue(float(new_position))
            self.position_slider.setValue(float(new_position))
            self.position_spinbox.blockSignals(False)
            self.position_slider.blockSignals(False)
        except BaseException:
            logging.getLogger("user_level_log").debug(
                "Unable to set motor position: %s" % str(new_position)
            )

    def set_position_spinbox_color(self, state):
        """Changes color of the spinbox based on the state"""
        if state in MotorSpinBoxBrick.STATE_COLORS:
            color = MotorSpinBoxBrick.STATE_COLORS[state]
        else:
            color = Colors.DARK_GRAY
        Colors.set_widget_color(
            self.position_spinbox.lineEdit(), color, QtImport.QPalette.Base
        )

    def state_changed(self, state):
        """Enables/disables controls based on the state
        """
        self.set_position_spinbox_color(state)

        if state is self.motor_hwobj.STATES.READY:
            if self.demand_move == 1:
                if self["invertButtons"]:
                    self.really_move_down()
                else:
                    self.really_move_up()
                return
            elif self.demand_move == -1:
                if self["invertButtons"]:
                    self.really_move_up()
                else:
                    self.really_move_down()
                return

            self.position_spinbox.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
            self.step_combo.setEnabled(True)
        elif state == self.motor_hwobj.STATES.FAULT:
            self.position_spinbox.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        elif state == self.motor_hwobj.STATES.BUSY:
            # self.update_history(self.motor_hwobj.get_value())
            self.position_spinbox.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
            self.step_combo.setEnabled(False)
        elif state in (
            self.motor_hwobj.STATES.READY,
            #self.motor_hwobj.STATES.HIGHLIMIT,
        ):
            self.position_spinbox.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        self.set_tool_tip(state=state)

    def change_position(self):
        if self.motor_hwobj is not None:
            self.motor_hwobj.set_value(self.position_spinbox.value())
        self.update_history(self.position_spinbox.value())

    def position_value_edited(self, value):
        Colors.set_widget_color(
            self.position_spinbox.lineEdit(),
            QtImport.QColor(255, 165, 0),
            QtImport.QPalette.Base,
        )

    def set_tool_tip(self, name=None, state=None, limits=None):
        states = (
            "NOTINITIALIZED",
            "MOVESTARTED",
            "READY",
            "MOVING",
            "HIGHLIMIT",
            "LOWLIMIT",
        )
        if name is None:
            try:
                name = self.motor_hwobj.motor_name
            except BaseException:
                name = self["mnemonic"]

        if self.motor_hwobj is None:
            tip = "Status: unknown motor " + name
        else:
            try:
                if state is None:
                    state = self.motor_hwobj.get_state()
            except BaseException:
                logging.getLogger("user_level_log").exception(
                    "%s: could not get motor state", self.objectName()
                )

                state = self.motor_hwobj.STATES.FAULT

            try:
                if limits is None and self.motor_hwobj.is_ready():
                    limits = self.motor_hwobj.get_limits()
            except BaseException:
                logging.getLogger("user_level_log").exception(
                    "%s: could not get motor limits", self.objectName()
                )
                limits = None
            try:
                state_str = state.name
            except IndexError:
                state_str = "UNKNOWN"

            limits_str = ""
            if limits is not None and not None in limits:
                l_bot = self["formatString"] % float(limits[0])
                l_top = self["formatString"] % float(limits[1])
                limits_str = " Limits:%s,%s" % (l_bot, l_top)
            tip = name + " State: " + state_str + limits_str

        self.motor_label.setToolTip(tip)
        if not self["showBox"]:
            tip = ""
        self.main_gbox.setToolTip(tip)

    def set_label(self, label):
        if not self["showLabel"]:
            label = None

        if label is None:
            self.motor_label.hide()
            self.containerBox.setTitle("")
            return

        if label == "":
            if self.motor_hwobj is not None:
                label = self.motor_hwobj.username

        if self["showBox"]:
            self.motor_label.hide()
            self.main_gbox.setTitle(label)
        else:
            if label != "":
                label += ": "
            self.main_gbox.setTitle("")
            self.motor_label.setText(label)
            self.motor_label.show()

    def set_motor(self, motor, motor_ho_name=None):
        if self.motor_hwobj is not None:
            self.disconnect(self.motor_hwobj, "limitsChanged", self.limits_changed)
            self.disconnect(self.motor_hwobj, "valueChanged", self.position_changed)
            self.disconnect(self.motor_hwobj, "stateChanged", self.state_changed)

        if motor_ho_name is not None:
            self.motor_hwobj = self.get_hardware_object(motor_ho_name)
            
        if self.motor_hwobj is None:
            # first time motor is set
            try:
                step = float(self.default_step)
            except BaseException:
                try:
                    step = self.motor_hwobj.GUIstep
                except BaseException:
                    step = 1.0
            self.set_line_step(step)

        if self.motor_hwobj is not None:
            self.connect(self.motor_hwobj, "limitsChanged", self.limits_changed)
            self.connect(
                self.motor_hwobj,
                "valueChanged",
                self.position_changed,
                instance_filter=True,
            )
            self.connect(
                self.motor_hwobj,
                "stateChanged",
                self.state_changed,
                instance_filter=True,
            )

        # get motor position and set to brick
        self.position_changed(self.motor_hwobj.get_value())
        self.position_history = []
        self.update_gui()
        # self['label'] = self['label']
        # self['defaultStep']=self['defaultStep']

    def position_slider_double_value_changed(self, value):
        """Sets motor postion based on the slider value"""
        if self.motor_hwobj is not None:
            self.motor_hwobj.set_value(value)

    def set_buttons_press_nature(self, new_state):
        """Changes right/left buttons functionality
        if new_state : buttons act while mouse button is pressed
        if not : buttons stop acting even if mouse button is pressed
        Args:
            new_state (bool):
        """

        self.move_left_button.setAutoRepeat(new_state)
        self.move_right_button.setAutoRepeat(new_state)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            self.set_motor(self.motor_hwobj, new_value)
        elif property_name == "formatString":
            if self.motor_hwobj is not None:
                self.update_gui()
        elif property_name == "label":
            self.set_label(new_value)
        elif property_name == "showLabel":
            if new_value:
                self.set_label(self["label"])
            else:
                self.set_label(None)
        elif property_name == "showMoveButtons":
            if new_value:
                self.move_left_button.show()
                self.move_right_button.show()
            else:
                self.move_left_button.hide()
                self.move_right_button.hide()
        elif property_name == "showStop":
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == "showStep":
            if new_value:
                self.step_button.show()
            else:
                self.step_button.hide()
        elif property_name == "showStepList":
            if new_value:
                self.step_combo.show()
            else:
                self.step_combo.hide()
        elif property_name == "showPosition":
            if new_value:
                self.position_spinbox.show()
            else:
                self.position_spinbox.hide()
        elif property_name == "icons":
            icons_list = new_value.split()
            try:
                self.move_left_button.setIcon(Icons.load_icon(icons_list[0]))
                self.move_right_button.setIcon(Icons.load_icon(icons_list[1]))
                self.stop_button.setIcon(Icons.load_icon(icons_list[2]))
                self.set_step_button_icon(icons_list[3])
            except IndexError:
                pass
        elif property_name == "helpDecrease":
            if new_value == "":
                self.move_left_button.setToolTip("Moves the motor down (while pressed)")
            else:
                self.move_left_button.setToolTip(new_value)
        elif property_name == "helpIncrease":
            if new_value == "":
                self.move_right_button.setToolTip("Moves the motor up (while pressed)")
            else:
                self.move_right_button.setToolTip(new_value)
        elif property_name == "defaultSteps":
            if new_value != "":
                default_step_list = new_value.split()
                for default_step in default_step_list:
                    self.set_line_step(float(default_step))
                self.step_changed(None)
        elif property_name == "decimals":
            self.position_spinbox.setDecimals(new_value)
        elif property_name == "showSlider":
            self.position_slider.setVisible(new_value)
        elif property_name == "enableSliderTracking":
            self.position_slider.setTracking(new_value)
        elif property_name == "oneClickPressButton":
            self.set_buttons_press_nature(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)


class StepEditorDialog(QtImport.QDialog):
    def __init__(self, parent):

        QtImport.QDialog.__init__(self, parent)
        # Graphic elements-----------------------------------------------------
        # self.main_gbox = QtGui.QGroupBox('Motor step', self)
        # box2 = QtGui.QWidget(self)
        self.grid = QtImport.QWidget(self)
        label1 = QtImport.QLabel("Current:", self)
        self.current_step = QtImport.QLineEdit(self)
        self.current_step.setEnabled(False)
        label2 = QtImport.QLabel("Set to:", self)
        self.new_step = QtImport.QLineEdit(self)
        self.new_step.setAlignment(QtImport.Qt.AlignRight)
        self.new_step.setValidator(QtImport.QDoubleValidator(self))

        self.button_box = QtImport.QWidget(self)
        self.apply_button = QtImport.QPushButton("Apply", self.button_box)
        self.close_button = QtImport.QPushButton("Dismiss", self.button_box)

        # Layout --------------------------------------------------------------
        self.button_box_layout = QtImport.QHBoxLayout(self.button_box)
        self.button_box_layout.addWidget(self.apply_button)
        self.button_box_layout.addWidget(self.close_button)

        self.grid_layout = QtImport.QGridLayout(self.grid)
        self.grid_layout.addWidget(label1, 0, 0)
        self.grid_layout.addWidget(self.current_step, 0, 1)
        self.grid_layout.addWidget(label2, 1, 0)
        self.grid_layout.addWidget(self.new_step, 1, 1)

        self.main_layout = QtImport.QVBoxLayout(self)
        self.main_layout.addWidget(self.grid)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections -----------------------------------------
        self.new_step.returnPressed.connect(self.apply_clicked)
        self.apply_button.clicked.connect(self.apply_clicked)
        self.close_button.clicked.connect(self.accept)

        # SizePolicies --------------------------------------------------------
        self.close_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )
        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Minimum)

        # Other ---------------------------------------------------------------
        self.setWindowTitle("Motor step editor")
        self.apply_button.setIcon(Icons.load_icon("Check"))
        self.close_button.setIcon(Icons.load_icon("Delete"))

    def set_motor(self, motor, brick, name, default_step):
        self.motor_hwobj = motor
        self.brick = brick

        if name is None or name == "":
            name = motor.username
        self.setWindowTitle(name)
        self.setWindowTitle("%s step editor" % name)
        self.current_step.setText(str(brick.get_line_step()))

    def apply_clicked(self):
        try:
            val = float(str(self.new_step.text()))
        except ValueError:
            return
        self.brick.set_line_step(val)
        self.new_step.setText("")
        self.current_step.setText(str(val))
        self.close()


class SpinBoxEvent(QtImport.QObject):

    returnPressedSignal = QtImport.pyqtSignal()
    contextMenuSignal = QtImport.pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() == QtImport.QEvent.KeyPress:
            if event.key() in [QtImport.Qt.Key_Enter, QtImport.Qt.Key_Return]:
                self.returnPressedSignal.emit()

        elif event.type() == QtImport.QEvent.MouseButtonRelease:
            self.returnPressedSignal.emit()
        elif event.type() == QtImport.QEvent.ContextMenu:
            self.contextMenuSignal.emit()
        return False
