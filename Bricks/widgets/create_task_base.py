import qt
import logging
import queue_item
import queue_model
import widget_utils
import abc

class CreateTaskBase(qt.QWidget):
    def __init__(self, parent, name, fl, task_node_name = 'Unamed task-node'):
         qt.QWidget.__init__(self, parent, name, fl)
         
         self._qub_helper = None
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


    def set_tree_brick(self, brick):
        self._tree_brick = brick


    def set_qub_helper(self, qub_helper):
        self._qub_helper = qub_helper


    @abc.abstractmethod
    def set_energies(self):
        pass


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


    @abc.abstractmethod
    def get_prefix_type(self):
        pass

    
    def _selection_changed(self, tree_item):
        pass


    def get_default_prefix(self, sample_data_node):
        prefix = queue_model.QueueModelFactory.\
            get_context().get_default_prefix(self.get_prefix_type(),
                                             sample_data_node)            
        return prefix

        
    def get_default_directory(self, sample_data_node):
        group_item = self.get_group_item()
        sample_item = self.get_sample_item()
        sub_dir = str()

        if group_item:
            sub_dir = group_item.get_model().get_name().lower().replace(' ','')
        else:
            sub_dir = self.get_next_group_name(sample_item).\
                lower().replace(' ','')
            
        data_directory = queue_model.QueueModelFactory.\
                         get_context().get_image_directory(sample_data_node, 
                                                           sub_dir = sub_dir)

        proc_directory = queue_model.QueueModelFactory.\
                         get_context().get_process_directory(sample_data_node, 
                                                             sub_dir = sub_dir)
        

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
        sample_item = self.get_sample_item()
        sample_data_node = sample_item.get_model() if sample_item else None
        group_item = self.get_group_item()
        
        acq_widget = self.get_acquisition_widget()

        if acq_widget:
            acq_widget.set_energies(sample_data_node.energy_scan_result)


        data_path_widget = self.get_data_path_widget()
        if data_path_widget and sample_data_node:
            (data_directory, proc_directory) = self.get_default_directory(sample_data_node)
            data_path_widget.set_directory(data_directory)

            prefix = self.get_default_prefix(sample_data_node)

            run_number = queue_model.QueueModelFactory.\
                get_context().get_free_run_number(prefix, data_directory)

            data_path_widget.set_run_number(run_number)
            data_path_widget.set_prefix(prefix)
            self._path_template.process_directory = proc_directory

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
    def create_parent_task_node(self, sample_item):
        sample = sample_item.get_model()
        task_node = queue_model.QueueModelFactory.create(queue_model.TaskNode)
        task_node.set_name(sample_item.get_next_free_name(self._task_node_name))

        self.create_task(task_node, sample)
                                
        return [task_node]
