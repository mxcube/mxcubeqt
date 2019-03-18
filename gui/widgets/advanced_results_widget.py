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
from gui.utils import QtImport
from gui.widgets.heat_map_widget import HeatMapWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class AdvancedResultsWidget(QtImport.QWidget):
    def __init__(self, parent=None, allow_adjust_size=True):
        QtImport.QWidget.__init__(self, parent)
        self.setObjectName("advanced_results_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._initialized = None
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        self.heat_map_widget = HeatMapWidget(self, allow_adjust_size)

        # Layout --------------------------------------------------------------
        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(self.heat_map_widget)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        _main_hlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def init_api(self):
        if not self._initialized:
            api.parallel_processing.connect(
               "processingStarted", self.processing_started
            )
            api.parallel_processing.connect(
               "processingResultsUpdate", self.update_processing_results
            )
            self._initialized = True

    def populate_widget(self, item, data_collection):
        # if isinstance(item, queue_item.XrayCenteringQueueItem):
        #    data_collection = item.get_model().reference_image_collection
        # else:
        #    data_collection = item.get_model()

        executed = data_collection.is_executed()
        self.heat_map_widget.set_associated_data_collection(data_collection)

        if executed:
            processing_results = data_collection.get_parallel_processing_result()
            if processing_results is not None:
                self.heat_map_widget.set_results(processing_results)
                self.heat_map_widget.update_results(True)

    def processing_started(self, params_dict, raw_results, aligned_results):
        self.heat_map_widget.set_results(aligned_results)

    def update_processing_results(self, last_results):
        self.heat_map_widget.update_results(last_results)
