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
from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

from mxcubeqt.utils import queue_item, qt_import
from mxcubecore.utils import conversion
from mxcubeqt.widgets.create_task_base import CreateTaskBase
from mxcubeqt.widgets.data_path_widget import DataPathWidget
from mxcubeqt.widgets.gphl_acquisition_widget import GphlAcquisitionWidget
from mxcubeqt.widgets.gphl_acquisition_widget import GphlDiffractcalWidget
from mxcubeqt.widgets.gphl_data_dialog import GphlDataDialog

from mxcubecore import HardwareRepository as HWR
from mxcubecore.model import queue_model_objects

__copyright__ = """ Copyright © 2016 - 2019 by Global Phasing Ltd. """
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
        self.current_prefix = None

        self.init_models()

    def _initialize_graphics(self):
        # Graphic elements ----------------------------------------------------
        self._workflow_type_widget = qt_import.QGroupBox("Workflow type", self)

        self._workflow_cbox = qt_import.QComboBox(self._workflow_type_widget)
        self._gphl_acq_widget = qt_import.QGroupBox("Acquisition", self)
        self._gphl_acq_param_widget = GphlAcquisitionWidget(
            self._gphl_acq_widget, "gphl_acquisition_parameter_widget"
        )
        self._gphl_diffractcal_widget = GphlDiffractcalWidget(
            self._gphl_acq_widget, "gphl_diffractcal_widget"
        )

        self._data_path_widget = DataPathWidget(
            self, "create_dc_path_widget", layout="vertical"
        )
        data_path_layout = self._data_path_widget.data_path_layout
        data_path_layout.file_name_label.hide()
        data_path_layout.file_name_value_label.hide()
        data_path_layout.run_number_label.hide()
        data_path_layout.run_number_ledit.hide()
        data_path_layout.folder_ledit.setReadOnly(True)

        # Layout --------------------------------------------------------------
        _workflow_type_vlayout = qt_import.QVBoxLayout(self._workflow_type_widget)
        _workflow_type_vlayout.addWidget(self._workflow_cbox)
        _gphl_acq_vlayout = qt_import.QVBoxLayout(self._gphl_acq_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_acq_param_widget)
        _gphl_acq_vlayout.addWidget(self._gphl_diffractcal_widget)
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self._workflow_type_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._gphl_acq_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._workflow_cbox.currentIndexChanged.connect(self.workflow_selected)

        # set up popup data dialog
        self.gphl_data_dialog = GphlDataDialog(self, "GPhL Workflow Data")
        self.gphl_data_dialog.setModal(True)
        self.gphl_data_dialog.continueClickedSignal.connect(self.data_acquired)

    def initialise_workflows(self):

        workflow_hwobj = HWR.beamline.gphl_workflow
        if workflow_hwobj is not None:
            workflow_hwobj.setup_workflow_object()
            workflow_names = list(workflow_hwobj.get_available_workflows())
            self._initialize_graphics()
            self._workflow_cbox.clear()
            for workflow_name in workflow_names:
                self._workflow_cbox.addItem(workflow_name)
            self.workflow_selected()
            workflow_hwobj.connect(
                "gphlParametersNeeded", self.gphl_data_dialog.open_dialog
            )

    def workflow_selected(self):
        # necessary as this comes in as a QString object
        name = conversion.text_type(self._workflow_cbox.currentText())
        # if reset or name != self._previous_workflow:
        xx0 = self._workflow_cbox
        xx0.setCurrentIndex(xx0.findText(name))
        self.init_models()
        self._data_path_widget.update_data_model(self._path_template)

        parameters = HWR.beamline.gphl_workflow.get_available_workflows()[name]
        strategy_type = parameters.get("strategy_type")
        if strategy_type == "transcal":
            # NB Once we do not have to set unique prefixes, this should be readOnly
            self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(False)
            self._gphl_acq_widget.hide()
        elif strategy_type == "diffractcal":
            # TODO update this
            self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(True)
            self._gphl_diffractcal_widget.populate_widget()
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.show()
            self._gphl_acq_param_widget.hide()
        else:
            # acquisition type strategy
            self._data_path_widget.data_path_layout.prefix_ledit.setReadOnly(True)
            self._gphl_acq_param_widget.populate_widget()
            self._gphl_acq_widget.show()
            self._gphl_diffractcal_widget.hide()
            self._gphl_acq_param_widget.show()

        prefix = parameters.get("prefix")
        if prefix is not None:
            self.current_prefix = prefix

    def data_acquired(self):
        """Data gathered from popup, continue execution"""
        pass

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        wf_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.SampleQueueItem):
            self.init_models()

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
    def _create_task(self, sample, shape):
        tasks = []

        path_template = self._create_path_template(sample, self._path_template)
        path_template.num_files = 0
        path_template.compression = False

        workflow_hwobj = HWR.beamline.gphl_workflow
        if workflow_hwobj.get_state() == workflow_hwobj.STATES.OFF:
            # We will be setting up the connection now - time to connect to quit
            qt_import.QApplication.instance().aboutToQuit.connect(
                workflow_hwobj.shutdown
            )

            tree_brick = self._tree_brick
            if tree_brick:
                tree_brick.dc_tree_widget.confirm_dialog.continueClickedSignal.connect(
                    self.continue_button_click
                )

        wf = queue_model_objects.GphlWorkflow(workflow_hwobj)
        wf_type = conversion.text_type(self._workflow_cbox.currentText())
        wf.set_type(wf_type)

        if self.current_prefix:
            path_template.base_prefix = self.current_prefix
        wf.path_template = path_template
        wf.set_name(wf.path_template.get_prefix())
        wf.set_number(wf.path_template.run_number)

        wf_parameters = workflow_hwobj.get_available_workflows()[wf_type]
        strategy_type = wf_parameters.get("strategy_type")
        wf.set_interleave_order(wf_parameters.get("interleaveOrder", ""))
        if strategy_type.startswith("transcal"):
            pass

        elif strategy_type.startswith("diffractcal"):
            ss0 = self._gphl_diffractcal_widget.get_parameter_value("test_crystal")
            crystal_data = self._gphl_diffractcal_widget.test_crystals.get(ss0)
            wf.set_space_group(crystal_data.space_group)
            wf.set_cell_parameters(
                tuple(
                    getattr(crystal_data, tag)
                    for tag in ("a", "b", "c", "alpha", "beta", "gamma")
                )
            )
            tag = self._gphl_acq_param_widget.get_parameter_value("dose_budget")
            wf.set_dose_budget(HWR.beamline.gphl_workflow.dose_budgets.get(tag))
            # The entire strategy runs as a 'characterisation'
            wf.set_characterisation_budget_fraction(1.0)
        else:
            # Coulds be native_... phasing_... etc.

            wf.set_space_group(
                self._gphl_acq_param_widget.get_parameter_value("space_group")
            )
            wf.set_characterisation_strategy(
                self._gphl_acq_param_widget.get_parameter_value(
                    "characterisation_strategy"
                )
            )
            tag = self._gphl_acq_param_widget.get_parameter_value("crystal_system")
            crystal_system, point_group = None, None
            if tag:
                data = self._gphl_acq_param_widget._CRYSTAL_SYSTEM_DATA[tag]
                crystal_system = data.crystal_system
                point_groups = data.point_groups
                if len(point_groups) == 1 or point_groups[0] == "32":
                    # '32' is a special case; '312' and '321' are also returned as '32'
                    point_group = point_groups[0]
            wf.set_point_group(point_group)
            wf.set_crystal_system(crystal_system)
            wf.set_beam_energies(wf_parameters["beam_energies"])
            tag = self._gphl_acq_param_widget.get_parameter_value("dose_budget")
            wf.set_dose_budget(HWR.beamline.gphl_workflow.dose_budgets.get(tag))
            val = self._gphl_acq_param_widget.get_parameter_value(
                "relative_rad_sensitivity"
            )
            wf.set_relative_rad_sensitivity(val)
            wf.set_characterisation_budget_fraction(
                HWR.beamline.gphl_workflow.get_property(
                    "characterisation_budget_percent", 5.0
                )
                / 100.0
            )

        tasks.append(wf)

        return tasks

    # NB do we need this? Check what happens when prefix is changed
    # # Added in porting to master branch
    # def _prefix_ledit_change(self, new_value):
    #     prefix = self._data_path_widget._data_model.base_prefix
    #     self._data_collection.set_name(prefix)
    #     self._tree_view_item.setText(0, self._data_collection.get_name())
