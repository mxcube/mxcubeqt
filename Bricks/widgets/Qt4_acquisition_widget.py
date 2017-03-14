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
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os

from QtImport import *

import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_widget_utils import DataModelInputBinder
from BlissFramework.Utils import Qt4_widget_colors


MAD_ENERGY_COMBO_NAMES = {'ip': 0, 'pk': 1, 'rm1': 2, 'rm2': 3}


class AcquisitionWidget(QWidget):
    """
    Descript. :
    """
  
    acqParametersChangedSignal = pyqtSignal(list)
    madEnergySelectedSignal = pyqtSignal(str, float, bool)

    def __init__(self, parent = None, name = None, fl = 0, acq_params = None,
                 path_template = None, layout = 'horizontal'):
        """
        Descript. :
        """
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))
        
        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None
        self._diffractometer_hwobj = None

        # Internal variables --------------------------------------------------
        self.previous_energy = 0

        # Properties ---------------------------------------------------------- 

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        if acq_params is None:
            self._acquisition_parameters = queue_model_objects.\
                                           AcquisitionParameters()
        else:
            self._acquisition_parameters = acq_params

        if path_template is None:
           self._path_template = queue_model_objects.PathTemplate()
        else:
            self._path_template = path_template

        self._acquisition_mib = DataModelInputBinder(self._acquisition_parameters)

        if layout == "horizontal":
            self.acq_widget_layout = loadUi(os.path.join(\
                 os.path.dirname(__file__),
                 "ui_files/Qt4_acquisition_widget_horizontal_layout.ui"))
        else:
            self.acq_widget_layout = loadUi(os.path.join(\
                 os.path.dirname(__file__),
                 "ui_files/Qt4_acquisition_widget_vertical_layout.ui"))
        # Layout --------------------------------------------------------------
        __main_vlayout = QVBoxLayout(self)
        __main_vlayout.addWidget(self.acq_widget_layout)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.acq_widget_layout.osc_start_cbox.stateChanged.connect(\
             self.fix_osc_start)
        self.acq_widget_layout.exp_time_ledit.textChanged.connect(\
             self.exposure_time_ledit_changed)
        self.acq_widget_layout.first_image_ledit.textChanged.connect(\
             self.first_image_ledit_change)
        self.acq_widget_layout.num_images_ledit.textChanged.connect(\
             self.num_images_ledit_change)
        self.acq_widget_layout.detector_roi_mode_combo.activated.connect(\
             self.detector_roi_mode_changed)
        self.acq_widget_layout.energies_combo.activated.connect(\
             self.energy_selected)
        self.acq_widget_layout.mad_cbox.toggled.connect(\
             self.use_mad)

        self.acq_widget_layout.osc_start_ledit.textEdited.connect(\
             self.osc_start_ledit_changed)
        self.acq_widget_layout.osc_range_ledit.textEdited.connect(\
             self.osc_range_ledit_changed)
        self.acq_widget_layout.energy_ledit.textEdited.connect(\
             self.energy_ledit_changed)
        self.acq_widget_layout.transmission_ledit.textEdited.connect(\
             self.transmission_ledit_changed)
        self.acq_widget_layout.resolution_ledit.textEdited.connect(\
             self.resolution_ledit_changed)
        
        overlap_ledit = self.acq_widget_layout.findChild(\
            QLineEdit, "overlap_ledit")
        if overlap_ledit is not None:
            overlap_ledit.textChanged.connect(self.overlap_changed)

        # Other --------------------------------------------------------------- 
        self.value_changed_list = []

        self.acq_widget_layout.energies_combo.setDisabled(True)
        self.acq_widget_layout.energies_combo.addItems(['ip: -', 'pk: -', 'rm1: -', 'rm2: -'])

        self.osc_start_validator = QDoubleValidator(\
             -10000, 10000, 4, self.acq_widget_layout.osc_start_ledit)
        self.osc_range_validator = QDoubleValidator(\
             -10000, 10000, 4, self.acq_widget_layout.osc_range_ledit)
        self.kappa_validator = QDoubleValidator(\
             0, 360, 4, self.acq_widget_layout.kappa_ledit)
        self.kappa_phi_validator = QDoubleValidator(\
             0, 360, 4, self.acq_widget_layout.kappa_phi_ledit)
        self.energy_validator = QDoubleValidator(\
             4, 25, 4, self.acq_widget_layout.energy_ledit)
        self.resolution_validator = QDoubleValidator(\
             0, 15, 3, self.acq_widget_layout.resolution_ledit)
        self.transmission_validator = QDoubleValidator(\
             0, 100, 3, self.acq_widget_layout.transmission_ledit)
        self.exp_time_validator = QDoubleValidator(\
             0.0001, 10000, 4, self.acq_widget_layout.exp_time_ledit)
        self.first_img_validator = QIntValidator(\
             0, 99999, self.acq_widget_layout.first_image_ledit)
        self.num_img_validator = QIntValidator(\
             1, 99999, self.acq_widget_layout.num_images_ledit) 
        self.acq_widget_layout.detector_roi_mode_label.setEnabled(False)
        self.acq_widget_layout.detector_roi_mode_combo.setEnabled(False)

        if self.acq_widget_layout.findChild(QPushButton, "set_max_osc_range_button"):
            self.acq_widget_layout.set_max_osc_range_button.hide()

    def fix_osc_start(self, state):
        """
        Fix osc start, so the lineEdit do not change when osc is changed
        """
        self.acq_widget_layout.osc_start_ledit.setEnabled(state)

    def set_osc_start_limits(self, limits):
        """
        Sets osc start limits
        """
        if not None in limits:
            self.osc_start_validator.setRange(limits[0], limits[1], 4)
            self.update_osc_range_limits()
            self.update_num_images_limits()

    def osc_start_ledit_changed(self, osc_start):
        """Fixes osc start edit"""

        if "osc_start" not in self.value_changed_list:
            self.value_changed_list.append("osc_start")
        self.update_osc_range_limits()
        self.update_num_images_limits()

    def update_osc_start(self, new_value):
        """
        Updates osc line edit
        """
        if "osc_start" not in self.value_changed_list and \
           not self.acq_widget_layout.osc_start_ledit.hasFocus() and \
           not self.acq_widget_layout.osc_start_cbox.isChecked():
            osc_start_value = 0
            try:
               osc_start_value = round(float(new_value), 2)
            except TypeError:
               pass
    
            self.acq_widget_layout.osc_start_ledit.setText(str(osc_start_value))
            self._acquisition_parameters.osc_start = osc_start_value

            self.update_osc_range_limits() 
            self.update_num_images_limits()

    def osc_range_ledit_changed(self, new_value):
        self.update_num_images_limits()

    def update_kappa(self, new_value):
        """
        Updates kappa value
        """
        if not self.acq_widget_layout.kappa_ledit.hasFocus() and \
           new_value:
            self.acq_widget_layout.kappa_ledit.setText(str(new_value))
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def update_kappa_phi(self, new_value):
        """
        Descript. :
        """
        if not self.acq_widget_layout.kappa_phi_ledit.hasFocus() and \
           new_value:
            self.acq_widget_layout.kappa_phi_ledit.setText(str(new_value))
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def use_osc_start(self, state):
        """
        Descript. :
        """
        self.acq_widget_layout.osc_start_cbox.setVisible(state)
        self.acq_widget_layout.osc_start_label.setVisible(not state)
        self.acq_widget_layout.osc_start_ledit.setEnabled(not state)

    def use_kappa(self, state):
        """
        Descript. :
        """
        if self._diffractometer_hwobj is not None:
            if self._diffractometer_hwobj.in_plate_mode():
                state = False
        self.acq_widget_layout.kappa_label.setEnabled(state)
        self.acq_widget_layout.kappa_ledit.setEnabled(state)
        self.acq_widget_layout.kappa_phi_label.setEnabled(state)
        self.acq_widget_layout.kappa_phi_ledit.setEnabled(state)

    def set_beamline_setup(self, beamline_setup):
        """
        Descript. :
        """
        self._beamline_setup_hwobj = beamline_setup
        limits_dict = self._beamline_setup_hwobj.get_acquisition_limit_values()
        self._diffractometer_hwobj = self._beamline_setup_hwobj.diffractometer_hwobj
        

        if 'osc_range' in limits_dict:
            limits = tuple(map(float, limits_dict['osc_range'].split(',')))
            (lower, upper) = limits
            self.osc_start_validator.setRange(lower, upper, 4)
            self.osc_range_validator.setRange(lower, upper, 4)

        self._acquisition_mib.bind_value_update('osc_start', 
                                                self.acq_widget_layout.osc_start_ledit,
                                                float, 
                                                self.osc_start_validator)

        self._acquisition_mib.bind_value_update('osc_range', 
                                                self.acq_widget_layout.osc_range_ledit,
                                                float, 
                                                self.osc_range_validator)

        if 'kappa' in limits_dict:
            limits = tuple(map(float, limits_dict['kappa'].split(',')))
            (lower, upper) = limits
            self.kappa_validator.setRange(lower, upper, 4)
        self._acquisition_mib.bind_value_update('kappa', 
                                                self.acq_widget_layout.kappa_ledit,
                                                float,
                                                self.kappa_validator)

        if 'kappa_phi' in limits_dict:
            limits = tuple(map(float, limits_dict['kappa_phi'].split(',')))
            (lower, upper) = limits
            self.kappa_phi_validator.setRange(lower, upper, 4)
        self._acquisition_mib.bind_value_update('kappa_phi',     
                                                self.acq_widget_layout.kappa_phi_ledit,
                                                float,
                                                self.kappa_phi_validator)

        if 'exposure_time' in limits_dict:
            limits = tuple(map(float, limits_dict['exposure_time'].split(',')))
            (lower, upper) = limits
            self.exp_time_validator.setRange(lower, upper, 5)
        
        self._acquisition_mib.bind_value_update('exp_time', 
                                                self.acq_widget_layout.exp_time_ledit,
                                                float, 
                                                self.exp_time_validator)

        if 'number_of_images' in limits_dict:
            limits = tuple(map(int, limits_dict['number_of_images'].split(',')))
            (lower, upper) = limits
            self.num_img_validator.setRange(lower, upper)
            self.first_img_validator.setRange(lower, upper)
        
        self._acquisition_mib.bind_value_update('first_image', 
                                                self.acq_widget_layout.first_image_ledit,
                                                int, 
                                                self.first_img_validator)

        self._acquisition_mib.bind_value_update('num_images', 
                                                self.acq_widget_layout.num_images_ledit,
                                                int, 
                                                self.num_img_validator)

        num_passes = self.acq_widget_layout.findChild(QLineEdit, "num_passes_ledit")

        if num_passes:
            self._acquisition_mib.\
                bind_value_update('num_passes', num_passes, int,
                                  QIntValidator(1, 1000, self))

        overlap_ledit = self.acq_widget_layout.findChild(QLineEdit, "overlap_ledit")

        if overlap_ledit:
            self._acquisition_mib.\
                bind_value_update('overlap', overlap_ledit, float,
                                  QDoubleValidator(-1000, 1000, 2, self))

        self._acquisition_mib.\
             bind_value_update('energy',
                               self.acq_widget_layout.energy_ledit,
                               float,
                               self.energy_validator)
        self.update_energy_limits((self.energy_validator.bottom(),
                                   self.energy_validator.top()))

        self._acquisition_mib.\
             bind_value_update('transmission',
                               self.acq_widget_layout.transmission_ledit,
                               float,
                               self.transmission_validator)
        self.update_transmission_limits((self.transmission_validator.bottom(),
                                         self.transmission_validator.top()))

        self._acquisition_mib.\
             bind_value_update('resolution',
                               self.acq_widget_layout.resolution_ledit,
                               float,
                               self.resolution_validator)
        self.update_resolution_limits((self.resolution_validator.bottom(),
                                       self.resolution_validator.top()))

        self._acquisition_mib.\
             bind_value_update('shutterless',
                               self.acq_widget_layout.shutterless_cbx,
                               bool,
                               None)

        self.set_tunable_energy(beamline_setup.tunable_wavelength())

        has_shutter_less = self._beamline_setup_hwobj.detector_has_shutterless()
        self.acq_widget_layout.shutterless_cbx.setEnabled(has_shutter_less)
        self.acq_widget_layout.shutterless_cbx.setChecked(has_shutter_less)

        if self._beamline_setup_hwobj.disable_num_passes():
            num_passes = self.acq_widget_layout.findChild(QLineEdit, "num_passes_ledit")
            if num_passes:
                num_passes.setDisabled(True)

    def first_image_ledit_change(self, new_value):
        """
        Descript. :
        """
        if str(new_value).isdigit():
            #self._path_template.start_num = int(new_value)
            #widget = self.acq_widget_layout.first_image_ledit
            self.acqParametersChangedSignal.emit(\
                 self.check_parameter_conflict())

    def exposure_time_ledit_changed(self, new_values):
        """
        Descript. :
        """
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def num_images_ledit_change(self, new_value):
        """
        Descript. :
        """
        if str(new_value).isdigit():
            #self._path_template.num_files = int(new_value)
            self.acqParametersChangedSignal.emit(\
                 self.check_parameter_conflict())

    def overlap_changed(self, new_value):
        """
        Descript. :
        """
        if self._beamline_setup_hwobj:
            has_shutter_less = self._beamline_setup_hwobj.detector_has_shutterless()
        else:
            has_shutter_less = True

        if has_shutter_less:
            try:
                new_value = float(new_value)
            except ValueError:
                pass

            if new_value != 0:
                self.acq_widget_layout.shutterless_cbx.setEnabled(False)
                self.acq_widget_layout.shutterless_cbx.setChecked(False)
                self._acquisition_parameters.shutterless = False
            else:
                self.acq_widget_layout.shutterless_cbx.setEnabled(True)
                self.acq_widget_layout.shutterless_cbx.setChecked(True)
                self._acquisition_parameters.shutterless = True

    def use_mad(self, state):
        """
        Descript. :
        """
        self.acq_widget_layout.energies_combo.setEnabled(state)
        if state:
            (name, energy) = self.get_mad_energy()

            if energy != 0:
                self.update_energy(energy)
            self.madEnergySelectedSignal.emit(name, energy, state)
        else:
            self.update_energy(self.previous_energy)
            energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
            self.madEnergySelectedSignal.emit('', self.previous_energy, state)

    def get_mad_energy(self):
        """
        Descript. :
        """
        energy_str = str(self.acq_widget_layout.energies_combo.currentText())
        (name, value) = energy_str.split(':')
        
        name = name.strip()
        value = value.strip()
        value = 0 if (value == '-') else float(value)

        return (name, value)

    def set_energies(self, energy_scan_result):
        """
        Descript. :
        """
        self.acq_widget_layout.energies_combo.clear()

        inflection = ('ip: %.4f' % energy_scan_result.inflection) if \
                     energy_scan_result.inflection else 'ip: -'

        peak = ('pk: %.4f' % energy_scan_result.peak) if \
               energy_scan_result.peak else 'pk: -'

        first_remote = ('rm1: %.4f' % energy_scan_result.first_remote) if \
                       energy_scan_result.first_remote else 'rm1: -'

        second_remote = ('rm2: %.4f' % energy_scan_result.second_remote) if \
                        energy_scan_result.second_remote else 'rm2: -'

        self.acq_widget_layout.energies_combo.\
             addItems([inflection, peak, first_remote, second_remote])

    def energy_selected(self, index):
        """
        Descript. :
        """
        if self.acq_widget_layout.mad_cbox.isChecked():
            (name, energy) = self.get_mad_energy()
            if energy != 0:
                self.update_energy(energy)

            self.madEnergySelectedSignal.emit(name, energy, True)

    def energy_ledit_changed(self, energy):
        if "energy" not in self.value_changed_list:
            self.value_changed_list.append("energy") 
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def update_energy(self, energy, wav=None):
        """
        Descript. :
        """
        if "energy" not in self.value_changed_list and \
           not self.acq_widget_layout.energy_ledit.hasFocus():
            self.acq_widget_layout.energy_ledit.setText(str(energy))
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def transmission_ledit_changed(self, transmission):
        if "transmission" not in self.value_changed_list:
            self.value_changed_list.append("transmission")
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def update_transmission(self, transmission):
        if "transmission" not in self.value_changed_list:
            self.acq_widget_layout.transmission_ledit.setText(str(transmission))
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())
           
    def resolution_ledit_changed(self, resolution):
        if "resolution" not in self.value_changed_list:
            self.value_changed_list.append("resolution") 
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def update_resolution(self, resolution):
        if "resolution" not in self.value_changed_list and \
           not self.acq_widget_layout.resolution_ledit.hasFocus():
            self.acq_widget_layout.resolution_ledit.setText(str(resolution))
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def update_energy_limits(self, limits):
        if limits:
            self.energy_validator.setBottom(limits[0])
            self.energy_validator.setTop(limits[1])
            self.acq_widget_layout.energy_ledit.setToolTip(\
               "Energy limits %0.4f : %0.4f keV\n" % \
               (limits[0], limits[1]) + \
               "4 digits precision.")
            self._acquisition_mib.validate_all()

    def update_transmission_limits(self, limits):
        if limits:
            self.transmission_validator.setBottom(limits[0])
            self.transmission_validator.setTop(limits[1])
            self.acq_widget_layout.transmission_ledit.setToolTip(\
               "Transmission limits %0.2f : %0.2f %%\n" % \
               (limits[0], limits[1]) + \
               "2 digits precision.")
            self._acquisition_mib.validate_all()

    def update_resolution_limits(self, limits):
        if limits:
            self.resolution_validator.setBottom(limits[0])
            self.resolution_validator.setTop(limits[1])
            self.acq_widget_layout.resolution_ledit.setToolTip(
               "Resolution limits %0.4f : %0.4f %s\n" % \
               (limits[0], limits[1], chr(197)) + 
               "4 digits precision.")
            self._acquisition_mib.validate_all()

    def update_detector_exp_time_limits(self, limits):
        if limits:
            self.exp_time_validator.setRange(limits[0], limits[1], 4)
            self.acq_widget_layout.exp_time_ledit.setToolTip(
               "Exposure time limits %0.4f s : %0.4f s\n" % \
               (limits[0], limits[1]) + \
               "5 digits precision.")
            self._acquisition_mib.validate_all()

    def update_osc_range_limits(self, limits=None):
        """Updates osc range limits.
           Osc range limits are changed if a plate is used.
           - For simple oscillation osc_range is defined by osc_start and 
             osc_start top limit.
           - For mesh osc_range is defined by number of images per line
             and osc in the middle of mesh  
        """

        if self._diffractometer_hwobj.in_plate_mode():
            if limits is None:
                osc_start = float(self.acq_widget_layout.osc_start_ledit.text())
                limits = [0, abs(self.osc_start_validator.top() - osc_start)]

            self.osc_range_validator.setRange(limits[0], limits[1], 4)
            self.acq_widget_layout.osc_range_ledit.setToolTip(
                "Oscillation range limits %0.4f : %0.4f\n4 digits precision." % \
                (limits[0], limits[1]))
            self._acquisition_mib.validate_all()

    def update_num_images_limits(self, num_images_limits=None):
        """Updates number of images limit
           Method used if plate mode.
        """
        if self._diffractometer_hwobj.in_plate_mode():
           if num_images_limits is None:
               try:
                  osc_start = float(self.acq_widget_layout.osc_start_ledit.text())
                  osc_range = float(self.acq_widget_layout.osc_range_ledit.text())
               except ValueError:
                  return

               if osc_range == 0:
                   return

               num_images_limits = int((self.osc_start_validator.top() - \
                                        osc_start) / osc_range)

           self.num_img_validator.setTop(num_images_limits)
           self.acq_widget_layout.num_images_ledit.setToolTip(\
               "Number of images limits : %d" % num_images_limits)
           self._acquisition_mib.validate_all()

    def init_detector_roi_modes(self):
        """
        Descript. :
        """
        if self._beamline_setup_hwobj is not None:
            roi_modes = self._beamline_setup_hwobj._get_roi_modes()
            if (len(roi_modes) > 0 and
                self.acq_widget_layout.detector_roi_mode_combo.count() == 0):
                for roi_mode in roi_modes:
                    self.acq_widget_layout.detector_roi_mode_combo.\
                         addItem(roi_mode)
                self.acq_widget_layout.detector_roi_mode_label.setEnabled(True)
                self.acq_widget_layout.detector_roi_mode_combo.setEnabled(True)
                #self._acquisition_mib.bind_value_update('detector_roi_mode',
                #               self.acq_widget_layout.detector_roi_mode_combo,
                ##               str,
                #               None)

    def update_detector_roi_mode(self, roi_mode_index):
        """
        Descript. :
        """
        if self.acq_widget_layout.detector_roi_mode_combo.count() > 0:
            self.acq_widget_layout.detector_roi_mode_combo.\
                 setCurrentIndex(roi_mode_index)

    def detector_roi_mode_changed(self, roi_mode_index):
        """
        Descript. :
        """
        if self._beamline_setup_hwobj is not None:
            self._beamline_setup_hwobj.detector_hwobj.set_roi_mode(roi_mode_index)

    def update_data_model(self, acquisition_parameters, path_template):
        """
        Descript. :
        """
        self._acquisition_parameters = acquisition_parameters
        self._path_template = path_template        
        self._acquisition_mib.set_model(acquisition_parameters)
        
        #Update mad widgets
        mad = True if self._path_template.mad_prefix != '' else False

        if mad:
            mad_prefix = self._path_template.mad_prefix
            index = MAD_ENERGY_COMBO_NAMES[mad_prefix]
            self.acq_widget_layout.energies_combo.setCurrentIndex(index)
            self.acq_widget_layout.mad_cbox.setChecked(True)
            self.acq_widget_layout.energies_combo.setEnabled(True)
        else:
            self.acq_widget_layout.mad_cbox.setChecked(False)
            self.acq_widget_layout.energies_combo.setEnabled(False)
            self.acq_widget_layout.energies_combo.setCurrentIndex(0)
        self.acqParametersChangedSignal.emit(\
             self.check_parameter_conflict())

    def set_tunable_energy(self, state):
        """
        Descript. :
        """
        self.acq_widget_layout.energy_ledit.setEnabled(state)
        self.acq_widget_layout.mad_cbox.setEnabled(state)
        self.acq_widget_layout.energies_combo.setEnabled(state)

    def check_parameter_conflict(self):
        return self._acquisition_mib.validate_all()
