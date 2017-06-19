import qt


from BlissFramework import BaseComponents
from widgets.xrf_spectrum_parameters_widget import XRFSpectrumParametersWidget


__category__ = 'mxCuBE_v3'


class XRFSpectrumParametersBrick(BaseComponents.BlissWidget):

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('xrf-spectrum', 'string', '')        
        self.addProperty("session", "string", "/session")
        self.session_hwobj = None
	self.xrf_spectrum_hwobj = None
        
        # Layout
        main_layout = qt.QVBoxLayout(self)
        self.xrf_spectrum_widget = XRFSpectrumParametersWidget(self)
        main_layout.addWidget(self.xrf_spectrum_widget)

        # Qt-Slots and signals
        self.defineSlot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self.xrf_spectrum_widget.data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.xrf_spectrum_widget.data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()
        self.xrf_spectrum_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
	if property_name == 'xrf-spectrum':
	    self.xrf_spectrum_hwobj = self.getHardwareObject(new_value) 	 
            self.xrf_spectrum_widget.set_xrf_spectrum_hwobj(self.getHardwareObject(new_value))
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)

