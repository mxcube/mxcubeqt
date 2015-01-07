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
from widgets.Qt4_confirm_dialog import Qt4_ConfirmDialog
from queue_model_enumerables_v1 import CENTRING_METHOD

SCFilterOptions = namedtuple('SCFilterOptions', 
                             ['SAMPLE_CHANGER', 'MOUNTED_SAMPLE', 'FREE_PIN', 'PLATE'])

SC_FILTER_OPTIONS = SCFilterOptions(0, 1, 2, 3)


class Qt4_DataCollectTree(QtGui.QWidget):
    def __init__(self, parent = None, name = "data_collect", 
                 selection_changed = None):
        QtGui.QWidget.__init__(self, parent)

        self.setObjectName(name)

        # Internal members
        self.collecting = False
        self.centring_method = 0
        self.queue_hwobj = None
        self.queue_model_hwobj = None
        self.beamline_setup_hwobj = None
        self.sample_centring_result = gevent.event.AsyncResult()

        # HW-Object set by TreeBrick
        self.sample_changer_hwobj = None
        self.hl_motor_hwobj = None
        self.tree_brick = self.parent()

        self.sample_item_list = []
        self.collect_tree_task = None
        self.user_stopped = False
        
        # Callbacks TODO:Document better
        self.selection_changed_cb = None
        self.collect_stop_cb = None
        #self.clear_centred_positions_cb = None
        self.run_cb = None

        # Layout
        self.setWindowTitle("Data collect")

        self.confirm_dialog = Qt4_ConfirmDialog(self, 'Confirm Dialog')
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
                        
        self.up_button = QtGui.QPushButton(self)
        self.up_button.setIcon(QtGui.QIcon(self.up_pixmap))
        self.up_button.setFixedHeight(25)

        self.delete_button = QtGui.QPushButton(self)
        self.delete_button.setIcon(QtGui.QIcon(self.delete_pixmap))
        self.delete_button.setDisabled(True)
        self.delete_button.setToolTip("Delete highlighted queue entries")

        self.down_button = QtGui.QPushButton(self)
        self.down_button.setIcon(QtGui.QIcon(self.down_pixmap))
        self.down_button.setFixedHeight(25)

        self.collect_button = QtGui.QPushButton(self)
        self.collect_button.setText("Collect Queue")
        self.collect_button.setFixedWidth(125)
        self.collect_button.setIcon(QtGui.QIcon(self.play_pixmap))
        Qt4_widget_colors.set_widget_color(self.collect_button, Qt4_widget_colors.LIGHT_GREEN)

        self.continue_button = QtGui.QPushButton(self)
        self.continue_button.setText('Pause')
        self.continue_button.setEnabled(True)
        self.continue_button.setFixedWidth(75)
        self.continue_button.setToolTip("Pause after current data collection")

        #self.sample_tree_widget = QtGui.QListView(self, "sample_list_view")
        self.sample_tree_widget = QtGui.QTreeWidget(self)
        
        ##self.sample_tree_widget.setSelectionMode(qt.QListView.Extended)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                             QtGui.QSizePolicy.Expanding))   
        self.sample_tree_widget.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                                                QtGui.QSizePolicy.Expanding))
    
        #elf.sample_tree_widget.setSorting(-1)
        self.sample_tree_widget.setColumnCount(2)
        """self.sample_tree_widget.addColumn("", 280)
        self.sample_tree_widget.addColumn("", 130)"""
        self.sample_tree_widget.header().hide()
        #self.sample_tree_widget.setFrameShape(qt.QListView.StyledPanel)
        #self.sample_tree_widget.setFrameShadow(qt.QListView.Sunken)
        self.sample_tree_widget.setRootIsDecorated(1)
        self.sample_tree_widget.setCurrentItem(self.sample_tree_widget.topLevelItem(0))
        
        layout = QtGui.QVBoxLayout(self)
        button_layout = QtGui.QHBoxLayout(self)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        layout.setSpacing(10)
        layout.addWidget(self.sample_tree_widget)
        self.buttons_grid_layout = QtGui.QGridLayout(self)
        layout.addLayout(self.buttons_grid_layout)
        self.buttons_grid_layout.addLayout(button_layout, 0, 0)
        self.buttons_grid_layout.addWidget(self.delete_button, 0, 4)
        self.buttons_grid_layout.addWidget(self.collect_button, 1, 0)
        self.buttons_grid_layout.addWidget(self.continue_button, 1, 4)

        self.setAttribute(QtCore.Qt.WA_WState_Polished)      
        self.setLayout(layout)
        
        QtCore.QObject.connect(self.up_button, QtCore.SIGNAL("clicked()"), self.up_click)
        QtCore.QObject.connect(self.down_button, QtCore.SIGNAL("clicked()"), self.down_click)
        QtCore.QObject.connect(self.delete_button, QtCore.SIGNAL("clicked()"), self.delete_click)
        QtCore.QObject.connect(self.collect_button, QtCore.SIGNAL("clicked()"), self.collect_stop_toggle)

        QtCore.QObject.connect(self.sample_tree_widget, QtCore.SIGNAL("selectionChanged()"),
                               self.sample_tree_widget_selection)

        QtCore.QObject.connect(self.sample_tree_widget,
                              QtCore.SIGNAL("customContextMenuRequested (const QPoint & pos)"),
                              self.show_context_menu)

        #tCore.QObject.connect(self.sample_tree_widget, 
        #                      QtCore.SIGNAL("itemRenamed(QListViewItem *, int , const QString& )"),
        #                      self.item_renamed)

        QtCore.QObject.connect(self.sample_tree_widget,
                               QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem*, int)"),
                               self.item_double_click)

        QtCore.QObject.connect(self.sample_tree_widget,
                               QtCore.SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                               self.item_click)

        QtCore.QObject.connect(self.confirm_dialog, QtCore.SIGNAL("continue_clicked"),
                               self.collect_items)

        QtCore.QObject.connect(self.continue_button, QtCore.SIGNAL("clicked()"),
                               self.continue_button_click)

        self.sample_tree_widget.viewport().installEventFilter(self)
        self.setFixedWidth(415)

        self.collect_button.setDisabled(True)

    def eventFilter(self, _object, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.show_details()
            return True
        else:
            return False

    def enable_collect(self, state):
        self.sample_tree_widget.setDisabled(not state)
        self.collect_button.setDisabled(not state)
        self.up_button.setDisabled(not state)
        self.down_button.setDisabled(not state)
        self.delete_button.setDisabled(not state)

    def show_context_menu(self, item, point, col):
        menu = QtGui.QMenu(self.sample_tree_widget)

        if item:
            if isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                menu.insertItem(QtCore.QString("Rename"), self.rename_list_view_item)
                menu.insertSeparator(1)
                menu.insertItem(QtCore.QString("Remove"), self.delete_click)
                menu.popup(point);
            elif isinstance(item, Qt4_queue_item.SampleQueueItem):
                if not item.get_model().free_pin_mode:
                    if self.is_mounted_sample_item(item): 
                        menu.insertItem(QtCore.QString("Un-Mount"), self.unmount_sample)
                    else:
                        menu.insertItem(QtCore.QString("Mount"), self.mount_sample)
                       
                menu.insertSeparator(3)
                menu.insertItem(QtCore.QString("Details"), self.show_details) 
                menu.popup(point);
            else:
                menu.popup(point);
                menu.insertSeparator(2)
                menu.insertItem(QtCore.QString("Remove"), self.delete_click)
                menu.insertSeparator(4)
                menu.insertItem(QtCore.QString("Details"), self.show_details)
            
    def item_double_click(self):
        self.show_details()

    def item_click(self):
        self.check_for_path_collisions()

    def context_collect_item(self):
        items = self.get_selected_items()
        
        if len(items) == 1:
            item = items[0]
        
            # Turn this item on (check it), incase its not already checked.
            if item.state() == 0:
                item.setOn(True)
            
            self.collect_items(items)

    def show_details(self):
        items = self.get_selected_items()
        if len(items) == 1:
            item = items[0]
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.tree_brick.show_sample_tab(item)
            elif isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                self.tree_brick.show_datacollection_tab(item)
            elif isinstance(item, Qt4_queue_item.CharacterisationQueueItem):
                self.tree_brick.show_edna_tab(item)
            elif isinstance(item, Qt4_queue_item.EnergyScanQueueItem):
                self.tree_brick.show_energy_scan_tab(item)
	    elif isinstance(item, Qt4_queue_item.XRFScanQueueItem):
                self.tree_brick.show_xrf_scan_tab(item)
            elif isinstance(item, Qt4_queue_item.GenericWorkflowQueueItem):
                self.tree_brick.show_workflow_tab(item)
        #elif len(items) == 0:
        #    self.tree_brick.show_sample_tab()

    def rename_list_view_item(self):
        items = self.get_selected_items()
        if len(items) == 1:
            items[0].setRenameEnabled(0, True);
            items[0].startRename(0);

    def item_renamed(self, item, col, text):
        item.get_model().set_name(text)

    def mount_sample(self):
        self.enable_collect(False)
        gevent.spawn(self.mount_sample_task)

    def mount_sample_task(self):
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
        if success:
            self.sample_centring_result.set(centring_info)
        else:
            msg = "Loop centring failed or was cancelled, " +\
                  "please continue manually."
            logging.getLogger("user_level_log").warning(msg)

    def unmount_sample(self):
        gevent.spawn(self.unmount_sample_task)

    def unmount_sample_task(self):
        items = self.get_selected_items()

        if len(items) == 1:
            self.beamline_setup_hwobj.shape_history_hwobj.clear_all()
            logging.getLogger("user_level_log").\
                info("All centred positions associated with this " + \
                     "sample will be lost.")

            location = items[0].get_model().location

            if hasattr(self.beamline_setup_hwobj.sample_changer_hwobj, '__TYPE__')\
               and (self.beamline_setup_hwobj.sample_changer_hwobj.__TYPE__ == 'CATS'):
                self.beamline_setup_hwobj.sample_changer_hwobj.unload(wait=True)
            else:
                self.beamline_setup_hwobj.sample_changer_hwobj.\
                    unload(22, sample_location = location, wait = False)

            items[0].setOn(False)
            items[0].set_mounted_style(False)

    def sample_tree_widget_selection(self):

        items = self.get_selected_items()
 
        if len(items) == 1:
            item = items[0]
            
            #if item.deletable:
            #    self.delete_button.setDisabled(False)
            #else:
            #    self.delete_button.setDisabled(True)

        if len(items) > 1:
            for item in items:
                if isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem) or \
                       isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                    self.delete_button.setDisabled(False)
                    break

        self.selection_changed_cb(items)        
        checked_items = self.get_checked_items()
        self.collect_button.setDisabled(len(checked_items) == 0)
        self.set_first_element()

    def add_empty_task_node(self):
        samples = self.get_selected_samples()
        task_node = queue_model_objects.TaskGroup()
        task_node.set_name('Collection group')
        Qt4_queue_item.DataCollectionGroupQueueItem(samples[0], 
                                                samples[0].lastItem(),
                                                task_node.get_display_name())

    def get_item_by_model(self, parent_node):
        it = qt.QListViewItemIterator(self.sample_tree_widget)
        item = it.current()
    
        while item:
            if item.get_model() is parent_node:
                return item

            it += 1
            item = it.current()

        return self.sample_tree_widget

    def last_top_level_item(self):
        sibling = self.sample_tree_widget.firstChild()
        last_child = None

        while(sibling):
            last_child = sibling
            sibling = sibling.nextSibling()
            
        return last_child
        
    def add_to_view(self, parent, task):
        view_item = None
        parent_tree_item = self.get_item_by_model(parent)

        if parent_tree_item is self.sample_tree_widget:
            last_item = self.last_top_level_item()
        else:
            last_item = parent_tree_item.lastItem()
        
        cls = Qt4_queue_item.MODEL_VIEW_MAPPINGS[task.__class__]

        if parent_tree_item.lastItem():
            view_item = cls(parent_tree_item, last_item,
                            task.get_display_name())
            #view_item = cls(parent_tree_item, last_item,
            #                task.get_display_name())
        else:
            view_item = cls(parent_tree_item, task.get_display_name())
        
        if isinstance (task, queue_model_objects.Basket):
            view_item.setOpen(task.get_is_present())
        else:
            view_item.setOpen(True)
        self.queue_model_hwobj.view_created(view_item, task)

    def get_selected_items(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                             Qt4_queue_item.is_selected,
                                             Qt4_queue_item.get_item)
        return res

    def get_selected_samples(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                          Qt4_queue_item.is_selected_sample,
                                          Qt4_queue_item.get_item)
        return res
    
    def get_selected_tasks(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                             Qt4_queue_item.is_selected_task,
                                             Qt4_queue_item.get_item)

        return res

    def get_selected_dcs(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                          Qt4_queue_item.is_selected_dc,
                                          Qt4_queue_item.get_item)
        return res

    def get_selected_task_nodes(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                             Qt4_queue_item.is_selected_task_node,
                                             Qt4_queue_item.get_item)
        return res

    def is_sample_selected(self):
        items = self.get_selected_items()
        
        for item in items:
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                return True

        return False

    def filter_sample_list(self, option):
        self.sample_tree_widget.clearSelection()
        self.beamline_setup_hwobj.set_plate_mode(False)
        self.confirm_dialog.set_plate_mode(False)       
        if option == SC_FILTER_OPTIONS.SAMPLE_CHANGER:
            self.sample_tree_widget.clear()
            self.queue_model_hwobj.select_model('ispyb')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.MOUNTED_SAMPLE:
            loaded_sample = self.sample_changer_hwobj.\
                                 getLoadedSample()

            try:
                loaded_sample_loc = loaded_sample.getCoords()
            except:
                loaded_sample_loc = None

            it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
            item = it.current()
        
            while item:
                if isinstance(item, Qt4_queue_item.SampleQueueItem):
                    if item.get_model().location == loaded_sample_loc:
                        item.setSelected(True)
                        item.setVisible(True)
                    else:
                        item.setVisible(False)

                it += 1
                item = it.current()

        elif option == SC_FILTER_OPTIONS.FREE_PIN:
            self.sample_tree_widget.clear()
            self.queue_model_hwobj.select_model('free-pin')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.PLATE:
            #self.sample_tree_widget.clear()
            #self.sample_tree_widget.setDisabled(True)
            self.beamline_setup_hwobj.set_plate_mode(True)
            self.confirm_dialog.set_plate_mode(True)       

        self.sample_tree_widget_selection()
        
    def set_centring_method(self, method_number):       
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
        if self.queue_hwobj.is_executing():
            if not self.queue_hwobj.is_paused():
                self.queue_hwobj.set_pause(True)
            else:
                self.queue_hwobj.set_pause(False)

    def queue_paused_handler(self, state):
        if state:
            self.parent().enable_hutch_menu(True)
            self.parent().enable_command_menu(True)
            self.parent().enable_task_toolbox(True)
            self.continue_button.setText('Continue')
            self.continue_button.setPaletteBackgroundColor(Qt4_widget_colors.LIGHT_YELLOW)
        else:
            self.parent().enable_hutch_menu(False)
            self.parent().enable_command_menu(False)
            self.parent().enable_task_toolbox(False)
            self.continue_button.setText('Pause')
            color = self.paletteBackgroundColor()
            self.continue_button.setPaletteBackgroundColor(color)

    def collect_stop_toggle(self):
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
                self.sample_tree_widget.setSelected(item, False)
            
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
        self.parent().sample_changer_widget.child('synch_button').setEnabled(state)
        self.parent().sample_changer_widget.child('centring_cbox').setEnabled(state)
        self.parent().sample_changer_widget.child('filter_cbox').setEnabled(state)

    def is_mounted_sample_item(self, item):
        result = False

        if isinstance(item, Qt4_queue_item.SampleQueueItem):
            if item.get_model().free_pin_mode == True:
                result = True
            elif not self.sample_changer_hwobj.hasLoadedSample():
                result = False
            elif item.get_model().location == self.sample_changer_hwobj.getLoadedSample().getCoords():
                result = True

        return result

    def collect_items(self, items = [], checked_items = []):
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
        Qt4_widget_colors.set_widget_colors(self.collect_button, Qt4_widget_colors.LIGHT_RED)
        self.collect_button.setIconSet(QtGui.QIcon(self.stop_pixmap))
        self.parent().enable_hutch_menu(False)
        self.run_cb()
        
        try:
            self.queue_hwobj.execute()
        except Exception, e:
            raise e
        
    def stop_collection(self):
        self.queue_hwobj.stop()
        self.queue_stop_handler()

    def queue_stop_handler(self, status = None):
        self.user_stopped = True
        self.queue_execution_completed(None)
               
    def queue_execution_completed(self, status):
        self.collecting = False
        self.collect_button.setText("Collect Queue")
        self.collect_button.setIconSet(QtGui.QIcon(self.play_pixmap))
        self.collect_button.setPaletteBackgroundColor(Qt4_widget_colors.LIGHT_GREEN)
        self.delete_button.setEnabled(True)
        self.enable_sample_changer_widget(True)
        self.parent().enable_hutch_menu(True)
        self.parent().enable_command_menu(True)
        self.parent().enable_task_toolbox(True)
        self.set_sample_pin_icon()

    def get_checked_items(self):
        res = Qt4_queue_item.perform_on_children(self.sample_tree_widget,
                                          Qt4_queue_item.is_checked,
                                          Qt4_queue_item.get_item)

        return res
 
    def delete_click(self, selected_items = None):
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
                    parent.takeItem(item)

                    if not parent.firstChild():
                        parent.setOn(False)
            else:
                item.reset_style()
                child = item.firstChild() 

                while child: 
                    children.append(child)
                    child = child.nextSibling()

        if children:
            self.delete_click(selected_items = children)

        self.check_for_path_collisions()

        self.set_first_element() 

    def set_first_element(self):
        selected_items = self.get_selected_items()
        if len(selected_items) == 0:        
            it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
            item = it.current()
            if item.get_model().free_pin_mode:
                self.sample_tree_widget.setSelected(self.sample_list_view.firstChild(), True)

    def down_click(self):
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, Qt4_queue_item.QueueItem):
                if item.nextSibling() is not None:
                    item.moveItem(item.nextSibling())

    def previous_sibling(self, item):
        if item.parent():
            first_child = item.parent().firstChild()
        else:
            first_child = item.listView().firstChild() 

        if first_child is not item :
            sibling = first_child.nextSibling()   
        
            while sibling:           
                if sibling is item :
                    return first_child
                elif sibling.nextSibling() is item:
                    return sibling
                else:
                    sibling = sibling.nextSibling()
        else :
            return None
        
    def up_click(self):
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, Qt4_queue_item.QueueItem): 
                older_sibling = self.previous_sibling(item)
                if older_sibling :
                    older_sibling.moveItem(item)

    def samples_from_sc_content(self, sc_basket_content, sc_sample_content):
        """sample_list = []
        
        for sample_info in sc_content:
            sample = queue_model_objects.Sample()
            sample.init_from_sc_sample(sample_info)
            sample_list.append(sample)

        return sample_list"""
        basket_list = []
        sample_list = []
        #IK added sample groups    
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
        for sample in sample_list:
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
            self.add_to_queue([sample], self.sample_tree_widget, False)

    def populate_free_pin(self):
        self.queue_model_hwobj.clear_model('free-pin')
        self.queue_model_hwobj.select_model('free-pin')
        sample = queue_model_objects.Sample()
        sample.free_pin_mode = True
        sample.set_name('manually-mounted')
        self.queue_model_hwobj.add_child(self.queue_model_hwobj.get_model_root(),
                                         sample)

    """def populate_list_view(self, sample_list):
        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model('ispyb')
        self.sample_tree_widget.clear()
        self.queue_model_hwobj.select_model('ispyb')
        
        for sample in sample_list:
            sample.set_enabled(False)
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
        self.set_sample_pin_icon()"""

    def populate_list_view(self, basket_list, sample_list):   
        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model('ispyb')
        self.sample_tree_widget.clear()
        self.queue_model_hwobj.select_model('ispyb')
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

        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.current()

        while item:
            if self.is_mounted_sample_item(item):
                item.setSelected(True)
                item.set_mounted_style(True)
                #self.sample_tree_widget_selection()
            elif isinstance(item, Qt4_queue_item.SampleQueueItem):
                item.set_mounted_style(False)
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                if item.get_model().lims_location != (None, None):
                    item.setPixmap(0, self.ispyb_pixmap)
                    item.setText(0, item.get_model().loc_str + ' - ' \
                                 + item.get_model().get_display_name())
            elif isinstance(item, Qt4_queue_item.BasketQueueItem):
                #if item.get_model().lims_location != (None, None):
                #    item.setPixmap(0, self.ispyb_pixmap)
                item.setText(0, item.get_model().get_display_name())
                if not item.get_model().get_is_present():
                    item.setEnabled(False)
                    item.setOpen(False)
                    #item.setOn(False)
        
            it += 1
            item = it.current()

    def check_for_path_collisions(self):
        conflict = False
        it = QtGui.QTreeWidgetItemIterator(self.sample_tree_widget)
        item = it.current()

        while item:
            if item.isOn():
                pt = item.get_model().get_path_template()
                
                if pt:
                     path_conflict = self.queue_model_hwobj.\
                                check_for_path_collisions(pt)

                     if path_conflict:
                         conflict = True
                         item.setIcon(QtGui.QIcon(self.caution_pixmap))
                     else:
                         item.setIcon(QtGui.QIcon())
                         
            it += 1
            item = it.current()

        return conflict
        
