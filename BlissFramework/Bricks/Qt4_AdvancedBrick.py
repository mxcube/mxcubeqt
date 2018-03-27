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

import os

from QtImport import *

import Qt4_queue_item

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_advanced_parameters_widget import AdvancedParametersWidget
from widgets.Qt4_advanced_results_widget import AdvancedResultsWidget
from widgets.Qt4_snapshot_widget import SnapshotWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = 'Task'


class Qt4_AdvancedBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.session_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty("beamline_setup", "string", "/beamline-setup")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_advanced_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.tool_box = QToolBox(self)
        self.parameters_widget = AdvancedParametersWidget(self) 
        self.results_widget = AdvancedResultsWidget(self)

        self.line_parameters_widget = AdvancedParametersWidget(self)
        self.line_results_widget = AdvancedResultsWidget(self)
        self.snapshot_widget = SnapshotWidget(self)

        self.tool_box.addItem(self.parameters_widget, "2D Heat map: Parameters")
        self.tool_box.addItem(self.results_widget, "2D Heat map: Results")
        self.tool_box.addItem(self.line_parameters_widget, "Line scan: Parameters")
        self.tool_box.addItem(self.line_results_widget, "Line scan: Results")

        # Layout --------------------------------------------------------------
        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.snapshot_widget)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        

    def populate_advanced_widget(self, item):
        self.parameters_widget._data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.parameters_widget._data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        self.line_parameters_widget._data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.line_parameters_widget._data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()

        #self.parameters_widget.populate_widget(item)
        #self.results_widget.populate_widget(item)

        if isinstance(item, Qt4_queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.parameters_widget.populate_widget(item, data_collection)
            self.results_widget.populate_widget(item, data_collection)   

            self.line_parameters_widget.populate_widget(item, item.get_model().line_collection)
            self.line_results_widget.populate_widget(item, item.get_model().line_collection) 
        else:
            data_collection = item.get_model()
            self.parameters_widget.populate_widget(item, data_collection)
            self.results_widget.populate_widget(item, data_collection) 

        self.line_parameters_widget.setEnabled(isinstance(item, Qt4_queue_item.XrayCenteringQueueItem))
        self.line_results_widget.setEnabled(isinstance(item, Qt4_queue_item.XrayCenteringQueueItem))

        self.snapshot_widget.display_snapshot(\
             data_collection.grid.get_snapshot())

        self.tool_box.setCurrentWidget(self.results_widget)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'beamline_setup':
            bl_setup = self.getHardwareObject(new_value)
            self.session_hwobj = bl_setup.session_hwobj
            self.parameters_widget.set_beamline_setup(bl_setup)
            self.results_widget.set_beamline_setup(bl_setup)

            self.line_parameters_widget.set_beamline_setup(bl_setup)
            self.line_results_widget.set_beamline_setup(bl_setup)
