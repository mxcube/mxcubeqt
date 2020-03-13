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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from gui.utils import QtImport
from gui.utils.widget_utils import DataModelInputBinder


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class XrayImagingParametersWidget(QtImport.QWidget):
    def __init__(self, parent=None, name=None, fl=0, xray_imaging_params=None):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self._xray_imaging_parameters = xray_imaging_params
        self._xray_imaging_mib = DataModelInputBinder(self._xray_imaging_parameters)

        self._parameters_widget = QtImport.load_ui_file(
            "xray_imaging_parameters_widget_layout.ui"
        )
        # Layout --------------------------------------------------------------
        __main_vlayout = QtImport.QVBoxLayout(self)
        __main_vlayout.addWidget(self._parameters_widget)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._parameters_widget.ff_pre_cbox.toggled.connect(self.ff_pre_toggled)
        self._parameters_widget.ff_post_cbox.toggled.connect(self.ff_post_toggled)
        self._parameters_widget.add_button.pressed.connect(self.add_distance_pressed)
        self._parameters_widget.remove_button.pressed.connect(self.remove_distance_pressed)

        # Other ---------------------------------------------------------------
        # self.detector_distance_validator = QtImport.QIntValidator(
        #     0, 99999, self._parameters_widget.detector_distance_ledit
        # )
        self.detector_distance_validator = QtImport.QDoubleValidator(
            0, 99999, 2, self._parameters_widget.detector_distance_ledit
        )

        self._xray_imaging_mib.bind_value_update(
            "camera_write_data", self._parameters_widget.store_data_cbox, bool, None
        )

        self._xray_imaging_mib.bind_value_update(
            "ff_pre", self._parameters_widget.ff_pre_cbox, bool, None
        )

        self._xray_imaging_mib.bind_value_update(
            "ff_post", self._parameters_widget.ff_post_cbox, bool, None
        )

        self._xray_imaging_mib.bind_value_update(
            "ff_apply", self._parameters_widget.ff_apply_cbox, bool, None
        )

        self._xray_imaging_mib.bind_value_update(
            "ff_ssim_enabled", self._parameters_widget.ff_ssim_cbox, bool, None
        )

        self._xray_imaging_mib.bind_value_update(
            "ff_num_images", self._parameters_widget.ff_num_images_ledit, int, None
        )

        self._xray_imaging_mib.bind_value_update(
            "sample_offset_a",
            self._parameters_widget.ff_offset_a_ledit,
            float,
            None,
        )

        self._xray_imaging_mib.bind_value_update(
            "sample_offset_b",
            self._parameters_widget.ff_offset_b_ledit,
            float,
            None,
        )

        self._xray_imaging_mib.bind_value_update(
            "sample_offset_c",
            self._parameters_widget.ff_offset_c_ledit,
            float,
            None,
        )

        self._xray_imaging_mib.bind_value_update(
            "detector_distance",
            self._parameters_widget.detector_distance_ledit,
            float,
            self.detector_distance_validator,
        )

    def ff_pre_toggled(self, state):
        self.toggle_ff_controls()
        
    def ff_post_toggled(self, state):
        self.toggle_ff_controls()

    def toggle_ff_controls(self):
        enable_ff_controls = self._parameters_widget.ff_pre_cbox.isChecked() or \
           self._parameters_widget.ff_post_cbox.isChecked()

        self._parameters_widget.ff_apply_cbox.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_ssim_cbox.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_num_images_label.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_num_images_ledit.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_a_label.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_a_ledit.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_b_label.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_b_ledit.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_c_label.setEnabled(enable_ff_controls)
        self._parameters_widget.ff_offset_c_ledit.setEnabled(enable_ff_controls)

    def add_distance_pressed(self):
        if str(self._parameters_widget.detector_distance_ledit.text()).isdigit:
            self._parameters_widget.detector_distance_listwidget.addItem(self._parameters_widget.detector_distance_ledit.text())
            self._parameters_widget.remove_button.setEnabled(True)
            self._parameters_widget.detector_distance_listwidget.setCurrentRow(self._parameters_widget.detector_distance_listwidget.count() - 1)
 
    def remove_distance_pressed(self):
        self._parameters_widget.detector_distance_listwidget.takeItem(
            self._parameters_widget.detector_distance_listwidget.currentRow())
        self._parameters_widget.remove_button.setEnabled(
            self._parameters_widget.detector_distance_listwidget.count > 0) 

    def enable_distance_tools(self, state):
        self._parameters_widget.add_button.setEnabled(state)
        self._parameters_widget.remove_button.setEnabled(state)
        self._parameters_widget.detector_distance_listwidget.setEnabled(state)

    def set_detector_distance(self, value):
        self._parameters_widget.detector_distance_ledit.setText("%d" % value)
        self._xray_imaging_parameters.detector_distance = value

    def populate_widget(self, item):
        xray_imaging_params = item.get_model().xray_imaging_parameters
        self.update_data_model(xray_imaging_params)

    def update_data_model(self, xray_imaging_params):
        self._xray_imaging_parameters = xray_imaging_params
        self._xray_imaging_mib.set_model(xray_imaging_params)
