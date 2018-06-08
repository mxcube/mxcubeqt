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

import queue_model_objects_v1 as queue_model_objects
from widgets.Qt4_heat_map_widget import HeatMapWidget


class AdvancedResultsWidget(QWidget):
    def __init__(self, parent=None, allow_adjust_size=True):
        QWidget.__init__(self, parent)
        self.setObjectName('advanced_results_widget')  

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._initialized = None
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        self.heat_map_widget = HeatMapWidget(self, allow_adjust_size)

        # Layout --------------------------------------------------------------
        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(self.heat_map_widget)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        _main_hlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def set_beamline_setup(self, bl_setup):
        if hasattr(bl_setup, 'parallel_processing_hwobj'):
            if bl_setup.parallel_processing_hwobj and \
            not self._initialized:
                bl_setup.parallel_processing_hwobj.connect(
                         'paralleProcessingResults', 
                         self.set_processing_results)
                self._initialized = True
        self.heat_map_widget.set_beamline_setup(bl_setup)

    def populate_widget(self, item, data_collection):
        #if isinstance(item, Qt4_queue_item.XrayCenteringQueueItem):
        #    data_collection = item.get_model().reference_image_collection
        #else: 
        #    data_collection = item.get_model()

        executed = data_collection.is_executed()

        self.heat_map_widget.clean_result()
        self.heat_map_widget.set_associated_data_collection(data_collection)
     
        if executed: 
            processing_results = data_collection.get_parallel_processing_result()
            if processing_results is not None:
                self.heat_map_widget.set_results(processing_results, True)

    def set_processing_results(self, processing_results, param, last_results):
        self.heat_map_widget.set_results(processing_results, last_results)
