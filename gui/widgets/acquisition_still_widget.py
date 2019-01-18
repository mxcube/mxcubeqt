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

import QtImport

from gui.utils.widget_utils import DataModelInputBinder

from HardwareRepository.HardwareObjects import queue_model_objects


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class AcquisitionStillWidget(QtImport.QWidget):

    acqParametersChangedSignal = QtImport.pyqtSignal(list)

    def __init__(
        self,
        parent=None,
        name=None,
        fl=0,
        acq_params=None,
        path_template=None,
        layout="vertical",
    ):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None
        self._diffractometer_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        if acq_params is None:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
        else:
            self._acquisition_parameters = acq_params

        if path_template is None:
            self._path_template = queue_model_objects.PathTemplate()
        else:
            self._path_template = path_template

        self._acquisition_mib = DataModelInputBinder(self._acquisition_parameters)

        self.acq_widget_layout = QtImport.load_ui_file(
            "acquisition_widget_vertical_still_layout.ui"
        )
        # Layout --------------------------------------------------------------
        __main_vlayout = QtImport.QVBoxLayout(self)
        __main_vlayout.addWidget(self.acq_widget_layout)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.acq_widget_layout.num_triggers_ledit.textChanged.connect(
            self.num_triggers_ledit_changed
        )
        self.acq_widget_layout.num_images_per_trigger_ledit.textChanged.connect(
            self.num_images_per_trigger_ledit_changed
        )

        self.acq_widget_layout.exp_time_ledit.textChanged.connect(
            self.exposure_time_ledit_changed
        )
        self.acq_widget_layout.detector_roi_mode_combo.activated.connect(
            self.detector_roi_mode_changed
        )
        self.acq_widget_layout.energy_ledit.textEdited.connect(
            self.energy_ledit_changed
        )
        self.acq_widget_layout.transmission_ledit.textEdited.connect(
            self.transmission_ledit_changed
        )
        self.acq_widget_layout.resolution_ledit.textEdited.connect(
            self.resolution_ledit_changed
        )

        # Other ---------------------------------------------------------------
        self.value_changed_list = []

        self.energy_validator = QtImport.QDoubleValidator(
            4, 25, 4, self.acq_widget_layout.energy_ledit
        )
        self.resolution_validator = QtImport.QDoubleValidator(
            0, 15, 3, self.acq_widget_layout.resolution_ledit
        )
        self.transmission_validator = QtImport.QDoubleValidator(
            0, 100, 3, self.acq_widget_layout.transmission_ledit
        )
        self.exp_time_validator = QtImport.QDoubleValidator(
            0.0001, 10000, 7, self.acq_widget_layout.exp_time_ledit
        )
        self.num_triggers_validator = QtImport.QIntValidator(
            1, 9999999, self.acq_widget_layout.num_triggers_ledit
        )
        self.num_images_per_trigger_validator = QtImport.QIntValidator(
            1, 9999999, self.acq_widget_layout.num_images_per_trigger_ledit
        )
        self.num_img_validator = QtImport.QIntValidator(
            1, 9999999, self.acq_widget_layout.num_images_ledit
        )
        self.acq_widget_layout.detector_roi_mode_label.setEnabled(False)
        self.acq_widget_layout.detector_roi_mode_combo.setEnabled(False)

    def update_osc_total_range(self):
        pass

    def use_osc_start(self, status):
        pass

    def use_max_osc_range(self, status):
        pass

    def use_kappa(self, status):
        pass

    def set_beamline_setup(self, beamline_setup):
        self._beamline_setup_hwobj = beamline_setup
        limits_dict = self._beamline_setup_hwobj.get_acquisition_limit_values()
        self._diffractometer_hwobj = self._beamline_setup_hwobj.diffractometer_hwobj

        if "exposure_time" in limits_dict:
            limits = tuple(map(float, limits_dict["exposure_time"].split(",")))
            (lower, upper) = limits
            self.exp_time_validator.setRange(lower, upper, 6)

        self._acquisition_mib.bind_value_update(
            "exp_time",
            self.acq_widget_layout.exp_time_ledit,
            float,
            self.exp_time_validator,
        )

        self._acquisition_mib.bind_value_update(
            "num_triggers",
            self.acq_widget_layout.num_triggers_ledit,
            int,
            self.num_triggers_validator,
        )

        self._acquisition_mib.bind_value_update(
            "num_images_per_trigger",
            self.acq_widget_layout.num_images_per_trigger_ledit,
            int,
            self.num_images_per_trigger_validator,
        )

        if "number_of_images" in limits_dict:
            limits = tuple(map(float, limits_dict["number_of_images"].split(",")))
            (lower, upper) = limits
            self.num_img_validator.setRange(lower, upper)

        self._acquisition_mib.bind_value_update(
            "num_images",
            self.acq_widget_layout.num_images_ledit,
            int,
            self.num_img_validator,
        )

        self._acquisition_mib.bind_value_update(
            "energy", self.acq_widget_layout.energy_ledit, float, self.energy_validator
        )
        self.update_energy_limits(
            (self.energy_validator.bottom(), self.energy_validator.top())
        )

        self._acquisition_mib.bind_value_update(
            "transmission",
            self.acq_widget_layout.transmission_ledit,
            float,
            self.transmission_validator,
        )
        self.update_transmission_limits(
            (self.transmission_validator.bottom(), self.transmission_validator.top())
        )

        self._acquisition_mib.bind_value_update(
            "resolution",
            self.acq_widget_layout.resolution_ledit,
            float,
            self.resolution_validator,
        )

        has_shutter_less = self._beamline_setup_hwobj.detector_has_shutterless()
        self.init_detector_roi_modes()

    def exposure_time_ledit_changed(self, new_values):
        self.emit_acq_parameters_changed()

    def energy_ledit_changed(self, new_value):
        if "energy" not in self.value_changed_list:
            self.value_changed_list.append("energy")
        self.emit_acq_parameters_changed()

    def update_energy(self, energy, wav=None):
        if (
            "energy" not in self.value_changed_list
            and not self.acq_widget_layout.energy_ledit.hasFocus()
        ):
            self.acq_widget_layout.energy_ledit.setText(str(energy))
        self.emit_acq_parameters_changed()

    def transmission_ledit_changed(self, transmission):
        if "transmission" not in self.value_changed_list:
            self.value_changed_list.append("transmission")
        self.emit_acq_parameters_changed()

    def update_transmission(self, transmission):
        if "transmission" not in self.value_changed_list:
            self.acq_widget_layout.transmission_ledit.setText(str(transmission))
        self.emit_acq_parameters_changed()

    def resolution_ledit_changed(self, resolution):
        if "resolution" not in self.value_changed_list:
            self.value_changed_list.append("resolution")
        self.emit_acq_parameters_changed()

    def update_resolution(self, resolution):
        if (
            "resolution" not in self.value_changed_list
            and not self.acq_widget_layout.resolution_ledit.hasFocus()
        ):
            self.acq_widget_layout.resolution_ledit.setText(str(resolution))
        self.emit_acq_parameters_changed()

    def update_energy_limits(self, limits):
        if limits:
            self.energy_validator.setBottom(limits[0])
            self.energy_validator.setTop(limits[1])
            self.acq_widget_layout.energy_ledit.setToolTip(
                "Energy limits %0.4f : %0.4f keV\n" % (limits[0], limits[1])
                + "4 digits precision."
            )
            self._acquisition_mib.validate_all()

    def update_transmission_limits(self, limits):
        if limits:
            self.transmission_validator.setBottom(limits[0])
            self.transmission_validator.setTop(limits[1])
            self.acq_widget_layout.transmission_ledit.setToolTip(
                "Transmission limits %0.2f : %0.2f %%\n" % (limits[0], limits[1])
                + "2 digits precision."
            )
            self._acquisition_mib.validate_all()

    def update_resolution_limits(self, limits):
        if limits:
            self.resolution_validator.setBottom(limits[0])
            self.resolution_validator.setTop(limits[1])
            self.acq_widget_layout.resolution_ledit.setToolTip(
                "Resolution limits %0.4f : %0.4f %s\n"
                % (limits[0], limits[1], chr(197))
                + "4 digits precision."
            )
            self._acquisition_mib.validate_all()

    def update_detector_exp_time_limits(self, limits):
        if limits:
            self.exp_time_validator.setRange(limits[0], limits[1], 6)
            self.acq_widget_layout.exp_time_ledit.setToolTip(
                "Exposure time limits %0.6f s : %0.1f s\n" % (limits[0], limits[1])
                + "6 digits precision."
            )
            self._acquisition_mib.validate_all()

    def init_detector_roi_modes(self):
        if self._beamline_setup_hwobj is not None:
            roi_modes = self._beamline_setup_hwobj.detector_hwobj.get_roi_modes()
            if (
                len(roi_modes) > 0
                and self.acq_widget_layout.detector_roi_mode_combo.count() == 0
            ):
                for roi_mode in roi_modes:
                    self.acq_widget_layout.detector_roi_mode_combo.addItem(roi_mode)
            self.acq_widget_layout.detector_roi_mode_label.setEnabled(
                len(roi_modes) > 1
            )
            self.acq_widget_layout.detector_roi_mode_combo.setEnabled(
                len(roi_modes) > 1
            )

    def update_detector_roi_mode(self, roi_mode_index):
        if (
            roi_mode_index is not None
            and self.acq_widget_layout.detector_roi_mode_combo.count() > 0
        ):
            self.acq_widget_layout.detector_roi_mode_combo.setCurrentIndex(
                roi_mode_index
            )

    def detector_roi_mode_changed(self, roi_mode_index):
        if self._beamline_setup_hwobj is not None:
            self._beamline_setup_hwobj.detector_hwobj.set_roi_mode(roi_mode_index)

    def update_osc_range_per_frame_limits(self):
        pass

    def update_exp_time_limits(self):
        pass

    def update_osc_start(self, value):
        pass

    def update_kappa(self, value):
        pass

    def update_kappa_phi(self, value):
        pass

    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._path_template = path_template
        self._acquisition_mib.set_model(acquisition_parameters)
        self.emit_acq_parameters_changed()

    def check_parameter_conflict(self):
        return self._acquisition_mib.validate_all()

    def emit_acq_parameters_changed(self):
        self.acqParametersChangedSignal.emit(self._acquisition_mib.validate_all())

    def set_energies(self, energies):
        pass

    def num_triggers_ledit_changed(self, value):
        if "num_triggers" not in self.value_changed_list:
            self.value_changed_list.append("num_triggers")
        self.update_num_images()
        self.emit_acq_parameters_changed()

    def num_images_per_trigger_ledit_changed(self, values):
        if "num_images_per_trigger" not in self.value_changed_list:
            self.value_changed_list.append("num_images_per_trigger")
        self.update_num_images()
        self.emit_acq_parameters_changed()

    def update_num_images(self):
        self.acq_widget_layout.num_images_ledit.setText(
            str(
                self._acquisition_parameters.num_triggers
                * self._acquisition_parameters.num_images_per_trigger
            )
        )
