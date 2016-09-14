import qt
import logging
import queue_item
import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables
import abc
import copy
import ShapeHistory as shape_history
import os

#from BlissFramework.Utils import widget_colors


class CreateTaskBase(qt.QWidget):
    """
    Base class for widgets that are used to create tasks.
    Contains methods for handling the PathTemplate,
    AcqusitionParameters object, and other functionalty for
    creating Task objects.

    The members self._acq_widget and self._data_path_widget
    are used to reference the widgets for respective widgets.

    Tests for self.acq_widgets and self._data_path_widget is
    be made, to make this class generic for widgets not using
    the objects PathTemplate and AcquisitionParameters.
    """
    def __init__(self, parent, name, fl, task_node_name = 'Unamed task-node'):
         qt.QWidget.__init__(self, parent, name, fl)
         
         self._shape_history = None
         self._tree_brick = None
         self._task_node_name = task_node_name

         # Centred positons that currently are selected in the parent
         # widget, position_history_brick.
         self._selected_positions = []

         # Abstract attributes
         self._acq_widget = None
         self._data_path_widget = None
         self._current_selected_items = []
         self._path_template = None
         self._energy_scan_result = None
         self._session_hwobj = None
         self._beamline_setup_hwobj = None
         
         qt.QObject.connect(qt.qApp, qt.PYSIGNAL('tab_changed'),
                            self.tab_changed)

    def init_models(self):
        self.init_acq_model()
        self.init_data_path_model()

    def init_acq_model(self):
        bl_setup = self._beamline_setup_hwobj

        if bl_setup is not None:
            if self._acq_widget:
                self._acq_widget.set_beamline_setup(bl_setup)
                self._acquisition_parameters = bl_setup.get_default_acquisition_parameters()
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()

    def init_data_path_model(self):
        bl_setup = self._beamline_setup_hwobj

        if bl_setup is not None:
            # Initialize the path_template of the widget to default
            # values read from the beamline setup
            if self._data_path_widget:
                self._data_path_widget._base_image_dir = \
                    self._session_hwobj.get_base_image_directory()
                self._data_path_widget._base_process_dir = \
                    self._session_hwobj.get_base_process_directory()

                (data_directory, proc_directory) = self.get_default_directory()
                self._path_template = bl_setup.get_default_path_template()
                self._path_template.directory = data_directory
                self._path_template.process_directory = proc_directory
                self._path_template.base_prefix = self.get_default_prefix()
                self._path_template.run_number = bl_setup.queue_model_hwobj.\
                    get_next_run_number(self._path_template)
        else:
            self._path_template = queue_model_objects.PathTemplate()

    def tab_changed(self, tab_index, tab):
        # Update the selection if in the main tab and logged in to
        # ISPyB
        if self._session_hwobj:
            if tab_index is 0 and self._session_hwobj.proposal_code:
                self.update_selection()

    def set_beamline_setup(self, bl_setup_hwobj):
        self._beamline_setup_hwobj = bl_setup_hwobj

        try:
            bl_setup_hwobj.energy_hwobj.connect('energyChanged', self.set_energy)
            if bl_setup_hwobj.transmission_hwobj is not None:
                bl_setup_hwobj.transmission_hwobj.connect('attFactorChanged', self.set_transmission)
            if bl_setup_hwobj.resolution_hwobj is not None:
                bl_setup_hwobj.resolution_hwobj.connect('positionChanged', self.set_resolution)
            if bl_setup_hwobj.omega_axis_hwobj is not None:
                bl_setup_hwobj.omega_axis_hwobj.connect('positionChanged', self.update_osc_start)
            #TODO discuss dynamic value limits
            #bl_setup_hwobj.energy_hwobj.connect('energyLimitsChanged', self.set_energy_limits)
            #bl_setup_hwobj.transmission_hwobj.connect('attLimitsChanged', self.set_transmission_limits)
            #bl_setup_hwobj.resolution_hwobj.connect('limitsChanged', self.set_resolution_limits)

            if bl_setup_hwobj.kappa_axis_hwobj is not None:
                bl_setup_hwobj.kappa_axis_hwobj.connect('positionChanged', self.set_kappa)
            if bl_setup_hwobj.kappa_phi_axis_hwobj is not None:
                bl_setup_hwobj.kappa_phi_axis_hwobj.connect('positionChanged', self.set_kappa_phi)
            #bl_setup_hwobj.detector_hwobj.connect('detectorModeChanged', self.set_detector_mode)
            #bl_setup_hwobj.detector_hwobj.connect('expTimeLimitsChanged', self.set_detector_exp_time_limits)
            #bl_setup_hwobj.beam_info_hwobj.connect('beamInfoChanged', self.set_beam_info)
        except AttributeError as ex:
            msg = 'Could not connect to one or more hardware objects' + str(ex)
            logging.getLogger("HWR").warning(msg)
        
        self._shape_history = bl_setup_hwobj.shape_history_hwobj
        self._session_hwobj = bl_setup_hwobj.session_hwobj
        self.init_models()

    def update_osc_start(self, new_value):
        acq_widget = self.get_acquisition_widget()

        if acq_widget:
            acq_widget.update_osc_start(new_value)

    def update_kappa(self, new_value):
        acq_widget = self.get_acquisition_widget()

        if acq_widget:
            self.kappa_value = new_value
            acq_widget.update_kappa(new_value)

    def update_kappa_phi(self, new_value):
        acq_widget = self.get_acquisition_widget()

        if acq_widget:
            self.kappa_phi_value = new_value
            acq_widget.update_kappa_phi(new_value)

    def _prefix_ledit_change(self, new_value):
        item = self._current_selected_items[0]
        model = item.get_model()

        if self.isEnabled():
            if isinstance(item, queue_item.TaskQueueItem) and \
                   not isinstance(item, queue_item.DataCollectionGroupQueueItem):
                self._path_template.base_prefix = str(new_value)
                name = self._path_template.get_prefix()
                model.set_name(name)
                #item.setText(0, model.get_name())
                item.setText(0, model.get_display_name())

    def refresh_current_item(self):
        if len(self._current_selected_items) > 0:
            item = self._current_selected_items[0]
            model = item.get_model()
            if self.isEnabled():
                if isinstance(item, queue_item.TaskQueueItem) and \
                     not isinstance(item, queue_item.DataCollectionGroupQueueItem):
                    name = self._path_template.get_prefix()
                    model.set_name(name)
                    item.setText(0, model.get_display_name())
        
    def _run_number_ledit_change(self, new_value):
        item = self._current_selected_items[0]
        model = item.get_model()

        if self.isEnabled():
            if isinstance(item, queue_item.TaskQueueItem) and \
                   not isinstance(item, queue_item.DataCollectionGroupQueueItem):
                if str(new_value).isdigit():
                    model.set_number(int(new_value))
                    #item.setText(0, model.get_name())
                    item.setText(0, model.get_display_name())

    def handle_path_conflict(self, widget, new_value):
        self._tree_brick.dc_tree_widget.check_for_path_collisions()
        
        path_conflict = self._beamline_setup_hwobj.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if new_value != '':
            self._data_path_widget.indicate_path_conflict(path_conflict)                    
        
    def set_tree_brick(self, brick):
        self._tree_brick = brick

    @abc.abstractmethod
    def set_energies(self):
        pass
 
    def get_sample_item(self, item):
        if isinstance(item, queue_item.SampleQueueItem):
            return item
        elif isinstance(item, queue_item.TaskQueueItem):
            return item.get_sample_view_item()
        else:
            return None

    def get_group_item(self, item):
        if isinstance(item, queue_item.DataCollectionGroupQueueItem):
            return item
        elif isinstance(item, queue_item.TaskQueueItem):
            return self.item.parent()
        else:
            return None

    def get_acquisition_widget(self):
        return self._acq_widget

    def get_data_path_widget(self):
        return self._data_path_widget

    def _item_is_group_or_sample(self):
        result = False
        
        if self._current_selected_items:
            item = self._current_selected_items[0]
        
            if isinstance(item, queue_item.SampleQueueItem) or \
                isinstance(item, queue_item.DataCollectionGroupQueueItem):
                    result = True
                    
        return result

    def set_energy(self, energy, wavelength):         
        if self._item_is_group_or_sample() and energy:
            acq_widget = self.get_acquisition_widget()
            
            if acq_widget:
                acq_widget.previous_energy = energy
                acq_widget.set_energy(energy, wavelength)

    def set_transmission(self, trans):
        acq_widget = self.get_acquisition_widget()
        
        if self._item_is_group_or_sample() and acq_widget:
            acq_widget.update_transmission(trans)

    def set_resolution(self, res):
        acq_widget = self.get_acquisition_widget()
        
        if self._item_is_group_or_sample() and acq_widget:
            acq_widget.update_resolution(res)

    def set_detector_mode(self, detector_mode):
        acq_widget = self.get_acquisition_widget()

        if acq_widget:
            acq_widget.update_detector_mode(detector_mode)

    def set_kappa(self, kappa):
        acq_widget = self.get_acquisition_widget()

        if self._item_is_group_or_sample() and acq_widget:
            acq_widget.update_kappa(kappa)

    def set_kappa_phi(self, kappa_phi):
        acq_widget = self.get_acquisition_widget()
        if self._item_is_group_or_sample() and acq_widget:
            acq_widget.update_kappa_phi(kappa_phi)

    def set_energy_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()
            if acq_widget:
                acq_widget.update_energy_limits(limits)

    def set_transmission_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_transmission_limits(limits)

    def set_resolution_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_resolution_limits(limits)

    def set_detector_exp_time_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_detector_exp_time_limits(limits)

    def set_beam_info(self, beam_info_dict):
        pass
                                                      
    def set_run_number(self, run_number):
        data_path_widget = self.get_data_path_widget()

        if data_path_widget:
            data_path_widget.set_run_number(run_number)

    def get_default_prefix(self, sample_data_node = None, generic_name = False):
        prefix = self._session_hwobj.get_default_prefix(sample_data_node, generic_name)
        return prefix
        
    def get_default_directory(self, tree_item = None, sub_dir = ''):
        group_name = self._session_hwobj.get_group_name()

        if group_name:
            sub_dir = group_name + '/' + sub_dir

        if tree_item:
            item = self.get_sample_item(tree_item)            
            sub_dir += item.get_model().get_name()

            if isinstance(item, queue_item.SampleQueueItem):
                if item.get_model().lims_id == -1:
                    sub_dir += ''
            
        data_directory = self._session_hwobj.\
                         get_image_directory(sub_dir)

        try:
            proc_directory = self._session_hwobj.\
                get_process_directory(sub_dir)
        except AttributeError:
            proc_directory = ''
    
        return (data_directory, proc_directory)

    def ispyb_logged_in(self, logged_in):
        self.init_models()
        self.update_selection()

    def select_shape_with_cpos(self, cpos):
        self._shape_history.select_shape_with_cpos(cpos)
            
    def selection_changed(self, items):
        if items:
            if len(items) == 1:
                self._current_selected_items = items
                self.single_item_selection(items[0])
            elif len(items) > 1:                
                sample_items = []

                # Allow mutiple selections on sample items, only.
                for item in items:
                    if isinstance(item, queue_item.SampleQueueItem):
                        sample_items.append(item)

                if sample_items:
                    self._current_selected_items = sample_items
                    self.multiple_item_selection(sample_items)
        else:
            self.setDisabled(True)

    def update_selection(self):
        self.selection_changed(self._current_selected_items)

    def single_item_selection(self, tree_item):
        sample_item = self.get_sample_item(tree_item)
        
        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_data_model = sample_item.get_model()
            self._path_template = copy.deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)

            # Sample with lims information, use values from lims
            # to set the data path. Or has a specific user group set.
            if sample_data_model.lims_id != -1:
                prefix = self.get_default_prefix(sample_data_model)
                (data_directory, proc_directory) = self.get_default_directory(tree_item, \
                                 sub_dir = "%s%s" % (prefix.split("-")[0], os.path.sep))
                self._path_template.directory = data_directory
                self._path_template.process_directory = proc_directory
                self._path_template.base_prefix = prefix
            elif self._session_hwobj.get_group_name() != '':
                base_dir = self._session_hwobj.get_base_image_directory()
                # Update with group name as long as user didn't specify
                # differnt path.
                if base_dir == self._path_template.directory:
                    (data_directory, proc_directory) = self.get_default_directory()
                    self._path_template.directory = data_directory
                    self._path_template.process_directory = proc_directory
                    self._path_template.base_prefix = self.get_default_prefix()

            # Get the next available run number at this level of the model.
            self._path_template.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                get_next_run_number(self._path_template)

            #Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                sample_data_model = sample_item.get_model()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
                self.get_acquisition_widget().use_osc_start(False)

            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)

            self.setDisabled(False)
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self.setDisabled(False)
            self._path_template = copy.deepcopy(self._path_template)
            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)
        elif isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            self.setDisabled(True)
            self._path_template = copy.deepcopy(self._path_template)
            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)

    def _update_etr(self):
        energy = self._beamline_setup_hwobj._get_energy()
        transmission = self._beamline_setup_hwobj._get_transmission()
        resolution = self._beamline_setup_hwobj._get_resolution()
                
        self._acquisition_parameters.energy = energy
        self._acquisition_parameters.transmission = transmission
        self._acquisition_parameters.resolution = resolution

    def multiple_item_selection(self, tree_items):
        tree_item = tree_items[0]
        
        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_data_model = tree_item.get_model()
            self._path_template = copy.deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)

            # Sample with lims information, use values from lims
            # to set the data path.
            (data_directory, proc_directory) = self.get_default_directory(\
                             sub_dir = '<acronym>%s<sample_name>%s' % (os.path.sep, os.path.sep))    
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(generic_name = True)

            # Get the next available run number at this level of the model.
            self._path_template.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                get_next_run_number(self._path_template)

            #Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
                self.get_acquisition_widget().use_osc_start(False)

            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)

            self.setDisabled(False)

    # Called by the owning widget (task_toolbox_widget) when
    # one or several centred positions are selected.
    def centred_position_selection(self, positions):
        """
        Descript. : Called by the owning widget (task_toolbox_widget) when
                    one or several centred positions are selected. 
                    Updates kappa/phi position from the centring point
                    Enables kappa/phi edit if not collection item and no
                    centring point is selected. In all other cases kappa/phi
                    edit is disabled.
                    Also updates centring point if a data collection item is
                    selected and new centring point clicked 
        Args.     : centring points
        Return    "
        """
        self._selected_positions = positions

        if self._acq_widget:
            self._acq_widget.use_kappa(False)
            self._acq_widget.use_kappa_phi(False)

            if len(self._current_selected_items) == 1:
                item = self._current_selected_items[0]
                if len(positions) == 1:
                    pos = positions[0]
                    if isinstance(pos, shape_history.Point):
                        cpos = pos.get_centred_positions()[0]
                        if cpos.kappa is not None:
                            self._acq_widget.update_kappa(cpos.kappa)
                            self._acq_widget.update_kappa_phi(cpos.kappa_phi)
                        if isinstance(item, queue_item.TaskQueueItem):
                            snapshot = self._shape_history.get_snapshot([pos.qub_point])
                            cpos.snapshot_image = snapshot
                            self._acquisition_parameters.centred_position = cpos
                elif len(positions) == 0:
                    if isinstance(item, queue_item.SampleQueueItem):
                        self._acq_widget.use_kappa(True)
                        self._acq_widget.use_kappa_phi(True)


    # Should be called by the object that calls create_task,
    # and add_task.
    def approve_creation(self):
        result = True
        
        path_conflict = self._beamline_setup_hwobj.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if path_conflict:
            logging.getLogger("user_level_log").\
                error('The current path settings will overwrite data' +\
                      ' from another task. Correct the problem before adding to queue')
            result = False

        #Decide how to make this more general 
        """if self._acq_widget is not None:
            parameter_conflict =  self._acq_widget.check_parameter_conflict()
            if parameter_conflict:
                logging.getLogger("user_level_log").\
                    error('One or several collection parameters are out of range. ' +\
                          'Correct the problem before adding to queue')
                result = False"""

        return result
            
    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a task_node is selected.
    def create_task(self, sample, shape):
        (tasks, sc) = ([], None)

        try: 
            sample_is_mounted = self._beamline_setup_hwobj.sample_changer_hwobj.\
                                getLoadedSample().getCoords() == sample.location
        except AttributeError:
            sample_is_mounted = False

        try:
            dm = self._beamline_setup_hwobj.diffractometer_hwobj
            fully_automatic = (not dm.user_confirms_centring)
        except AttributeError:
            fully_automatic = False

        free_pin_mode = sample.free_pin_mode
        temp_tasks = self._create_task(sample, shape)

        if (not fully_automatic):
            if ((not free_pin_mode) and (not sample_is_mounted) or (not shape)):
                # No centred positions selected, or selected sample not
                # mounted create sample centring task.

                # Check if the tasks requires centring, assumes that all
                # the "sub tasks" has the same centring requirements.
                if temp_tasks[0].requires_centring():
                    kappa = None
                    kappa_phi = None
                    task_label = 'sample-centring'
                    if isinstance(temp_tasks[0], queue_model_objects.DataCollection):
                        kappa = temp_tasks[0].acquisitions[0].acquisition_parameters.kappa
                        kappa_phi = temp_tasks[0].acquisitions[0].acquisition_parameters.kappa_phi
                        if kappa and kappa_phi:
                            task_label = 'sample-centring (kappa: %0.2f, phi: %0.2f)' %(kappa, kappa_phi)
                    elif isinstance(temp_tasks[0], queue_model_objects.Characterisation):
                        kappa = temp_tasks[0].reference_image_collection.acquisitions[0].acquisition_parameters.kappa
                        kappa_phi = temp_tasks[0].reference_image_collection.acquisitions[0].acquisition_parameters.kappa_phi
                        if kappa and kappa_phi:
                            task_label = 'sample-centring (kappa: %0.2f, phi: %0.2f)' %(kappa, kappa_phi)
                    sc = queue_model_objects.SampleCentring(task_label, kappa, kappa_phi)
                    tasks.append(sc)


        for task in temp_tasks:
            if sc:
                sc.add_task(task)
            tasks.append(task)

        return tasks

    @abc.abstractmethod
    def _create_task(self, task_node, shape):
        pass

    def _create_path_template(self, sample, path_template):
        bl_setup = self._beamline_setup_hwobj

        acq_path_template = copy.deepcopy(path_template)

        if '<sample_name>' in acq_path_template.directory:
            name = sample.get_name().replace(':', '-')
            acq_path_template.directory = acq_path_template.directory.\
                                          replace('<sample_name>', name)
            acq_path_template.process_directory = acq_path_template.process_directory.\
                                                  replace('<sample_name>', name)

        if '<acronym>-<name>' in acq_path_template.base_prefix:
            acq_path_template.base_prefix = self.get_default_prefix(sample)
            acq_path_template.run_number = bl_setup.queue_model_hwobj.get_next_run_number(acq_path_template)

        if '<acronym>' in acq_path_template.directory:
            prefix = self.get_default_prefix(sample)
            acronym = prefix.split("-")[0]
            acq_path_template.directory = acq_path_template.directory.\
                                          replace('<acronym>', acronym)
            acq_path_template.process_directory = acq_path_template.process_directory.\
                                                  replace('<acronym>', acronym)

        #acq_path_template.suffix = bl_setup.suffix

        return acq_path_template

    def _create_acq(self, sample):
        parameters = self._acquisition_parameters
        path_template = self._path_template
        shape_history = self._shape_history
        processing_parameters = self._processing_parameters
        bl_setup = self._beamline_setup_hwobj

        acq = queue_model_objects.Acquisition()
        acq.acquisition_parameters = \
            copy.deepcopy(parameters)
        acq.acquisition_parameters.collect_agent = \
            queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
        
        acq.path_template = self._create_path_template(sample, path_template)

        """
        if bl_setup.diffractometer_hwobj.in_plate_mode():
            acq.acquisition_parameters.take_snapshots = False
        else:
            acq.acquisition_parameters.take_snapshots = True
        """

        return acq
