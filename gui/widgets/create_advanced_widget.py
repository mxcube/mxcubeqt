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

import logging

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.acquisition_widget import AcquisitionWidget
from gui.widgets.comments_widget import CommentsWidget

from HardwareRepository.HardwareObjects import queue_model_objects

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateAdvancedWidget(CreateTaskBase):
    """Widget used to create advanced collection methods
    """

    def __init__(self, parent=None, name=None, fl=0):
        CreateTaskBase.__init__(
            self, parent, name, QtImport.Qt.WindowFlags(fl), "Advanced"
        )

        if not name:
            self.setObjectName("create_advanced_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._advanced_methods = None
        self._grid_map = {}
        self.spacing = [0, 0]
        self.dc_selected = False

        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._advanced_methods_widget = QtImport.load_ui_file(
            "advanced_methods_layout.ui"
        )
        self._acq_widget = AcquisitionWidget(
            self,
            "acquisition_widget",
            layout="vertical",
            acq_params=self._acquisition_parameters,
            path_template=self._path_template,
        )
        self._acq_widget.grid_mode = True

        self._data_path_widget = DataPathWidget(
            self,
            "create_dc_path_widget",
            data_model=self._path_template,
            layout="vertical",
        )

        self._comments_widget = CommentsWidget(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._advanced_methods_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._comments_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(6)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._acq_widget.acqParametersChangedSignal.connect(self.acq_parameters_changed)
        self._acq_widget.madEnergySelectedSignal.connect(self.mad_energy_selected)

        self._acq_widget.acq_widget_layout.osc_range_ledit.textEdited.connect(
            self.grid_osc_range_ledit_changed
        )
        self._acq_widget.acq_widget_layout.osc_total_range_ledit.textEdited.connect(
            self.grid_osc_total_range_ledit_changed
        )

        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )

        self._advanced_methods_widget.grid_treewidget.itemSelectionChanged.connect(
            self.grid_treewidget_item_selection_changed
        )
        self._advanced_methods_widget.draw_grid_button.clicked.connect(
            self.draw_grid_button_clicked
        )
        self._advanced_methods_widget.remove_grid_button.clicked.connect(
            self.remove_grid_button_clicked
        )
        self._advanced_methods_widget.hor_spacing_ledit.textEdited.connect(
            self.hor_spacing_changed
        )
        self._advanced_methods_widget.ver_spacing_ledit.textEdited.connect(
            self.ver_spacing_changed
        )

        self._advanced_methods_widget.move_right_button.clicked.connect(
            lambda: self.move_grid("right")
        )
        self._advanced_methods_widget.move_left_button.clicked.connect(
            lambda: self.move_grid("left")
        )
        self._advanced_methods_widget.move_up_button.clicked.connect(
            lambda: self.move_grid("up")
        )
        self._advanced_methods_widget.move_down_button.clicked.connect(
            lambda: self.move_grid("down")
        )

        self._advanced_methods_widget.overlay_cbox.toggled.connect(self.overlay_toggled)
        self._advanced_methods_widget.overlay_slider.valueChanged.connect(
            self.overlay_alpha_changed
        )
        self._advanced_methods_widget.overlay_color_button.clicked.connect(
            self.overlay_change_color
        )
        self._advanced_methods_widget.move_to_grid_button.clicked.connect(
            self.move_to_grid
        )
        self._advanced_methods_widget.method_combo.activated.connect(
            self.method_combo_activated
        )

        # Other ---------------------------------------------------------------
        self._acq_widget.use_osc_start(False)
        self._acq_widget.use_kappa(False)
        self._acq_widget.acq_widget_layout.num_images_label.setEnabled(False)
        self._acq_widget.acq_widget_layout.num_images_ledit.setEnabled(False)
        for col in range(self._advanced_methods_widget.grid_treewidget.columnCount()):
            self._advanced_methods_widget.grid_treewidget.resizeColumnToContents(col)

        self._acq_widget.acq_widget_layout.osc_total_range_label.setText(
            "Total osc. range per line"
        )

        self._advanced_methods = list(HWR.beamline.advanced_methods)
        if self._advanced_methods:
            for method in self._advanced_methods:
                self._advanced_methods_widget.method_combo.addItem(method)
        else:
            self.setEnabled(False)

        self._acq_widget.acq_widget_layout.osc_start_label.setText(
            "Oscillation middle:"
        )

        hor_size, ver_size = HWR.beamline.beam.get_beam_size()
        self.spacing[0] = hor_size
        self.spacing[1] = ver_size

        self._advanced_methods_widget.hor_spacing_ledit.setText(
            "%.1f" % (hor_size * 1000)
        )
        self._advanced_methods_widget.ver_spacing_ledit.setText(
            "%.1f" % (ver_size * 1000)
        )

        HWR.beamline.sample_view.connect("shapeCreated", self.shape_created)
        HWR.beamline.sample_view.connect("shapeChanged", self.shape_changed)
        HWR.beamline.sample_view.connect("shapeDeleted", self.shape_deleted)
        self._comments_widget.setHidden(True)

    def enable_widgets(self, state):
        return
        self._acq_widget.setEnabled(state)
        self._data_path_widget.setEnabled(state)

    def init_models(self):
        CreateTaskBase.init_models(self)

        self._processing_parameters = queue_model_objects.ProcessingParameters()

        has_shutter_less = HWR.beamline.detector.has_shutterless()
        self._acquisition_parameters.shutterless = has_shutter_less

        self._acquisition_parameters = (
            HWR.beamline.get_default_acquisition_parameters("advanced")
        )

    def set_beam_info(self, beam_info):
        self.spacing[0] = beam_info["size_x"]
        self.spacing[1] = beam_info["size_y"]
        self._advanced_methods_widget.hor_spacing_ledit.setText(
            "%.1f" % (beam_info["size_x"] * 1000)
        )
        self._advanced_methods_widget.ver_spacing_ledit.setText(
            "%.1f" % (beam_info["size_x"] * 1000)
        )

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)
        selected_grid = self.get_selected_shapes()[0]

        if not selected_grid:
            msg = "No grid selected. Please select a grid to continue!"
            logging.getLogger("GUI").warning(msg)
            result = False
            # selected_grid = HWR.beamline.sample_view.get_auto_grid()
        else:
            grid_properties = selected_grid.get_properties()
            exp_time = float(self._acq_widget.acq_widget_layout.exp_time_ledit.text())
            speed = grid_properties["yOffset"] / exp_time
            if speed >= 2.25:
                logging.getLogger("GUI").error(
                    "Translation speed %.3f is above the limit 2.25" % speed
                )
                return False
            osc_range_per_frame = float(
                self._acq_widget.acq_widget_layout.osc_range_ledit.text()
            )
            speed = osc_range_per_frame / exp_time
            if speed >= 300:
                logging.getLogger("GUI").error(
                    "Rotation speed per frame %.3f is above the limit 300" % speed
                )
                return False
        return result

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)
        self.dc_selected = False

        if isinstance(tree_item, queue_item.SampleQueueItem):
            pass
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            pass
            # self.setDisabled(False)
        elif isinstance(tree_item, queue_item.DataCollectionQueueItem) or isinstance(
            tree_item, queue_item.XrayCenteringQueueItem
        ):

            if isinstance(tree_item, queue_item.XrayCenteringQueueItem):
                data_collection = tree_item.get_model().reference_image_collection
            else:
                data_collection = tree_item.get_model()

            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if data_collection.is_mesh():
                HWR.beamline.sample_view.select_shape(data_collection.grid)
                self._advanced_methods_widget.grid_treewidget.setCurrentItem(
                    self._grid_map[data_collection.grid]
                )

                self._path_template = data_collection.get_path_template()
                self._data_path_widget.update_data_model(self._path_template)

                self._acquisition_parameters = data_collection.acquisitions[
                    0
                ].acquisition_parameters
                self._acq_widget.update_data_model(
                    self._acquisition_parameters, self._path_template
                )
                # self.get_acquisition_widget().use_osc_start(True)
            self.dc_selected = True
        else:
            self.setDisabled(True)
        self.grid_treewidget_item_selection_changed()

    def _create_task(self, sample, shape, comments=None):
        """Creates tasks based on selected grids

        :param sample: selected sample object
        :type sample: SampleQueueItem
        :param shape: selected shape
        :type shape: GraphicsLib.GraphicsItem
        """

        tasks = []
        selected_grid = self.get_selected_shapes()[0]
        mesh_dc = self._create_dc_from_grid(sample, selected_grid)

        cpos = queue_model_objects.CentredPosition()
        cpos.snapshot_image = HWR.beamline.sample_view.get_snapshot()

        exp_type = str(self._advanced_methods_widget.method_combo.currentText())
        if exp_type == "MeshScan":
            tasks.append(mesh_dc)
        elif exp_type == "XrayCentering":
            xray_centering = queue_model_objects.XrayCentering(mesh_dc)
            tasks.append(xray_centering)
        elif exp_type == "MXPressO":
            optical_centering = queue_model_objects.OpticalCentring()
 
            dc_task = self.create_dc(sample, cpos=cpos)[0]
            dc_task.set_requires_centring(False)
            
            tasks.append(optical_centering)
            tasks.append(dc_task)

        else:
            logging.getLogger("GUI").warning(
                "Method %s does not exist in queue_model_objects" % exp_type
            )
        mesh_dc.run_processing_parallel = exp_type

        return tasks

    def shape_created(self, shape, shape_type):
        """If a grid is created then adds it to the treewidget.
           A binding between graphical grid and treewidget item is based
           on the self._grid_map

        :param shape: graphics object
        :type shape: GraphicsLib.GraphicsItem
        :param shape_type: type of the object (point, line, grid)
        :type shape_type: str
        """

        if shape_type == "Grid":
            self._advanced_methods_widget.grid_treewidget.clearSelection()
            grid_properties = shape.get_properties()
            info_str_list = []
            info_str_list.append(grid_properties["name"])
            info_str_list.append("%d" % grid_properties["num_lines"])
            info_str_list.append("%d" % grid_properties["num_images_per_line"])

            if not self.dc_selected:
                exp_time = max(
                    float(grid_properties["yOffset"] / 2.245),
                    self._acq_widget.exp_time_validator.bottom() + 0.00001,
                )
                self._acq_widget.acq_widget_layout.exp_time_ledit.setText(
                    "%.6f" % exp_time
                ) 

            grid_treewidget_item = QtImport.QTreeWidgetItem(
                self._advanced_methods_widget.grid_treewidget, info_str_list
            )
            self._grid_map[shape] = grid_treewidget_item

            if not self.dc_selected:
                grid_treewidget_item.setSelected(True)
                self.grid_treewidget_item_selection_changed()
                if self._acq_widget.acq_widget_layout.max_osc_range_cbx.isChecked():
                    self._acq_widget.update_osc_total_range_limits(
                        grid_properties["num_images_per_line"]
                    )
                else:
                    self.update_grid_osc_total_range()

    def shape_deleted(self, shape, shape_type):
        """Removes shape from QTreeWidget and self._grid_map

        :param shape: graphics object
        :type shape: QtGraphicsLib.GraphicsItem
        :param shape_type: type of the object (point, line, grid)
        :type shape_type: str
        """
        if self._grid_map.get(shape):
            treewidget_item_modelindex = self._advanced_methods_widget.grid_treewidget.indexFromItem(
                self._grid_map[shape]
            )
            self._advanced_methods_widget.grid_treewidget.takeTopLevelItem(
                treewidget_item_modelindex.row()
            )
            self._grid_map.pop(shape)

    def grid_treewidget_item_selection_changed(self):
        """Updates acquisition parameters based on the selected grid.
        """
        self.enable_grid_controls(False)

        for item in self._grid_map.items():
            grid = item[0]
            treewidget_item = item[1]

            if treewidget_item.isSelected():
                grid_properties = grid.get_properties()
                cell_count = (
                    grid_properties["num_lines"]
                    * grid_properties["num_images_per_line"]
                )
                self._acq_widget.acq_widget_layout.num_images_ledit.setText(
                    "%d" % cell_count
                )
                self._acq_widget.acq_widget_layout.first_image_ledit.setText(
                    "%d" % grid_properties["first_image_num"]
                )
                centred_point = grid.get_centred_position()
                self._acq_widget.acq_widget_layout.kappa_ledit.setText(
                    "%.2f" % float(centred_point.kappa)
                )
                self._acq_widget.acq_widget_layout.kappa_phi_ledit.setText(
                    "%.2f" % float(centred_point.kappa_phi)
                )
                self._advanced_methods_widget.hor_spacing_ledit.setText(
                    "%.2f" % (float(grid_properties["xOffset"]) * 1000)
                )
                self._advanced_methods_widget.ver_spacing_ledit.setText(
                    "%.2f" % (float(grid_properties["yOffset"]) * 1000)
                )

                treewidget_item.setText(3, str(grid_properties["num_lines"]))
                treewidget_item.setText(4, str(grid_properties["num_images_per_line"]))

                grid.setSelected(True)
                self.enable_grid_controls(True)
            else:
                grid.setSelected(False)

    def get_selected_shapes(self):
        """Returns selected grids

        :returns: selected grid objects
        """
        shapes = []
        for grid, grid_treewidget_item in self._grid_map.items():
            if grid_treewidget_item.isSelected():
                shapes.append(grid)
        return shapes

    def get_selected_grid_properties(self):
        """Returns properties of the selected grid

        :returns: dict with properties
        """

        for grid, grid_treewidget_item in self._grid_map.items():
            if grid_treewidget_item.isSelected():
                return grid.get_properties()

    def draw_grid_button_clicked(self):
        """Starts grid drawing
        """
        HWR.beamline.sample_view.create_grid(self.spacing)

    def remove_grid_button_clicked(self):
        """Removes selected grid
        """
        grid_to_delete = self.get_selected_shapes()[0]

        if grid_to_delete:
            HWR.beamline.sample_view.delete_shape(grid_to_delete)
            self._advanced_methods_widget.move_to_grid_button.setEnabled(False)

    def hor_spacing_changed(self, value):
        """Updates spacing of the selected grid
        """
        try:
            self.spacing[0] = (
                float(self._advanced_methods_widget.hor_spacing_ledit.text()) / 1000
            )
            self.set_spacing()
        except BaseException:
            pass

    def ver_spacing_changed(self, value):
        """Updates spacing of the selected grid
        """
        try:
            self.spacing[1] = (
                float(self._advanced_methods_widget.ver_spacing_ledit.text()) / 1000
            )
            self.set_spacing()
        except BaseException:
            pass

    def set_spacing(self):
        if 0 in self.spacing:
            return

        for grid, treewidget_item in self._grid_map.items():
            if treewidget_item.isSelected():
                grid.set_spacing(
                    self.spacing,
                    adjust_size=self._advanced_methods_widget.adjust_size_cbox.isChecked(),
                )
                grid_properties = grid.get_properties()

                treewidget_item.setText(1, str(grid_properties["num_lines"]))
                treewidget_item.setText(2, str(grid_properties["num_images_per_line"]))
                self._acq_widget.acq_widget_layout.num_images_ledit.setText(
                    str(
                        grid_properties["num_lines"]
                        * grid_properties["num_images_per_line"]
                    )
                )

    def move_to_grid(self):
        """Moves diffractometer to the center of the grid
        """
        grid = self.get_selected_shapes()[0]

        if grid:
            HWR.beamline.diffractometer.move_to_centred_position(
                grid.get_centred_position()
            )

    def method_combo_activated(self, index):
        self._task_node_name = self._advanced_methods_widget.method_combo.currentText()

    def overlay_toggled(self, state):
        """Toggles (on/off) overlay
        """
        grid = self.get_selected_shapes()[0]

        if grid:
            grid.set_display_overlay(state)

    def overlay_alpha_changed(self, alpha_value):
        """Changes the transperency of the grid
        """
        grid = self.get_selected_shapes()[0]

        if grid:
            grid.set_fill_alpha(alpha_value)

    def overlay_change_color(self):
        """Changes the default color (blue) of overlay
        """
        color = QtImport.QColorDialog.getColor()
        grid = self.get_selected_shapes()[0]

        if color.isValid() and grid:
            grid.set_base_color(color)

    def move_grid(self, direction):
        """Moves grid by one pix in selected direction

        :param direction: direction to move (right, left, up, down)
        :type direction: str
        """
        grid = self.get_selected_shapes()[0]

        if grid:
            grid.move_by_pix(direction)
            HWR.beamline.sample_view.update_grid_motor_positions(grid)

    def enable_grid_controls(self, state):
        """Enables grid controls if a grid is selectd
        """
        self._advanced_methods_widget.overlay_cbox.setEnabled(state)
        self._advanced_methods_widget.overlay_slider.setEnabled(state)
        self._advanced_methods_widget.overlay_color_button.setEnabled(state)
        self._advanced_methods_widget.move_to_grid_button.setEnabled(state)
        self._advanced_methods_widget.remove_grid_button.setEnabled(state)

        self._advanced_methods_widget.move_right_button.setEnabled(state)
        self._advanced_methods_widget.move_left_button.setEnabled(state)
        self._advanced_methods_widget.move_up_button.setEnabled(state)
        self._advanced_methods_widget.move_down_button.setEnabled(state)

        self._acq_widget.acq_widget_layout.max_osc_range_cbx.setEnabled(
            state and self._in_plate_mode
        )

        self.enable_widgets(state)
        self._acq_widget.emit_acq_parameters_changed()

    def grid_osc_range_ledit_changed(self, new_value):
        """Osc range per frame changed

        :param new_value: new value
        :type new_value: str
        """

        self.update_grid_osc_total_range()

    def grid_osc_total_range_ledit_changed(self, new_value):
        """Updates osc range per frame


        :param new_value: new value
        :type new_value: str
        """

        grid_properties = self.get_selected_grid_properties()
        if grid_properties:
            try:
                self._acq_widget.acq_widget_layout.osc_range_ledit.setText(
                    "%.4f"
                    % (float(new_value) / grid_properties["num_images_per_line"] - 1e-5)
                )
                self._acq_widget.emit_acq_parameters_changed()
            except BaseException:
                pass

    def update_grid_osc_total_range(self):
        """Updates osc range per line
        """

        grid_properties = self.get_selected_grid_properties()
        if grid_properties:
            self._acq_widget.acq_widget_layout.osc_total_range_ledit.setText(
                str(
                    float(self._acq_widget.acq_widget_layout.osc_range_ledit.text())
                    * grid_properties["num_images_per_line"]
                )
            )

    def set_osc_total_range(self, num_images=None, mesh=False):
        grid_properties = self.get_selected_grid_properties()
        if grid_properties:
            CreateTaskBase.set_osc_total_range(
                self, grid_properties["num_images_per_line"], mesh=True
            )
