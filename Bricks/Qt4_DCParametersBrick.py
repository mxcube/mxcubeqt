#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import html_template

from PyQt4 import QtGui

from widgets.Qt4_dc_parameters_widget import DCParametersWidget
from widgets.Qt4_image_tracking_widget import ImageTrackingWidget
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Task'


class Qt4_DCParametersBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beamline_setup_hwobj = None
        self.queue_model_hwobj = None
        self.session_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty("session", "string", "/session")
        self.addProperty("queue-model", "string", "/Qt4_queue-model")
        self.addProperty("beamline_setup", "string", "/Qt4_beamline-setup")
        self.addProperty("useImageTracking", "boolean", True)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_dc_parameter_widget",({}))
       
        # Graphic elements ---------------------------------------------------- 
        self.parameters_widget = DCParametersWidget(self, "parameters_widget")
        self.toggle_page_button = QtGui.QPushButton('View Results', self)
        self.toggle_page_button.setFixedWidth(120)
        self.results_static_view = QtGui.QTextBrowser(self)
        self.results_dynamic_view = ImageTrackingWidget(self) 
        self.stacked_widget = QtGui.QStackedWidget(self)
        self.stacked_widget.addWidget(self.parameters_widget)
        self.stacked_widget.addWidget(self.results_static_view) 
        self.stacked_widget.addWidget(self.results_dynamic_view)
       
        # Layout -------------------------------------------------------------- 
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.stacked_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.addWidget(self.toggle_page_button)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.toggle_page_button.clicked.connect(self.toggle_page)

        # Other --------------------------------------------------------------- 
        self.parameters_widget.collection_type = None
        #self.toggle_page_button.setDisabled(True)
        self.stacked_widget.setCurrentWidget(self.parameters_widget) 

    def populate_dc_parameter_widget(self, item):
        """
        Descript. :
        """
        self.parameters_widget._data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.parameters_widget._data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        data_collection = item.get_model()
        
        if data_collection.is_collected():
            self.parameters_widget.set_enabled(False)
            if self.use_image_tracking:
                self.results_dynamic_view.set_data_collection(data_collection)
                self.stacked_widget.setCurrentWidget(self.results_dynamic_view)
            else:
                self.populate_results(data_collection)
                self.stacked_widget.setCurrentWidget(self.results_static_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.parameters_widget.set_enabled(True)
            self.stacked_widget.setCurrentWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

        self.parameters_widget.populate_widget(item)
        #self.toggle_page_button.setEnabled(data_collection.is_collected())

    def populate_results(self, data_collection):
        """
        Descript. :
        """
        if data_collection.html_report[-4:] == 'html':
            if self.results_static_view.mimeSourceFactory().\
                   data(data_collection.html_report) == None:
                self.results_static_view.setText(\
                     html_template.html_report(data_collection))
            else:
                self.results_static_view.setSource(data_collection.html_report)
        else:
            self.results_static_view.setText(\
                 html_template.html_report(data_collection))
        
    def toggle_page(self):
        """
        Descript. :
        """
        if self.stacked_widget.currentWidget() is self.parameters_widget:
            self.results_static_view.reload()
            if self.use_image_tracking:
                self.results_dynamic_view.refresh()
                self.stacked_widget.setCurrentWidget(self.results_dynamic_view)
            else:
                self.results_static_view.reload()
                self.stacked_widget.setCurrentWidget(self.results_static_view)
            self.toggle_page_button.setText("View parameters")
        else:
            self.stacked_widget.setCurrentWidget(self.parameters_widget)
            self.toggle_page_button.setText("View Results")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'beamline_setup':            
            self.beamline_setup_hwobj = self.getHardwareObject(new_value)
            self.parameters_widget.set_beamline_setup(self.beamline_setup_hwobj)
            if hasattr(self.beamline_setup_hwobj, "image_tracking_hwobj"):
                self.results_dynamic_view.set_image_tracking_hwobj(\
                     self.beamline_setup_hwobj.image_tracking_hwobj)
        elif property_name == 'queue-model':            
            self.parameters_widget.queue_model_hwobj = \
                 self.getHardwareObject(new_value)
        elif property_name == 'useImageTracking':
            self.use_image_tracking = new_value
