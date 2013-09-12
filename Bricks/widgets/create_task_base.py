import qt
import logging
import queue_item
import queue_model_objects_v1 as queue_model_objects
import abc


from BlissFramework.Utils import widget_colors


class CreateTaskBase(qt.QWidget):
    def __init__(self, parent, name, fl, task_node_name = 'Unamed task-node'):
         qt.QWidget.__init__(self, parent, name, fl)
         
         self._shape_history = None
         self._tree_brick = None
         self._task_node_name = task_node_name

         # Centred positons that currently are selected in the parent widget,
         # position_history_brick.
         self._selected_positions = []

         # Abstract attributes
         self._acq_widget = None
         self._data_path_widget = None
         self._current_selected_items = None
         self._path_template = None
         self._energy_scan_result = None
         self._session_hwobj = None
         self._beamline_setup_hwobj = None
         
         qt.QObject.connect(qt.qApp, qt.PYSIGNAL('tab_changed'),
                            self.tab_changed)

    def init_models(self):
        if self._beamline_setup_hwobj is not None:
            self._path_template = self._beamline_setup_hwobj.get_default_path_template()
        else:
            self._path_template = queue_model_objects.PathTemplate()

    def tab_changed(self, tab_index, tab):
        if tab_index is 0 and self._session_hwobj.proposal_code:
            self.update_selection()

    def set_beamline_setup(self, bl_setup_hwobj):
        self._beamline_setup_hwobj = bl_setup_hwobj
        self._shape_history = bl_setup_hwobj.shape_history_hwobj
        self._session_hwobj = bl_setup_hwobj.session_hwobj

        if self._acq_widget:
            self._acq_widget.set_beamline_setup(self._beamline_setup_hwobj)

            try:
                transmission = bl_setup_hwobj.transmission_hwobj.getAttFactor()
            except AttributeError:
                transmission = 0

            try:
                resolution = bl_setup_hwobj.resolution_hwobj.getPosition()
            except AttributeError:
                resolution = 0

            try:
                energy =  bl_setup_hwobj.energy_hwobj.getCurrentEnergy()
            except AttributeError:
                energy = 0
                
            self.set_energy(energy, 0)
            self.set_transmission(transmission)
            self.set_resolution(resolution)

            try:
                bl_setup_hwobj.energy_hwobj.connect('energyChanged',
                                                    self.set_energy)
                
                bl_setup_hwobj.transmission_hwobj.connect('attFactorChanged',
                                                          self.set_transmission)
                
                bl_setup_hwobj.resolution_hwobj.connect('positionChanged',
                                                        self.set_resolution)
            except AttributeError as ex:
                logging.getLogger("HWR").exception('Could not connect to one or '+\
                                                   'more hardware objects' + str(ex))

        if self._data_path_widget:
            self._data_path_widget.set_session(self._session_hwobj)

    def _prefix_ledit_change(self, new_value):
        item = self._current_selected_items[0]
        
        if isinstance(item, queue_item.TaskQueueItem) and \
               not isinstance(item, queue_item.DataCollectionGroupQueueItem):
            item.get_model().set_name(prefix)
            item.setText(0, item.get_model().get_name())
        
    def _run_number_ledit_change(self, new_value):
        item = self._current_selected_items[0]
        
        if isinstance(item, queue_item.TaskQueueItem) and \
               not isinstance(item, queue_item.DataCollectionGroupQueueItem):
            if str(new_value).isdigit():
                item.get_model().set_number(int(new_value))
                item.setText(0, item.get_model().get_name())

    def handle_path_conflict(self, widget, new_value):
        self._tree_brick.dc_tree_widget.check_for_path_collisions()
        
        path_conflict = self._beamline_setup_hwobj.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if new_value != '':
            if path_conflict:
                logging.getLogger("user_level_log").\
                    error('The current path settings will overwrite data' +\
                          ' from another task. Correct the problem before adding to queue')

                widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
            else:
                widget.setPaletteBackgroundColor(widget_colors.WHITE)
        
    def set_tree_brick(self, brick):
        self._tree_brick = brick

    @abc.abstractmethod
    def set_energies(self):
        pass
 
    def mad_energy_selected(self, name, energy, state):
        data_path_widget = self.get_data_path_widget()

        if data_path_widget:
            if state:
                self._path_template.mad_prefix = name
            else:
                self._path_template.mad_prefix = ''

            data_path_widget.set_prefix(self._path_template.base_prefix)

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

    def set_energy(self, energy, wavelength):
        if energy:
            acq_widget = self.get_acquisition_widget()
        
            if acq_widget:
                acq_widget.set_energy(energy, wavelength)

    def set_transmission(self, trans):
        acq_widget = self.get_acquisition_widget()
        
        if acq_widget:
            acq_widget.update_transmission(trans)

    def set_resolution(self, res):
        acq_widget = self.get_acquisition_widget()
        
        if acq_widget:
            acq_widget.update_resolution(res)
                                                      
    def set_run_number(self, run_number):
        data_path_widget = self.get_data_path_widget()

        if data_path_widget:
            data_path_widget.set_run_number(run_number)

    def get_default_prefix(self, sample_data_node):
        prefix = self._session_hwobj.get_default_prefix(sample_data_node)
        return prefix
        
    def get_default_directory(self, tree_item):        
        item = self.get_sample_item(tree_item)
        sub_dir = item.get_model().get_name()
            
        data_directory = self._session_hwobj.\
                         get_image_directory(sub_dir)

        proc_directory = self._session_hwobj.\
                         get_process_directory(sub_dir)
    
        return (data_directory, proc_directory)

    def ispyb_logged_in(self, logged_in):
        if logged_in and self.get_data_path_widget():
            self.update_selection()
            
    def selection_changed(self, items):
        if items:
            self._current_selected_items = items
        
            if len(items) == 1:
                self.single_item_selection(items[0])
            elif len(items) > 1:
                self.multiple_item_selection(items)
        else:
            self.setDisabled(True)

    def update_selection(self):
        self.selection_changed(self._current_selected_items)

    def single_item_selection(self, tree_item):
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            self.init_models()
            sample_data_model = self.get_sample_item(tree_item).get_model()
            
            (data_directory, proc_directory) = self.get_default_directory(tree_item)
                
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(sample_data_model)
            self._path_template.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                                             get_next_run_number(self._path_template)
            self.setDisabled(False)
            
        if self._data_path_widget:
            self._data_path_widget.update_data_model(self._path_template)

    def multiple_item_selection(self, tree_items):
        pass

    # Called by the owning widget (task_toolbox_widget) when
    # one or several centred positions are selected.
    def centred_position_selection(self, positions):
         self._selected_positions = positions

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

        return result
            
    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a task_node is selected.
    def create_task(self, sample):        
        tasks = self._create_task(sample)        
        return tasks

    @abc.abstractmethod
    def _create_task(self, task_node, sample):
        pass
