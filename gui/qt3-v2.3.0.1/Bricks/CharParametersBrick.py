import qt


from BlissFramework import BaseComponents
from widgets.char_parameters_widget import CharParametersWidget


__category__ = "mxCuBE_v3"


class CharParametersBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.session_hwobj = None

        # Framwork-2 properties
        self.addProperty("tunable-energy", "boolean", "True")
        self.addProperty("session", "string", "/session")
        self.addProperty("beamline_setup", "string", "/beamline-setup")

        # Qt-Slots
        self.defineSlot("populate_edna_parameter_widget", ({}))

        # Layout
        self.stack = qt.QWidgetStack(self, "stack")
        self.parameters_widget = CharParametersWidget(self)
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

    def populate_edna_parameter_widget(self, item):
        self.parameters_widget.path_widget._base_image_dir = (
            self.session_hwobj.get_base_image_directory()
        )
        self.parameters_widget.path_widget._base_process_dir = (
            self.session_hwobj.get_base_process_directory()
        )

        char = item.get_model()

        if char.is_executed():
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
            self.parameters_widget.set_enabled(False)

            if char.html_report:
                if self.results_view.mimeSourceFactory().data(char.html_report) is None:
                    self.results_view.setText(
                        "<center><h1>Characterisation failed</h1></center>"
                    )
                else:
                    self.results_view.setSource(char.html_report)
            else:
                self.results_view.setText(
                    "<center><h1>Characterisation failed</h1></center>"
                )
        else:
            self.parameters_widget.set_enabled(True)
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.populate_parameter_widget(item)
        self.toggle_page_button.setEnabled(char.is_executed())

    def toggle_page(self):
        if self.stack.visibleWidget() is self.parameters_widget:
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

    # Framework-2 callback
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == "tunable-energy":
            self.parameters_widget.acq_widget.set_tunable_energy(new_value)
        elif property_name == "session":
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == "beamline_setup":
            beamline_setup = self.getHardwareObject(new_value)
            self.parameters_widget.set_beamline_setup(beamline_setup)
