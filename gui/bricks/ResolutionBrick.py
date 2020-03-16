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

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ResolutionBrick(BaseWidget):

    STATE_COLORS = (
        Colors.LIGHT_RED,
        Colors.LIGHT_RED,
        Colors.LIGHT_GREEN,
        Colors.LIGHT_YELLOW,
        Colors.LIGHT_YELLOW,
        Colors.LIGHT_YELLOW,
        QtImport.QColor(255, 165, 0),
        Colors.LIGHT_RED,
    )

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.resolution_limits = None
        self.detector_distance_limits = None
        self.door_interlocked = True

        # Properties ----------------------------------------------------------
        self.add_property("defaultMode", "combo", ("Ang", "mm"), "Ang")
        self.add_property("mmFormatString", "formatString", "###.##")
        self.add_property("angFormatString", "formatString", "##.###")

        self.group_box = QtImport.QGroupBox("Resolution", self)
        current_label = QtImport.QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)

        self.resolution_ledit = QtImport.QLineEdit(self.group_box)
        self.resolution_ledit.setReadOnly(True)
        self.detector_distance_ledit = QtImport.QLineEdit(self.group_box)
        self.detector_distance_ledit.setReadOnly(True)

        _new_value_widget = QtImport.QWidget(self)
        set_to_label = QtImport.QLabel("Set to:", self.group_box)
        self.new_value_ledit = QtImport.QLineEdit(self.group_box)
        self.units_combobox = QtImport.QComboBox(_new_value_widget)
        self.stop_button = QtImport.QPushButton(_new_value_widget)
        self.stop_button.setIcon(Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(25)

        # Layout --------------------------------------------------------------
        _new_value_widget_hlayout = QtImport.QHBoxLayout(_new_value_widget)
        _new_value_widget_hlayout.addWidget(self.new_value_ledit)
        _new_value_widget_hlayout.addWidget(self.units_combobox)
        _new_value_widget_hlayout.addWidget(self.stop_button)
        _new_value_widget_hlayout.setSpacing(0)
        _new_value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _group_box_gridlayout = QtImport.QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0, 2, 1)
        _group_box_gridlayout.addWidget(self.resolution_ledit, 0, 1)
        _group_box_gridlayout.addWidget(self.detector_distance_ledit, 1, 1)
        _group_box_gridlayout.addWidget(set_to_label, 2, 0)
        _group_box_gridlayout.addWidget(_new_value_widget, 2, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.new_value_ledit.returnPressed.connect(self.current_value_changed)
        self.new_value_ledit.textChanged.connect(self.input_field_changed)
        self.units_combobox.activated.connect(self.unit_changed)
        self.stop_button.clicked.connect(self.stop_clicked)

        # Other ---------------------------------------------------------------
        Colors.set_widget_color(
            self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
        )
        self.new_value_validator = QtImport.QDoubleValidator(
            0, 15, 4, self.new_value_ledit
        )

        self.units_combobox.addItem(chr(197))
        self.units_combobox.addItem("mm")
        self.instance_synchronize(
            "group_box",
            "resolution_ledit",
            "detector_distance_ledit",
            "new_value_ledit",
            "units_combobox",
        )

    def run(self):
        if HWR.beamline.detector.distance is not None:
            self.connect(
                HWR.beamline.detector.distance,
                "deviceReady",
                self.detector_distance_ready
            )
            self.connect(
                HWR.beamline.detector.distance,
                "deviceNotReady",
                self.detector_distance_not_ready,
            )
            self.connect(
                HWR.beamline.detector.distance,
                "stateChanged",
                self.detector_distance_state_changed,
            )
            self.connect(
                HWR.beamline.detector.distance,
                "valueChanged",
                self.detector_distance_changed
            )
            self.connect(
                HWR.beamline.detector.distance,
                "limitsChanged",
                self.detector_distance_limits_changed,
            )

            if HWR.beamline.detector.distance.is_ready():
                HWR.beamline.detector.distance.update_values()
                self.connected()
            else:
                self.disconnected()
        if HWR.beamline.energy is not None:
            self.connect(HWR.beamline.energy, "energyChanged", self.energy_changed)
        if HWR.beamline.resolution is not None:
            self.connect(
                HWR.beamline.resolution, "deviceReady", self.resolution_ready
            )
            self.connect(
                HWR.beamline.resolution, "deviceNotReady", self.resolution_not_ready
            )
            self.connect(
                HWR.beamline.resolution,
                "stateChanged",
                self.resolution_state_changed
            )
            self.connect(
                HWR.beamline.resolution,
                "valueChanged",
                self.resolution_value_changed
            )
            self.connect(
                HWR.beamline.resolution,
                "limitsChanged",
                self.resolution_limits_changed
            )

            if HWR.beamline.resolution.is_ready():
                HWR.beamline.resolution.update_values()
                self.connected()
            else:
                self.disconnected()
            self.update_gui()

        if HWR.beamline.hutch_interlock is not None:
            self.connect(
                HWR.beamline.hutch_interlock,
                "doorInterlockStateChanged",
                self.door_interlock_state_changed,
            )
        self.update_gui()

    def input_field_changed(self, input_field_text):
        if (
            self.new_value_validator.validate(input_field_text, 0)[0]
            == QtImport.QValidator.Acceptable
        ):
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_CHANGED, QtImport.QPalette.Base
            )
        else:
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ERROR, QtImport.QPalette.Base
            )

    def current_value_changed(self):
        input_field_text = self.new_value_ledit.text()

        if (
            self.new_value_validator.validate(input_field_text, 0)[0]
            == QtImport.QValidator.Acceptable
        ):
            unit = self.units_combobox.currentText()
            self.new_value_ledit.setText("")
            if unit == chr(197):
                self.set_resolution(float(input_field_text))
            elif unit == "mm":
                self.set_detector_distance(float(input_field_text))
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
            )

    def connected(self):
        self.setEnabled(True)

    def disconnected(self):
        self.setEnabled(False)

    def detector_distance_limits_changed(self, limits):
        if limits:
            self.detector_distance_limits = limits
            self.update_gui()

    def resolution_limits_changed(self, limits):
        if limits:
            self.resolution_limits = limits
            self.update_gui()

    def create_tool_tip(self):
        tool_tip = ""
        if self.units_combobox.currentText() == "mm":
            if self.detector_distance_limits:
                tool_tip = "Detector distance limits %0.4f : %0.4f mm" % (
                    self.detector_distance_limits[0],
                    self.detector_distance_limits[1],
                )
        elif self.resolution_limits:
            tool_tip = "Resolution limits %0.4f : %0.4f %s" % (
                self.resolution_limits[0],
                self.resolution_limits[1],
                chr(197),
            )
        if not self.door_interlocked:
            tool_tip = "\n\nMove resolution command disabled."
            tool_tip += "\nLock the hutch doors to enable."
        self.new_value_ledit.setToolTip(tool_tip)

    def unit_changed(self, unit_index):
        self.update_gui()

        self.new_value_ledit.blockSignals(True)
        self.new_value_ledit.setText("")
        self.new_value_ledit.blockSignals(False)

    def update_gui(self, resolution_ready=None, detector_ready=None):
        """
        Door interlock is optional, because not all sites might have it
        """
        groupbox_title = ""
        detector_distance = HWR.beamline.detector.distance
        if detector_distance is None:
            detector_ready = False
        elif detector_ready is None:
            try:
                if detector_distance.connection.isSpecConnected():
                    detector_ready = detector_distance.isReady()
            except AttributeError:
                detector_ready = detector_distance.is_ready()

        if detector_ready:
            self.get_detector_distance_limits()
            curr_detector_distance = detector_distance.get_position()
            self.detector_distance_changed(curr_detector_distance)
            self.detector_distance_state_changed(detector_distance.get_state())
            if self.units_combobox.currentText() == "mm":
                groupbox_title = "Detector distance"
                self.new_value_validator.setRange(
                    self.detector_distance_limits[0],
                    self.detector_distance_limits[1],
                    2,
                )
        else:
            self.detector_distance_state_changed(None)

        if HWR.beamline.resolution is None:
            resolution_ready = False
        elif resolution_ready is None:
            try:
                if HWR.beamline.resolution.connection.isSpecConnected():
                    resolution_ready = HWR.beamline.resolution.isReady()
            except AttributeError:
                resolution_ready = HWR.beamline.resolution.isReady()

        if resolution_ready:
            self.get_resolution_limits()
            curr_resolution = HWR.beamline.resolution.getPosition()
            self.resolution_value_changed(curr_resolution)
            self.resolution_state_changed(HWR.beamline.resolution.get_state())
            if self.units_combobox.currentText() != "mm":
                groupbox_title = "Resolution"
                self.new_value_validator.setRange(
                    self.resolution_limits[0], self.resolution_limits[1], 3
                )
        else:
            self.resolution_state_changed(None)

        self.setEnabled(self.door_interlocked)
        if not self.door_interlocked:
            groupbox_title += " (door is unlocked)"
        self.group_box.setTitle(groupbox_title)
        self.create_tool_tip()

    def resolution_ready(self):
        self.update_gui(resolution_ready=True)

    def resolution_not_ready(self):
        self.update_gui(resolution_ready=False)

    def detector_distance_ready(self):
        self.update_gui(detector_ready=True)

    def detector_distance_not_ready(self):
        self.update_gui(detector_ready=False)

    def set_resolution(self, value):
        if self.resolution_limits is not None:
            if self.resolution_limits[0] < value < self.resolution_limits[1]:
                HWR.beamline.resolution.move(value)

    def set_detector_distance(self, value):
        if self.detector_distance_limits is not None:
            if (
                self.detector_distance_limits[0]
                < value
                < self.detector_distance_limits[1]
            ):
                HWR.beamline.detector.distance.move(value)

    def energy_changed(self, energy_kev, energy_wavelength):
        self.get_resolution_limits(True)

    def get_resolution_limits(self, force=False, resolution_ready=None):
        if self.resolution_limits is not None and force is False:
            return

        if resolution_ready is None:
            resolution_ready = False
            if HWR.beamline.resolution is not None:
                try:
                    if HWR.beamline.resolution.connection.isSpecConnected():
                        resolution_ready = HWR.beamline.resolution.isReady()
                except AttributeError:
                    resolution_ready = HWR.beamline.resolution.isReady()

        if resolution_ready:
            # TODO remove this check and use get_limits
            if hasattr(HWR.beamline.resolution, "get_limits"):
                self.resolution_limits_changed(HWR.beamline.resolution.get_limits())
            else:
                self.resolution_limits_changed(HWR.beamline.resolution.get_limits())
        else:
            self.resolution_limits = None

    def get_detector_distance_limits(self, force=False):
        if self.detector_distance_limits is not None and force is False:
            return

        detector_ready = False
        detector_distance = HWR.beamline.detector.distance
        if detector_distance is not None:
            try:
                if detector_distance.connection.isSpecConnected():
                    detector_ready = detector_distance.is_ready()
            except AttributeError:
                detector_ready = detector_distance.is_ready()

        if detector_ready:
            self.detector_distance_limits_changed(
                detector_distance.get_limits()
            )
        else:
            self.detector_distance_limits = None

    def resolution_value_changed(self, value):
        if value:
            resolution_str = self["angFormatString"] % float(value)
            self.resolution_ledit.setText("%s %s" % (resolution_str, u"\u212B"))

    def detector_distance_changed(self, value):
        if value:
            detector_str = self["mmFormatString"] % value
            self.detector_distance_ledit.setText("%s mm" % detector_str)

    def resolution_state_changed(self, state):
        detector_distance = HWR.beamline.detector.distance
        if detector_distance is not None:
            if state:
                color = ResolutionBrick.STATE_COLORS[state]
            else:
                color = Colors.LIGHT_RED

            unit = self.units_combobox.currentText()
            if unit is chr(197):
                if state == detector_distance.motor_states.READY:
                    self.new_value_ledit.blockSignals(True)
                    self.new_value_ledit.setText("")
                    self.new_value_ledit.blockSignals(False)
                    self.new_value_ledit.setEnabled(True)
                else:
                    self.new_value_ledit.setEnabled(False)
                # or state == detector_distance.motor_states.MOVESTARTED:
                if state == detector_distance.motor_states.MOVING:
                    self.stop_button.setEnabled(True)
                else:
                    self.stop_button.setEnabled(False)

                Colors.set_widget_color(self.new_value_ledit, color)

    def detector_distance_state_changed(self, state):
        if state is None:
            return

        detector_distance = HWR.beamline.detector.distance
        color = ResolutionBrick.STATE_COLORS[state]
        unit = self.units_combobox.currentText()
        if unit == "mm":
            if state == detector_distance.motor_states.READY:
                self.new_value_ledit.blockSignals(True)
                self.new_value_ledit.setText("")
                self.new_value_ledit.blockSignals(False)
                self.new_value_ledit.setEnabled(True)
            else:
                self.new_value_ledit.setEnabled(False)
            if state == detector_distance.motor_states.MOVING:
                # or \
                # state == detector_distance.motor_states.MOVESTARTED:
                self.stop_button.setEnabled(True)
            else:
                self.stop_button.setEnabled(False)

            Colors.set_widget_color(self.new_value_ledit, color)

    def stop_clicked(self):
        unit = self.units_combobox.currentText()
        if unit == chr(197):
            HWR.beamline.resolution.stop()
        elif unit == "mm":
            HWR.beamline.detector.distance.stop()

    def door_interlock_state_changed(self, state, state_message):
        self.door_interlocked = state in ["locked_active", "locked_inactive"]
        self.update_gui()
