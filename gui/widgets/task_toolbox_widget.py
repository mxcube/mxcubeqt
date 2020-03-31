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

import logging
import importlib

from gui.utils import Icons, queue_item, QtImport
from gui.widgets.create_discrete_widget import CreateDiscreteWidget
from gui.widgets.create_helical_widget import CreateHelicalWidget
from gui.widgets.create_char_widget import CreateCharWidget
from gui.widgets.create_energy_scan_widget import CreateEnergyScanWidget
from gui.widgets.create_xrf_spectrum_widget import CreateXRFSpectrumWidget
from gui.widgets.create_gphl_workflow_widget import CreateGphlWorkflowWidget
from gui.widgets.create_advanced_widget import CreateAdvancedWidget
from gui.widgets.create_xray_imaging_widget import CreateXrayImagingWidget
from gui.widgets.create_still_scan_widget import CreateStillScanWidget

from HardwareRepository.HardwareObjects import queue_model_objects

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class TaskToolBoxWidget(QtImport.QWidget):
    def __init__(self, parent=None, name="task_toolbox"):

        QtImport.QWidget.__init__(self, parent)
        self.setObjectName = name

        # Internal variables --------------------------------------------------
        self.tree_brick = None
        self.previous_page_index = 0
        self.is_running = None
        self.path_conflict = False
        self.acq_conflict = False
        self.enable_collect = False
        self.create_task_widgets = {}

        # Graphic elements ----------------------------------------------------
        self.method_label = QtImport.QLabel("Collection method", self)
        self.method_label.setAlignment(QtImport.Qt.AlignCenter)

        self.tool_box = QtImport.QToolBox(self)
        self.tool_box.setObjectName("tool_box")
        # self.tool_box.setFixedWidth(600)

        self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete")
        self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page")
        self.energy_scan_page = CreateEnergyScanWidget(self.tool_box, "energy_scan")
        self.xrf_spectrum_page = CreateXRFSpectrumWidget(self.tool_box, "xrf_spectrum")
        if HWR.beamline.gphl_workflow is not None:
            self.gphl_workflow_page = CreateGphlWorkflowWidget(
                self.tool_box, "gphl_workflow"
            )
        else:
            self.gphl_workflow_page = None
        self.advanced_page = CreateAdvancedWidget(self.tool_box, "advanced_scan")
        self.xray_imaging_page = CreateXrayImagingWidget(self.tool_box, "xray_imaging")
        self.still_scan_page = CreateStillScanWidget(self.tool_box, "still_scan")

        self.tool_box.addItem(self.discrete_page, "Standard Collection")
        self.tool_box.addItem(self.char_page, "Characterisation")
        self.tool_box.addItem(self.helical_page, "Helical Collection")
        self.tool_box.addItem(self.energy_scan_page, "Energy Scan")
        self.tool_box.addItem(self.xrf_spectrum_page, "XRF Spectrum")
        if self.gphl_workflow_page is not None:
            self.tool_box.addItem(self.gphl_workflow_page, "GPhL Workflows")
        self.tool_box.addItem(self.advanced_page, "Advanced")
        self.tool_box.addItem(self.xray_imaging_page, "Xray Imaging")
        self.tool_box.addItem(self.still_scan_page, "Still")

        self.button_box = QtImport.QWidget(self)
        self.create_task_button = QtImport.QPushButton(
            "  Add to queue", self.button_box
        )
        self.create_task_button.setIcon(Icons.load_icon("add_row.png"))
        msg = "Add the collection method to the selected sample"
        self.create_task_button.setToolTip(msg)
        self.create_task_button.setEnabled(False)

        self.collect_now_button = QtImport.QPushButton("Collect Now", self.button_box)
        self.collect_now_button.setIcon(Icons.load_icon("VCRPlay2.png"))
        self.collect_now_button.setToolTip(
            "Add the collection method to the queue and execute it"
        )

        # Layout --------------------------------------------------------------
        _button_box_hlayout = QtImport.QHBoxLayout(self.button_box)
        _button_box_hlayout.addWidget(self.collect_now_button)
        _button_box_hlayout.addStretch(0)
        _button_box_hlayout.addWidget(self.create_task_button)
        _button_box_hlayout.setSpacing(0)
        _button_box_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.method_label)
        _main_vlayout.addWidget(self.tool_box)
        _main_vlayout.addWidget(self.button_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        # self.setSizePolicy(QSizePolicy.Expanding,
        #                   QSizePolicy.Expanding)

        # Qt signal/slot connections ------------------------------------------
        self.create_task_button.clicked.connect(self.create_task_button_click)
        self.collect_now_button.clicked.connect(self.collect_now_button_click)
        self.tool_box.currentChanged.connect(self.current_page_changed)

        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).acqParametersConflictSignal.connect(
                self.acq_parameters_conflict_changed
            )
            self.tool_box.widget(i).pathTempleConflictSignal.connect(
                self.path_template_conflict_changed
            )

        # Other ---------------------------------------------------------------
        in_plate_mode = HWR.beamline.diffractometer.in_plate_mode()

        if (
            HWR.beamline.energy_scan is None
            or in_plate_mode
            or not HWR.beamline.tunable_wavelength
        ):
            self.hide_task(self.energy_scan_page)
            logging.getLogger("HWR").info("Energy scan task not available")

        if HWR.beamline.xrf_spectrum is None or in_plate_mode:
            self.hide_task(self.xrf_spectrum_page)
            logging.getLogger("HWR").info("XRF spectrum task not available")

        if not HWR.beamline.imaging or in_plate_mode:
            self.hide_task(self.xray_imaging_page)
            logging.getLogger("HWR").info("Xray Imaging task not available")

        if HWR.beamline.gphl_connection and HWR.beamline.gphl_workflow:
            self.gphl_workflow_page.initialise_workflows()
        else:
            logging.getLogger("HWR").info("GPhL workflow task not available")

    def set_available_tasks(self, available_tasks):
        for task_name in available_tasks.split():
            module_name = "gui.widgets.create_%s_widget" % task_name
            class_name = "Create%sWidget" % task_name.title().replace(" ", "")
            create_task_widget_cls = getattr(
                importlib.import_module(module_name), class_name
            )
            create_task_widget = create_task_widget_cls(self.tool_box, task_name)
            self.tool_box.addItem(create_task_widget, task_name.title())
            self.create_task_widgets[task_name] = create_task_widget

    def adjust_width(self, width):
        # Adjust periodic table width
        if width > -1:
            self.energy_scan_page._periodic_table_widget.setFixedWidth(width - 4)
            self.energy_scan_page._periodic_table_widget.setFixedHeight(width / 1.5)

    def set_expert_mode(self, state):
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).set_expert_mode(state)

    def enable_compression(self, state):
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).enable_compression(state)

    def set_tree_brick(self, brick):
        """Sets the tree brick of each page in the toolbox.
        """
        self.tree_brick = brick
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).set_tree_brick(brick)
        self.tree_brick.dc_tree_widget.enableCollectSignal.connect(
            self.enable_collect_changed
        )
        self.selection_changed(self.tree_brick.get_selected_items())

    def use_osc_start_cbox(self, status):
        for i in range(0, self.tool_box.count()):
            acq_widget = self.tool_box.widget(i).get_acquisition_widget()
            if acq_widget:
                acq_widget.use_osc_start(status)

    def hide_task(self, task_page):
        self.tool_box.removeItem(self.tool_box.indexOf(task_page))
        task_page.hide()

    def update_data_path_model(self):
        for i in range(0, self.tool_box.count()):
            item = self.tool_box.widget(i)
            item.init_data_path_model()
            item.update_selection()

    def ispyb_logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles LIMS (ISPyB)
        login, ie ProposalBrick. The signal is emitted when a user was
        succesfully logged in.
        """
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).ispyb_logged_in(logged_in)

    def current_page_changed(self, page_index):
        if not self.tree_brick:
            return

        tree_items = self.tree_brick.get_selected_items()
        # self.collect_now_button.setHidden(page_index > 0)
        self.create_task_button.setEnabled(False)

        if len(tree_items) > 0:
            tree_item = tree_items[0]

            # Get the directory form the previous page and update
            # the new page with the direcotry and run_number from the old.
            # IF sample, basket group selected.
            if type(tree_item) in (
                queue_item.DataCollectionGroupQueueItem,
                queue_item.SampleQueueItem,
                queue_item.BasketQueueItem,
            ):
                new_pt = self.tool_box.widget(page_index)._path_template
                previous_pt = self.tool_box.widget(
                    self.previous_page_index
                )._path_template

                new_pt.directory = previous_pt.directory
                new_pt.base_prefix = previous_pt.base_prefix
                new_pt.run_number = HWR.beamline.queue_model.get_next_run_number(
                    new_pt
                )
                self.create_task_button.setEnabled(True)

            elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
                # self.collect_now_button.show()
                data_collection = tree_item.get_model()
                if data_collection.is_helical():
                    if self.tool_box.currentWidget() == self.helical_page:
                        self.create_task_button.setEnabled(True)
                elif data_collection.is_mesh():
                    if self.tool_box.currentWidget() == self.advanced_page:
                        self.create_task_button.setEnabled(True)
                elif data_collection.is_still():
                    if self.tool_box.currentWidget() == self.still_scan_page:
                        self.create_task_button.setEnabled(True)
                elif self.tool_box.currentWidget() == self.discrete_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.CharacterisationQueueItem):
                if self.tool_box.currentWidget() == self.char_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.EnergyScanQueueItem):
                if self.tool_box.currentWidget() == self.energy_scan_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.XRFSpectrumQueueItem):
                if self.tool_box.currentWidget() == self.xrf_spectrum_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.GphlWorkflowQueueItem):
                if self.tool_box.currentWidget() == self.gphl_workflow_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.GenericWorkflowQueueItem):
                if self.tool_box.currentWidget() == self.workflow_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.XrayCenteringQueueItem):
                if self.tool_box.currentWidget() == self.advanced_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, queue_item.XrayImagingQueueItem):
                if self.tool_box.currentWidget() == self.xray_imaging_page:
                    self.create_task_button.setEnabled(True)

            self.tool_box.widget(page_index).selection_changed(tree_items)
            self.previous_page_index = page_index

    def selection_changed(self, items):
        """
        Called by the parent widget when selection in the tree changes.
        """
        title = "<b>Collection method template</b>"

        if len(items) == 1:
            self.create_task_button.setEnabled(False)
            data_model = items[0].get_model()
            title = "<b>%s</b>" % data_model.get_display_name()

            if not isinstance(items[0], queue_item.DataCollectionGroupQueueItem):
                self.create_task_button.setEnabled(True)
            if isinstance(items[0], queue_item.DataCollectionQueueItem):
                if data_model.is_helical():
                    self.tool_box.setCurrentWidget(self.helical_page)
                elif data_model.is_mesh():
                    self.tool_box.setCurrentWidget(self.advanced_page)
                elif data_model.is_still():
                    self.tool_box.setCurrentWidget(self.still_scan_page)
                else:
                    self.tool_box.setCurrentWidget(self.discrete_page)
            elif isinstance(items[0], queue_item.CharacterisationQueueItem):
                self.tool_box.setCurrentWidget(self.char_page)
            elif isinstance(items[0], queue_item.EnergyScanQueueItem):
                self.tool_box.setCurrentWidget(self.energy_scan_page)
            elif isinstance(items[0], queue_item.XRFSpectrumQueueItem):
                self.tool_box.setCurrentWidget(self.xrf_spectrum_page)
            elif isinstance(items[0], queue_item.GphlWorkflowQueueItem):
                self.tool_box.setCurrentWidget(self.gphl_workflow_page)
            elif isinstance(items[0], queue_item.GenericWorkflowQueueItem):
                self.tool_box.setCurrentWidget(self.workflow_page)
            elif isinstance(items[0], queue_item.XrayCenteringQueueItem):
                self.tool_box.setCurrentWidget(self.advanced_page)
            elif isinstance(items[0], queue_item.XrayImagingQueueItem):
                self.tool_box.setCurrentWidget(self.xray_imaging_page)

            elif isinstance(items[0], queue_item.SampleQueueItem):
                title = "<b>Sample: %s</b>" % data_model.get_display_name()
            self.method_label.setText(title)
        else:
            self.create_task_button.setEnabled(True)

        current_page = self.tool_box.currentWidget()
        current_page.selection_changed(items)

    def create_task_button_click(self):
        if self.tool_box.currentWidget().approve_creation():
            items = self.tree_brick.get_selected_items()

            if not items:
                logging.getLogger("GUI").warning(
                    "Select the sample, basket or task group you would like to add to."
                )
            else:
                for item in items:
                    shapes = HWR.beamline.sample_view.get_selected_points()
                    task_model = item.get_model()

                    # TODO Consider if GPhL workflow needs task-per-shape
                    # like xrf does

                    # Create a new group if sample is selected
                    if isinstance(task_model, queue_model_objects.Sample):
                        task_model = self.create_task_group(task_model)
                        if self.tool_box.currentWidget() in (
                            self.discrete_page,
                            self.char_page,
                            self.energy_scan_page,
                            self.xrf_spectrum_page,
                        ) and len(shapes):
                            # This could be done in more nicer way...
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                            self.create_task(task_model)
                    elif isinstance(task_model, queue_model_objects.Basket):
                        for sample_node in task_model.get_sample_list():
                            task_group = self.create_task_group(sample_node)
                            if self.tool_box.currentWidget() in (
                                self.discrete_page,
                                self.char_page,
                                self.energy_scan_page,
                                self.xrf_spectrum_page,
                                self.xray_imaging_page,
                            ) and len(shapes):
                                for shape in shapes:
                                    self.create_task(task_group, shape)
                            else:
                                self.create_task(task_group)
                    else:
                        if self.tool_box.currentWidget() in (
                            self.discrete_page,
                            self.char_page,
                            self.energy_scan_page,
                            self.xrf_spectrum_page,
                            self.xray_imaging_page,
                        ) and len(shapes):
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                            self.create_task(task_model)
                self.tree_brick.select_last_added_item()
                self.tree_brick.update_enable_collect()

            self.tool_box.currentWidget().update_selection()

    def create_task_group(self, task_model):
        group_task_node = queue_model_objects.TaskGroup()
        current_item = self.tool_box.currentWidget()

        group_name = current_item.get_task_node_name()
        group_task_node.set_name(group_name)
        num = task_model.get_next_number_for_name(group_name)
        group_task_node.set_number(num)

        HWR.beamline.queue_model.add_child(task_model, group_task_node)

        return group_task_node

    def create_task(self, task_node, shape=None):
        # Selected item is a task group
        if isinstance(task_node, queue_model_objects.TaskGroup):
            sample = task_node.get_parent()
            task_list = self.tool_box.currentWidget().create_task(sample, task_node, shape)

            for child_task_node in task_list:
                HWR.beamline.queue_model.add_child(task_node, child_task_node)
        # The selected item is a task, make a copy.
        else:
            new_node = HWR.beamline.queue_model.copy_node(task_node)
            new_snapshot = (
                HWR.beamline.sample_view.get_scene_snapshot()
            )

            if isinstance(task_node, queue_model_objects.Characterisation):
                new_node.reference_image_collection.acquisitions[
                    0
                ].acquisition_parameters.centred_position.snapshot_image = new_snapshot
            elif isinstance(task_node, queue_model_objects.DataCollection):
                new_node.acquisitions[
                    0
                ].acquisition_parameters.centred_position.snapshot_image = new_snapshot
            elif type(task_node) in (
                queue_model_objects.DataCollection,
                queue_model_objects.XRFSpectrum,
            ):
                new_node.centred_position.snapshot_image = new_snapshot

            HWR.beamline.queue_model.add_child(
                task_node.get_parent(), new_node
            )

    def collect_now_button_click(self):
        if not self.tree_brick.dc_tree_widget.enable_collect_condition:
            logging.getLogger("GUI").warning("Collections are disabled")

        selected_items = self.tree_brick.get_selected_items()
        mounted_sample_item = self.tree_brick.dc_tree_widget.get_mounted_sample_item()
        will_mount_sample = False

        for item in selected_items:
            if isinstance(item, queue_item.SampleQueueItem):
                if item != mounted_sample_item:
                    will_mount_sample = True
            else:
                sample_item = item.get_sample_view_item()
                if sample_item != mounted_sample_item:
                    will_mount_sample = True

        if will_mount_sample:
            conf_msg = "One or several not mounted samples are selected.\n" +\
                       "Before collecting sample(s) will be mounted. Continue?"
            if (
                QtImport.QMessageBox.warning(
                      None, "Question", conf_msg,
                      QtImport.QMessageBox.Ok, QtImport.QMessageBox.No
                )
                == QtImport.QMessageBox.No
            ):
                return


        self.create_task_button_click()
        collect_items = []
        for item in self.tree_brick.dc_tree_widget.get_collect_items():
            if isinstance(item, queue_item.SampleCentringQueueItem):
                item.setOn(False)
                item.setText(1, "Skipped")
                item.set_strike_out(True)
                item.get_model().set_executed(True)
                item.get_model().set_running(False)
                item.get_model().set_enabled(False)
            else:
                collect_items.append(item)
        if self.tree_brick.dc_tree_widget.enable_collect_condition:
            self.tree_brick.dc_tree_widget.collect_items(collect_items)
        else:
            logging.getLogger("GUI").warning("Collections are disabled")

    def path_template_conflict_changed(self, is_conflict):
        self.path_conflict = is_conflict
        self.toggle_queue_button_enable()

    def acq_parameters_conflict_changed(self, is_conflict):
        self.acq_conflict = is_conflict
        self.toggle_queue_button_enable()

    def enable_collect_changed(self, enable_collect):
        self.enable_collect = enable_collect
        self.toggle_queue_button_enable()

    def toggle_queue_button_enable(self):
        self.create_task_button.setDisabled(self.path_conflict or self.acq_conflict)
        self.collect_now_button.setDisabled(
            self.path_conflict or self.acq_conflict or not self.enable_collect
        )
        if self.tool_box.currentWidget() in (self.helical_page, self.advanced_page):
            if len(self.tool_box.currentWidget().get_selected_shapes()) == 0:
                self.create_task_button.setEnabled(False)
                self.collect_now_button.setEnabled(False)
        if self.tool_box.currentWidget() == self.xray_imaging_page:
            self.create_task_button.setEnabled(True)
            self.collect_now_button.setEnabled(True)
