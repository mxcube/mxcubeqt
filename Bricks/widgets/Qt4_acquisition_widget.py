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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_widget_utils import DataModelInputBinder
from BlissFramework.Utils import Qt4_widget_colors


MAD_ENERGY_COMBO_NAMES = {'ip': 0, 'pk': 1, 'rm1': 2, 'rm2': 3}


class AcquisitionWidget(QtGui.QWidget):
    """
    Descript. :
    """
  
    acqParametersChangedSignal = QtCore.pyqtSignal()

    def __init__(self, parent = None, name = None, fl = 0, acq_params = None,
                 path_template = None, layout = 'horizontal'):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        
        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None

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
            self.acq_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                "ui_files/Qt4_acquisition_widget_horizontal_layout.ui"))
        else:
            self.acq_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                "ui_files/Qt4_acquisition_widget_vertical_layout.ui"))
        # Layout --------------------------------------------------------------
        __main_vlayout = QtGui.QVBoxLayout(self)
        __main_vlayout.addWidget(self.acq_widget)
        __main_vlayout.setSpacing(0)
        __main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.acq_widget.energies_combo.activated.connect(self.energy_selected)
        self.acq_widget.mad_cbox.toggled.connect(self.use_mad)
        self.acq_widget.inverse_beam_cbx.toggled.connect(self.set_use_inverse_beam)
        self.acq_widget.first_image_ledit.textChanged.connect(self.first_image_ledit_change)
        self.acq_widget.num_images_ledit.textChanged.connect(self.num_images_ledit_change)

        overlap_ledit = self.acq_widget.findChild(QtGui.QLineEdit, "overlap_ledit")
        if overlap_ledit is not None:
            overlap_ledit.textChanged.connect(self.overlap_changed)

        self.acq_widget.subwedge_size_ledit.textChanged.connect(self.subwedge_size_ledit_change)

        # Other --------------------------------------------------------------- 
        self.acq_widget.subwedge_size_ledit.setDisabled(True)
        self.acq_widget.energies_combo.setDisabled(True)
        self.acq_widget.energies_combo.addItems(['ip: -', 'pk: -', 'rm1: -', 'rm2: -'])

        self.osc_start_validator = QtGui.QDoubleValidator(-10000, 10000, 4, self)
        self.osc_range_validator = QtGui.QDoubleValidator(-10000, 10000, 4, self)
        self.kappa_validator = QtGui.QDoubleValidator(0, 360, 4, self)
        self.kappa_phi_validator = QtGui.QDoubleValidator(0, 360, 4, self)
        self.energy_validator = QtGui.QDoubleValidator(0, 25, 4, self)
        self.resolution_validator = QtGui.QDoubleValidator(0, 15, 3, self)
        self.transmission_validator = QtGui.QDoubleValidator(0, 100, 3, self)
        self.exp_time_validator = QtGui.QDoubleValidator(0.0001, 10000, 4, self)
        self.first_img_validator = QtGui.QIntValidator(0, 99999, self)
        self.num_img_validator = QtGui.QIntValidator(1, 99999, self) 
        self.disable_inverse_beam(True)

    def update_osc_start(self, new_value):
        """
        Descript. :
        """
        osc_start_value = 0
        try:
           osc_start_value = round(float(new_value), 2)
        except TypeError:
           pass
        self.acq_widget.osc_start_ledit.setText("%.2f" % osc_start_value)
        self._acquisition_parameters.osc_start = osc_start_value

    def update_kappa(self, new_value):
        self.acq_widget.kappa_ledit.setText("%.2f" % float(new_value))
        #self._acquisition_parameters.kappa = float(new_value)

    def update_kappa_phi(self, new_value):
        self.acq_widget.kappa_phi_ledit.setText("%.2f" % float(new_value))
        #self._acquisition_parameters.kappa_phi = float(new_value)

    def use_osc_start(self, state):
        self.acq_widget.osc_start_ledit.setEnabled(state)

    def use_kappa(self, state):
        if self._beamline_setup_hwobj.diffractometer_hwobj.in_plate_mode():
            state = False
        self.acq_widget.kappa_ledit.setEnabled(state)

    def use_kappa_phi(self, state):
        if self._beamline_setup_hwobj.diffractometer_hwobj.in_plate_mode():
            state = False
        self.acq_widget.kappa_phi_ledit.setEnabled(state)
            
    def set_beamline_setup(self, beamline_setup):
        """
        Descript. :
        """
        self._beamline_setup_hwobj = beamline_setup
        limits_dict = self._beamline_setup_hwobj.get_acquisition_limit_values()

        if 'osc_range' in limits_dict:
            limits = tuple(map(float, limits_dict['osc_range'].split(',')))
            (lower, upper) = limits
            self.osc_start_validator.setRange(lower, upper, 4)
            self.osc_range_validator.setRange(lower, upper, 4)

        self._acquisition_mib.bind_value_update('osc_start', 
                                                self.acq_widget.osc_start_ledit,
                                                float, 
                                                self.osc_start_validator)

        self._acquisition_mib.bind_value_update('osc_range', 
                                                self.acq_widget.osc_range_ledit,
                                                float, 
                                                self.osc_range_validator)

        if self.acq_widget.findChild(QtGui.QLineEdit, "kappa_ledit"):
            if 'kappa' in limits_dict:
                limits = tuple(map(float, limits_dict['kappa'].split(',')))
                (lower, upper) = limits
                self.kappa_validator.setRange(lower, upper, 4)
            self._acquisition_mib.bind_value_update('kappa', 
                 self.acq_widget.kappa_ledit, float, self.kappa_validator)

        if self.acq_widget.findChild(QtGui.QLineEdit, "kappa_phi_ledit"):
            if 'kappa_phi' in limits_dict:
                limits = tuple(map(float, limits_dict['kappa_phi'].split(',')))
                (lower, upper) = limits
                self.kappa_phi_validator.setRange(lower, upper, 4)
            self._acquisition_mib.bind_value_update('kappa_phi',     
                 self.acq_widget.kappa_phi_ledit, float, self.kappa_phi_validator)

        if 'exposure_time' in limits_dict:
            limits = tuple(map(float, limits_dict['exposure_time'].split(',')))
            (lower, upper) = limits
            self.exp_time_valdidator.setRange(lower, upper, 5)
        
        self._acquisition_mib.bind_value_update('exp_time', 
                                                self.acq_widget.exp_time_ledit,
                                                float, 
                                                self.exp_time_validator)

        if 'number_of_images' in limits_dict:
            limits = tuple(map(int, limits_dict['number_of_images'].split(',')))
            (lower, upper) = limits
            self.num_img_valdidator.setRange(lower, upper)
            self.first_img_valdidator.setRange(lower, upper)
        
        self._acquisition_mib.bind_value_update('first_image', 
                                                self.acq_widget.first_image_ledit,
                                                int, 
                                                self.first_img_validator)

        self._acquisition_mib.bind_value_update('num_images', 
                                                self.acq_widget.num_images_ledit,
                                                int, 
                                                self.num_img_validator)

        num_passes = self.acq_widget.findChild(QtGui.QLineEdit, "num_passes_ledit")

        if num_passes:
            self._acquisition_mib.\
                bind_value_update('num_passes', num_passes, int,
                                  QtGui.QIntValidator(1, 1000, self))

        overlap_ledit = self.acq_widget.findChild(QtGui.QLineEdit, "overlap_ledit")

        if overlap_ledit:
            self._acquisition_mib.\
                bind_value_update('overlap', overlap_ledit, float,
                                  QtGui.QDoubleValidator(-1000, 1000, 2, self))

        self._acquisition_mib.\
             bind_value_update('energy',
                               self.acq_widget.energy_ledit,
                               float,
                               self.energy_validator)

        self._acquisition_mib.\
             bind_value_update('transmission',
                               self.acq_widget.transmission_ledit,
                               float,
                               self.transmission_validator)

        self._acquisition_mib.\
             bind_value_update('resolution',
                               self.acq_widget.resolution_ledit,
                               float,
                               self.resolution_validator)

        self._acquisition_mib.\
             bind_value_update('inverse_beam',
                               self.acq_widget.inverse_beam_cbx,
                               bool,
                               None)

        self._acquisition_mib.\
             bind_value_update('shutterless',
                               self.acq_widget.shutterless_cbx,
                               bool,
                               None)

        """self.acq_widget.osc_start_ledit.setToolTip(\
               "Oscillation start limits %0.2f : %0.2f" %(\
               self.osc_start_validator.bottom(),
               self.osc_start_validator.top()))

        self.acq_widget.osc_range_ledit.setToolTip(\
               "Oscillation range limits %0.2f : %0.2f" %(\
               self.osc_ra_validator.bottom(),
               self.osc_start_validator.top()))""" 

        self.set_tunable_energy(beamline_setup.tunable_wavelength())

        has_shutter_less = self._beamline_setup_hwobj.detector_has_shutterless()
        self.acq_widget.shutterless_cbx.setEnabled(has_shutter_less)
        self.acq_widget.shutterless_cbx.setChecked(has_shutter_less)

        if self._beamline_setup_hwobj.disable_num_passes():
            num_passes = self.acq_widget.findChild(QtGui.QLineEdit, "num_passes_ledit")
            if num_passes:
                num_passes.setDisabled(True)

    def first_image_ledit_change(self, new_value):
        """
        Descript. :
        """
        if str(new_value).isdigit():
            self._path_template.start_num = int(new_value)
            widget = self.acq_widget.first_image_ledit
            self.acqParametersChangedSignal.emit()

    def num_images_ledit_change(self, new_value):
        """
        Descript. :
        """
        if str(new_value).isdigit():
            self._path_template.num_files = int(new_value)
            widget = self.acq_widget.num_images_ledit
            self.acqParametersChangedSignal.emit()

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
                self.acq_widget.shutterless_cbx.setEnabled(False)
                self.acq_widget.shutterless_cbx.setChecked(False)
                self._acquisition_parameters.shutterless = False
            else:
                self.acq_widget.shutterless_cbx.setEnabled(True)
                self.acq_widget.shutterless_cbx.setChecked(True)
                self._acquisition_parameters.shutterless = True

    def use_mad(self, state):
        """
        Descript. :
        """
        self.acq_widget.energies_combo.setEnabled(state)
        if state:
            (name, energy) = self.get_mad_energy()

            if energy != 0:
                self.set_energy(energy, 0)

            self.emit(QtCore.SIGNAL('mad_energy_selected'),
                      name, energy, state)
        else:
            self.set_energy(self.previous_energy, 0)
            energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
            self.emit(QtCore.SIGNAL('mad_energy_selected'),
                      '', self.previous_energy, state)

    def set_use_inverse_beam(self, state):
        """
        Descript. :
        """
        if state:
            self.acq_widget.subwedge_size_ledit.setEnabled(True)
        else:
            self.acq_widget.subwedge_size_ledit.setDisabled(True)

    def use_inverse_beam(self):
        """
        Descript. :
        """
        return self.acq_widget.inverse_beam_cbx.checkState == QtCore.Qt.Checked

    def get_num_subwedges(self):
        """
        Descript. :
        """
        return int(self.acq_widget.subwedge_size_ledit.text())

    def subwedge_size_ledit_change(self, new_value):
        """
        Descript. :
        """
        if int(new_value) > self._acquisition_parameters.num_images:
            Qt4_widget_colors.set_widget_color(\
                 self.acq_widget.subwedge_size_ledit,
                 Qt4_widget_colors.LIGHT_RED)
        else:
            Qt4_widget_colors.set_widget_color(
                 self.acq_widget.subwedge_size_ledit,
                 Qt4_widget_colors.WHITE)

    def get_mad_energy(self):
        """
        Descript. :
        """
        energy_str = str(self.acq_widget.energies_combo.currentText())
        (name, value) = energy_str.split(':')
        
        name = name.strip()
        value = value.strip()
        value = 0 if (value == '-') else value

        return (name, value)

    def set_energies(self, energy_scan_result):
        """
        Descript. :
        """
        self.acq_widget.energies_combo.clear()

        inflection = ('ip: %.4f' % energy_scan_result.inflection) if \
                     energy_scan_result.inflection else 'ip: -'

        peak = ('pk: %.4f' % energy_scan_result.peak) if \
               energy_scan_result.peak else 'pk: -'

        first_remote = ('rm1: %.4f' % energy_scan_result.first_remote) if \
                       energy_scan_result.first_remote else 'rm1: -'

        second_remote = ('rm2: %.4f' % energy_scan_result.second_remote) if \
                        energy_scan_result.second_remote else 'rm2: -'

        self.acq_widget.energies_combo.\
             addItems([inflection, peak, first_remote, second_remote])

    def energy_selected(self, index):
        """
        Descript. :
        """
        if self.acq_widget.mad_cbox.isChecked():
            (name, energy) = self.get_mad_energy()
            if energy != 0:
                self.set_energy(energy, 0)

            self.emit(QtCore.SIGNAL('madEnergySelected'), name, energy, True)

    def set_energy(self, energy, wav):
        """
        Descript. :
        """
        self.acq_widget.energy_ledit.setText("%.4f" % float(energy))

    def update_transmission(self, transmission):
        """
        Descript. :
        """
        self.acq_widget.transmission_ledit.setText("%.2f" % float(transmission))

    def update_resolution(self, resolution):
        """
        Descript. :
        """
        self.acq_widget.resolution_ledit.setText("%.3f" % float(resolution))

    def update_energy_limits(self, limits):
        if limits:
            self.energy_validator.setBottom(limits[0])
            self.energy_validator.setTop(limits[1])
            self.acq_widget.energy_ledit.setToolTip(\
               "Energy limits %0.3f : %0.3f" %(limits[0], limits[1]))
            self._acquisition_mib.validate_all()

    def update_transmission_limits(self, limits):
        if limits:
            self.transmission_validator.setBottom(limits[0])
            self.transmission_validator.setTop(limits[1])
            self.acq_widget.transmission_ledit.setToolTip(\
               "Transmission limits %0.3f : %0.3f" %(limits[0], limits[1]))
            self._acquisition_mib.validate_all()

    def update_resolution_limits(self, limits):
        if limits:
            self.resolution_validator.setBottom(limits[0])
            self.resolution_validator.setTop(limits[1])
            self.acq_widget.resolution_ledit.setToolTip(
               "Resolution limits %0.3f : %0.3f" %(limits[0], limits[1]))
            self._acquisition_mib.validate_all()

    def update_detector_exp_time_limits(self, limits):
        if limits:
            self.exp_time_validator.setRange(limits[0], limits[1], 4)
            self.acq_widget.exp_time_ledit.setToolTip(
               "Exposure time limits %0.3f : %0.3f" %(limits[0], limits[1]))
            self._acquisition_mib.validate_all()

    def update_osc_range_limits(self, exp_time):
        osc_range = 40.0 * exp_time
        self.osc_range_validator.setRange(0, osc_range, 4)
        self.acq_widget.osc_range_ledit.setToolTip(
              "Oscillation range limits %0.2f : %0.2f" %(0, osc_range))
        self._acquisition_mib.validate_all()

    def update_num_image_limits(self):
        try:
           osc_start = float(self.acq_widget.osc_start_ledit.text())
           osc_range = float(self.acq_widget.osc_range_ledit.text())
        except ValueError:
           return

        if osc_range == 0:
            return
        if self._beamline_setup.diffractometer_hwobj.in_plate_mode():
            num_image_limit = int((self.osc_start_validator.top() - osc_start) / osc_range)
        else:
            num_image_limit = 99999

        self.num_img_validator.setTop(num_image_limit)
        qt.QToolTip.add(self.acq_widgetnum_images_ledit,
              "Number of frames limit : %d" % num_image_limit)
        self._acquisition_mib.validate_all()

    def init_detector_modes(self):
        if self._beamline_setup_hwobj is not None:
            modes_list = self._beamline_setup_hwobj.detector_hwobj.get_roi_modes()
            if (len(modes_list) > 0 and
                self.acq_widget_layout.detector_mode_combo.count() == 0):
                self.acq_widget_layout.detector_mode_combo.\
                     insertStrList(modes_list)
            else:
                self.acq_widget_layout.detector_mode_combo.\
                     setDisabled(True)

    def update_detector_mode(self, detector_mode):
        if self.acq_widget.detector_mode_combo.count() > 0:
            self.acq_widgetdetector_mode_combo.\
                 setCurrentItem(detector_mode)

    def detector_mode_changed(self, detector_mode):
        if self._beamline_setup_hwobj is not None:
            self._beamline_setup_hwobj.detector_hwobj.set_roi_mode(detector_mode)

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
            self.acq_widget.energies_combo.setCurrentIndex(index)
            self.acq_widget.mad_cbox.setChecked(True)
            self.acq_widget.energies_combo.setEnabled(True)
        else:
            self.acq_widget.mad_cbox.setChecked(False)
            self.acq_widget.energies_combo.setEnabled(False)
            self.acq_widget.energies_combo.setCurrentIndex(0)

    def set_tunable_energy(self, state):
        """
        Descript. :
        """
        self.acq_widget.energy_ledit.setEnabled(state)
        self.acq_widget.mad_cbox.setEnabled(state)
        self.acq_widget.energies_combo.setEnabled(state)

    def disable_inverse_beam(self, state):
        """
        Descript. :
        """
        self.acq_widget.inverse_beam_cbx.setDisabled(state)
        self.acq_widget.subwedge_size_label.setDisabled(state)
        self.acq_widget.subwedge_size_ledit.setDisabled(state)

    def hide_aperture(self, state):
        """
        Descript. :
        """
        pass
        #if state:
        #    self.acq_widget.findChild('aperture_ledit').show()
        #    self.acq_widget.findChild('aperture_cbox').show()
        #else:
        #    self.acq_widget.findChild('aperture_ledit').hide()
        #    self.acq_widget.findChild('aperture_cbox').hide()
