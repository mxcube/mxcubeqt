import qt


from BlissFramework import BaseComponents
from widgets.energy_scan_parameters_widget import EnergyScanParametersWidget


__category__ = 'mxCuBE_v3'


class EnergyScanParametersBrick(BaseComponents.BlissWidget):

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('energy-scan', 'string', '')        

        # Layout
        main_layout = qt.QVBoxLayout(self)
        self.energy_scan_widget = EnergyScanParametersWidget(self)
        main_layout.addWidget(self.energy_scan_widget)

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))


    def populate_parameter_widget(self, energy_scan):
        self.energy_scan_widget.populate_widget(energy_scan)


    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'energy-scan':
            self.energy_scan_widget.periodic_table['mnemonic'] = new_value
