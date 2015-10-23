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
#
#  Please user PEP 0008 -- "Style Guide for Python Code" to format code
#  https://www.python.org/dev/peps/pep-0008/

import logging
import gevent
from collections import namedtuple

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import Qt4_queue_item
import queue_entry
import queue_model_objects_v1 as queue_model_objects

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_confirm_dialog import ConfirmDialog
from queue_model_enumerables_v1 import CENTRING_METHOD

SCFilterOptions = namedtuple('SCFilterOptions', 
                             ['FREE_PIN',
                              'SAMPLE_CHANGER_ONE', 
                              'SAMPLE_CHANGER_TWO', 
                              'MOUNTED_SAMPLE']) 

SC_FILTER_OPTIONS = SCFilterOptions(0, 1, 2, 3)


class DataCollectTree(QtGui.QWidget):
    """
    Descript. :
    """ 

    def __init__(self, parent = None, name = "data_collect", 
                 selection_changed = None):
        """
        Descript. :
        """
 
        QtGui.QWidget.__init__(self, parent)

        self.setObjectName(name)

        # Hardware objects ----------------------------------------------------
        self.queue_hwobj = None
        self.queue_model_hwobj = None
        self.beamline_setup_hwobj = None
        self.active_sample_changer_hwobj = None

        # Internal values -----------------------------------------------------
        self.collecting = False
        self.sample_mount_method = 0
        self.centring_method = 0
        self.sample_centring_result = gevent.event.AsyncResult()
        self.tree_brick = self.parent()
        self.sample_item_list = []
        self.collect_tree_task = None
        self.user_stopped = False
        
        self.selection_changed_cb = None
        self.collect_stop_cb = None
        #self.clear_centred_positions_cb = None
        self.run_cb = None

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.confirm_dialog = ConfirmDialog(self, 'Confirm Dialog')
        self.confirm_dialog.setModal(True)

        self.pin_pixmap = Qt4_Icons.load("sample_axis.png")
        self.task_pixmap = Qt4_Icons.load("task.png")
        self.play_pixmap = Qt4_Icons.load("VCRPlay.png")
        self.stop_pixmap = Qt4_Icons.load("Stop.png")
        self.up_pixmap = Qt4_Icons.load("Up2.png")
        self.down_pixmap = Qt4_Icons.load("Down2.png")
        self.delete_pixmap = Qt4_Icons.load("bin_small.png")
        self.ispyb_pixmap = Qt4_Icons.load("SampleChanger2.png")
        self.caution_pixmap = Qt4_Icons.load("Caution2.png")
        
        self.button_widget = QtGui.QWidget(self)                
        self.up_button = QtGui.QPushButton(self.button_widget)
        self.up_button.setIcon(QtGui.QIcon(self.up_pixmap))
        self.up_button.setFixedHeight(25)
        self.down_button = QtGui.QPushButton(self.button_widget)
        self.down_button.setIcon(QtGui.QIcon(self.down_pixmap))
        self.down_button.setFixedHeight(25)

        self.delete_button = QtGui.QPushButton(self.button_widget)
        self.delete_button.setIcon(QtGui.QIcon(self.delete_pixmap))
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip("Delete highlighted queue entries")

        self.collect_button = QtGui.QPushButton(self.button_widget)
        self.collect_button.setText("Collect Queue")
        self.collect_button.setFixedWidth(125)
        self.collect_button.setIcon(QtGui.QIcon(self.play_pixmap))
        Qt4_widget_colors.set_widget_color(self.collect_button, 
            Qt4_widget_colors.LIGHT_GREEN)

        self.continue_button = QtGui.QPushButton(self.button_widget)
        self.continue_button.setText('Pause')
        self.continue_button.setEnabled(True)
        self.continue_button.setFixedWidth(75)
        self.continue_button.setToolTip("Pause after current data collection")

        self.sample_tree_widget = QtGui.QTreeWidget(self)

        # Layout --------------------------------------------------------------
        button_widget_grid_layout = QtGui.QGridLayout(self.button_widget) 
        button_widget_grid_layout.addWidget(self.up_button, 0, 0)
        button_widget_grid_layout.addWidget(self.down_button, 0, 1)
        button_widget_grid_layout.addWidget(self.collect_button, 1, 0, 1, 2)
        button_widget_grid_layout.addWidget(self.delete_button, 0, 3)
        button_widget_grid_layout.addWidget(self.continue_button, 1, 3)
        button_widget_grid_layout.setColumnStretch(2, 1)
        button_widget_grid_layout.setContentsMargins(0, 0, 0, 0)
        button_widget_grid_layout.setSpacing(1)
        
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addWidget(self.sample_tree_widget)
        main_layout.addWidget(self.button_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(1) 

        # SizePolicies --------------------------------------------------------
        self.sample_tree_widget.setSizePolicy(QtGui.QSizePolicy(\
             QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        # Qt signal/slot connections ------------------------------------------
        self.up_button.clicked.connect(self.up_click)
        self.down_button.clicked.connect(self.down_click)
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

        # Other ---------------------------------------------------------------    
        self.sample_tree_widget.setColumnCount(2)
        self.sample_tree_widget.setColumnWidth(0, 250)
        self.sample_tree_widget.header().setDefaultSectionSize(250)
        self.sample_tree_widget.header().hide()
        self.sample_tree_widget.setRootIsDecorated(1)
        self.sample_tree_widget.setCurrentItem(self.sample_tree_widget.topLevelItem(0))
        self.sample_tree_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setAttribute(QtCore.Qt.WA_WState_Polished)      
        self.sample_tree_widget.viewport().installEventFilter(self)
        self.collect_button.setDisabled(True)

    def eventFilter(self, _object, event):
        """
        Descript. :
        """
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.show_details()
            return True
        else:
            return False

    def enable_collect(self, state):
        """
        Descript. :
        """
        self.sample_tree_widget.setDisabled(not state)
        self.collect_button.setDisabled(not state)
        self.up_button.setDisabled(not state)
        self.down_button.setDisabled(not state)
        self.delete_button.setDisabled(not state)

    def show_context_menu(self, context_menu_event):
        """
        Descript. :
        """
        menu = QtGui.QMenu(self.sample_tree_widget)
        item = self.sample_tree_widget.currentItem()

        if item:
            menu.addAction("Rename", self.rename_treewidget_item)
            if isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                menu.addSeparator()
                menu.addAction("Remove", self.delete_click)
            elif isinstance(item, Qt4_queue_item.SampleQueueItem):
                if not item.get_model().free_pin_mode:
                    if self.beamline_setup_hwobj.diffractometer_hwobj.in_plate_mode():
                        self.plate_sample_to_mount = item
                        menu.addAction("Move", self.mount_sample)
                    else:
                        if self.is_mounted_sample_item(item):
                            menu.addAction("Un-Mount", self.unmount_sample)
                        else:
                            menu.addAction("Mount", self.mount_sample)

                menu.addSeparator()
                menu.addAction("Details", self.show_details)
            else:
                menu.addSeparator()
                menu.addAction("Remove", self.delete_click)
                menu.addSeparator()
                menu.addAction("Details", self.show_details)
            menu.popup(QtGui.QCursor.pos())

        
    def item_double_click(self):
        """
        Descript. :
        """
        self.show_details()

    def item_click(self):
        """
        Descript. :
        """
        self.check_for_path_collisions()

    def item_changed(self, item, column):
        """
        Descript. : As there is no signal when item is checked/unchecked
                    it is necessary to update item based on QTreeWidget
                    signal itemChanged. 
                    Item check state is updated when checkbox is toggled
                    (to avoid update when text is changed)                    
        """
        if item.checkState(0) != item.get_previous_check_state():
            item.update_check_state()        

    def context_collect_item(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        
        if len(items) == 1:
            item = items[0]
        
            # Turn this item on (check it), incase its not already checked.
            if item.state() == 0:
                item.setOn(True)
            
            self.collect_items(items)

    def show_details(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        if len(items) == 1:
            item = items[0]
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.tree_brick.show_sample_tab(item)
            elif isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                if item.get_model().is_mesh_scan():
                    self.tree_brick.show_advanced_scan_tab(item)
                else:
                    self.tree_brick.show_datacollection_tab(item)
            elif isinstance(item, Qt4_queue_item.CharacterisationQueueItem):
                self.tree_brick.show_char_parameters_tab(item)
            elif isinstance(item, Qt4_queue_item.EnergyScanQueueItem):
                self.tree_brick.show_energy_scan_tab(item)
	    elif isinstance(item, Qt4_queue_item.XRFScanQueueItem):
                self.tree_brick.show_xrf_scan_tab(item)
            elif isinstance(item, Qt4_queue_item.GenericWorkflowQueueItem):
                self.tree_brick.show_workflow_tab(item)
        #elif len(items) == 0:
        #    self.tree_brick.show_sample_tab()

    def rename_treewidget_item(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        if len(items) == 1:
            items[0].setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled |
                              QtCore.Qt.ItemIsEditable)
            self.sample_tree_widget.editItem(items[0])
            items[0].setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
            items[0].get_model().set_name(items[0].text(0))

    def mount_sample(self):
        """
        Descript. :
        """
        self.enable_collect(False)
        gevent.spawn(self.mount_sample_task)

    def mount_sample_task(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        
        if len(items) == 1:
            if not items[0].get_model().free_pin_mode:
                self.sample_centring_result = gevent.event.AsyncResult()
                try:
                    queue_entry.mount_sample(self.beamline_setup_hwobj, items[0],
                                             items[0].get_model(), self.centring_done,
                                             self.sample_centring_result)
                except Exception as e:
                    items[0].setText(1, "Error loading")
                    msg = "Error loading sample, please check" +\
                          " sample changer: " + e.message
                    logging.getLogger("user_level_log").error(msg)
                finally:
                    self.enable_collect(True)
            else:
                logging.getLogger("user_level_log").\
                  info('Its not possible to mount samples in free pin mode')

    def centring_done(self, success, centring_info):
        """
        Descript. :
        """
        if success:
            self.sample_centring_result.set(centring_info)
        else:
            msg = "Loop centring failed or was cancelled, " +\
                  "please continue manually."
            logging.getLogger("user_level_log").warning(msg)

    def unmount_sample(self):
        """
        Descript. :
        """
        gevent.spawn(self.unmount_sample_task)

    def unmount_sample_task(self):
        """
        Descript. :
        """
        items = self.get_selected_items()

        if len(items) == 1:
            self.beamline_setup_hwobj.shape_history_hwobj.clear_all()
            logging.getLogger("user_level_log").\
                info("All centred positions associated with this " + \
                     "sample will be lost.")

            location = items[0].get_model().location

            if hasattr(self.active_sample_changer_hwobj, '__TYPE__')\
               and (self.active_sample_changer_hwobj.__TYPE__ == 'CATS'):
                self.active_sample_changer_hwobj.unload(wait=True)
            else:
                self.active_sample_changer_hwobj.\
                    unload(22, sample_location = location, wait = False)

            items[0].setOn(False)
            items[0].set_mounted_style(False)

    def sample_tree_widget_selection(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        if len(items) == 1:
            item = items[0]
            
        if len(items) > 1:
            for item in items:
                if isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem) or \
                       isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                    self.delete_button.setDisabled(False)
                    break

        self.selection_changed_cb(items)        
        #checked_items = self.get_checked_items()
        #self.collect_button.setDisabled(len(checked_items) == 0)
        #self.set_first_element()

    def add_empty_task_node(self):
        """
        Descript. :
        """
        samples = self.get_selected_samples()
        task_node = queue_model_objects.TaskGroup()
        task_node.set_name('Collection group')
        Qt4_queue_item.DataCollectionGroupQueueItem(samples[0], 
                                                samples[0].lastItem(),
                                                task_node.get_display_name())

    def get_item_by_model(self, parent_node):
        """
        Descript. :
        """
        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()
    
        while item:
            if item.get_model() is parent_node:
                return item

            it += 1
            item = it.value()

        return self.sample_tree_widget

    def last_top_level_item(self):
        """
        Descript. :
        """
        last_child_index = self.sample_tree_widget.topLevelItemCount() - 1
        return self.sample_tree_widget.topLevelItem(last_child_index) 

    def add_to_view(self, parent, task):
        """
        Descript. : Adds queue element to the tree. After element has been
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
        
        cls = Qt4_queue_item.MODEL_VIEW_MAPPINGS[task.__class__]

        view_item = cls(parent_tree_item, last_item, task.get_display_name())

        if isinstance(task, queue_model_objects.Basket):
            view_item.setExpanded(task.get_is_present() == True)
        else:
            view_item.setExpanded(True) 

        self.queue_model_hwobj.view_created(view_item, task)
        self.collect_button.setDisabled(False)

    def get_selected_items(self):
        """
        Descript. :
        """
        return self.sample_tree_widget.selectedItems()

    def get_selected_samples(self):
        """
        Descript. :
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item,  Qt4_queue_item.SampleQueueItem):
               res_list.append(item)
        return res_list
    
    def get_selected_tasks(self):
        """
        Descript. :
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item,  Qt4_queue_item.TaskQueueItem):
               res_list.append(item)
        return res_list

    def get_selected_dcs(self):
        """
        Descript. :
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item,  Qt4_queue_item.DataCollectionQueueItem):
               res_list.append(item)
        return res_list

    def get_selected_task_nodes(self):
        """
        Descript. :
        """
        res_list = []
        for item in self.get_selected_items():
            if isinstance(item,  Qt4_queue_item.DataCollectionGroupQueueItem):
               res_list.append(item)
        return res_list

    def is_sample_selected(self):
        """
        Descript. :
        """
        items = self.get_selected_items()
        
        for item in items:
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                return True

        return False

    def filter_sample_list(self, option):
        """
        Descript. :
        """
        self.sample_tree_widget.clearSelection()
        self.beamline_setup_hwobj.set_plate_mode(False)
        self.confirm_dialog.set_plate_mode(False)       
        self.sample_mount_method = option
        if option == SC_FILTER_OPTIONS.SAMPLE_CHANGER_ONE:
            self.sample_tree_widget.clear()
            self.queue_model_hwobj.select_model('sc_one')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.SAMPLE_CHANGER_TWO:
            self.sample_tree_widget.clear()
            self.queue_model_hwobj.select_model('sc_two')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.MOUNTED_SAMPLE:
            loaded_sample_loc = None
            try:
                loaded_sample = self.active_sample_changer_hwobj.\
                                 getLoadedSample()
                loaded_sample_loc = loaded_sample.getCoords()
            except:
                loaded_sample_loc = None

            it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
            item = it.value()
        
            while item:
                if isinstance(item, Qt4_queue_item.SampleQueueItem):
                    if item.get_model().location == loaded_sample_loc:
                        item.setSelected(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)

                it += 1
                item = it.value()

        elif option == SC_FILTER_OPTIONS.FREE_PIN:
            self.sample_tree_widget.clear()
            self.queue_model_hwobj.select_model('free-pin')
            self.set_sample_pin_icon()
        self.sample_tree_widget_selection()
        
    def set_centring_method(self, method_number):       
        """
        Descript. :
        """
        self.centring_method = method_number

        try:
            dm = self.beamline_setup_hwobj.diffractometer_hwobj
        
            if self.centring_method == CENTRING_METHOD.FULLY_AUTOMATIC:
                dm.user_confirms_centring = False
            else:
                dm.user_confirms_centring = True
        except AttributeError:
            #beamline_setup_hwobj not set when method called
            pass

    def continue_button_click(self):
        """
        Descript. :
        """
        if self.queue_hwobj.is_executing():
            if not self.queue_hwobj.is_paused():
                self.queue_hwobj.set_pause(True)
            else:
                self.queue_hwobj.set_pause(False)

    def queue_paused_handler(self, state):
        """
        Descript. :
        """
        if state:
            self.parent().enable_hutch_menu(True)
            self.parent().enable_command_menu(True)
            self.parent().enable_task_toolbox(True)
            self.continue_button.setText('Continue')
            Qt4_widget_colors.set_widget_color(self.continue_button, 
                                               Qt4_widget_colors.LIGHT_YELLOW, 
                                               QtGui.QPalette.Button)
        else:
            self.parent().enable_hutch_menu(False)
            self.parent().enable_command_menu(False)
            self.parent().enable_task_toolbox(False)
            self.continue_button.setText('Pause')
            Qt4_widget_colors.set_widget_color(
                              self.continue_button, 
                              Qt4_widget_colors.BUTTON_ORIGINAL, 
                              QtGui.QPalette.Button)

    def collect_stop_toggle(self):
        """
        Descript. :
        """
        checked_items = self.get_checked_items()
        self.queue_hwobj.disable(False)

        path_conflict = self.check_for_path_collisions()     

        if path_conflict:
            self.queue_hwobj.disable(True)
        
        if self.queue_hwobj.is_disabled():
            logging.getLogger("user_level_log").\
                error('Can not start collect, see the tasks marked' +\
                      ' in the tree and solve the prorblems.')
            
        elif not self.collecting:
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

                QtGui.QMessageBox.information(self,"Data collection",
                                              message, "OK")
        else:
            self.stop_collection()

    def enable_sample_changer_widget(self, state):
        """
        Descript. :
        """
        self.parent().sample_changer_widget.synch_combo.setEnabled(state)
        self.parent().sample_changer_widget.centring_cbox.setEnabled(state)
        self.parent().sample_changer_widget.filter_cbox.setEnabled(state)

    def is_mounted_sample_item(self, item):
        """
        Descript. :
        """
        result = False

        if isinstance(item, Qt4_queue_item.SampleQueueItem):
           if item.get_model().free_pin_mode == True:
               result = True
           elif self.active_sample_changer_hwobj is not None:
               if not self.active_sample_changer_hwobj.hasLoadedSample():
                   result = False
               elif item.get_model().location == self.active_sample_changer_hwobj.getLoadedSample().getCoords():
                   result = True
        return result

    def collect_items(self, items = [], checked_items = []):
        """
        Descript. :
        """
        self.beamline_setup_hwobj.shape_history_hwobj.de_select_all()
        for item in checked_items:
            # update the run-number text incase of re-collect
            #item.setText(0, item.get_model().get_name())

            #Clear status
            item.setText(1, "")
            item.reset_style()
        
        self.user_stopped = False
        self.delete_button.setEnabled(False)
        self.enable_sample_changer_widget(False)
        self.collecting = True
        self.collect_button.setText(" Stop   ")
        Qt4_widget_colors.set_widget_color(
                          self.collect_button, 
                          Qt4_widget_colors.LIGHT_RED,
                          QtGui.QPalette.Button)
        self.collect_button.setIcon(QtGui.QIcon(self.stop_pixmap))
        self.parent().enable_hutch_menu(False)
        self.run_cb()

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        try:
            self.queue_hwobj.execute()
        except Exception, e:
            raise e
        
    def stop_collection(self):
        """
        Descript. :
        """
        QtGui.QApplication.restoreOverrideCursor()
        self.queue_hwobj.stop()
        self.queue_stop_handler()

    def queue_stop_handler(self, status = None):
        """
        Descript. :
        """
        QtGui.QApplication.restoreOverrideCursor()
        self.user_stopped = True
        self.queue_execution_completed(None)
               
    def queue_execution_completed(self, status):
        """
        Descript. :
        """
        QtGui.QApplication.restoreOverrideCursor() 
        self.collecting = False
        self.collect_button.setText("Collect Queue")
        self.collect_button.setIcon(QtGui.QIcon(self.play_pixmap))
        Qt4_widget_colors.set_widget_color(
                          self.collect_button,
                          Qt4_widget_colors.LIGHT_GREEN,
                          QtGui.QPalette.Button)
        self.delete_button.setEnabled(True)
        self.enable_sample_changer_widget(True)
        self.parent().enable_hutch_menu(True)
        self.parent().enable_command_menu(True)
        self.parent().enable_task_toolbox(True)
        self.set_sample_pin_icon()

    def get_checked_items(self):
        """
        Descript. :
        """
        checked_items = []
        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()
        while item: 
            if item.checkState(0) > 0:
               checked_items.append(item)   
            it += 1
            item = it.value()
        return checked_items
 
    def delete_click(self, selected_items = None):
        """
        Descript. :
        """
        children = []

        if not isinstance(selected_items, list):
            selected_items = self.get_selected_items()

        for item in selected_items:
            parent = item.parent()
            if item.deletable:
                if not parent.isSelected() or (not parent.deletable):
                    self.tree_brick.show_sample_centring_tab()

                    self.queue_model_hwobj.del_child(parent.get_model(),
                                                     item.get_model())
                    qe = item.get_queue_entry()
                    parent.get_queue_entry().dequeue(qe)
                    parent.takeChild(parent.indexOfChild(item))

                    if not parent.child(0):
                        parent.setOn(False)
            else:
                item.reset_style()
                #child = item.firstChild() 
                child = item.child(0)

                while child: 
                    children.append(child)
                    #child = child.nextSibling()
                    child = child.treeWidget().itemBelow(child)

        if children:
            self.delete_click(selected_items = children)

        self.check_for_path_collisions()

    def set_first_element(self):
        """
        Descript. :
        """
        selected_items = self.get_selected_items()
        if len(selected_items) == 0:        
            it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
            #item = it.current()
            item = it.value()
            if item.get_model().free_pin_mode:
                self.sample_tree_widget.topLevelItem(0).setSelected(True)
                #self.sample_tree_widget.setSelected(self.sample_list_view.firstChild(), True)

    def down_click(self):
        """
        Descript. :
        """
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, Qt4_queue_item.QueueItem):
                if item.treeWidget().itemBelow(item) is not None:
                    item.move_item(item.treeWidget().itemBelow(item))

    def previous_sibling(self, item):
        """
        Descript. :
        """
        if item.parent():
            first_child = item.parent().child(0)
        else:
            first_child = item.treeWidget().topLevelItem(0) 

        if first_child is not item :
            sibling = first_child.treeWidget().itemBelow(first_child) 
            #sibling = first_child.nextSibling()   
        
            while sibling:           
                if sibling is item :
                    return first_child
                #elif sibling.nextSibling() is item:
                elif first_child.treeWidget().itemBelow(first_child) is item:
                    return sibling
                else:
                    sibling = first_child.treeWidget().itemBelow(first_child)
                    #sibling = sibling.nextSibling()
        else :
            return None
        
    def up_click(self):
        """
        Descript. :
        """
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, Qt4_queue_item.QueueItem): 
                older_sibling = self.previous_sibling(item)
                if older_sibling :
                    older_sibling.move_item(item)

    def samples_from_sc_content(self, sc_basket_content, sc_sample_content):
        """
        Descript. :
        """
        basket_list = []
        sample_list = []
        for basket_info in sc_basket_content:
            basket = queue_model_objects.Basket()
            basket.init_from_sc_basket(basket_info)
            basket_list.append(basket)
        for sample_info in sc_sample_content:
            sample = queue_model_objects.Sample()
            sample.init_from_sc_sample(sample_info)
            sample_list.append(sample)
        return basket_list, sample_list

    def samples_from_lims(self, lims_sample_list):
        """
        Descript. :
        """
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
        """
        Descript. :
        """
        for sample in sample_list:
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
            self.add_to_queue([sample], self.sample_tree_widget, False)

    def populate_free_pin(self):
        """
        Descript. :
        """
        self.queue_model_hwobj.clear_model('free-pin')
        self.queue_model_hwobj.select_model('free-pin')
        sample = queue_model_objects.Sample()
        sample.free_pin_mode = True
        sample.set_name('manually-mounted')
        self.queue_model_hwobj.add_child(self.queue_model_hwobj.get_model_root(),
                                         sample)

    def populate_tree_widget(self, basket_list, sample_list, sample_changer_num):   
        """
        Descript. :
        """
        #Make this better
        if sample_changer_num == 1:
            mode_str = "sc_one"
        else:
            mode_str = "sc_two" 
        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model(mode_str)
        self.sample_tree_widget.clear()
        self.queue_model_hwobj.select_model(mode_str)
        for basket in basket_list:
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), basket)
            basket.set_enabled(False)
            for sample in sample_list:
                 if sample.location[0] == basket.get_location():
                     self.queue_model_hwobj.add_child(basket, sample)
                     sample.set_enabled(False)
        #self.sample_tree_widget 
        self.set_sample_pin_icon()
    
    def set_sample_pin_icon(self):
        """
        Descript. :
        """
        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if self.is_mounted_sample_item(item):
                item.setSelected(True)
                item.set_mounted_style(True)
                #self.sample_tree_widget_selection()
                #self.sample_tree_widget_selection()
            elif isinstance(item, Qt4_queue_item.SampleQueueItem):
                item.set_mounted_style(False)
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                if item.get_model().lims_location != (None, None):
                    item.setIcon(0, QtGui.QIcon(self.ispyb_pixmap))
                    item.setText(0, item.get_model().loc_str + ' - ' \
                                 + item.get_model().get_display_name())
            elif isinstance(item, Qt4_queue_item.BasketQueueItem):
                #pass
                item.setText(0, item.get_model().get_display_name())
                do_it = True
                child_item = item.child(0)
                while child_item:
                    if child_item.child(0):
                        do_it = False
                        break
                    child_item = self.sample_tree_widget.itemBelow(child_item)
                    #child_item = child_item.ibling()
                if do_it:
                    item.setOn(False)        
                #item.setVisible(item.get_model().get_is_present()) 
            it += 1
            item = it.value()

    def check_for_path_collisions(self):
        """
        Descript. :
        """
        conflict = False
        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.value()

        while item:
            if item.checkState(0) == QtCore.Qt.Checked:
                pt = item.get_model().get_path_template()
                
                if pt:
                     path_conflict = self.queue_model_hwobj.\
                                check_for_path_collisions(pt)

                     if path_conflict:
                         conflict = True
                         item.setIcon(0, QtGui.QIcon(self.caution_pixmap))
                     else:
                         item.setIcon(0, QtGui.QIcon())
                         
            it += 1
            item = it.value()

        return conflict
