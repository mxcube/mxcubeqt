import qt
import logging
import queue_item
import queue_model_objects_v1 as queue_model_objects
import widget_utils
import abc
import os

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
         self._current_selected_item = None
         self._path_template = None
         self._energy_scan_result = None
         self._session_hwobj = None
         self._bl_config_hwobj = None
         
         qt.QObject.connect(qt.qApp, qt.PYSIGNAL('tab_changed'),
                            self.tab_changed)


    def tab_changed(self, tab_index, tab):
        if tab_index is 0:
            self.selection_changed(self._current_selected_item)


    def set_tree_brick(self, brick):
        self._tree_brick = brick


    def set_shape_history(self, shape_history):
        self._shape_history = shape_history


    def set_session(self, session_hwobj):
        self._session_hwobj = session_hwobj

        if self._data_path_widget:
            self._data_path_widget.set_session(session_hwobj)


    def set_bl_config(self, bl_config):
        self._bl_config = bl_config

        if self._acq_widget:
            self._acq_widget.set_bl_config(bl_config)


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


    def get_sample_item(self):
        if isinstance(self._current_selected_item, queue_item.SampleQueueItem):
            return self._current_selected_item
        elif isinstance(self._current_selected_item, queue_item.TaskQueueItem):
            return self._current_selected_item.get_sample_view_item()
        else:
            return None


    def get_group_item(self):
        if isinstance(self._current_selected_item, queue_item.DataCollectionGroupQueueItem):
            return self._current_selected_item
        elif isinstance(self._current_selected_item, queue_item.TaskQueueItem):
            return self._current_selected_item.parent()
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

    
    def _selection_changed(self, tree_item):
        pass


    def get_default_prefix(self, sample_data_node):
        prefix = self._session_hwobj.get_default_prefix(sample_data_node)
        return prefix

        
    def get_default_directory(self, sample_data_node):
        sub_dir = str()
        item = self.get_group_item()
        
        if not item:
            item = self.get_sample_item()
            
        data_directory = self._session_hwobj.\
                         get_image_directory(item.get_model())
        proc_directory = self._session_hwobj.\
                         get_process_directory(item.get_model())
    
        return (data_directory,
                proc_directory)


    def ispyb_logged_in(self, logged_in):        
        data_path_widget = self.get_data_path_widget()
        sample_item = self.get_sample_item()
        sample_data_node = sample_item.get_model() if sample_item else None

        if data_path_widget and sample_data_node:
            (data_directory, proc_directory) = self.get_default_directory(sample_data_node)
            prefix = self.get_default_prefix(sample_data_node)

            data_path_widget.set_directory(data_directory)
            data_path_widget.set_prefix(prefix)
            self._path_template.process_directory = proc_directory
            

    def selection_changed(self, tree_item):
        self._current_selected_item = tree_item
        self._selection_changed(tree_item)


    # Called by the owning widget (task_toolbox_widget) when
    # one or several centred positions are selected.
    def centred_position_selection(self, positions):
         self._selected_positions = positions


    # Should be called by the object that calls create_task,
    # and add_task.
    def approve_creation(self):
        return True


    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a task_node is selected.
    def create_task(self, task_node, sample):        
        tasks = self._create_task(task_node, sample)
        
        # Increase run number for next collection
        #if not isinstance(self._current_selected_item, 
        #                  queue_item.SampleQueueItem):
        #    self.set_run_number(self._path_template.run_number + 1)

        return tasks


    @abc.abstractmethod
    def _create_task(self, task_node, sample):
        pass


    def get_next_group_name(self, sample_item):
        task_node_names = []
        task_node_item = sample_item.firstChild()

        while task_node_item:
            task_node_names.append(str(task_node_item.text()))
            task_node_item = task_node_item.nextSibling()

        num = widget_utils.next_free_name(task_node_names, 
                                          self._task_node_name)

        return self._task_node_name + ' - ' + str(num)


    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a sample is selected.
    def create_parent_task_node(self):
        group_task_node = queue_model_objects.TaskGroup()
        group_task_node.set_name(self._task_node_name)
                                
        return group_task_node
