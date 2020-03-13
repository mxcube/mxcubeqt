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

"""BeamPositionBrick contains controls to
   * control the beam position
   * start automatic beam centering
   * measure flux
"""

from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget
from gui.bricks.MotorSpinBoxBrick import MotorSpinBoxBrick

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "EMBL"


class BeamPositionBrick(BaseWidget):
    """
    BeamPositionBrick
    """

    def __init__(self, *args):
        """
        Based on BaseWidget
        :param args:
        """

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.beam_focusing_hwobj = None
        self.beamline_test_hwobj = None
        self.unf_hor_motor = None
        self.unf_ver_motor = None
        self.double_hor_motor = None
        self.double_ver_motor = None
        self.motor_widget_list = []
        self.focus_mode = None
        self.is_beam_location_phase = False

        # Properties ----------------------------------------------------------
        self.add_property("hwobj_beam_focusing", "string", "")
        self.add_property("hwobj_beamline_test", "string", "/beamline-test")
        self.add_property("hwobj_motors_list", "string", "")
        self.add_property("icon_list", "string", "")
        self.add_property("defaultSteps", "string", "")
        self.add_property("defaultDeltas", "string", "")
        self.add_property("defaultDecimals", "string", "")
        self.add_property("enableCenterBeam", "boolean", True)
        self.add_property("enableMeasureFlux", "boolean", True)
        self.add_property("compactView", "boolean", False)
        self.add_property("alwaysEnableBeamPositioning", "boolean", False)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_group_box = QtImport.QGroupBox(self)
        self.unf_hor_motor_brick = MotorSpinBoxBrick(self.main_group_box)
        self.unf_ver_motor_brick = MotorSpinBoxBrick(self.main_group_box)
        self.double_hor_motor_brick = MotorSpinBoxBrick(self.main_group_box)
        self.double_ver_motor_brick = MotorSpinBoxBrick(self.main_group_box)
        self.motor_widget_list = (
            self.unf_hor_motor_brick,
            self.unf_ver_motor_brick,
            self.double_hor_motor_brick,
            self.double_ver_motor_brick,
        )
        self.center_beam_button = QtImport.QPushButton(self.main_group_box)
        self.center_beam_button.setFixedSize(27, 27)
        self.measure_flux_button = QtImport.QPushButton(self.main_group_box)
        self.measure_flux_button.setFixedSize(27, 27)

        # Layout --------------------------------------------------------------
        _gbox_grid_layout = QtImport.QGridLayout(self.main_group_box)
        _gbox_grid_layout.addWidget(self.unf_hor_motor_brick, 0, 0)
        _gbox_grid_layout.addWidget(self.unf_ver_motor_brick, 1, 0)
        _gbox_grid_layout.addWidget(self.double_hor_motor_brick, 0, 1)
        _gbox_grid_layout.addWidget(self.double_ver_motor_brick, 1, 1)
        _gbox_grid_layout.addWidget(self.center_beam_button, 0, 2)
        _gbox_grid_layout.addWidget(self.measure_flux_button, 1, 2)
        _gbox_grid_layout.setSpacing(2)
        _gbox_grid_layout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(self.main_group_box)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.center_beam_button.clicked.connect(self.center_beam_clicked)
        self.measure_flux_button.clicked.connect(self.measure_flux_clicked)

        # Other ---------------------------------------------------------------
        self.unf_hor_motor_brick.set_label("Horizontal")
        self.unf_ver_motor_brick.set_label("Vertical")
        self.double_hor_motor_brick.set_label("Horizontal")
        self.double_ver_motor_brick.set_label("Vertical")

        self.unf_hor_motor_brick.setEnabled(False)
        self.unf_ver_motor_brick.setEnabled(False)
        self.double_hor_motor_brick.setEnabled(False)
        self.double_ver_motor_brick.setEnabled(False)

        self.double_hor_motor_brick.setVisible(False)
        self.double_ver_motor_brick.setVisible(False)

        self.center_beam_button.setToolTip("Start center beam procedure")
        self.center_beam_button.setIcon(Icons.load_icon("QuickRealign"))
        self.measure_flux_button.setToolTip("Measure flux")
        self.measure_flux_button.setIcon(Icons.load_icon("Sun"))

        self.connect(
            HWR.beamline.diffractometer, "minidiffPhaseChanged", self.phase_changed
        )

        HWR.beamline.diffractometer.update_values()
        self.update_gui()

    def enable_widget(self, state):
        """
        Enables widget
        :param state: boolean
        :return:
        """
        pass

    def disable_widget(self, state):
        """
        Disables widget
        :param state: boolean
        :return:
        """
        pass

    def property_changed(self, property_name, old_value, new_value):
        """
        Defines the behaviour
        :param property_name: str
        :param old_value: value
        :param new_value: value
        :return:
        """
        if property_name == "hwobj_motors_list":
            hwobj_names_list = new_value.split()

            default_delta_list = self["defaultDeltas"].split()
            default_decimal_list = self["defaultDecimals"].split()
            default_step_list = self["defaultSteps"].split()
            icon_list = self["icon_list"].split()

            for index, hwobj_name in enumerate(hwobj_names_list):
                temp_motor_hwobj = self.get_hardware_object(hwobj_name)
                if temp_motor_hwobj is not None:
                    temp_motor_widget = self.motor_widget_list[index]
                    temp_motor_widget.set_motor(temp_motor_hwobj, hwobj_name)
                    temp_motor_widget.move_left_button.setVisible(True)
                    temp_motor_widget.move_right_button.setVisible(True)
                    temp_motor_widget.position_slider.setVisible(False)
                    temp_motor_widget.step_button.setVisible(False)
                    # temp_motor_widget.stop_button.setVisible(False)

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

                    try:
                        temp_motor_widget.move_left_button.setIcon(
                            Icons.load_icon(icon_list[index * 2])
                        )
                        temp_motor_widget.move_right_button.setIcon(
                            Icons.load_icon(icon_list[index * 2 + 1])
                        )
                    except BaseException:
                        temp_motor_widget.move_left_button.setIcon(
                            Icons.load_icon("Right2")
                        )
                        temp_motor_widget.move_right_button.setIcon(
                            Icons.load_icon("Left2")
                        )

                    temp_motor_widget.step_changed(None)
                    temp_motor_hwobj.update_values()
                    temp_motor_widget.update_gui()
        elif property_name == "hwobj_beam_focusing":
            if self.beam_focusing_hwobj is not None:
                self.disconnect(
                    self.beam_focusing_hwobj,
                    "focusingModeChanged",
                    self.focus_mode_changed,
                )
            self.beam_focusing_hwobj = self.get_hardware_object(
                new_value, optional=True
            )
            if self.beam_focusing_hwobj is not None:
                self.connect(
                    self.beam_focusing_hwobj,
                    "focusingModeChanged",
                    self.focus_mode_changed,
                )
                mode, beam_size = self.beam_focusing_hwobj.get_active_focus_mode()
                self.focus_mode_changed(mode, beam_size)
        elif property_name == "hwobj_beamline_test":
            self.beamline_test_hwobj = self.get_hardware_object(
                new_value, optional=True
            )
        elif property_name == "enableCenterBeam":
            self.center_beam_button.setVisible(new_value)
        elif property_name == "enableMeasureFlux":
            self.measure_flux_button.setVisible(new_value)
        elif property_name == "compactView":
            for widget in self.motor_widget_list:
                widget.position_spinbox.setHidden(new_value)
                widget.position_slider.setHidden(new_value)
                widget.step_button.setHidden(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def run(self):
        """
        Updates gui
        :return:
        """
        self.update_gui()

    def focus_mode_changed(self, focus_mode, beam_size):
        """
        Updates gui if the focus mode has been changed
        :param focus_mode: str
        :param beam_size: in microns (list of two floats)
        :return:
        """
        self.focus_mode = focus_mode
        self.update_gui()

    def update_gui(self):
        """
        Updates gui
        :return:
        """
        if self.focus_mode:
            self.main_group_box.setTitle("Beam positioning (%s mode)" % self.focus_mode)
            self.unf_hor_motor_brick.setVisible(self.focus_mode != "Double")
            self.unf_ver_motor_brick.setVisible(self.focus_mode != "Double")
            self.double_hor_motor_brick.setVisible(self.focus_mode == "Double")
            self.double_ver_motor_brick.setVisible(self.focus_mode == "Double")
        else:
            self.unf_hor_motor_brick.setVisible(True)
            self.unf_ver_motor_brick.setVisible(True)
            self.double_hor_motor_brick.setVisible(False)
            self.double_ver_motor_brick.setVisible(False)
            self.main_group_box.setTitle("Beam positioning")

        if self['alwaysEnableBeamPositioning']:
            enable = True
        elif self.is_beam_location_phase:
            enable = True
        else:
            enable = False
        self.unf_hor_motor_brick.setEnabled(enable)
        self.unf_ver_motor_brick.setEnabled(enable)
        self.double_hor_motor_brick.setEnabled(enable)
        self.double_ver_motor_brick.setEnabled(enable)

    def center_beam_clicked(self):
        """
        Starts automatic beam centering procedure
        :return:
        """
        conf_msg = "This will start automatic beam centering. Continue?"
        if (
            QtImport.QMessageBox.warning(
                None,
                "Question",
                conf_msg,
                QtImport.QMessageBox.Ok,
                QtImport.QMessageBox.Cancel,
            )
            == QtImport.QMessageBox.Ok
        ):
            self.beamline_test_hwobj.center_beam()

    def phase_changed(self, phase):
        """
        Enable beam positioning controls if diffractometer is in Beam phase
        :param phase:
        :return:
        """
        self.is_beam_location_phase = phase == HWR.beamline.diffractometer.PHASE_BEAM
        self.update_gui()

    def measure_flux_clicked(self):
        """
        Starts measure flux procedure
        :return:
        """
        conf_msg = (
            "This will measure flux at 100% transmission.\n"
            + "If necessary move the sample out of beam. Continue?"
        )
        if (
            QtImport.QMessageBox.warning(
                None,
                "Question",
                conf_msg,
                QtImport.QMessageBox.Ok,
                QtImport.QMessageBox.Cancel,
            )
            == QtImport.QMessageBox.Ok
        ):
            self.beamline_test_hwobj.measure_flux()
