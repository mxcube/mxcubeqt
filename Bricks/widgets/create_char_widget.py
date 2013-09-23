import os
import qtui
import qt
import copy
import logging
import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables
import queue_item
import ShapeHistory as shape_history

from widgets.widget_utils import DataModelInputBinder
from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from acquisition_widget_simple import AcquisitionWidgetSimple

from queue_model_enumerables_v1 import XTAL_SPACEGROUPS


class CreateCharWidget(CreateTaskBase):
    def __init__(self,parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Characterisation')

        if not name:
            self.setName("create_char_widget")

        #
        # Data attributes
        #
        self._current_selected_item = None
        self.init_models()
        self._char_params_mib = DataModelInputBinder(self._char_params)
   
        #
        # Layout
        #
        v_layout = qt.QVBoxLayout(self, 2, 6, "v_layout")
        
        self._acq_widget = \
            AcquisitionWidgetSimple(self, acq_params = self._acquisition_parameters,
                                    path_template = self._path_template)

        current_dir = os.path.dirname(__file__)
        ui_file = 'ui_files/vertical_crystal_dimension_widget_layout.ui'
        widget = qtui.QWidgetFactory.\
                 create(os.path.join(current_dir, ui_file))

        widget.reparent(self, qt.QPoint(0,0))
        self._vertical_dimension_widget = widget

        ui_file = 'ui_files/characterise_simple_widget_vertical_layout.ui'
        widget = qtui.QWidgetFactory.\
                 create(os.path.join(current_dir, ui_file))

        widget.reparent(self, qt.QPoint(0,0))
        self._char_widget = widget

        self._data_path_gbox = \
            qt.QVGroupBox('Data location', self, 'data_path_gbox')
        
        self._data_path_widget = \
            DataPathWidget(self._data_path_gbox, 
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
        optimised_sad_cbx = self._char_widget.\
                            child('optimised_sad_cbx')
        account_rad_dmg_cbx = self._char_widget.\
                              child('account_rad_dmg_cbx')
        start_comp_cbox = self._char_widget.child('start_comp_cbox')
        induced_burn_cbx = self._char_widget.child('induced_burn_cbx')
        max_vdim_ledit = self._vertical_dimension_widget.\
                         child('max_vdim_ledit')
        min_vdim_ledit = self._vertical_dimension_widget.\
                         child('min_vdim_ledit')

        min_vphi_ledit = self._vertical_dimension_widget.\
                         child('min_vphi_ledit')

        max_vphi_ledit = self._vertical_dimension_widget.\
                         child('max_vphi_ledit')

        space_group_ledit = self._vertical_dimension_widget.\
                            child('space_group_ledit')
        
        self._char_params_mib.bind_value_update('opt_sad',
                                                optimised_sad_cbx,
                                                bool, None)

        self._char_params_mib.bind_value_update('account_rad_damage', 
                                                account_rad_dmg_cbx,
                                                bool, None)

        self._char_params_mib.bind_value_update('determine_rad_params', 
                                                induced_burn_cbx,
                                                bool, None)

        self._char_params_mib.bind_value_update('strategy_complexity',
                                                start_comp_cbox,
                                                int, None)

        self._char_params_mib.\
            bind_value_update('max_crystal_vdim',
                              max_vdim_ledit, float,
                              qt.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('min_crystal_vdim',
                              min_vdim_ledit, float,
                              qt.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('min_crystal_vphi',
                              min_vphi_ledit, float,
                              qt.QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.\
            bind_value_update('max_crystal_vphi',
                              max_vphi_ledit, float,
                              qt.QDoubleValidator(0.0, 1000, 2, self))
        
        space_group_ledit.insertStrList(XTAL_SPACEGROUPS)

        prefix_ledit = self._data_path_widget.\
                       data_path_widget_layout.prefix_ledit

        run_number_ledit = self._data_path_widget.\
                           data_path_widget_layout.run_number_ledit

        self.connect(prefix_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)

        self.connect(run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)

        self.connect(space_group_ledit,
                     qt.SIGNAL("activated(int)"),
                     self._space_group_change)

        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

    def _space_group_change(self, index):
       self._char_params.space_group = queue_model_enumerables.\
                                       XTAL_SPACEGROUPS[index]
    def _set_space_group(self, space_group):
        index  = 0
        
        if space_group in XTAL_SPACEGROUPS:
            index = XTAL_SPACEGROUPS.index(space_group)

        self._space_group_change(index)
        self._vertical_dimension_widget.\
            child('space_group_ledit').setCurrentItem(index)

    def init_models(self):
        CreateTaskBase.init_models(self)
        
        self._char = queue_model_objects.Characterisation()
        self._char_params = self._char.characterisation_parameters
        self._char_params.experiment_type = queue_model_enumerables.EXPERIMENT_TYPE.OSC
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:            
            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_characterisation_parameters()

            try:
                transmission = self._beamline_setup_hwobj.transmission_hwobj.getAttFactor()
                transmission = round(float(transmission), 1)
            except AttributeError:
                transmission = 0

            try:
                resolution = self._beamline_setup_hwobj.resolution_hwobj.getPosition()
                resolution = round(float(resolution), 4)
            except AttributeError:
                resolution = 0

            try:
                energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
                energy = round(float(energy), 2)
            except AttributeError:
                energy = 0

            self._acquisition_parameters.resolution = resolution
            self._acquisition_parameters.energy = energy
            self._acquisition_parameters.transmission = transmission
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            
        self._path_template.reference_image_prefix = 'ref'
        # The num images drop down default value is 1
        # we would like it to be 2
        self._acquisition_parameters.num_images = 2
        self._char.characterisation_software =\
            queue_model_enumerables.COLLECTION_ORIGIN.EDNA
        self._path_template.num_files = 2
        self._acquisition_parameters.shutterless = False

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            sample_data_model = self.get_sample_item(tree_item).get_model()
            self.update_processing_parameters(sample_data_model.crystals[0])

        elif isinstance(tree_item, queue_item.CharacterisationQueueItem):
            self.setDisabled(False)
            self._char = tree_item.get_model()

            if self._char.get_path_template():
                self._path_template = self._char.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
            
            data_collection = self._char.reference_image_collection

            self._char_params = self._char.characterisation_parameters
            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters

            if len(data_collection.acquisitions) == 1:
                self.select_shape_with_cpos(self._acquisition_parameters.\
                                            centred_position)

            self._processing_parameters = data_collection.processing_parameters
        else:
            self.setDisabled(True)

        if isinstance(tree_item, queue_item.SampleQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionGroupQueueItem) or \
           isinstance(tree_item, queue_item.CharacterisationQueueItem):

            self._set_space_group(self._char_params.space_group)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
            self._char_params_mib.set_model(self._char_params)

    def update_processing_parameters(self, crystal):
        self._processing_parameters.space_group = crystal.space_group
        self._char_params.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma

    def approve_creation(self):
        return CreateTaskBase.approve_creation(self)
        
    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. when a data collection group is selected.
    def _create_task(self, sample):
        tasks = []

        if not self._selected_positions:
            cpos = None
            
            if self._beamline_setup_hwobj.diffractometer_hwobj:
                pos_dict = self._beamline_setup_hwobj.\
                           diffractometer_hwobj.getPositions()
                cpos = queue_model_objects.CentredPosition(pos_dict)

            logging.getLogger("user_level_log").\
                info("No centred position(s) was selected " + str(cpos) + \
                     " (current position) will be used.")

            selected_shapes = [shape_history.Point(self._shape_history.get_drawing(), cpos, None)]
        else:
            selected_shapes = self._shape_history.selected_shapes

        for shape in selected_shapes:
            snapshot = None
            
            if isinstance(shape, shape_history.Point):
                sc = None
                sample_is_mounted = self._beamline_setup_hwobj.sample_changer_hwobj.\
                                    is_mounted_sample(sample)
                
                if (not shape.screen_pos) or (not sample_is_mounted):
                    sc = queue_model_objects.SampleCentring()
                    sc.set_name('sample-centring')
                    tasks.append(sc)

                char_params = copy.deepcopy(self._char_params)

                if shape.qub_point is not None:
                    snapshot = self._shape_history.get_snapshot([shape.qub_point])
                else:
                    snapshot = self._shape_history.get_snapshot([])

                # Acquisition for start position
                acq = queue_model_objects.Acquisition()
                acq.acquisition_parameters = \
                    copy.deepcopy(self._acquisition_parameters)
                acq.acquisition_parameters.collect_agent = \
                    queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
                acq.acquisition_parameters.\
                    centred_position = shape.get_centred_positions()[0]
                acq.path_template = copy.deepcopy(self._path_template)
                acq.acquisition_parameters.centred_position.\
                    snapshot_image = snapshot

                if '<sample_name>' in acq.path_template.directory:
                    name = sample.get_name().replace(':', '-')
                    acq.path_template.directory = acq.path_template.directory.\
                                                  replace('<sample_name>', name)
                    acq.path_template.process_directory = acq.path_template.process_directory.\
                                                          replace('<sample_name>', name)

                if '<acronym>-<name>' in acq.path_template.base_prefix:
                    acq.path_template.base_prefix = self.get_default_prefix(sample)
                    acq.path_template.run_numer = self._beamline_setup_hwobj.queue_model_hwobj.\
                                                  get_next_run_number(acq.path_template)

                processing_parameters = copy.deepcopy(self._processing_parameters)

                data_collection = queue_model_objects.\
                                  DataCollection([acq], sample.crystals[0],
                                                 processing_parameters)

                # Referance images for characterisations should be taken 90 deg apart
                # this is achived by setting overap to 89
                acq.acquisition_parameters.overlap = 89
                data_collection.acquisitions[0] = acq               
                data_collection.experiment_type = queue_model_enumerables.EXPERIMENT_TYPE.EDNA_REF

                if sc:
                    sc.add_task(data_collection)
                    
                char = queue_model_objects.Characterisation(data_collection, 
                                                            char_params)
                char.set_name(data_collection.acquisitions[0].\
                              path_template.get_prefix())
                char.set_number(data_collection.acquisitions[0].\
                                path_template.run_number)

                # Increase run number for next collection
                #self.set_run_number(self._path_template.run_number + 1)

                tasks.append(char)
                self._path_template.run_number += 1

        return tasks
