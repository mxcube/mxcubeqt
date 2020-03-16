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

"""StillCollectionPreviewBrick"""

import os
import numpy as np

from gui.BaseComponents import BaseWidget
from gui.utils import Colors, QtImport
from gui.widgets.pyqtgraph_widget import PlotWidget

from HardwareRepository.HardwareObjects.QtGraphicsLib import GraphicsView

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "EMBL"


class StillCollectionPreviewBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.current_chip_config = None
        self.info_dict = {
           "collect_grid_cell": -1,
           "collect_comp_cell": -1,
           "processing_grid_cell": -1,
           "processing_comp_cell": -1
        }
        self.params_dict = None
        self.results = None
        self.collect_frame_num = 0
        self.processing_frame_num = 0
        self.score_type = "score"
        self.score_type_list = ("score", "spots_resolution", "spots_num")
        self.grid_table_item_fixed = False
        self.comp_table_item_fixed = False

        # Properties ----------------------------------------------------------
        self.add_property("cell_size", "integer", 22)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.grid_widget = QtImport.QWidget(self)
        self.grid_table = QtImport.QTableWidget(self.grid_widget)
        self.grid_cell_label = QtImport.QLabel(
            "Selected grid cell: A1", self.grid_widget
        )
        self.chip_config_combo = QtImport.QComboBox(self)

        self.inverted_rows_cbox = QtImport.QCheckBox("Inverted rows", self.grid_widget)
        self.image_tracking_cbox = QtImport.QCheckBox("Live update", self.grid_widget)
        self.score_type_combo = QtImport.QComboBox(self.grid_widget)
        self.show_grid_dialog_button = QtImport.QPushButton(
            "Full grid view", self.grid_widget
        )

        self.comp_widget = QtImport.QWidget(self)
        self.comp_cell_label = QtImport.QLabel(
            "Selected compartment cell: A1", self.comp_widget
        )
        self.comp_table = QtImport.QTableWidget(self.comp_widget)
        self.hit_map_plot = PlotWidget(self.comp_widget)

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
        _grid_vlayout.addWidget(self.chip_config_combo)
        _grid_vlayout.addWidget(self.inverted_rows_cbox)
        _grid_vlayout.addWidget(self.image_tracking_cbox)
        _grid_vlayout.addWidget(self.score_type_combo)
        _grid_vlayout.addWidget(self.show_grid_dialog_button)
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
        self.chip_config_combo.activated.connect(self.grid_properties_combo_changed)
        self.score_type_combo.activated.connect(self.score_type_changed)
        self.show_grid_dialog_button.clicked.connect(self.show_grid_dialog)
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

        HWR.beamline.online_processing.connect(
            "processingStarted", self.processing_started
        )
        HWR.beamline.online_processing.connect(
            "processingFinished", self.processing_finished
        )
        HWR.beamline.online_processing.connect(
            "processingFailed", self.processing_failed
        )
        HWR.beamline.online_processing.connect(
            "processingFrame", self.processing_frame_changed
        )
        self.current_grid_properties = (
            HWR.beamline.online_processing.get_current_grid_properties()
        )

        self.grid_properties_combo.blockSignals(True)
        for prop in HWR.beamline.online_processing.get_available_grid_properties():
            self.grid_properties_combo.addItem(str(prop))
        self.grid_properties_combo.setCurrentIndex(0)
        self.grid_properties_combo.blockSignals(False)

        self.init_gui()
        self.grid_graphics_base.init_item(self.current_chip_config)
        self.grid_graphics_overlay.init_item(self.current_chip_config)

    def init_gui(self):
        """
        Inits gui
        :return: None
        """
        self.image_tracking_cbox.setChecked(True)
        self.inverted_rows_cbox.setChecked(
            self.current_chip_config["inverted_rows"]
        )
        self.grid_table.setColumnCount(self.current_chip_config["num_comp_h"])
        self.grid_table.setRowCount(self.current_chip_config["num_comp_v"])

        for col in range(self.current_chip_config["num_comp_h"]):
            temp_header_item = QtImport.QTableWidgetItem("%d" % (col + 1))
            self.grid_table.setHorizontalHeaderItem(col, temp_header_item)
            self.grid_table.setColumnWidth(col, self["cell_size"])

        for row in range(self.current_chip_config["num_comp_v"]):
            temp_header_item = QtImport.QTableWidgetItem(chr(65 + row))
            self.grid_table.setVerticalHeaderItem(row, temp_header_item)
            self.grid_table.setRowHeight(row, self["cell_size"])

        for col in range(self.current_chip_config["num_comp_h"]):
            for row in range(self.current_chip_config["num_comp_v"]):
                temp_item = QtImport.QTableWidgetItem()
                self.grid_table.setItem(row, col, temp_item)

        table_width = (
            self["cell_size"] * (self.current_chip_config["num_comp_h"] + 1) + 4
        )
        table_height = (
            self["cell_size"] * (self.current_chip_config["num_comp_v"] + 1) + 4
        )
        self.grid_table.setFixedWidth(table_width)
        self.grid_table.setFixedHeight(table_height)

        self.comp_table.setColumnCount(self.current_chip_config["num_crystal_h"])
        self.comp_table.setRowCount(self.current_chip_config["num_crystal_v"])

        for col in range(self.current_chip_config["num_crystal_h"]):
            temp_header_item = QtImport.QTableWidgetItem("%d" % (col + 1))
            self.comp_table.setHorizontalHeaderItem(col, temp_header_item)
            self.comp_table.setColumnWidth(col, self["cell_size"])

        for row in range(self.current_chip_config["num_crystal_v"]):
            temp_header_item = QtImport.QTableWidgetItem(chr(65 + row))
            self.comp_table.setVerticalHeaderItem(row, temp_header_item)
            self.comp_table.setRowHeight(row, self["cell_size"])

        for col in range(self.current_chip_config["num_crystal_h"]):
            for row in range(self.current_chip_config["num_crystal_v"]):
                temp_item = QtImport.QTableWidgetItem()
                self.comp_table.setItem(row, col, temp_item)

        table_width = (
            self["cell_size"] * (self.current_chip_config["num_crystal_h"] + 1) + 7
        )
        table_height = (
            self["cell_size"] * (self.current_chip_config["num_crystal_v"] + 1) + 7
        )
        self.comp_table.setFixedWidth(table_width + 10)
        self.comp_table.setFixedHeight(table_height)

        self.hit_map_plot.setFixedWidth(table_width)
        self.hit_map_plot.setFixedHeight(200)

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

    def show_grid_dialog(self):
        """
        Opens dialog with full grid view
        :return: None
        """
        self.grid_dialog.show()

    def save_grid_view(self):
        """
        Saves grid view in png file
        :return: None
        """
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
        """
        Fixes grid cell
        :param row: int
        :param col: int
        :return: None
        """
        self.grid_table_item_fixed = not self.grid_table_item_fixed

    def grid_cell_entered(self, row, col):
        """
        Updates grid view and loads image
        :param row: int
        :param col: int
        :return: None
        """
        if not self.grid_table_item_fixed and not self.image_tracking_cbox.isChecked():
            self.info_dict["processing_grid_cell"] = (
                row * self.current_chip_config["num_comp_v"] + col
            )
            self.grid_cell_label.setText(
                "Current grid cell: %s%d" % (chr(65 + row), col + 1)
            )
            self.update_comp_table()

            if self.params_dict:
                grid_cell = row * self.current_chip_config["num_comp_v"] + col

                start_index = (
                    grid_cell
                    * self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    * self.params_dict["num_images_per_trigger"]
                )
                end_index = min(
                    start_index
                    + self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    * self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )

                if start_index < self.results[self.score_type].size:
                    index = start_index + np.argmax(
                        self.results[self.score_type][start_index:end_index]
                    )

                    filename = self.params_dict["template"] % (
                        self.params_dict["run_number"],
                        index + self.params_dict["first_image_num"],
                    )
                    try:
                        HWR.beamline.image_tracking.load_image(filename)
                    except BaseException:
                        pass

    def comp_cell_clicked(self, row, col):
        """
        Fixes or release com table item
        :param row: int
        :param col: int
        :return: None
        """
        self.comp_table_item_fixed = not self.comp_table_item_fixed

    def comp_cell_entered(self, row, col):
        """
        Method called when compartm. cell entered
        :param row: int
        :param col: int
        :return: None
        """
        if not self.comp_table_item_fixed and not self.image_tracking_cbox.isChecked():
            self.comp_cell_label.setText(
                "Current compartment cell: %s%d" % (chr(65 + row), col + 1)
            )

            if self.params_dict is not None:
                start_index = (
                    self.info_dict["processing_grid_cell"]
                    * self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    + row * self.current_chip_config["num_crystal_h"]
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
                        #self.hit_map_plot.adjust_axes(self.score_type)
                        self.hit_map_plot.autoscale_axes()

                        index = start_index + np.argmax(
                            self.results[self.score_type][start_index:end_index]
                        )

                        filename = self.params_dict["template"] % (
                            self.params_dict["run_number"],
                            index + self.params_dict["first_image_num"],
                        )
                        try:
                            HWR.beamline.image_tracking.load_image(filename)
                        except BaseException:
                            pass

    def grid_properties_combo_changed(self, index):
        """
        Redraws grid view based on the selected grid property
        :param index: int
        :return: None
        """
        HWR.beamline.online_processing.set_current_grid_index(index)
        self.current_grid_properties = (
            HWR.beamline.online_processing.get_current_grid_properties()
        )
        self.init_gui()
        self.grid_graphics_base.init_item(self.current_chip_config)
        self.grid_graphics_overlay.init_item(self.current_chip_config)

    def score_type_changed(self, index):
        """
        Updates plots based on the selected score type
        :param index: int
        :return: None
        """
        self.score_type = self.score_type_list[index]

    def hit_map_mouse_moved(self, pos_x, pos_y):
        """
        Loads image in ADxV based on mouse move
        :param pos_x: float
        :param pos_y: float
        :return: None
        """
        if self.params_dict is not None:
            filename = self.params_dict["template"] % (
                self.params_dict["run_number"],
                int(pos_x),
            )
            try:
                HWR.beamline.image_tracking.load_image(filename)
            except BaseException:
                pass

    def grid_view_mouse_moved(self, pos_x, pos_y):
        """
        Not implemented yet
        :param pos_x:
        :param pos_y:
        :return:
        """
        return

    def processing_started(self, params_dict, raw_results, aligned_results):
        """
        Processing started event. Cleans graphs
        :param params_dict: dict with processing parameters
        :param raw_results: dict with one dimension numpy arrays
        :param aligned_results: dict with multi dimensional numpy arrays
        :return: None
        """
        self.image_tracking_cbox.setChecked(True)

        self.results = raw_results
        self.params_dict = params_dict
        self.hit_map_plot.set_x_axis_limits(
            (0, self.params_dict["num_images_per_trigger"])
        )

        self.grid_graphics_base.set_results(params_dict, raw_results)
        self.grid_graphics_overlay.set_results(params_dict, raw_results)

    def processing_finished(self):
        """
        Updates grid view last time
        :return: None
        """
        self.image_tracking_cbox.setChecked(False)

        self.info_dict["processing_comp_cell"] = -1
        self.processing_frame_changed(self.params_dict["images_num"])

    def processing_failed(self):
        """
        Not implemented
        :return: None
        """
        return

    def processing_frame_changed(self, frame_num):
        """
        Redraws grid view
        :param frame_num: int
        :return: None
        """
        self.processing_frame_num = frame_num
        self.update_gui()
        self.grid_graphics_view.scene().update()

    def collect_frame_changed(self, frame_num):
        """
        Redraws grid view
        :param frame_num: int
        :return: None
        """
        self.collect_frame_num = frame_num
        self.update_gui()
        self.grid_graphics_view.scene().update()

    def update_gui(self):
        """
        Updates gui
        :return: None
        """
        if not self.image_tracking_cbox.isChecked():
            return

        self.info_dict["collect_comp_num"] = (
            self.collect_frame_num / self.params_dict["num_images_per_trigger"]
        )
        self.info_dict["processing_comp_num"] = (
            self.processing_frame_num / self.params_dict["num_images_per_trigger"]
        )

        collect_grid_cell = (
            self.info_dict["collect_comp_num"]
            / self.current_chip_config["num_crystal_v"]
            / self.current_chip_config["num_crystal_h"]
        )
        processing_grid_cell = (
            self.info_dict["processing_comp_num"]
            / self.current_chip_config["num_crystal_v"]
            / self.current_chip_config["num_crystal_h"]
        )

        if self.info_dict["collect_grid_cell"] != collect_grid_cell:
            self.info_dict["collect_grid_cell"] = collect_grid_cell
            self.info_dict["collect_comp_cell"] = -1

        if self.info_dict["processing_grid_cell"] != processing_grid_cell:
            self.info_dict["processing_grid_cell"] = processing_grid_cell
            self.info_dict["processing_comp_cell"] = -1
            self.update_grid_table()

        

        collect_comp_cell = (
            self.collect_frame_num
            - collect_grid_cell
            * self.current_chip_config["num_crystal_v"]
            * self.current_chip_config["num_crystal_h"]
            * self.params_dict["num_images_per_trigger"]
        ) / self.params_dict["num_images_per_trigger"]        

        processing_comp_cell = (
            self.processing_frame_num
            - processing_grid_cell
            * self.current_chip_config["num_crystal_v"]
            * self.current_chip_config["num_crystal_h"]
            * self.params_dict["num_images_per_trigger"]
        ) / self.params_dict["num_images_per_trigger"]

        self.info_dict["collect_comp_cell"] = collect_comp_cell

        if self.info_dict["processing_comp_cell"] != processing_comp_cell:
            self.info_dict["processing_comp_cell"] = processing_comp_cell
            self.update_comp_table()

        self.update_stats()

    def update_grid_table(self):
        """
        Updates grid table
        :return: None
        """
        if self.params_dict is None or not self.image_tracking_cbox.isChecked():
            return

        for row in range(self.current_chip_config["num_comp_v"]):
            for col in range(self.current_chip_config["num_comp_h"]):
                grid_table_item = self.grid_table.item(row, col)
                grid_cell = row * self.current_chip_config["num_comp_v"] + col

                start_index = (
                    grid_cell
                    * self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    * self.params_dict["num_images_per_trigger"]
                )
                end_index = min(
                    start_index
                    + self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    * self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )

                color = Colors.LIGHT_GRAY
                if grid_cell == self.info_dict["processing_grid_cell"]:
                    color = Colors.DARK_GREEN
                elif grid_cell == self.info_dict["collect_grid_cell"]:
                    color = Colors.LIGHT_ORANGE
                elif start_index < self.results[self.score_type].size:
                    if self.results[self.score_type][start_index:end_index].max() > 0:
                        color = Colors.LIGHT_BLUE
                    else:
                        color = Colors.WHITE
                grid_table_item.setBackground(color)

    def update_comp_table(self):
        """
        Updates comp. table
        :return: None
        """
        if self.params_dict is None or not self.image_tracking_cbox.isChecked():
            return

        for row in range(self.current_chip_config["num_crystal_h"]):
            for col in range(self.current_chip_config["num_crystal_v"]):

                if self.inverted_rows_cbox.isChecked() and row % 2:
                    table_col = self.current_chip_config["num_crystal_v"] - col - 1
                else:
                    table_col = col

                comp_table_item = self.comp_table.item(row, table_col)
                start_index = (
                    self.info_dict["processing_grid_cell"]
                    * self.current_chip_config["num_crystal_v"]
                    * self.current_chip_config["num_crystal_h"]
                    * self.params_dict["num_images_per_trigger"]
                    + (row * self.current_chip_config["num_crystal_h"] + col)
                    * self.params_dict["num_images_per_trigger"]
                )

                end_index = min(
                    start_index + self.params_dict["num_images_per_trigger"],
                    self.results[self.score_type].size - 1,
                )
                color = Colors.LIGHT_GRAY
                if (
                    self.info_dict["collect_comp_cell"]
                    == row * self.current_chip_config["num_crystal_h"] + col
                ):
                    color = Colors.LIGHT_ORANGE
                elif (
                    self.info_dict["processing_comp_cell"]
                    == row * self.current_chip_config["num_crystal_h"] + col
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

    def update_stats(self):
        return
        #for key in self.results.keys():
        #    print(key, self.results[key].min(), self.results[key].max())


class GridViewGraphicsItem(QtImport.QGraphicsItem):
    """
    Class to represent full grid
    """

    def __init__(self):
        """
        Defines grid view
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
        self.num_comp_x = None
        self.num_comp_y = None
        self.num_holes_x = None
        self.num_holes_y = None
        self.offset_hole = 2
        self.offset_comp = 10

        self.size_hole = None
        self.size_comp_x = None
        self.size_comp_y = None
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
            for comp_y in range(self.num_comp_y):
                for comp_x in range(self.num_comp_x):
                    for hole_y in range(1, self.num_holes_y + 1):
                        for hole_x in range(1, self.num_holes_x + 1):
                            # comp_y = self.num_comp_y - comp_y + 1
                            hole_y = self.num_holes_y - hole_y + 1
                            corner_x = (
                                comp_x * (self.size_comp_x + self.offset_comp)
                            ) + (hole_x * (self.size_hole + self.offset_hole))
                            corner_y = (
                                comp_y * (self.size_comp_y + self.offset_comp)
                            ) + (hole_y * (self.size_hole + self.offset_hole))
                            painter.drawRect(
                                corner_x, corner_y, self.size_hole, self.size_hole
                            )

    def init_item(self, params_dict, results=None):
        """
        Inits item
        :param params_dict: configuration dict
        :param results: None
        :return:
        """
        self.results = results

        self.num_comp_x = params_dict["num_comp_h"]
        self.num_comp_y = params_dict["num_comp_v"]
        self.num_holes_x = params_dict["num_crystal_h"]
        self.num_holes_y = params_dict["num_crystal_v"]

        self.size_hole = 2000 / (
            self.num_comp_x * (self.offset_comp + self.num_holes_x * self.offset_hole)
        )
        self.size_comp_x = (self.size_hole + self.offset_hole) * self.num_holes_x
        self.size_comp_y = (self.size_hole + self.offset_hole) * self.num_holes_y
        self.size_chip_x = (self.size_comp_x + self.offset_comp) * (
            self.num_comp_x + 0.5
        )
        self.size_chip_y = (self.size_comp_y + self.offset_comp) * (
            self.num_comp_y + 0.5
        )

        self.scene().setSceneRect(0, 0, self.size_chip_x + 10, self.size_chip_y + 10)

    def set_results(self, params_dict, results):
        """
        Updates results
        :param params_dict:
        :param results:
        :return:
        """
        self.images_per_crystal = params_dict["num_images_per_trigger"]
        self.results = results


class GridViewOverlayItem(GridViewGraphicsItem):
    """
    Overlay to draw fits over the grid view
    """

    def calc_hole_coordinates(self, image_index):
        """
        Calculates hole coordinates
        :param img_index:
        :return:
        """
        image_index = int(image_index)
        image_number = image_index // self.images_per_crystal

        comp_serial = image_number // (self.num_holes_x * self.num_holes_y)
        holes_serial = image_number % (self.num_holes_x * self.num_holes_y)
        timepoint_serial = image_index % self.images_per_crystal

        comp_x = comp_serial % self.num_comp_x
        comp_y = comp_serial // self.num_comp_x
        hole_x = holes_serial % self.num_holes_x + 1
        hole_y = holes_serial // self.num_holes_x + 1
        timepoint_x = timepoint_serial % 2 + 1
        timepoint_y = timepoint_serial // 2 + 1

        if not hole_y & 1:
            hole_x = self.num_holes_x - hole_x + 1

        return (comp_x, comp_y, hole_x, hole_y, timepoint_x, timepoint_y)

    def paint(self, painter, option, widget):
        """
        Main pain method
        :param painter:
        :param option:
        :param widget:
        :return:
        """
        self.custom_brush.setColor(QtImport.Qt.blue)
        painter.setBrush(self.custom_brush)

        def draw_hole_timeseries(
            comp_x, comp_y, hole_x, hole_y, subpixel_x, subpixel_y
        ):
            """
            Draws holes
            :param comp_x:
            :param comp_y:
            :param hole_x:
            :param hole_y:
            :param subpixel_x:
            :param subpixel_y:
            :return:
            """
            # comp_y = self.num_comp_y - comp_y +1
            # hole_y        = self.num_holes_y - hole_y +1
            # subpixel_y    = self.no_subpixels_y - subpixel_y +1

            corner_x = (
                comp_x * (self.size_comp_x + self.offset_comp)
                + (hole_x * (self.size_hole + self.offset_hole))
                + ((subpixel_x - 1) * self.size_hole)
            )

            corner_y = (
                comp_y * (self.size_comp_y + self.offset_comp)
                + (hole_y * (self.size_hole + self.offset_hole))
                + ((subpixel_y - 1) * self.size_hole)
            )

            painter.drawRect(corner_x, corner_y, self.size_hole, self.size_hole)

        if self.results is not None:
            hitlist = np.where(self.results["score"] > 0)[0]
            for hit in hitlist:
                comp_x, comp_y, hole_x, hole_y, timepoint_x, timepoint_y = self.calc_hole_coordinates(
                    hit
                )
                if timepoint_y <= 1:
                    draw_hole_timeseries(
                        comp_x, comp_y, hole_x, hole_y, timepoint_x, timepoint_y
                    )
