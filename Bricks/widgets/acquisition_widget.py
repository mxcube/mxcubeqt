import os
import qt
import qtui
import queue_model_objects_v1 as queue_model_objects


from widgets.acquisition_widget_vertical_layout \
    import AcquisitionWidgetVerticalLayout
from widgets.acquisition_widget_horizontal_layout \
    import AcquisitionWidgetHorizontalLayout
from widgets.widget_utils import DataModelInputBinder
from BlissFramework.Utils import widget_colors


MAD_ENERGY_COMBO_NAMES = {'ip':0, 'pk':1, 'rm1':2, 'rm2':3}


class AcquisitionWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, acq_params = None,
                 path_template = None, layout = 'horizontal'):      
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        self._beamline_setup = None

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
        
        if layout == 'vertical':
            widget = self.acq_widget_layout = qtui.QWidgetFactory.\
                     create(os.path.join(os.path.dirname(__file__),
                                         'ui_files/acquisition_widget_vertical_layout.ui'))
        elif layout == 'horizontal':
            widget = qtui.QWidgetFactory.\
                     create(os.path.join(os.path.dirname(__file__),
                                         'ui_files/acquisition_widget_horizontal_layout.ui'))

            widget.child('inverse_beam_cbx').hide()
            widget.child('subwedge_size_label').hide()
            widget.child('subwedge_size_ledit').hide()
        else:
            widget = qtui.QWidgetFactory.\
                     create(os.path.join(os.path.dirname(__file__),
                                         'ui_files/acquisition_widget_vertical_layout.ui'))

        widget.reparent(self, qt.QPoint(0,0))
        self.acq_widget_layout = widget
            
        h_layout.addWidget(self.acq_widget_layout)

        #
        # Logic
        #
        self._acquisition_mib.bind_value_update('osc_start', 
                                                self.acq_widget_layout.child('osc_start_ledit'),
                                                float,
                                                qt.QDoubleValidator(0, 1000, 2, self))
        
        self._acquisition_mib.bind_value_update('first_image', 
                                                self.acq_widget_layout.child('first_image_ledit'),
                                                int,
                                                qt.QIntValidator(1, 10000, self))

        self._acquisition_mib.bind_value_update('exp_time', 
                                                self.acq_widget_layout.child('exp_time_ledit'),
                                                float,
                                                qt.QDoubleValidator(0.001, 6000, 3, self))

        self._acquisition_mib.bind_value_update('osc_range', 
                                                self.acq_widget_layout.child('osc_range_ledit'),
                                                float,
                                                qt.QDoubleValidator(0.001, 1000, 2, self))

        self._acquisition_mib.bind_value_update('num_images', 
                                                self.acq_widget_layout.child('num_images_ledit'),
                                                int,
                                                qt.QIntValidator(1, 10000, self))
        
        self._acquisition_mib.bind_value_update('num_passes', 
                                                self.acq_widget_layout.child('num_passes_ledit'),
                                                int,
                                                qt.QIntValidator(1, 1000, self))
        
        self._acquisition_mib.bind_value_update('overlap', 
                                                self.acq_widget_layout.child('overlap_ledit'),
                                                float,
                                                qt.QDoubleValidator(-1000, 1000, 2, self))

        self._acquisition_mib.bind_value_update('energy',
                                                self.acq_widget_layout.child('energy_ledit'),
                                                float,
                                                qt.QDoubleValidator(0, 1000, 4 , self))

        self._acquisition_mib.bind_value_update('transmission',
                                                self.acq_widget_layout.child('transmission_ledit'),
                                                float,
                                                qt.QDoubleValidator(0, 1000, 2, self))

        self._acquisition_mib.bind_value_update('resolution',
                                                self.acq_widget_layout.child('resolution_ledit'),
                                                float,
                                                qt.QDoubleValidator(0, 1000, 4, self))

        self._acquisition_mib.bind_value_update('inverse_beam', 
                                                self.acq_widget_layout.child('inverse_beam_cbx'),
                                                bool,
                                                None)

        self._acquisition_mib.bind_value_update('shutterless', 
                                                self.acq_widget_layout.child('shutterless_cbx'),
                                                bool,
                                                None)

        qt.QObject.connect(self.acq_widget_layout.child('energies_combo'),
                        qt.SIGNAL("activated(int)"),
                        self.energy_selected)

        qt.QObject.connect(self.acq_widget_layout.child('mad_cbox'),
                        qt.SIGNAL("toggled(bool)"),
                        self.use_mad)

        qt.QObject.connect(self.acq_widget_layout.child('inverse_beam_cbx'),
                           qt.SIGNAL("toggled(bool)"),
                           self.set_use_inverse_beam)

        qt.QObject.connect(self.acq_widget_layout.child('first_image_ledit'),
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.first_image_ledit_change)
        
        qt.QObject.connect(self.acq_widget_layout.child('num_images_ledit'),
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.num_images_ledit_change)

        qt.QObject.connect(self.acq_widget_layout.child('overlap_ledit'),
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.overlap_changed)

        qt.QObject.connect(self.acq_widget_layout.child('subwedge_size_ledit'),
                           qt.SIGNAL("textChanged(const QString &)"),
                           self.subwedge_size_ledit_change)

        self.acq_widget_layout.child('subwedge_size_ledit').setDisabled(True)


    def set_beamline_setup(self, beamline_setup):
        self._beamline_setup = beamline_setup

        te = beamline_setup.tunable_wavelength()
        self.set_tunable_energy(te)

        has_shutter_less = self._beamline_setup.detector_has_shutterless()
        self.acq_widget_layout.child('shutterless_cbx').setEnabled(has_shutter_less)
        self.acq_widget_layout.child('shutterless_cbx').setOn(has_shutter_less)

        if self._beamline_setup.disable_num_passes():
            self.acq_widget_layout.child('num_passes_ledit').setDisabled(True)


    def first_image_ledit_change(self, new_value):
        self._path_template.start_num = int(new_value)


    def num_images_ledit_change(self, new_value):
        self._path_template.num_files = int(new_value)


    def overlap_changed(self, new_value):
        has_shutter_less = self._beamline_setup.detector_has_shutterless()

        if has_shutter_less:
            try:
                new_value = float(new_value)
            except ValueError:
                pass
            
            if new_value != 0:
                self.acq_widget_layout.child('shutterless_cbx').setEnabled(False)
                self.acq_widget_layout.child('shutterless_cbx').setOn(False)
                self._acquisition_parameters.shutterless = False
            else:         
                self.acq_widget_layout.child('shutterless_cbx').setEnabled(True)
                self.acq_widget_layout.child('shutterless_cbx').setOn(True)
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


    def set_use_inverse_beam(self, state):
        if state:
            self.acq_widget_layout.child('subwedge_size_ledit').setEnabled(True)
        else:
            self.acq_widget_layout.child('subwedge_size_ledit').setDisabled(True)


    def use_inverse_beam(self):
        return self.acq_widget_layout.child('inverse_beam_cbx').isOn()


    def get_num_subwedges(self):
        return int(self.acq_widget_layout.child('subwedge_size_ledit').text())


    def subwedge_size_ledit_change(self, new_value):
        widget = self.acq_widget_layout.child('subwedge_size_ledit')
        
        if int(new_value) > self._acquisition_parameters.num_images:
            widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
        else:
            widget.setPaletteBackgroundColor(widget_colors.WHITE)
            

    def get_mad_energy(self):
        energy_str = str(self.acq_widget_layout.child('energies_combo').currentText())
        (name, value) = energy_str.split('-')
        name = name.strip()
        value = value.strip()
        
        return (name, value)


    def set_energies(self, energy_scan_result):
        self.acq_widget_layout.child('energies_combo').clear()
        self.acq_widget_layout.child('energies_combo').\
            insertStrList(['ip - %.4f' % energy_scan_result.inflection , 
                           'pk - %.4f' % energy_scan_result.peak,
                           'rm1 - %.4f' % energy_scan_result.first_remote, 
                           'rm2 - %.4f' % energy_scan_result.second_remote])


    def energy_selected(self, index):
        if self.acq_widget_layout.child('mad_cbox').isChecked():
            (name, energy) = self.get_mad_energy()
            self.set_energy(energy, 0)
            self.emit(qt.PYSIGNAL('mad_energy_selected'), (name, energy, True))


    def set_energy(self, energy, wav):
        energy = round(float(energy), 4)
        self._acquisition_parameters.energy = energy
        self.acq_widget_layout.child('energy_ledit').setText("%.4f" % energy)

    
    def update_transmission(self, transmission):
        transmission = round(float(transmission), 1)
        self.acq_widget_layout.child('transmission_ledit').setText(str(transmission))
        self._acquisition_parameters.transmission = float(transmission)


    def update_resolution(self, resolution):
        resolution = round(float(resolution), 4)
        self.acq_widget_layout.child('resolution_ledit').setText(str(resolution))
        self._acquisition_parameters.resolution = float(resolution)


    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._path_template = path_template
        self._acquisition_mib.set_model(acquisition_parameters)
        #self._path_template_mib.set_model(path_template)


    def set_tunable_energy(self, state):
        self.acq_widget_layout.child('energy_ledit').setEnabled(state)
        self.acq_widget_layout.child('mad_cbox').setEnabled(state)
        self.acq_widget_layout.child('energies_combo').setEnabled(state)
    
