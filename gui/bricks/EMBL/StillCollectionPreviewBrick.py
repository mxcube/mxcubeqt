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

import os
import numpy as np

import QtImport

from gui.BaseComponents import BaseWidget
from gui.utils import Colors
from widgets.matplot_widget import TwoDimenisonalPlotWidget

from HardwareRepository.HardwareObjects.Qt4_GraphicsLib import GraphicsView


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"
__category__ = "EMBL"


class StillCollectionPreviewBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beamline_setup_hwobj = None
        self.parallel_processing_hwobj = None

        # Internal values -----------------------------------------------------
        self.grid_properties = None
        self.info_dict = {"grid_cell": -1, "comp_cell": -1}
        self.params_dict = None
        self.results = None
        self.frame_num = 0
        self.score_type = "score"
        self.score_type_list = ("score", "spots_resolution", "spots_num")
        self.grid_table_item_fixed = False
        self.comp_table_item_fixed = False

        # Properties ----------------------------------------------------------
        self.add_property("cell_size", "integer", 22)
        self.add_property("hwobj_beamline_setup", "string", "/beamline-setup")
        # self.addProperty('hwobj_parallel_processing', 'string', '/parallel-processing')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.grid_widget = QtImport.QWidget(self)
        self.grid_table = QtImport.QTableWidget(self.grid_widget)
        self.grid_cell_label = QtImport.QLabel(
            "Selected grid cell: A1", self.grid_widget
        )
        self.grid_properties_combo = QtImport.QComboBox(self)

        self.inverted_rows_cbox = QtImport.QCheckBox("Inverted rows", self.grid_widget)
        self.image_tracking_cbox = QtImport.QCheckBox("Live update", self.grid_widget)
        self.score_type_combo = QtImport.QComboBox(self.grid_widget)
        self.save_hit_plot_button = QtImport.QPushButton(
            "Full grid view", self.grid_widget
        )

        self.comp_widget = QtImport.QWidget(self)
        self.comp_cell_label = QtImport.QLabel(
            "Selected compartment cell: A1", self.comp_widget
        )
        self.comp_table = QtImport.QTableWidget(self.comp_widget)
        self.hit_map_plot = TwoDimenisonalPlotWidget(self.comp_widget)

        self.grid_dialog = QtImport.QDialog(self)
        self.grid_graphics_view = GraphicsView()
        self.grid_graphics_base = GridViewGraphicsItem()
        self.grid_graphics_overlay = GridViewOverlayItem()
        # self.grid_graphics_view.scene().setSceneRect(0, 0, 2000, 2000)
        self.grid_graphics_view.scene().addItem(self.grid_graphics_base)
        self.grid_graphics_view.scene().addItem(self.grid_graphics_overlay)
        self.save_grid_view_button = QtImport.QPushButton("Save", self.grid_dialog)
        self.save_grid_view_button.setFixedWidth(100)

        # Layout --------------------------------------------------------------
        _grid_vlayout = QtImport.QVBoxLayout(self.grid_widget)
        _grid_vlayout.addWidget(self.grid_cell_label)
        _grid_vlayout.addWidget(self.grid_table)
        _grid_vlayout.addStretch()
        _grid_vlayout.addWidget(self.grid_properties_combo)
        _grid_vlayout.addWidget(self.inverted_rows_cbox)
        _grid_vlayout.addWidget(self.image_tracking_cbox)
        _grid_vlayout.addWidget(self.score_type_combo)
        _grid_vlayout.addWidget(self.save_hit_plot_button)
        _grid_vlayout.setSpacing(2)
        _grid_vlayout.setContentsMargins(2, 2, 2, 2)

        _comp_vlayout = QtImport.QVBoxLayout(self.comp_widget)
        _comp_vlayout.addWidget(self.comp_cell_label)
        _comp_vlayout.addWidget(self.comp_table)
        _comp_vlayout.addWidget(self.hit_map_plot)
        _comp_vlayout.setSpacing(2)
        _comp_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QHBoxLayout(self)
        _main_vlayout.addWidget(self.grid_widget)
        _main_vlayout.addWidget(self.comp_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_grid_dialog_vlayout = QtImport.QVBoxLayout(self.grid_dialog)
        _main_grid_dialog_vlayout.addWidget(self.grid_graphics_view)
        _main_grid_dialog_vlayout.addWidget(self.save_grid_view_button)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.grid_table.cellClicked.connect(self.grid_cell_clicked)
        self.grid_table.cellEntered.connect(self.grid_cell_entered)

        self.comp_table.cellClicked.connect(self.comp_cell_clicked)
        self.comp_table.cellEntered.connect(self.comp_cell_entered)
        self.grid_properties_combo.activated.connect(self.grid_properties_combo_changed)
        self.score_type_combo.activated.connect(self.score_type_changed)
        self.save_hit_plot_button.clicked.connect(self.save_hit_plot)
        self.hit_map_plot.mouseMovedSignal.connect(self.hit_map_mouse_moved)
        self.grid_graphics_view.mouseMovedSignal.connect(self.grid_view_mouse_moved)
        self.save_grid_view_button.clicked.connect(self.save_grid_view)

        # Other ---------------------------------------------------------------
        self.grid_table.setEditTriggers(QtImport.QAbstractItemView.NoEditTriggers)
        self.grid_table.setHorizontalScrollBarPolicy(QtImport.Qt.ScrollBarAlwaysOff)
        self.grid_table.setVerticalScrollBarPolicy(QtImport.Qt.ScrollBarAlwaysOff)
        self.grid_table.setMouseTracking(True)

        self.comp_table.setEditTriggers(QtImport.QAbstractItemView.NoEditTriggers)
        self.comp_table.setHorizontalScrollBarPolicy(QtImport.Qt.ScrollBarAlwaysOff)
        self.comp_table.setVerticalScrollBarPolicy(QtImport.Qt.ScrollBarAlwaysOff)
        self.comp_table.setMouseTracking(True)

        for score_type in ("Score", "Resolution", "Number of spots"):
            self.score_type_combo.addItem(score_type)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "hwobj_beamline_setup":
            if self.parallel_processing_hwobj is not None:
                self.parallel_processing_hwobj.disconnect(
                    "processingStarted", self.processing_started
                )
                self.parallel_processing_hwobj.disconnect(
                    "processingFinished", self.processing_finished
                )
                self.parallel_processing_hwobj.disconnect(
                    "processingFailed", self.processing_failed
                )
                self.parallel_processing_hwobj.disconnect(
                    "processingFrame", self.processing_frame_changed
                )
            self.beamline_setup_hwobj = self.get_hardware_object(new_value)
            self.parallel_processing_hwobj = (
                self.beamline_setup_hwobj.parallel_processing_hwobj
            )

            if self.parallel_processing_hwobj is not None:
                self.parallel_processing_hwobj.connect(
                    "processingStarted", self.processing_started
                )
                self.parallel_processing_hwobj.connect(
                    "processingFinished", self.processing_finished
                )
                self.parallel_processing_hwobj.connect(
                    "processingFailed", self.processing_failed
                )
                self.parallel_processing_hwobj.connect(
                    "processingFrame", self.processing_frame_changed
                )
                for (
                    grid_property
                ) in self.parallel_processing_hwobj.get_available_grid_properties():
                    self.grid_properties_combo.addItem(str(grid_property))
                self.grid_properties_combo.blockSignals(True)
                self.grid_properties_combo.setCurrentIndex(0)
                self.grid_properties_combo.blockSignals(False)
                self.grid_properties = (
                    self.parallel_processing_hwobj.get_current_grid_properties()
                )
                self.init_gui()
                self.grid_graphics_base.init_item(self.grid_properties)
                self.grid_graphics_overlay.init_item(self.grid_properties)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def init_gui(self):
        self.image_tracking_cbox.setChecked(True)
        self.inverted_rows_cbox.setChecked(self.grid_properties["inverted_rows"])
        self.grid_table.setColumnCount(self.grid_properties["grid_num_col"])
        self.grid_table.setRowCount(self.grid_properties["grid_num_row"])

        for col in range(self.grid_properties["grid_num_col"]):
            temp_header_item = QtImport.QTableWidgetItem("%d" % (col + 1))
            self.grid_table.setHorizontalHeaderItem(col, temp_header_item)
            self.grid_table.setColumnWidth(col, self["cell_size"])

        for row in range(self.grid_properties["grid_num_row"]):
            temp_header_item = QtImport.QTableWidgetItem(chr(65 + row))
            self.grid_table.setVerticalHeaderItem(row, temp_header_item)
            self.grid_table.setRowHeight(row, self["cell_size"])

        for col in range(self.grid_properties["grid_num_col"]):
            for row in range(self.grid_properties["grid_num_row"]):
                temp_item = QtImport.QTableWidgetItem()
                self.grid_table.setItem(row, col, temp_item)

        table_width = self["cell_size"] * (self.grid_properties["grid_num_col"] + 1) + 4
        table_height = (
            self["cell_size"] * (self.grid_properties["grid_num_row"] + 1) + 4
        )
        self.grid_table.setFixedWidth(table_width)
        self.grid_table.setFixedHeight(table_height)

        self.comp_table.setColumnCount(self.grid_properties["comp_num_col"])
        self.comp_table.setRowCount(self.grid_properties["comp_num_row"])

        for col in range(self.grid_properties["comp_num_col"]):
            temp_header_item = QtImport.QTableWidgetItem("%d" % (col + 1))
            self.comp_table.setHorizontalHeaderItem(col, temp_header_item)
            self.comp_table.setColumnWidth(col, self["cell_size"])

        for row in range(self.grid_properties["comp_num_row"]):
            temp_header_item = QtImport.QTableWidgetItem(chr(65 + row))
            self.comp_table.setVerticalHeaderItem(row, temp_header_item)
            self.comp_table.setRowHeight(row, self["cell_size"])

        for col in range(self.grid_properties["comp_num_col"]):
            for row in range(self.grid_properties["comp_num_row"]):
                temp_item = QtImport.QTableWidgetItem()
                self.comp_table.setItem(row, col, temp_item)

        table_width = self["cell_size"] * (self.grid_properties["comp_num_col"] + 1) + 7
        table_height = (
            self["cell_size"] * (self.grid_properties["comp_num_row"] + 1) + 7
        )
        self.comp_table.setFixedWidth(table_width)
        self.comp_table.setFixedHeight(table_height)

        for score_type in self.score_type_list:
            self.hit_map_plot.add_curve(
                score_type,
                np.array([]),
                np.array([]),
                linestyle="None",
                label=score_type,
                color="m",
                marker="s",
            )
        self.hit_map_plot.hide_all_curves()
        self.hit_map_plot.show_curve(self.score_type)

    def save_hit_plot(self):
        self.grid_dialog.show()

    def save_grid_view(self):
        file_types = "PNG (*.png)"
        filename = str(
            QtImport.QFileDialog.getSaveFileName(
                self,
                "Choose a filename to save under",
                os.path.expanduser("~"),
                file_types,
            )
        )

        filename += ".png"
        image = QtImport.QImage(
            self.grid_graphics_view.scene().sceneRect().size().toSize(),
            QtImport.QImage.Format_ARGB32,
        )
        image.fill(QtImport.Qt.white)
        image_painter = QtImport.QPainter(image)
        self.grid_graphics_view.render(image_painter)
        image_painter.end()
        image.save(filename)

    def grid_cell_clicked(self, row, col):
        self.grid_table_item_fixed = not self.grid_table_item_fixed

    def grid_cell_entered(self, row, col):
        if not self.grid_table_item_fixed:
            self.info_dict["grid_cell"] = (
                row * self.grid_properties["grid_num_row"] + col
            )
            self.grid_cell_label.setText(
                "Current grid cell: %s%d" % (chr(65 + row), col + 1)
            )
            self.update_comp_table()

            if self.params_dict:
                grid_cell = row * self.grid_properties["grid_num_row"] + col

                start_index = (
                    grid_cell
                    * self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    * self.params_dict["num_images_per_trigger"]
                )
                end_index = min(
                    start_index
                    + self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    * self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )

                index = self.results[self.score_type].max()

                filename = self.params_dict["template"] % (
                    self.params_dict["run_number"],
                    index,
                )
                try:
                    self.beamline_setup_hwobj.image_tracking_hwobj.load_image(filename)
                except BaseException:
                    pass

    def comp_cell_clicked(self, row, col):
        self.comp_table_item_fixed = not self.comp_table_item_fixed

    def comp_cell_entered(self, row, col):
        if not self.comp_table_item_fixed:
            self.comp_cell_label.setText(
                "Current compartment cell: %s%d" % (chr(65 + row), col + 1)
            )

            if self.params_dict is not None:
                start_index = (
                    self.info_dict["grid_cell"]
                    * self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    + row * self.grid_properties["comp_num_row"]
                    + col
                ) * self.params_dict["num_images_per_trigger"]
                end_index = min(
                    start_index + self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size,
                )

                if self.results is not None:
                    if start_index < self.results[self.score_type].size:
                        data = {
                            self.score_type: self.results[self.score_type][
                                start_index:end_index
                            ],
                            "x_array": np.linspace(
                                start_index,
                                end_index,
                                end_index - start_index,
                                dtype=np.int32,
                            ),
                        }
                        self.hit_map_plot.update_curves(data)
                        self.hit_map_plot.set_x_axis_limits(
                            (start_index - 0.5, end_index + 0.5)
                        )
                        self.hit_map_plot.adjust_axes(self.score_type)

    def grid_properties_combo_changed(self, index):
        self.parallel_processing_hwobj.set_current_grid_index(index)
        self.grid_properties = (
            self.parallel_processing_hwobj.get_current_grid_properties()
        )
        self.init_gui()
        self.grid_graphics_base.init_item(self.grid_properties)
        self.grid_graphics_overlay.init_item(self.grid_properties)

    def score_type_changed(self, index):
        self.score_type = self.score_type_list[index]

    def hit_map_mouse_moved(self, pos_x, pos_y):
        if self.params_dict is not None:
            filename = self.params_dict["template"] % (
                self.params_dict["run_number"],
                int(pos_x),
            )
            try:
                self.beamline_setup_hwobj.image_tracking_hwobj.load_image(filename)
            except BaseException:
                pass

    def grid_view_mouse_moved(self, pos_x, pos_y):
        pass

    def processing_started(self, params_dict, raw_results, aligned_results):
        self.results = raw_results
        self.params_dict = params_dict
        self.hit_map_plot.set_x_axis_limits(
            (0, self.params_dict["num_images_per_trigger"])
        )

        self.grid_graphics_base.set_results(params_dict, raw_results)
        self.grid_graphics_overlay.set_results(params_dict, raw_results)

    def processing_finished(self):
        # self.info_dict["grid_cell"] = -1
        self.info_dict["comp_cell"] = -1
        self.processing_frame_changed(self.params_dict["images_num"])

    def processing_failed(self):
        pass

    def processing_frame_changed(self, frame_num):
        self.frame_num = frame_num
        self.update_gui()
        self.grid_graphics_view.scene().update()

    def update_gui(self):
        if not self.image_tracking_cbox.isChecked():
            return

        self.info_dict["frame_num"] = self.frame_num
        self.info_dict["comp_num"] = (
            self.frame_num / self.params_dict["num_images_per_trigger"]
        )

        grid_cell = (
            self.info_dict["comp_num"]
            / self.grid_properties["comp_num_col"]
            / self.grid_properties["comp_num_row"]
        )

        if self.info_dict["grid_cell"] != grid_cell:
            self.info_dict["grid_cell"] = grid_cell
            self.info_dict["comp_cell"] = -1
            self.update_grid_table()

        comp_cell = (
            self.frame_num
            - grid_cell
            * self.grid_properties["comp_num_col"]
            * self.grid_properties["comp_num_row"]
            * self.params_dict["num_images_per_trigger"]
        ) / self.params_dict["num_images_per_trigger"]

        if self.info_dict["comp_cell"] != comp_cell:
            self.info_dict["comp_cell"] = comp_cell
            self.update_comp_table()

    def update_grid_table(self):
        if self.params_dict is None:
            return

        for row in range(self.grid_properties["grid_num_row"]):
            for col in range(self.grid_properties["grid_num_col"]):
                grid_table_item = self.grid_table.item(row, col)
                grid_cell = row * self.grid_properties["grid_num_row"] + col

                start_index = (
                    grid_cell
                    * self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    * self.params_dict["num_images_per_trigger"]
                )
                end_index = min(
                    start_index
                    + self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    * self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )

                color = Colors.LIGHT_GRAY
                if grid_cell == self.info_dict["grid_cell"]:
                    color = Colors.DARK_GREEN
                elif start_index < self.results[self.score_type].size:
                    if self.results[self.score_type][start_index:end_index].max() > 0:
                        color = Colors.LIGHT_BLUE
                    else:
                        color = Colors.WHITE
                grid_table_item.setBackground(color)

    def update_comp_table(self):
        if self.params_dict is None:
            return

        for row in range(self.grid_properties["comp_num_row"]):
            for col in range(self.grid_properties["comp_num_col"]):

                if self.inverted_rows_cbox.isChecked() and row % 2:
                    table_col = self.grid_properties["comp_num_col"] - col - 1
                else:
                    table_col = col

                comp_table_item = self.comp_table.item(row, table_col)
                start_index = (
                    self.info_dict["grid_cell"]
                    * self.grid_properties["comp_num_col"]
                    * self.grid_properties["comp_num_row"]
                    * self.params_dict["num_images_per_trigger"]
                    + (row * self.grid_properties["comp_num_row"] + col)
                    * self.params_dict["num_images_per_trigger"]
                )
                # self.grid_properties["comp_num_col"]
                end_index = min(
                    start_index + self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )
                color = Colors.LIGHT_GRAY
                if (
                    self.info_dict["comp_cell"]
                    == row * self.grid_properties["comp_num_row"] + col
                ):
                    color = Colors.DARK_GREEN
                elif start_index < self.results[self.score_type].size:
                    if start_index != end_index:
                        if (
                            self.results[self.score_type][start_index:end_index].max()
                            > 0
                        ):
                            color = Colors.LIGHT_BLUE
                        else:
                            color = Colors.WHITE
                    else:
                        if self.results[self.score_type][start_index] > 0:
                            color = Colors.LIGHT_BLUE
                        else:
                            color = Colors.WHITE
                comp_table_item.setBackground(color)


class GridViewGraphicsItem(QtImport.QGraphicsItem):
    def __init__(self):
        """
        :param position_x: x coordinate in the scene
        :type position_x: int
        :param position_y: y coordinate in the scene
        :type position_y: int
        """

        QtImport.QGraphicsItem.__init__(self)
        self.index = None
        self.rect = QtImport.QRectF(0, 0, 0, 0)
        self.setPos(10, 10)

        self.custom_pen = QtImport.QPen(QtImport.Qt.SolidLine)
        self.custom_pen.setWidth(1)
        self.custom_pen.setColor(QtImport.Qt.lightGray)

        self.custom_brush = QtImport.QBrush(QtImport.Qt.SolidPattern)
        brush_color = QtImport.Qt.white
        self.custom_brush.setColor(brush_color)

        self.results = None
        self.debug_hit_limit = 1e9
        self.no_compartments_x = None
        self.no_compartments_y = None
        self.no_holes_x = None
        self.no_holes_y = None
        self.offset_hole = 2
        self.offset_compartment = 10

        self.size_hole = None
        self.size_compartment_x = None
        self.size_compartment_y = None
        self.size_chip_x = None
        self.size_chip_y = None
        self.images_per_crystal = 1

    def boundingRect(self):
        """Returns adjusted rect

        :returns: QRect
        """
        return self.rect.adjusted(0, 0, 40, 40)

    def paint(self, painter, option, widget):
        """Main beam painter method
           Draws ellipse or rectangle with a cross in the middle
        """
        if self.size_hole:
            self.custom_brush.setColor(QtImport.Qt.lightGray)
            painter.setBrush(self.custom_brush)
            for compartment_y in range(self.no_compartments_y):
                for compartment_x in range(self.no_compartments_x):
                    for hole_y in range(1, self.no_holes_y + 1):
                        for hole_x in range(1, self.no_holes_x + 1):
                            # compartment_y = self.no_compartments_y - compartment_y + 1
                            hole_y = self.no_holes_y - hole_y + 1
                            corner_x = (
                                compartment_x
                                * (self.size_compartment_x + self.offset_compartment)
                            ) + (hole_x * (self.size_hole + self.offset_hole))
                            corner_y = (
                                compartment_y
                                * (self.size_compartment_y + self.offset_compartment)
                            ) + (hole_y * (self.size_hole + self.offset_hole))
                            painter.drawRect(
                                corner_x, corner_y, self.size_hole, self.size_hole
                            )

    def init_item(self, params_dict, results=None):
        self.results = results
        self.item_initialized = False

        self.no_compartments_x = params_dict["grid_num_col"]
        self.no_compartments_y = params_dict["grid_num_row"]
        self.no_holes_x = params_dict["comp_num_row"]
        self.no_holes_y = params_dict["comp_num_col"]

        self.size_hole = 2000 / (
            self.no_compartments_x
            * (self.offset_compartment + self.no_holes_x * self.offset_hole)
        )
        self.size_compartment_x = (self.size_hole + self.offset_hole) * self.no_holes_x
        self.size_compartment_y = (self.size_hole + self.offset_hole) * self.no_holes_y
        self.size_chip_x = (self.size_compartment_x + self.offset_compartment) * (
            self.no_compartments_x + 0.5
        )
        self.size_chip_y = (self.size_compartment_y + self.offset_compartment) * (
            self.no_compartments_y + 0.5
        )

        self.scene().setSceneRect(0, 0, self.size_chip_x + 10, self.size_chip_y + 10)

    def set_results(self, params_dict, results):
        self.images_per_crystal = params_dict["num_images_per_trigger"]
        self.results = results


class GridViewOverlayItem(GridViewGraphicsItem):
    def __init__(self):
        GridViewGraphicsItem.__init__(self)

    def calc_hole_coordinates(self, imgno):
        imgno = int(imgno)
        image_number = imgno // self.images_per_crystal

        compartments_serial = image_number // (self.no_holes_x * self.no_holes_y)
        holes_serial = image_number % (self.no_holes_x * self.no_holes_y)
        timepoint_serial = imgno % self.images_per_crystal

        compartment_x = compartments_serial % self.no_compartments_x
        compartment_y = compartments_serial // self.no_compartments_x
        hole_x = holes_serial % self.no_holes_x + 1
        hole_y = holes_serial // self.no_holes_x + 1
        timepoint_x = timepoint_serial % 2 + 1
        timepoint_y = timepoint_serial // 2 + 1

        if not hole_y & 1:
            hole_x = self.no_holes_x - hole_x + 1

        return (
            compartments_serial,
            holes_serial,
            timepoint_serial,
            compartment_x,
            compartment_y,
            hole_x,
            hole_y,
            timepoint_x,
            timepoint_y,
        )

    def paint(self, painter, option, widget):
        self.custom_brush.setColor(QtImport.Qt.blue)
        painter.setBrush(self.custom_brush)

        def draw_hole_timeseries(
            compartment_x, compartment_y, hole_x, hole_y, subpixel_x, subpixel_y
        ):
            # compartment_y = self.no_compartments_y - compartment_y +1
            # hole_y        = self.no_holes_y - hole_y +1
            # subpixel_y    = self.no_subpixels_y - subpixel_y +1

            corner_x = (
                compartment_x * (self.size_compartment_x + self.offset_compartment)
                + (hole_x * (self.size_hole + self.offset_hole))
                + ((subpixel_x - 1) * self.size_hole)
            )

            corner_y = (
                compartment_y * (self.size_compartment_y + self.offset_compartment)
                + (hole_y * (self.size_hole + self.offset_hole))
                + ((subpixel_y - 1) * self.size_hole)
            )

            painter.drawRect(corner_x, corner_y, self.size_hole, self.size_hole)

        if self.results is not None:
            hitlist = np.where(self.results["score"] > 0)[0]
            for hit in hitlist:
                compartments_serial, holes_serial, timepoint_serial, compartment_x, compartment_y, hole_x, hole_y, timepoint_x, timepoint_y = self.calc_hole_coordinates(
                    hit
                )
                if timepoint_y <= 1:
                    draw_hole_timeseries(
                        compartment_x,
                        compartment_y,
                        hole_x,
                        hole_y,
                        timepoint_x,
                        timepoint_y,
                    )
