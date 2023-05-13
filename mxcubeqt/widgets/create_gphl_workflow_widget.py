#! /usr/bin/env python
# encoding: utf-8
#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from mxcubecore.utils import conversion
from mxcubecore import HardwareRepository as HWR
from mxcubecore.model import queue_model_objects

from mxcubeqt.utils import queue_item, qt_import
from mxcubeqt.widgets.create_task_base import CreateTaskBase
from mxcubeqt.widgets.data_path_widget import DataPathWidget
from mxcubeqt.widgets.gphl_json_dialog import GphlJsonDialog

__copyright__ = """ Copyright © 2016 - 2022 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


class CreateGphlWorkflowWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):

        CreateTaskBase.__init__(
            self, parent, name, qt_import.Qt.WindowFlags(fl), "GphlWorkflow"
        )

        if not name:
            self.setObjectName("create_gphl_workflow_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._workflow_type_widget = None
        self._workflow_cbox = None
        self.gphl_data_dialog = None

        self.init_models()

    def _initialize_graphics(self):
        # Graphic elements ----------------------------------------------------
        self._workflow_type_widget = qt_import.QGroupBox("Workflow type", self)

        # NB widget must start out hidden,
        # so as to be shown when workflow type is initialiesd
        self._workflow_cbox = qt_import.QComboBox(self._workflow_type_widget)
        # self._gphl_acq_widget = qt_import.QGroupBox("Acquisition", self)
        # self._gphl_acq_param_widget = GphlAcquisitionWidget(
        #     self._gphl_acq_widget, "gphl_acquisition_parameter_widget"
        # )
        # self._gphl_acq_param_widget.hide()
        # self._gphl_diffractcal_widget = GphlDiffractcalWidget(
        #     self._gphl_acq_widget, "gphl_diffractcal_widget"
        # )
        # self._gphl_diffractcal_widget.hide()
        #
        # self._gphl_runtime_widget = GphlRuntimeWidget(
        #     self._gphl_acq_widget, "gphl_runtime_widge"
        # )

        self._data_path_widget = DataPathWidget(
            self,
            "create_dc_path_widget",
            data_model=self._path_template,
            layout="vertical",
        )
        self._data_path_widget._base_image_dir = (
            HWR.beamline.session.get_base_image_directory()
        )
        self._data_path_widget._base_process_dir = (
            HWR.beamline.session.get_base_process_directory()
        )
        data_path_layout = self._data_path_widget.data_path_layout
        data_path_layout.run_number_ledit.setReadOnly(True)
        data_path_layout.run_number_ledit.setEnabled(False)
        # data_path_layout.folder_ledit.setReadOnly(True)

        # Layout --------------------------------------------------------------
        _workflow_type_vlayout = qt_import.QVBoxLayout(self._workflow_type_widget)
        _workflow_type_vlayout.addWidget(self._workflow_cbox)
        # _gphl_acq_vlayout = qt_import.QVBoxLayout(self._gphl_acq_widget)
        # _gphl_acq_vlayout.addWidget(self._gphl_acq_param_widget)
        # _gphl_acq_vlayout.addWidget(self._gphl_diffractcal_widget)
        # _gphl_acq_vlayout.addWidget(self._gphl_runtime_widget)
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self._workflow_type_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        # _main_vlayout.addWidget(self._gphl_acq_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._workflow_cbox.currentIndexChanged.connect(self.workflow_selected)
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )

        # set up popup data dialog
        self.gphl_data_dialog = GphlJsonDialog(self, "GΦL Workflow Data")
        self.gphl_data_dialog.setModal(True)

    def initialise_workflows(self):

        workflow_hwobj = HWR.beamline.gphl_workflow
        if workflow_hwobj is not None:
            # workflow_hwobj.setup_workflow_object()
            workflow_names = list(workflow_hwobj.workflow_strategies)
            self._initialize_graphics()
            self._workflow_cbox.clear()
            for workflow_name in workflow_names:
                self._workflow_cbox.addItem(workflow_name)
            self.workflow_selected()
            workflow_hwobj.connect(
                "gphlJsonParametersNeeded", self.gphl_data_dialog.open_dialog
            )
            workflow_hwobj.connect("gphlStartAcquisition", self.gphl_start_acquisition)
            workflow_hwobj.connect("gphlDoneAcquisition", self.gphl_done_acquisition)

    def init_data_path_model(self):
        # Initialize the path_template of the widget to default
        # values read from the beamline setup
        if self._data_path_widget:
            self._data_path_widget._base_image_dir = (
                HWR.beamline.session.get_base_image_directory()
            )
            self._data_path_widget._base_process_dir = (
                HWR.beamline.session.get_base_process_directory()
            )

        (data_directory, proc_directory) = self.get_default_directory()
        self._path_template = HWR.beamline.get_default_path_template()
        self._path_template.directory = data_directory
        self._path_template.process_directory = proc_directory
        self._path_template.base_prefix = self.get_default_prefix()
        self._path_template.run_number = HWR.beamline.queue_model.get_next_run_number(
            self._path_template
        )

    def gphl_start_acquisition(self, workflow_model):
        """Change tab to runtime display"""
        pass

    def gphl_done_acquisition(self, workflow_model):
        """Change tab back to acquisition display"""
        self.workflow_selected()
        # Necessary to clean up folder settings
        self.init_data_path_model()

    def workflow_selected(self):
        # necessary as this comes in as a QString object
        name = conversion.text_type(self._workflow_cbox.currentText())
        # if reset or name != self._previous_workflow:
        xx0 = self._workflow_cbox
        xx0.setCurrentIndex(xx0.findText(name))

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        model = tree_item.get_model()

        if isinstance(tree_item, queue_item.DataCollectionQueueItem):
            self._path_template = tree_item.get_model().acquisitions[0].path_template
            self._data_path_widget.update_data_model(self._path_template)

        elif self._tree_brick.dc_tree_widget.collecting:
            # We do not want reset after collection has started
            return

        elif isinstance(tree_item, queue_item.GphlWorkflowQueueItem):
            if model.is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            if model.get_path_template():
                self._path_template = model.get_path_template()
            self._data_path_widget.update_data_model(self._path_template)

        elif isinstance(tree_item, queue_item.SampleQueueItem):
            if not model.has_lims_data() and not HWR.beamline.session.get_group_name():
                # When no prefix is set, override prefix setting;
                # globally we cannot set location as name, apparently, but here we can
                self._path_template.base_prefix = (
                    model.get_name() or HWR.beamline.session.get_proposal()
                )
                self._data_path_widget.update_data_model(self._path_template)

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
                    ss0 = dialog.conf_dialog_layout.take_snapshots_combo.currentText()
                    model.set_snapshot_count(int(ss0) if ss0 else 0)

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape, comments=None):

        tasks = []

        path_template = self._create_path_template(sample, self._path_template)
        path_template.num_files = 0

        workflow_hwobj = HWR.beamline.gphl_workflow
        if workflow_hwobj.get_state() == workflow_hwobj.STATES.OFF:
            # We will be setting up the connection now - time to connect to quit
            qt_import.QApplication.instance().aboutToQuit.connect(
                workflow_hwobj.shutdown
            )

        wfl = queue_model_objects.GphlWorkflow()
        wfl.path_template = path_template
        strategy_name = conversion.text_type(self._workflow_cbox.currentText())
        wfl.init_from_task_data(
            sample,
            {"strategy_name": strategy_name, "prefix": path_template.get_prefix()},
        )
        wfl.set_number(path_template.run_number)

        tasks.append(wfl)

        return tasks
