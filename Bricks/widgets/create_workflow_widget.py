import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys
import os
import MxLookupScanBrick


from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout


class CreateWorkflowWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Workflow')

        # Data attributes
        self.workflow_hwobj = None
        
        self.init_models()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 5, "main_v_layout")

        self._workflow_type_gbox = qt.QVGroupBox('Workflow type', self,
                                                 'workflow_rtype')

        self._workflow_cbox = qt.QComboBox(self._workflow_type_gbox)

        self._data_path_gbox = qt.QVGroupBox('Data location', self,
                                             'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                                data_model = self._path_template,
                                                layout = DataPathWidgetVerticalLayout)

        self._data_path_widget.data_path_widget_layout.file_name_label.setText('')
        self._data_path_widget.data_path_widget_layout.file_name_value_label.hide()


        self._grid_widget = MxLookupScanBrick.\
                            MxLookupScanBrick(self, 'grid_widget')


        self._grid_widget.command = '/eh1/scans'
        self._grid_widget.horizontal = '/eh1/horizontal_motors'
        self._grid_widget.vertical = '/eh1/vertical_motors'
        self._grid_widget.offsetmeasure = 1000

        self._grid_widget.propertyChanged('command', '' , '/eh1/scans')
        self._grid_widget.propertyChanged('horizontal', '', '/eh1/horizontal_motors')
        self._grid_widget.propertyChanged('vertical', '', '/eh1/vertical_motors')
        self._grid_widget.propertyChanged('offsetmeasure', 0, 1000)

        v_layout.addWidget(self._workflow_type_gbox)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addWidget(self._grid_widget)
        v_layout.addStretch()

        self.connect(self._data_path_widget.data_path_widget_layout.prefix_ledit, 
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)


        self.connect(self._data_path_widget.data_path_widget_layout.run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)
        

        #self.connect(self._workflow_cbox, qt.SIGNAL('activated ( const QString &)'),
        #             self.workflow_selected)


    def set_workflow(self, workflow_hwobj):
        self._workflow_hwobj = workflow_hwobj

        if self._workflow_hwobj is not None:
            for workflow in self._workflow_hwobj.get_available_workflows():
                self._workflow_cbox.insertItem(workflow['name'])


    def _prefix_ledit_change(self, new_value):
        item = self._current_selected_item
        
        if isinstance(item, queue_item.GenericWorkflowQueueItem):
            prefix = self._path_template.get_prefix()
            item.get_model().set_name(prefix)
            item.setText(0, item.get_model().get_name())
        

    def _run_number_ledit_change(self, new_value):
        item = self._current_selected_item
        
        if isinstance(item, queue_item.GenericWorkflowQueueItem):
            if str(new_value).isdigit():
                item.get_model().set_number(int(new_value))
                item.setText(0, item.get_model().get_name())


    def init_models(self):
        self._path_template = queue_model_objects.PathTemplate()


    def _selection_changed(self, tree_item):
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):

            self.init_models()
            sample_data_model = self.get_sample_item().get_model()

            if isinstance(tree_item, queue_item.SampleQueueItem):
                (data_directory, proc_directory) = self.get_default_directory(sample_data_model)
                sub_dir =  'workflow-%i' % tree_item.get_model().\
                          get_next_number_for_name('Workflow')       
                proc_directory = os.path.join(proc_directory, sub_dir)
                data_directory = os.path.join(data_directory, sub_dir)     
            else:
                (data_directory, proc_directory) = self.get_default_directory(sample_data_model)
                
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(sample_data_model)

            self._path_template.run_number = self._current_selected_item.\
                get_model().get_next_number_for_name(self._path_template.get_prefix())

        elif isinstance(tree_item, queue_item.GenericWorkflowQueueItem):
            workflow_model = tree_item.get_model()
            self._path_template = workflow_model.path_template

        self._data_path_widget.update_data_model(self._path_template)


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, dcg, sample):
        tasks = []

        path_template = copy.deepcopy(self._path_template)
        wf = queue_model_objects.Workflow()
        wf.path_template = path_template
        wf.set_name(path_template.get_prefix())
        wf.set_type(self._workflow_cbox.currentText())
        
        tasks.append(wf)

        return tasks
