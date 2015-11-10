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
import copy
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import Qt4_queue_item
import Qt4_GraphicsManager as graphics_manager
import queue_model_objects_v1 as queue_model_objects

from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN
from Qt4_create_task_base import CreateTaskBase
from Qt4_data_path_widget import DataPathWidget
from Qt4_acquisition_widget import AcquisitionWidget
from Qt4_processing_widget import ProcessingWidget


class CreateHelicalWidget(CreateTaskBase):
    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Helical')

        if not name:
            self.setObjectName("create_helical_widget")
        self.init_models() 
         
        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._lines_map = {}

        # Graphic elements ----------------------------------------------------
        self._lines_widget = uic.loadUi(os.path.join(\
            os.path.dirname(__file__), "ui_files/Qt4_helical_line_widget_layout.ui"))

        self._acq_widget =  AcquisitionWidget(self, "acquisition_widget",
             layout='vertical', acq_params=self._acquisition_parameters,
             path_template=self._path_template)

        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_widget = \
            DataPathWidget(self._data_path_gbox,
                           'create_dc_path_widget',
                           data_model=self._path_template,
                           layout='vertical')

        self._processing_widget = ProcessingWidget(self,
             data_model=self._processing_parameters)

        # Layout --------------------------------------------------------------
        _data_path_gbox_layout = QtGui.QVBoxLayout(self._data_path_gbox)
        _data_path_gbox_layout.addWidget(self._data_path_widget)
        _data_path_gbox_layout.setSpacing(0)
        _data_path_gbox_layout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._lines_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_gbox)
        _main_vlayout.addWidget(self._processing_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._lines_widget.lines_treewidget.itemSelectionChanged.connect(\
             self.lines_treewidget_selection_changed)
        self._lines_widget.create_line_button.clicked.connect(\
             self.create_line_button_clicked)
        self._lines_widget.remove_line_button.clicked.connect(\
             self.remove_line_button_clicked)  

        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.\
             connect(self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        self._data_path_widget.pathTemplateChangedSignal.connect(\
             self.handle_path_conflict)

        self._acq_widget.madEnergySelectedSignal.connect(\
             self.mad_energy_selected)
        self._acq_widget.acqParametersChangedSignal.connect(\
             self.handle_path_conflict)

        self._processing_widget.enableProcessingSignal.connect(\
             self._enable_processing_toggled)

        # Other ---------------------------------------------------------------

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._energy_scan_result = queue_model_objects.EnergyScanResult()
        self._processing_parameters = queue_model_objects.ProcessingParameters()
  
        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.\
                               detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less

            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters()
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._path_template = queue_model_objects.PathTemplate()

    def shape_created(self, shape, shape_type):
        if shape_type == "Line":
            self._lines_widget.lines_treewidget.clearSelection()
            info_str_list = QtCore.QStringList()
            info_str_list.append(shape.get_display_name())
            info_str_list.append("%d" % shape.get_points_index()[0])
            info_str_list.append("%d" % shape.get_points_index()[1])
            
            lines_treewidget_item = QtGui.QTreeWidgetItem(\
                self._lines_widget.lines_treewidget,
                info_str_list)
            lines_treewidget_item.setSelected(True)
            self._lines_map[shape] = lines_treewidget_item

            self.lines_treewidget_selection_changed()

    def shape_deleted(self, shape, shape_type):
        if self._lines_map.get(shape):
            shape_index = self._lines_widget.lines_treewidget.\
                 indexFromItem(self._lines_map[shape])
            self._lines_widget.lines_treewidget.\
                 takeTopLevelItem(shape_index.row())
            self._lines_map.pop(shape)

    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)
   
        if len(self._lines_widget.lines_treewidget.selectedItems()) == 0:
            logging.getLogger("user_level_log").\
                warning("No lines selected, please select one or more lines.")
            return False
        else:
            return base_result
            
    def update_processing_parameters(self, crystal):
        self._processing_parameters.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma
        self._processing_widget.update_data_model(self._processing_parameters)

    def select_shape_with_cpos(self, start_cpos, end_cpos):
        self._graphics_manager_hwobj.de_select_all()
        selected_line = None

        for shape in self._graphics_manager_hwobj.get_shapes():
            if isinstance(shape, graphics_manager.GraphicsItemLine):
                (line_start_cpos, line_end_cpos) = shape.get_centred_positions() 
                if line_start_cpos == start_cpos and line_end_cpos == end_cpos:
                    self._graphics_manager_hwobj.de_select_all()
                    shape.setSelected(True)
                    selected_line = shape

        #de-select previous selected list items and
        #select the current shape (Line).
        for (list_item, shape) in self._lines_map.iteritems():
            if selected_line is shape:
                list_item.setSelected(True)
            else:
                list_item.setSelected(False)

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
                                                             
        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            self._processing_parameters = sample_model.processing_parameters
            #self._processing_parameters = copy.deepcopy(self._processing_parameters)
            self._processing_widget.update_data_model(self._processing_parameters)

        elif isinstance(tree_item, Qt4_queue_item.DataCollectionQueueItem):
            data_collection = tree_item.get_model()

            if data_collection.experiment_type == EXPERIMENT_TYPE.HELICAL:
                if tree_item.get_model().is_executed():
                    self.setDisabled(True)
                else:
                    self.setDisabled(False)

                self._path_template = data_collection.get_path_template()
                self._data_path_widget.update_data_model(self._path_template)
                
                self._acquisition_parameters = data_collection.acquisitions[0].\
                                               acquisition_parameters

                if len(data_collection.acquisitions) == 2:
                    start_cpos = data_collection.acquisitions[0].acquisition_parameters.\
                                 centred_position
                    end_cpos = data_collection.acquisitions[1].acquisition_parameters.\
                               centred_position

                    self.select_shape_with_cpos(start_cpos, end_cpos)

                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
                self.get_acquisition_widget().use_osc_start(True)
                
                self._processing_parameters = data_collection.processing_parameters
                self._processing_widget.update_data_model(self._processing_parameters)
            else:
                self.setDisabled(True)
        else:
            self.setDisabled(True)

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem) or \
           isinstance(tree_item, Qt4_queue_item.DataCollectionGroupQueueItem) or \
           isinstance(tree_item, Qt4_queue_item.DataCollectionQueueItem):

            self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
  
    def _create_task(self,  sample, shape):
        data_collections = []

        if isinstance(shape, graphics_manager.GraphicsItemLine):
            snapshot = self._graphics_manager_hwobj.get_snapshot(shape)

            # Acquisition for start position
            start_acq = self._create_acq(sample) 
           
            start_graphical_point, end_graphical_point = \
                shape.get_graphical_points() 
            start_acq.acquisition_parameters.\
                centred_position = copy.deepcopy(start_graphical_point.get_centred_position())
            start_acq.acquisition_parameters.centred_position.\
                snapshot_image = snapshot

            start_acq.path_template.suffix = self._session_hwobj.suffix

            # Add another acquisition for the end position
            end_acq = self._create_acq(sample)

            end_acq.acquisition_parameters.\
                centred_position = copy.deepcopy(end_graphical_point.get_centred_position())
            end_acq.acquisition_parameters.centred_position.\
                snapshot_image = snapshot

            end_acq.path_template.suffix = self._session_hwobj.suffix

            processing_parameters = copy.deepcopy(self._processing_parameters)

            dc = queue_model_objects.DataCollection([start_acq, end_acq],
                                    sample.crystals[0],
                                    processing_parameters)

            dc.set_name(start_acq.path_template.get_prefix())
            dc.set_number(start_acq.path_template.run_number)
            dc.experiment_type = EXPERIMENT_TYPE.HELICAL

            data_collections.append(dc)
            self._path_template.run_number += 1

        return data_collections

    def lines_treewidget_selection_changed(self):
        for shape, list_item in self._lines_map.iteritems():
            shape.setSelected(list_item.isSelected())

    def create_line_button_clicked(self):
        self._graphics_manager_hwobj.create_line()

    def remove_line_button_clicked(self):
        line_object_to_delete = None
        for line, treewidget_item in self._lines_map.iteritems():
            if treewidget_item.isSelected():
                line_to_delete = line
                break
        if line_to_delete:
            self._graphics_manager_hwobj.delete_shape(line_to_delete)
