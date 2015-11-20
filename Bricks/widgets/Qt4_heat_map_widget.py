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

from PyQt4 import QtGui
from PyQt4 import QtCore

from copy import copy
from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_matplot_widget import TwoDimenisonalPlotWidget


class HeatMapWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName('heat_map_widget')

        # Properties ---------------------------------------------------------- 
        #self.__half_widget_size = 900

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None
        self._data_analysis_hwobj = None

        # Internal values -----------------------------------------------------
        self.__results = None
        self.__result_display = None
        self.__associated_grid = None
        self.__associated_data_collection = None
        self.__selected_x = 0
        self.__selected_y = 0
        self.__selected_image_serial = 0
        #self.__axis_x_range = None
        #self.__axis_y_range = None
        self.__is_map_plot = None
        self.__score_type_index = 0
        self.__max_value = 0
        self.__filter_min_value = 0
        self.__best_pos_list = None
        self.__heat_map_max_size = []

        # Graphic elements ----------------------------------------------------
        self._heat_map_gbox = QtGui.QGroupBox('Heat map', self)
        #self._heat_map_plot = QtBlissGraph(self._heat_map_gbox)
        self._heat_map_plot = TwoDimenisonalPlotWidget(self)
        self._heat_map_popup_menu = QtGui.QMenu(self._heat_map_gbox)
        self._image_info_label = QtGui.QLabel("Image: #, value #", self._heat_map_gbox)

        self._heat_map_tools_widget = QtGui.QWidget(self._heat_map_gbox)
        score_type_label = QtGui.QLabel("Score type: ", self._heat_map_tools_widget)
        self._score_type_cbox = QtGui.QComboBox(self._heat_map_tools_widget)

        _threshold_label = QtGui.QLabel("Threshold: ", self._heat_map_tools_widget)
        self._threshold_slider = QtGui.QSlider(QtCore.Qt.Horizontal, 
               self._heat_map_tools_widget)
        self._create_points_button = QtGui.QPushButton("Create centring points", 
             self._heat_map_tools_widget)

        self._best_pos_gbox = QtGui.QGroupBox("Best positions", self)
        self._best_pos_table = QtGui.QTableWidget(self._best_pos_gbox)

        # Layout --------------------------------------------------------------
        _heat_map_tools_hlayout = QtGui.QHBoxLayout(self._heat_map_tools_widget)
        _heat_map_tools_hlayout.addWidget(score_type_label)
        _heat_map_tools_hlayout.addWidget(self._score_type_cbox)
        _heat_map_tools_hlayout.addWidget(_threshold_label)
        _heat_map_tools_hlayout.addWidget(self._threshold_slider)
        _heat_map_tools_hlayout.addStretch(0)
        _heat_map_tools_hlayout.addWidget(self._create_points_button)
        _heat_map_tools_hlayout.setSpacing(2)
        _heat_map_tools_hlayout.setContentsMargins(0, 0, 0, 0)

        _heat_map_gbox_vlayout = QtGui.QVBoxLayout(self._heat_map_gbox)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_plot)
        _heat_map_gbox_vlayout.addWidget(self._image_info_label)
        _heat_map_gbox_vlayout.addWidget(self._heat_map_tools_widget)
        _heat_map_gbox_vlayout.setSpacing(2)
        _heat_map_gbox_vlayout.setContentsMargins(0, 4, 0, 0)
        
        _best_postition_gbox_vlayout = QtGui.QVBoxLayout(self._best_pos_gbox)
        _best_postition_gbox_vlayout.addWidget(self._best_pos_table)
        _best_postition_gbox_vlayout.setSpacing(2)
        _best_postition_gbox_vlayout.setContentsMargins(0, 4, 0, 0)

        _main_hlayout = QtGui.QVBoxLayout(self)
        _main_hlayout.addWidget(self._heat_map_gbox)
        _main_hlayout.addWidget(self._best_pos_gbox)
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self._image_info_label.setAlignment(QtCore.Qt.AlignRight)
        self._image_info_label.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                             QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------
        self._heat_map_plot.mouseClickedSignal.connect(self.mouse_clicked)
        self._score_type_cbox.activated.connect(self.score_type_changed)
        self._threshold_slider.valueChanged.connect(\
             self.filter_min_slider_changed)
        self._create_points_button.clicked.connect(\
             self.create_points_clicked)

        # Other ----------------------------------------------------------------
        #self._heat_map_plot.canvas().setMouseTracking(False)
        #Qt4_widget_colors.set_widget_color(self._heat_map_plot, QtCore.Qt.white)
        #self._heat_map_plot.mouseDoubleClickEvent = self.plot_double_clicked
        #self._heat_map_plot.setAxisAutoScale(False)
        #self._heat_map_plot.enableZoom(True)
        #self._heat_map_plot.showGrid()
        tooltip_text = "Double click to move to the position. " + \
                       "Right click to open menu."
        self._heat_map_plot.setToolTip(tooltip_text) 

        #self._heat_map_popup_menu.addAction(\
        #     "Reset zoom", self._heat_map_plot.zoomReset)
        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(\
             "Move to position", self.move_to_position_clicked)
        self._heat_map_popup_menu.addAction(\
             "Create centring point", self.create_centring_point_clicked)
        self._heat_map_popup_menu.addSeparator()
        self._heat_map_popup_menu.addAction(\
             "Open image in ADXV", self.display_image_clicked)
        self._heat_map_plot.contextMenuEvent = self.open_heat_map_popup_menu

        score_types = ["Score", "Spots num", "Int aver.", "Resolution"]
        for score_type in score_types:
            self._score_type_cbox.addItem(score_type)
        self._score_type_cbox.setMaximumWidth(200)

        #self._threshold_slider.setTickmarks(QtGui.QSlider.Below)
        self._threshold_slider.setRange(0, 100)
        self._threshold_slider.setTickInterval(5)
        self._threshold_slider.setFixedWidth(200)
        self._threshold_slider.setTracking(False)

        font = self._best_pos_table.font()
        font.setPointSize(8)
        self._best_pos_table.setFont(font)
        self._best_pos_table.setEditTriggers(\
             QtGui.QAbstractItemView.NoEditTriggers)
        self._best_pos_table.setColumnCount(9)
        self._best_pos_table.horizontalHeader().setStretchLastSection(True)
     
        self._best_pos_table.setHorizontalHeaderItem(0, \
            QtGui.QTableWidgetItem("No."))
        for score_type in enumerate(score_types):
            self._best_pos_table.setHorizontalHeaderItem(\
                 score_type[0] + 1, QtGui.QTableWidgetItem(score_type[1]))

        self._best_pos_table.setHorizontalHeaderItem(5,
             QtGui.QTableWidgetItem("Path"))
        self._best_pos_table.setHorizontalHeaderItem(6,
             QtGui.QTableWidgetItem("Col"))
        self._best_pos_table.setHorizontalHeaderItem(7,
             QtGui.QTableWidgetItem("Row"))
        self._best_pos_table.setHorizontalHeaderItem(8,
             QtGui.QTableWidgetItem("Motor positions"))

        screenShape = QtGui.QDesktopWidget().screenGeometry()
        self.__heat_map_max_size = (screenShape.width() / 2,
                                    screenShape.height() / 2)

    def set_beamline_setup(self, beamline_setup_hwobj):
        self._beamline_setup_hwobj = beamline_setup_hwobj
        self._data_analysis_hwobj = self._beamline_setup_hwobj.data_analysis_hwobj 

    def set_associated_data_collection(self, data_collection):
        self.__associated_data_collection = data_collection
        
        #self._heat_map_plot.set_x_axis_limits((- 0.5, data_collection.\
        #      acquisitions[0].acquisition_parameters.num_images - 0.5))

    def set_associated_grid(self, grid):
        if grid is None:
            self.__is_map_plot = False
            #self._heat_map_plot.x1Label("Image num")
            #self._heat_map_plot.y1Label("Score")
        else:
            self.__is_map_plot = True
            self.__associated_grid = grid
            axis_range = self.__associated_grid.get_col_row_num()
            grid_size = self.__associated_grid.get_size_pix()

            width = grid_size[0] * 10
            height = grid_size[1] * 10
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
            self._heat_map_plot.set_x_axis_limits((- 0.5, axis_range[0] - 0.5))
            self._heat_map_plot.set_y_axis_limits((- 0.5, axis_range[1] - 0.5))

    def main_gbox_toggled(self, toggle):
        self._heat_map_plot.setHidden(not toggle)
        self._heat_map_tools_widget.setHidden(not toggle)
            
    def open_heat_map_popup_menu(self, context_event):
        point = QtCore.QPoint(context_event.globalX(), 
                          context_event.globalY())
        self._heat_map_popup_menu.popup(point)

    def open_best_pos_popup_menu(self, context_event):
        point = QtCore.QPoint(context_event.globalX(), 
                          context_event.globalY())
        self._best_pos_popup_menu.popup(point)  

    def score_type_changed(self, score_type_index):
        self.__score_type_index = score_type_index
        #self._threshold_slider.setValue(0)
        self.refresh()         

    def refresh(self):
        if self.__results is None:
            return         

        self.__result_display = copy(self.__results["score"])
        if self.__score_type_index == 0:
            self.__result_display = copy(self.__results["score"])
        elif self.__score_type_index == 1:    
            self.__result_display = copy(self.__results["spots_num"])
        elif self.__score_type_index == 2:
            self.__result_display = copy(self.__results["spots_int_aver"])
        elif self.__score_type_index == 3:
            self.__result_display = copy(self.__results["spots_resolution"])
        elif self.__score_type_index == 4:
            self.__result_display = copy(self.__results["image_num"])

        #self.__max_value = self.__result_display.max()
        self.__filter_min_value = self.__result_display.max() * \
             self._threshold_slider.value() / 100.0
        self.__result_display[self.__result_display < self.__filter_min_value] = 0
      
        if len(self.__result_display.shape) == 1:
            #Displaying results as a line
            x_data = numpy.arange(self.__result_display.shape[0])
            #self.__axis_x_range = [0, self.__result_display.shape[0] - 1]
            #self.__axis_y_range = [self.__result_display.min(), 
            #                       self.__result_display.max()]
            #self._heat_map_plot.clearcurves()
            #self._heat_map_plot.setx1timescale(False)
            #self._heat_map_plot.setY1AxisLimits(self.__result_display.min(),
            #                                    self.__result_display.max())
            self._heat_map_plot.newcurve("Dozor result", x_data, self.__result_display)
        else:
            #2D plot
            #self._heat_map_plot.imagePlot(self.__result_display, ymirror=False)
            #self._heat_map_plot.plotImage.show()
            self._heat_map_plot.plot_result(self.__result_display)
        #self._heat_map_plot.setX1AxisLimits(0, self.__axis_x_range[1])
        #self._heat_map_plot.setY1AxisLimits(0, self.__axis_y_range[1])
        #self._heat_map_plot.replot() 

    def filter_min_slider_changed(self, value):
        self.refresh()

    def mouse_clicked(self, pos_x, pos_y):
        self.__selected_x = pos_x
        self.__selected_y = pos_y
        image, line, self.selected_image_serial, image_path = \
              self.get_image_parameters_from_coord()
        try:
           col, row = self.get_col_row_from_image_line(line, image)
           msg = "Image: %d, value: %.3f" %(self.selected_image_serial,
                 self.__result_display[row][col])
        except:
           msg = "Image: %d" % self.selected_image_serial
        self._image_info_label.setText(msg)

    def plot_double_clicked(self, event):
        self.move_to_selected_position()

    def move_to_position_clicked(self):
        self.move_to_selected_position()

    def set_results(self, results, last_results=False):
        """
        Descript. : Displays results on the widget
        """
        self._heat_map_gbox.setEnabled(True)
        self.__results = results
        self.refresh()
        if last_results:
            self.set_best_pos()

    def clean_result(self):
        self.__results = None
        #self.__axis_x_range = None
        #self.__axis_y_range = None
        self.__associated_grid = None
        self.__associated_data_collection = None
        self._threshold_slider.setValue(0)

        #if self._heat_map_plot.plotImage is not None:
        #    self._heat_map_plot.plotImage.hide()
        #self._heat_map_plot.clearcurves()
        #self._heat_map_plot.setTitle("")
        self._best_pos_table.setRowCount(0)

    def create_centring_point_clicked(self):
        self.create_centring_point()

    def create_points_clicked(self):
        """
        Descript. : creates new centring points based on each image score.
                    All images are checked and if the value
                    is over the threshold then screen x and y coordinates
                    are estimated.
        """
        if self.__is_map_plot:
            result_display = numpy.transpose(self.__result_display)
            #step_x = pix_width / self.__result_display.shape[0]
            #step_y = pix_height / self.__result_display.shape[1]
            for col in range(result_display.shape[0]):
                for row in range(result_display.shape[1]):
                    if result_display[col][row] > 0:
                        #MD2
                        row = result_display.shape[1] - row - 1
                        self.create_centring_point(col + 0.5, row + 0.5)
        else:
            for col in range(self.__result_display.shape[0]):
                if self.__result_display[col] > 0:
                    self.create_centring_point(col + 0.5)
        self._beamline_setup_hwobj.shape_history_hwobj.select_all_cpos()
  
    def display_image_clicked(self):
        """
        Decript. : displays image in image tracker (by default adxv)
        """
        image, line, image_num, image_path = self.get_image_parameters_from_coord()
        if self._beamline_setup_hwobj.image_tracking_hwobj is not None:
            self._beamline_setup_hwobj.image_tracking_hwobj.load_image(image_path)

    def get_image_parameters_from_coord(self, coord_x=None, coord_y=None):
        """
        Descript. : returns image parameters for selected heat map frame
        """
        if not coord_x:
            coord_x = self.__selected_x
        if not coord_y:
            coord_y = self.__selected_y

        if self.__is_map_plot:
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
        if self._data_analysis_hwobj is not None:
           return self._data_analysis_hwobj.get_col_row_from_line_image(line, image) 
        else:
           return None, None

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
        if self.__is_map_plot:
            self.__associated_grid.set_osc_range(osc_range)
            motor_pos_dict = self.__associated_grid.\
                 get_motor_pos_from_col_row(coord_x, coord_y)
        else:
            omega = osc_start + osc_range * float(coord_x) / num_images
            (point_one, point_two) = self.__associated_data_collection.\
                      get_centred_positions()
            motor_pos_dict = self._beamline_setup_hwobj.diffractometer_hwobj.\
                      get_point_from_line(point_one, point_two, coord_x, num_images)
        self._beamline_setup_hwobj.diffractometer_hwobj.\
             create_centring_point(motor_pos_dict, omega)

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
        if self.__is_map_plot:
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
             move_to_motors_positions(motor_pos_dict)

    def set_best_pos(self):
        """
        Descript. : Displays 10 (if exists) best positions, estimated
                    by fast processing.
        """
        self._best_pos_table.setRowCount(len(self.__results["best_positions"]))
        for row in range(len(self.__results["best_positions"])):
            self._best_pos_table.setItem(row, 0, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("index") + 1)))  
            self._best_pos_table.setItem(row, 1, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("score"))))
            self._best_pos_table.setItem(row, 2, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("spots_num"))))
            self._best_pos_table.setItem(row, 3, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("spots_int_aver"))))
            self._best_pos_table.setItem(row, 4, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("spots_resolution"))))
            self._best_pos_table.setItem(row, 5, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("filename"))))
            self._best_pos_table.setItem(row, 6, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("col"))))
            self._best_pos_table.setItem(row, 7, QtGui.QTableWidgetItem(\
                 str(self.__results["best_positions"][row].get("row"))))
            if self.__results["best_positions"][row]["cpos"]:
                self._best_pos_table.setItem(row, 8, QtGui.QTableWidgetItem(\
                   self.__results["best_positions"][row]["cpos"].as_str()))

    def move_to_best_position_clicked(self):
        if self._best_pos_table.currentRow() > -1:
            self._beamline_setup_hwobj.diffractometer_hwobj.move_to_motors_positions(\
                self.__results["best_positions"][self._best_pos_table.currentRow()].get("cpos").as_dict())

    def create_best_centring_point_clicked(self):
        if self._best_pos_table.currentRow() > -1:
            self._beamline_setup_hwobj.diffractometer_hwobj.create_centring_point(\
                self.__results["best_positions"][self._best_pos_table.currentRow()].get("cpos").as_dict())   

    def display_best_image_clicked(self):
        if self._best_pos_table.currentRow() > -1:
            image_path = self.__results["best_positions"][self._best_pos_table.currentRow()].get("filename")
            self._beamline_setup_hwobj.image_tracking_hwobj.load_image(image_path)
