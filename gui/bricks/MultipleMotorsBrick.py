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

from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget
from gui.bricks.MotorSpinBoxBrick import MotorSpinBoxBrick


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"


class MultipleMotorsBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.motor_hwobj_list = []
        self.motor_widget_list = []
        self.motor_widget_labels = []
        self.predefined_positions_list = []
        self.positions = None

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("labels", "string", "")
        self.add_property("moveButtonIcons", "string", "")
        self.add_property("alignment", "combo", ("vertical", "horizontal"), "vertical")
        self.add_property("defaultSteps", "string", "")
        self.add_property("defaultDeltas", "string", "")
        self.add_property("defaultDecimals", "string", "")
        self.add_property("predefinedPositions", "string", "")
        self.add_property("showMoveButtons", "boolean", True)
        self.add_property("showSlider", "boolean", False)
        self.add_property("showStop", "boolean", True)
        self.add_property("showStep", "boolean", True)
        self.add_property("showEnableButtons", "boolean", False)
        self.add_property("inExpertMode", "boolean", False)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_group_box = QtImport.QGroupBox(self)
        self.enable_motors_buttons = QtImport.QPushButton("Enable", self.main_group_box)
        self.disable_motors_buttons = QtImport.QPushButton(
            "Disable", self.main_group_box
        )

        # Layout --------------------------------------------------------------
        if self["alignment"] == "horizontal":
            self.main_groupbox_hlayout = QtImport.QHBoxLayout(self.main_group_box)
        else:
            self.main_groupbox_hlayout = QtImport.QVBoxLayout(self.main_group_box)
        self.main_groupbox_hlayout.setSpacing(2)
        self.main_groupbox_hlayout.setContentsMargins(0, 0, 0, 0)

        self.main_hlayout = QtImport.QHBoxLayout(self)
        self.main_hlayout.addWidget(self.main_group_box)
        self.main_hlayout.setSpacing(2)
        self.main_hlayout.setContentsMargins(2, 2, 2, 2)

        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.enable_motors_buttons.clicked.connect(self.enable_motors)
        self.disable_motors_buttons.clicked.connect(self.disable_motors)

        # Other ---------------------------------------------------------------

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            hwobj_names_list = new_value.split()

            default_delta_list = self["defaultDeltas"].split()
            default_decimal_list = self["defaultDecimals"].split()
            default_step_list = self["defaultSteps"].split()

            for index, hwobj_name in enumerate(hwobj_names_list):
                temp_motor_hwobj = self.get_hardware_object(hwobj_name)
                if temp_motor_hwobj is not None:
                    temp_motor_widget = MotorSpinBoxBrick(self)
                    temp_motor_widget.set_motor(temp_motor_hwobj, hwobj_name)
                    temp_motor_widget.move_left_button.setVisible(
                        self["showMoveButtons"]
                    )
                    temp_motor_widget.move_right_button.setVisible(
                        self["showMoveButtons"]
                    )
                    temp_motor_widget.position_slider.setVisible(self["showSlider"])
                    temp_motor_widget.step_button.setVisible(self["showStep"])
                    temp_motor_widget.stop_button.setVisible(self["showStop"])

                    try:
                        temp_motor_widget.set_line_step(default_step_list[index])
                        temp_motor_widget["defaultStep"] = default_step_list[index]
                    except BaseException:
                        temp_motor_widget.set_line_step(0.001)
                        temp_motor_widget["defaultStep"] = 0.001

                    try:
                        temp_motor_widget["delta"] = default_delta_list[index]
                    except BaseException:
                        temp_motor_widget["delta"] = 0.001
                    try:
                        temp_motor_widget.set_decimals(
                            float(default_decimal_list[index])
                        )
                    except BaseException:
                        pass

                    temp_motor_widget.step_changed(None)
                    self.main_groupbox_hlayout.addWidget(temp_motor_widget)

                    self.motor_hwobj_list.append(temp_motor_hwobj)
                    self.motor_widget_list.append(temp_motor_widget)

                    temp_motor_hwobj.update_values()
                    temp_motor_widget.update_gui()

            self.enable_motors_buttons.setVisible(self["showEnableButtons"])
            self.disable_motors_buttons.setVisible(self["showEnableButtons"])
            if self["showEnableButtons"]:
                self.main_groupbox_hlayout.addWidget(self.enable_motors_buttons)
                self.main_groupbox_hlayout.addWidget(self.disable_motors_buttons)
            if len(self.motor_widget_labels):
                for index, label in enumerate(self.motor_widget_labels):
                    self.motor_widget_list[index].setLabel(label)
        elif property_name == "moveButtonIcons":
            icon_list = new_value.split()
            for index in range(len(icon_list) - 1):
                if index % 2 == 0:
                    self.motor_widget_list[index / 2].move_left_button.setIcon(
                        Icons.load_icon(icon_list[index])
                    )
                    self.motor_widget_list[index / 2].move_right_button.setIcon(
                        Icons.load_icon(icon_list[index + 1])
                    )
        elif property_name == "labels":
            self.motor_widget_labels = new_value.split()
            if len(self.motor_widget_list):
                for index, label in enumerate(self.motor_widget_labels):
                    self.motor_widget_list[index].setLabel(label)
        elif property_name == "predefinedPositions":
            self.predefined_positions_list = new_value.split()
            for predefined_position in self.predefined_positions_list:
                temp_position_button = QtImport.QPushButton(
                    predefined_position, self.main_group_box
                )
                self.main_groupbox_hlayout.addWidget(temp_position_button)
                temp_position_button.clicked.connect(
                    lambda: self.predefined_position_clicked(predefined_position)
                )
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def set_expert_mode(self, expert):
        if self["inExpertMode"]:
            self.setEnabled(expert)

    def predefined_position_clicked(self, predefined_position):
        for motor in self.motor_hwobj_list:
            motor.move_to_predefined_position(predefined_position.lower())

    def enable_motors(self):
        for motor in self.motor_hwobj_list:
            motor.enable_motor()

    def disable_motors(self):
        for motor in self.motor_hwobj_list:
            motor.disable_motor()
