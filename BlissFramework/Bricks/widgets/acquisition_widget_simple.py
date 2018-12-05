import os
import qt
import qtui
import queue_model_objects

from widgets.widget_utils import DataModelInputBinder

class AcquisitionWidgetSimple(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, acq_params = None, 
                 path_template = None, layout = None):
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        if acq_params is None:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
        else:
            self._acquisition_parameters = acq_params


        if path_template is None:
            self._path_template = queue_model_objects.PathTemplate()
        else:
            self._path_template = path_template

        self._acquisition_mib = DataModelInputBinder(self._acquisition_parameters)

        #   
        # Layout
        #
        h_layout = qt.QHBoxLayout(self)

        current_dir = os.path.dirname(__file__)
        ui_file = 'ui_files/acquisition_widget_vertical_simple_layout.ui'
        widget = qtui.QWidgetFactory.create(os.path.join(current_dir, ui_file))
        widget.reparent(self, qt.QPoint(0,0))
        h_layout.addWidget(widget)

        self.acq_widget_layout = widget

        #
        # Logic
        #
        self.acq_widget_layout.child('kappa_ledit').setEnabled(False)
        self.acq_widget_layout.child('kappa_phi_ledit').setEnabled(False)
        self.acq_widget_layout.child('osc_start_ledit').setEnabled(False)

        # Default to 2-images
        self.acq_widget_layout.child('num_images_cbox').setCurrentItem(1)

        qt.QObject.connect(self.acq_widget_layout.child('num_images_cbox'),
                           qt.SIGNAL("activated(int)"),
                           self.update_num_images)

    def osc_start_cbox_click(self, state):
        self.update_osc_start(self._beamline_setup._get_omega_axis_position())
        self.acq_widget_layout.child('osc_start_ledit').setEnabled(state)

    def update_osc_start(self, new_value):
        if not self.acq_widget_layout.child('osc_start_cbox').isChecked():
            osc_start_ledit = self.acq_widget_layout.child('osc_start_ledit')
            osc_start_value = 0

            try:
                osc_start_value = round(float(new_value),2)
            except TypeError:
                pass
            
            osc_start_ledit.setText("%.2f" % osc_start_value)
            self._acquisition_parameters.osc_start = osc_start_value

    def update_kappa(self, new_value):
        self.acq_widget_layout.child('kappa_ledit').\
             setText("%.2f" % float(new_value))

    def update_kappa_phi(self, new_value):
        self.acq_widget_layout.child('kappa_phi_ledit').\
             setText("%.2f" % float(new_value))

    def use_kappa(self, state):
        self.acq_widget_layout.child('kappa_ledit').setDisabled(state)

    def use_kappa_phi(self, state):
        self.acq_widget_layout.child('kappa_phi_ledit').setDisabled(state)
    
    def update_num_images(self, index = None, num_images = None):
        if index is not None:
            if index is 0:
                self._acquisition_parameters.num_images = 1
                self._path_template.num_files = 1
            elif index is 1:
                self._acquisition_parameters.num_images = 2
                self._path_template.num_files = 2
            elif index is 2:
                self._acquisition_parameters.num_images = 4
                self._path_template.num_files = 4

        if num_images:
            if self.acq_widget_layout.child('num_images_cbox').count() > 3:
                self.acq_widget_layout.child('num_images_cbox').removeItem(4)
        
            if num_images is 1:
                self.acq_widget_layout.child('num_images_cbox').setCurrentItem(0)    
            elif num_images is 2:
                self.acq_widget_layout.child('num_images_cbox').setCurrentItem(1)
            elif num_images is 4:
                self.acq_widget_layout.child('num_images_cbox').setCurrentItem(2)
            else:
                self.acq_widget_layout.child('num_images_cbox').insertItem(str(num_images))
                self.acq_widget_layout.child('num_images_cbox').setCurrentItem(3)

            self._path_template.num_files = num_images

    def use_mad(self, state):
        pass

    def get_mad_energy(self):
        pass

    def set_energies(self, energy_scan_result):
        pass

    def energy_selected(self, index):
        pass

    def set_beamline_setup(self, beamline_setup):
        self._beamline_setup = beamline_setup

        limits_dict = self._beamline_setup.get_acquisition_limit_values()

        if 'osc_range' in limits_dict:
            limits = tuple(map(float, limits_dict['osc_range'].split(',')))
            (lower, upper) = limits
            osc_start_validator = qt.QDoubleValidator(lower, upper, 4, self)
            osc_range_validator = qt.QDoubleValidator(lower, upper, 4, self)
        else:
            osc_start_validator = qt.QDoubleValidator(-10000, 10000, 4, self)
            osc_range_validator = qt.QDoubleValidator(-10000, 10000, 4, self)

        osc_start_ledit = self.acq_widget_layout.child('osc_start_ledit')
        self._acquisition_mib.bind_value_update('osc_start', osc_start_ledit,
                                                float, osc_start_validator)

        osc_range_ledit = self.acq_widget_layout.child('osc_range_ledit')
        self._acquisition_mib.bind_value_update('osc_range', osc_range_ledit,
                                                float, osc_range_validator)

        if 'exposure_time' in limits_dict:
            limits = tuple(map(float, limits_dict['exposure_time'].split(',')))
            (lower, upper) = limits
            exp_time_valdidator = qt.QDoubleValidator(lower, upper, 5, self)
        else:
            exp_time_valdidator = qt.QDoubleValidator(-0.003, 6000, 5, self)
        
        exp_time_ledit = self.acq_widget_layout.child('exp_time_ledit')
        self._acquisition_mib.bind_value_update('exp_time', exp_time_ledit,
                                                float, exp_time_valdidator)

        self._acquisition_mib.\
             bind_value_update('energy',
                               self.acq_widget_layout.child('energy_ledit'),
                               float,
                               qt.QDoubleValidator(0, 1000, 4, self))

        self._acquisition_mib.\
             bind_value_update('transmission',
                            self.acq_widget_layout.child('transmission_ledit'),
                            float,
                            qt.QDoubleValidator(0, 1000, 2, self))

        self._acquisition_mib.\
             bind_value_update('resolution',
                               self.acq_widget_layout.child('resolution_ledit'),
                               float,
                               qt.QDoubleValidator(0, 1000, 3, self))

        qt.QObject.connect(self.acq_widget_layout.child('osc_start_cbox'),
                           qt.SIGNAL("toggled(bool)"),
                           self.osc_start_cbox_click)

        te = beamline_setup.tunable_wavelength()
        self.set_tunable_energy(te)

        has_aperture = self._beamline_setup.has_aperture()
        self.hide_aperture(has_aperture)    

    def set_energy(self, energy, wav):
        self._acquisition_parameters.energy = energy
        self.acq_widget_layout.child('energy_ledit').setText("%.4f" % float(energy))

    def update_transmission(self, transmission):
        self.acq_widget_layout.child('transmission_ledit').\
             setText("%.2f" % float(transmission))
        self._acquisition_parameters.transmission = float(transmission)

    def update_resolution(self, resolution):
        self.acq_widget_layout.child('resolution_ledit').\
             setText("%.3f" % float(resolution))
        self._acquisition_parameters.resolution = float(resolution)
    
    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._acquisition_mib.set_model(acquisition_parameters)
        self._path_template = path_template
        self.update_num_images(None, acquisition_parameters.num_images)

    def set_tunable_energy(self, state):
        self.acq_widget_layout.child('energy_ledit').setEnabled(state)

    def hide_aperture(self, state):
        if state:
            self.acq_widget_layout.child('aperture_ledit').show()
            self.acq_widget_layout.child('aperture_cbox').show()
        else:
            self.acq_widget_layout.child('aperture_ledit').hide()
            self.acq_widget_layout.child('aperture_cbox').hide()

    def use_osc_start(self, state):
        self.acq_widget_layout.child('osc_start_cbox').setChecked(state)
        self.acq_widget_layout.child('osc_start_cbox').setDisabled(state)

    def check_parameter_conflict(self):
        return len(self._acquisition_mib.validate_all()) > 0
