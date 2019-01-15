import qt
import html_template

from widgets.dc_parameters_widget import DCParametersWidget
from BlissFramework import BaseComponents

__category__ = "mxCuBE_v3"


class DCParametersBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        # Data attribtues
        self.energy_hwobj = None
        self.transmission_hwobj = None
        self.resolution_hwobj = None
        self.queue_model_hwobj = None
        self.session_hwobj = None

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))

        # Properties
        self.addProperty("session", "string", "/session")
        self.addProperty("queue-model", "string", "/queue-model")
        self.addProperty("beamline_setup", "string", "/beamline-setup")

        # Layout
        self.stack = qt.QWidgetStack(self, "stack")
        self.parameters_widget = DCParametersWidget(self, "parameters_widget")

        self.toggle_page_button = qt.QPushButton(
            "View Results", self, "toggle_page_button"
        )
        self.toggle_page_button.setFixedWidth(100)

        self.results_view = qt.QTextBrowser(self, "results_view")
        self.stack.addWidget(self.parameters_widget)
        self.stack.addWidget(self.results_view)

        main_layout = qt.QVBoxLayout(self)
        self.layout().addWidget(self.stack)
        bottom_layout = qt.QHBoxLayout(main_layout)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.toggle_page_button)

        # Logic
        self.stack.raiseWidget(self.parameters_widget)
        self.parameters_widget.collection_type = None
        qt.QObject.connect(
            self.toggle_page_button, qt.SIGNAL("clicked()"), self.toggle_page
        )

        self.toggle_page_button.setDisabled(True)

    def populate_parameter_widget(self, item):
        self.parameters_widget.path_widget._base_image_dir = (
            self.session_hwobj.get_base_image_directory()
        )
        self.parameters_widget.path_widget._base_process_dir = (
            self.session_hwobj.get_base_process_directory()
        )

        data_collection = item.get_model()

        if data_collection.is_collected():
            self.parameters_widget.set_enabled(False)
            self.populate_results(data_collection)
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.parameters_widget.set_enabled(True)
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.populate_parameter_widget(item)
        self.toggle_page_button.setEnabled(data_collection.is_collected())

    def populate_results(self, data_collection):
        if data_collection.html_report[-4:] == "html":
            if (
                self.results_view.mimeSourceFactory().data(data_collection.html_report)
                is None
            ):
                self.results_view.setText(html_template.html_report(data_collection))
            else:
                self.results_view.setSource(data_collection.html_report)
        else:
            self.results_view.setText(html_template.html_report(data_collection))

    def toggle_page(self):
        if self.stack.visibleWidget() is self.parameters_widget:
            self.results_view.reload()
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == "session":
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == "beamline_setup":
            self.beamline_setup = self.getHardwareObject(new_value)
            self.parameters_widget.set_beamline_setup(self.beamline_setup)
        elif property_name == "queue-model":
            self.parameters_widget.queue_model_hwobj = self.getHardwareObject(new_value)
