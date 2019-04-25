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

import api
from gui.utils import queue_item, QtImport
from gui.BaseComponents import BaseWidget
from gui.widgets.advanced_parameters_widget import AdvancedParametersWidget
from gui.widgets.advanced_results_widget import AdvancedResultsWidget
from gui.widgets.snapshot_widget import SnapshotWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class AdvancedBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_advanced_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.tool_box = QtImport.QToolBox(self)
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
        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.snapshot_widget)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def populate_advanced_widget(self, item):
        self.parameters_widget._data_path_widget.set_base_image_directory(
            api.session.get_base_image_directory()
        )
        self.parameters_widget._data_path_widget.set_base_process_directory(
            api.session.get_base_process_directory()
        )

        self.line_parameters_widget._data_path_widget.set_base_image_directory(
            api.session.get_base_image_directory()
        )
        self.line_parameters_widget._data_path_widget.set_base_process_directory(
            api.session.get_base_process_directory()
        )

        # self.parameters_widget.populate_widget(item)
        # self.results_widget.populate_widget(item)

        if isinstance(item, queue_item.XrayCenteringQueueItem):
            data_collection = item.get_model().reference_image_collection
            self.parameters_widget.populate_widget(item, data_collection)
            self.results_widget.populate_widget(item, data_collection)

            self.line_parameters_widget.populate_widget(
                item, item.get_model().line_collection
            )
            self.line_results_widget.populate_widget(
                item, item.get_model().line_collection
            )
        else:
            data_collection = item.get_model()
            self.parameters_widget.populate_widget(item, data_collection)
            self.results_widget.populate_widget(item, data_collection)

        self.line_parameters_widget.setEnabled(
            isinstance(item, queue_item.XrayCenteringQueueItem)
        )
        self.line_results_widget.setEnabled(
            isinstance(item, queue_item.XrayCenteringQueueItem)
        )

        try:
            self.snapshot_widget.display_snapshot(data_collection.grid.get_snapshot())
        except BaseException:
            pass

        self.tool_box.setCurrentWidget(self.results_widget)
