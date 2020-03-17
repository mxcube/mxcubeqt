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
try:
   from widgets.pyqtgraph_widget import PlotWidget
except:
   from gui.widgets.matplot_widget import PlotWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class HitMapWidget(QtImport.QWidget):

    def __init__(self, parent=None, show_aligned_results=False):

        QtImport.QWidget.__init__(self, parent)

        self.setObjectName("hit_map_widget")

        # Properties ----------------------------------------------------------

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Internal values -----------------------------------------------------
        self.__plot_type = "1D"
        self.__result_types = []
        self.__results_raw = None
        self.__results_aligned = None
        self.__first_result = True
        self.__associated_grid = None
        self.__associated_data_collection = None
        self.__selected_col = 0
        self.__selected_row = 0
        self.__score_key = None
        self.__max_value = 0
        self.__filter_min_value = 0
        self.__best_pos_list = None
        self.__hit_map_max_size = []
        self.__hitmap_clicked = False
        self.__enable_continues_image_display = False
        #self.__tooltip_text = None
        self.selected_image_serial = None

        # Graphic elements ----------------------------------------------------
        self._hit_map_gbox = QtImport.QGroupBox("Hit map", self)
        self._hit_map_plot = PlotWidget(self._hit_map_gbox)
        self._hit_map_popup_menu = QtImport.QMenu(self._hit_map_gbox)
        

        hit_map_info_widget = QtImport.QWidget(self._hit_map_gbox)
        score_type_label = QtImport.QLabel("Result: ", hit_map_info_widget)
        self._score_type_cbox = QtImport.QComboBox(hit_map_info_widget)
        self._autoscale_button = QtImport.QPushButton("Auto scale", hit_map_info_widget)
        image_display_cbox = QtImport.QCheckBox("Display image in ADxV", hit_map_info_widget)
        self._image_info_label = QtImport.QLabel(
            "Image: #, value #", hit_map_info_widget
        )

        self._hit_map_tools_widget = QtImport.QWidget(self._hit_map_gbox)

        _threshold_label = QtImport.QLabel("Threshold: ", self._hit_map_tools_widget)
        self._threshold_slider = QtImport.QSlider(
            QtImport.Qt.Horizontal, self._hit_map_tools_widget
        )
        self._relaunch_processing_button = QtImport.QPushButton(
            "Relaunch processing", self._hit_map_tools_widget
        )
        self._create_points_button = QtImport.QPushButton(
            "Create centring points", self._hit_map_tools_widget
        )

        self._summary_gbox = QtImport.QGroupBox("Summary", self)
        self._summary_textbrowser = QtImport.QTextBrowser(self._summary_gbox)
        self._best_pos_gbox = QtImport.QGroupBox("Best positions", self)
        self._best_pos_table = QtImport.QTableWidget(self._best_pos_gbox)
        self._best_pos_popup_menu = QtImport.QMenu(self._hit_map_gbox)
        self._best_pos_gbox.setHidden(True)

        # Layout --------------------------------------------------------------
        _hit_map_info_hlayout = QtImport.QHBoxLayout(hit_map_info_widget)
        _hit_map_info_hlayout.addWidget(score_type_label)
        _hit_map_info_hlayout.addWidget(self._score_type_cbox)
        _hit_map_info_hlayout.addWidget(self._autoscale_button)
        _hit_map_info_hlayout.addWidget(image_display_cbox)
        _hit_map_info_hlayout.addStretch(0)
        _hit_map_info_hlayout.addWidget(self._image_info_label)
        _hit_map_info_hlayout.setSpacing(2)
        _hit_map_info_hlayout.setContentsMargins(0, 0, 0, 0)

        _hit_map_tools_hlayout = QtImport.QHBoxLayout(self._hit_map_tools_widget)
        _hit_map_tools_hlayout.addWidget(_threshold_label)
        _hit_map_tools_hlayout.addWidget(self._threshold_slider)
        _hit_map_tools_hlayout.addStretch(0)
        _hit_map_tools_hlayout.addWidget(self._relaunch_processing_button)
        _hit_map_tools_hlayout.addWidget(self._create_points_button)
        _hit_map_tools_hlayout.setSpacing(2)
        _hit_map_tools_hlayout.setContentsMargins(0, 0, 0, 0)

        _hit_map_gbox_vlayout = QtImport.QVBoxLayout(self._hit_map_gbox)
        _hit_map_gbox_vlayout.addWidget(self._hit_map_plot)
        _hit_map_gbox_vlayout.addWidget(hit_map_info_widget)
        _hit_map_gbox_vlayout.addWidget(self._hit_map_tools_widget)
        _hit_map_gbox_vlayout.setSpacing(2)
        _hit_map_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _summary_gbox_vlayout = QtImport.QVBoxLayout(self._summary_gbox)
        _summary_gbox_vlayout.addWidget(self._summary_textbrowser)
        _summary_gbox_vlayout.setSpacing(2)
        _summary_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _best_postition_gbox_vlayout = QtImport.QVBoxLayout(self._best_pos_gbox)
        _best_postition_gbox_vlayout.addWidget(self._best_pos_table)
        _best_postition_gbox_vlayout.setSpacing(2)
        _best_postition_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QtImport.QVBoxLayout(self)
        _main_hlayout.addWidget(self._hit_map_gbox)
        _main_hlayout.addWidget(self._summary_gbox)
        _main_hlayout.addWidget(self._best_pos_gbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        #self._image_info_label.setAlignment(QtImport.Qt.AlignLeft)
        #self._image_info_label.setSizePolicy(
        #    QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed
        #)

        # Qt signals and slots ------------------------------------------------
        image_display_cbox.stateChanged.connect(self.enable_image_display_state_changed)
        self._score_type_cbox.activated.connect(self.score_type_changed)
        self._threshold_slider.valueChanged.connect(self.filter_min_slider_changed)
        self._relaunch_processing_button.clicked.connect(
            self.relaunch_processing_clicked
        )
        self._create_points_button.clicked.connect(self.create_points_clicked)
        self._hit_map_plot.mouseMovedSignal.connect(self.mouse_moved)
        self._hit_map_plot.mouseClickedSignal.connect(self.mouse_clicked)
        self._hit_map_plot.mouseDoubleClickedSignal.connect(
            self.move_to_position_clicked
        )
        self._hit_map_plot.mouseLeftSignal.connect(self.mouse_left_plot)
        self._autoscale_button.clicked.connect(self.autoscale_pressed)

        # Other ---------------------------------------------------------------
        #self.__tooltip_text = (
        #    "Double click to move to the position. " + "Right click to open menu."
        #)
        #self._hit_map_plot.setToolTip(self.__tooltip_text)
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

        #self._hit_map_plot.contextMenuEvent = self.open_hit_map_popup_menu

        if HWR.beamline.online_processing is not None:
            self.__result_types = HWR.beamline.online_processing.get_result_types()
        for result in self.__result_types:
            self._score_type_cbox.addItem(result["descr"])
        self._score_type_cbox.setMaximumWidth(200)
        self.__score_key = "spots_resolution"

        self._threshold_slider.setRange(0, 100)
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setFixedWidth(200)
        self._threshold_slider.setTracking(False)

        #font = self._best_pos_table.font()
        #font.setPointSize(8)
        #self._best_pos_table.setFont(font)
        self._best_pos_table.setEditTriggers(QtImport.QAbstractItemView.NoEditTriggers)
        self._best_pos_table.setColumnCount(9)
        self._best_pos_table.setAlternatingRowColors(True)
        self._best_pos_table.setWordWrap(False)
        self._best_pos_table.horizontalHeader().setSortIndicatorShown(True)
        self._best_pos_table.setHorizontalHeaderItem(
            0, QtImport.QTableWidgetItem("No.")
        )
        for index, result_type in enumerate(self.__result_types):
            self._best_pos_table.setHorizontalHeaderItem(
                index + 1, QtImport.QTableWidgetItem(result_type["descr"])
            )

        for index, header_text in enumerate(("Path", "Col", "Row", "Motor positions")):
            self._best_pos_table.setHorizontalHeaderItem(
                5 + index, QtImport.QTableWidgetItem(header_text)
            )

        self._best_pos_popup_menu.addAction(
            "Move to position", self.move_to_best_position_clicked
        )
        self._best_pos_table.contextMenuEvent = self.open_best_pos_popup_menu

        screen_shape = QtImport.QDesktopWidget().screenGeometry()
        self.__hit_map_max_size = (screen_shape.width() / 2, screen_shape.height() / 2)

    def set_plot_type(self, plot_type):
        self.__plot_type = plot_type
        self._hit_map_plot.set_plot_type(plot_type)
        self._hit_map_gbox.setTitle("%s hit map" % plot_type)

    def set_associated_data_collection(self, data_collection):
        self.clean_result()

        self.__associated_data_collection = data_collection
        self.__associated_grid = self.__associated_data_collection.grid
        acq_parameters = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters
        self.__first_result = True
        x_axis_range = [0, acq_parameters.num_images]
        y_axis_range = [0, 1]

        if self.__plot_type == "1D":
            #x_array = np.linspace(0, acq_parameters.num_images, acq_parameters.num_images, dtype=int)
            #y_array = np.zeros(acq_parameters.num_images)
            y_array = np.zeros(1)

            self._hit_map_plot.clear()

            for result_type in self.__result_types:
                self._hit_map_plot.add_curve(
                    result_type["key"],
                    y_array,
                    x_array=None,
                    linestyle="None",
                    label=result_type["descr"],
                    color=result_type["color"],
                    marker="s",
                )

            self._hit_map_plot.hide_all_curves()
            self._hit_map_plot.show_curve(self.__score_key)
        elif self.__associated_grid is not None:
            (num_col, num_row) = self.__associated_grid.get_col_row_num()
            x_axis_range = [0, num_col]
            y_axis_range = [0, num_row]

            self._summary_textbrowser.append("<b>Mesh parameters</b>")
            grid_params = self.__associated_grid.get_properties()

            empty_array = np.zeros(acq_parameters.num_images).reshape(
                grid_params["steps_x"], grid_params["steps_y"]
            )

            self._hit_map_plot.plot_result(empty_array)

        self._hit_map_plot.set_x_axis_limits(x_axis_range)
        self._hit_map_plot.set_y_axis_limits(y_axis_range)

        self.refresh()
        #self._hit_map_plot.autoscale_axes()

    def main_gbox_toggled(self, toggle):
        self._hit_map_plot.setHidden(not toggle)
        self._hit_map_tools_widget.setHidden(not toggle)

    def open_hit_map_popup_menu(self, context_event):
        point = QtImport.QPoint(context_event.globalX(), context_event.globalY())
        self._hit_map_popup_menu.popup(point)

    def open_best_pos_popup_menu(self, context_event):
        if self._best_pos_table.rowCount() > 0:
            point = QtImport.QPoint(context_event.globalX(), context_event.globalY())
            self._best_pos_popup_menu.popup(point)

    def score_type_changed(self, index):
        self.__score_key = self.__result_types[index]["key"]

        if self.__plot_type == "1D":
            self._hit_map_plot.hide_all_curves()
            self._hit_map_plot.show_curve(self.__score_key)
            self.refresh()
        elif self.__associated_grid:
            self._hit_map_plot.update_plot(self.__results_aligned[self.__score_key])
            self.__associated_grid.set_score(self.__results_raw[self.__score_key])

        self._hit_map_plot.autoscale_axes()

    def refresh(self):
        return

        if self.__results_raw:
            if self.__plot_type == "1D":
                #self._hit_map_plot.adjust_axes(self.__score_key)
                            
                """
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

                self._hit_map_plot.set_yticks(positions)
                self._hit_map_plot.set_ytick_labels(labels)
                """
                self._hit_map_plot.autoscale_axes()
            #elif self.__associated_grid:
            #    self._hit_map_plot.plot_result(
            #        self.__results_aligned[self.__score_key]
            #    )

    def filter_min_slider_changed(self, value):
        # self.__associated_grid.set_min_score(self._threshold_slider.value() / 100.0)
        filter_min_value = self.__results_raw[self.__score_key].max() * value / 100.0
        self.__results_aligned[self.__score_key] = deepcopy(
            self.__results_raw[self.__score_key]
        )
        self.__results_aligned[self.__score_key][
            self.__results_raw[self.__score_key] < filter_min_value
        ] = 0
        self._hit_map_plot.update_plot(
            self.__results_aligned[self.__score_key]
        )

    def mouse_moved(self, pos_x, pos_y):
        do_update = False

        if self.__plot_type == "1D":
            if abs(pos_x - self.__selected_col) > 1:
                self.__selected_col = pos_x
                do_update = True 
        elif self.__associated_grid is not None: 
            (num_col, num_row) = self.__associated_grid.get_col_row_num()
            pos_y = num_row - pos_y

            if abs(int(pos_x) - int(self.__selected_col)):
                self.__selected_col = pos_x
                do_update = True
            if abs(int(pos_y) - int(self.__selected_row)):
                self.__selected_row = pos_y
                do_update = True

        if do_update and self.__results_raw is not None:
            self.update_image_info()
            #self.display_image_tooltip()
            if self.__enable_continues_image_display: 
                self.display_image_clicked()

    def mouse_clicked(self, pos_x, pos_y):
        self.__hitmap_clicked = True

    def update_image_info(self):
        if self.__associated_data_collection:
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
        #self._hit_map_plot.setToolTip(self.__tooltip_text)
 
    def autoscale_pressed(self):
        self._hit_map_plot.autoscale_axes()

    def move_to_position_clicked(self):
        self.move_to_selected_position()

    def set_results(self, results_raw, results_aligned):
        """Displays results on the widget
        """

        self.__results_raw = results_raw
        self.__results_aligned = results_aligned

        if self.__plot_type  == 1:
            if self.__first_result:
                self.__score_key = "spots_resolution"
                self._score_type_cbox.setCurrentIndex(0)
        else:
            if self.__first_result:
                self.__score_key = "spots_num"
                self._score_type_cbox.setCurrentIndex(2)

        self.__first_result = False
        self._hit_map_plot.autoscale_axes()

    def update_results(self, last_results):
        if self.__plot_type == "1D":
            self._hit_map_plot.update_curves(self.__results_raw)
        elif self.__associated_grid:
            self._hit_map_plot.update_plot(self.__results_aligned[self.__score_key])
        self._hit_map_plot.autoscale_axes()

    def clean_result(self):
        """
        Method to clean hit map, summary log and table with best positions
        """
        self.__results_raw = None
        self.__results_aligned = None
        self.__associated_grid = None
        self.__associated_data_collection = None
        self._hit_map_plot.clear()
        self._threshold_slider.setValue(0)
        self._summary_textbrowser.clear()
        self._best_pos_table.setRowCount(0)
        self._best_pos_table.setSortingEnabled(False)

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
            if self.__plot_type == "1D":
                tooltip_text += (
                    "\nTotal score: %.1f" % self.__results_raw["score"][image]
                    + "\nNumber of spots: %d" % self.__results_raw["spots_num"][image]
                )

            elif self.__associated_grid:
                col, row = self.__associated_grid.get_col_row_from_image(
                    self.selected_image_serial - 1
                )
                tooltip_text += (
                    "\nTotal score: %.1f" % self.__results_raw["score"][col][row]
                    + "\nNumber of spots: %d"
                    % self.__results_raw["spots_num"][col][row]
                )
        self._hit_map_plot.setToolTip(tooltip_text)

    def enable_image_display_state_changed(self, state):
        self.__enable_continues_image_display = state

    def get_image_parameters_from_coord(self):
        """
        returns image parameters for selected hit map frame
        """
        if self.__plot_type == "1D":
            image = int(self.__selected_col)
            line = 1
            image_num = (
                image
                + self.__associated_data_collection.acquisitions[
                    0
                ].acquisition_parameters.first_image
            )
        elif self.__associated_grid:
            image, line, image_num = self.__associated_grid.get_image_from_col_row(
                self.__selected_col, self.__selected_row
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
        if self.__results_aligned:
            row = self.__results_aligned[self.__score_key].shape[1] - row - 1
        return int(col), int(row)

    def create_centring_point(self, coord_x=None, coord_y=None):
        """
        Descript. : creates a new centring point for selected coordinate.
                    For mesh scan coord_x, and coord_y are grid coordinates in microns
                    For helical line coord_x represents frame number
        """
        if coord_x is None:
            coord_x = self.__selected_col
        if coord_y is None:
            coord_y = self.__selected_row
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
        HWR.beamline.sample_view.create_centring_point(
            True, {"motors": motor_pos_dict}
        )

    def create_helical_line_clicked(self):
        motor_pos_dict = self.__associated_grid.get_motor_pos_from_col_row(
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
        osc_range = self.__associated_data_collection.acquisitions[
            0
        ].acquisition_parameters.osc_range
        if self.__associated_grid:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.get_motor_pos_from_col_row(
                self.__selected_col, self.__selected_row
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
