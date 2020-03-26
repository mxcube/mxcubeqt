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


class EnergyBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------
        self.add_property("defaultMode", "combo", ("keV", "Ang"), "keV")
        self.add_property("kevFormatString", "formatString", "##.####")
        self.add_property("angFormatString", "formatString", "##.####")
        self.add_property("displayStatus", "boolean", False)
        self.add_property("doBeamAlignment", "boolean", False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.energy_limits = None
        self.wavelength_limits = None

        # Graphic elements ----------------------------------------------------
        self.group_box = QtImport.QGroupBox("Energy", self)
        energy_label = QtImport.QLabel("Current:", self.group_box)
        energy_label.setFixedWidth(75)
        wavelength_label = QtImport.QLabel("Wavelength: ", self.group_box)
        self.energy_ledit = QtImport.QLineEdit(self.group_box)
        self.energy_ledit.setReadOnly(True)
        self.wavelength_ledit = QtImport.QLineEdit(self.group_box)
        self.wavelength_ledit.setReadOnly(True)

        self.status_label = QtImport.QLabel("Status:", self.group_box)
        self.status_label.setEnabled(False)
        self.status_ledit = QtImport.QLineEdit(self.group_box)
        self.status_ledit.setEnabled(False)

        self.new_value_widget = QtImport.QWidget(self)
        self.set_to_label = QtImport.QLabel("Set to: ", self)
        self.new_value_ledit = QtImport.QLineEdit(self.new_value_widget)
        # self.new_value_ledit.setMaximumWidth(60)
        self.units_combobox = QtImport.QComboBox(self.new_value_widget)
        self.units_combobox.addItems(["keV", u"\u212B"])
        self.stop_button = QtImport.QPushButton(self.new_value_widget)
        self.stop_button.setIcon(Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(25)

        self.beam_align_cbox = QtImport.QCheckBox(
            "Center beam after energy change", self
        )

        # Layout --------------------------------------------------------------
        _new_value_widget_hlayout = QtImport.QHBoxLayout(self.new_value_widget)
        _new_value_widget_hlayout.addWidget(self.new_value_ledit)
        _new_value_widget_hlayout.addWidget(self.units_combobox)
        _new_value_widget_hlayout.addWidget(self.stop_button)
        _new_value_widget_hlayout.setSpacing(0)
        _new_value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _group_box_gridlayout = QtImport.QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(energy_label, 0, 0)
        _group_box_gridlayout.addWidget(self.energy_ledit, 0, 1)
        _group_box_gridlayout.addWidget(wavelength_label, 1, 0)
        _group_box_gridlayout.addWidget(self.wavelength_ledit, 1, 1)
        _group_box_gridlayout.addWidget(self.status_label, 2, 0)
        _group_box_gridlayout.addWidget(self.status_ledit, 2, 1)
        _group_box_gridlayout.addWidget(self.set_to_label, 3, 0)
        _group_box_gridlayout.addWidget(self.new_value_widget, 3, 1)
        _group_box_gridlayout.addWidget(self.beam_align_cbox, 4, 0, 1, 2)

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
        self.units_combobox.activated.connect(self.units_changed)
        self.stop_button.clicked.connect(self.stop_clicked)
        self.beam_align_cbox.stateChanged.connect(self.do_beam_align_changed)

        # Other ---------------------------------------------------------------
        # self.group_box.setCheckable(True)
        # self.group_box.setChecked(True)
        self.new_value_validator = QtImport.QDoubleValidator(
            0, 15, 4, self.new_value_ledit
        )
        self.status_ledit.setEnabled(False)

        self.instance_synchronize("energy_ledit", "new_value_ledit")

    def run(self):
        if HWR.beamline.energy is not None:
            self.set_new_value_limits()
            self.connect(HWR.beamline.energy, "deviceReady", self.connected)
            self.connect(HWR.beamline.energy, "deviceNotReady", self.disconnected)
            self.connect(HWR.beamline.energy, "energyChanged", self.energy_changed)
            self.connect(HWR.beamline.energy, "stateChanged", self.state_changed)
            self.connect(
                HWR.beamline.energy, "statusInfoChanged", self.status_info_changed
            )

            HWR.beamline.energy.update_values()
            if hasattr(HWR.beamline.energy, "set_do_beam_alignment"):
                HWR.beamline.energy.set_do_beam_alignment(self["doBeamAlignment"])
            if HWR.beamline.energy.is_ready():
                self.connected()
            else:
                self.disconnected()
        else:
            self.disconnected()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "defaultMode":
            if new_value == "keV":
                self.units_combobox.setCurrentIndex(0)
            else:
                self.units_combobox.setCurrentIndex(1)

        elif property_name == "displayStatus":
            self.status_label.setVisible(new_value)
            self.status_ledit.setVisible(new_value)
        elif property_name == "doBeamAlignment":
            self.beam_align_cbox.setEnabled(new_value)
            self.beam_align_cbox.setChecked(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def connected(self):
        self.setEnabled(True)
        tunable_energy = HWR.beamline.energy.tunable
        if tunable_energy is None:
            tunable_energy = False
        self.set_to_label.setEnabled(tunable_energy)
        self.new_value_ledit.setEnabled(tunable_energy)
        self.units_combobox.setEnabled(tunable_energy)
        if tunable_energy:
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
            )
            # Colors.set_widget_color(\
            #   self.units_combobox,
            #   Colors.LIGHT_GREEN,
            #   QtGui.QPalette.Button)

    def disconnected(self):
        self.setEnabled(False)

    def do_beam_align_changed(self, state):
        if HWR.beamline.energy is not None:
            HWR.beamline.energy.set_do_beam_alignment(
                self.beam_align_cbox.isChecked()
            )

    def energy_changed(self, energy_value, wavelength_value):
        energy_value_str = self["kevFormatString"] % energy_value
        wavelength_value_str = self["angFormatString"] % wavelength_value
        self.energy_ledit.setText("%s keV" % energy_value_str)
        self.wavelength_ledit.setText("%s %s" % (wavelength_value_str, u"\u212B"))

    def state_changed(self, state):
        self.setEnabled(state == "ready")
        BaseWidget.set_status_info("status", "", "")

    def status_info_changed(self, status_info):
        self.status_ledit.setText(status_info)

    def current_value_changed(self):
        input_field_text = self.new_value_ledit.text()

        if (
            self.new_value_validator.validate(input_field_text, 0)[0]
            == QtImport.QValidator.Acceptable
        ):
            if self.units_combobox.currentIndex() == 0:
                BaseWidget.set_status_info("status", "Setting energy...", "running")
                HWR.beamline.energy.set_value(float(input_field_text))
            else:
                HWR.beamline.energy.set_wavelength(float(input_field_text))
            self.new_value_ledit.setText("")
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
            )

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

    def units_changed(self, unit):
        self.set_new_value_limits()

    def set_new_value_limits(self):
        if self.units_combobox.currentIndex() == 0:
            value_limits = HWR.beamline.energy.get_limits()
            self.group_box.setTitle("Energy")
            self.new_value_ledit.setToolTip(
                "Energy limits %.4f : %.4f keV" % (value_limits[0], value_limits[1])
            )
        else:
            value_limits = HWR.beamline.energy.get_wavelength_limits()
            self.group_box.setTitle("Wavelength")
            self.new_value_ledit.setToolTip(
                "Wavelength limits %.4f : %.4f %s"
                % (value_limits[0], value_limits[1], u"\u212B")
            )
        self.new_value_validator.setRange(value_limits[0], value_limits[1], 4)

    def stop_clicked(self):
        print("stoped clicked")
