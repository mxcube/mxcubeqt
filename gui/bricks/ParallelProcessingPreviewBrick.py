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

from gui.utils import queue_item, QtImport
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
        self.show_raw_results_cbox = QtImport.QCheckBox("Raw results", self)
        self.show_aligned_results_cbox = QtImport.QCheckBox("Aligned results", self)
        self.raw_results_widget = AdvancedResultsWidget(self, show_aligned_results=False)
        self.aligned_results_widget = AdvancedResultsWidget(self, show_aligned_results=True)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.raw_results_widget)
        _main_vlayout.addWidget(self.aligned_results_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.MinimumExpanding
        )

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.raw_results_widget.heat_map_widget._heat_map_tools_widget.setHidden(True)
        self.raw_results_widget.heat_map_widget._summary_gbox.setHidden(True)
        self.aligned_results_widget.setHidden(True)
        self.aligned_results_widget.heat_map_widget._heat_map_tools_widget.setHidden(True)
        self.aligned_results_widget.heat_map_widget._summary_gbox.setHidden(True)

        self.aligned_results_widget.heat_map_widget.setFixedWidth(1300)
        self.raw_results_widget.heat_map_widget.setFixedWidth(1300)

        print "raw  ", self.raw_results_widget.heat_map_widget
        print "aligned ", self.aligned_results_widget.heat_map_widget

    def populate_widget(self, item):
        if isinstance(item, queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.results_widget.populate_widget(item, data_collection)
            self.raw_results_widget.populate_widget(
                item, item.get_model().line_collection
            )
        else:
            data_collection = item.get_model()
            self.raw_results_widget.populate_widget(item, data_collection)
            self.aligned_results_widget.populate_widget(item, data_collection)
