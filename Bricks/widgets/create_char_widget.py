import queue_model
import queue_item
import copy
import widget_utils
import logging
import math
import ShapeHistory as shape_history

from qt import *
from widgets.widget_utils import DataModelInputBinder
from widgets.characterise_simple_widget_vertical_layout import \
    CharacteriseSimpleWidgetVerticalLayout
from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from widgets.vertical_crystal_dimension_widget_layout\
    import VerticalCrystalDimensionWidgetLayout
from acquisition_widget_simple import AcquisitionWidgetSimple


class CreateCharWidget(CreateTaskBase):
    def __init__(self,parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Characterisation')

        if not name:
            self.setName("create_char_widget")

        #
        # Data attributes
        #
        self._char = queue_model.Characterisation()
        self._data_collection = self._char.reference_image_collection

        self._path_template = self._data_collection.\
            acquisitions[0].path_template
        self._char_params = self._char.characterisation_parameters
        self._char_params.experiment_type = queue_model.EXPERIMENT_TYPE.OSC
        self._char_params_mib = DataModelInputBinder(self._char_params)

        self._current_selected_item = None

        # The num images drop down default value is 1 
        self._data_collection.acquisitions[0].\
            acquisition_parameters.num_images = 2
        self._char.characterisation_software =\
            queue_model.COLLECTION_ORIGIN.EDNA
        self._path_template.num_files = 2

        #
        # Layout
        #
        v_layout = QVBoxLayout(self, 2, 6, "v_layout")
        self._acq_widget = \
            AcquisitionWidgetSimple(self, acq_params = self._data_collection.\
                                    acquisitions[0].acquisition_parameters,
                                    path_template = self._path_template)
                
        self._vertical_dimension_widget = VerticalCrystalDimensionWidgetLayout(self)
        self._char_widget = CharacteriseSimpleWidgetVerticalLayout(self, 
                                                                 "characterise_widget")


        self._data_path_gbox = QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = DataPathWidgetVerticalLayout)

        v_layout.addWidget(self._acq_widget)
        v_layout.addWidget(self._char_widget)
        v_layout.addWidget(self._vertical_dimension_widget)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch(10)

        #
        # Logic
        #
        self._char_params_mib.bind_value_update('opt_sad', 
                                                 self._char_widget.optimised_sad_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('account_rad_damage', 
                                                 self._char_widget.account_rad_dmg_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('determine_rad_params', 
                                                 self._char_widget.induced_burn_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('strategy_complexity',
                                                 self._char_widget.start_comp_cbox,
                                                 int,
                                                 None)

        self._char_params_mib.bind_value_update('max_crystal_vdim',
                                                self._vertical_dimension_widget.max_vdim_ledit,
                                                float,
                                                QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('min_crystal_vdim',
                                                self._vertical_dimension_widget.min_vdim_ledit,
                                                float,
                                                QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('min_crystal_vphi',
                                                self._vertical_dimension_widget.min_vphi_ledit,
                                                float,
                                                QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('max_crystal_vphi',
                                                self._vertical_dimension_widget.max_vphi_ledit,
                                                float,
                                                QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('space_group',
                                                self._vertical_dimension_widget.space_group_ledit,
                                                str,
                                                None)

    def get_prefix_type(self):
        return 'ref'

#     def set_energy(self, pos, wav):
#         self._data_collection.acquisitions[0].acquisition_parameters.energy = \
#             round(float(wav), 4)
        
        
#     def set_transmission(self, trans):
#         self._data_collection.acquisitions[0].acquisition_parameters.transmission = \
#             round(float(trans), 1)
        

#     def set_resolution(self, res):
#         self._data_collection.acquisitions[0].acquisition_parameters.\
#             resolution = round(float(res), 4)


#     def set_run_number(self, run_number):
#         self._data_collection.acquisitions[0].\
#             path_template.run_number = run_number
#         self.acq_widget.run_number_ledit.\
#             setText(str(run_number))


#     def selection_changed(self, tree_item):
#         self.current_selected_item = tree_item
#         self.set_energies()

#         if isinstance(tree_item, queue_item.DataCollectionGroupQueueItem) or \
#                isinstance(tree_item, queue_item.DataCollectionQueueItem):
            
#             run_number = queue_model.\
#                          get_largest_prefix_with_name(tree_item, 
#                              self._data_collection.acquisitions[0].path_template.prefix) + 1 
#             self.set_run_number(run_number)
        
#         elif isinstance(tree_item, queue_item.SampleQueueItem):
#             self.set_run_number(1)


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. when a data collection group is selected.
    def _create_task(self, parent_task_node, sample):
        selected_positions = []
        tasks = []

        if not self._selected_positions:
            cpos = None
            
            if self._tree_brick.diffractometer_hwobj:
                pos_dict = self._tree_brick.diffractometer_hwobj.getPositions()
                cpos = queue_model.CentredPosition(pos_dict)

            logging.getLogger("user_level_log").\
                info("No centred position(s) was selected " + str(cpos) + \
                     " (current position) will be used.")

            selected_shapes = [shape_history.Point(None, cpos, None)]
        else:
            selected_shapes = self._qub_helper.selected_shapes

        for shape in selected_shapes:
            snapshot = None
            
            if isinstance(shape, shape_history.Point):
                sc = None
                 
                if not shape.get_drawing():
                    sc = queue_model.QueueModelFactory.\
                         create(queue_model.SampleCentring, parent_task_node)

                    sc.set_name('sample-centring')
                    
                    tasks.append(sc)

                data_collection = copy.deepcopy(self._data_collection)
                data_collection.acquisitions[0].\
                    acquisition_parameters.centred_position = \
                    copy.deepcopy(shape.centred_position)
                char_params = copy.deepcopy(self._char_params)

                if shape.qub_point is not None:
                    snapshot = self._qub_helper.get_snapshot([shape.qub_point])
                else:
                    snapshot = self._qub_helper.get_snapshot([])

                data_collection.acquisitions[0].acquisition_parameters.\
                    centred_position.snapshot_image = snapshot

                # Referance images for characterisations should be taken 90 deg apart
                # this is achived by setting overap to 89
                data_collection.acquisitions[0].\
                    acquisition_parameters.overlap = 89

                data_collection.experiment_type = queue_model.EXPERIMENT_TYPE.EDNA_REF

                if sc:
                    sc.set_task(data_collection)

                    
                char_name = data_collection.acquisitions[0].path_template.prefix + '_' + \
                    str(data_collection.acquisitions[0].path_template.run_number)

                char = queue_model.QueueModelFactory.\
                    create(queue_model.Characterisation, parent_task_node, data_collection, 
                           char_params, sample.crystals[0], char_name)

                # Increase run number for next collection
                self.set_run_number(self._path_template.run_number + 1)

  
                tasks.append(char)

        return tasks
