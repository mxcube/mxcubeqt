#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from QtImport import *

import Qt4_queue_item
from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_advanced_results_widget import AdvancedResultsWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = 'Task'


class Qt4_ParallelProcessingPreviewBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty("beamline_setup", "string", "/beamline-setup")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("populate_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.mesh_results_widget = AdvancedResultsWidget(self, allow_adjust_size=True)
        self.line_results_widget = AdvancedResultsWidget(self, allow_adjust_size=True)

        # Layout --------------------------------------------------------------
        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(self.mesh_results_widget)
        _main_vlayout.addWidget(self.line_results_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.line_results_widget.setHidden(True)
        self.line_results_widget.heat_map_widget._heat_map_tools_widget.setHidden(True)
        self.line_results_widget.heat_map_widget._summary_gbox.setHidden(True)
        self.mesh_results_widget.heat_map_widget._heat_map_tools_widget.setHidden(True)
        self.mesh_results_widget.heat_map_widget._summary_gbox.setHidden(True)

        self.mesh_results_widget.heat_map_widget.setFixedWidth(1300)
        self.line_results_widget.heat_map_widget.setFixedWidth(1300)

    def populate_widget(self, item):
        if isinstance(item, Qt4_queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.results_widget.populate_widget(item, data_collection)   
            self.line_results_widget.populate_widget(item, item.get_model().line_collection) 
        else:
            data_collection = item.get_model()
            if data_collection.is_mesh():
                self.mesh_results_widget.setHidden(False)
                self.line_results_widget.setHidden(True)
                self.mesh_results_widget.populate_widget(item, data_collection)
            else:
                self.mesh_results_widget.setHidden(True)
                self.line_results_widget.setHidden(False)
                self.line_results_widget.populate_widget(item, data_collection)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'beamline_setup':
            bl_setup = self.getHardwareObject(new_value)
            self.mesh_results_widget.set_beamline_setup(bl_setup)
            self.line_results_widget.set_beamline_setup(bl_setup)
