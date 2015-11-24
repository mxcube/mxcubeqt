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

import copy
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import Qt4_queue_item
import Qt4_GraphicsManager
import queue_model_objects_v1 as queue_model_objects

from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN
from Qt4_create_task_base import CreateTaskBase
from Qt4_data_path_widget import DataPathWidget
from Qt4_periodic_table_widget import PeriodicTableWidget


class CreateEnergyScanWidget(CreateTaskBase):
    """
    Descript. :
    """ 

    def __init__(self, parent = None,name = None, fl = 0):
        """
        Descript. :
        """
 
        CreateTaskBase.__init__(self, parent, name, fl, 'Energy scan')

        if not name:
            self.setObjectName("create_energy_scan_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._periodic_table_widget = PeriodicTableWidget(self)
        self._data_path_widget = DataPathWidget(self, 
             data_model = self._path_template, layout = 'vertical')

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self._periodic_table_widget)
        self.main_layout.addWidget(self._data_path_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)
        self.main_layout.addStretch(10)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._periodic_table_widget.elementEdgeSelectedSignal.connect(\
             self.element_edge_selected)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        self._data_path_widget.pathTemplateChangedSignal.connect(
             self.handle_path_conflict)

    def init_models(self):
        """
        Descript. :
        """
       
        CreateTaskBase.init_models(self)
        self.enery_scan = queue_model_objects.EnergyScan()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = 'raw'

    def set_energy_scan_hwobj(self, energy_scan_hwobj):
        """
        Descript. :
        """
        self._periodic_table_widget.periodic_table.setElements(\
             energy_scan_hwobj.getElements())

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)
        escan_model = tree_item.get_model()

        if isinstance(tree_item, Qt4_queue_item.EnergyScanQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if escan_model.get_path_template():
                self._path_template = escan_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not(isinstance(tree_item, Qt4_queue_item.SampleQueueItem) or \
                     isinstance(tree_item, Qt4_queue_item.DataCollectionGroupQueueItem)):
            self.setDisabled(True)

    def approve_creation(self):
        """
        Descript. :
        """
        base_result = CreateTaskBase.approve_creation(self)
        selected_element, selected_edge = self._periodic_table_widget.get_selected_element_edge()
        if not selected_element:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.")

        return base_result and selected_element

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        """
        Descript. :
        """
        data_collections = []
        selected_element, selected_edge = self._periodic_table_widget.get_selected_element_edge()   

        if selected_element:
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = self._graphics_manager_hwobj.get_snapshot()
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, Qt4_GraphicsManager.GraphicsItemPoint):
                    snapshot = self._graphics_manager_hwobj.\
                           get_snapshot(shape)

                    cpos = copy.deepcopy(shape.get_centred_position())
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)

            energy_scan = queue_model_objects.EnergyScan(sample,
                                                         path_template,
                                                         cpos)
            energy_scan.set_name(path_template.get_prefix())
            energy_scan.set_number(path_template.run_number)
            energy_scan.element_symbol = selected_element
            energy_scan.edge = selected_edge

            data_collections.append(energy_scan)
            self._path_template.run_number += 1
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.")

        return data_collections

    def element_edge_selected(self, element, edge):
        if len(self._current_selected_items) == 1:
            item = self._current_selected_items[0]
            if isinstance(item, Qt4_queue_item.EnergyScanQueueItem):
                item.get_model().element_symbol = str(element)
                item.get_model().edge = str(edge)
