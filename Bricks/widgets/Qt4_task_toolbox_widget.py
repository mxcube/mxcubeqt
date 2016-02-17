#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import Qt4_queue_item
import queue_model_objects_v1 as queue_model_objects
from queue_model_enumerables_v1 import EXPERIMENT_TYPE

from BlissFramework import Qt4_Icons
from widgets.Qt4_create_discrete_widget import CreateDiscreteWidget
from widgets.Qt4_create_helical_widget import CreateHelicalWidget
from widgets.Qt4_create_char_widget import CreateCharWidget
from widgets.Qt4_create_energy_scan_widget import CreateEnergyScanWidget
from widgets.Qt4_create_xrf_spectrum_widget import CreateXRFSpectrumWidget
from widgets.Qt4_create_advanced_widget import CreateAdvancedWidget


class TaskToolBoxWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "task_toolbox"):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName = name

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None

        # Internal variables --------------------------------------------------
        self.tree_brick = None
        self.previous_page_index = 0

        # Graphic elements ----------------------------------------------------
        self.method_group_box = QtGui.QGroupBox(" Collection method", self)
        font = self.method_group_box.font()
        font.setPointSize(10)
        self.method_group_box.setFont(font)
    
        self.tool_box = QtGui.QToolBox(self.method_group_box)
        self.tool_box.setObjectName("tool_box")
        self.tool_box.setFixedWidth(475)
        self.tool_box.setFont(font)
        
        self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete",)
        self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page")
        self.energy_scan_page = CreateEnergyScanWidget(self.tool_box, "energy_scan")
        self.xrf_spectrum_page = CreateXRFSpectrumWidget(self.tool_box, "xrf_spectrum")  
        self.advanced_page = CreateAdvancedWidget(self.tool_box, "advanced_scan")
        
        self.tool_box.addItem(self.discrete_page, "Standard Collection")
        self.tool_box.addItem(self.char_page, "Characterisation")
        self.tool_box.addItem(self.helical_page, "Helical Collection")
        self.tool_box.addItem(self.energy_scan_page, "Energy Scan")
        self.tool_box.addItem(self.xrf_spectrum_page, "XRF Spectrum")
        self.tool_box.addItem(self.advanced_page, "Advanced")

        self.button_box = QtGui.QWidget(self)
        self.create_task_button = QtGui.QPushButton("  Add to queue", self.button_box)
        self.create_task_button.setIcon(QtGui.QIcon(Qt4_Icons.load("add_row.png")))
        msg = "Add the collection method to the selected sample"
        self.create_task_button.setToolTip(msg)
        
        # Layout --------------------------------------------------------------
        _method_group_box_vlayout = QtGui.QVBoxLayout(self.method_group_box)
        _method_group_box_vlayout.addWidget(self.tool_box)
        _method_group_box_vlayout.setSpacing(0)
        _method_group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _button_box_hlayout = QtGui.QHBoxLayout(self.button_box)
        _button_box_hlayout.addStretch(0)
        _button_box_hlayout.addWidget(self.create_task_button)
        _button_box_hlayout.setSpacing(0)
        _button_box_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.method_group_box)
        #_main_vlayout.addStretch(0)  
        _main_vlayout.addWidget(self.button_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)


        # Qt signal/slot connections ------------------------------------------
        self.create_task_button.clicked.connect(self.create_task_button_click)
        self.tool_box.currentChanged.connect(self.current_page_changed)

        # Other ---------------------------------------------------------------   

    def set_tree_brick(self, brick):
        """
        Sets the tree brick of each page in the toolbox.
        """
        self.tree_brick = brick
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).set_tree_brick(brick)

    def set_beamline_setup(self, beamline_setup_hwobj):
        self._beamline_setup_hwobj = beamline_setup_hwobj
        for i in range(0, self.tool_box.count()):
            self.tool_box.widget(i).set_beamline_setup(beamline_setup_hwobj)

        self.graphics_manager_hwobj = beamline_setup_hwobj.shape_history_hwobj
        self.energy_scan_page.set_energy_scan_hwobj(\
             beamline_setup_hwobj.energyscan_hwobj)

        # Remove energy scan page from non tunable wavelentgh beamlines
        if not beamline_setup_hwobj.tunable_wavelength():
            self.tool_box.removeItem(self.tool_box.indexOf(self.energy_scan_page))
            self.energy_scan_page.hide()
            logging.getLogger("user_level_log").info("Energy scan task not available")
        
        has_xrf_spectrum = False
        if hasattr(beamline_setup_hwobj, 'xrf_spectrum_hwobj'):
            if beamline_setup_hwobj.xrf_spectrum_hwobj:
                has_xrf_spectrum = True

        if not has_xrf_spectrum:
            self.tool_box.removeItem(self.tool_box.indexOf(self.xrf_spectrum_page))
            self.xrf_spectrum_page.hide()
            logging.getLogger("user_level_log").info("XRF spectrum task not available")

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
        tree_items =  self.tree_brick.get_selected_items()

        if len(tree_items) > 0:        
            tree_item = tree_items[0]

            # Get the directory form the previous page and update 
            # the new page with the direcotry and run_number from the old.
            # IF sample, basket group selected.
            if type(tree_item) in (Qt4_queue_item.DataCollectionGroupQueueItem, \
                                  Qt4_queue_item.SampleQueueItem, \
                                  Qt4_queue_item.BasketQueueItem):
                new_pt = self.tool_box.widget(page_index)._path_template
                previous_pt = self.tool_box.widget(self.previous_page_index)._path_template
                new_pt.directory = previous_pt.directory
                new_pt.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                    get_next_run_number(new_pt)
            elif isinstance(tree_item, Qt4_queue_item.DataCollectionQueueItem):
                data_collection = tree_item.get_model()
                if data_collection.experiment_type == EXPERIMENT_TYPE.HELICAL:
                    if self.tool_box.currentWidget() == self.helical_page:
                        self.create_task_button.setEnabled(True)
                elif self.tool_box.currentWidget() == self.discrete_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, Qt4_queue_item.CharacterisationQueueItem):
                if self.tool_box.currentWidget() == self.char_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, Qt4_queue_item.EnergyScanQueueItem):
                if self.tool_box.currentWidget() == self.energy_scan_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, Qt4_queue_item.XRFSpectrumQueueItem):
                if self.tool_box.currentWidget() == self.xrf_spectrum_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, Qt4_queue_item.GenericWorkflowQueueItem):
                if self.tool_box.currentWidget() == self.workflow_page:
                    self.create_task_button.setEnabled(True)
            elif isinstance(tree_item, Qt4_queue_item.AdvancedQueueItem):
                if self.tool_box.currentWidget() == self.advanced_page:
                    self.create_task_button.setEnabled(True)

            self.tool_box.widget(page_index).selection_changed(tree_items)
            self.previous_page_index = page_index

    def selection_changed(self, items):
        """
        Called by the parent widget when selection in the tree changes.
        """
        if len(items) == 1:
            if isinstance(items[0], Qt4_queue_item.DataCollectionGroupQueueItem):
                self.create_task_button.setEnabled(False)
            else:
                self.create_task_button.setEnabled(True)
            if isinstance(items[0], Qt4_queue_item.DataCollectionQueueItem):
                data_collection = items[0].get_model()
                if data_collection.experiment_type == EXPERIMENT_TYPE.HELICAL:
                    self.tool_box.setCurrentWidget(self.helical_page)
                else:
                    self.tool_box.setCurrentWidget(self.discrete_page)
            elif isinstance(items[0], Qt4_queue_item.CharacterisationQueueItem):
                self.tool_box.setCurrentWidget(self.char_page)
            elif isinstance(items[0], Qt4_queue_item.EnergyScanQueueItem):
                self.tool_box.setCurrentWidget(self.energy_scan_page)
            elif isinstance(items[0], Qt4_queue_item.XRFSpectrumQueueItem):
                self.tool_box.setCurrentWidget(self.xrf_spectrum_page)
            elif isinstance(items[0], Qt4_queue_item.GenericWorkflowQueueItem):
                self.tool_box.setCurrentWidget(self.workflow_page)
            elif isinstance(items[0], Qt4_queue_item.AdvancedQueueItem):
                self.tool_box.setCurrentWidget(self.advanced_page)

        current_page = self.tool_box.currentWidget()
        current_page.selection_changed(items)

    def create_task_button_click(self):
        if self.tool_box.currentWidget().approve_creation():
            items = self.tree_brick.get_selected_items()

            if not items:
                logging.getLogger("user_level_log").\
                    warning("Select the sample or group you "\
                            "would like to add to.")
            else:
                for item in items:
                    shapes = self.graphics_manager_hwobj.get_selected_points()
                    task_model = item.get_model()

                    # Create a new group if sample is selected
                    if isinstance(task_model, queue_model_objects.Sample):
                        task_model = self.create_task_group(task_model)
                        if self.tool_box.currentWidget() in (self.discrete_page, 
                           self.char_page, self.energy_scan_page, 
                           self.xrf_spectrum_page) and len(shapes):
                            #This could be done in more nicer way...
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                            self.create_task(task_model)
                    elif isinstance(task_model, queue_model_objects.Basket):
                        for sample_node in task_model.get_sample_list():
                            child_task_model = self.create_task_group(sample_node)
                            if self.tool_box.currentWidget() in (self.discrete_page,
                               self.char_page, self.energy_scan_page, 
                               self.xrf_spectrum_page) and len(shapes):
                                for shape in shapes:
                                    self.create_task(child_task_model, shape)
                            else:
                                self.create_task(child_task_model)
                    else:
                        if self.tool_box.currentWidget() in (self.discrete_page,
                           self.char_page, self.energy_scan_page, 
                           self.xrf_spectrum_page) and len(shapes):
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                             self.create_task(task_model)
                self.tree_brick.select_last_added_item()

            self.tool_box.currentWidget().update_selection()

    def create_task_group(self, task_model):
        group_task_node = queue_model_objects.TaskGroup()
        current_item = self.tool_box.currentWidget()

        group_name = current_item._task_node_name
        group_task_node.set_name(group_name)
        num = task_model.get_next_number_for_name(group_name)
        group_task_node.set_number(num)

        self.tree_brick.queue_model_hwobj.\
            add_child(task_model, group_task_node)

        return group_task_node


    def create_task(self, task_node, shape = None):
        # Selected item is a task group
        if isinstance(task_node, queue_model_objects.TaskGroup):
            sample = task_node.get_parent()
            task_list = self.tool_box.currentWidget().create_task(sample, shape)

            for child_task_node in task_list:
                self.tree_brick.queue_model_hwobj.add_child(task_node, child_task_node)
        # The selected item is a task, make a copy.
        else:
            new_node = self.tree_brick.queue_model_hwobj.copy_node(task_node)
            self.tree_brick.queue_model_hwobj.add_child(task_node.get_parent(), new_node)
