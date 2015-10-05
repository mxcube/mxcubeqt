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
            self.setObjectName("create_advanced_scan_widget")

        # Hardware objects ----------------------------------------------------
        self.__mini_diff_hwobj = None
 
        # Internal variables --------------------------------------------------
        self.init_models()
        self._prev_pos = None
        self._current_pos = None
        self._list_item_map = {}
        self._advanced_methods = None
        self._grid_map = {}

        self.init_models()


        # Graphic elements ----------------------------------------------------
        self._advanced_methods_widget = uic.loadUi(os.path.join(\
            os.path.dirname(__file__), "ui_files/Qt4_advanced_methods_layout.ui"))

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
        _main_vlayout.addWidget(self._advanced_methods_widget)
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
        self._data_path_widget.pathTemplateChangedSignal.connect(\
                     self.handle_path_conflict)

        self._acq_widget.use_osc_start(False)

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
            if not self._advanced_methods:
                self._advanced_methods = self._beamline_setup_hwobj.get_advanced_methods()            
                for method in self._advanced_methods:
                    self._advanced_methods_widget.method_combo.addItem(method)
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._path_template = queue_model_objects.PathTemplate()

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)

        method_name = str(self._advanced_methods_widget.method_combo.\
                currentText()).title().replace(' ', '')
        if not hasattr(queue_model_objects, method_name):
            logging.getLogger("user_level_log").error("Advanced method %s not defined" \
                    % method_name)
            result = False 

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
        
    def shape_created(self, shape, shape_type):
        if shape_type == "Grid":
            self._advanced_methods_widget.grid_combo.addItem(shape.get_full_name())            
            self._grid_map[shape] = self._advanced_methods_widget.grid_combo.count() - 1
  
    def shape_deleted(self, shape, shape_type):
        if self._grid_map.get(shape):
            self._advanced_methods_widget.grid_combo.removeItem(self._grid_map[shape])
            self._grid_map.pop(shape) 

    def mesh_treewidget_current_item_changed(self, item, prev_item):
        for index, current_item in enumerate(self.__list_items.iterkeys()):
            mesh = self.__list_items[current_item]
            if current_item == item:
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
