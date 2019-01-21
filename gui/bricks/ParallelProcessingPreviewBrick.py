#
#  Project: MXCuBE
#  https://github.com/mxcube
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

import QtImport

from gui.utils import queue_item
from gui.BaseComponents import BaseWidget
from gui.widgets.advanced_results_widget import AdvancedResultsWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class ParallelProcessingPreviewBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("beamline_setup", "string", "/beamline-setup")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.mesh_results_widget = AdvancedResultsWidget(self, allow_adjust_size=True)
        self.line_results_widget = AdvancedResultsWidget(self, allow_adjust_size=True)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.mesh_results_widget)
        _main_vlayout.addWidget(self.line_results_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.MinimumExpanding
        )

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
        if isinstance(item, queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.results_widget.populate_widget(item, data_collection)
            self.line_results_widget.populate_widget(
                item, item.get_model().line_collection
            )
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

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "beamline_setup":
            bl_setup = self.get_hardware_object(new_value)
            self.mesh_results_widget.set_beamline_setup(bl_setup)
            self.line_results_widget.set_beamline_setup(bl_setup)
