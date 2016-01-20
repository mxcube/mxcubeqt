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

import Qt4_queue_item
import Qt4_GraphicsManager
import queue_model_objects_v1 as queue_model_objects

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN


class CreateAdvancedWidget(CreateTaskBase):
    """
    Descript. :
    """

    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, QtCore.Qt.WindowFlags(fl), 'Advanced')

        if not name:
            self.setObjectName("create_advanced_widget")

        # Hardware objects ----------------------------------------------------
 
        # Internal variables --------------------------------------------------
        self.init_models()
        self._advanced_methods = None
        self._grid_map = {}

        # Graphic elements ----------------------------------------------------
        self._advanced_methods_widget = uic.loadUi(os.path.join(\
            os.path.dirname(__file__), "ui_files/Qt4_advanced_methods_layout.ui"))

        self._acq_widget =  AcquisitionWidget(self, "acquisition_widget",
             layout='vertical', acq_params=self._acquisition_parameters,
             path_template=self._path_template)

        self._data_path_widget = DataPathWidget(self, 'create_dc_path_widget', 
             data_model = self._path_template, layout = 'vertical')

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self) 
        _main_vlayout.addWidget(self._advanced_methods_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.\
             connect(self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        self._data_path_widget.pathTemplateChangedSignal.connect(\
             self.handle_path_conflict)

        self._acq_widget.acqParametersChangedSignal.connect(\
             self.handle_path_conflict)
        self._acq_widget.madEnergySelectedSignal.connect(\
             self.mad_energy_selected)

        self._advanced_methods_widget.grid_treewidget.itemSelectionChanged.\
             connect(self.grid_treewidget_item_selection_changed)
        self._advanced_methods_widget.draw_grid_button.clicked.\
             connect(self.draw_grid_button_clicked)
        self._advanced_methods_widget.remove_grid_button.clicked.\
             connect(self.remove_grid_button_clicked)
        self._advanced_methods_widget.hor_spacing_ledit.textChanged.\
             connect(self.spacing_changed)
        self._advanced_methods_widget.ver_spacing_ledit.textChanged.\
             connect(self.spacing_changed)

        self._advanced_methods_widget.move_right_button.clicked.\
             connect(lambda : self.move_grid("right"))
        self._advanced_methods_widget.move_left_button.clicked.\
             connect(lambda : self.move_grid("left"))
        self._advanced_methods_widget.move_up_button.clicked.\
             connect(lambda : self.move_grid("up"))
        self._advanced_methods_widget.move_down_button.clicked.\
             connect(lambda : self.move_grid("down"))        
      
        self._advanced_methods_widget.overlay_cbox.toggled.\
             connect(self.overlay_cbox_toggled)
        self._advanced_methods_widget.overlay_alpha_progressbar.valueChanged.\
             connect(self.overlay_alpha_changed) 
        self._advanced_methods_widget.move_to_grid_button.clicked.\
             connect(self.move_to_grid)

        # Other ---------------------------------------------------------------
        self._acq_widget.use_osc_start(False)
        self._acq_widget.use_kappa(False) 
        self._acq_widget.use_kappa_phi(False)
        self._acq_widget.acq_widget_layout.num_images_label.setEnabled(False)
        self._acq_widget.acq_widget_layout.num_images_ledit.setEnabled(False)
        for col in range(self._advanced_methods_widget.\
                         grid_treewidget.columnCount()):
            self._advanced_methods_widget.grid_treewidget.\
                 resizeColumnToContents(col)

    def init_models(self):
        """
        Descript. :
        """
        CreateTaskBase.init_models(self)
        self._init_models()

    def _init_models(self):
        """
        Descript. :
        """
        self._advanced = queue_model_objects.Advanced()
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.\
                               detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less

            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters("default_advanced_values")

            if not self._advanced_methods:
                self._advanced_methods = self._beamline_setup_hwobj.get_advanced_methods()            
                if self._advanced_methods:
                   for method in self._advanced_methods:
                       self._advanced_methods_widget.method_combo.addItem(method)
                else:
                   self.setEnabled(False)    
            try:
                transmission = self._beamline_setup_hwobj.transmission_hwobj.getAttFactor()
                transmission = round(float(transmission), 1)
            except AttributeError:
                transmission = 0

            try:
                resolution = self._beamline_setup_hwobj.resolution_hwobj.getPosition()
                resolution = round(float(resolution), 3)
            except AttributeError:
                resolution = 0

            try:
                energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
                energy = round(float(energy), 4)
            except AttributeError:
                energy = 0

            self._acquisition_parameters.resolution = resolution
            self._acquisition_parameters.energy = energy
            self._acquisition_parameters.transmission = transmission

            self.grid_treewidget_item_selection_changed()
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)

        if len(self._advanced_methods_widget.grid_treewidget.\
            selectedItems()) == 0:
            msg = "No grid selected. Automatic grid will be used."
            logging.getLogger("user_level_log").info(msg)
        return result
            
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
            self._init_models()
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                                self._path_template)            
        elif isinstance(tree_item, Qt4_queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif isinstance(tree_item, Qt4_queue_item.AdvancedQueueItem):
            advanced = tree_item.get_model()
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            # sample_data_model = self.get_sample_item(tree_item).get_model()
            #self._acq_widget.disable_inverse_beam(True)

            self._path_template = advanced.get_path_template()
            self._data_path_widget.update_data_model(self._path_template)

            data_collection = advanced.reference_image_collection

            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
            self.get_acquisition_widget().use_osc_start(True)
        else:
            self.setDisabled(True)
        #if self._advanced_methods_widget.grid_treewidget.count() > 0:
        #    self._advanced_methods_widget.grid_treewidget.clearSelection() 
  
    def _create_task(self,  sample, shape):
        """
        Descript. :
        """
        data_collections = []
        selected_grids = self.get_selected_grids() 

        if len(selected_grids) == 0:
            selected_grids.append(self._graphics_manager_hwobj.\
                create_automatic_grid()) 

        for shape in selected_grids:
            shape.set_snapshot(self._graphics_manager_hwobj.\
                  get_snapshot(shape))

            grid_properties = shape.get_properties()

            acq = self._create_acq(sample)
            acq.acquisition_parameters.centred_position = \
                shape.get_centred_position()
            acq.acquisition_parameters.mesh_range = \
                [grid_properties["dx_mm"], grid_properties["dy_mm"]]
            acq.acquisition_parameters.num_lines = \
                grid_properties["num_lines"]
            acq.acquisition_parameters.num_images = \
                grid_properties["num_lines"] * \
                grid_properties["num_images_per_line"]

            processing_parameters = deepcopy(self._processing_parameters)

            dc = queue_model_objects.DataCollection([acq],
                                     sample.crystals[0],
                                     processing_parameters)

            dc.set_name(acq.path_template.get_prefix())
            dc.set_number(acq.path_template.run_number)
            dc.set_experiment_type(EXPERIMENT_TYPE.MESH)

            exp_type = str(self._advanced_methods_widget.method_combo.\
                currentText()).title().replace(" ", "")
            advanced = queue_model_objects.Advanced(exp_type, dc, 
                  shape, sample.crystals[0])

            data_collections.append(advanced)
            self._path_template.run_number += 1

            return data_collections            

    def shape_created(self, shape, shape_type):
        if shape_type == "Grid":
            self._advanced_methods_widget.grid_treewidget.clearSelection()
            grid_properties = shape.get_properties()
            info_str_list = QtCore.QStringList()
            info_str_list.append(grid_properties["name"])
            info_str_list.append("%d" % grid_properties["beam_x"])
            info_str_list.append("%d" % grid_properties["beam_y"])
            info_str_list.append("%d" % grid_properties["num_lines"])
            info_str_list.append("%d" % grid_properties["num_images_per_line"])

            grid_treewidget_item = QtGui.QTreeWidgetItem(\
                self._advanced_methods_widget.grid_treewidget,
                info_str_list)
            grid_treewidget_item.setSelected(True)
            self._grid_map[shape] = grid_treewidget_item
            self.grid_treewidget_item_selection_changed()
            
    def shape_deleted(self, shape, shape_type):
        if self._grid_map.get(shape):
            treewidget_item_modelindex = self._advanced_methods_widget.\
                 grid_treewidget.indexFromItem(self._grid_map[shape])
            self._advanced_methods_widget.grid_treewidget.takeTopLevelItem(\
                 treewidget_item_modelindex.row())
            self._grid_map.pop(shape) 

    def grid_treewidget_item_selection_changed(self):
        self._advanced_methods_widget.remove_grid_button.setEnabled(False)
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_properties = grid_object.get_properties() 
                cell_count = grid_properties["num_lines"] * \
                             grid_properties["num_images_per_line"]
                self._acq_widget.acq_widget_layout.num_images_ledit.setText(\
                     "%d" % cell_count)
                self._acq_widget.acq_widget_layout.first_image_ledit.setText(\
                     "%d" % grid_properties["first_image_num"])
                centred_point = grid_object.get_centred_position()
                self._acq_widget.acq_widget_layout.osc_start_ledit.setText(\
                     "%.2f" % float(centred_point.phi))
                self._acq_widget.acq_widget_layout.kappa_ledit.setText(\
                     "%.2f" % float(centred_point.kappa))
                self._acq_widget.acq_widget_layout.kappa_phi_ledit.setText(\
                     "%.2f" % float(centred_point.kappa_phi))
                self._advanced_methods_widget.hor_spacing_ledit.setText(\
                     "%.2f" % float(grid_properties["xOffset"]))
                self._advanced_methods_widget.ver_spacing_ledit.setText(\
                     "%.2f" % float(grid_properties["yOffset"]))
                grid_object.setSelected(True) 
                self._advanced_methods_widget.remove_grid_button.setEnabled(True)
            else:
                grid_object.setSelected(False)
        self._advanced_methods_widget.move_to_grid_button.setEnabled(True)

    def get_selected_grids(self):
        selected_grids = [] 
        for grid, grid_treewidget_item in self._grid_map.iteritems():
            if grid_treewidget_item.isSelected():
                selected_grids.append(grid)
        return selected_grids

    def draw_grid_button_clicked(self):
        self._graphics_manager_hwobj.create_grid(self.get_spacing())

    def remove_grid_button_clicked(self):
        grid_to_delete = None 
        for grid, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_to_delete = grid
                break
        if grid_to_delete:
            self._graphics_manager_hwobj.delete_shape(grid_to_delete)
            self._advanced_methods_widget.move_to_grid_button.setEnabled(False)           

    def get_spacing(self):
        spacing = [0, 0]
        try:
           spacing[0] = float(self._advanced_methods_widget.\
               hor_spacing_ledit.text())
        except:
           pass
        try:
           spacing[1] = float(self._advanced_methods_widget.\
               ver_spacing_ledit.text())
        except:
           pass
        return spacing

    def spacing_changed(self, value):
        spacing = self.get_spacing()
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_object.set_spacing(spacing)

    def move_to_grid(self):
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                self._beamline_setup_hwobj.diffractometer_hwobj.\
                     move_to_centred_position(grid_object.get_centred_position())

    def overlay_cbox_toggled(self, state):
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_object.set_display_score(state)
           
    def overlay_alpha_changed(self, alpha_value):
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_object.set_fill_alpha(alpha_value)

    def move_grid(self, direction):
        for grid_object, treewidget_item in self._grid_map.iteritems():
            if treewidget_item.isSelected():
                grid_object.move_by_pix(direction)
                self._graphics_manager_hwobj.\
                     update_grid_motor_positions(grid_object)
