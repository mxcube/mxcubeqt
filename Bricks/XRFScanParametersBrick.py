import qt


from BlissFramework import BaseComponents
from widgets.xrf_scan_parameters_widget import XRFScanParametersWidget


__category__ = 'mxCuBE_v3'


class XRFScanParametersBrick(BaseComponents.BlissWidget):

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('xrf-scan', 'string', '')        
        self.addProperty("session", "string", "/session")
        self.session_hwobj = None
        
        # Layout
        main_layout = qt.QVBoxLayout(self)
        self.xrf_scan_widget = XRFScanParametersWidget(self)
        main_layout.addWidget(self.xrf_scan_widget)

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self.xrf_scan_widget.data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.xrf_scan_widget.data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()
        self.xrf_scan_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
