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

from QtImport import *

from widgets.Qt4_dc_parameters_widget import DCParametersWidget
from widgets.Qt4_image_tracking_widget import ImageTrackingWidget
from widgets.Qt4_advanced_results_widget import AdvancedResultsWidget
from widgets.Qt4_snapshot_widget import SnapshotWidget
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Task"


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
        self.addProperty("queue-model", "string", "/queue-model")
        self.addProperty("beamline_setup", "string", "/beamline-setup")
        self.addProperty("useImageTracking", "boolean", True)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_dc_parameter_widget",({}))
       
        # Graphic elements ---------------------------------------------------- 
        self.tool_box = QToolBox(self)
        self.parameters_widget = DCParametersWidget(self, "parameters_widget")
        self.results_static_view = QTextBrowser(self.tool_box)
        self.image_tracking_widget = ImageTrackingWidget(self.tool_box) 
        self.advance_results_widget = AdvancedResultsWidget(self.tool_box)
        self.snapshot_widget = SnapshotWidget(self)

        self.tool_box.addItem(self.parameters_widget, "Parameters")
        self.tool_box.addItem(self.image_tracking_widget, "Results - ADXV control")
        self.tool_box.addItem(self.results_static_view, "Results - Summary")
        self.tool_box.addItem(self.advance_results_widget, "Results - Parallel processing")

        # Layout -------------------------------------------------------------- 
        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.snapshot_widget)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other --------------------------------------------------------------- 

    def populate_dc_parameter_widget(self, item):
        """
        Descript. :
        """
        self.parameters_widget._data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.parameters_widget._data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        data_collection = item.get_model()

        #if data_collection.is_helical():
        #    self.advance_results_widget.show()
        #else:
        #    self.advance_results_widget.hide()
              
        self.snapshot_widget.display_snapshot(data_collection.\
             acquisitions[0].acquisition_parameters.\
             centred_position.snapshot_image,
             width=400) 
        
        if data_collection.is_collected():
            self.parameters_widget.setEnabled(False)
            self.results_static_view.reload()
            self.image_tracking_widget.set_data_collection(data_collection)
            self.image_tracking_widget.refresh()
        else:
            self.parameters_widget.setEnabled(True)

        self.parameters_widget.populate_widget(item)
        self.advance_results_widget.populate_widget(item, data_collection)

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
        
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'beamline_setup':            
            self.beamline_setup_hwobj = self.getHardwareObject(new_value)
            self.session_hwobj = self.beamline_setup_hwobj.session_hwobj
            self.parameters_widget.set_beamline_setup(self.beamline_setup_hwobj)
            self.advance_results_widget.set_beamline_setup(self.beamline_setup_hwobj)
            if hasattr(self.beamline_setup_hwobj, "image_tracking_hwobj"):
                self.image_tracking_widget.set_image_tracking_hwobj(\
                     self.beamline_setup_hwobj.image_tracking_hwobj)
        elif property_name == 'queue-model':            
            self.parameters_widget.queue_model_hwobj = \
                 self.getHardwareObject(new_value)
        elif property_name == 'useImageTracking':
            if new_value:
                self.tool_box.removeItem(self.tool_box.indexOf(\
                     self.results_static_view))
                self.results_static_view.hide()
            else:
                self.tool_box.removeItem(self.tool_box.indexOf(\
                     self.image_tracking_widget))
                self.image_tracking_widget.hide()
