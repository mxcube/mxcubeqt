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

"""AcquisitionStillWidget is customized for ssx type acquisitions"""

from gui.utils import QtImport
from gui.utils.widget_utils import DataModelInputBinder

from HardwareRepository.HardwareObjects import queue_model_objects

from HardwareRepository import HardwareRepository as HWR


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
        """
        Loads ui file that defines the gui layout.
        Initiates QLineEdits by adding limits, precision
        Connects to qt signals to update acquisition parameters
        :param parent:
        :param name:
        :param fl:
        :param acq_params:
        :param path_template:
        :param layout:
        """

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Internal variables --------------------------------------------------
        self.value_changed_list = []

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
        self.hare_num_validator = QtImport.QIntValidator(
            1, 9999999, self.acq_widget_layout.hare_num_ledit
        )

        limits_dict = HWR.beamline.acquisition_limit_values

        tpl = limits_dict.get("exposure_time")
        if tpl:
            self.exp_time_validator.setRange(tpl[0], tpl[1], 6)

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

        self._acquisition_mib.bind_value_update(
            "hare_num",
            self.acq_widget_layout.hare_num_ledit,
            int,
            self.hare_num_validator,
        )


        tpl = limits_dict.get("number_of_images")
        if tpl:
            self.num_img_validator.setRange(tpl[0], tpl[1])

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

        self.init_detector_roi_modes()
        self.acq_widget_layout.detector_roi_mode_label.setEnabled(False)
        self.acq_widget_layout.detector_roi_mode_combo.setEnabled(False)
        self.update_exp_time_limits()

    def update_osc_total_range(self):
        """
        :return: None
        """
        return

    def use_osc_start(self, status):
        """
        :param status: boolean
        :return: None
        """
        return

    def use_max_osc_range(self, status):
        """
        :param status: boolean
        :return: None
        """
        return

    def use_kappa(self, status):
        """
        :param status: boolean
        :return: None
        """
        return

    def exposure_time_ledit_changed(self, value):
        """
        Updates exposure time QLineEdit
        :param value: str
        :return: None
        """
        self.update_total_exp_time()
        self.emit_acq_parameters_changed()

    def energy_ledit_changed(self, value):
        """
        Fixes energy value. Energy change will not rewrite the typed energy value
        :param value: str
        :return: None
        """
        if "energy" not in self.value_changed_list:
            self.value_changed_list.append("energy")
        self.emit_acq_parameters_changed()

    def update_energy(self, energy, wav=None):
        """
        Updates energy QLineEdit
        :param energy: energy in keV (float)
        :param wav: wavelength in A (float)
        :return: None
        """
        if (
            "energy" not in self.value_changed_list
            and not self.acq_widget_layout.energy_ledit.hasFocus()
        ):
            self.acq_widget_layout.energy_ledit.setText(str(energy))
        self.emit_acq_parameters_changed()

    def transmission_ledit_changed(self, transmission):
        """
        Event when a value in the transmission QLineEdit is changed
        :param transmission: in perc. (str)
        :return: None
        """
        if "transmission" not in self.value_changed_list:
            self.value_changed_list.append("transmission")
        self.emit_acq_parameters_changed()

    def update_transmission(self, transmission):
        """
        Updates transmission QLineEdit
        :param transmission: in perc. (float)
        :return: None
        """
        if "transmission" not in self.value_changed_list:
            self.acq_widget_layout.transmission_ledit.setText(str(transmission))
        self.emit_acq_parameters_changed()

    def resolution_ledit_changed(self, resolution):
        """
        Method called when user changes resolution
        :param resolution: in A (float)
        :return: None
        """
        if "resolution" not in self.value_changed_list:
            self.value_changed_list.append("resolution")
        self.emit_acq_parameters_changed()

    def update_resolution(self, resolution):
        """
        Updates resolution QLineEdit
        :param resolution: A (float)
        :return: None
        """
        if (
            "resolution" not in self.value_changed_list
            and not self.acq_widget_layout.resolution_ledit.hasFocus()
        ):
            self.acq_widget_layout.resolution_ledit.setText(str(resolution))
        self.emit_acq_parameters_changed()

    def update_energy_limits(self, limits):
        """
        Updates energy limits
        :param limits: list of two floats
        :return: None
        """
        if limits:
            self.energy_validator.setBottom(limits[0])
            self.energy_validator.setTop(limits[1])
            self.acq_widget_layout.energy_ledit.setToolTip(
                "Energy limits %0.4f : %0.4f keV\n" % (limits[0], limits[1])
                + "4 digits precision."
            )
            self._acquisition_mib.validate_all()

    def update_transmission_limits(self, limits):
        """
        Updates transmission limits
        :param limits: list of two floats
        :return: None
        """
        if limits:
            self.transmission_validator.setBottom(limits[0])
            self.transmission_validator.setTop(limits[1])
            self.acq_widget_layout.transmission_ledit.setToolTip(
                "Transmission limits %0.2f : %0.2f %%\n" % (limits[0], limits[1])
                + "2 digits precision."
            )
            self._acquisition_mib.validate_all()

    def update_resolution_limits(self, limits):
        """
        Updates resolution limits
        :param limits: list of two floats
        :return: None
        """
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
        """
        Updates exposure time limits
        :param limits: list of two floats
        :return: None
        """
        if limits:
            self.exp_time_validator.setRange(limits[0], limits[1], 6)
            self.acq_widget_layout.exp_time_ledit.setToolTip(
                "Exposure time limits %0.6f s : %0.1f s\n" % (limits[0], limits[1])
                + "6 digits precision."
            )
            self._acquisition_mib.validate_all()

    def init_detector_roi_modes(self):
        """
        Initiates detetor ROI modes. Available modes are added to the combobox
        :return: None
        """
        roi_modes = HWR.beamline.detector.get_roi_modes()
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
        """
        Method called when roi mode has been chaned
        :param roi_mode_index: int
        :return: None
        """
        if (
            roi_mode_index is not None
            and self.acq_widget_layout.detector_roi_mode_combo.count() > 0
        ):
            self.acq_widget_layout.detector_roi_mode_combo.setCurrentIndex(
                roi_mode_index
            )

    def detector_roi_mode_changed(self, roi_mode_index):
        """
        Method called when user selects a detector roi mode
        :param roi_mode_index: int
        :return:
        """
        HWR.beamline.detector.set_roi_mode(roi_mode_index)

    def update_osc_range_per_frame_limits(self):
        """
        Updates osc range per frame limits
        :return: None
        """
        return

    def update_exp_time_limits(self):
        self.update_detector_exp_time_limits(
            HWR.beamline.detector.get_exposure_time_limits()
        )

    def update_osc_start(self, value):
        """
        Updates osc start
        :param value: float
        :return: None
        """
        return

    def update_kappa(self, value):
        """
        Updates kappa value
        :param value: float
        :return:
        """
        return

    def update_kappa_phi(self, value):
        """
        Updates kappa phi value
        :param value: float
        :return: None
        """
        return

    def update_data_model(self, acquisition_parameters, path_template):
        """
        Updates data model
        :param acquisition_parameters: AcquisitionParameters
        :param path_template: PathTemplate
        :return: None
        """
        self._acquisition_parameters = acquisition_parameters
        self._path_template = path_template
        self._acquisition_mib.set_model(acquisition_parameters)
        self.emit_acq_parameters_changed()

    def check_parameter_conflict(self):
        """
        Checks for parameter conflicts
        :return: list of conflicts
        """
        return self._acquisition_mib.validate_all()

    def emit_acq_parameters_changed(self):
        """
        Emits acqParametersChangedSignal
        :return: None
        """
        self.acqParametersChangedSignal.emit(self._acquisition_mib.validate_all())

    def set_energies(self, energies):
        """
        Sets energies
        :param energies:
        :return: None
        """
        return

    def num_triggers_ledit_changed(self, value):
        """
        Updates num images and total exp time
        :param value: QString
        :return: None
        """
        if "num_triggers" not in self.value_changed_list:
            self.value_changed_list.append("num_triggers")
        self.update_num_images()
        self.update_total_exp_time()
        self.emit_acq_parameters_changed()

    def num_images_per_trigger_ledit_changed(self, value):
        """
                Updates num images and total exp time
                :param value: QString
                :return: None
                """
        if "num_images_per_trigger" not in self.value_changed_list:
            self.value_changed_list.append("num_images_per_trigger")
        self.update_num_images()
        self.update_total_exp_time()
        self.emit_acq_parameters_changed()

    def update_num_images(self):
        """
        Updates num images
        :return: None
        """
        self.acq_widget_layout.num_images_ledit.setText(
            str(
                self._acquisition_parameters.num_triggers
                * self._acquisition_parameters.num_images_per_trigger
            )
        )

    def update_total_exp_time(self):
        """Updates total exposure time
        :return: None
        """
        try:
            self.acq_widget_layout.exp_time_total_ledit.setText(
                "%.2f"
                % (
                    float(self.acq_widget_layout.exp_time_ledit.text())
                    * float(self.acq_widget_layout.num_images_ledit.text())
                )
            )
        except BaseException:
            pass
