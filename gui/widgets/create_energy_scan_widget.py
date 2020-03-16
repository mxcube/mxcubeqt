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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

import copy
import logging

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.periodic_table_widget import PeriodicTableWidget
from gui.widgets.comments_widget import CommentsWidget

from HardwareRepository.HardwareObjects import queue_model_objects
from HardwareRepository.HardwareObjects.QtGraphicsLib import GraphicsItemPoint

from HardwareRepository import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateEnergyScanWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):

        CreateTaskBase.__init__(self, parent, name, fl, "Energy scan")

        if not name:
            self.setObjectName("create_energy_scan_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._periodic_table_widget = PeriodicTableWidget(self)
        self._data_path_widget = DataPathWidget(
            self, data_model=self._path_template, layout="vertical"
        )

        _parameters_gbox = QtImport.QGroupBox("Parameters", self)
        self._adjust_transmission_cbox = QtImport.QCheckBox(
            "Adjust transmission", _parameters_gbox
        )
        self._adjust_transmission_cbox.setChecked(False)
        self._adjust_transmission_cbox.setEnabled(True)
        self._max_transmission_label = QtImport.QLabel("Maximum transmission:")
        self._max_transmission_ledit = QtImport.QLineEdit("20", _parameters_gbox)
        self._max_transmission_ledit.setFixedWidth(80)
        self._max_transmission_ledit.setEnabled(False)

        self._comments_widget = CommentsWidget(self)

        # Layout --------------------------------------------------------------
        _parameters_gbox_hlayout = QtImport.QGridLayout(_parameters_gbox)
        _parameters_gbox_hlayout.addWidget(self._adjust_transmission_cbox, 0, 0)
        _parameters_gbox_hlayout.addWidget(self._max_transmission_label, 1, 0)
        _parameters_gbox_hlayout.addWidget(self._max_transmission_ledit, 1, 1)
        _parameters_gbox_hlayout.setColumnStretch(2, 1)
        _parameters_gbox_hlayout.setSpacing(2)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._periodic_table_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(_parameters_gbox)
        _main_vlayout.addWidget(self._comments_widget)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.setSpacing(6)
        _main_vlayout.addStretch(10)

        # SizePolicies --------------------------------------------------------
        self._comments_widget.setFixedHeight(100)

        # Qt signal/slot connections ------------------------------------------
        # self._periodic_table_widget.elementEdgeSelectedSignal.connect(\
        #     self.acq_parameters_changed)
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )
        self._adjust_transmission_cbox.stateChanged.connect(
            self.adjust_transmission_state_changed
        )
        self._max_transmission_ledit.textEdited.connect(
            self.max_transmission_value_changed
        )

        self._data_path_widget.data_path_layout.compression_cbox.setVisible(False)

        try:
            self._periodic_table_widget.set_elements(
                HWR.beamline.energy_scan.getElements()
            )

            max_transmission_value = (
                HWR.beamline.energy_scan.get_max_transmission_value()
            )

            self._adjust_transmission_cbox.setEnabled(True)
            self._adjust_transmission_cbox.setChecked(True)
            HWR.beamline.energy_scan.adjust_transmission(True)

            if max_transmission_value:
                self._max_transmission_ledit.setText("%.2f" % max_transmission_value)
        except BaseException:
            pass

    def set_expert_mode(self, state):
        self._adjust_transmission_cbox.setEnabled(state)
        self._max_transmission_label.setEnabled(state)
        self._max_transmission_ledit.setEnabled(state)

    def enable_compression(self, state):
        CreateTaskBase.enable_compression(self, False)

    def init_models(self):

        CreateTaskBase.init_models(self)
        self.enery_scan = queue_model_objects.EnergyScan()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = "raw"
        self._path_template.compression = False

    def init_data_path_model(self):
        # Initialize the path_template of the widget to default
        # values read from the beamline setup
        if self._data_path_widget:
            if hasattr(HWR.beamline.session, 'get_secondary_image_directory'):
                self._data_path_widget.set_base_image_directory(
                    HWR.beamline.session.get_secondary_image_directory()
                )
            self._data_path_widget.set_base_process_directory(
                HWR.beamline.session.get_base_process_directory()
            )

            (data_directory, proc_directory) = self.get_default_directory()
            self._path_template = HWR.beamline.get_default_path_template()
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix()
            self._path_template.run_number = HWR.beamline.queue_model.get_next_run_number(
                  self._path_template
            )
            self._path_template.compression = self._enable_compression
        else:
            self._path_template = queue_model_objects.PathTemplate()

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        escan_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.EnergyScanQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if escan_model.get_path_template():
                self._path_template = escan_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not (
            isinstance(tree_item, queue_item.SampleQueueItem)
            or isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)
        ):
            self.setDisabled(True)

    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)
        selected_element, selected_edge = (
            self._periodic_table_widget.get_selected_element_edge()
        )
        if not selected_element:
            logging.getLogger("GUI").warning(
                "No element selected, please select an element."
            )

        return base_result and selected_element

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape, comments=None):
        data_collections = []
        selected_element, selected_edge = (
            self._periodic_table_widget.get_selected_element_edge()
        )

        if selected_element:
            if not shape:
                cpos = queue_model_objects.CentredPosition()
                cpos.snapshot_image = HWR.beamline.sample_view.get_scene_snapshot()
            else:
                # Shapes selected and sample is mounted, get the
                # centred positions for the shapes
                if isinstance(shape, GraphicsItemPoint):
                    snapshot = HWR.beamline.sample_view.get_scene_snapshot(shape)

                    cpos = copy.deepcopy(shape.get_centred_position())
                    cpos.snapshot_image = snapshot

            path_template = self._create_path_template(sample, self._path_template)

            energy_scan = queue_model_objects.EnergyScan(sample, path_template, cpos)
            energy_scan.set_name(path_template.get_prefix())
            energy_scan.set_number(path_template.run_number)
            energy_scan.element_symbol = selected_element
            energy_scan.edge = selected_edge

            data_collections.append(energy_scan)
            self._path_template.run_number += 1
        else:
            logging.getLogger("GUI").info(
                "No element selected, please select an element."
            )

        return data_collections

    def element_edge_selected(self, element, edge):
        if len(self._current_selected_items) == 1:
            item = self._current_selected_items[0]
            if isinstance(item, queue_item.EnergyScanQueueItem):
                item.get_model().element_symbol = str(element)
                item.get_model().edge = str(edge)

    def adjust_transmission_state_changed(self, state):
        self._max_transmission_ledit.setEnabled(state)
        HWR.beamline.energy_scan.adjust_transmission(state)

    def max_transmission_value_changed(self, value):
        try:
            max_transmission = float(value)
            HWR.beamline.energy_scan.set_max_transmission(max_transmission)
        except BaseException:
            pass
