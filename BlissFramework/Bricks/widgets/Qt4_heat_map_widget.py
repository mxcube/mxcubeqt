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

import os
import numpy
from scipy import ndimage

from QtImport import *

from copy import deepcopy
from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_matplot_widget import TwoDimenisonalPlotWidget


class HeatMapWidget(QWidget):
    def __init__(self, parent=None, allow_adjust_size=True):
        QWidget.__init__(self, parent)
        self.setObjectName('heat_map_widget')
        self.allow_adjust_size = allow_adjust_size

        # Properties ---------------------------------------------------------- 

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None

        # Internal values -----------------------------------------------------
        self.__results = None
        self.__results_display = None
        self.__associated_grid = None
        self.__associated_data_collection = None
        self.__selected_x = 0
        self.__selected_y = 0
        self.__selected_image_serial = 0
        self.__score_key = "score"
        self.__max_value = 0
        self.__filter_min_value = 0
        self.__best_pos_list = None
        self.__label_im = None
        self.__heat_map_max_size = []
        self.__heatmap_clicked = False
        self.__enable_continues_image_display = True
        self.__tooltip_text = None

        # Graphic elements ----------------------------------------------------
        self._heat_map_gbox = QGroupBox('Heat map', self)
        self._heat_map_plot = TwoDimenisonalPlotWidget(self)
        self._heat_map_popup_menu = QMenu(self._heat_map_gbox)

        heat_map_info_widget = QWidget(self._heat_map_gbox)
        score_type_label = QLabel("Score type: ", heat_map_info_widget)
        self._score_type_cbox = QComboBox(heat_map_info_widget)
        self._image_info_label = QLabel("Image: #, value #", heat_map_info_widget)

        self._heat_map_tools_widget = QWidget(self._heat_map_gbox)

        _threshold_label = QLabel("Threshold: ", self._heat_map_tools_widget)
        self._threshold_slider = QSlider(Qt.Horizontal, 
               self._heat_map_tools_widget)
        self._relaunch_processing_button = QPushButton("Relaunch processing",
             self._heat_map_tools_widget)
        self._create_points_button = QPushButton("Create centring points", 
             self._heat_map_tools_widget)

        self._summary_gbox = QGroupBox("Summary", self)
        self._summary_textbrowser = QTextBrowser(self._summary_gbox)
        self._best_pos_gbox = QGroupBox("Best positions", self)
        self._best_pos_table = QTableWidget(self._best_pos_gbox)
        self._best_pos_popup_menu = QMenu(self._heat_map_gbox)
        self._best_pos_gbox.setHidden(True)

        # Layout --------------------------------------------------------------
        _heat_map_info_hlayout = QHBoxLayout(heat_map_info_widget)
        _heat_map_info_hlayout.addWidget(score_type_label)
        _heat_map_info_hlayout.addWidget(self._score_type_cbox)
        _heat_map_info_hlayout.addStretch(0)
        _heat_map_info_hlayout.addWidget(self._image_info_label)
        _heat_map_info_hlayout.setSpacing(2)
        _heat_map_info_hlayout.setContentsMargins(0, 0, 0, 0)

        _heat_map_tools_hlayout = QHBoxLayout(self._heat_map_tools_widget)
        _heat_map_tools_hlayout.addWidget(_threshold_label)
        _heat_map_tools_hlayout.addWidget(self._threshold_slider)
        _heat_map_tools_hlayout.addStretch(0)
        _heat_map_tools_hlayout.addWidget(self._relaunch_processing_button)
        _heat_map_tools_hlayout.addWidget(self._create_points_button)
        _heat_map_tools_hlayout.setSpacing(2)
        _heat_map_tools_hlayout.setContentsMargins(0, 0, 0, 0)

        _heat_map_gbox_vlayout = QVBoxLayout(self._heat_map_gbox)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_plot)
        _heat_map_gbox_vlayout.addWidget(heat_map_info_widget)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_tools_widget)
        _heat_map_gbox_vlayout.setSpacing(2)
        _heat_map_gbox_vlayout.setContentsMargins(0, 0, 0, 0)
        
        _summary_gbox_vlayout = QVBoxLayout(self._summary_gbox)
        _summary_gbox_vlayout.addWidget(self._summary_textbrowser)
        _summary_gbox_vlayout.setSpacing(2)
        _summary_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _best_postition_gbox_vlayout = QVBoxLayout(self._best_pos_gbox)
        _best_postition_gbox_vlayout.addWidget(self._best_pos_table)
        _best_postition_gbox_vlayout.setSpacing(2)
        _best_postition_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QVBoxLayout(self)
        _main_hlayout.addWidget(self._heat_map_gbox)
        _main_hlayout.addWidget(self._summary_gbox)
        _main_hlayout.addWidget(self._best_pos_gbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        self._image_info_label.setAlignment(Qt.AlignLeft)
        self._image_info_label.setSizePolicy(QSizePolicy.Expanding, 
                                             QSizePolicy.Fixed)

        # Qt signals and slots ------------------------------------------------
        self._score_type_cbox.activated.connect(self.score_type_changed)
        self._threshold_slider.valueChanged.\
             connect(self.filter_min_slider_changed)
        self._relaunch_processing_button.clicked.\
             connect(self.relaunch_processing_clicked)
        self._create_points_button.clicked.\
             connect(self.create_points_clicked)
        self._heat_map_plot.mouseMovedSignal.\
             connect(self.mouse_moved)
        self._heat_map_plot.mouseClickedSignal.\
             connect(self.mouse_clicked)
        self._heat_map_plot.mouseDoubleClickedSignal.\
             connect(self.move_to_position_clicked)
        self._heat_map_plot.mouseLeftSignal.connect(\
             self.mouse_left_plot)
             

        # Other ---------------------------------------------------------------
        self.__tooltip_text = "Double click to move to the position. " + \
                              "Right click to open menu."
        self._heat_map_plot.setToolTip(self.__tooltip_text) 
        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(\
             "Move to position",
             self.move_to_position_clicked)
        self._heat_map_popup_menu.addAction(\
             "Create centring point",
             self.create_centring_point_clicked)

        self._heat_map_popup_menu.addAction(\
             "Create helical line",
             self.create_helical_line_clicked)
        self._heat_map_popup_menu.addAction(\
             "Rotate 90 degrees and create helical line",
             self.rotate_and_create_helical_line_clicked)
        
        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(\
             "Open image in ADXV", self.display_image_clicked)
        self.continues_display_action = \
             self._heat_map_popup_menu.addAction(\
             "Continues image display in ADXV",
              self.toogle_continues_image_display)
        self.continues_display_action.setCheckable(True)
        self.continues_display_action.setChecked(True)

        self._heat_map_popup_menu.addSeparator()
        options_menu = self._heat_map_popup_menu.addMenu("Options")

        self._heat_map_plot.contextMenuEvent = self.open_heat_map_popup_menu

        score_types = ["Resolution", "Score", "Spots num"]
        for score_type in score_types:
            self._score_type_cbox.addItem(score_type)
        self._score_type_cbox.setMaximumWidth(200)
        self.__score_key = "spots_resolution"

        #self._threshold_slider.setTickmarks(QtGui.QSlider.Below)
        self._threshold_slider.setRange(0, 100)
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setFixedWidth(200)
        self._threshold_slider.setTracking(False)

        font = self._best_pos_table.font()
        font.setPointSize(8)
        self._best_pos_table.setFont(font)
        self._best_pos_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._best_pos_table.setColumnCount(9)
        self._best_pos_table.setAlternatingRowColors(True)
        self._best_pos_table.setWordWrap(False)
        self._best_pos_table.horizontalHeader().setSortIndicatorShown(True)
        self._best_pos_table.setHorizontalHeaderItem(0, \
            QTableWidgetItem("No."))
        for score_type in enumerate(score_types):
            self._best_pos_table.setHorizontalHeaderItem(\
                 score_type[0] + 1, QTableWidgetItem(score_type[1]))

        self._best_pos_table.setHorizontalHeaderItem(5,
             QTableWidgetItem("Path"))
        self._best_pos_table.setHorizontalHeaderItem(6,
             QTableWidgetItem("Col"))
        self._best_pos_table.setHorizontalHeaderItem(7,
             QTableWidgetItem("Row"))
        self._best_pos_table.setHorizontalHeaderItem(8,
             QTableWidgetItem("Motor positions"))

        self._best_pos_popup_menu.addAction(\
             "Move to position",
              self.move_to_best_position_clicked)
        self._best_pos_table.contextMenuEvent = self.open_best_pos_popup_menu
        #self._best_pos_table.setHidden(True)

        screenShape = QDesktopWidget().screenGeometry()
        self.__heat_map_max_size = (screenShape.width() / 2,
                                    screenShape.height() / 2)

    def set_beamline_setup(self, beamline_setup_hwobj):
        self._beamline_setup_hwobj = beamline_setup_hwobj

    def set_associated_data_collection(self, data_collection):
        self.__associated_data_collection = data_collection
        self.__associated_grid = self.__associated_data_collection.grid
        acq_parameters = self.__associated_data_collection.acquisitions[0].\
                    acquisition_parameters

        if not data_collection.is_mesh():
            #x_array = numpy.linspace(0, acq_parameters.num_images, acq_parameters.num_images, dtype="int16")
            x_array = numpy.array([])
            y_array = numpy.array([])

            self._heat_map_plot.add_curve("spots_resolution",
                                          y_array,
                                          x_array,
                                          linestyle="None",
                                          label="Resolution",
                                          color="m",
                                          marker=".")
            self._heat_map_plot.add_curve("score",
                                          y_array,
                                          x_array,
                                          label="Total score",
                                          linestyle="None",
                                          color="b",
                                          marker=".")
            self._heat_map_plot.add_curve("spots_num",
                                          y_array,
                                          x_array,
                                          label="Number of spots",
                                          linestyle="None",
                                          color="b",
                                          marker=".")
            self._heat_map_plot.hide_all_curves()
            self._heat_map_plot.show_curve(self.__score_key)

            self.adjust_axes()
        else:
            if self.allow_adjust_size:
                grid_size = self.__associated_grid.get_size_pix()

                width = grid_size[0] * 5
                height = grid_size[1] * 5
                ratio = float(width) / height

                if width > self.__heat_map_max_size[0]:
                    width = self.__heat_map_max_size[0]
                    height = width / ratio
                if height > self.__heat_map_max_size[1]:
                    height = self.__heat_map_max_size[1]
                    width = height * ratio

                self._heat_map_plot.setFixedWidth(width)
                self._heat_map_plot.setFixedHeight(height)

            axis_range = self.__associated_grid.get_col_row_num()
            self._heat_map_plot.set_y_axis_limits((0, axis_range[1]))
            self._heat_map_plot.set_x_axis_limits((0, axis_range[0]))

            self._summary_textbrowser.append("<b>Mesh parameters</b>")
            grid_params = self.__associated_grid.get_properties()

            empty_array = numpy.zeros(acq_parameters.num_images).\
                reshape(grid_params["steps_x"], grid_params["steps_y"])
                                                                  
            self._heat_map_plot.plot_result(numpy.transpose(empty_array))

    def main_gbox_toggled(self, toggle):
        self._heat_map_plot.setHidden(not toggle)
        self._heat_map_tools_widget.setHidden(not toggle)
            
    def open_heat_map_popup_menu(self, context_event):
        point = QPoint(context_event.globalX(), 
                       context_event.globalY())
        self._heat_map_popup_menu.popup(point)

    def open_best_pos_popup_menu(self, context_event):
        if self._best_pos_table.rowCount() > 0:
            point = QPoint(context_event.globalX(), 
                           context_event.globalY())
            self._best_pos_popup_menu.popup(point)  

    def score_type_changed(self, score_type_index):
        if score_type_index == 0:
            self.__score_key = "spots_resolution"
        elif score_type_index == 1:
            self.__score_key = "score"
        elif score_type_index == 2:
            self.__score_key = "spots_num"

        if self.__results is not None:
            if self.__results[self.__score_key].ndim == 1:
                self._heat_map_plot.hide_all_curves()
                self._heat_map_plot.show_curve(self.__score_key)
                self.adjust_axes()
            else:
                self._heat_map_plot.plot_result(numpy.transpose(self.__results[self.__score_key]))

    def adjust_axes(self):
        #self._summary_textbrowser.clear()

        if self.__results:
            if self.__results[self.__score_key].ndim == 1:
                self._heat_map_plot.adjust_axes(self.__score_key)

                labels = []
                positions = numpy.linspace(0, self.__results[self.__score_key].max(), 5)

                if self.__score_key == "spots_resolution":
                    labels.append('inf')
                    for item in positions[1:]:  
                        labels.append("%.2f"%(1./item))
                else:
                    for item in positions:
                        labels.append("%d"% item)

                self._heat_map_plot.set_yticks(positions)
                self._heat_map_plot.set_ytick_labels(labels)

    def filter_min_slider_changed(self, value):
        self.__results_display = deepcopy(self.__results)

        for key in self.__results_display.keys():
            if key != "best_positions":
                filter_value = self.__results_display[key].max() * value / 100.0
                self.__results_display[key][self.__results_display[key] < filter_value] = 0

        if self.__results_display[self.__score_key].ndim == 1:
            self._heat_map_plot.update_curves(self.__results_display)
            self.adjust_axes()
        else:
            self._heat_map_plot.plot_result(numpy.transpose(self.__results_display[self.__score_key]))

    def mouse_moved(self, pos_x, pos_y):
        if self.__enable_continues_image_display and \
           self.__heatmap_clicked:
            if abs(int(self.__selected_x) - int(pos_x)) >= 1 or \
               abs(int(self.__selected_y) - int(pos_y)) >= 1:
                self.__selected_x = pos_x
                self.__selected_y = pos_y
                self.display_image_clicked()
                self.display_image_tooltip()

    def mouse_clicked(self, pos_x, pos_y):
        self.__heatmap_clicked = True
        self.__selected_x = pos_x
        self.__selected_y = pos_y

        if self.__associated_data_collection:
            msg = ""
            if self.__associated_grid: 
                image, line, self.selected_image_serial, image_path = \
                      self.get_image_parameters_from_coord()
                col, row = self.get_col_row_from_image_line(line, image)
                if self.__results:
                    msg = "Image: %d, value: %.1f" %(self.selected_image_serial,
                             self.__results[self.__score_key][col][row])
                else: 
                    msg = "Image: %d" % self.selected_image_serial

                label_im = deepcopy(self.__label_im)
                label_im[label_im != label_im[col, row]] = 0
            else:
                msg = "Image: %d" % int(pos_x) 
            self._image_info_label.setText(msg)

    def plot_double_clicked(self, event):
        self.move_to_selected_position()

    def mouse_left_plot(self):
        self.__heatmap_clicked = False
        self._heat_map_plot.setToolTip(self.__tooltip_text)

    def move_to_position_clicked(self):
        self.move_to_selected_position()

    def set_results(self, results, last_results=False):
        """
        Displays results on the widget
        """
        self.__results = results
        #self.__results_display = results

        if self.__results[self.__score_key].ndim == 1:
            self._heat_map_plot.update_curves(results)
            self.adjust_axes()
        else:
            self._heat_map_plot.plot_result(numpy.transpose(results[self.__score_key]))
        
        if last_results:
            self.__label_im, nb_labels = ndimage.label(self.__results['score'] > 0)
        #self.set_best_pos()

    def clean_result(self):
        """
        Method to clean heat map, summary log and table with best positions
        """
        #self.setEnabled(False)
        self.__results = None
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
        if self.__results[self.__score_key].ndim == 1:
            for col in range(self.__result.shape[0]):
                if self.__result[col] > 0:
                    self.create_centring_point(col + 0.5)
        else:
            #result_display = numpy.transpose(self.__result_display[self.__score_key])
            result_display = self.__results[self.__score_key]
            #step_x = pix_width / self.__result_display.shape[0]
            #step_y = pix_height / self.__result_display.shape[1]
            for col in range(result_display.shape[0]):
                for row in range(result_display.shape[1]):
                    if result_display[col][row] > 0:
                        #MD2
                        row = result_display.shape[1] - row - 1
                        self.create_centring_point(col + 0.5, row + 0.5)
        self._beamline_setup_hwobj.shape_history_hwobj.select_all_points()
  
    def display_image_clicked(self):
        """
        Displays image in image tracker (by default adxv)
        """
        image, line, image_num, image_path = self.get_image_parameters_from_coord()
        try:
            self._beamline_setup_hwobj.image_tracking_hwobj.load_image(image_path)
        except:
            pass

    def display_image_tooltip(self):
        image, line, self.selected_image_serial, image_path = \
              self.get_image_parameters_from_coord()
        tooltip_text = "Image no. %d" % self.selected_image_serial
        if self.__results is not None:
            try:
                col, row = self.get_col_row_from_image_line(line, image)
                tooltip_text += "\nTotal score: %.1f" %  \
                                self.__results['score'][col][row] +\
                                "\nNumber of spots: %d" % \
                                self.__results['spots_num'][col][row]
            except:
                pass
        self._heat_map_plot.setToolTip(tooltip_text)

    def toogle_continues_image_display(self):
        self.__enable_continues_image_display = \
            self.continues_display_action.isChecked()

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

            image, line, image_num = self.__associated_grid.\
                  get_image_from_col_row(coord_x, coord_y)
        else:
            image = int(self.__selected_x)
            line = 1
            image_num = image + self.__associated_data_collection.\
                  acquisitions[0].acquisition_parameters.first_image
        image_path = self.__associated_data_collection.acquisitions[0].\
                      path_template.get_image_path()
        image_path = image_path % image_num  
        return image, line, image_num, image_path

    def get_col_row_from_image_line(self, line, image):
        """
        Returns col and row from image and line
        """
        col, row = self.__associated_grid.get_col_row_from_line_image(line, image)
        ## TODO check if next line needs to be removed
        row = self.__results[self.__score_key].shape[1] - row - 1
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
        num_images = self.__associated_data_collection.acquisitions[0].\
                          acquisition_parameters.num_images
        osc_start = self.__associated_data_collection.acquisitions[0].\
                         acquisition_parameters.osc_start
        osc_range = self.__associated_data_collection.acquisitions[0].\
                         acquisition_parameters.osc_range

        omega = None
        if self.__associated_grid:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.\
                 get_motor_pos_from_col_row(coord_x, coord_y)
        else:
            omega = osc_start + osc_range * float(coord_x) / num_images
            (point_one, point_two) = self.__associated_data_collection.\
                      get_centred_positions()
            motor_pos_dict = self._beamline_setup_hwobj.diffractometer_hwobj.\
                      get_point_from_line(point_one, point_two, coord_x, num_images)
            motor_pos_dict['phi'] = omega
        self._beamline_setup_hwobj.shape_history_hwobj.\
             create_centring_point(True, {"motors": motor_pos_dict})

    def create_helical_line_clicked(self):
        motor_pos_dict = self.__associated_grid.\
              get_motor_pos_from_col_row(self.__selected_x, self.__selected_y)
        self._beamline_setup_hwobj.shape_history_hwobj.create_auto_line(motor_pos_dict)

    def rotate_and_create_helical_line_clicked(self):
        self.move_to_selected_position()
        self._beamline_setup_hwobj.diffractometer_hwobj.move_omega_relative(90)
        self._beamline_setup_hwobj.shape_history_hwobj.create_auto_line()

    def move_to_selected_position(self):
        """
        Descript. : Moves to grid position
        Args.     : x and y are positions in micrometers starting from left 
                    top corner (as graphical coordinates)
        """
        osc_start = self.__associated_data_collection.acquisitions[0].\
                         acquisition_parameters.osc_start
        osc_range = self.__associated_data_collection.acquisitions[0].\
                         acquisition_parameters.osc_range
        if self.__associated_grid:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.\
                 get_motor_pos_from_col_row(self.__selected_x, self.__selected_y)
        else:
            num_images = self.__associated_data_collection.\
                      acquisitions[0].acquisition_parameters.num_images - 1
            (point_one, point_two) = self.__associated_data_collection.\
                      get_centred_positions()
            motor_pos_dict = self._beamline_setup_hwobj.diffractometer_hwobj.\
                      get_point_from_line(point_one, point_two, 
                      int(self.__selected_x), num_images)

        self._beamline_setup_hwobj.diffractometer_hwobj.\
             move_to_motors_positions(motor_pos_dict, wait=True)

    def set_best_pos(self):
        """
        Descript. : Displays 10 (if exists) best positions, estimated
                    by fast processing.
        """
        self._best_pos_table.setRowCount(len(self.__results.get("best_positions", [])))
        for row, best_pos in enumerate(self.__results.get("best_positions", [])):
            self._best_pos_table.setItem(row, 0, QTableWidgetItem("%d" \
                 % (best_pos.get("index") + 1)))  
            self._best_pos_table.setItem(row, 1, QTableWidgetItem("%.2f"\
                 % (best_pos.get("score"))))
            self._best_pos_table.setItem(row, 2, QTableWidgetItem("%d"\
                 % (best_pos.get("spots_num"))))
            self._best_pos_table.setItem(row, 3, QTableWidgetItem("%.2f"\
                 % (best_pos.get("spots_int_aver"))))
            self._best_pos_table.setItem(row, 4, QTableWidgetItem("%.2f"\
                 % (best_pos.get("spots_resolution"))))
            self._best_pos_table.setItem(row, 5, QTableWidgetItem(\
                 str(best_pos.get("filename"))))
            self._best_pos_table.setItem(row, 6, QTableWidgetItem("%d" \
                 % (best_pos.get("col"))))
            self._best_pos_table.setItem(row, 7, QTableWidgetItem("%d"\
                 % (best_pos.get("row"))))
            if best_pos["cpos"]:
                self._best_pos_table.setItem(row, 8, QTableWidgetItem(\
                 str(best_pos["cpos"])))
        self._best_pos_table.setSortingEnabled(True)

    def move_to_best_position_clicked(self):
        """
        Moves diffractometer motors to the selected position
        """
        if self._best_pos_table.currentRow() > -1:
            self._beamline_setup_hwobj.diffractometer_hwobj.\
                move_to_motors_positions(self.__results["best_positions"]\
                [self._best_pos_table.currentRow()]["cpos"])

    def create_best_centring_point_clicked(self):
        """
        Creates a new centring point based on the selected point
        from the table of best positions.
        """
        if self._best_pos_table.currentRow() > -1:
            self._beamline_setup_hwobj.diffractometer_hwobj.\
                create_centring_point(self.__results["best_positions"]\
                [self._best_pos_table.currentRow()].get("cpos").as_dict())   

    def display_best_image_clicked(self):
        """
        Displays image (clicked from best position table) in ADXV
        """
        if self._best_pos_table.currentRow() > -1:
            image_path = self.__results["best_positions"]\
               [self._best_pos_table.currentRow()].get("filename")
            self._beamline_setup_hwobj.image_tracking_hwobj.\
               load_image(image_path)

    def relaunch_processing_clicked(self):
        """
        Relaunches parallel processing
        """
        if self.__associated_data_collection and self.__associated_grid:
            self._beamline_setup_hwobj.parallel_processing_hwobj.\
                 run_processing(self.__associated_data_collection)
