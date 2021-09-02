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


from mxcubeqt.utils import qt_import, queue_item
from mxcubeqt.base_components import BaseWidget
from mxcubeqt.widgets.hit_map_widget import HitMapWidget

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class OnlineProcessingBrick(BaseWidget):

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.define_slot("populate_widget", ({}))

        # Graphic elements ----------------------------------------------------
        self.hit_map_widget = HitMapWidget(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = qt_import.QHBoxLayout(self)
        _main_vlayout.addWidget(self.hit_map_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

        if HWR.beamline.online_processing is not None:
            HWR.beamline.online_processing.connect(
               "processingStarted", self.processing_started
            )
            HWR.beamline.online_processing.connect(
               "processingResultsUpdate", self.update_processing_results
            )
        else:
            self.setEnabled(False)

    def populate_widget(self, item):
        data_collection = item.get_model()
        if isinstance(item, queue_item.XrayCenteringQueueItem):
            data_collection = data_collection.mesh_dc
        self.hit_map_widget.set_data_collection(data_collection)
        if data_collection.is_executed():
            processing_results = data_collection.get_online_processing_results()
            self.hit_map_widget.set_results(
                    processing_results["raw"],
                    processing_results["aligned"]
            )
            self.hit_map_widget.update_results(True)

    def processing_started(self, data_collection, results_raw, results_aligned):
        self.hit_map_widget.set_results(results_raw, results_aligned)

    def update_processing_results(self, last_results):
        self.hit_map_widget.update_results(last_results)
