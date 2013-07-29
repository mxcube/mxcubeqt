import qt
import queue_model_objects_v1 as queue_model_objects


from widgets.acquisition_widget_vertical_layout \
    import AcquisitionWidgetVerticalLayout
from widgets.acquisition_widget_horizontal_layout \
    import AcquisitionWidgetHorizontalLayout
from widgets.widget_utils import DataModelInputBinder


MAD_ENERGY_COMBO_NAMES = {'ip':0, 'pk':1, 'rm1':2, 'rm2':3}


class AcquisitionWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, acq_params = None,
                 path_template = None, layout = None):      
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        self._bl_config = None

        if acq_params is None:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
        else:
            self._acquisition_parameters = acq_params

        if path_template is None:
            self._path_template = queue_model_objects.PathTemplate()
        else:
            self._path_template = path_template

        self._acquisition_mib = DataModelInputBinder(self._acquisition_parameters)
        #self._path_template_mib = DataModelInputBinder(self._path_template)

        #   
        # Layout
        #
        h_layout = qt.QHBoxLayout(self)
        
        if layout:
            self.acq_widget_layout = layout(self)
        else:
            self.acq_widget_layout = AcquisitionWidgetHorizontalLayout(self)

        h_layout.addWidget(self.acq_widget_layout)


        #
        # Logic
        #
        self._acquisition_mib.bind_value_update('osc_start', 
                                                self.acq_widget_layout.osc_start_ledit,
                                                float,
                                                qt.QDoubleValidator(0, 1000, 2, self))
        
        self._acquisition_mib.bind_value_update('first_image', 
                                                self.acq_widget_layout.first_image_ledit,
                                                int,
                                                qt.QIntValidator(1, 10000, self))

        self._acquisition_mib.bind_value_update('exp_time', 
                                                self.acq_widget_layout.exp_time_ledit,
                                                float,
                                                qt.QDoubleValidator(0.001, 6000, 3, self))

        self._acquisition_mib.bind_value_update('osc_range', 
                                                self.acq_widget_layout.osc_range_ledit,
                                                float,
                                                qt.QDoubleValidator(0.001, 1000, 2, self))

        self._acquisition_mib.bind_value_update('num_images', 
                                                self.acq_widget_layout.num_images_ledit,
                                                int,
                                                qt.QIntValidator(1, 10000, self))
        
        self._acquisition_mib.bind_value_update('num_passes', 
                                                self.acq_widget_layout.num_passes_ledit,
                                                int,
                                                qt.QIntValidator(1, 1000, self))
        
        self._acquisition_mib.bind_value_update('overlap', 
                                                self.acq_widget_layout.overlap_ledit,
                                                float,
                                                qt.QDoubleValidator(-1000, 1000, 2, self))

        self._acquisition_mib.bind_value_update('energy',
                                                self.acq_widget_layout.energy_ledit,
                                                float,
                                                qt.QDoubleValidator(0, 1000, 4 , self))

        self._acquisition_mib.bind_value_update('transmission',
                                                self.acq_widget_layout.transmission_ledit,
                                                float,
                                                qt.QDoubleValidator(0, 1000, 2, self))

        self._acquisition_mib.bind_value_update('resolution',
                                                self.acq_widget_layout.resolution_ledit,
                                                float,
                                                qt.QDoubleValidator(0, 1000, 4, self))

        self._acquisition_mib.bind_value_update('inverse_beam', 
                                                self.acq_widget_layout.inverse_beam_cbx,
                                                bool,
                                                None)

        self._acquisition_mib.bind_value_update('shutterless', 
                                                self.acq_widget_layout.shutterless_cbx,
                                                bool,
                                                None)

        qt.QObject.connect(self.acq_widget_layout.energies_combo,
                        qt.SIGNAL("activated(int)"),
                        self.energy_selected)

        qt.QObject.connect(self.acq_widget_layout.mad_cbox,
                        qt.SIGNAL("toggled(bool)"),
                        self.use_mad)

        qt.QObject.connect(self.acq_widget_layout.first_image_ledit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.first_image_ledit_change)
        
        qt.QObject.connect(self.acq_widget_layout.num_images_ledit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.num_images_ledit_change)

        qt.QObject.connect(self.acq_widget_layout.overlap_ledit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.overlap_changed)


    def set_bl_config(self, bl_config):
        self._bl_config = bl_config

        te = bl_config.tunable_wavelength()
        self.set_tunable_energy(te)

        has_shutter_less = self._bl_config.detector_has_shutterless()
        self.acq_widget_layout.shutterless_cbx.setEnabled(has_shutter_less)
        self.acq_widget_layout.shutterless_cbx.setOn(has_shutter_less)

        if self._bl_config.disable_num_passes():
            self.acq_widget_layout.num_passes_ledit.setDisabled(True)


    def first_image_ledit_change(self, new_value):
        self._path_template.start_num = int(new_value)


    def num_images_ledit_change(self, new_value):
        self._path_template.num_files = int(new_value)


    def overlap_changed(self, new_value):
        has_shutter_less = self._bl_config.detector_has_shutterless()

        if has_shutter_less:
            try:
                new_value = float(new_value)
            except ValueError:
                pass
            
            if new_value != 0:
                self.acq_widget_layout.shutterless_cbx.setEnabled(False)
                self.acq_widget_layout.shutterless_cbx.setOn(False)
                self._acquisition_parameters.shutterless = False
            else:         
                self.acq_widget_layout.shutterless_cbx.setEnabled(True)
                self.acq_widget_layout.shutterless_cbx.setOn(True)
                self._acquisition_parameters.shutterless = True


    def use_mad(self, state):
        if state:    
            self.previous_energy = self._acquisition_parameters.energy
            (name, energy) = self.get_mad_energy()
            self.set_energy(energy, 0)
            self.emit(qt.PYSIGNAL('mad_energy_selected'),
                      (name, energy, state))
        else:
            self.set_energy(self.previous_energy, 0)
            self.emit(qt.PYSIGNAL('mad_energy_selected'),
                      ('', self.previous_energy, state))


    def get_mad_energy(self):
        energy_str = str(self.acq_widget_layout.energies_combo.currentText())
        (name, value) = energy_str.split('-')
        name = name.strip()
        value = value.strip()
        
        return (name, value)


    def set_energies(self, energy_scan_result):
        self.acq_widget_layout.energies_combo.clear()
        self.acq_widget_layout.energies_combo.\
            insertStrList(['ip - %.4f' % energy_scan_result.inflection , 
                           'pk - %.4f' % energy_scan_result.peak,
                           'rm1 - %.4f' % energy_scan_result.first_remote, 
                           'rm2 - %.4f' % energy_scan_result.second_remote])

        #if self._path_template.mad_prefix:
        #    self.acq_widget_layout.mad_cbox.setOn(True)
        #    self.acq_widget_layout.energies_combo.\
        #        setCurrentItem(MAD_ENERGY_COMBO_NAMES[self._path_template.mad_prefix])


    def energy_selected(self, index):
        if self.acq_widget_layout.mad_cbox.isChecked():
            (name, energy) = self.get_mad_energy()
            self.set_energy(energy, 0)
            self.emit(qt.PYSIGNAL('mad_energy_selected'), (name, energy, True))


    def set_energy(self, energy, wav):
        energy = round(float(energy), 4)
        self._acquisition_parameters.energy = energy
        self.acq_widget_layout.energy_ledit.setText("%.4f" % energy)

    
    def update_transmission(self, transmission):
        transmission = round(float(transmission), 1)
        self.acq_widget_layout.transmission_ledit.setText(str(transmission))
        self._acquisition_parameters.transmission = float(transmission)


    def update_resolution(self, resolution):
        resolution = round(float(resolution), 4)
        self.acq_widget_layout.resolution_ledit.setText(str(resolution))
        self._acquisition_parameters.resolution = float(resolution)


    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._acquisition_mib.set_model(acquisition_parameters)
        self._path_template = path_template
        #self._path_template_mib.set_model(path_template)


    def set_tunable_energy(self, state):
        self.acq_widget_layout.energy_ledit.setEnabled(state)
        self.acq_widget_layout.mad_cbox.setEnabled(state)
        self.acq_widget_layout.energies_combo.setEnabled(state)
    
