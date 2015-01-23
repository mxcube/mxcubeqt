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
    def __init__(self, parent=None, name=None, fl=0, acq_params=None,
                 path_template=None, layout='horizontal'):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        self._beamline_setup = None
        self.previous_energy = 0

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
            self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx').hide()
            self.acq_widget.findChild(QtGui.QLabel, 'subwedge_size_label').hide()
            self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').hide()
        else:
            self.acq_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                                "ui_files/Qt4_acquisition_widget_vertical_layout.ui"))

        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.acq_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.connect(self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo'),
                     QtCore.SIGNAL("activated(int)"), self.energy_selected)

        self.connect(self.acq_widget.findChild(QtGui.QCheckBox, 'mad_cbox'),
                     QtCore.SIGNAL("toggled(bool)"), self.use_mad)

        self.connect(self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx'),
                     QtCore.SIGNAL("toggled(bool)"), self.set_use_inverse_beam)

        self.connect(self.acq_widget.findChild(QtGui.QLineEdit, 'first_image_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"), 
                     self.first_image_ledit_change)

        self.connect(self.acq_widget.findChild(QtGui.QLineEdit, 'num_images_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"),
                     self.num_images_ledit_change)

        overlap_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'overlap_ledit')
        
        if overlap_ledit:
            self.connect(self.acq_widget.findChild(QtGui.QLineEdit, 'overlap_ledit'),
                         QtCore.SIGNAL("textChanged(const QString &)"),
                         self.overlap_changed)

        self.connect(self.acq_widget.findChild(QtGui.QLineEdit,'subwedge_size_ledit'),
                     QtCore.SIGNAL("textChanged(const QString &)"),
                     self.subwedge_size_ledit_change)

        self.connect(self.acq_widget.findChild(QtGui.QCheckBox, 'osc_start_cbox'),
                     QtCore.SIGNAL("toggled(bool)"),
                     self.osc_start_cbox_click)

        self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').setDisabled(True)
        self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setDisabled(True)
        self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').\
            addItems(['ip: -', 'pk: -', 'rm1: -', 'rm2: -'])

        self.acq_widget.findChild(QtGui.QLineEdit, 'osc_start_ledit').setEnabled(False)

    def osc_start_cbox_click(self, state):
        self.update_osc_start(self._beamline_setup._get_omega_axis_position())
        self.acq_widget.findChild(QtGui.QLineEdit, 'osc_start_ledit').setEnabled(state)

    def update_osc_start(self, new_value):
        if not self.acq_widget.findChild(QtGui.QCheckBox, 'osc_start_cbox').isChecked():
            osc_start_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'osc_start_ledit')
            osc_start_value = 0

            try:
                osc_start_value = round(float(new_value),2)
            except TypeError:
                pass
            
            osc_start_ledit.setText("%.2f" % osc_start_value)
            self._acquisition_parameters.osc_start = osc_start_value

    def use_osc_start(self, state):
        self.acq_widget.findChild(QtGui.QCheckBox, 'osc_start_cbox').setChecked(state)
        self.acq_widget.findChild(QtGui.QCheckBox, 'osc_start_cbox').setDisabled(state)
            
    def set_beamline_setup(self, beamline_setup):
        self._beamline_setup = beamline_setup
        limits_dict = self._beamline_setup.get_acquisition_limit_values()

        if 'osc_range' in limits_dict:
            limits = tuple(map(float, limits_dict['osc_range'].split(',')))
            (lower, upper) = limits
            osc_start_validator = QtGui.QDoubleValidator(lower, upper, 4, self)
            osc_range_validator = QtGui.QDoubleValidator(lower, upper, 4, self)
        else:
            osc_start_validator = QtGui.QDoubleValidator(-10000, 10000, 4, self)
            osc_range_validator = QtGui.QDoubleValidator(-10000, 10000, 4, self)

        osc_start_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'osc_start_ledit')
        self._acquisition_mib.bind_value_update('osc_start', osc_start_ledit,
                                                float, osc_start_validator)

        osc_range_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'osc_range_ledit')
        self._acquisition_mib.bind_value_update('osc_range', osc_range_ledit,
                                                float, osc_range_validator)

        if 'exposure_time' in limits_dict:
            limits = tuple(map(float, limits_dict['exposure_time'].split(',')))
            (lower, upper) = limits
            exp_time_valdidator = QtGui.QDoubleValidator(lower, upper, 5, self)
        else:
            exp_time_valdidator = QtGui.QDoubleValidator(-0.003, 6000, 5, self)
        
        exp_time_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'exp_time_ledit')
        self._acquisition_mib.bind_value_update('exp_time', exp_time_ledit,
                                                float, exp_time_valdidator)

        if 'number_of_images' in limits_dict:
            limits = tuple(map(int, limits_dict['number_of_images'].split(',')))
            (lower, upper) = limits
            num_img_valdidator = QtGui.QIntValidator(lower, upper, self)
            first_img_valdidator = QtGui.QIntValidator(lower, upper, self)
        else:
            num_img_valdidator = QtGui.QIntValidator(1, 9999, self)
            first_img_valdidator = QtGui.QIntValidator(1, 9999, self)
        
        first_img_ledit =  self.acq_widget.findChild(QtGui.QLineEdit, 'first_image_ledit') 
        self._acquisition_mib.bind_value_update('first_image', first_img_ledit,
                                                int, first_img_valdidator)

        num_img_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'num_images_ledit')
        self._acquisition_mib.bind_value_update('num_images', num_img_ledit,
                                                int, num_img_valdidator)

        num_passes = self.acq_widget.findChild(QtGui.QLineEdit, 'num_passes_ledit')

        if num_passes:
            self._acquisition_mib.\
                bind_value_update('num_passes', num_passes, int,
                                  QtGui.QIntValidator(1, 1000, self))

        overlap_ledit = self.acq_widget.findChild(QtGui.QLineEdit, 'overlap_ledit')

        if overlap_ledit:
            self._acquisition_mib.\
                bind_value_update('overlap', overlap_ledit, float,
                                  QtGui.QDoubleValidator(-1000, 1000, 2, self))

        self._acquisition_mib.\
             bind_value_update('energy',
                               self.acq_widget.findChild(QtGui.QLineEdit, 'energy_ledit'),
                               float,
                               QtGui.QDoubleValidator(0, 1000, 4, self))

        self._acquisition_mib.\
             bind_value_update('transmission',
                            self.acq_widget.findChild(QtGui.QLineEdit, 'transmission_ledit'),
                            float,
                            QtGui.QDoubleValidator(0, 1000, 2, self))

        self._acquisition_mib.\
             bind_value_update('resolution',
                               self.acq_widget.findChild(QtGui.QLineEdit, 'resolution_ledit'),
                               float,
                               QtGui.QDoubleValidator(0, 1000, 3, self))

        self._acquisition_mib.\
             bind_value_update('inverse_beam',
                               self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx'),
                               bool,
                               None)

        self._acquisition_mib.\
             bind_value_update('shutterless',
                               self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx'),
                               bool,
                               None)

        te = beamline_setup.tunable_wavelength()
        self.set_tunable_energy(te)

        has_shutter_less = self._beamline_setup.detector_has_shutterless()
        self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').\
             setEnabled(has_shutter_less)
        self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').setChecked(has_shutter_less)

        if self._beamline_setup.disable_num_passes():
            num_passes = self.acq_widget.findChild(QtGui.QLineEdit, 'num_passes_ledit')
            if num_passes:
                self.acq_widget.findChild(QtGui.QLineEdit, 'num_passes_ledit').setDisabled(True)

    def first_image_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._path_template.start_num = int(new_value)
            widget = self.acq_widget.findChild(QtGui.QLineEdit, 'first_image_ledit')
            self.emit(QtCore.SIGNAL('path_template_changed'),
                      widget, new_value)

    def num_images_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self._path_template.num_files = int(new_value)
            widget = self.acq_widget.findChild(QtGui.QLineEdit, 'num_images_ledit')
            self.emit(QtCore.SIGNAL('path_template_changed'),
                      widget, new_value)

    def overlap_changed(self, new_value):
        if self._beamline_setup:
            has_shutter_less = self._beamline_setup.detector_has_shutterless()
        else:
            has_shutter_less = True

        if has_shutter_less:
            try:
                new_value = float(new_value)
            except ValueError:
                pass

            if new_value != 0:
                self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').\
                    setEnabled(False)
                self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').setChecked(False)
                self._acquisition_parameters.shutterless = False
            else:
                self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').setEnabled(True)
                self.acq_widget.findChild(QtGui.QCheckBox, 'shutterless_cbx').setChecked(True)
                self._acquisition_parameters.shutterless = True

    def use_mad(self, state):
        self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setEnabled(state)
        if state:
            (name, energy) = self.get_mad_energy()

            if energy != 0:
                self.set_energy(energy, 0)

            self.emit(QtCore.SIGNAL('mad_energy_selected'),
                      name, energy, state)
        else:
            self.set_energy(self.previous_energy, 0)
            energy = self._beamline_setup.energy_hwobj.getCurrentEnergy()
            self.emit(QtCore.SIGNAL('mad_energy_selected'),
                      '', self.previous_energy, state)

    def set_use_inverse_beam(self, state):
        if state:
            self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').setEnabled(True)
        else:
            self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').\
                 setDisabled(True)

    def use_inverse_beam(self):
        return self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx').checkState == QtCore.Qt.Checked

    def get_num_subwedges(self):
        return int(self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').text())

    def subwedge_size_ledit_change(self, new_value):
        widget = self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit')

        if int(new_value) > self._acquisition_parameters.num_images:
            Qt4_widget_colors.set_widget_color(widget, Qt4_widget_colors.LIGHT_RED)
        else:
            Qt4_widget_colors.set_widget_color(widget, Qt4_widget_colors.WHITE)

    def get_mad_energy(self):
        energy_str = str(self.acq_widget.\
                         findChild(QtGui.QComboBox, 'energies_combo').currentText())
        (name, value) = energy_str.split(':')
        
        name = name.strip()
        value = value.strip()
        value = 0 if (value == '-') else value

        return (name, value)

    def set_energies(self, energy_scan_result):
        self.acq_widget.findChild(QtGui.QComboBox,
                                  'energies_combo').clear()

        inflection = ('ip: %.4f' % energy_scan_result.inflection) if \
                     energy_scan_result.inflection else 'ip: -'

        peak = ('pk: %.4f' % energy_scan_result.peak) if \
               energy_scan_result.peak else 'pk: -'

        first_remote = ('rm1: %.4f' % energy_scan_result.first_remote) if \
                       energy_scan_result.first_remote else 'rm1: -'

        second_remote = ('rm2: %.4f' % energy_scan_result.second_remote) if \
                        energy_scan_result.second_remote else 'rm2: -'

        self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').\
             addItems([inflection, peak, first_remote, second_remote])

    def energy_selected(self, index):
        if self.acq_widget.findChild(QtGui.QCheckBox, 'mad_cbox').isChecked():
            (name, energy) = self.get_mad_energy()
            if energy != 0:
                self.set_energy(energy, 0)

            self.emit(QtCore.SIGNAL('mad_energy_selected'), name, energy, True)

    def set_energy(self, energy, wav):
        self._acquisition_parameters.energy = energy
        self.acq_widget.findChild(QtGui.QLineEdit, 'energy_ledit').\
             setText("%.4f" % float(energy))

    def update_transmission(self, transmission):
        self.acq_widget.findChild(QtGui.QLineEdit,'transmission_ledit').\
             setText("%.2f" % float(transmission))
        #self._acquisition_parameters.transmission = float(transmission)

    def update_resolution(self, resolution):
        self.acq_widget.findChild(QtGui.QLineEdit, 'resolution_ledit').\
             setText("%.3f" % float(resolution))
        #self._acquisition_parameters.resolution = float(resolution)

    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._path_template = path_template        
        self._acquisition_mib.set_model(acquisition_parameters)
        
        #Update mad widgets
        mad = True if self._path_template.mad_prefix != '' else False

        if mad:
            mad_prefix = self._path_template.mad_prefix
            index = MAD_ENERGY_COMBO_NAMES[mad_prefix]
            self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setCurrentIndex(index)
            self.acq_widget.findChild(QtGui.QCheckBox, 'mad_cbox').setChecked(True)
            self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setEnabled(True)
        else:
            self.acq_widget.findChild(QtGui.QCheckBox, 'mad_cbox').setChecked(False)
            self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setEnabled(False)
            self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setCurrentIndex(0)

    def set_tunable_energy(self, state):
        self.acq_widget.findChild(QtGui.QLineEdit, 'energy_ledit').setEnabled(state)
        self.acq_widget.findChild(QtGui.QCheckBox, 'mad_cbox').setEnabled(state)
        self.acq_widget.findChild(QtGui.QComboBox, 'energies_combo').setEnabled(state)

    def disable_inverse_beam(self, state):
        if state:
            self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx').hide()
            self.acq_widget.findChild(QtGui.QLabel, 'subwedge_size_label').hide()
            self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').hide()
        else:
            self.acq_widget.findChild(QtGui.QCheckBox, 'inverse_beam_cbx').show()
            self.acq_widget.findChild(QtGui.QLabel, 'subwedge_size_label').show()
            self.acq_widget.findChild(QtGui.QLineEdit, 'subwedge_size_ledit').show()

    def hide_aperture(self, state):
        pass
        #if state:
        #    self.acq_widget.findChild('aperture_ledit').show()
        #    self.acq_widget.findChild('aperture_cbox').show()
        #else:
        #    self.acq_widget.findChild('aperture_ledit').hide()
        #    self.acq_widget.findChild('aperture_cbox').hide()
