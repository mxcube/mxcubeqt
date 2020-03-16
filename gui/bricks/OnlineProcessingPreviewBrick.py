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


class OnlineProcessingPreviewBrick(BaseWidget):

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.tab_widget = QtImport.QTabWidget(self)
        self.osc_results_widget = AdvancedResultsWidget(self.tab_widget)
        self.mesh_results_widget = AdvancedResultsWidget(self.tab_widget)

        self.tab_widget.addTab(self.osc_results_widget, "Osc")
        self.tab_widget.addTab(self.mesh_results_widget, "Mesh")

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.tab_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.osc_results_widget.hit_map_widget._hit_map_tools_widget.setHidden(True)
        self.osc_results_widget.hit_map_widget._summary_gbox.setHidden(True)
        self.mesh_results_widget.hit_map_widget._hit_map_tools_widget.setHidden(True)
        self.mesh_results_widget.hit_map_widget._summary_gbox.setHidden(True)

    def populate_widget(self, item):
        if isinstance(item, queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.osc_results_widget.populate_widget(
                item, item.get_model().line_collection
            )
        else:
            data_collection = item.get_model()
            self.osc_results_widget.populate_widget(item)
            self.mesh_results_widget.populate_widget(item)

    def run(self):
        self.osc_results_widget.hit_map_widget.set_plot_type("1D")
        self.mesh_results_widget.hit_map_widget.set_plot_type("2D")
        if self["fixedWidth"] > 0:
            #self.results_widget._hit_map_gbox.setFixedWidth(self["fixedWidth"] - 2)
            self.osc_results_widget.hit_map_widget._hit_map_plot.setFixedWidth(self["fixedWidth"] - 4)
            self.mesh_results_widget.hit_map_widget._hit_map_plot.setFixedWidth(self["fixedWidth"] - 4)
        if self["fixedHeight"] > 0:
            self.osc_results_widget.hit_map_widget._hit_map_gbox.setFixedHeight(self["fixedHeight"] - 2)
            self.osc_results_widget.hit_map_widget._hit_map_plot.setFixedHeight(self["fixedHeight"] - 40)
            self.mesh_results_widget.hit_map_widget._hit_map_gbox.setFixedHeight(self["fixedHeight"] - 2)
            self.mesh_results_widget.hit_map_widget._hit_map_plot.setFixedHeight(self["fixedHeight"] - 40)
