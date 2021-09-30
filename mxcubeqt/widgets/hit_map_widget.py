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

import numpy as np
from copy import deepcopy

from mxcubeqt.utils import qt_import
from widgets.pyqtgraph_widget import PlotWidget
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class HitMapWidget(qt_import.QWidget):

    def __init__(self, parent=None):

        qt_import.QWidget.__init__(self, parent)

        self.setObjectName("hit_map_widget")

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Internal values -----------------------------------------------------
        self.__result_types = []
        self.__results_raw = None
        self.__results_aligned = None
        self.__first_result = True
        self.__grid = None
        #self.__is_mesh_scan = False
        self.__data_collection = None
        self.__selected_col = 0
        self.__selected_row = 0
        self.__score_key = None
        self.__max_value = 0
        self.__filter_min_value = 0
        self.__best_pos_list = None
        self.__hitmap_clicked = False
        self.__enable_continues_image_display = False
        #self.__tooltip_text = None
        self.selected_image_serial = None

        # Graphic elements ----------------------------------------------------
        self._hit_map_gbox = qt_import.QGroupBox("Online processing results", self)
        hit_maps_widget = qt_import.QWidget(self._hit_map_gbox)
        self._osc_hit_map_plot = PlotWidget(hit_maps_widget)
        self._osc_hit_map_plot.set_plot_type("1D")
        self._grid_hit_map_plot = PlotWidget(hit_maps_widget)
        self._grid_hit_map_plot.set_plot_type("2D")
        self._hit_map_popup_menu = qt_import.QMenu(self._hit_map_gbox)

        hit_map_info_widget = qt_import.QWidget(self._hit_map_gbox)
        score_type_label = qt_import.QLabel("Result: ", hit_map_info_widget)
        self._score_type_cbox = qt_import.QComboBox(hit_map_info_widget)
        self._autoscale_button = qt_import.QPushButton("Auto scale", hit_map_info_widget)
        image_display_cbox = qt_import.QCheckBox("Display image in ADxV", hit_map_info_widget)
        self._image_info_label = qt_import.QLabel(
            "Image: #, value #", hit_map_info_widget
        )

        self._hit_map_tools_widget = qt_import.QWidget(self._hit_map_gbox)

        _threshold_label = qt_import.QLabel("Threshold: ", self._hit_map_tools_widget)
        self._threshold_slider = qt_import.QSlider(
            qt_import.Qt.Horizontal, self._hit_map_tools_widget
        )
        self._relaunch_processing_button = qt_import.QPushButton(
            "Relaunch processing", self._hit_map_tools_widget
        )
        self._create_points_button = qt_import.QPushButton(
            "Create centring points", self._hit_map_tools_widget
        )

        """
        self._summary_gbox = qt_import.QGroupBox("Summary", self)
        self._summary_textbrowser = qt_import.QTextBrowser(self._summary_gbox)
        self._best_pos_gbox = qt_import.QGroupBox("Best positions", self)
        self._best_pos_table = qt_import.QTableWidget(self._best_pos_gbox)
        self._best_pos_popup_menu = qt_import.QMenu(self._hit_map_gbox)
        self._best_pos_gbox.setHidden(True)
        """

        # Layout --------------------------------------------------------------
        _hit_map_info_hlayout = qt_import.QHBoxLayout(hit_map_info_widget)
        _hit_map_info_hlayout.addWidget(score_type_label)
        _hit_map_info_hlayout.addWidget(self._score_type_cbox)
        _hit_map_info_hlayout.addWidget(self._autoscale_button)
        _hit_map_info_hlayout.addWidget(image_display_cbox)
        _hit_map_info_hlayout.addStretch(0)
        _hit_map_info_hlayout.addWidget(self._image_info_label)
        _hit_map_info_hlayout.setSpacing(2)
        _hit_map_info_hlayout.setContentsMargins(0, 0, 0, 0)

        _hit_map_tools_hlayout = qt_import.QHBoxLayout(self._hit_map_tools_widget)
        _hit_map_tools_hlayout.addWidget(_threshold_label)
        _hit_map_tools_hlayout.addWidget(self._threshold_slider)
        _hit_map_tools_hlayout.addStretch(0)
        _hit_map_tools_hlayout.addWidget(self._relaunch_processing_button)
        _hit_map_tools_hlayout.addWidget(self._create_points_button)
        _hit_map_tools_hlayout.setSpacing(2)
        _hit_map_tools_hlayout.setContentsMargins(0, 0, 0, 0)

        _hit_maps_hlayout = qt_import.QHBoxLayout(hit_maps_widget)
        _hit_maps_hlayout.addWidget(self._osc_hit_map_plot)
        _hit_maps_hlayout.addWidget(self._grid_hit_map_plot)

        _hit_map_gbox_vlayout = qt_import.QVBoxLayout(self._hit_map_gbox)
        _hit_map_gbox_vlayout.addWidget(hit_maps_widget)
        _hit_map_gbox_vlayout.addWidget(hit_map_info_widget)
        _hit_map_gbox_vlayout.addWidget(self._hit_map_tools_widget)
        _hit_map_gbox_vlayout.setSpacing(2)
        _hit_map_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        """
        _summary_gbox_vlayout = qt_import.QVBoxLayout(self._summary_gbox)
        _summary_gbox_vlayout.addWidget(self._summary_textbrowser)
        _summary_gbox_vlayout.setSpacing(2)
        _summary_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _best_postition_gbox_vlayout = qt_import.QVBoxLayout(self._best_pos_gbox)
        _best_postition_gbox_vlayout.addWidget(self._best_pos_table)
        _best_postition_gbox_vlayout.setSpacing(2)
        _best_postition_gbox_vlayout.setContentsMargins(0, 0, 0, 0)
        """

        _main_hlayout = qt_import.QVBoxLayout(self)
        _main_hlayout.addWidget(self._hit_map_gbox)
        #_main_hlayout.addWidget(self._summary_gbox)
        #_main_hlayout.addWidget(self._best_pos_gbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signals and slots ------------------------------------------------
        image_display_cbox.stateChanged.connect(self.enable_image_display_state_changed)
        self._score_type_cbox.activated.connect(self.score_type_changed)
        self._threshold_slider.valueChanged.connect(self.filter_min_slider_changed)
        self._relaunch_processing_button.clicked.connect(
            self.relaunch_processing_clicked
        )
        self._create_points_button.clicked.connect(self.create_points_clicked)
        self._osc_hit_map_plot.mouseMovedSignal.connect(self.mouse_moved)
        self._osc_hit_map_plot.mouseClickedSignal.connect(self.mouse_clicked)
        self._osc_hit_map_plot.mouseDoubleClickedSignal.connect(
            self.move_to_position_clicked
        )
        self._osc_hit_map_plot.mouseLeftSignal.connect(self.mouse_left_plot)
        self._autoscale_button.clicked.connect(self.autoscale_pressed)

        # Other ---------------------------------------------------------------
        #self.__tooltip_text = (
        #    "Double click to move to the position. " + "Right click to open menu."
        #)
        #self._osc_hit_map_plot.setToolTip(self.__tooltip_text)
        self._hit_map_popup_menu.addSeparator()
        self._hit_map_popup_menu.addAction(
            "Move to position", self.move_to_position_clicked
        )
        self._hit_map_popup_menu.addAction(
            "Create centring point", self.create_centring_point_clicked
        )

        self._hit_map_popup_menu.addAction(
            "Create helical line", self.create_helical_line_clicked
        )
        self._hit_map_popup_menu.addAction(
            "Rotate 90 degrees and create helical line",
            self.rotate_and_create_helical_line_clicked,
        )

        self._hit_map_popup_menu.addSeparator()
        self._hit_map_popup_menu.addAction(
            "Open image in ADXV", self.display_image_clicked
        )
        self._hit_map_popup_menu.addSeparator()

        #self._osc_hit_map_plot.contextMenuEvent = self.open_hit_map_popup_menu

        if HWR.beamline.online_processing is not None:
            self.__result_types = HWR.beamline.online_processing.get_result_types()
        for result in self.__result_types:
            self._score_type_cbox.addItem(result["descr"])
        self._score_type_cbox.setMaximumWidth(200)
        self.__score_key = "spots_resolution"

        self._relaunch_processing_button.setVisible(False)

        self._threshold_slider.setRange(0, 100)
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setFixedWidth(200)
        self._threshold_slider.setTracking(False)

        #font = self._best_pos_table.font()
        #font.setPointSize(8)
        #self._best_pos_table.setFont(font)
        """
        self._best_pos_table.setEditTriggers(qt_import.QAbstractItemView.NoEditTriggers)
        self._best_pos_table.setColumnCount(9)
        self._best_pos_table.setAlternatingRowColors(True)
        self._best_pos_table.setWordWrap(False)
        self._best_pos_table.horizontalHeader().setSortIndicatorShown(True)
        self._best_pos_table.setHorizontalHeaderItem(
            0, qt_import.QTableWidgetItem("No.")
        )
        for index, result_type in enumerate(self.__result_types):
            self._best_pos_table.setHorizontalHeaderItem(
                index + 1, qt_import.QTableWidgetItem(result_type["descr"])
            )

        for index, header_text in enumerate(("Path", "Col", "Row", "Motor positions")):
            self._best_pos_table.setHorizontalHeaderItem(
                5 + index, qt_import.QTableWidgetItem(header_text)
            )

        self._best_pos_popup_menu.addAction(
            "Move to position", self.move_to_best_position_clicked
        )
        self._best_pos_table.contextMenuEvent = self.open_best_pos_popup_menu

        screen_shape = qt_import.QDesktopWidget().screenGeometry()
        """

    def set_data_collection(self, data_collection):
        self.clean_result()

        self.__data_collection = data_collection
        self.__grid = self.__data_collection.grid
        num_images = self.__data_collection.acquisitions[
            0
        ].acquisition_parameters.num_images
        self.__first_result = True

        y_array = np.zeros(1)
        for result_type in self.__result_types:
            self._osc_hit_map_plot.add_curve(
                result_type["key"],
                y_array,
                x_array=None,
                color=result_type["color"],
            )
        self._osc_hit_map_plot.hide_all_curves()
        self._osc_hit_map_plot.show_curve(self.__score_key)
        self._osc_hit_map_plot.autoscale_axes()

        if self.__grid:
            (num_col, num_row) = self.__grid.get_col_row_num()
            #self._summary_textbrowser.append("<b>Mesh parameters</b>")
            grid_params = self.__grid.get_properties()
            empty_array = np.zeros(num_images).reshape(
                grid_params["steps_x"],
                grid_params["steps_y"]
            )
            self._grid_hit_map_plot.plot_result(empty_array)
        
    def main_gbox_toggled(self, toggle):
        self._osc_hit_map_plot.setHidden(not toggle)
        self._hit_map_tools_widget.setHidden(not toggle)

    def open_hit_map_popup_menu(self, context_event):
        point = qt_import.QPoint(context_event.globalX(), context_event.globalY())
        self._hit_map_popup_menu.popup(point)

    def open_best_pos_popup_menu(self, context_event):
        if self._best_pos_table.rowCount() > 0:
            point = qt_import.QPoint(context_event.globalX(), context_event.globalY())
            self._best_pos_popup_menu.popup(point)

    def score_type_changed(self, index):
        self.__score_key = self.__result_types[index]["key"]

        self._osc_hit_map_plot.hide_all_curves()
        self._osc_hit_map_plot.show_curve(self.__score_key)
        self._osc_hit_map_plot.autoscale_axes()
        self.adjust_y_labels()

        if self.__grid:
            self._grid_hit_map_plot.plot_result(
                self.__results_aligned[self.__score_key]
            )
            self.__grid.set_score(
                self.__results_raw[self.__score_key]
            )

        
    def adjust_y_labels(self):
        labels = []
        positions = np.linspace(0, self.__results_raw[self.__score_key].max(), 5)

        if self.__score_key == "spots_resolution":
            labels.append("inf")
            for item in positions[1:]:
                if item == 0:
                   labels.append("0")
                else:
                   labels.append("%.2f" % (1.0 / item))
        else:
            for item in positions:
                labels.append("%.2f" % item)

        self._osc_hit_map_plot.set_yticks(list(zip(positions, labels)))
        
    def filter_min_slider_changed(self, value):
        # self.__grid.set_min_score(self._threshold_slider.value() / 100.0)
        filter_min_value = self.__results_raw[self.__score_key].max() * value / 100.0
        result = deepcopy(self.__results_aligned[self.__score_key])
        
        self.__results_aligned[self.__score_key][result < filter_min_value] = 0
        self._grid_hit_map_plot.plot_result(result)

    def mouse_moved(self, pos_x, pos_y):
        if self.__results_raw:
            do_update = False

            if self.__grid: 
                (num_col, num_row) = self.__grid.get_col_row_num()
                pos_y = num_row - pos_y

                if abs(int(pos_x) - int(self.__selected_col)):
                    self.__selected_col = pos_x
                    do_update = True
                if abs(int(pos_y) - int(self.__selected_row)):
                    self.__selected_row = pos_y
                    do_update = True
            else:
                if pos_x < 0:
                    pos_x = 0
                elif pos_x > len(self.__results_raw[self.__score_key])- 1:
                    pos_x = len(self.__results_raw[self.__score_key]) - 1
                if abs(pos_x - self.__selected_col) > 1:
                    self.__selected_col = pos_x
                    do_update = True

            if do_update:
                self.update_image_info()
                if self.__enable_continues_image_display: 
                    self.display_image_clicked()

    def mouse_clicked(self, pos_x, pos_y):
        self.__hitmap_clicked = True

    def update_image_info(self):
        if self.__data_collection:
            msg = ""
            image, line, self.selected_image_serial, image_path = (
                self.get_image_parameters_from_coord()
            )
            msg = "Image %d, value: %.1f" % (
                self.selected_image_serial,
                self.__results_raw[self.__score_key][image],
            )
            self._image_info_label.setText(msg)

    def plot_double_clicked(self, event):
        self.move_to_selected_position()

    def mouse_left_plot(self):
        self.__hitmap_clicked = False
        #self._osc_hit_map_plot.setToolTip(self.__tooltip_text)
 
    def autoscale_pressed(self):
        self._osc_hit_map_plot.autoscale_axes()

    def move_to_position_clicked(self):
        self.move_to_selected_position()

    def set_results(self, results_raw, results_aligned):
        """Displays results on the widget
        """
        self.__results_raw = results_raw
        self.__results_aligned = results_aligned

        #self.__is_mesh_scan = list(self.__results_aligned.values())[0].ndim == 2

        if self.__first_result:
            if self.__grid:
                self.__score_key = "score"
                self._score_type_cbox.setCurrentIndex(1)
            else:
                self.__score_key = "spots_resolution"
                self._score_type_cbox.setCurrentIndex(0)
            self.adjust_y_labels()
            self.__first_result = False

        self._osc_hit_map_plot.autoscale_axes()
        #self._grid_hit_map_plot.autoscale_axes()

    def update_results(self, last_results):
        self._osc_hit_map_plot.update_curves(self.__results_raw)
        self._osc_hit_map_plot.autoscale_axes()
        self.adjust_y_labels()
        if self.__grid:
            self._grid_hit_map_plot.plot_result(self.__results_aligned[self.__score_key])
        
    def clean_result(self):
        """
        Method to clean hit map, summary log and table with best positions
        """
        self.__results_raw = None
        self.__results_aligned = None
        self.__grid = None
        self.__data_collection = None
        self._osc_hit_map_plot.clear()
        self._grid_hit_map_plot.clear()
        self._threshold_slider.setValue(0)
        #self._summary_textbrowser.clear()
        #self._best_pos_table.setRowCount(0)
        #self._best_pos_table.setSortingEnabled(False)

    def create_centring_point_clicked(self):
        """
        Creates a centring point based on the location on the location
        on hit map.
        """
        self.create_centring_point()

    def create_points_clicked(self):
        """
        Creates new centring points based on each image score.
        All images are checked and if the value is over the threshold
         then screen x and y coordinates are estimated.
        """
        if self.__results_raw[self.__score_key].ndim == 1:
            for col in range(self.__results_raw[self.__score_key].shape[0]):
                if self.__results_raw[self.__score_key][col] > 0:
                    self.create_centring_point(col + 0.5)
        else:
            for col in range(self.__results_aligned[self.__score_key].shape[0]):
                for row in range(self.__results_aligned[self.__score_key].shape[1]):
                    if self.__results_aligned[self.__score_key][col][row] > 0:
                        # MD2
                        row = (
                            self.__results_aligned[self.__score_key].shape[1] - row - 1
                        )
                        self.create_centring_point(col + 0.5, row + 0.5)
        HWR.beamline.sample_view.select_all_points()

    def display_image_clicked(self):
        """
        Displays image in image tracker (by default adxv)
        """
        image, line, image_num, image_path = self.get_image_parameters_from_coord()
        try:
            HWR.beamline.image_tracking.load_image(image_path)
        except BaseException:
            pass

    def display_image_tooltip(self):
        image, line, self.selected_image_serial, image_path = (
            self.get_image_parameters_from_coord()
        )
        tooltip_text = "Image no. %d" % self.selected_image_serial
        if self.__results_raw:
            if self.__grid:
                col, row = self.__grid.get_col_row_from_image(
                    self.selected_image_serial - 1
                )
                tooltip_text += (
                    "\nTotal score: %.1f" % self.__results_raw["score"][col][row]
                    + "\nNumber of spots: %d"
                    % self.__results_raw["spots_num"][col][row]
                )

            else:
                tooltip_text += (
                    "\nTotal score: %.1f" % self.__results_raw["score"][image]
                    + "\nNumber of spots: %d" % self.__results_raw["spots_num"][image]
                )
        self._osc_hit_map_plot.setToolTip(tooltip_text)

    def enable_image_display_state_changed(self, state):
        self.__enable_continues_image_display = state

    def get_image_parameters_from_coord(self):
        """
        returns image parameters for selected hit map frame
        """
        if self.__grid:
            image, line, image_num = self.__grid.get_image_from_col_row(
                self.__selected_col, self.__selected_row
            ) 
        else:
            image = int(self.__selected_col)
            line = 1
            image_num = (
                image
                + self.__data_collection.acquisitions[
                    0
                ].acquisition_parameters.first_image
            )


        image_path = self.__data_collection.acquisitions[
            0
        ].path_template.get_image_path()
        image_path = image_path % image_num
        return image, line, image_num, image_path

    def get_col_row_from_image_line(self, line, image):
        """
        Returns col and row from image and line
        """
        col, row = self.__grid.get_col_row_from_line_image(line, image)
        if self.__results_aligned:
            row = self.__results_aligned[self.__score_key].shape[1] - row - 1
        return int(col), int(row)

    def create_centring_point(self, coord_x=None, coord_y=None):
        """
        Descript. : creates a new centring point for selected coordinate.
                    For grid scan coord_x, and coord_y are grid coordinates in microns
                    For helical line coord_x represents frame number
        """
        if coord_x is None:
            coord_x = self.__selected_col
        if coord_y is None:
            coord_y = self.__selected_row
        num_images = self.__data_collection.acquisitions[
            0
        ].acquisition_parameters.num_images
        osc_start = self.__data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_start
        osc_range = self.__data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_range

        omega = None
        if self.__grid:
            self.__grid.set_osc_range(osc_range)
            motor_pos_dict = self.__grid.get_motor_pos_from_col_row(
                coord_x, coord_y
            )
        else:
            omega = osc_start + osc_range * float(coord_x) / num_images
            (
                point_one,
                point_two,
            ) = self.__data_collection.get_centred_positions()
            motor_pos_dict = HWR.beamline.diffractometer.get_point_from_line(
                point_one, point_two, coord_x, num_images
            )
            motor_pos_dict["phi"] = omega
        HWR.beamline.sample_view.create_centring_point(
            True, {"motors": motor_pos_dict}
        )

    def create_helical_line_clicked(self):
        motor_pos_dict = self.__grid.get_motor_pos_from_col_row(
            self.__selected_col, self.__selected_row
        )
        HWR.beamline.sample_view.create_auto_line(motor_pos_dict)

    def rotate_and_create_helical_line_clicked(self):
        self.move_to_selected_position()
        HWR.beamline.diffractometer.move_omega_relative(90)
        HWR.beamline.sample_view.create_auto_line()

    def move_to_selected_position(self):
        """Moves to grid position x and y are positions in micrometers starting
           from left top corner (as graphical coordinates)
        """
        osc_range = self.__data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_range
        if self.__grid:
            self.__grid.set_osc_range(osc_range)
            motor_pos_dict = self.__grid.get_motor_pos_from_col_row(
                self.__selected_col, self.__selected_row
            )
        else:
            num_images = (
                self.__data_collection.acquisitions[
                    0
                ].acquisition_parameters.num_images
                - 1
            )
            (
                point_one,
                point_two,
            ) = self.__data_collection.get_centred_positions()
            motor_pos_dict = HWR.beamline.diffractometer.get_point_from_line(
                point_one, point_two, int(self.__selected_x), num_images
            )

        HWR.beamline.diffractometer.move_to_motors_positions(
            motor_pos_dict, wait=True
        )

    def set_best_pos(self):
        """Displays 10 (if exists) best positions
        """

        return
        self._best_pos_table.setRowCount(
            len(self.__results_raw.get("best_positions", []))
        )
        for row, best_pos in enumerate(self.__results_raw.get("best_positions", [])):
            self._best_pos_table.setItem(
                row, 0, qt_import.QTableWidgetItem("%d" % (best_pos.get("index") + 1))
            )
            self._best_pos_table.setItem(
                row, 1, qt_import.QTableWidgetItem("%.2f" % (best_pos.get("score")))
            )
            self._best_pos_table.setItem(
                row, 2, qt_import.QTableWidgetItem("%d" % (best_pos.get("spots_num")))
            )
            self._best_pos_table.setItem(
                row,
                3,
                qt_import.QTableWidgetItem("%.2f" % (best_pos.get("spots_int_aver"))),
            )
            self._best_pos_table.setItem(
                row,
                4,
                qt_import.QTableWidgetItem("%.2f" % (best_pos.get("spots_resolution"))),
            )
            self._best_pos_table.setItem(
                row, 5, qt_import.QTableWidgetItem(str(best_pos.get("filename")))
            )
            self._best_pos_table.setItem(
                row, 6, qt_import.QTableWidgetItem("%d" % (best_pos.get("col")))
            )
            self._best_pos_table.setItem(
                row, 7, qt_import.QTableWidgetItem("%d" % (best_pos.get("row")))
            )
            if best_pos["cpos"]:
                self._best_pos_table.setItem(
                    row, 8, qt_import.QTableWidgetItem(str(best_pos["cpos"]))
                )
        self._best_pos_table.setSortingEnabled(True)

    def move_to_best_position_clicked(self):
        """
        Moves diffractometer motors to the selected position
        """
        if self._best_pos_table.currentRow() > -1:
            HWR.beamline.diffractometer.move_to_motors_positions(
                self.__results_raw["best_positions"][self._best_pos_table.currentRow()][
                    "cpos"
                ]
            )

    def create_best_centring_point_clicked(self):
        """
        Creates a new centring point based on the selected point
        from the table of best positions.
        """
        if self._best_pos_table.currentRow() > -1:
            HWR.beamline.diffractometer.create_centring_point(
                self.__results_raw["best_positions"][self._best_pos_table.currentRow()]
                .get("cpos")
                .as_dict()
            )

    def display_best_image_clicked(self):
        """
        Displays image (clicked from best position table) in ADXV
        """
        if self._best_pos_table.currentRow() > -1:
            image_path = self.__results_raw["best_positions"][
                self._best_pos_table.currentRow()
            ].get("filename")
            HWR.beamline.image_tracking.load_image(image_path)

    def relaunch_processing_clicked(self):
        """
        Relaunches parallel processing
        """
        if self.__data_collection and self.__grid:
            HWR.beamline.online_processing.run_processing(
                self.__data_collection
            )
