#pylint: skip-file

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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.
#
#  Please user PEP 0008 -- "Style Guide for Python Code" to format code
#  https://www.python.org/dev/peps/pep-0008/

import os
import time

import logging
import gevent
import jsonpickle
import webbrowser
from datetime import datetime
from collections import namedtuple

from gui.utils import Colors, Icons, queue_item, QtImport
from gui.widgets.confirm_dialog import ConfirmDialog
from gui.widgets.plate_navigator_widget import PlateNavigatorWidget

from HardwareRepository.HardwareObjects import queue_entry
from HardwareRepository.HardwareObjects import queue_model_objects
from HardwareRepository.HardwareObjects.queue_model_enumerables import CENTRING_METHOD

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MxCuBE collaboration"]
__license__ = "LGPLv3+"


SCFilterOptions = namedtuple('SCFilterOptions',
                             ['FREE_PIN',
                              'SAMPLE_CHANGER',
                              'PLATE',
                              'MOUNTED_SAMPLE'])

SC_FILTER_OPTIONS = SCFilterOptions(0, 1, 2, 3)


class DataCollectTree(QtImport.QWidget):

    enableCollectSignal = QtImport.pyqtSignal(bool)

    def __init__(self, parent=None, name="data_collect",
                 selection_changed=None):

        QtImport.QWidget.__init__(self, parent)

        self.setObjectName(name)

        # Internal values -----------------------------------------------------
        self.item_iterator = None
        self.enable_collect_condition = False
        self.collecting = False
        self.sample_mount_method = 0
        self.centring_method = 0
        self.sample_centring_result = gevent.event.AsyncResult()
        self.tree_brick = self.parent()
        self.samples_initialized = None
        self.user_stopped = False
        self.last_added_item = None
        self.item_copy = None

        self.selection_changed_cb = None
        self.collect_stop_cb = None
        #self.clear_centred_positions_cb = None
        self.run_cb = None
        self.item_menu = None
        self.item_history_list = []
        self.close_kappa = False
        self.show_sc_during_mount = True
        self.show_sc_during_mount = True

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.confirm_dialog = ConfirmDialog(self, 'Confirm Dialog')
        self.confirm_dialog.setModal(True)

        self.pin_icon = Icons.load_icon("sample_axis.png")
        self.task_icon = Icons.load_icon("task.png")
        self.play_icon = Icons.load_icon("VCRPlay.png")
        self.stop_icon = Icons.load_icon("Stop.png")
        self.ispyb_icon = Icons.load_icon("SampleChanger2.png")
        self.ispyb_diff_plan_icon = Icons.load_icon("NewDocument.png")
        self.star_icon = Icons.load_icon("star")
        self.caution_icon = Icons.load_icon("Caution2.png")

        self.button_widget = QtImport.QWidget(self)
        self.up_button = QtImport.QPushButton(self.button_widget)
        self.up_button.setIcon(Icons.load_icon("Up2.png"))
        self.up_button.setFixedHeight(25)
        self.down_button = QtImport.QPushButton(self.button_widget)
        self.down_button.setIcon(Icons.load_icon("Down2.png"))
        self.down_button.setFixedHeight(25)

        self.copy_button = QtImport.QPushButton(self.button_widget)
        self.copy_button.setIcon(Icons.load_icon("copy.png"))
        self.copy_button.setDisabled(True)
        self.copy_button.setToolTip("Copy highlighted queue entries")

        self.delete_button = QtImport.QPushButton(self.button_widget)
        self.delete_button.setIcon(Icons.load_icon("bin_small.png"))
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip("Delete highlighted queue entries")

        self.collect_button = QtImport.QPushButton(self.button_widget)
        self.collect_button.setText("Collect Queue")
        #elf.collect_button.setFixedWidth(125)
        self.collect_button.setIcon(self.play_icon)
        self.collect_button.setDisabled(True)
        Colors.set_widget_color(self.collect_button,
                                Colors.LIGHT_GREEN,
                                QtImport.QPalette.Button)

        self.continue_button = QtImport.QPushButton(self.button_widget)
        self.continue_button.setText('Pause')
        self.continue_button.setDisabled(True)
        self.continue_button.setToolTip("Pause after current data collection")

        self.tree_splitter = QtImport.QSplitter(QtImport.Qt.Vertical, self)
        self.sample_tree_widget = QtImport.QTreeWidget(self.tree_splitter)
        self.history_tree_widget = QtImport.QTreeWidget(self.tree_splitter)
        self.history_tree_widget.setHidden(True)
        self.history_enable_cbox = QtImport.QCheckBox("Queue history", self)
        self.history_enable_cbox.setChecked(False)

        self.plate_navigator_cbox = QtImport.QCheckBox("Plate navigator", self)
        self.plate_navigator_widget = PlateNavigatorWidget(self)
        self.plate_navigator_widget.hide()

        # Layout --------------------------------------------------------------
        button_widget_grid_layout = QtImport.QGridLayout(self.button_widget)
        button_widget_grid_layout.addWidget(self.up_button, 0, 0)
        button_widget_grid_layout.addWidget(self.down_button, 0, 1)
        button_widget_grid_layout.addWidget(self.collect_button, 1, 0, 1, 2)
        button_widget_grid_layout.addWidget(self.copy_button, 0, 3)
        button_widget_grid_layout.addWidget(self.delete_button, 0, 4)
        button_widget_grid_layout.addWidget(self.continue_button, 1, 3, 1, 2)
        button_widget_grid_layout.setColumnStretch(2, 1)
        button_widget_grid_layout.setContentsMargins(0, 0, 0, 0)
        button_widget_grid_layout.setSpacing(1)

        main_layout = QtImport.QVBoxLayout(self)
        # main_layout.addWidget(self.sample_tree_widget)
        main_layout.addWidget(self.tree_splitter)
        main_layout.addWidget(self.history_enable_cbox)
        main_layout.addWidget(self.plate_navigator_cbox)
        main_layout.addWidget(self.plate_navigator_widget)
        main_layout.addWidget(self.button_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(1)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.up_button.clicked.connect(self.up_click)
        self.down_button.clicked.connect(self.down_click)
        self.copy_button.clicked.connect(self.copy_click)
        self.delete_button.clicked.connect(self.delete_click)
        self.collect_button.clicked.connect(self.collect_stop_toggle)
        self.sample_tree_widget.itemSelectionChanged.\
            connect(self.sample_tree_widget_selection)
        self.sample_tree_widget.contextMenuEvent = self.show_context_menu
        self.sample_tree_widget.itemDoubleClicked.connect(self.item_double_click)
        self.sample_tree_widget.itemClicked.connect(self.item_click)
        self.sample_tree_widget.itemChanged.connect(self.item_changed)

        self.confirm_dialog.continueClickedSignal.connect(self.collect_items)
        self.continue_button.clicked.connect(self.continue_button_click)

        # self.history_tree_widget.cellDoubleClicked.\
        #     connect(self.history_table_double_click)
        self.history_enable_cbox.stateChanged.\
            connect(self.history_tree_widget.setVisible)

        self.plate_navigator_cbox.stateChanged.\
            connect(self.use_plate_navigator)

        # Other ---------------------------------------------------------------
        # TODO number of columns should not be hard coded but come from processing
        # methods
        self.sample_tree_widget.setColumnCount(6)
        for col in range(3):
            self.sample_tree_widget.setColumnWidth(2 + col, 25)
        self.sample_tree_widget.setColumnWidth(1, 200)
        self.sample_tree_widget.setColumnWidth(5, 1000)

        self.sample_tree_widget.header().hide()
        self.sample_tree_widget.setRootIsDecorated(1)
        self.sample_tree_widget.setCurrentItem(self.sample_tree_widget.topLevelItem(0))
        self.sample_tree_widget.setSelectionMode(
            QtImport.QAbstractItemView.ExtendedSelection)
        self.setAttribute(QtImport.Qt.WA_WState_Polished)
        self.sample_tree_widget.viewport().installEventFilter(self)

        self.history_tree_widget.setEditTriggers(
            QtImport.QAbstractItemView.NoEditTriggers)
        self.history_tree_widget.setColumnCount(5)
        self.history_tree_widget.setHeaderLabels(
            ("Date/Time", "Sample", "Type", "Status", "Details"))
        self.tree_splitter.setSizes([200, 20])

    def setFont(self, font):
        QtImport.QWidget.setFont(self, font)
        self.confirm_dialog.setFont(font)

    def eventFilter(self, _object, event):
        """Custom event filter"""
        if event.type() == QtImport.QEvent.MouseButtonDblClick:
            self.show_details()
            return True
        else:
            return False

    def enable_collect(self, state):
        """
        Descript. :
        """
        self.sample_tree_widget.setDisabled(not state)
        #self.collect_button.setDisabled(not state)
        #self.up_button.setDisabled(not state)
        #self.down_button.setDisabled(not state)
        self.delete_button.setDisabled(not state)
        self.toggle_collect_button_enabled()

    def show_context_menu(self, context_menu_event):
        """When on a tree item clicked creates and opens popup menu"""
        if len(self.get_selected_items()) > 1:
            return

        self.item_menu = QtImport.QMenu(self.sample_tree_widget)
        item = self.sample_tree_widget.currentItem()

        if item:
            add_remove = True
            add_details = False
            self.item_menu.addAction("Rename", self.rename_treewidget_item)
            if item.has_star():
                self.item_menu.addAction(
                    "Remove star", self.remove_star_treewidget_item)
            else:
                self.item_menu.addAction(self.star_icon,
                                         "Add star",
                                         self.add_star_treewidget_item)

            if isinstance(item, queue_item.TaskQueueItem):
                if not isinstance(item.get_model(),
                                  queue_model_objects.SampleCentring):
                    self.item_menu.addSeparator()
                    self.item_menu.addAction("Cut", self.cut_item)
                    self.item_menu.addAction("Copy", self.copy_item)
                    paste_action = self.item_menu.addAction("Paste", self.paste_item)
                    paste_action.setEnabled(self.item_copy is not None)
                    self.item_menu.addSeparator()
                    self.item_menu.addAction("Save in file", self.save_item)
                    self.item_menu.addAction("Load from file", self.load_item)
                    add_details = True
                else:
                    self.item_menu.addSeparator()
            elif isinstance(item, queue_item.DataCollectionGroupQueueItem):
                self.item_menu.addSeparator()
                paste_action = self.item_menu.addAction("Paste", self.paste_item)
                paste_action.setEnabled(self.item_copy is not None)
                add_details = True
            elif isinstance(item, queue_item.SampleQueueItem):
                paste_action = self.item_menu.addAction("Paste", self.paste_item)
                paste_action.setEnabled(self.item_copy is not None)
                self.item_menu.addSeparator()
                if not item.get_model().free_pin_mode:
                    if HWR.beamline.diffractometer.in_plate_mode():
                        self.plate_sample_to_mount = item
                        self.item_menu.addAction("Move", self.mount_sample)
                    else:
                        if self.is_mounted_sample_item(item):
                            self.item_menu.addAction("Un-Mount", self.unmount_sample)
                        else:
                            self.item_menu.addAction("Mount",
                                                     self.mount_sample)
                            close_kappa_action = self.item_menu.addAction(
                                "Close kappa after sample mount")
                            close_kappa_action.toggled.connect(
                                self.close_kappa_toggled)
                            close_kappa_action.setCheckable(True)
                            close_kappa_action.setChecked(self.close_kappa)

                            show_sc_view_action = self.item_menu.addAction(
                                "During mount show sample changer")
                            show_sc_view_action.toggled.connect(
                                self.show_sc_during_mount_toggled)
                            show_sc_view_action.setCheckable(True)
                            show_sc_view_action.setChecked(self.show_sc_during_mount)

                self.item_menu.addSeparator()

                sync_action = self.item_menu.addAction("Add diffraction plan from ISPyB",
                                                       self.sync_diffraction_plan)
                sample_model = item.get_model()
                sync_action.setEnabled(sample_model.diffraction_plan is not None)

                add_remove = False
                add_details = True
            elif isinstance(item, queue_item.BasketQueueItem):
                paste_action = self.item_menu.addAction("Paste", self.paste_item)
                paste_action.setEnabled(self.item_copy is not None)
                self.item_menu.addSeparator()
                add_remove = False

            self.item_menu.addAction("Add collection from file", self.insert_item)
            self.item_menu.addSeparator()
            if add_remove:
                self.item_menu.addAction("Remove", self.delete_click)
            if add_details:
                self.item_menu.addAction("Details", self.show_details)
            if isinstance(item, queue_item.DataCollectionQueueItem):
                open_in_ispyb_action = self.item_menu.addAction(
                    "View results in ISPyB", self.open_ispyb_link)
                open_in_ispyb_action.setEnabled(item.get_model().id > 0)
            self.item_menu.popup(QtImport.QCursor.pos())

    def item_double_click(self):
        """Shows more details of a double clicked tree item"""
        self.show_details()

    def history_table_double_click(self, row, col):
        """Shows more details of a double clicked history view item"""
        # elf.show_details([self.item_history_list[row]])
        pass

    def item_click(self):
        """Single item click verifies if there is a path conflict"""
        self.check_for_path_collisions()
        # self.sample_tree_widget_selection()
        self.toggle_collect_button_enabled()

    def item_changed(self, item, column):
        """As there is no signal when item is checked/unchecked
          it is necessary to update item based on QTreeWidget signal itemChanged.
          Item check state is updated when checkbox is toggled
          (to avoid update when text is changed)
        """
        # if item.checkState(0) != item.get_previous_check_state():
        #   item.update_check_state()

        # IK. This type check should not be here,because all tree items are
        # anyway QueueItems. but somehow on the init item got native
        # QTreeWidgetItem type and method was not found. Interesting...

        if isinstance(item, queue_item.QueueItem):
            item.update_check_state(item.checkState(0))

    def use_plate_navigator(self, state):
        """Toggles visibility of the plate navigator"""
        self.plate_navigator_widget.setVisible(state)

    def item_parameters_changed(self):
        """Updates tree items when one or several parameters are changed"""
        items = self.get_selected_items()
        for item in items:
            item.update_display_name()

    def context_collect_item(self):
        """Calls collect_items method"""
        items = self.get_selected_items()

        if len(items) == 1:
            item = items[0]

            # Turn this item on (check it), incase its not already checked.
            if item.state() == 0:
                item.setOn(True)

            self.collect_items(items)

    def show_details(self, items=None):
        """Shows more details of a selected tree item"""
        if items is None:
            items = self.get_selected_items()
        if len(items) == 1:
            item = items[0]
            if isinstance(item, queue_item.SampleQueueItem):
                self.tree_brick.show_sample_tab(item)
            elif isinstance(item, queue_item.DataCollectionQueueItem):
                data_collection = item.get_model()
                if data_collection.is_mesh():
                    self.tree_brick.show_advanced_tab(item)
                else:
                    self.tree_brick.show_datacollection_tab(item)
            elif isinstance(item, queue_item.CharacterisationQueueItem):
                self.tree_brick.show_char_parameters_tab(item)
            elif isinstance(item, queue_item.EnergyScanQueueItem):
                self.tree_brick.show_energy_scan_tab(item)
            elif isinstance(item, queue_item.XRFSpectrumQueueItem):
                self.tree_brick.show_xrf_spectrum_tab(item)
            elif isinstance(item, queue_item.GenericWorkflowQueueItem):
                self.tree_brick.show_workflow_tab(item)
            elif isinstance(item, queue_item.DataCollectionGroupQueueItem):
                self.tree_brick.show_dcg_tab(item)
            elif isinstance(item, queue_item.XrayCenteringQueueItem):
                self.tree_brick.show_advanced_tab(item)
        # elif len(items) == 0:
        #    self.tree_brick.show_sample_tab()

    def rename_treewidget_item(self):
        """Rename treewidget item"""
        items = self.get_selected_items()
        if len(items) == 1:
            items[0].setFlags(QtImport.Qt.ItemIsSelectable |
                              QtImport.Qt.ItemIsEnabled |
                              QtImport.Qt.ItemIsEditable)
            self.sample_tree_widget.editItem(items[0])
            items[0].setFlags(QtImport.Qt.ItemIsSelectable |
                              QtImport.Qt.ItemIsEnabled)
            items[0].get_model().set_name(items[0].text(0))

    def add_star_treewidget_item(self):
        """Add star to the item for further filter"""
        items = self.get_selected_items()
        for item in items:
            item.set_star(True)
            if item.has_star():
                item.setIcon(0, self.star_icon)

    def remove_star_treewidget_item(self):
        """Removes star"""
        items = self.get_selected_items()
        for item in items:
            item.set_star(False)
            if not item.has_star():
                if self.is_mounted_sample_item(item):
                    item.set_mounted_style(True)
                else:
                    item.setIcon(0, QtImport.QIcon())

    def scroll_to_item(self, item=None):
        if not item:
            items = self.get_selected_items()
            if len(items) > 0:
                item = items[0]

        if item:
            self.sample_tree_widget.scrollToItem(
                item, QtImport.QAbstractItemView.PositionAtCenter)
            self.sample_tree_widget.horizontalScrollBar().setValue(0)

    def mount_sample(self):
        """Calls sample mounting"""
        self.enable_collect(False)
        gevent.spawn(self.mount_sample_task)

    def close_kappa_toggled(self, state):
        self.close_kappa = state

    def show_sc_during_mount_toggled(self, state):
        self.show_sc_during_mount = state

    def mount_sample_task(self):
        """Sample mount task via queue_entry"""
        items = self.get_selected_items()

        if len(items) == 1:
            if not items[0].get_model().free_pin_mode:
                items[0].setText(1, "Loading sample...")
                self.sample_centring_result = gevent.event.AsyncResult()
                try:
                    if self.show_sc_during_mount:
                        self.tree_brick.sample_mount_started.emit()
                    queue_entry.mount_sample(
                        items[0],
                        items[0].get_model(),
                        self.centring_done,
                        self.sample_centring_result
                    )
                    if self.close_kappa:
                        HWR.beamline.diffractometer.close_kappa()
                except Exception as e:
                    items[0].setText(1, "Error loading")
                    items[0].set_background_color(3)
                    msg = "Error loading sample, " + str(e)
                    logging.getLogger("GUI").error(msg)
                finally:
                    self.enable_collect(True)
                    self.tree_brick.sample_mount_finished.emit()
            else:
                logging.getLogger("GUI").\
                    info('Its not possible to mount samples in free pin mode')

    def centring_done(self, success, centring_info):
        """Updates centring status"""
        if success:
            self.sample_centring_result.set(centring_info)
        else:
            msg = "Loop centring failed or was cancelled, " +\
                  "please continue manually."
            logging.getLogger("GUI").warning(msg)

    def unmount_sample(self):
        """Sample unmount task"""
        self.enable_collect(False)
        gevent.spawn(self.unmount_sample_task)

    def unmount_sample_task(self):
        """Sample unmount"""
        items = self.get_selected_items()

        if len(items) == 1:
            if self.show_sc_during_mount:
                self.tree_brick.sample_mount_started.emit()
            items[0].setText(1, "Unloading sample...")
            HWR.beamline.sample_view.clear_all()
            logging.getLogger("GUI").\
                info("All centred positions associated with this " +
                     "sample will be lost.")

            location = items[0].get_model().location

            if self.show_sc_during_mount:
                self.tree_brick.sample_mount_started.emit()
            self.tree_brick.enable_widgets.emit(False)

            sample_changer = None
            if self.sample_mount_method == 1:
                try:
                    sample_changer = HWR.beamline.sample_changer
                except AttributeError:
                    sample_changer = None
            elif self.sample_mount_method == 2:
                try:
                    sample_changer = HWR.beamline.plate_manipulator
                except AttributeError:
                    sample_changer = None

            if sample_changer:
                robot_action_dict = {"actionType": "UNLOAD",
                                     "containerLocation": location[1],
                                     "dewarLocation": location[0],
                                     "sampleBarcode": items[0].get_model().code,
                                     "sampleId": items[0].get_model().lims_id,
                                     "sessionId": HWR.beamline.session.session_id,
                                     "startTime": time.strftime("%Y-%m-%d %H:%M:%S")}

                try:
                    if hasattr(sample_changer, '__TYPE__')\
                            and sample_changer.__TYPE__ in ('CATS', 'Marvin', 'Mockup'):
                        sample_changer.unload(wait=True)
                    else:
                        sample_changer.unload(22, location, wait=False)
                except Exception as e:
                    items[0].setText(1, "Error in unloading")
                    msg = "Error unloading sample, " + str(3) #please check" +\
                    #    " sample changer: " + str(e)
                    logging.getLogger("GUI").error(msg)

                robot_action_dict["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
                if not sample_changer.hasLoadedSample():
                    robot_action_dict['status'] = "SUCCESS"
                else:
                    robot_action_dict['message'] = "Sample was not unloaded"
                    robot_action_dict['status'] = "ERROR"

                HWR.beamline.lims.store_robot_action(
                    robot_action_dict)

            items[0].setText(1, "")
            items[0].setOn(False)
            items[0].set_mounted_style(False)
        self.enable_collect(True)
        self.tree_brick.enable_widgets.emit(True)
        self.tree_brick.sample_mount_finished.emit()

    def sample_tree_widget_selection(self):
        """Callback when a tree item is selected.
           If a item selected then enables copy,up and down buttons
        """
        items = self.get_selected_items()
        self.copy_button.setDisabled(True)
        self.up_button.setDisabled(True)
        self.down_button.setDisabled(True)

        for item in items:
            if isinstance(item, queue_item.TaskQueueItem):
                self.copy_button.setDisabled(False)
                if len(items) == 1:
                    if item.parent().indexOfChild(item) > 0:
                        self.up_button.setDisabled(False)
                    if item.parent().indexOfChild(item) < item.parent().childCount() - 1:
                        self.down_button.setDisabled(False)
            break

        self.selection_changed_cb(items)
        self.toggle_collect_button_enabled()

    def toggle_collect_button_enabled(self):
        enable_collect = (len(self.get_checked_items()) > 1 and
                          len(self.get_checked_samples()) and
                          self.enable_collect_condition) or \
            self.collecting

        self.collect_button.setEnabled(enable_collect)
        self.enableCollectSignal.emit(
            self.enable_collect_condition and not self.collecting)

    def get_item_by_model(self, parent_node):
        """Returns tree item by its model
        """
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if item.get_model() is parent_node:
                return item

            it += 1
            item = it.value()

        return self.sample_tree_widget

    def last_top_level_item(self):
        """Returns the last top level item"""
        last_child_index = self.sample_tree_widget.topLevelItemCount() - 1
        return self.sample_tree_widget.topLevelItem(last_child_index)

    def add_to_view(self, parent, task):
        """Adds queue element to the tree. After element has been
           added selection of tree is cleared.
           If entry is a collection then it is selected and
           selection callback is raised.
        """
        view_item = None
        parent_tree_item = self.get_item_by_model(parent)

        if parent_tree_item is self.sample_tree_widget:
            last_item = self.last_top_level_item()
        else:
            last_item = parent_tree_item.lastItem()

        cls = queue_item.MODEL_VIEW_MAPPINGS[task.__class__]
        view_item = cls(parent_tree_item, last_item, task.get_display_name())

        if isinstance(task, queue_model_objects.Basket):
            view_item.setExpanded(task.get_is_present() == True)
            view_item.setDisabled(not task.get_is_present())
        else:
            view_item.setExpanded(True)

        HWR.beamline.queue_model.view_created(view_item, task)
        # self.sample_tree_widget_selection()
        self.toggle_collect_button_enabled()

        self.last_added_item = view_item

        if isinstance(view_item, queue_item.TaskQueueItem) and \
                self.samples_initialized:
            self.tree_brick.auto_save_queue()

        #for col in range(2):
        self.sample_tree_widget.resizeColumnToContents(0)

        if isinstance(task, queue_model_objects.DataCollection):
            view_item.init_tool_tip()
            view_item.init_processing_info()

    def get_selected_items(self):
        """Return a list with selected items"""
        items = self.sample_tree_widget.selectedItems()
        for item in items:
            if item.isDisabled():
                items.pop(item)
        return items

    def de_select_items(self):
        """De selects all items"""
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            item.setCheckState(0, QtImport.Qt.Unchecked)
            it += 1
            item = it.value()

    def get_selected_samples(self):
        """Returns a list with selected samples"""
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item, queue_item.SampleQueueItem):
                res_list.append(item)
        return res_list

    def get_selected_tasks(self):
        """Returns a list with tasks"""
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item, queue_item.TaskQueueItem):
                res_list.append(item)
        return res_list

    def get_selected_dcs(self):
        """Returns a list with data collection tasks
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item, queue_item.DataCollectionQueueItem):
                res_list.append(item)
        return res_list

    def get_selected_task_nodes(self):
        """Returns a list with data collection groups
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item, queue_item.DataCollectionGroupQueueItem):
                res_list.append(item)
        return res_list

    def is_sample_selected(self):
        """Returns True if a mounted sample"""
        items = self.get_selected_items()

        for item in items:
            if isinstance(item, queue_item.SampleQueueItem):
                return True
        return False

    def get_mounted_sample_item(self):
        """Returns mounted sample item"""
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if isinstance(item, queue_item.SampleQueueItem):
                if item.mounted_style:
                    return item
            it += 1
            item = it.value()

    def get_checked_samples(self):
        res_list = []
        for item in self.get_checked_items():
            if isinstance(item, queue_item.SampleQueueItem):
                res_list.append(item)
        return res_list

    def filter_sample_list(self, option):
        """Updates sample tree based on the sample mount"""
        self.sample_tree_widget.clearSelection()
        self.confirm_dialog.set_plate_mode(False)
        self.sample_mount_method = option
        if option == SC_FILTER_OPTIONS.SAMPLE_CHANGER:
            self.sample_tree_widget.clear()
            HWR.beamline.queue_model.select_model('ispyb')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.PLATE:
            self.sample_tree_widget.clear()
            HWR.beamline.queue_model.select_model('plate')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.MOUNTED_SAMPLE:
            loaded_sample_loc = None

            if HWR.beamline.diffractometer.in_plate_mode():
                try:
                    loaded_sample = HWR.beamline.plate_manipulator.getLoadedSample()
                    loaded_sample_loc = loaded_sample.getCoords()
                except BaseException:
                    pass
            else:
                try:
                    loaded_sample = HWR.beamline.sample_changer.getLoadedSample()
                    loaded_sample_loc = loaded_sample.getCoords()
                except BaseException:
                    pass
            it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
            item = it.value()

            while item:
                if isinstance(item, queue_item.SampleQueueItem):
                    # TODO fix this to actual plate sample!!!
                    if item.get_model().location == loaded_sample_loc:
                        item.setSelected(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)

                it += 1
                item = it.value()

            self.hide_empty_baskets()

        elif option == SC_FILTER_OPTIONS.FREE_PIN:
            self.sample_tree_widget.clear()
            HWR.beamline.queue_model.select_model('free-pin')
            self.set_sample_pin_icon()
        self.sample_tree_widget_selection()

    def set_centring_method(self, method_number):
        """Sets centring method"""
        self.centring_method = method_number

        try:
            dm = HWR.beamline.diffractometer

            if self.centring_method == CENTRING_METHOD.FULLY_AUTOMATIC:
                dm.user_confirms_centring = False
            else:
                dm.user_confirms_centring = True
        except AttributeError:
            # beamline_setup_hwobj not set when method called
            pass

    def continue_button_click(self):
        """Sets or resets pause event"""
        if HWR.beamline.queue_manager.is_executing():
            if not HWR.beamline.queue_manager.is_paused():
                HWR.beamline.queue_manager.set_pause(True)
            else:
                HWR.beamline.queue_manager.set_pause(False)

    def queue_paused_handler(self, state):
        """Pause handlers"""
        if state:
            self.continue_button.setText('Continue')
            QtImport.QToolTip.showText(self.continue_button.mapToGlobal(
                QtImport.QPoint(0, 10)),
                "If necessary please center a new point.\n\n" +
                "Press 'Continue' to continue.")
            Colors.set_widget_color(self.continue_button,
                                    Colors.LIGHT_YELLOW,
                                    QtImport.QPalette.Button)
        else:
            self.continue_button.setText('Pause')
            Colors.set_widget_color(
                self.continue_button,
                Colors.BUTTON_ORIGINAL,
                QtImport.QPalette.Button)

    def collect_stop_toggle(self):
        """Stops queue"""

        HWR.beamline.queue_manager.disable(False)
        if self.collecting:
            self.stop_collection()

        else:
            path_conflict = self.check_for_path_collisions()

            if path_conflict:
                HWR.beamline.queue_manager.disable(True)

            if HWR.beamline.queue_manager.is_disabled():
                logging.getLogger("GUI").\
                    error('Can not start collect, see the tasks marked' +
                          ' in the tree and solve the prorblems.')

            else:
                checked_items = self.get_collect_items()
                # Unselect selected items.
                selected_items = self.get_selected_items()
                for item in selected_items:
                    item.setSelected(False)
                    #self.sample_tree_widget.setSelected(item, False)

                if len(checked_items):
                    self.confirm_dialog.set_items(checked_items)
                    self.confirm_dialog.show()
                else:
                    message = "No data collections selected, please select one" + \
                              " or more data collections"

                    QtImport.QMessageBox.information(self, "Data collection",
                                                     message, "OK")

    def enable_sample_changer_widget(self, state):
        """Enables sample changer widget"""
        self.tree_brick.sample_changer_widget.centring_cbox.setEnabled(state)
        self.tree_brick.sample_changer_widget.filter_cbox.setEnabled(state)

    def is_mounted_sample_item(self, item):
        """Checks if item is mounted"""
        result = False

        if isinstance(item, queue_item.SampleQueueItem):
            if item.get_model().free_pin_mode == True:
                result = True
            elif HWR.beamline.diffractometer.in_plate_mode():
                if HWR.beamline.plate_manipulator is not None:
                    if not HWR.beamline.plate_manipulator.hasLoadedSample():
                        result = False
                    # TODO remove :2 and check full location
                    elif item.get_model().location == HWR.beamline.plate_manipulator.getLoadedSample().getCoords():
                        result = True
            elif HWR.beamline.sample_changer is not None:
                if not HWR.beamline.sample_changer.hasLoadedSample():
                    result = False
                elif item.get_model().location == HWR.beamline.sample_changer.getLoadedSample().getCoords():
                    result = True
        return result

    def collect_items(self, items=[], checked_items=[]):
        """Starts data collection
           - deselects all shapes
           - checks data collection parameters via beamline setup
           - calls collection method
        """
        HWR.beamline.sample_view.de_select_all()

        collection_par_list = []
        for item in checked_items:
            # update the run-number text incase of re-collect
            #item.setText(0, item.get_model().get_name())

            # Clear status
            item.setText(1, "")
            item.reset_style()
            if isinstance(item.get_model(), queue_model_objects.DataCollection):
                collection_par_list.append(item.get_model().as_dict())
        """
        invalid_parameters = HWR.beamline.\
            check_collection_parameters(collection_par_list)
        if len(invalid_parameters) > 0:
            msg = "Collection parameter "
            for item in invalid_parameters:
                msg = msg + "%s, " % item
            msg = msg[:-2]
            msg += " is out of range. Correct the parameter(s) " + \
                   "and run queue again"
            logging.getLogger("GUI").error(msg)
            return
        """

        self.user_stopped = False
        self.delete_button.setEnabled(False)
        self.enable_sample_changer_widget(False)
        self.collecting = True
        self.collect_button.setText(" Stop   ")
        Colors.set_widget_color(
            self.collect_button,
            Colors.LIGHT_RED,
            QtImport.QPalette.Button)
        self.collect_button.setIcon(self.stop_icon)
        self.continue_button.setEnabled(True)
        self.parent().set_condition_state("confirmation_window_accepted",
                                          True)
        self.run_cb()
        HWR.beamline.sample_view.set_cursor_busy(True)
        try:
            HWR.beamline.queue_manager.execute()
        except Exception as ex:
            raise ex
        self.parent().set_condition_state("confirmation_window_accepted",
                                          False)

    def stop_collection(self):
        """Stops queue"""
        HWR.beamline.sample_view.set_cursor_busy(False)
        HWR.beamline.queue_manager.stop()
        self.queue_stop_handler()

    def queue_stop_handler(self, status=None):
        """Stop handler"""
        HWR.beamline.sample_view.set_cursor_busy(False)
        self.user_stopped = True
        self.queue_execution_completed(None)

    def queue_entry_execution_started(self, queue_entry):
        """Slot connected to the signal comming from QueueManager
           If energy scan, xrf spectrum or mesh scan then opens
           a tab with detailed results
        """
        view_item = queue_entry.get_view()

        if isinstance(view_item, queue_item.EnergyScanQueueItem):
            self.tree_brick.show_energy_scan_tab(view_item)
        elif isinstance(view_item, queue_item.XRFSpectrumQueueItem):
            self.tree_brick.show_xrf_spectrum_tab(view_item)
        elif isinstance(view_item, queue_item.DataCollectionQueueItem):
            if view_item.get_model().is_mesh():
                self.tree_brick.populate_advanced_tab(view_item)
            else:
                self.tree_brick.populate_dc_parameters_tab(view_item)

        self.sample_tree_widget.clearSelection()
        view_item.setSelected(True)

    def queue_entry_execution_finished(self, queue_entry, status):
        """Slot connected to the signal coming from QueueManager
           Adds executed queue entry to the history view
        """
        view_item = queue_entry.get_view()
        if queue_entry.get_type_str() not in ["Sample", "Basket", ""]:
            item_model = queue_entry.get_data_model()
            item_details = ""
            sample_model = item_model.get_sample_node()
            # sample_model = item_model.get_parent().get_parent()

            if isinstance(view_item, queue_item.DataCollectionQueueItem):
                item_details = "%.1f%s " % (item_model.as_dict()["osc_range"],
                                            u"\u00b0") + \
                               "%.5f sec, " % item_model.as_dict()["exp_time"] + \
                               "%d images, " % item_model.as_dict()["num_images"] + \
                               "%.2f keV, " % item_model.as_dict()["energy"] + \
                               "%d%% transm, " % item_model.as_dict()["transmission"] + \
                               "%.2f A" % item_model.as_dict()["resolution"]
            elif isinstance(view_item, queue_item.EnergyScanQueueItem):
                item_details = "Element: %s, " % item_model.element_symbol + \
                               "Edge: %s" % item_model.edge

            self.add_history_entry(sample_model.get_display_name(),
                                   datetime.now().strftime("%Y.%m.%d"),
                                   datetime.now().strftime("%H:%M:%S"),
                                   queue_entry.get_type_str(),
                                   status,
                                   item_details,
                                   view_item)

    def add_history_entry(self, sample_name, date, time, entry_type,
                          status, entry_details, view_item=None):
        # At the top level insert date
        date_item = None
        for item_index in range(self.history_tree_widget.topLevelItemCount()):
            if self.history_tree_widget.topLevelItem(item_index).text(0) == date:
                date_item = self.history_tree_widget.topLevelItem(item_index)
                break
        if not date_item:
            date_item = QtImport.QTreeWidgetItem()
            date_item.setText(0, date)
            self.history_tree_widget.insertTopLevelItem(0, date_item)

        time_item = None
        for item_index in range(date_item.childCount()):
            if date_item.child(item_index).text(0) == time.split(":")[0] + "h":
                time_item = date_item.child(item_index)

        if not time_item:
            time_item = QtImport.QTreeWidgetItem()
            time_item.setText(0, time.split(":")[0] + "h")
            date_item.insertChild(0, time_item)

        entry_item = QtImport.QTreeWidgetItem()
        entry_item.setText(0, time)
        entry_item.setText(1, sample_name)
        entry_item.setText(2, entry_type)
        entry_item.setText(3, status)
        entry_item.setText(4, entry_details)

        if status == "Successful":
            entry_item.setBackground(3, QtImport.QBrush(Colors.LIGHT_GREEN))
        else:
            entry_item.setBackground(3, QtImport.QBrush(Colors.LIGHT_RED))

        time_item.insertChild(0, entry_item)

        for col in range(1, 4):
            self.history_tree_widget.resizeColumnToContents(col)
        """
        self.history_tree_widget.setItem(0, 4, QTableWidgetItem(entry_details))
        self.history_tree_widget.resizeRowsToContents()
        self.history_tree_widget.resizeColumnsToContents()
        self.history_tree_widget.setRowHeight(0, 17)
        self.history_tree_widget.setVerticalHeaderItem(\
             0, QTableWidgetItem(str(self.history_tree_widget.rowCount())))
        """
        self.item_history_list.append((sample_name, date, time, entry_type,
                                       status, entry_details))

    def queue_execution_completed(self, status):
        """Restores normal cursors, changes collect button
           Deselects all items and selects mounted sample
        """
        HWR.beamline.sample_view.set_cursor_busy(False)
        self.collecting = False
        self.collect_button.setText("Collect Queue")
        self.collect_button.setIcon(self.play_icon)
        self.continue_button.setEnabled(False)
        Colors.set_widget_color(
            self.collect_button,
            Colors.LIGHT_GREEN,
            QtImport.QPalette.Button)
        self.delete_button.setEnabled(True)
        self.enable_sample_changer_widget(True)
        # self.parent().enable_hutch_menu(True)
        # self.parent().enable_command_menu(True)
        # self.parent().enable_task_toolbox(True)

        self.sample_tree_widget.clearSelection()
        sample_item = self.get_mounted_sample_item()
        if sample_item is not None:
            sample_item.setSelected(True)
        self.set_sample_pin_icon()
        self.save_history_queue()

    def get_checked_items(self):
        """Returns all checked items"""
        checked_items = []
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()
        while item:
            if item.checkState(0) > 0 and not \
               item.isHidden():
                checked_items.append(item)
            it += 1
            item = it.value()
        return checked_items

    def get_collect_items(self):
        """Returns a list of all items to be collected
           Do not include samples without data collection(s)
        """
        checked_items = []
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()
        while item:
            append = False
            if item.checkState(0) > 0 and not item.isHidden():
                append = True
                if isinstance(item, queue_item.SampleQueueItem):
                    append = len(item.get_all_grand_children()) > 0
            if append:
                checked_items.append(item)
            it += 1
            item = it.value()
        return checked_items

    def copy_click(self, selected_items=None):
        """Copy item"""
        if not isinstance(selected_items, list):
            selected_items = self.get_selected_items()

        for item in selected_items:
            if type(item) not in (queue_item.BasketQueueItem,
                                  queue_item.SampleQueueItem,
                                  queue_item.DataCollectionGroupQueueItem):
                new_node = HWR.beamline.queue_model.copy_node(item.get_model())
                new_node.set_snapshot(HWR.beamline.sample_view.get_scene_snapshot())
                HWR.beamline.queue_model.add_child(
                    item.get_model().get_parent(), new_node)
        self.sample_tree_widget_selection()

    def delete_click(self, selected_items=None):
        """Deletes selected items"""
        children = []

        if not isinstance(selected_items, list):
            selected_items = self.get_selected_items()

        for item in selected_items:
            parent = item.parent()
            if item.deletable and parent:
                if not parent.isSelected() or (not parent.deletable):
                    self.tree_brick.show_sample_centring_tab()

                    HWR.beamline.queue_model.del_child(parent.get_model(),
                                                     item.get_model())
                    qe = item.get_queue_entry()
                    parent.get_queue_entry().dequeue(qe)
                    parent.takeChild(parent.indexOfChild(item))

                    if not parent.child(0):
                        parent.setOn(False)
            else:
                item.reset_style()

                for index in range(item.childCount()):
                    children.append(item.child(index))

        if children:
            self.delete_click(selected_items=children)

        self.check_for_path_collisions()
        self.set_first_element()
        self.toggle_collect_button_enabled()
        self.tree_brick.auto_save_queue()

    def set_first_element(self):
        """Selects first element from the tree"""
        selected_items = self.get_selected_items()
        if len(selected_items) == 0:
            it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
            #item = it.current()
            item = it.value()
            if item.get_model().free_pin_mode:
                self.sample_tree_widget.topLevelItem(0).setSelected(True)
                #self.sample_tree_widget.setSelected(self.sample_list_view.firstChild(), True)

    def down_click(self):
        """Moves tree item down"""
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, queue_item.QueueItem):
                if item.treeWidget().itemBelow(item) is not None:
                    item.move_item(item.treeWidget().itemBelow(item))
                    self.sample_tree_widget_selection()

    def previous_sibling(self, item):
        """Returns previous item"""
        if item.parent():
            first_child = item.parent().child(0)
        else:
            first_child = item.treeWidget().topLevelItem(0)

        if first_child is not item:
            sibling = first_child.treeWidget().itemBelow(first_child)
            #sibling = first_child.nextSibling()

            while sibling:
                if sibling is item:
                    return first_child
                # elif sibling.nextSibling() is item:
                elif first_child.treeWidget().itemBelow(first_child) is item:
                    return sibling
                else:
                    sibling = first_child.treeWidget().itemBelow(first_child)
                    #sibling = sibling.nextSibling()
        else:
            return None

    def up_click(self):
        """Move item one position up"""
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, queue_item.QueueItem):
                #older_sibling = self.previous_sibling(item)
                older_sibling = self.sample_tree_widget.itemAbove(item)
                if older_sibling:
                    older_sibling.move_item(item)
                    self.sample_tree_widget_selection()

    def samples_from_sc_content(self, sc_basket_content, sc_sample_content):
        """Initiates lists of baskets and samples"""
        basket_list = []
        sample_list = []
        for basket_info in sc_basket_content:
            basket = queue_model_objects.Basket()
            basket.init_from_sc_basket(basket_info, basket_info[2])
            basket_list.append(basket)
        for sample_info in sc_sample_content:
            sample = queue_model_objects.Sample()
            sample.init_from_sc_sample(sample_info)
            sample_list.append(sample)
        return basket_list, sample_list

    """
    def samples_from_plate_content(self, plate_row_content, plate_sample_content):
        row_list = []
        sample_list = []

        for row_info in plate_row_content:
            basket = queue_model_objects.Basket()
            basket.init_from_sc_basket(row_info, row_info[2])
            row_list.append(basket)
        for sample_info in plate_sample_content:
            sample = queue_model_objects.Sample()
            sample.init_from_sc_sample(sample_info)
            sample_list.append(sample)
        return row_list, sample_list
    """

    def samples_from_lims(self, lims_sample_list):
        """Sync samples with ispyb"""
        barcode_samples = {}
        location_samples = {}

        for lims_sample in lims_sample_list:
            sample = queue_model_objects.Sample()
            sample.init_from_lims_object(lims_sample)

            if sample.lims_code:
                barcode_samples[sample.lims_code] = sample

            if sample.lims_location:
                location_samples[sample.lims_location] = sample

        return (barcode_samples, location_samples)

    def enqueue_samples(self, sample_list):
        """Adds items to the queue"""
        for sample in sample_list:
            HWR.beamline.queue_model.add_child(HWR.beamline.queue_model.
                                             get_model_root(), sample)
            self.add_to_queue([sample], self.sample_tree_widget, False)

    def populate_free_pin(self, sample=None):
        """Populates manualy mounted sample"""
        HWR.beamline.queue_model.clear_model('free-pin')
        HWR.beamline.queue_model.select_model('free-pin')
        if sample is None:
            sample = queue_model_objects.Sample()
            sample.set_name('manually-mounted')
        sample.free_pin_mode = True
        HWR.beamline.queue_model.add_child(HWR.beamline.queue_model.get_model_root(),
                                         sample)
        self.set_sample_pin_icon()

    def populate_tree_widget(self, basket_list, sample_list, sample_changer_num):
        """Populates tree with samples from sample changer or plate"""
        # Make this better
        if sample_changer_num == 1:
            mode_str = "ispyb"
        else:
            mode_str = "plate"

        HWR.beamline.queue_manager.clear()
        HWR.beamline.queue_model.clear_model(mode_str)
        self.sample_tree_widget.clear()
        HWR.beamline.queue_model.select_model(mode_str)

        for basket_index, basket in enumerate(basket_list):
            HWR.beamline.queue_model.add_child(HWR.beamline.queue_model.get_model_root(), basket)
            basket.set_enabled(False)
            for sample in sample_list:
                if sample.location[0] == basket_index + 1:
                    basket.add_sample(sample)
                    HWR.beamline.queue_model.add_child(basket, sample)
                    sample.set_enabled(False)
        self.set_sample_pin_icon()

    def set_sample_pin_icon(self):
        """Updates sample icon"""
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if self.is_mounted_sample_item(item):
                item.setSelected(True)
                item.set_mounted_style(True)
                # self.sample_tree_widget.scrollTo(self.sample_tree_widget.\
                #     indexFromItem(item))
            elif isinstance(item, queue_item.SampleQueueItem):
                item.set_mounted_style(False)

            if isinstance(item, queue_item.SampleQueueItem):
                if item.get_model().lims_location != (None, None):
                    # if item.get_model().diffraction_plan is not None:
                    #    item.setIcon(0, self.ispyb_diff_plan_icon)
                    if not self.is_mounted_sample_item(item):
                        item.setIcon(0, self.ispyb_icon)
                    item.setText(0, item.get_model().get_display_name())
            elif isinstance(item, queue_item.BasketQueueItem):
                # pass
                item.setText(0, item.get_model().get_display_name())
                """
                do_it = True
                child_item = item.child(0)
                while child_item:
                    if child_item.child(0):
                        do_it = False
                        break
                    child_item = self.sample_tree_widget.itemBelow(child_item)
                if do_it:
                    item.setOn(False)
                """

            if item.has_star():
                item.setIcon(0, Icons.load_icon("star"))

            it += 1
            item = it.value()

    def update_basket_selection(self):
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if isinstance(item, queue_item.BasketQueueItem):
                item.setExpanded(item.get_model().get_is_present() == True)
                item.setDisabled(not item.get_model().get_is_present())
            it += 1
            item = it.value()

    def check_for_path_collisions(self):
        """Checks for path conflicts"""
        conflict = False
        it = QtImport.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if item.checkState(0) == QtImport.Qt.Checked:
                pt = item.get_model().get_path_template()

                if pt:
                    path_conflict = HWR.beamline.queue_model.\
                        check_for_path_collisions(pt)

                    if path_conflict:
                        conflict = True
                        item.setIcon(0, self.caution_icon)
                    else:
                        if item.has_star():
                            item.setIcon(0, self.star_icon)
                        else:
                            item.setIcon(0, QtImport.QIcon())

            it += 1
            item = it.value()

        return conflict

    def select_last_added_item(self):
        """Selects last added item"""
        if self.last_added_item:
            self.sample_tree_widget.clearSelection()
            self.last_added_item.setSelected(True)
            self.sample_tree_widget_selection()

    def hide_empty_baskets(self):
        """Hides empty baskets after the tree filtering"""
        self.item_iterator = QtImport.QTreeWidgetItemIterator(
            self.sample_tree_widget)
        item = self.item_iterator.value()
        while item:
            hide = True

            if type(item) in(queue_item.BasketQueueItem,
                             queue_item.DataCollectionGroupQueueItem):
                for index in range(item.childCount()):
                    if not item.child(index).isHidden():
                        hide = False
                        break
                if hide:
                    item.set_hidden(hide)

            self.item_iterator += 1
            item = self.item_iterator.value()

    def delete_empty_finished_items(self):
        """Deletes collected items"""
        self.item_iterator = QtImport.QTreeWidgetItemIterator(
            self.sample_tree_widget)
        item = self.item_iterator.value()
        while item:
            # if type(item) in(queue_item.BasketQueueItem,
            #                 queue_item.DataCollectionGroupQueueItem):
            #    for index in range(item.childCount()):
            #        if not item.child(index).isHidden():
            #            hide = False
            #            break
            #    item.setHidden(hide)
            self.item_iterator += 1
            item = self.item_iterator.value()

    def cut_item(self):
        """Cut selected item"""

        item = self.sample_tree_widget.currentItem()
        self.item_copy = (item.get_model(), True)
        self.delete_click([item])

    def copy_item(self):
        """Makes a copy of the selected item"""

        item = self.sample_tree_widget.currentItem()
        self.item_copy = (item.get_model(), False)

    def paste_item(self, new_node=None):
        """Paste item. If item was cut then remove item from clipboard"""

        for item in self.get_selected_items():
            parent_nodes = []
            if new_node is None:
                new_node = HWR.beamline.queue_model.copy_node(self.item_copy[0])
            else:
                # we have to update run number
                new_node.acquisitions[0].path_template.run_number = \
                    HWR.beamline.queue_model.get_next_run_number(
                    new_node.acquisitions[0].path_template)

            new_node.set_snapshot(HWR.beamline.sample_view.get_scene_snapshot())

            if isinstance(item, queue_item.DataCollectionQueueItem):
                parent_nodes = [item.get_model().get_parent()]
            elif isinstance(item, queue_item.DataCollectionGroupQueueItem):
                parent_nodes = [item.get_model()]
            elif isinstance(item, queue_item.SampleQueueItem):
                # If sample was selected then a new task group is created
                parent_nodes = [self.create_task_group(item.get_model())]
            elif isinstance(item, queue_item.BasketQueueItem):
                for sample in item.get_model().get_sample_list():
                    parent_nodes.append(self.create_task_group(sample))

            for parent_node in parent_nodes:
                HWR.beamline.queue_model.add_child(parent_node, new_node)
        self.sample_tree_widget_selection()

        if self.item_copy[1]:
            self.item_copy = None

    def save_item(self):
        """Saves a single item in a file"""

        filename = str(QtImport.QFileDialog.getSaveFileName(
            self, "Choose a filename to save selected item",
            os.environ["HOME"]))
        if not filename.endswith(".dat"):
            filename += ".dat"

        save_file = None
        try:
            save_file = open(filename, 'w')
            items_to_save = []
            for item in self.get_selected_items():
                items_to_save.append(item.get_model())
            save_file.write(jsonpickle.encode(items_to_save))
        except BaseException:
            logging.getLogger().exception("Cannot save file %s", filename)
            if save_file:
                save_file.close()

    def load_item(self):
        """Load item from a template saved in a file"""

        items_to_apply = self.get_selected_items()
        self.insert_item(apply_once=True)
        self.delete_click(items_to_apply)

    def insert_item(self, apply_once=False):
        """Inserts item from a file"""

        filename = str(QtImport.QFileDialog.getOpenFileName(self,
                                                            "Open file", os.environ["HOME"],
                                                            "Item file (*.dat)", "Choose a itemfile to open"))
        if len(filename) > 0:
            load_file = None
            try:
                load_file = open(filename, 'r')
                for item in jsonpickle.decode(load_file.read()):
                    self.item_copy = (item, True)
                    self.paste_item(item)
                    if apply_once:
                        break
            except BaseException:
                logging.getLogger().exception(
                    "Cannot insert an item from file %s", filename)
                if load_file:
                    load_file.close()

    def open_ispyb_link(self):
        selected_items = self.get_selected_items()
        if selected_items:
            item_model = selected_items[0].get_model().id
            if item_model:
                webbrowser.open("%s%d" %
                                (HWR.beamline.lims.get_dc_display_link(),
                                 item_model))

    def create_task_group(self, sample_item_model, group_name="Group"):
        """Creates empty task group"""
        task_group_node = queue_model_objects.TaskGroup()

        if self.item_copy:
            if isinstance(self.item_copy[0], queue_model_objects.DataCollection):
                if self.item_copy[0].is_helical():
                    group_name = "Helical"
                elif self.item_copy[0].is_mesh():
                    group_name = "Advanced"
                else:
                    group_name = "Standard"
            elif isinstance(self.item_copy[0], queue_model_objects.Characterisation):
                group_name = "Characterisation"
            elif isinstance(self.item_copy[0], queue_model_objects.EnergyScan):
                group_name = "Energy scan"
            elif isinstance(self.item_copy[0], queue_model_objects.XRFSpectrum):
                group_name = "XRF spectrum"
            elif isinstance(self.item_copy[0], queue_model_objects.XrayCentering):
                group_name = "Xray centering"

        task_group_node.set_name(group_name)
        num = sample_item_model.get_next_number_for_name(group_name)
        task_group_node.set_number(num)

        HWR.beamline.queue_model.add_child(sample_item_model, task_group_node)

        return task_group_node

    def save_queue_in_file(self):
        """Saves queue in the file"""
        filename = str(QtImport.QFileDialog.getSaveFileName(
            self, "Choose a filename to save selected item",
            os.environ["HOME"]))
        if not filename.endswith(".dat"):
            filename += ".dat"
        HWR.beamline.queue_model.save_queue(filename)

    def load_queue_from_file(self):
        """Loads queue from file"""
        filename = str(QtImport.QFileDialog.getOpenFileName(self,
                                                            "Open file", os.environ["HOME"],
                                                            "Item file (*.dat)", "Choose queue file to open"))
        if len(filename) > 0:
            self.sample_tree_widget.clear()
            loaded_model = HWR.beamline.queue_model.load_queue(filename,
                                                             HWR.beamline.sample_view.get_scene_snapshot())
            return loaded_model

    def save_history_queue(self):
        pass

    def save_history_in_file(self):
        filename = os.path.join(self.tree_brick.user_file_directory,
                                "queue_history.dat")
        save_file = None
        try:
            save_file = open(filename, 'w')
            #items_to_save = []
            # for item in self.item_history_list:
            #    items_to_save.append(item.get_model())
            # save_file.write(jsonpickle.encode(items_to_save))
            save_file.write(jsonpickle.encode(self.item_history_list))
        except BaseException:
            logging.getLogger().exception("Cannot save file %s", filename)
            if save_file:
                save_file.close()

    def load_history_queue_from_file(self):
        filename = os.path.join(self.tree_brick.user_file_directory,
                                "queue_history.dat")

        load_file = None
        try:
            load_file = open(filename, 'r')
            for item in jsonpickle.decode(load_file.read()):
                self.add_history_entry(*item)
        except BaseException:
            pass
        finally:
            if load_file:
                load_file.close()

    def undo_queue(self):
        """Undo last change"""
        raise NotImplementedError

    def redo_queue(self):
        """Redo last changed"""
        raise NotImplementedError

    def shape_created(self, shape, shape_type):
        if self.tree_brick.redis_client_hwobj is not None:
            self.tree_brick.redis_client_hwobj.save_graphics()

    def shape_deleted(self, shape, shape_type):
        if self.tree_brick.redis_client_hwobj is not None:
            self.tree_brick.redis_client_hwobj.save_graphics()

    def shape_changed(self, shape, shape_type):
        """Updates tree item if its related shape has changed"""
        self.item_iterator = QtImport.QTreeWidgetItemIterator(
            self.sample_tree_widget)
        item = self.item_iterator.value()
        while item:
            item_model = item.get_model()
            if shape_type == "Line" and \
               isinstance(item_model, queue_model_objects.DataCollection):
                if item_model.is_helical():
                    (cp_start, cp_end) = item_model.get_centred_positions()
                    item_model.set_centred_positions((cp_end, cp_start))
                    item.update_display_name()
            self.item_iterator += 1
            item = self.item_iterator.value()

    def sync_diffraction_plan(self):
        """Adds data collection items defined in ispyb diffraction plan"""
        for item in self.get_selected_items():
            if isinstance(item, queue_item.SampleQueueItem):
                if item.get_model().diffraction_plan is not None:
                    self.add_sample_diffraction_plan(item.get_model())
            elif isinstance(item, queue_item.BasketQueueItem):
                for sample in item.get_model().get_sample_list():
                    if sample.diffraction_plan is not None:
                        self.add_sample_diffraction_plan(sample)

    def add_sample_diffraction_plan(self, sample_model):
        """Adds diffraction plan defined in ispyb
           At first experimentKind is checked and related data collection
           queue entry is created.
        """
        # logging.getLogger("HWR").debug("Adding diffraction plan : %s",
        #                               str(sample_model.diffraction_plan))
        task_node = self.create_task_group(sample_model, "Diffraction plan")
        prefix = HWR.beamline.session.get_default_prefix(
            sample_model)
        snapshot = HWR.beamline.sample_view.get_scene_snapshot()

        if sample_model.diffraction_plan.experimentKind in ("OSC", "Default"):
            acq = queue_model_objects.Acquisition()

            # TODO create default_diffraction_plan_values
            acq.acquisition_parameters = HWR.beamline.\
                get_default_acquisition_parameters("default_acquisition_values")
            if hasattr(sample_model.diffraction_plan, "oscillationRange"):
                acq.acquisition_parameters.osc_range = \
                    sample_model.diffraction_plan.oscillationRange

            acq.acquisition_parameters.exp_time = 0.04
            if hasattr(sample_model.diffraction_plan, "exposureTime"):
                if sample_model.diffraction_plan.exposureTime > 0:
                    acq.acquisition_parameters.exp_time = \
                        sample_model.diffraction_plan.exposureTime

            acq.acquisition_parameters.centred_position.snapshot_image = snapshot
            path_template = HWR.beamline.get_default_path_template()
            path_template.base_prefix = prefix
            path_template.num_files = 1800
            path_template.reference_image_prefix = "plan"
            path_template.run_number = HWR.beamline.queue_model.\
                get_next_run_number(path_template)
            acq.path_template = path_template

            dc = queue_model_objects.DataCollection([acq],
                                                    sample_model.crystals[0])
            dc.set_name("OSC_" + str(sample_model.diffraction_plan.diffractionPlanId))
            HWR.beamline.queue_model.add_child(task_node, dc)

        self.sample_tree_widget_selection()
