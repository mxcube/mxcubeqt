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
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from QtImport import *

from Qt4_MotorSpinBoxBrick import Qt4_MotorSpinBoxBrick

from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = 'EMBL'


class Qt4_BeamPositionBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.flux_hwobj = None
        self.beam_focusing_hwobj = None
        self.beamline_test_hwobj = None
        self.diffractometer_hwobj = None
        self.unf_hor_motor = None
        self.unf_ver_motor = None
        self.double_hor_motor = None
        self.double_ver_motor = None
        self.motor_widget_list = []
        self.focus_mode = None
        self.is_beam_location_phase = False

        # Properties ----------------------------------------------------------
        self.addProperty('hwobj_beam_focusing', 'string', '/eh1/beamFocusing')
        self.addProperty('hwobj_beamline_test', 'string', '/beamline-test')
        self.addProperty('hwobj_diffractometer', 'string', '/mini-diff')
        self.addProperty('hwobj_motors_list', 'string', '')
        self.addProperty('icon_list', 'string', '')
        self.addProperty('defaultSteps', 'string', '')
        self.addProperty('defaultDeltas', 'string', '')
        self.addProperty('defaultDecimals', 'string', '')

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_group_box = QGroupBox(self)
        self.unf_hor_motor_brick = Qt4_MotorSpinBoxBrick(self.main_group_box)
        self.unf_ver_motor_brick = Qt4_MotorSpinBoxBrick(self.main_group_box)
        self.double_hor_motor_brick = Qt4_MotorSpinBoxBrick(self.main_group_box)
        self.double_ver_motor_brick = Qt4_MotorSpinBoxBrick(self.main_group_box)
        self.motor_widget_list = (self.unf_hor_motor_brick,
                                  self.unf_ver_motor_brick,
                                  self.double_hor_motor_brick,
                                  self.double_ver_motor_brick)
        self.center_beam_button = QPushButton(self.main_group_box)
        self.center_beam_button.setFixedSize(27, 27)
        self.measure_flux_button = QPushButton(self.main_group_box)
        self.measure_flux_button.setFixedSize(27, 27)
        
        # Layout -------------------------------------------------------------- 
        _gbox_grid_layout = QGridLayout(self.main_group_box)
        _gbox_grid_layout.addWidget(self.unf_hor_motor_brick, 0, 0)
        _gbox_grid_layout.addWidget(self.unf_ver_motor_brick, 1, 0)
        _gbox_grid_layout.addWidget(self.double_hor_motor_brick, 0, 1)
        _gbox_grid_layout.addWidget(self.double_ver_motor_brick, 1, 1)
        _gbox_grid_layout.addWidget(self.center_beam_button, 0, 2)  
        _gbox_grid_layout.addWidget(self.measure_flux_button, 1, 2)
        _gbox_grid_layout.setSpacing(2)
        _gbox_grid_layout.setContentsMargins(2, 2, 2, 2)

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(self.main_group_box)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.center_beam_button.clicked.connect(self.center_beam_clicked)
        self.measure_flux_button.clicked.connect(self.measure_flux_clicked)

        # Other ---------------------------------------------------------------
        self.unf_hor_motor_brick.setLabel("Horizontal")
        self.unf_ver_motor_brick.setLabel("Vertical")
        self.double_hor_motor_brick.setLabel("Horizontal")
        self.double_ver_motor_brick.setLabel("Vertical")

        self.unf_hor_motor_brick.setEnabled(False)
        self.unf_ver_motor_brick.setEnabled(False)
        self.double_hor_motor_brick.setEnabled(False)
        self.double_ver_motor_brick.setEnabled(False)

        self.double_hor_motor_brick.setVisible(False)
        self.double_ver_motor_brick.setVisible(False)

        self.center_beam_button.setToolTip("Start center beam procedure")
        self.center_beam_button.setIcon(Qt4_Icons.load_icon("QuickRealign"))
        self.measure_flux_button.setToolTip("Measure flux")
        self.measure_flux_button.setIcon(Qt4_Icons.load_icon("Sun"))

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'hwobj_motors_list':
            hwobj_names_list = new_value.split()

            default_delta_list = self['defaultDeltas'].split()
            default_decimal_list = self['defaultDecimals'].split()
            default_step_list = self['defaultSteps'].split()
            icon_list = self['icon_list'].split()

            for index, hwobj_name in enumerate(hwobj_names_list):
                temp_motor_hwobj = self.getHardwareObject(hwobj_name)
                if temp_motor_hwobj is not None:
                    temp_motor_widget = self.motor_widget_list[index] 
                    temp_motor_widget.set_motor(temp_motor_hwobj, hwobj_name)
                    temp_motor_widget.move_left_button.setVisible(True)
                    temp_motor_widget.move_right_button.setVisible(True)
                    temp_motor_widget.position_slider.setVisible(False)
                    temp_motor_widget.step_button.setVisible(False)
                    temp_motor_widget.stop_button.setVisible(False)
                    
                    try:  
                        temp_motor_widget.set_line_step(default_step_list[index])
                        temp_motor_widget['defaultStep'] = default_step_list[index]
                    except:
                        temp_motor_widget.set_line_step(0.001)
                        temp_motor_widget['defaultStep'] = 0.001

                    try:    
                        temp_motor_widget['delta'] = default_delta_list[index]
                    except:
                        temp_motor_widget['delta'] = 0.001

                    try:
                        temp_motor_widget.set_decimals(float(default_decimal_list[index]))
                    except:
                        pass

                    try:
                        temp_motor_widget.move_left_button.setIcon(\
                            Qt4_Icons.load_icon(icon_list[index * 2]))
                        temp_motor_widget.move_right_button.setIcon(\
                            Qt4_Icons.load_icon(icon_list[index * 2 + 1]))
                    except:
                        temp_motor_widget.move_left_button.setIcon(\
                            Qt4_Icons.load_icon("Right2"))
                        temp_motor_widget.move_right_button.setIcon(\
                            Qt4_Icons.load_icon("Left2"))

                    
                    temp_motor_widget.step_changed(None)
                    temp_motor_hwobj.update_values()
                    temp_motor_widget.update_gui()
        elif property_name == 'hwobj_beam_focusing':
            if self.beam_focusing_hwobj is not None:
                self.disconnect(self.beam_focusing_hwobj,
                                'focusingModeChanged',
                                self.focus_mode_changed)
            self.beam_focusing_hwobj = self.getHardwareObject(new_value)
            if self.beam_focusing_hwobj is not None:
                self.connect(self.beam_focusing_hwobj,
                             'focusingModeChanged',
                             self.focus_mode_changed)
                mode, beam_size = self.beam_focusing_hwobj.get_active_focus_mode()
                self.focus_mode_changed(mode, beam_size)
        elif property_name == "hwobj_beamline_test":
            self.beamline_test_hwobj = self.getHardwareObject(new_value)  
        elif property_name == "hwobj_diffractometer":
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj,
                                'minidiffPhaseChanged',
                                self.phase_changed)
            self.diffractometer_hwobj = self.getHardwareObject(new_value)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj,
                             'minidiffPhaseChanged',
                             self.phase_changed)
            self.update_gui()
        else:
            BlissWidget.propertyChanged(self,property_name, old_value, new_value)

    def run(self):
        self.update_gui()         

    def focus_mode_changed(self, new_focus_mode, beam_size):
        self.focus_mode = new_focus_mode
        self.update_gui()

    def update_gui(self):
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

        self.unf_hor_motor_brick.setEnabled(self.is_beam_location_phase)
        self.unf_ver_motor_brick.setEnabled(self.is_beam_location_phase)
        self.double_hor_motor_brick.setEnabled(self.is_beam_location_phase)
        self.double_ver_motor_brick.setEnabled(self.is_beam_location_phase)

    def center_beam_clicked(self):
        conf_msg = "This will start automatic beam centering. Continue?"
        if QMessageBox.warning(None, "Question", conf_msg,
               QMessageBox.Ok, QMessageBox.Cancel) == QMessageBox.Ok:
            self.beamline_test_hwobj.center_beam_report()

    def phase_changed(self, phase):
        self.is_beam_location_phase = phase == self.diffractometer_hwobj.PHASE_BEAM
        self.update_gui()

    def measure_flux_clicked(self):
        conf_msg = "This will measure flux. Continue?"
        if QMessageBox.warning(None, "Question", conf_msg,
               QMessageBox.Ok, QMessageBox.Cancel) == QMessageBox.Ok:
            self.beamline_test_hwobj.measure_intensity()
