import qt
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import MxLookupScanBrick
import itertools

from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout


class CreateWorkflowWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Workflow')

        # Data attributes
        self.workflow_hwobj = None
        self.workflows = {}
        
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

        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)
        
        #self.connect(self._workflow_cbox, qt.SIGNAL('activated ( const QString &)'),
        #             self.workflow_selected)


    def set_workflow(self, workflow_hwobj):
        self._workflow_hwobj = workflow_hwobj
        self.workflows.clear()
        self._workflow_cbox.clear()

        if self._workflow_hwobj is not None:
            for workflow in self._workflow_hwobj.get_available_workflows():
                self._workflow_cbox.insertItem(workflow['name'])
                self.workflows[workflow['name']] = workflow


    def set_shape_history(self, shape_history_hwobj):
        self._grid_widget._shape_history = shape_history_hwobj

        motor =  self._beamline_setup_hwobj.\
                getObjectByRole('horizontal_motors')
        self._grid_widget.initialize_motors('horizontal', motor)

        motor = self._beamline_setup_hwobj.\
                getObjectByRole('vertical_motors')
        self._grid_widget.initialize_motors('vertical', motor)


    def init_models(self):
        CreateTaskBase.init_models(self)


    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.GenericWorkflowQueueItem):
            self.setDisabled(False)
        elif not(isinstance(tree_item, queue_item.SampleQueueItem) or \
                     isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)):
            self.setDisabled(True)


    def approve_creation(self):
        return CreateTaskBase.approve_creation(self)


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample):
        tasks = []

        path_template = copy.deepcopy(self._path_template)
        path_template.num_files = 0

        wf = queue_model_objects.Workflow()
        wf_name = str(self._workflow_cbox.currentText())
        wf.path_template = path_template
        wf.set_name(path_template.get_prefix())
        wf.set_type(wf_name)
        
        beamline_params = {}
        beamline_params['directory'] = wf.path_template.directory
        beamline_params['prefix'] = wf.path_template.get_prefix()
        beamline_params['run_number'] = wf.path_template.run_number
        beamline_params['collection_software'] = 'mxCuBE - 2.0'
        beamline_params['sample_node_id'] = sample._node_id

        params_list = map(str, list(itertools.chain(*beamline_params.iteritems())))
        params_list.insert(0, self.workflows[wf_name]['path'])
        params_list.insert(0, 'modelpath')
        
        wf.params_list = params_list
        
        tasks.append(wf)

        return tasks
