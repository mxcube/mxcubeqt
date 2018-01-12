from PyQt4 import QtGui
from PyQt4 import QtCore
import Qt4_queue_item as queue_item
import queue_model_objects_v1 as queue_model_objects

from General import States

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_processing_widget import ProcessingWidget
from widgets.Qt4_gphl_acquisition_widget import GphlAcquisitionWidget
from widgets.Qt4_gphl_data_dialog import GphlDataDialog

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class CreateGphlWorkflowWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):
        CreateTaskBase.__init__(self, parent, name,
                                QtCore.Qt.WindowFlags(fl), 'GphlWorkflow')

        if not name:
            self.setObjectName("Qt4_create_gphl_workflow_widget")

        # Hardware objects ----------------------------------------------------
        self._workflow_hwobj = None

        # Internal variables --------------------------------------------------
        self.current_prefix = None

        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._workflow_type_widget = QtGui.QGroupBox('Workflow type', self)

        self._workflow_cbox = QtGui.QComboBox(self._workflow_type_widget)
        self._gphl_acq_widget = QtGui.QGroupBox('Acquisition', self)
        self._gphl_acq_param_widget =  GphlAcquisitionWidget(
            self._gphl_acq_widget, "gphl_acquisition_parameter_widget"
        )

        self._data_path_widget = DataPathWidget(self, 'create_dc_path_widget',
                                                layout='vertical')
        data_path_layout = self._data_path_widget.data_path_layout
        data_path_layout.file_name_label.hide()
        data_path_layout.file_name_value_label.hide()
        data_path_layout.run_number_label.hide()
        data_path_layout.run_number_ledit.hide()

        self._processing_widget = ProcessingWidget(self)
        processing_layout = self._processing_widget.processing_widget
        processing_layout.num_residues_label.hide()
        processing_layout.num_residues_ledit.hide()
        processing_layout.run_processing_cbox.hide()

        # Layout --------------------------------------------------------------
        _workflow_type_vlayout = QtGui.QVBoxLayout(self._workflow_type_widget)
        _workflow_type_vlayout.addWidget(self._workflow_cbox)
        _gphl_acq_vlayout = QtGui.QVBoxLayout(self._gphl_acq_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_acq_param_widget)
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._workflow_type_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._gphl_acq_widget)
        _main_vlayout.addWidget(self._processing_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0,0,0,0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.connect(
                     self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.connect(
                     self._run_number_ledit_change)
        self._workflow_cbox.currentIndexChanged[str].connect(
            self.workflow_selected
        )


        # set up popup data dialog
        self.gphl_data_dialog = GphlDataDialog(self, 'GPhL Workflow Data')
        self.gphl_data_dialog.setModal(True)
        self.gphl_data_dialog.continueClickedSignal.connect(self.data_acquired)
        # self.connect(self.gphl_data_dialog, qt.PYSIGNAL("continue_clicked"),
        #              self.data_acquired)

    def initialise_workflows(self, workflow_hwobj):
        self._workflow_hwobj = workflow_hwobj
        self._workflow_cbox.clear()
        # self._gphl_parameters_widget.set_workflow(workflow_hwobj)

        if self._workflow_hwobj is not None:
            workflow_names = list(workflow_hwobj.get_available_workflows())
            for workflow_name in workflow_names:
                self._workflow_cbox.addItem(workflow_name)
            self.workflow_selected(workflow_names[0])

            workflow_hwobj.connect('gphlParametersNeeded',
                                   self.gphl_data_dialog.open_dialog)

        # # Set hardwired and default values
        # self._gphl_acquisition_widget.set_param_value('char_energy',
        #     workflow_hwobj.getProperty('characterisation_energy')
        # )
        # # Placeholder. Must be set to match hardwired detector distance
        # self._gphl_acquisition_widget.set_param_value('detector_resolution', -1)

    def workflow_selected(self, name):
        # necessary as this comes in as a QString object
        name = str(name)
        # if reset or name != self._previous_workflow:
        xx = self._workflow_cbox
        xx.setCurrentIndex(xx.findText(name))
        # self._previous_workflow = name

        parameters = self._workflow_hwobj.get_available_workflows()[name]
        beam_energies = parameters.get('beam_energies', {})
        strategy_type = parameters.get('strategy_type')
        if strategy_type == 'transcal':
            self._processing_widget.hide()
            self._gphl_acq_widget.hide()
        else:
            # diffractcal or acquisition type strategy
            self._processing_widget.show()
            self._gphl_acq_param_widget.populate_widget(
                beam_energies=beam_energies
            )
            self._gphl_acq_widget.show()

        prefix = parameters.get('prefix')
        if prefix is not None:
            self.current_prefix = prefix

    def data_acquired(self):
        """Data gathered from popup, continue execution"""
        pass

    # def set_beam_energies(self, beam_energy_dict):
    #     parameter_dict = self._gphl_acquisition_widget.get_parameter_dict()
    #     for tag, energy in beam_energy_dict.items():
    #         if tag in parameter_dict:
    #             self._gphl_acquisition_widget.set_param_value(tag, energy)
    #         else:
    #             raise ValueError("GPhL: No active beam energy named %s"
    #                              % tag)

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        wf_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            self._processing_parameters = sample_model.processing_parameters
        else:

            if isinstance(tree_item, queue_item.GphlWorkflowQueueItem):
                if tree_item.get_model().is_executed():
                    self.setDisabled(True)
                else:
                    self.setDisabled(False)

                if wf_model.get_path_template():
                    self._path_template = wf_model.get_path_template()

                self._data_path_widget.update_data_model(self._path_template)

            elif isinstance(tree_item, queue_item.BasketQueueItem):
                self.setDisabled(False)
            elif not isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
                self.setDisabled(True)

        self._processing_widget.update_data_model(self._processing_parameters)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._init_models()

    def _init_models(self):
        self._processing_parameters = queue_model_objects.ProcessingParameters()
        self._processing_parameters.num_residues = 0
        self._processing_parameters.process_data = False
        # self.workflow_selected(self._workflow_cbox.currentText())

    def continue_button_click(self, sample_items, checked_items):
        """Intercepts the datacollection continue_button click for parameter setting"""
        tree_brick = self._tree_brick
        if tree_brick:
            for item in checked_items:
                model = item.get_model()
                if isinstance(model, queue_model_objects.GphlWorkflow):
                    dialog = tree_brick.dc_tree_widget.confirm_dialog
                    ss = dialog.conf_dialog_layout.take_snapshots_combo.currentText()
                    model.set_snapshot_count(int(ss) if ss else 0)

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        tasks = []

        path_template = self._create_path_template(sample, self._path_template)
        path_template.num_files = 0

        ho = self._workflow_hwobj
        if ho.get_state() == States.OFF:
            # We will be setting up the connection now - time to connect to quit
            QtGui.QApplication.instance().aboutToQuit.connect(ho.shutdown)

            tree_brick = self._tree_brick
            if tree_brick:
                tree_brick.dc_tree_widget.confirm_dialog.continueClickedSignal\
                    .connect(self.continue_button_click)


        wf = queue_model_objects.GphlWorkflow(self._workflow_hwobj)
        wf.set_type(str(self._workflow_cbox.currentText()))

        if self.current_prefix:
            path_template.base_prefix = self.current_prefix
        wf.path_template = path_template
        wf.processing_parameters = self._processing_parameters
        wf.set_name(wf.path_template.get_prefix())
        wf.set_number(wf.path_template.run_number)

        data_object = self._gphl_acq_param_widget.get_data_object()

        wf.set_expected_resolution(data_object.expected_resolution)

        dd = self._gphl_acq_param_widget.get_energy_dict()
        wf.set_beam_energies(dd)
        
        tasks.append(wf)

        return tasks
