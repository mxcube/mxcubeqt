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

import logging
import copy

from PyQt4 import QtCore
from PyQt4 import QtGui

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
         
        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.init_models()
        self._prev_pos = None
        self._current_pos = None
        self._list_item_map = {}
        self.init_models()

        self._lines_gbox = QtGui.QGroupBox('Lines', self)
        self._lines_list_widget = QtGui.QListWidget(self._lines_gbox)
        self._lines_list_widget.setFixedWidth(175)
        self._lines_list_widget.setFixedHeight(50)
        self._lines_list_widget.setToolTip(\
             "Select the line(s) to perfrom helical scan on")

        add_button = QtGui.QPushButton("+", self._lines_gbox)
        add_button.setFixedWidth(20)
        add_button.setFixedHeight(20)
        remove_button = QtGui.QPushButton("-", self._lines_gbox)
        remove_button.setFixedWidth(20)
        remove_button.setFixedHeight(20)        

        add_button_tool_tip = "Add a line between two saved positions, " \
                              "CTRL click to select more than one position"
        add_button.setToolTip(add_button_tool_tip)
        remove_button_tool_tip = "Remove selected line(s)"
        remove_button.setToolTip(remove_button_tool_tip)

        self._acq_gbox = QtGui.QGroupBox('Acquisition', self)
        self._acq_widget =  AcquisitionWidget(self._acq_gbox,
                              "acquisition_widget",
                              layout='vertical',
                              acq_params=self._acquisition_parameters,
                              path_template=self._path_template)

        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_widget = \
            DataPathWidget(self._data_path_gbox,
                           'create_dc_path_widget',
                           data_model=self._path_template,
                           layout='vertical')

        self._processing_gbox = QtGui.QGroupBox('Processing', self)
        self._processing_gbox.setObjectName('processing_gbox')
        self._processing_widget = \
            ProcessingWidget(self._processing_gbox,
                             data_model=self._processing_parameters)

        # Layout --------------------------------------------------------------
        _lines_gbox_gridlayout = QtGui.QGridLayout(self)
        _lines_gbox_gridlayout.addWidget(self._lines_list_widget, 0, 0, 2, 1)
        _lines_gbox_gridlayout.addWidget(add_button, 0, 1)
        _lines_gbox_gridlayout.addWidget(remove_button, 1, 1) 
        _lines_gbox_gridlayout.setSpacing(2)
        _lines_gbox_gridlayout.setColumnStretch(2, 10)
        _lines_gbox_gridlayout.setContentsMargins(2, 2, 2, 2)
        self._lines_gbox.setLayout(_lines_gbox_gridlayout)

        _acq_gbox_layout = QtGui.QVBoxLayout(self)
        _acq_gbox_layout.addWidget(self._acq_widget)
        _acq_gbox_layout.setSpacing(0)
        _acq_gbox_layout.setContentsMargins(0,0,0,0)
        self._acq_gbox.setLayout(_acq_gbox_layout)

        _data_path_gbox_layout = QtGui.QVBoxLayout(self)
        _data_path_gbox_layout.addWidget(self._data_path_widget)
        _data_path_gbox_layout.setSpacing(0)
        _data_path_gbox_layout.setContentsMargins(0,0,0,0)
        self._data_path_gbox.setLayout(_data_path_gbox_layout)

        _processing_gbox_layout = QtGui.QVBoxLayout(self)
        _processing_gbox_layout.addWidget(self._processing_widget)
        _processing_gbox_layout.setSpacing(0)
        _processing_gbox_layout.setContentsMargins(0,0,0,0)
        self._processing_gbox.setLayout(_processing_gbox_layout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._lines_gbox)
        _main_vlayout.addWidget(self._acq_gbox)
        _main_vlayout.addWidget(self._data_path_gbox)
        _main_vlayout.addWidget(self._processing_gbox)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0,0,0,0)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        add_button.clicked.connect(self.add_clicked)
        remove_button.clicked.connect(self.remove_clicked)
        prefix_ledit = self._data_path_widget.\
                       data_path_widget.findChild(QtGui.QLineEdit, 
                                                  'prefix_ledit')
        prefix_ledit.textChanged.connect(self._prefix_ledit_change)
        run_number_ledit = self._data_path_widget.\
                           data_path_widget.findChild(QtGui.QLineEdit, 
                                                      'run_number_ledit')
        run_number_ledit.textChanged.connect(self._run_number_ledit_change)

        QtCore.QObject.connect(self._lines_list_widget, 
                               QtCore.SIGNAL("selectionChanged()"),
                               self.list_box_selection_changed)

        QtCore.QObject.connect(self._data_path_widget,
                     QtCore.SIGNAL("path_template_changed"),
                     self.handle_path_conflict)

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

    def add_clicked(self):
        selected_shapes = self._graphics_manager.selected_shapes.values()

        if len(selected_shapes) == 2:
            p1 = selected_shapes[1]
            p2 = selected_shapes[0]
            
            line = graphics_manager.\
                   Line(self._graphics_manager.get_drawing(),
                        p1.qub_point, p2.qub_point,
                        p1.centred_position, p2.centred_position)

            line.show()
            self._graphics_manager.add_shape(line)
            list_box_item = qt.QListBoxText(self._lines_list_widget, 'Line')
            self._list_item_map[list_box_item] = line

            # De select previous items
            for item in self.selected_items():
                self._lines_list_widget.setSelected(item, False)
            
            self._lines_list_widget.setSelected(list_box_item, True)
        else:
            print "No points selected"

    def remove_clicked(self):
        selected_items = self.selected_items()

        if selected_items:
            for item in selected_items:
                self._lines_list_widget.removeItem(self._list_box.index(item))
                line = self._list_item_map[item]
                self._graphics_manager.delete_shape(line)
                del self._list_item_map[item]

    # Calback from graphics_manager, called when a shape is deleted
    def shape_deleted(self, shape):
        if isinstance(shape, graphics_manager.Point):
            items_to_remove = []

            for (list_item, line) in self._list_item_map.iteritems():
                for qub_object in shape.get_qub_objects():
                    if qub_object in line.get_qub_objects():
                        items_to_remove.append((list_item, line))

            for (list_item, line) in items_to_remove:
                self._lines_list_widget.removeItem(self._list_box.index(list_item))
                del self._list_item_map[list_item]

    def centred_position_selection(self, positions):
        if len(positions) == 1:
            self._prev_pos = positions[0]
            
        elif len(positions) == 2:

            for pos in positions:
                if pos != self._prev_pos:
                    self._current_pos = pos
        else:
            self._prev_pos = None
            self._current_pos = None

    def list_box_selection_changed(self):
        self.show_selected_lines()

    def selected_items(self):
        selected_items = []
                
        for item_index in range(0, self._lines_list_widget.count()):
            if self._lines_list_widget.isSelected(item_index):
                selected_items.append(self._lines_list_widget.item(item_index))

        return selected_items
        
    def show_selected_lines(self):
        selected_items = self.selected_items()

        for list_item in self._list_item_map.keys():
            line = self._list_item_map[list_item]
            if list_item in selected_items:
                self._graphics_manager.select_shape(line)
            else:
                self._graphics_manager.de_select_shape(line)

    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)
    
        selected_lines = False
        
        if self.selected_items():
            selected_lines = True
        else:
            logging.getLogger("user_level_log").\
                warning("No lines selected, please select one or more lines.")

        return base_result and selected_lines 
            
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
        self._graphics_manager.de_select_all()
        selected_line = None

        for shape in self._graphics_manager.get_shapes():
            if isinstance(shape, graphics_manager.Line):
                if shape.get_centred_positions()[0] == start_cpos and\
                       shape.get_centred_positions()[1] == end_cpos:
                    self._graphics_manager.select_shape(shape)
                    selected_line = shape

        #de-select previous selected list items and
        #select the current shape (Line).
        for (list_item, shape) in self._list_item_map.iteritems():

            if selected_line is shape:
                self._lines_list_widget.setSelected(list_item, True)
            else:
                self._lines_list_widget.setSelected(list_item, False)

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

        if isinstance(shape, graphics_manager.Line ):
            if shape.get_qub_objects() is not None:
                snapshot = self._graphics_manager.get_snapshot(shape.get_qub_objects())
            else:
                snapshot = self._graphics_manager.get_snapshot([])

            # Acquisition for start position
            start_acq = self._create_acq(sample) 
            
            start_acq.acquisition_parameters.\
                centred_position = copy.deepcopy(shape.start_cpos)
            start_acq.acquisition_parameters.centred_position.\
                snapshot_image = snapshot

            start_acq.path_template.suffix = self._session_hwobj.suffix

            # Add another acquisition for the end position
            end_acq = self._create_acq(sample)

            end_acq.acquisition_parameters.\
                centred_position = shape.end_cpos
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
                   
