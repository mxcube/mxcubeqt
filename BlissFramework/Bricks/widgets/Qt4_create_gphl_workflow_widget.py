from PyQt4 import QtGui
from PyQt4 import QtCore
import Qt4_queue_item as queue_item
import queue_model_objects_v1 as queue_model_objects

from queue_model_enumerables_v1 import States

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_gphl_acquisition_widget import GphlAcquisitionWidget
from widgets.Qt4_gphl_acquisition_widget import GphlDiffractcalWidget
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
        self._gphl_diffractcal_widget =  GphlDiffractcalWidget(
            self._gphl_acq_widget, "gphl_diffractcal_widget"
        )

        self._data_path_widget = DataPathWidget(self, 'create_dc_path_widget',
                                                layout='vertical')
        data_path_layout = self._data_path_widget.data_path_layout
        data_path_layout.file_name_label.hide()
        data_path_layout.file_name_value_label.hide()
        data_path_layout.run_number_label.hide()
        data_path_layout.run_number_ledit.hide()

        # Layout --------------------------------------------------------------
        _workflow_type_vlayout = QtGui.QVBoxLayout(self._workflow_type_widget)
        _workflow_type_vlayout.addWidget(self._workflow_cbox)
        _gphl_acq_vlayout = QtGui.QVBoxLayout(self._gphl_acq_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_acq_param_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_diffractcal_widget)
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._workflow_type_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._gphl_acq_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0,0,0,0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
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

    def workflow_selected(self, name):
        # necessary as this comes in as a QString object
        name = str(name)
        # if reset or name != self._previous_workflow:
        xx = self._workflow_cbox
        xx.setCurrentIndex(xx.findText(name))

        parameters = self._workflow_hwobj.get_available_workflows()[name]
        beam_energies = parameters.get('beam_energies', {})
        strategy_type = parameters.get('strategy_type')
        if strategy_type == 'transcal':
            self._gphl_acq_widget.hide()
        elif strategy_type == 'diffractcal':
            # TODO update this
            self._gphl_diffractcal_widget.populate_widget()
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.show()
            self._gphl_acq_param_widget.hide()
        else:
            # acquisition type strategy
            self._gphl_acq_param_widget.populate_widget(
                beam_energies=beam_energies,
            )
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.hide()
            self._gphl_acq_param_widget.show()

        prefix = parameters.get('prefix')
        if prefix is not None:
            self.current_prefix = prefix

    def data_acquired(self):
        """Data gathered from popup, continue execution"""
        pass

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        wf_model = tree_item.get_model()

        if not isinstance(tree_item, queue_item.SampleQueueItem):

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

    def init_models(self):
        CreateTaskBase.init_models(self)
        self._init_models()

    def _init_models(self):
        pass

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
        wf_type = str(self._workflow_cbox.currentText())
        wf.set_type(wf_type)

        if self.current_prefix:
            path_template.base_prefix = self.current_prefix
        wf.path_template = path_template
        wf.set_name(wf.path_template.get_prefix())
        wf.set_number(wf.path_template.run_number)

        wf_parameters = ho.get_available_workflows()[wf_type]
        strategy_type = wf_parameters.get('strategy_type')
        wf.set_interleave_order(wf_parameters.get('interleaveOrder', ''))
        if strategy_type == 'acquisition':
            expected_resolution = self._gphl_acq_param_widget.get_parameter_value(
                'expected_resolution'
            )

            dd = self._gphl_acq_param_widget.get_energy_dict()
            wf.set_beam_energies(dd)

            wf.set_space_group(
                self._gphl_acq_param_widget.get_parameter_value('space_group')
            )
            tag = self._gphl_acq_param_widget.get_parameter_value('crystal_system')
            crystal_system, point_group = None, None
            if tag:
                data = self._gphl_acq_param_widget._CRYSTAL_SYSTEM_DATA[tag]
                crystal_system = data.crystal_system
                point_groups = data.point_groups
                if len(point_groups) == 1 or point_groups[0] == '32':
                    # '32' is a special case; '312' and '321' are also returned as '32'
                    point_group = point_groups[0]
            wf.set_point_group(point_group)
            wf.set_crystal_system(crystal_system)

        elif strategy_type == 'diffractcal':
            expected_resolution = self._gphl_diffractcal_widget.get_parameter_value(
                'expected_resolution'
            )
            ss = self._gphl_diffractcal_widget.get_parameter_value('test_crystal')
            crystal_data = self._gphl_diffractcal_widget.test_crystals.get(ss)
            wf.set_space_group(crystal_data.space_group)
            wf.set_cell_parameters(
                tuple(getattr(crystal_data, tag)
                      for tag in ('a', 'b', 'c', 'alpha', 'beta', 'gamma'))
            )
        else:
            expected_resolution = None
        wf.set_expected_resolution(expected_resolution)
        
        tasks.append(wf)

        return tasks

    # NB do we need this? Check what happens when prefix is changed
    # # Added in porting to master branch
    # def _prefix_ledit_change(self, new_value):
    #     prefix = self._data_path_widget._data_model.base_prefix
    #     self._data_collection.set_name(prefix)
    #     self._tree_view_item.setText(0, self._data_collection.get_name())
