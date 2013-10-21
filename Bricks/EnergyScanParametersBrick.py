import qt


from BlissFramework import BaseComponents
from widgets.energy_scan_parameters_widget import EnergyScanParametersWidget


__category__ = 'mxCuBE_v3'


class EnergyScanParametersBrick(BaseComponents.BlissWidget):

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('energy-scan', 'string', '')        
        self.addProperty("session", "string", "/session")
        
        # Layout
        main_layout = qt.QVBoxLayout(self)
        self.energy_scan_widget = EnergyScanParametersWidget(self)
        main_layout.addWidget(self.energy_scan_widget)

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self.energy_scan_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'energy-scan':
            self.energy_scan_widget.periodic_table['mnemonic'] = new_value
        elif property_name == 'session':
            session_hwobj = self.getHardwareObject(new_value)
            self.energy_scan_widget.data_path_widget._base_image_dir = \
                session_hwobj.get_base_image_directory()
            self.energy_scan_widget.data_path_widget._base_process_dir = \
                session_hwobj.get_base_process_directory()
