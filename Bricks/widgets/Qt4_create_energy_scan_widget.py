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

import logging

from PyQt4 import QtGui

import Qt4_queue_item
import Qt4_GraphicsManager as graphics_manager
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
        self.periodic_table = PeriodicTableWidget(self)

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.periodic_table)
        self.main_layout.addStretch(0)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout) 

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

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
        self.periodic_table.periodicTable.\
            setElements(energy_scan_hwobj.getElements())

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

        selected_edge = False

        if self.periodic_table.current_edge:
            selected_edge = True
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.")

        return base_result and selected_edge

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        """
        Descript. :
        """
        data_collections = []

        if self.periodic_table.current_edge:
            path_template = self._create_path_template(sample, self._path_template)

            energy_scan = queue_model_objects.EnergyScan(sample,
                                                         path_template)
            energy_scan.set_name(path_template.get_prefix())
            energy_scan.set_number(path_template.run_number)
            energy_scan.element_symbol = self.periodic_table.current_element
            energy_scan.edge = self.periodic_table.current_edge

            data_collections.append(energy_scan)
        else:
            logging.getLogger("user_level_log").\
                info("No element selected, please select an element.")

        return data_collections
