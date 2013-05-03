import queue_model
import qt

from widgets.widget_utils import DataModelInputBinder
from acquisition_widget_vertical_simple_layout\
    import AcquisitionWidgetVerticalSimpleLayout

class AcquisitionWidgetSimple(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, acq_params = None, 
                 path_template = None, layout = None):
        qt.QWidget.__init__(self, parent, name, fl)

        #
        # Attributes
        #
        if acq_params is None:
            self._acquisition_parameters = queue_model.AcquisitionParameters()
        else:
            self._acquisition_parameters = acq_params


        if path_template is None:
            self._path_template = queue_model.PathTemplate()
        else:
            self._path_template = path_template


        self._acquisition_mib = DataModelInputBinder(self._acquisition_parameters)


        #   
        # Layout
        #
        h_layout = qt.QHBoxLayout(self)
        
        self.acq_widget_layout = AcquisitionWidgetVerticalSimpleLayout(self)

        h_layout.addWidget(self.acq_widget_layout)


        #
        # Logic
        #
        self._acquisition_mib.bind_value_update('exp_time', 
                                                self.acq_widget_layout.exp_time_ledit,
                                                float,
                                                qt.QDoubleValidator(0.001, 6000, 2, self))
        
        self._acquisition_mib.bind_value_update('osc_range', 
                                                self.acq_widget_layout.osc_range_ledit,
                                                float,
                                                qt.QDoubleValidator(0.001, 1000, 2, self))


        # Default to 2-images
        self.acq_widget_layout.num_images_cbox.setCurrentItem(1)

        qt.QObject.connect(self.acq_widget_layout.num_images_cbox,
                           qt.SIGNAL("activated(int)"),
                           self.update_num_images)


    def update_num_images(self, index):
        if index is 0:
            self._acquisition_parameters.num_images = 1
            self._path_template.num_files = 1
        elif index is 1:
            self._acquisition_parameters.num_images = 2
            self._path_template.num_files = 2
        elif index is 2:
            self._acquisition_parameters.num_images = 4
            self._path_template.num_files = 4


    def use_mad(self, state):
        pass


    def get_mad_energy(self):
        pass


    def set_energies(self, energy_scan_result):
        pass


    def energy_selected(self, index):
        pass


    def set_energy(self, energy, wav):
        energy = round(float(energy), 4)
        self._acquisition_parameters.energy = energy

    
    def update_transmission(self, transmission):
        transmission = round(float(transmission), 1)
        self._acquisition_parameters.transmission = float(transmission)


    def update_resolution(self, resolution):
        resolution = round(float(resolution), 4)
        self._acquisition_parameters.resolution = float(resolution)


    def set_tunable_energy(self, state):
        pass
    

    def update_data_model(self, acquisition_parameters, path_template):
        self._acquisition_parameters = acquisition_parameters
        self._acquisition_mib.set_model(acquisition_parameters)
        self._path_template = path_template
        self._path_template_mib.set_model(path_template)
