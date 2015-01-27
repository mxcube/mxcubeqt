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

import queue_model_objects_v1 as queue_model_objects 
import Qt4_queue_item
import Qt4_GraphicsManager as graphics_manager

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN


class CreateAdvancedScanWidget(CreateTaskBase):
    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, QtCore.Qt.WindowFlags(fl), 'Advanced')

        if not name:
            self.setObjectName("create_advanced_Scan_widget")

        # Hardware objects ----------------------------------------------------
 
        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------

        add_button  = QtGui.QPushButton("Add mesh", self)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(add_button)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        add_button.clicked.connect(self.add_button_clicked)

        return

        self.__mini_diff_hwobj = None

        self.init_models()
        self._prev_pos = None
        self._current_pos = None
        self._list_item_map = {}
        self.init_models()

        self.current_motor_positions = {}
        self.__cell_width = 0
        self.__cell_height = 0
        self.__list_items = {}
        self.__item_counter = 0
        self.__grid_list = []

        self.__canvas = None
        self.__matrix = None
        self.__event_mgr = None
        self.__drawing_object_layer = None
        self.__drawing_mgr = None
        self.__x_pixel_size = 1
        self.__y_pixel_size = 1
        self.__beam_size_x = 0
        self.__beam_size_y = 0
        self.__angle_active = 0

        v_layout = qt.QVBoxLayout(self, 2, 5, "v_layout")
        self._parameters_gbox = qt.QVGroupBox('Mesh parameters', self, "scan_gbox")

        self.mesh_parameters_widget = qtui.QWidgetFactory.\
                     create(os.path.join(os.path.dirname(__file__),
                                         'ui_files/mesh_widget_layout.ui'))
        self.mesh_parameters_widget.reparent(self._parameters_gbox, qt.QPoint(0, 0))
        self._parameters_gbox.setFixedHeight(335)
 
        self._acq_gbox = qt.QVGroupBox('Acquisition', self, 'acq_gbox')
        self._acq_widget = \
            AcquisitionWidget(self._acq_gbox,
                              "acquisition_widget", layout='vertical',
                              acq_params=self._acquisition_parameters,
                              path_template=self._path_template)

        self._acq_gbox.setSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed)

        self._acq_widget.disable_inverse_beam(True)
        self._acq_widget.disable_image_parameters(True)         

        self._data_path_gbox = qt.QVGroupBox('Data location', self,
                                             'data_path_gbox')
        self._data_path_widget = \
            DataPathWidget(self._data_path_gbox, 
                           data_model = self._path_template,
                           layout = 'vertical')

        v_layout.addWidget(self._parameters_gbox)
        v_layout.addWidget(self._acq_gbox)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch()

        prefix_ledit = self._data_path_widget.\
                       data_path_widget_layout.child('prefix_ledit')

        run_number_ledit = self._data_path_widget.\
                           data_path_widget_layout.child('run_number_ledit')

        self.connect(prefix_ledit, 
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)

        self.connect(run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)

        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

        qt.QObject.connect(self.mesh_parameters_widget.child("draw_button"),
                           qt.SIGNAL("clicked()"),
                           self.start_surface_drawing)

        qt.QObject.connect(self.mesh_parameters_widget.child("add_button"),
                           qt.SIGNAL("clicked()"),
                           self.add_drawing)

        qt.QObject.connect(self.mesh_parameters_widget.child("remove_button"),
                           qt.SIGNAL("clicked()"),
                           self.delete_drawing)

        qt.QObject.connect(self.mesh_parameters_widget.child("hor_spacing_ledit"),
                           qt.SIGNAL("textChanged ( const QString & )"),
                           self.set_hspace)

        qt.QObject.connect(self.mesh_parameters_widget.child("ver_spacing_ledit"),
                           qt.SIGNAL("textChanged ( const QString & )"),
                           self.set_vspace)

        self.__mesh_list_view = self.mesh_parameters_widget.child("mesh_listview")

        qt.QObject.connect(self.__mesh_list_view,
                           qt.SIGNAL("selectionChanged(QListViewItem * )"),
                           self.mesh_listview_selection_changed)

        self.__visibility_button = self.mesh_parameters_widget.child("visibility_button")
        qt.QObject.connect(self.__visibility_button,
                           qt.SIGNAL("clicked()"),
                           self.toggle_visibility_grid)

        #TODO somehow make this better
        for child in self._acq_widget.children(): 
            if child.children():
                for child_child in child.children():
                    if hasattr(child_child, 'hide'):
                        child_child.hide()
         
        self._acq_widget.child("osc_range_label").show()
        self._acq_widget.child("osc_range_ledit").show()
        self._acq_widget.child("detector_mode_label").show()
        self._acq_widget.child("detector_mode_combo").show()
        self._acq_widget.child("exp_time_label").show()
        self._acq_widget.child("exp_time_ledit").show()
        self._acq_widget.child("energy_label").show()
        self._acq_widget.child("energy_ledit").show()
        self._acq_widget.child("resolution_label").show()
        self._acq_widget.child("resolution_ledit").show()
        self._acq_widget.child("transmission_label").show()
        self._acq_widget.child("transmission_ledit").show()
        self._acq_widget.setFixedHeight(185)

    def add_button_clicked(self):
        self._graphics_manager_hwobj.start_mesh_draw(False)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        return  
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
        result = CreateTaskBase.approve_creation(self)

        list_view_item = self.__mesh_list_view.selectedItem()
        if list_view_item is not None:
            drawing_mgr = self.__list_items[list_view_item]
            key = str(list_view_item.text(0))
            selected_grid = drawing_mgr._get_grid(key)[0]
        else:
            logging.getLogger("user_level_log").\
                warning("No grid selected, please select a grid.")
            selected_grid = None
        return result and selected_grid
            
    def update_processing_parameters(self, crystal):
        return

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            #self._processing_parameters = sample_model.processing_parameters
            #self._processing_widget.update_data_model(self._processing_parameters)
        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
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

        if isinstance(tree_item, queue_item.SampleQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionGroupQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionQueueItem):

            #self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
  
    def _create_task(self,  sample, shape):
        data_collections = []

        selected_grid_info = None
        list_view_item = self.__mesh_list_view.selectedItem()
        if list_view_item is not None:
            drawing_mgr = self.__list_items[list_view_item]
            key = str(list_view_item.text(0))
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

    def connectToView(self, view_dict):
        qub_image = view_dict.get("drawing")
        if qub_image is not None:
            self.__canvas = qub_image.canvas()
            self.__matrix = qub_image.matrix()
            self.__event_mgr = qub_image
            #self.__drawing_mgr = Qub2PointSurfaceDrawingMgr(self.__canvas, self.__matrix)

    def set_kappa(self, new_value):
        self.kappa_position = new_value
        self.mesh_parameters_widget.child("kappa_ledit").\
             setText("%.2f" % float(new_value))

    def set_kappa_phi(self, new_value):
        self.kappa_phi_position = new_value
        self.mesh_parameters_widget.child("kappa_phi_ledit").\
             setText("%.2f" % float(new_value))

    def update_osc_start(self, new_value):
        self.omega_position = new_value
        self.mesh_parameters_widget.child("omega_ledit").\
             setText("%.2f" % float(new_value))

    def set_beam_info(self, beam_info_dict):
        self.__beam_size_x = beam_info_dict.get("size_x", 0)
        self.__beam_size_y = beam_info_dict.get("size_y", 0)
        self.__beam_shape = beam_info_dict.get("shape", 0)

        if self.__drawing_mgr is not None:
            vspace, hspace = self.get_cell_dim()
            self.__drawing_mgr.set_beam_position(0, 0, self.__beam_size_x, self.__beam_size_y)
            self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)
            self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)
            self.__drawing_mgr.set_cell_shape(self.__beam_shape == "ellipse")

    def start_surface_drawing(self):
        if self.__mini_diff_hwobj is not None:
            (self.__x_pixel_size, self.__y_pixel_size) = \
                    self.__mini_diff_hwobj.get_pixels_per_mm()
        self.__drawing_mgr = Qub2PointSurfaceDrawingMgr(self.__canvas, self.__matrix)
        self.__drawing_mgr.setAutoDisconnectEvent(False)
        drawing_object = graphics_manager.CanvasGrid(self.__canvas)
        self.__drawing_mgr.addDrawingObject(drawing_object)
        self.__event_mgr.addDrawingMgr(self.__drawing_mgr)
        vspace, hspace = self.get_cell_dim()
        self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)
        self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)
        self.__drawing_mgr.set_cell_shape(self.__beam_shape == "ellipse")
        self.__drawing_mgr.set_x_pixel_size(self.__x_pixel_size)
        self.__drawing_mgr.set_y_pixel_size(self.__y_pixel_size)
        self.__drawing_mgr.set_beam_position(0, 0, self.__beam_size_x, self.__beam_size_y)
        self.__drawing_mgr.startDrawing()
        self.__drawing_mgr.setEndDrawCallBack(self.end_surface_drawing)
        self.__drawing_mgr.setColor(qt.Qt.darkGreen)

    def end_surface_drawing(self, drawing_mgr = None):
        drawing_mgr.reshape()

    def add_drawing(self):
        if self.__drawing_mgr.isVisible()[0]:
            self.__item_counter += 1
            name = ("Grid - %i" % self.__item_counter)
            beam_width = str(self.__beam_size_x * 1000)
            beam_height = str(self.__beam_size_y * 1000)
            vspace, hspace = self.get_cell_dim()
            vspace = vspace * 1000
            hspace = hspace * 1000
            list_view_item = qt.QListViewItem(self.__mesh_list_view, name,
                beam_width,  beam_height, str(hspace), str(vspace))
            self.__list_items[list_view_item] = self.__drawing_mgr
            self.__drawing_mgr.stopDrawing()
            self.__drawing_mgr.set_label(name)
            self.__drawing_mgr.set_angles(self.omega_position,
                                          self.kappa_position,
                                          self.kappa_phi_position)[0]
            cell_count = self.__drawing_mgr.get_total_steps()[0]
            self.mesh_parameters_widget.child("num_images_ledit").\
                 setText("%d" % cell_count)

            self.__drawing_mgr.set_motor_pos_created(deepcopy(self.current_motor_positions))[0]
            self.__drawing_mgr.set_motor_pos_actual(self.current_motor_positions)[0]
            grid_coordinates = self.__drawing_mgr.get_grid_coordinates()[0]

            corner_points = []
            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(grid_coordinates[0][0],
                                            grid_coordinates[0][1], True)
            corner_points.append(temp_motor_pos)
            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(grid_coordinates[1][0],
                                            grid_coordinates[1][1], True)
            corner_points.append(temp_motor_pos)
            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(grid_coordinates[2][0],
                                            grid_coordinates[2][1], True)
            corner_points.append(temp_motor_pos)
            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(grid_coordinates[3][0],
                                            grid_coordinates[3][1], True)
            corner_points.append(temp_motor_pos)
            self.__drawing_mgr.set_grid_corner_points(corner_points)[0]

            temp_motor_pos = self.__mini_diff_hwobj.\
               get_centred_point_from_coord(abs((grid_coordinates[0][0] +
                                                 grid_coordinates[1][0]) / 2),
                                            abs((grid_coordinates[0][1] +
                                                grid_coordinates[2][1]) / 2), False)

            #self.__drawing_mgr.set_grid_center_point(temp_motor_pos)[0]

            cpos = self.__mini_diff_hwobj.convert_from_obj_to_name(temp_motor_pos)
            cpos = queue_model_objects.CentredPosition(cpos)
            self.__drawing_mgr.set_grid_center_point(cpos)[0]

            self.__mesh_list_view.setSelected(list_view_item, True)
            self.__drawing_mgr = Qub2PointSurfaceDrawingMgr(self.__canvas, self.__matrix)
            self.start_surface_drawing()

    def delete_drawing(self):
        if len(self.__list_items):
            list_view_item = self.__mesh_list_view.selectedItem()
            del self.__list_items[list_view_item]
            self.__mesh_list_view.takeItem(list_view_item)

            list_view_item = self.__mesh_list_view.lastItem()
            self.mesh_parameters_widget.child("num_images_ledit").setText("")
            self.__mesh_list_view.setSelected(list_view_item, True)

    def get_cell_dim(self):
        hspace = self.mesh_parameters_widget.child("hor_spacing_ledit").text()
        vspace = self.mesh_parameters_widget.child("ver_spacing_ledit").text()
        try:
            vspace = float(vspace)
        except ValueError:
            vspace = 0
        try:
            hspace = float(hspace)
        except ValueError:
            hspace = 0

        return ((vspace)/1000, (hspace)/1000)

    def set_vspace(self, vspace):
        vspace, hspace = self.get_cell_dim()
        self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)

    def set_hspace(self, hspace):
        vspace, hspace = self.get_cell_dim()
        self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)

    def set_x_pixel_size(self, x_size):
        x_size = 1e-3/x_size

        if self.__x_pixel_size != x_size:
            zoom_factor = x_size / self.__x_pixel_size
            beam_width_mm =  self.__beam_size_x
            self.__x_pixel_size = x_size
            self.__cell_width = int(beam_width_mm * self.__x_pixel_size)
            try:
                if self.__drawing_mgr:
                    self.__drawing_mgr.set_x_pixel_size(x_size)
                for drawing_mgr in self.__list_items.values():
                    drawing_mgr.set_x_pixel_size(x_size)
                    drawing_mgr.reposition(scale_factor_x = zoom_factor)
            except AttributeError:
                # Drawing manager not set when called
                pass

    def set_y_pixel_size(self, y_size):
        y_size = 1e-3/y_size

        if self.__y_pixel_size != y_size:
            zoom_factor = y_size / self.__y_pixel_size
            beam_height_mm =  self.__beam_size_y
            self.__y_pixel_size = y_size
            self.__cell_height = int(beam_height_mm * self.__y_pixel_size)

            try:
                if self.__drawing_mgr:
                    self.__drawing_mgr.set_y_pixel_size(y_size)
                    self.__drawing_mgr.reshape()

                for drawing_mgr in self.__list_items.values():
                    drawing_mgr.set_y_pixel_size(y_size)
                    drawing_mgr.reshape()
                    drawing_mgr.reposition(scale_factor_y = zoom_factor)
            except:
                # Drawing manager not set when called
                pass

    def set_beam_position(self, beam_c_x, beam_c_y, beam_size_x, beam_size_y):
        self.__cell_height = int(beam_size_x * self.__y_pixel_size)
        self.__cell_width = int(beam_size_y * self.__x_pixel_size)

        try:
            vspace, hspace = self.get_cell_dim()
            self.__drawing_mgr.set_cell_width(self.__beam_size_x + hspace)
            self.__drawing_mgr.set_cell_height(self.__beam_size_y + vspace)

            self.__drawing_mgr.set_beam_position(0, 0, beam_size_x, beam_size_y)
            #for drawing_mgr in self.__list_items.itervalues():
            #    drawing_mgr.set_beam_position(beam_c_x, beam_c_y)
        except:
            # Drawing manager not set when called
            pass

    def mesh_listview_selection_changed(self, item):
        for index, current_item in enumerate(self.__list_items.iterkeys()):
            drawing_mgr = self.__list_items[current_item]
            if current_item == item:
                drawing_mgr.highlight()
                key = str(current_item.text(0))
                if drawing_mgr.isVisible()[0]:
                    self.__visibility_button.setText("Hide")
                else:
                    self.__visibility_button.setText("Show")
                cell_count = drawing_mgr.get_total_steps()[0]
                self.mesh_parameters_widget.child("num_images_ledit").\
                     setText("%d" % cell_count)
                (omega_pos, kappa_pos, kappa_phi_pos) = drawing_mgr.get_angles()[0]

                self.mesh_parameters_widget.child("omega_ledit").\
                     setText("%.2f" % float(omega_pos))
                self.mesh_parameters_widget.child("kappa_ledit").\
                     setText("%.2f" % float(kappa_pos))
                self.mesh_parameters_widget.child("kappa_phi_ledit").\
                     setText("%.2f" % float(kappa_phi_pos))
            else:
                drawing_mgr.unhighlight()

    def toggle_visibility_grid(self):
        item = self.__mesh_list_view.currentItem()

        for current_item in self.__list_items.iterkeys():
            drawing_mgr = self.__list_items[current_item]
            if current_item == item:
                if drawing_mgr.isVisible()[0]:
                    drawing_mgr.hide()
                    self.__visibility_button.setText("Show")
                else:
                    drawing_mgr.show()
                    self.__visibility_button.setText("Hide")

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
        list_view_item = self.__mesh_list_view.selectedItem()
        drawing_mgr = self.__list_items[list_view_item]
        #motors_positions = drawing_mgr.get_grid_center_point()[0]
        #self.__mini_diff_hwobj.move_to_motors_positions(motors_positions)
        cpos = drawing_mgr.get_grid_center_point()[0]
        self.__mini_diff_hwobj.moveToMotorsPositions(cpos)

    def _get_grid_info(self, grid_dict):
        list_view_item = self.__mesh_list_view.selectedItem()
        if list_view_item is not None:
            drawing_mgr = self.__list_items[list_view_item]
            key = str(list_view_item.text(0))
            grid_dict.update(drawing_mgr._get_grid(key)[0])

    def _set_grid_data(self, key, result_data):
        for list_view_item in self.__list_items.keys():
            if key == str(list_view_item.text(0)):
                drawing_mgr = self.__list_items[list_view_item]

               #  num_cells = drawing_mgr.get_nummer_of_cells()[0]
#                 result_data = {}

#                 for cell in range(1, num_cells + 1):
#                     random.seed()
#                     result_data[cell] = (cell, (255, random.randint(0, 255), 0))

                drawing_mgr.set_data(result_data)
                break
