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
import numpy as np
import gevent
from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

from widgets.Qt4_matplot_widget import TwoDimenisonalPlotWidget

__credits__ = ["MXCuBE colaboration"]
__category__ = "EMBL"


class Qt4_StillCollectionPreviewBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
	
        # Hardware objects ----------------------------------------------------
        self.beamline_setup_hwobj = None
        self.parallel_processing_hwobj = None

        # Internal values -----------------------------------------------------
        self.grid_properties = None
        self.info_dict = {'grid_cell': -1,
                          'comp_cell': -1}
        self.params_dict = None
        self.results = None
        self.score_type = "score"
        self.score_type_list = ("score", "spots_resolution", "spots_num")
        self.comp_table_item_fixed = False

        # Properties ----------------------------------------------------------
        self.addProperty('cell_size', 'integer', 22)
        self.addProperty('hwobj_beamline_setup', 'string', '/beamline-setup')
        #self.addProperty('hwobj_parallel_processing', 'string', '/parallel-processing')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.grid_widget = QWidget(self)
        self.grid_table = QTableWidget(self.grid_widget)
        self.grid_cell_label = QLabel("Selected grid cell: A1", self.grid_widget)
        self.grid_properties_combo = QComboBox(self)

        self.inverted_rows_cbox = QCheckBox("Inverted rows", self.grid_widget)
        self.image_tracking_cbox = QCheckBox("Life update", self.grid_widget)
        self.score_type_combo = QComboBox(self.grid_widget)
        self.save_hit_plot_button = QPushButton("Save hit plot", self.grid_widget)

        self.comp_widget = QWidget(self)
        self.comp_cell_label = QLabel("Selected compartment cell: A1", self.comp_widget)
        self.comp_table = QTableWidget(self.comp_widget)
        self.hit_map_plot = TwoDimenisonalPlotWidget(self.comp_widget)

        # Layout --------------------------------------------------------------
        _grid_vlayout = QVBoxLayout(self.grid_widget)
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

        _comp_vlayout = QVBoxLayout(self.comp_widget)
        _comp_vlayout.addWidget(self.comp_cell_label)
        _comp_vlayout.addWidget(self.comp_table)
        _comp_vlayout.addWidget(self.hit_map_plot)
        _comp_vlayout.setSpacing(2)
        _comp_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QHBoxLayout(self)
        _main_vlayout.addWidget(self.grid_widget)
        _main_vlayout.addWidget(self.comp_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.grid_table.cellClicked.connect(self.grid_cell_clicked)
        self.comp_table.cellClicked.connect(self.comp_cell_clicked)
        self.comp_table.cellEntered.connect(self.comp_cell_entered)
        self.grid_properties_combo.activated.connect(self.grid_properties_combo_changed)
        self.score_type_combo.activated.connect(self.score_type_changed)
        self.save_hit_plot_button.clicked.connect(self.save_hit_plot)
        self.hit_map_plot.mouseMovedSignal.connect(self.hit_map_mouse_moved)

        # Other ---------------------------------------------------------------
        self.grid_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_table.setMouseTracking(True)

        self.comp_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.comp_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.comp_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.comp_table.setMouseTracking(True)

        for score_type in ("Score", "Resolution", "Number of spots"):
            self.score_type_combo.addItem(score_type)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'hwobj_beamline_setup':
            if self.parallel_processing_hwobj is not None:
                self.parallel_processing_hwobj.disconnect("processingFinished",
                                                          self.processing_finished)
                self.parallel_processing_hwobj.disconnect("processingFailed",
                                                          self.processing_failed)
                self.parallel_processing_hwobj.disconnect("processingFrame",
                                                          self.processing_frame_changed)
                self.parallel_processing_hwobj.disconnect("paralleProcessingResults",
                                                          self.set_results)

            self.beamline_setup_hwobj = self.getHardwareObject(new_value)
            self.parallel_processing_hwobj = self.beamline_setup_hwobj.parallel_processing_hwobj

            if self.parallel_processing_hwobj is not None:
                self.parallel_processing_hwobj.connect("processingFinished",
                                                       self.processing_finished)
                self.parallel_processing_hwobj.connect("processingFailed",
                                                       self.processing_failed)
                self.parallel_processing_hwobj.connect("processingFrame",
                                                       self.processing_frame_changed)
                self.parallel_processing_hwobj.connect("paralleProcessingResults",
                                                       self.set_results)

                for grid_property in self.parallel_processing_hwobj.get_available_grid_properties():
                    self.grid_properties_combo.addItem(str(grid_property))
                self.grid_properties_combo.blockSignals(True)
                self.grid_properties_combo.setCurrentIndex(0)
                self.grid_properties_combo.blockSignals(False)
                self.init_gui()
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def init_gui(self):
        self.image_tracking_cbox.setChecked(True)

        self.grid_properties = self.parallel_processing_hwobj.get_current_grid_properties()

        self.inverted_rows_cbox.setChecked(self.grid_properties["inverted_rows"])
        self.grid_table.setColumnCount(self.grid_properties["grid_num_col"])
        self.grid_table.setRowCount(self.grid_properties["grid_num_row"])

        for col in range(self.grid_properties["grid_num_col"]):
            temp_header_item = QTableWidgetItem("%d" % (col + 1))
            self.grid_table.setHorizontalHeaderItem(col, temp_header_item)
            self.grid_table.setColumnWidth(col, self['cell_size'])

        for row in range(self.grid_properties["grid_num_row"]):
            temp_header_item = QTableWidgetItem(chr(65 + row))
            self.grid_table.setVerticalHeaderItem(row, temp_header_item)
            self.grid_table.setRowHeight(row, self['cell_size'])

        for col in range(self.grid_properties["grid_num_col"]):
            for row in range(self.grid_properties["grid_num_row"]):
                temp_item = QTableWidgetItem()
                self.grid_table.setItem(row, col, temp_item) 

        table_width = self['cell_size'] * (self.grid_properties["grid_num_col"] + 1) + 5
        table_height = self['cell_size'] * (self.grid_properties["grid_num_row"] + 1) + 5
        self.grid_table.setFixedWidth(table_width)
        self.grid_table.setFixedHeight(table_height)

        self.comp_table.setColumnCount(self.grid_properties["comp_num_col"])
        self.comp_table.setRowCount(self.grid_properties["comp_num_row"])
 
        for col in range(self.grid_properties["comp_num_col"]):
            temp_header_item = QTableWidgetItem("%d" % (col + 1))
            self.comp_table.setHorizontalHeaderItem(col, temp_header_item)
            self.comp_table.setColumnWidth(col, self['cell_size'])

        for row in range(self.grid_properties["comp_num_row"]):
            temp_header_item = QTableWidgetItem(chr(65 + row))
            self.comp_table.setVerticalHeaderItem(row, temp_header_item)
            self.comp_table.setRowHeight(row, self['cell_size'])

        for col in range(self.grid_properties["comp_num_col"]):
            for row in range(self.grid_properties["comp_num_row"]):
                temp_item = QTableWidgetItem()
                self.comp_table.setItem(row, col, temp_item)

        table_width = self['cell_size'] * (self.grid_properties["comp_num_col"] + 1) + 5 
        table_height = self['cell_size'] * (self.grid_properties["comp_num_row"] + 1) + 5
        self.comp_table.setFixedWidth(table_width)
        self.comp_table.setFixedHeight(table_height)

        for score_type in self.score_type_list:
            self.hit_map_plot.add_curve(score_type,
                                        np.array([]),
                                        np.array([]),
                                        linestyle="None",
                                        label=score_type,
                                        color="m",
                                        marker="s")
        self.hit_map_plot.hide_all_curves()
        self.hit_map_plot.show_curve(self.score_type)

    def save_hit_plot(self):
        file_types = "PNG (*.png)"
        
        filename = str(QFileDialog.getSaveFileName(\
            self, "Choose a filename to save under",
            os.path.expanduser("~"), file_types))
        #defaultSuffix

        if len(filename):
            gevent.spawn(self.parallel_processing_hwobj.plot_processing_results_task,
                         self.score_type, filename)
            #self.parallel_processing_hwobj.plot_processing_results(self.score_type, filename)

    def grid_cell_clicked(self, row, col):
        self.info_dict["grid_cell"] = row * self.grid_properties["grid_num_row"] + col
        self.grid_cell_label.setText("Current grid cell: %s%d" % (chr(65 + row), col + 1))
        #self.update_grid_table()
        self.update_comp_table() 

    def comp_cell_clicked(self, row, col):
        self.comp_table_item_fixed != self.comp_table_item_fixed

    def comp_cell_entered(self, row, col):
        if not self.comp_table_item_fixed:
            self.comp_cell_label.setText("Current compartment cell: %s%d" % \
                                         (chr(65 + row), col + 1))
        
            if self.params_dict is not None:  
                start_index = (self.info_dict["grid_cell"] * \
                               self.grid_properties["comp_num_col"] * \
                               self.grid_properties["comp_num_row"] +
                               row * self.grid_properties["comp_num_row"] + \
                               col) * \
                              self.params_dict["num_images_per_trigger"]
                end_index = min(start_index + self.params_dict["num_images_per_trigger"],
                                self.results[self.score_type].size)
 
                if self.results is not None:
                    if start_index < self.results[self.score_type].size:
                        data = {self.score_type: self.results[self.score_type][start_index:end_index],
                                "x_array": np.linspace(start_index, end_index, end_index - start_index, dtype=np.int32)}
                        self.hit_map_plot.update_curves(data)
                        self.hit_map_plot.set_x_axis_limits((start_index - 0.5, end_index + 0.5))
                        self.hit_map_plot.adjust_axes(self.score_type)

    def grid_properties_combo_changed(self, index):
        self.parallel_processing_hwobj.set_current_grid_index(index)
        self.init_gui()

    def score_type_changed(self, index):
        self.score_type = self.score_type_list[index]

    def hit_map_mouse_moved(self, pos_x, pos_y):
        if self.params_dict is not None:
            filename = self.params_dict['template'] % (self.params_dict['run_number'], int(pos_x))
            try:
                self.beamline_setup_hwobj.image_tracking_hwobj.load_image(filename)
            except:
                pass 

    def processing_finished(self):
        #self.info_dict["grid_cell"] = -1
        self.info_dict["comp_cell"] = -1
        self.update_grid_table() 

    def processing_failed(self):
        pass

    def set_results(self, results, params_dict, last_result):
        self.params_dict = params_dict
        self.results = results
        self.hit_map_plot.set_x_axis_limits((0, self.params_dict["num_images_per_trigger"]))

    def processing_frame_changed(self, frame_num):
        if not self.image_tracking_cbox.isChecked():
            return

        self.info_dict["frame_num"] = frame_num
        self.info_dict["comp_num"] = frame_num / self.params_dict["num_images_per_trigger"]

        grid_cell = self.info_dict["comp_num"] / \
                    self.grid_properties["comp_num_col"] / \
                    self.grid_properties["comp_num_row"]

        if self.info_dict["grid_cell"] != grid_cell:
            self.info_dict["grid_cell"] = grid_cell
            self.info_dict["comp_cell"] = -1
            self.update_grid_table()

        comp_cell = (frame_num - grid_cell * \
                     self.grid_properties["comp_num_col"] * \
                     self.grid_properties["comp_num_row"] * \
                     self.params_dict["num_images_per_trigger"]) / \
                     self.params_dict["num_images_per_trigger"]

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

                start_index = grid_cell  * \
                              self.grid_properties["comp_num_col"] * \
                              self.grid_properties["comp_num_row"] * \
                              self.params_dict["num_images_per_trigger"]
                end_index = min(start_index + \
                                self.grid_properties["comp_num_col"] * \
                                self.grid_properties["comp_num_row"] * \
                                self.params_dict["num_images_per_trigger"],
                                self.results[self.score_type].size -1)

                color = Qt4_widget_colors.LIGHT_GRAY
                if grid_cell == self.info_dict["grid_cell"]:
                    color = Qt4_widget_colors.DARK_GREEN
                elif start_index < self.results[self.score_type].size:
                     if self.results[self.score_type][start_index:end_index].max() > 0:
                         color = Qt4_widget_colors.LIGHT_BLUE
                     else:
                         color = Qt4_widget_colors.WHITE
                grid_table_item.setBackground(color)

    def update_comp_table(self):
        if self.params_dict is None: 
            return

        for row in range(self.grid_properties["comp_num_row"]):
            for col in range(self.grid_properties["comp_num_col"]):

                if self.inverted_rows_cbox.isChecked() and row % 2:
                    table_col = self.grid_properties["comp_num_col"] - col -1
                else:
                    table_col = col

                comp_table_item = self.comp_table.item(row, table_col)
                start_index = self.info_dict["grid_cell"] * \
                              self.grid_properties["comp_num_col"] * \
                              self.grid_properties["comp_num_row"] * \
                              self.params_dict["num_images_per_trigger"] + \
                              (row * self.grid_properties["comp_num_row"] + col) * \
                              self.params_dict["num_images_per_trigger"]
                              #self.grid_properties["comp_num_col"]
                end_index = min(start_index + self.params_dict["num_images_per_trigger"],
                                self.results[self.score_type].size -1)
                color = Qt4_widget_colors.LIGHT_GRAY
                if self.info_dict["comp_cell"] == row * self.grid_properties["comp_num_row"] + col:
                    color = Qt4_widget_colors.DARK_GREEN
                elif start_index < self.results[self.score_type].size:
                     if self.results[self.score_type][start_index:end_index].max() > 0:
                         color = Qt4_widget_colors.LIGHT_BLUE
                     else:
                         color = Qt4_widget_colors.WHITE
                comp_table_item.setBackground(color)
