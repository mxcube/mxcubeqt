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

from gui.utils import QtImport
# try:
# from widgets.Qt4_pyqtgraph_widget import TwoDimenisonalPlotWidget
# except:
from gui.widgets.matplot_widget import TwoDimenisonalPlotWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class HeatMapWidget(QtImport.QWidget):

    def __init__(self, parent=None, show_aligned_results=False):

        QtImport.QWidget.__init__(self, parent)

        self.setObjectName("heat_map_widget")
        self._show_aligned_results = show_aligned_results

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Internal values -----------------------------------------------------
        self.__results_raw = None
        self.__results_display = {}
        self.__first_result = True
        self.__associated_grid = None
        self.__associated_data_collection = None
        self.__selected_x = 0
        self.__selected_y = 0
        self.__selected_image_serial = 0
        self.__score_key = "spots_num"
        self.__max_value = 0
        self.__filter_min_value = 0
        self.__best_pos_list = None
        self.__heat_map_max_size = []
        self.__heatmap_clicked = False
        self.__enable_continues_image_display = True
        self.__tooltip_text = None
        self.selected_image_serial = None

        # Graphic elements ----------------------------------------------------
        self._heat_map_gbox = QtImport.QGroupBox("Heat map", self)
        self._heat_map_plot = TwoDimenisonalPlotWidget(self)
        self._heat_map_popup_menu = QtImport.QMenu(self._heat_map_gbox)

        heat_map_info_widget = QtImport.QWidget(self._heat_map_gbox)
        score_type_label = QtImport.QLabel("Result: ", heat_map_info_widget)
        self._score_type_cbox = QtImport.QComboBox(heat_map_info_widget)
        self._image_info_label = QtImport.QLabel(
            "Image: #, value #", heat_map_info_widget
        )

        self._heat_map_tools_widget = QtImport.QWidget(self._heat_map_gbox)

        _threshold_label = QtImport.QLabel("Threshold: ", self._heat_map_tools_widget)
        self._threshold_slider = QtImport.QSlider(
            QtImport.Qt.Horizontal, self._heat_map_tools_widget
        )
        self._relaunch_processing_button = QtImport.QPushButton(
            "Relaunch processing", self._heat_map_tools_widget
        )
        self._create_points_button = QtImport.QPushButton(
            "Create centring points", self._heat_map_tools_widget
        )

        self._summary_gbox = QtImport.QGroupBox("Summary", self)
        self._summary_textbrowser = QtImport.QTextBrowser(self._summary_gbox)
        self._best_pos_gbox = QtImport.QGroupBox("Best positions", self)
        self._best_pos_table = QtImport.QTableWidget(self._best_pos_gbox)
        self._best_pos_popup_menu = QtImport.QMenu(self._heat_map_gbox)
        self._best_pos_gbox.setHidden(True)

        # Layout --------------------------------------------------------------
        _heat_map_info_hlayout = QtImport.QHBoxLayout(heat_map_info_widget)
        _heat_map_info_hlayout.addWidget(score_type_label)
        _heat_map_info_hlayout.addWidget(self._score_type_cbox)
        _heat_map_info_hlayout.addStretch(0)
        _heat_map_info_hlayout.addWidget(self._image_info_label)
        _heat_map_info_hlayout.setSpacing(2)
        _heat_map_info_hlayout.setContentsMargins(0, 0, 0, 0)

        _heat_map_tools_hlayout = QtImport.QHBoxLayout(self._heat_map_tools_widget)
        _heat_map_tools_hlayout.addWidget(_threshold_label)
        _heat_map_tools_hlayout.addWidget(self._threshold_slider)
        _heat_map_tools_hlayout.addStretch(0)
        _heat_map_tools_hlayout.addWidget(self._relaunch_processing_button)
        _heat_map_tools_hlayout.addWidget(self._create_points_button)
        _heat_map_tools_hlayout.setSpacing(2)
        _heat_map_tools_hlayout.setContentsMargins(0, 0, 0, 0)

        _heat_map_gbox_vlayout = QtImport.QVBoxLayout(self._heat_map_gbox)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_plot)
        _heat_map_gbox_vlayout.addWidget(heat_map_info_widget)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_tools_widget)
        _heat_map_gbox_vlayout.setSpacing(2)
        _heat_map_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _summary_gbox_vlayout = QtImport.QVBoxLayout(self._summary_gbox)
        _summary_gbox_vlayout.addWidget(self._summary_textbrowser)
        _summary_gbox_vlayout.setSpacing(2)
        _summary_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _best_postition_gbox_vlayout = QtImport.QVBoxLayout(self._best_pos_gbox)
        _best_postition_gbox_vlayout.addWidget(self._best_pos_table)
        _best_postition_gbox_vlayout.setSpacing(2)
        _best_postition_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QtImport.QVBoxLayout(self)
        _main_hlayout.addWidget(self._heat_map_gbox)
        _main_hlayout.addWidget(self._summary_gbox)
        _main_hlayout.addWidget(self._best_pos_gbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        self._image_info_label.setAlignment(QtImport.Qt.AlignLeft)
        self._image_info_label.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed
        )

        # Qt signals and slots ------------------------------------------------
        self._score_type_cbox.activated.connect(self.score_type_changed)
        self._threshold_slider.valueChanged.connect(self.filter_min_slider_changed)
        self._relaunch_processing_button.clicked.connect(
            self.relaunch_processing_clicked
        )
        self._create_points_button.clicked.connect(self.create_points_clicked)
        self._heat_map_plot.mouseMovedSignal.connect(self.mouse_moved)
        self._heat_map_plot.mouseClickedSignal.connect(self.mouse_clicked)
        self._heat_map_plot.mouseDoubleClickedSignal.connect(
            self.move_to_position_clicked
        )
        self._heat_map_plot.mouseLeftSignal.connect(self.mouse_left_plot)

        # Other ---------------------------------------------------------------
        self.__tooltip_text = (
            "Double click to move to the position. " + "Right click to open menu."
        )
        self._heat_map_plot.setToolTip(self.__tooltip_text)
        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(
            "Move to position", self.move_to_position_clicked
        )
        self._heat_map_popup_menu.addAction(
            "Create centring point", self.create_centring_point_clicked
        )

        self._heat_map_popup_menu.addAction(
            "Create helical line", self.create_helical_line_clicked
        )
        self._heat_map_popup_menu.addAction(
            "Rotate 90 degrees and create helical line",
            self.rotate_and_create_helical_line_clicked,
        )

        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(
            "Open image in ADXV", self.display_image_clicked
        )
        self.continues_display_action = self._heat_map_popup_menu.addAction(
            "Continues image display in ADXV", self.toogle_continues_image_display
        )
        self.continues_display_action.setCheckable(True)
        self.continues_display_action.setChecked(True)

        self._heat_map_popup_menu.addSeparator()

        self._heat_map_plot.contextMenuEvent = self.open_heat_map_popup_menu

        score_types = ["Resolution", "Score", "Spots num"]
        for score_type in score_types:
            self._score_type_cbox.addItem(score_type)
        self._score_type_cbox.setMaximumWidth(200)
        self.__score_key = "spots_resolution"

        self._threshold_slider.setRange(0, 100)
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setFixedWidth(200)
        self._threshold_slider.setTracking(False)

        font = self._best_pos_table.font()
        font.setPointSize(8)
        self._best_pos_table.setFont(font)
        self._best_pos_table.setEditTriggers(QtImport.QAbstractItemView.NoEditTriggers)
        self._best_pos_table.setColumnCount(9)
        self._best_pos_table.setAlternatingRowColors(True)
        self._best_pos_table.setWordWrap(False)
        self._best_pos_table.horizontalHeader().setSortIndicatorShown(True)
        self._best_pos_table.setHorizontalHeaderItem(
            0, QtImport.QTableWidgetItem("No.")
        )
        for score_type in enumerate(score_types):
            self._best_pos_table.setHorizontalHeaderItem(
                score_type[0] + 1, QtImport.QTableWidgetItem(score_type[1])
            )

        self._best_pos_table.setHorizontalHeaderItem(
            5, QtImport.QTableWidgetItem("Path")
        )
        self._best_pos_table.setHorizontalHeaderItem(
            6, QtImport.QTableWidgetItem("Col")
        )
        self._best_pos_table.setHorizontalHeaderItem(
            7, QtImport.QTableWidgetItem("Row")
        )
        self._best_pos_table.setHorizontalHeaderItem(
            8, QtImport.QTableWidgetItem("Motor positions")
        )

        self._best_pos_popup_menu.addAction(
            "Move to position", self.move_to_best_position_clicked
        )
        self._best_pos_table.contextMenuEvent = self.open_best_pos_popup_menu

        screen_shape = QtImport.QDesktopWidget().screenGeometry()
        self.__heat_map_max_size = (screen_shape.width() / 2, screen_shape.height() / 2)

    def set_associated_data_collection(self, data_collection):
        self.clean_result()

        self.__associated_data_collection = data_collection
        self.__associated_grid = self.__associated_data_collection.grid
        acq_parameters = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters
        self.__first_result = True

        if not self._show_aligned_results:
            x_array = np.array([])
            y_array = np.zeros(acq_parameters.num_images)

            self._heat_map_plot.clear()
            self._heat_map_plot.add_curve(
                "spots_resolution",
                y_array,
                x_array,
                linestyle="None",
                label="Resolution",
                color="m",
                marker="s",
            )
            self._heat_map_plot.add_curve(
                "score",
                y_array,
                x_array,
                label="Total score",
                linestyle="None",
                color="b",
                marker="s",
            )
            self._heat_map_plot.add_curve(
                "spots_num",
                y_array,
                x_array,
                label="Number of spots",
                linestyle="None",
                color="b",
                marker="s",
            )
            self._heat_map_plot.hide_all_curves()
            self._heat_map_plot.show_curve(self.__score_key)
            self._heat_map_plot.set_x_axis_limits((0, acq_parameters.num_images))
            self._heat_map_plot.set_y_axis_limits((0, 1))
        else:
            axis_range = self.__associated_grid.get_col_row_num()
            self._heat_map_plot.set_y_axis_limits((0, axis_range[1]))
            self._heat_map_plot.set_x_axis_limits((0, axis_range[0]))

            self._summary_textbrowser.append("<b>Mesh parameters</b>")
            grid_params = self.__associated_grid.get_properties()

            empty_array = np.zeros(acq_parameters.num_images).reshape(
                grid_params["steps_x"], grid_params["steps_y"]
            )

            self._heat_map_plot.plot_result(np.transpose(empty_array))

        self.refresh()

    def main_gbox_toggled(self, toggle):
        self._heat_map_plot.setHidden(not toggle)
        self._heat_map_tools_widget.setHidden(not toggle)

    def open_heat_map_popup_menu(self, context_event):
        point = QtImport.QPoint(context_event.globalX(), context_event.globalY())
        self._heat_map_popup_menu.popup(point)

    def open_best_pos_popup_menu(self, context_event):
        if self._best_pos_table.rowCount() > 0:
            point = QtImport.QPoint(context_event.globalX(), context_event.globalY())
            self._best_pos_popup_menu.popup(point)

    def score_type_changed(self, score_type_index):
        if score_type_index == 0:
            self.__score_key = "spots_resolution"
        elif score_type_index == 1:
            self.__score_key = "score"
        elif score_type_index == 2:
            self.__score_key = "spots_num"

        if not self._show_aligned_results:
            self._heat_map_plot.hide_all_curves()
            self._heat_map_plot.show_curve(self.__score_key)
            self.refresh()
        else:
            self._heat_map_plot.plot_result(np.transpose(
                self.__results_display[self.__score_key]
            ))
            self._heat_map_plot.add_colorbar()

    def refresh(self):
        if self.__results_raw:
            if not self._show_aligned_results:
                self._heat_map_plot.adjust_axes(self.__score_key)

                labels = []
                positions = np.linspace(
                    0, self.__results_raw[self.__score_key].max(), 5
                    )

                if self.__score_key == "spots_resolution":
                    labels.append("inf")
                    for item in positions[1:]:
                        labels.append("%.2f" % (1.0 / item))
                else:
                    for item in positions:
                        labels.append("%d" % item)

                self._heat_map_plot.set_yticks(positions)
                self._heat_map_plot.set_ytick_labels(labels)
            else:
                self._heat_map_plot.plot_result(
                    self.__results_display[self.__score_key]
                )

    def filter_min_slider_changed(self, value):
        # self.__associated_grid.set_min_score(self._threshold_slider.value() / 100.0)
        filter_min_value = self.__results_raw[self.__score_key].max() * value / 100.0
        self.__results_display[self.__score_key] = deepcopy(
            self.__results_raw[self.__score_key]
        )
        self.__results_display[self.__score_key][
            self.__results_raw[self.__score_key] < filter_min_value
        ] = 0
        self.refresh()

    def mouse_moved(self, pos_x, pos_y):
        if self.__enable_continues_image_display and self.__heatmap_clicked:
            if (
                abs(int(self.__selected_x) - int(pos_x)) >= 1
                or abs(int(self.__selected_y) - int(pos_y)) >= 1
            ):
                self.__selected_x = pos_x
                self.__selected_y = pos_y
                self.display_image_clicked()
                self.display_image_tooltip()
                self.update_image_info()

    def mouse_clicked(self, pos_x, pos_y):
        self.__heatmap_clicked = True
        self.__selected_x = pos_x
        self.__selected_y = pos_y
        self.update_image_info()

    def update_image_info(self):
        if self.__associated_data_collection:
            msg = ""
            image, line, self.selected_image_serial, image_path = (
                self.get_image_parameters_from_coord()
            )
            if self.__associated_grid:
                try:
                    col, row = self.get_col_row_from_image_line(line, image)
                    msg = "Image %d, value: %.1f" % (
                        self.selected_image_serial,
                        self.__results_raw[self.__score_key][col][row],
                    )
                except BaseException:
                    msg = "Image %d" % self.selected_image_serial
            else:
                msg = "Image %d, value: %.1f" % (
                    self.selected_image_serial,
                    self.__results_raw[self.__score_key][image],
                )
            self._image_info_label.setText(msg)

    def plot_double_clicked(self, event):
        self.move_to_selected_position()

    def mouse_left_plot(self):
        self.__heatmap_clicked = False
        self._heat_map_plot.setToolTip(self.__tooltip_text)

    def move_to_position_clicked(self):
        self.move_to_selected_position()

    def set_results(self, results):
        """
        Displays results on the widget
        """

        self.__results_raw = results
        self.__results_display = results

        if self.__results_display[self.__score_key].ndim == 1:
            if self.__first_result:
                self._score_type_cbox.setCurrentIndex(0)
        else:
            if self.__first_result:
                self._score_type_cbox.setCurrentIndex(2)
                self.__score_key = "spots_num"
        self.__first_result = False

    def update_results(self, last_results):
        if not self._show_aligned_results:
            self._heat_map_plot.update_curves(self.__results_raw)
            self.refresh()
        else:
            self._heat_map_plot.plot_result(np.transpose(self.__results_display[self.__score_key]))

    def clean_result(self):
        """
        Method to clean heat map, summary log and table with best positions
        """
        self.__results_raw = None
        self.__results_display = None
        self.__associated_grid = None
        self.__associated_data_collection = None
        self._heat_map_plot.clear()
        self._threshold_slider.setValue(0)
        self._summary_textbrowser.clear()
        self._best_pos_table.setRowCount(0)
        self._best_pos_table.setSortingEnabled(False)

    def create_centring_point_clicked(self):
        """
        Creates a centring point based on the location on the location
        on heat map.
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
            for col in range(self.__results_display[self.__score_key].shape[0]):
                for row in range(self.__results_display[self.__score_key].shape[1]):
                    if self.__results_display[self.__score_key][col][row] > 0:
                        # MD2
                        row = (
                            self.__results_display[self.__score_key].shape[1] - row - 1
                        )
                        self.create_centring_point(col + 0.5, row + 0.5)
        HWR.beamline.microscope.select_all_points()

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
            if self.__associated_grid:
                col, row = self.__associated_grid.get_col_row_from_image(
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
        self._heat_map_plot.setToolTip(tooltip_text)

    def toogle_continues_image_display(self):
        self.__enable_continues_image_display = (
            self.continues_display_action.isChecked()
        )

    def get_image_parameters_from_coord(self, coord_x=None, coord_y=None):
        """
        returns image parameters for selected heat map frame
        """
        if not coord_x:
            coord_x = self.__selected_x
        if not coord_y:
            coord_y = self.__selected_y

        if self.__associated_grid:
            num_cols, num_rows = self.__associated_grid.get_col_row_num()
            if coord_x > num_cols:
                coord_x = num_cols
            if coord_y > num_rows:
                coord_y = num_rows

            image, line, image_num = self.__associated_grid.get_image_from_col_row(
                coord_x, coord_y
            )
        else:
            image = int(self.__selected_x)
            line = 1
            image_num = (
                image
                + self.__associated_data_collection.acquisitions[
                    0
                ].acquisition_parameters.first_image
            )
        image_path = self.__associated_data_collection.acquisitions[
            0
        ].path_template.get_image_path()
        image_path = image_path % image_num
        return image, line, image_num, image_path

    def get_col_row_from_image_line(self, line, image):
        """
        Returns col and row from image and line
        """
        col, row = self.__associated_grid.get_col_row_from_line_image(line, image)
        # TODO check if next line needs to be removed
        row = self.__results_raw[self.__score_key].shape[1] - row - 1
        return col, row

    def create_centring_point(self, coord_x=None, coord_y=None):
        """
        Descript. : creates a new centring point for selected coordinate.
                    For mesh scan coord_x, and coord_y are grid coordinates in microns
                    For helical line coord_x represents frame number
        """
        if coord_x is None:
            coord_x = self.__selected_x
        if coord_y is None:
            coord_y = self.__selected_y
        num_images = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters.num_images
        osc_start = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_start
        osc_range = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_range

        omega = None
        if self.__associated_grid:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.get_motor_pos_from_col_row(
                coord_x, coord_y
            )
        else:
            omega = osc_start + osc_range * float(coord_x) / num_images
            (
                point_one,
                point_two,
            ) = self.__associated_data_collection.get_centred_positions()
            motor_pos_dict = HWR.beamline.diffractometer.get_point_from_line(
                point_one, point_two, coord_x, num_images
            )
            motor_pos_dict["phi"] = omega
        HWR.beamline.microscope.create_centring_point(
            True, {"motors": motor_pos_dict}
        )

    def create_helical_line_clicked(self):
        motor_pos_dict = self.__associated_grid.get_motor_pos_from_col_row(
            self.__selected_x, self.__selected_y
        )
        HWR.beamline.microscope.create_auto_line(motor_pos_dict)

    def rotate_and_create_helical_line_clicked(self):
        self.move_to_selected_position()
        HWR.beamline.diffractometer.move_omega_relative(90)
        HWR.beamline.microscope.create_auto_line()

    def move_to_selected_position(self):
        """Moves to grid position x and y are positions in micrometers starting
           from left top corner (as graphical coordinates)
        """
        osc_range = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_range
        if self.__associated_grid:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.get_motor_pos_from_col_row(
                self.__selected_x, self.__selected_y
            )
        else:
            num_images = (
                self.__associated_data_collection.acquisitions[
                    0
                ].acquisition_parameters.num_images
                - 1
            )
            (
                point_one,
                point_two,
            ) = self.__associated_data_collection.get_centred_positions()
            motor_pos_dict = HWR.beamline.diffractometer.get_point_from_line(
                point_one, point_two, int(self.__selected_x), num_images
            )

        HWR.beamline.diffractometer.move_to_motors_positions(
            motor_pos_dict, wait=True
        )

    def set_best_pos(self):
        """Displays 10 (if exists) best positions
        """
        self._best_pos_table.setRowCount(
            len(self.__results_raw.get("best_positions", []))
        )
        for row, best_pos in enumerate(self.__results_raw.get("best_positions", [])):
            self._best_pos_table.setItem(
                row, 0, QtImport.QTableWidgetItem("%d" % (best_pos.get("index") + 1))
            )
            self._best_pos_table.setItem(
                row, 1, QtImport.QTableWidgetItem("%.2f" % (best_pos.get("score")))
            )
            self._best_pos_table.setItem(
                row, 2, QtImport.QTableWidgetItem("%d" % (best_pos.get("spots_num")))
            )
            self._best_pos_table.setItem(
                row,
                3,
                QtImport.QTableWidgetItem("%.2f" % (best_pos.get("spots_int_aver"))),
            )
            self._best_pos_table.setItem(
                row,
                4,
                QtImport.QTableWidgetItem("%.2f" % (best_pos.get("spots_resolution"))),
            )
            self._best_pos_table.setItem(
                row, 5, QtImport.QTableWidgetItem(str(best_pos.get("filename")))
            )
            self._best_pos_table.setItem(
                row, 6, QtImport.QTableWidgetItem("%d" % (best_pos.get("col")))
            )
            self._best_pos_table.setItem(
                row, 7, QtImport.QTableWidgetItem("%d" % (best_pos.get("row")))
            )
            if best_pos["cpos"]:
                self._best_pos_table.setItem(
                    row, 8, QtImport.QTableWidgetItem(str(best_pos["cpos"]))
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
        if self.__associated_data_collection and self.__associated_grid:
            HWR.beamline.online_processing.run_processing(
                self.__associated_data_collection
            )
