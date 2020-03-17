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

import copy
import logging

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.acquisition_widget import AcquisitionWidget
from gui.widgets.processing_widget import ProcessingWidget
from gui.widgets.comments_widget import CommentsWidget

from HardwareRepository.HardwareObjects import queue_model_objects
from HardwareRepository.HardwareObjects.queue_model_enumerables import EXPERIMENT_TYPE
from HardwareRepository.HardwareObjects.QtGraphicsLib import GraphicsItemLine

from HardwareRepository import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateHelicalWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):

        CreateTaskBase.__init__(self, parent, name, fl, "Helical")

        if not name:
            self.setObjectName("create_helical_widget")
        self.init_models()

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._lines_map = {}

        # Graphic elements ----------------------------------------------------
        self._lines_widget = QtImport.load_ui_file("helical_line_widget_layout.ui")

        self._acq_widget = AcquisitionWidget(
            self,
            "acquisition_widget",
            layout="vertical",
            acq_params=self._acquisition_parameters,
            path_template=self._path_template,
        )

        self._data_path_widget = DataPathWidget(
            self,
            "create_dc_path_widget",
            data_model=self._path_template,
            layout="vertical",
        )

        self._processing_widget = ProcessingWidget(
            self, data_model=self._processing_parameters
        )

        self._comments_widget = CommentsWidget(self) 

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._lines_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._processing_widget)
        _main_vlayout.addWidget(self._comments_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(6)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        self._comments_widget.setFixedHeight(100)

        # Qt signal/slot connections ------------------------------------------
        self._lines_widget.lines_treewidget.itemSelectionChanged.connect(
            self.lines_treewidget_selection_changed
        )
        self._lines_widget.create_line_button.clicked.connect(
            self.create_line_button_clicked
        )
        self._lines_widget.create_auto_line_button.clicked.connect(
            self.create_auto_line_button_clicked
        )
        self._lines_widget.remove_line_button.clicked.connect(
            self.remove_line_button_clicked
        )
        self._lines_widget.overlay_cbox.stateChanged.connect(self.overlay_toggled)
        self._lines_widget.overlay_slider.valueChanged.connect(
            self.overlay_alpha_changed
        )
        self._lines_widget.swap_points_button.clicked.connect(self.swap_points_clicked)

        self._acq_widget.acqParametersChangedSignal.connect(self.acq_parameters_changed)
        self._acq_widget.madEnergySelectedSignal.connect(self.mad_energy_selected)
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )
        self._processing_widget.enableProcessingSignal.connect(
            self._run_processing_toggled
        )
        # Other ---------------------------------------------------------------
        for col in range(self._lines_widget.lines_treewidget.columnCount()):
            self._lines_widget.lines_treewidget.resizeColumnToContents(col)
        # self._processing_widget.processing_widget.\
        #     run_processing_parallel_cbox.setChecked(False)


        self._processing_widget.processing_widget.run_processing_parallel_cbox.setChecked(
            HWR.beamline.run_processing_parallel
        )
        self.enable_widgets(False)

        shapes = HWR.beamline.sample_view.get_shapes()
        for shape in shapes:
            if isinstance(shape, GraphicsItemLine):
                self.shape_created(shape, "Line")

        HWR.beamline.sample_view.connect("shapeCreated", self.shape_created)
        HWR.beamline.sample_view.connect("shapeChanged", self.shape_changed)
        HWR.beamline.sample_view.connect("shapeDeleted", self.shape_deleted)

        self._comments_widget.setHidden(True)

    def enable_widgets(self, state):
        self._acq_widget.setEnabled(state)
        self._data_path_widget.setEnabled(state)
        self._processing_widget.setEnabled(state)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._energy_scan_result = queue_model_objects.EnergyScanResult()
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        has_shutter_less = HWR.beamline.detector.has_shutterless()
        self._acquisition_parameters.shutterless = has_shutter_less

        self._acquisition_parameters = (
            HWR.beamline.get_default_acquisition_parameters("helical")
        )

    def shape_created(self, shape, shape_type):
        if shape_type == "Line":
            self._lines_widget.lines_treewidget.clearSelection()
            # info_str_list = QStringList()
            info_str_list = []
            info_str_list.append(shape.get_display_name())
            info_str_list.append("%d" % shape.get_points_index()[0])
            info_str_list.append("%d" % shape.get_points_index()[1])

            lines_treewidget_item = QtImport.QTreeWidgetItem(
                self._lines_widget.lines_treewidget, info_str_list
            )
            lines_treewidget_item.setSelected(True)
            self._lines_map[shape] = lines_treewidget_item

            self.lines_treewidget_selection_changed()

    def shape_deleted(self, shape, shape_type):
        if shape_type == "Line" and self._lines_map.get(shape):
            shape_index = self._lines_widget.lines_treewidget.indexFromItem(
                self._lines_map[shape]
            )
            self._lines_widget.lines_treewidget.takeTopLevelItem(shape_index.row())
            self._lines_map.pop(shape)

    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)

        if len(self._lines_widget.lines_treewidget.selectedItems()) == 0:
            logging.getLogger("GUI").warning(
                "No lines selected, please select one or more lines."
            )
            return False
        else:
            return base_result

    def select_line_with_cpos(self, start_cpos, end_cpos, num_images):
        """Selects graphical line which contains two cpositions
           Adds number of frames next to the graphical line
        """
        self._lines_widget.overlay_slider.setEnabled(False)
        self._lines_widget.overlay_cbox.setEnabled(False)

        HWR.beamline.sample_view.de_select_all()
        for shape in HWR.beamline.sample_view.get_shapes():
            if isinstance(shape, GraphicsItemLine):
                (start_cpos_index, end_cpos_index) = shape.get_points_index()
                if (
                    start_cpos_index == start_cpos.index
                    and end_cpos_index == end_cpos.index
                ):
                    HWR.beamline.sample_view.select_shape(shape)
                    shape.set_num_images(num_images)

                    self._lines_widget.overlay_slider.setEnabled(True)
                    self._lines_widget.overlay_cbox.setEnabled(True)

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            self._processing_parameters = sample_model.processing_parameters
            # self._processing_parameters = copy.deepcopy(self._processing_parameters)
            self._processing_widget.update_data_model(self._processing_parameters)
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
            data_collection = tree_item.get_model()

            if data_collection.is_helical():
                self.setDisabled(tree_item.get_model().is_executed())

                self._path_template = data_collection.get_path_template()
                self._data_path_widget.update_data_model(self._path_template)
                self._acquisition_parameters = data_collection.acquisitions[
                    0
                ].acquisition_parameters

                if len(data_collection.acquisitions) == 2:
                    start_cpos = data_collection.acquisitions[
                        0
                    ].acquisition_parameters.centred_position
                    end_cpos = data_collection.acquisitions[
                        1
                    ].acquisition_parameters.centred_position
                    num_images = data_collection.acquisitions[
                        0
                    ].acquisition_parameters.num_images
                    self.select_line_with_cpos(start_cpos, end_cpos, num_images)

                self._acq_widget.update_data_model(
                    self._acquisition_parameters, self._path_template
                )
                # self.get_acquisition_widget().use_osc_start(True)

                self._processing_parameters = data_collection.processing_parameters
                self._processing_widget.update_data_model(self._processing_parameters)
            else:
                self.setDisabled(True)
        else:
            self.setDisabled(True)

        if (
            isinstance(tree_item, queue_item.SampleQueueItem)
            or isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)
            or isinstance(tree_item, queue_item.DataCollectionQueueItem)
        ):

            self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.update_data_model(
                self._acquisition_parameters, self._path_template
            )

    def _create_task(self, sample, shape, comments=None):
        data_collections = []

        for shape in self.get_selected_shapes():
            snapshot = HWR.beamline.sample_view.get_scene_snapshot(shape)

            # Acquisition for start position
            start_acq = self._create_acq(sample)

            start_graphical_point, end_graphical_point = shape.get_graphical_points()

            start_acq.acquisition_parameters.centred_position = copy.deepcopy(
                start_graphical_point.get_centred_position()
            )
            start_acq.acquisition_parameters.centred_position.snapshot_image = snapshot

            start_acq.path_template.suffix = HWR.beamline.session.suffix

            # Add another acquisition for the end position
            end_acq = self._create_acq(sample)

            end_acq.acquisition_parameters.centred_position = copy.deepcopy(
                end_graphical_point.get_centred_position()
            )
            end_acq.acquisition_parameters.centred_position.snapshot_image = snapshot
            end_acq.path_template.suffix = HWR.beamline.session.suffix

            processing_parameters = copy.deepcopy(self._processing_parameters)

            dc = queue_model_objects.DataCollection(
                [start_acq, end_acq], sample.crystals[0], processing_parameters
            )

            dc.set_name(start_acq.path_template.get_prefix())
            dc.set_number(start_acq.path_template.run_number)
            dc.set_experiment_type(EXPERIMENT_TYPE.HELICAL)
            dc.set_requires_centring(False)
            dc.run_processing_after = (
                self._processing_widget.processing_widget.run_processing_after_cbox.isChecked()
            )
            if (
                self._processing_widget.processing_widget.run_processing_parallel_cbox.isChecked()
            ):
                dc.run_processing_parallel = "LineScan"

            data_collections.append(dc)
            self._path_template.run_number += 1

        return data_collections

    def lines_treewidget_selection_changed(self):
        self.enable_widgets(
            len(self._lines_widget.lines_treewidget.selectedItems()) > 0
        )
        self._lines_widget.remove_line_button.setEnabled(
            len(self._lines_widget.lines_treewidget.selectedItems()) > 0
        )
        self._lines_widget.swap_points_button.setEnabled(
            len(self._lines_widget.lines_treewidget.selectedItems()) > 0
        )

        for shape, list_item in self._lines_map.items():
            HWR.beamline.sample_view.select_shape(shape, list_item.isSelected())
        self._acq_widget.emit_acq_parameters_changed()

    def create_line_button_clicked(self):
        HWR.beamline.sample_view.create_line()

    def create_auto_line_button_clicked(self):
        HWR.beamline.sample_view.create_auto_line()

    def remove_line_button_clicked(self):
        line_to_delete = None
        for line, treewidget_item in self._lines_map.items():
            if treewidget_item.isSelected():
                line_to_delete = line
                break
        if line_to_delete:
            HWR.beamline.sample_view.delete_shape(line_to_delete)
        self.lines_treewidget_selection_changed()

    def get_selected_shapes(self):
        selected_lines = []
        for line, treewidget_item in self._lines_map.items():
            if treewidget_item.isSelected():
                selected_lines.append(line)
        return selected_lines

    def overlay_toggled(self, state):
        HWR.beamline.sample_view.set_display_overlay(state)

    def overlay_alpha_changed(self, alpha_value):
        for line, treewidget_item in self._lines_map.items():
            if treewidget_item.isSelected():
                line.set_fill_alpha(alpha_value)

    def swap_points_clicked(self):
        for line, treewidget_item in self._lines_map.items():
            if treewidget_item.isSelected():
                HWR.beamline.sample_view.swap_line_points(line)
