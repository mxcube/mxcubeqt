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
import logging
from copy import deepcopy

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import queue_model_objects_v1 as queue_model_objects 
import Qt4_queue_item
import Qt4_GraphicsManager as graphics_manager

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN


class CreateAdvancedScanWidget(CreateTaskBase):
    """
    Descript. :
    """

    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, QtCore.Qt.WindowFlags(fl), 'Advanced')

        if not name:
            self.setObjectName("create_advanced_Scan_widget")

        # Hardware objects ----------------------------------------------------
        self.__mini_diff_hwobj = None
 
        # Internal variables --------------------------------------------------
        self.init_models()
        self._prev_pos = None
        self._current_pos = None
        self._list_item_map = {}
        self.init_models()

        self.__current_motor_positions = {}
        self.__list_items = {}
        self.__grid_list = []

        self.__beam_info = {}
        self.__spacing = [0, 0]

        # Graphic elements ----------------------------------------------------
        self.mesh_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
                               'ui_files/Qt4_mesh_widget_layout.ui'))

        self._acq_widget =  AcquisitionWidget(self, "acquisition_widget",
             layout='vertical', acq_params=self._acquisition_parameters,
             path_template=self._path_template)

        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_gbox.setObjectName('data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox,
                                   'create_dc_path_widget',
                                   data_model = self._path_template,
                                   layout = 'vertical')

        # Layout --------------------------------------------------------------
        self._data_path_gbox_layout = QtGui.QVBoxLayout(self)
        self._data_path_gbox_layout.addWidget(self._data_path_widget)
        self._data_path_gbox_layout.setSpacing(0)
        self._data_path_gbox_layout.setContentsMargins(0,0,0,0)
        self._data_path_gbox.setLayout(self._data_path_gbox_layout)

        _main_vlayout = QtGui.QVBoxLayout(self) 
        _main_vlayout.addWidget(self.mesh_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_gbox)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.\
             connect(self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        self.connect(self._data_path_widget,
                     QtCore.SIGNAL("pathTemplateChanged"),
                     self.handle_path_conflict)

        self.mesh_widget.draw_button.clicked.connect(self.draw_button_clicked)
        self.mesh_widget.remove_button.clicked.connect(self.delete_drawing_clicked)
        self.mesh_widget.hor_spacing_ledit.textChanged.connect(self.set_hspace)
        self.mesh_widget.ver_spacing_ledit.textChanged.connect(self.set_vspace)
        self.mesh_widget.mesh_treewidget.currentItemChanged.connect(\
             self.mesh_treewidget_current_item_changed)
        self.mesh_widget.visibility_button.clicked.\
             connect(self.toggle_visibility_grid)

    def init_models(self):
        """
        Descript. :
        """
        CreateTaskBase.init_models(self)
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.\
                               detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less

            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters("default_advanced_values")
            self.__mini_diff_hwobj = self._beamline_setup_hwobj.\
                                     diffractometer_hwobj
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._path_template = queue_model_objects.PathTemplate()

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)

        treewidget_item = self.mesh_widget.mesh_treewidget.currentItem()
        if treewidget_item is not None:
            drawing_mgr = self.__list_items[treewidget_item]
            key = str(treewidget_item.text(0))
            selected_grid = drawing_mgr._get_grid(key)[0]
        else:
            logging.getLogger("user_level_log").\
                warning("No grid selected, please select a grid.")
            selected_grid = None
        return result and selected_grid
            
    def update_processing_parameters(self, crystal):
        """
        Descript. :
        """
        return

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            #self._processing_parameters = sample_model.processing_parameters
            #self._processing_widget.update_data_model(self._processing_parameters)
        elif isinstance(tree_item, Qt4_queue_item.DataCollectionQueueItem):
            data_collection = tree_item.get_model()

            if data_collection.experiment_type == EXPERIMENT_TYPE.MESH:
                if tree_item.get_model().is_executed():
                    self.setDisabled(True)
                else:
                    self.setDisabled(False)

                sample_data_model = self.get_sample_item(tree_item).get_model()
                self._acq_widget.disable_inverse_beam(True)

                self._path_template = data_collection.get_path_template()
                self._data_path_widget.update_data_model(self._path_template)

                self._acquisition_parameters = data_collection.acquisitions[0].acquisition_parameters
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                    self._path_template)
                self.get_acquisition_widget().use_osc_start(True)
            else:
                self.setDisabled(True)
        else:
            self.setDisabled(True)

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem) or \
           isinstance(tree_item, Qt4_queue_item.DataCollectionGroupQueueItem) or \
           isinstance(tree_item, Qt4_queue_item.DataCollectionQueueItem):

            #self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
  
    def _create_task(self,  sample, shape):
        """
        Descript. :
        """
        data_collections = []

        selected_grid_info = None
        treewidget_item = self.mesh_widget.mesh_treewidget.selectedItem()
        if treewidget_item is not None:
            drawing_mgr = self.__list_items[treewidget_item]
            key = str(treewidget_item.text(0))
            selected_grid_info = drawing_mgr._get_grid(key)[0]

        if selected_grid_info:
            snapshot = self._graphics_manager.get_snapshot([])
            acq = self._create_acq(sample)
            cpoint = selected_grid_info.get("centred_point")
            #cpos = self._beamline_setup_hwobj.diffractometer_hwobj.convert_from_obj_to_name(cpoint)
            acq.acquisition_parameters.centred_position = cpoint
            acq.acquisition_parameters.mesh_steps = [selected_grid_info.get("steps_x"),
                                                     selected_grid_info.get("steps_y")]
            acq.acquisition_parameters.mesh_range = [selected_grid_info.get("dy_mm"),
                                                     selected_grid_info.get("dx_mm")]
            acq.acquisition_parameters.num_images = selected_grid_info.get("steps_x") * \
                                                    selected_grid_info.get("steps_y")
            
            processing_parameters = deepcopy(self._processing_parameters)
            dc = queue_model_objects.DataCollection([acq],
                                    sample.crystals[0],
                                    processing_parameters)

            dc.set_name(acq.path_template.get_prefix())
            dc.set_number(acq.path_template.run_number)
            dc.set_grid_id(selected_grid_info.get("id"))
            dc.set_experiment_type(EXPERIMENT_TYPE.MESH)

            data_collections.append(dc)
            self._path_template.run_number += 1

        return data_collections            

    def set_beam_info(self, beam_info_dict):
        """
        Descript. :
        """
        self.__beam_info = beam_info_dict
        
        """if self.__drawing_mgr is not None:
            vspace, hspace = self.get_cell_dim()
            self.__drawing_mgr.set_beam_position(0, 0, self.__beam_size_x, self.__beam_size_y)
            self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)
            self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)
            self.__drawing_mgr.set_cell_shape(self.__beam_shape == "ellipse")"""

    def draw_button_clicked(self):
        """
        Descript. :
        """
        self.__spacing = self.get_cell_spacing()
        self._graphics_manager_hwobj.start_mesh_draw(self.__beam_info, self.__spacing)

    def mesh_created(self, mesh):
        """
        Descript. :
        """
        mesh_properties = mesh.get_properties()
        num_lines = mesh_properties.get("num_lines")
        num_images_per_line = mesh_properties.get("num_images_per_line")
        info_str_list = QtCore.QStringList()
        info_str_list.append(mesh_properties.get("name"))
        info_str_list.append(str(mesh_properties.get("beam_hor") * 1000))
        info_str_list.append(str(mesh_properties.get("beam_ver") * 1000))
        info_str_list.append(str(num_lines))
        info_str_list.append(str(num_images_per_line))
        treewidget_item = QtGui.QTreeWidgetItem(self.mesh_widget.mesh_treewidget,
                                                info_str_list)
        self.__list_items[treewidget_item] = mesh
        self._acq_widget.acq_widget.num_images_ledit.setText(str(num_lines * num_images_per_line))

        grid_coordinates = mesh.get_corner_coord()
        self.update_corner_coord(grid_coordinates, mesh)
        treewidget_item.setSelected(True)
        self.mesh_widget.mesh_treewidget.setCurrentItem(treewidget_item) 

    def update_corner_coord(self, coordinates, grid=None):
        """ 
        Descript. : updates corner points and center point of a grid
                    if no grid obejct is passed then currently selected grid is updated
        """
        if not grid:
            treewidget_item = self.mesh_widget.mesh_treewidget.selectedItem()
            grid = self.__list_items[treewidget_item]
        #if drawing_mgr.in_projection_mode():
        if grid:
            # Grid is moved from the drawing position. 
            # Grid coordinates are updated via corner points

            corner_points = []
            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(coordinates[0][0],
                                            coordinates[0][1], True)
            corner_points.append(queue_model_objects.CentredPosition(temp_motor_pos))

            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(coordinates[1][0],
                                            coordinates[1][1], True)
            corner_points.append(queue_model_objects.CentredPosition(temp_motor_pos))

            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(coordinates[2][0],
                                            coordinates[2][1], True)
            corner_points.append(queue_model_objects.CentredPosition(temp_motor_pos))

            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(coordinates[3][0],
                                            coordinates[3][1], True)
            corner_points.append(queue_model_objects.CentredPosition(temp_motor_pos))
            grid.set_motor_pos_corner(corner_points)
            # Grid is in drawing position, we have to move 

            temp_motor_pos = self.__mini_diff_hwobj.\
                   get_centred_point_from_coord(abs((coordinates[0][0] +
                                                     coordinates[1][0]) / 2),
                                                abs((coordinates[0][1] +
                                                     coordinates[2][1]) / 2))

            #cpos = self.__mini_diff_hwobj.convert_from_obj_to_name(temp_motor_pos)
            cpos = queue_model_objects.CentredPosition(temp_motor_pos)
            grid.set_motor_pos_center(cpos)


    def delete_drawing_clicked(self):
        """
        Descript. :
        """
        if len(self.__list_items):
            treewidget_item = self.mesh_widget.mesh_treewidget.currentItem()

            self._graphics_manager_hwobj.delete_shape(self.__list_items[treewidget_item])
            self.mesh_widget.mesh_treewidget.takeTopLevelItem(\
                 self.mesh_widget.mesh_treewidget.indexOfTopLevelItem(treewidget_item))

            self._acq_widget.acq_widget.num_images_ledit.setText("0")

    def get_cell_spacing(self):
        hspace = self.mesh_widget.hor_spacing_ledit.text()
        vspace = self.mesh_widget.ver_spacing_ledit.text()
        try:
            vspace = float(vspace)
        except ValueError:
            vspace = 0
        try:
            hspace = float(hspace)
        except ValueError:
            hspace = 0

        return ((hspace/1000, (vspace)/1000))

    def set_vspace(self, vspace):
        vspace, hspace = self.get_cell_spacing()
        #self._graphics_manager

    def set_hspace(self, hspace):
        vspace, hspace = self.get_cell_spacing()

    def set_beam_position(self, beam_c_x, beam_c_y, beam_size_x, beam_size_y):
        self.__cell_height = int(beam_size_x * self.__y_pixel_size)
        self.__cell_width = int(beam_size_y * self.__x_pixel_size)

        try:
            vspace, hspace = self.get_cell_spacing()
            self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)
            self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)

            self.__drawing_mgr.set_beam_position(0, 0, beam_size_x, beam_size_y)
            #for drawing_mgr in self.__list_items.itervalues():
            #    drawing_mgr.set_beam_position(beam_c_x, beam_c_y)
        except:
            # Drawing manager not set when called
            pass

    def mesh_treewidget_current_item_changed(self, item, prev_item):
        for index, current_item in enumerate(self.__list_items.iterkeys()):
            mesh = self.__list_items[current_item]
            if current_item == item:
                print "set_selected" 
                if mesh.isVisible():
                    self.mesh_widget.visibility_button.setText("Hide")
                else:
                    self.mesh_widget.visibility_button.setText("Show")

                grid_properties = mesh.get_properties()
                cell_count = grid_properties.get("num_lines") * \
                             grid_properties.get("num_images_per_line")
                self._acq_widget.acq_widget.num_images_ledit.setText("%d" % cell_count)
                self.mesh_widget.hor_spacing_ledit.\
                     setText("%.2f" % float(grid_properties.get("spacing_hor") * 1000))
                self.mesh_widget.ver_spacing_ledit.\
                     setText("%.2f" % float(grid_properties.get("spacing_ver") * 1000)) 
                self._acq_widget.acq_widget.first_image_ledit.\
                     setText("%d" % grid_properties.get("first_image_num"))

                centred_point = mesh.get_motor_pos_center()
                self._acq_widget.acq_widget.osc_start_ledit.setText(\
                     "%.2f" % float(centred_point.phi))
                self._acq_widget.acq_widget.kappa_ledit.setText(\
                     "%.2f" % float(centred_point.kappa))
                self._acq_widget.acq_widget.kappa_phi_ledit.setText(\
                     "%.2f" % float(centred_point.kappa_phi))

            else:
                mesh.setSelected(False)


    def toggle_visibility_grid(self):
        item = self.mesh_widget.mesh_treewidget.currentItem()

        for current_item in self.__list_items.iterkeys():
            mesh = self.__list_items[current_item]
            if current_item == item:
                if mesh.isVisible():
                    mesh.hide()
                    self.mesh_widget.visibility_button.setText("Show")
                else:
                    mesh.show()
                    self.mesh_widget.visibility_button.setText("Hide")

    def display_grids(self, display):
        for drawing_mgr in self.__list_items.values():
            drawing_mgr.show() if display else drawing_mgr.hide()

    def set_motor_pos(self, motor_pos):
        for drawing_mgr in self.__list_items.values():
            drawing_mgr.set_motor_pos_actual(motor_pos)
        self.current_motor_positions = motor_pos

    def update_grid_corner_points(self):
        for drawing_mgr in self.__list_items.values():
            grid_corner_points = drawing_mgr.get_grid_corner_points()[0]
            grid_coordinates = []
            for grid_corner_point in grid_corner_points:
                grid_coordinates.append(self.__mini_diff_hwobj.motor_positions_to_screen(grid_corner_point))
            drawing_mgr.set_grid_coordinates(grid_coordinates)[0]

    def move_to_center_point(self):
        treewidget_item = self.mesh_widget.mesh_treewidget.selectedItem()
        drawing_mgr = self.__list_items[treewidget_item]
        cpos = drawing_mgr.get_grid_center_point()[0]
        self.__mini_diff_hwobj.moveToMotorsPositions(cpos)

    def _get_grid_info(self, grid_dict):
        treewidget_item = self.mesh_widget.mesh_treewidget.selectedItem()
        if treewidget_item is not None:
            drawing_mgr = self.__list_items[treewidget_item]
            key = str(treewidget_item.text(0))
            grid_dict.update(drawing_mgr._get_grid(key)[0])

    def _set_grid_data(self, key, result_data):
        for treewidget_item in self.__list_items.keys():
            if key == str(treewidget_item.text(0)):
                drawing_mgr = self.__list_items[treewidget_item]
                drawing_mgr.set_data(result_data)
                break
