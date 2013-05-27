import logging
import sys
import pprint


from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
from widgets.char_parameters_widget import CharParametersWidget


__category__ = 'mxCuBE_v3'

class CharParametersBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        # Framwork-2 properties
        self.addProperty("tunable-energy", "boolean", "True")
        self.addProperty("session", "string", "/session")

        # Qt-Slots
        self.defineSlot("populate_edna_parameter_widget",({}))

        # Layout        
        self.stack = QWidgetStack(self, 'stack')
        self.parameters_widget = CharParametersWidget(self)
        self.toggle_page_button = QPushButton('View Results', 
                                              self, 'toggle_page_button')
        self.toggle_page_button.setFixedWidth(100)

        self.results_view = QTextBrowser(self, "results_view")
        self.stack.addWidget(self.parameters_widget)
        self.stack.addWidget(self.results_view)

        main_layout = QVBoxLayout(self)
        self.layout().addWidget(self.stack)
        bottom_layout = QHBoxLayout(main_layout)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.toggle_page_button)

        # Logic
        self.stack.raiseWidget(self.parameters_widget)
        self.parameters_widget.collection_type = None
        QObject.connect(self.toggle_page_button, 
                        SIGNAL('clicked()'),
                        self.toggle_page)

        self.toggle_page_button.setDisabled(True)


    def populate_edna_parameter_widget(self, char):
        parameters = char.reference_image_collection
        char_params = char.characterisation_parameters
        
        if char.is_executed():
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("Back")

            if char.html_report:
                if self.results_view.mimeSourceFactory().\
                       data(char.html_report) == None:
                    self.results_view.setText("<center><h1>Characterisation failed</h1></center>") 
                else:
                    self.results_view.setSource(char.html_report)
            else:
                self.results_view.setText("<center><h1>Characterisation failed</h1></center>") 
                    
        else:
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.\
            populate_parameter_widget(char)
        self.toggle_page_button.setEnabled(char.is_executed())


    def toggle_page(self):
        if self.stack.visibleWidget() is self.parameters_widget:
            self.stack.raiseWidget(self.results_view)
            self.toggle_page_button.setText("Back")
        else:
            self.stack.raiseWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")


    # Framework-2 callback
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'tunable-energy':
            self.parameters_widget.acq_widget.set_tunable_energy(new_value)            
        elif property_name == 'session':
            session_hwobj = self.getHardwareObject(new_value)
            self.parameters_widget.path_widget.set_session(session_hwobj)
