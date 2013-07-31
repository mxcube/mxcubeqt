import queue_entry
import gevent
import gevent.event
import pprint 
import logging
import queue_model_objects_v1 as queue_model_objects
import queue_item
import functools

from BlissFramework import Icons
from widgets.collect_progress_widget_layout  import CollectProgressWidgetLayout
from position_history_widget import COLLECTION_METHOD_NAME
from qt import *
from qttable import QTable, QTableItem
from collections import namedtuple
from widgets.confirm_dialog import ConfirmDialog
from BlissFramework.Utils import widget_colors

SCFilterOptions = namedtuple('SCFilterOptions', ['ALL_SAMPLES', 
                                                 'MOUNTED_SAMPLE',
                                                 'FREE_PIN'])

SC_FILTER_OPTIONS = SCFilterOptions(0, 1, 2)

class DataCollectTree(QWidget):
    def __init__(self, parent = None, name = "data_collect", 
                 selection_changed = None):
        QWidget.__init__(self, parent, name)

        # Internal members
        self._holder_length = None
        self._current_item_name = None
        self.collect_clicked = False
        self.collecting = False
        self.loaded_sample = (-1, -1)
        #self._loaded_sample_item = None
        self.centring_method = 0
        self.queue_hwobj = None
        self.queue_model_hwobj = None
        self.beamline_setup_hwobj = None

        # HW-Object set by TreeBrick
        self.sample_changer_hwobj = None
        self.diffractometer_hwobj = None
        self.hl_motor_hwobj = None
        self.tree_brick = self.parent()

        self.sample_item_list = []
        self.collect_tree_task = None
        self.user_stopped = False
        
        # Callbacks TODO:Document better
        self.selection_changed_cb = None
        self.collect_stop_cb = None
        self.clear_centred_positions_cb = None
        self.run_cb = None

        # Layout
        self.confirm_dialog = ConfirmDialog(self)
        self.confirm_dialog.setModal(True)
        self.pin_pixmap = Icons.load("sample_axis.png")
        self.task_pixmap = Icons.load("task.png")
        self.play_pixmap = Icons.load("VCRPlay.png")
        self.stop_pixmap = Icons.load("Stop.png")
        self.up_pixmap = Icons.load("Up2.png")
        self.down_pixmap = Icons.load("Down2.png")
        self.delete_pixmap = Icons.load("Delete2.png")
        self.ispyb_pixmap = Icons.load("SampleChanger2.png")
                        
        self.up_button = QPushButton(self, "up_button")
        self.up_button.setPixmap(self.up_pixmap)
        self.delete_button = QPushButton(self, "delete_button")
        self.delete_button.setPixmap(self.delete_pixmap)
        self.delete_button.setDisabled(True)
        self.down_button = QPushButton(self, "down_button")
        self.down_button.setPixmap(self.down_pixmap)
        self.collect_button = QPushButton(self, "collect_button")
        self.collect_button.setFixedWidth(120)
        self.collect_button.setIconSet(QIconSet(self.play_pixmap))
        self.continue_button = QPushButton(self, "ok_button")
        self.continue_button.setText('Pause')
        self.continue_button.setEnabled(True)
        #self.progress_bar = CollectProgressWidgetLayout(self, "progress_bar")

        self.sample_list_view = QListView(self, "sample_list_view")
        self.sample_list_view.setSelectionMode(QListView.Extended)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Expanding))   
        self.sample_list_view.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                        QSizePolicy.Expanding))
    
        self.sample_list_view.setSorting(-1)
        self.sample_list_view.addColumn("", 250)
        self.sample_list_view.addColumn("", 125)
        self.sample_list_view.header()\
            .setClickEnabled(0, 0)
        self.sample_list_view.header()\
            .setResizeEnabled(0, 0)
        self.sample_list_view.header()\
            .setClickEnabled(0, 1)
        self.sample_list_view.header()\
            .setResizeEnabled(0, 1)
        self.sample_list_view.header().show()

        self.sample_list_view.setFrameShape(QListView.StyledPanel)
        self.sample_list_view.setFrameShadow(QListView.Sunken)
        self.sample_list_view.setRootIsDecorated(1)
        self.sample_list_view.setSelected(self.sample_list_view.firstChild(), 
                                          True)
        
        self.languageChange()
        
        layout = QVBoxLayout(self,0,0, 'main_layout')
        button_layout = QHBoxLayout(None, 0, 0, 'button_layout')
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        layout.setSpacing(10)
        layout.addWidget(self.sample_list_view)
        self.buttons_grid_layout = QGridLayout(2, 5)
        layout.addLayout(self.buttons_grid_layout)
        self.buttons_grid_layout.addLayout(button_layout, 0, 0)
        self.buttons_grid_layout.addWidget(self.delete_button, 0, 4)
        self.buttons_grid_layout.addWidget(self.collect_button, 1, 0)
        self.buttons_grid_layout.addWidget(self.continue_button, 1, 4)
        
        #layout.addWidget(self.progress_bar)
        
        
        self.clearWState(Qt.WState_Polished)
        
        QObject.connect(self.up_button, SIGNAL("clicked()"),
                        self.up_click)

        QObject.connect(self.down_button, SIGNAL("clicked()"),
                         self.down_click)

        QObject.connect(self.delete_button, SIGNAL("clicked()"),
                        self.delete_click)
      
        QObject.connect(self.collect_button, SIGNAL("clicked()"),
                        self.collect_stop_toggle)

        QObject.connect(self.sample_list_view, 
                        SIGNAL("selectionChanged()"),
                        self.sample_list_view_selection)

        QObject.connect(self.sample_list_view,
                        SIGNAL("contextMenuRequested(QListViewItem *, const QPoint& , int)"),
                        self.show_context_menu)

        QObject.connect(self.sample_list_view, 
                        SIGNAL("itemRenamed(QListViewItem *, int , const QString& )"),
                        self.item_renamed)

        QObject.connect(self.sample_list_view,
                        SIGNAL("doubleClicked(QListViewItem *, const QPoint &, int)"),
                        self.item_double_click)

        QObject.connect(self.confirm_dialog,
                        PYSIGNAL("continue_clicked"),
                        self.collect_items)

        QObject.connect(self.continue_button, SIGNAL("clicked()"),
                        self.continue_button_click)


        self.sample_list_view.viewport().installEventFilter(self)


    def eventFilter(self, _object, event):
        if event.type() == QEvent.MouseButtonDblClick:
            self.show_details()
            return True
        else:
            return False


    def show_context_menu(self, item, point, col):
        menu = QPopupMenu(self.sample_list_view, "popup_menu")

        if item:
            if isinstance(item, queue_item.DataCollectionGroupQueueItem):
                menu.insertItem(QString("Rename"), self.rename_list_view_item)
                menu.insertSeparator(1)
                menu.insertItem(QString("Remove"), self.delete_click)
                menu.popup(point);
            elif isinstance(item, queue_item.SampleQueueItem):
                if not item.get_model().free_pin_mode:
                    menu.insertItem(QString("Mount"), self.mount_sample)
                    menu.insertItem(QString("Un-Mount"), self.unmount_sample)
                menu.insertSeparator(3)
                #menu.insertItem(QString("Create Data Collection Group"), self.add_empty_task_node)
                #menu.insertSeparator(5)
                menu.insertItem(QString("Details"), self.show_details) 
                menu.popup(point);
            else:
                menu.popup(point);
                #menu.insertItem(QString("Duplicate"), self.copy_generic_dc_list_item)
                #menu.insertItem(QString("Rename"), self.rename_list_view_item)
                menu.insertSeparator(2)
                menu.insertItem(QString("Remove"), self.delete_click)
                menu.insertSeparator(4)
                menu.insertItem(QString("Details"), self.show_details)
            
            menu.insertItem(QString("Collect"), self.context_collect_item)
            

    def item_double_click(self):
        self.show_details()


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
            if isinstance(item, queue_item.SampleQueueItem):
                self.tree_brick.show_sample_tab(item)
            elif isinstance(item, queue_item.DataCollectionQueueItem):
                self.tree_brick.show_datacollection_tab(item)
            elif isinstance(item, queue_item.CharacterisationQueueItem):
                self.tree_brick.show_edna_tab(item)
            elif isinstance(item, queue_item.EnergyScanQueueItem):
                self.tree_brick.show_energy_scan_tab(item)
            elif isinstance(item, queue_item.GenericWorkflowQueueItem):
                self.tree_brick.show_workflow_tab(item)
        elif len(items) == 0:
            self.tree_brick.show_sample_tab()


    def rename_list_view_item(self):
        items = self.get_selected_items()
        if len(items) == 1:
            self._current_item_name = str(items[0].text())
            items[0].setRenameEnabled(0, True);
            items[0].startRename(0);


    def item_renamed(self, item, col, text):
        item.set_name(str(text))
        item.get_model().set_name(text)


    def mount_sample(self):
        gevent.spawn(self.mount_sample_task)


    def mount_sample_task(self):
        items = self.get_selected_items()

        if len(items) == 1:
            if not items[0].get_model().free_pin_mode:

                #message = "All centred positions associated with this " + \
                #    "sample will be lost, do you want to continue ?."
                #ans = QMessageBox.question(self,
                #                           "Data collection",
                #                           message,
                #                           QMessageBox.Yes,
                #                           QMessageBox.No,
                #                           QMessageBox.NoButton)

                ans = True
                if ans:
                    #self.clear_centred_positions_cb()
                    location = items[0].get_model().location

                    hl = 22
                    if self.hl_motor_hwobj:
                        hl = self.hl_motor_hwobj.getPosition()

                    try:
                        self.sample_changer_hwobj.\
                            loadSample(hl, sample_location = location, wait = True)
                    except Exception as e:
                        items[0].setText(1, "Error loading")
                        logging.getLogger('user_level_log').\
                            info("Error loading sample: " + e.message)   
                    else:
                        logging.getLogger('queue_exec').\
                            info("Sample loaded")
                        items[0].setText(1, "Sample loaded")
                        #self._loaded_sample_item.setPixmap(0, QPixmap())
                        #self._loaded_sample_item = items[0]
                        items[0].setSelected(True)  
        else:
            logging.getLogget("user_level_log").\
                info('Its not possible to mount samples in free pin mode')

            
    def unmount_sample(self):
        gevent.spawn(self.unmount_sample_task)


    def unmount_sample_task(self):
        items = self.get_selected_items()

        if len(items) == 1:

            logging.getLogget("user_level_log").\
                info("All centred positions associated with this " + \
                     "sample will be lost, do you want to continue ?.")

            #self.clear_centred_positions_cb()
            location = items[0].get_model().location
            self.sample_changer_hwobj.unloadSample(22, 
                                                   sample_location = location)

    def sample_list_view_selection(self):
        items = self.get_selected_items()

        if len(items) == 1:
            item = items[0]
            
            if item.deletable:
                self.delete_button.setDisabled(False)
            else:
                self.delete_button.setDisabled(True)

        if len(items) > 1:
            for item in items:
                if isinstance(item, queue_item.DataCollectionGroupQueueItem) or \
                       isinstance(item, queue_item.DataCollectionQueueItem):
                    self.delete_button.setDisabled(False)
                    break

        self.selection_changed_cb(items)


    def add_empty_task_node(self):
        samples = self.get_selected_samples()
        task_node = queue_model_objects.TaskGroup()
        task_node.set_name('Collection group')

        task_node_tree_item = \
            queue_item.DataCollectionGroupQueueItem(samples[0], 
                                                    samples[0].lastItem(),
                                                    task_node.get_name())


    def add_to_queue(self, task_list, parent_tree_item, set_on = True):
        for task in task_list:
            view_item = None
            qe = None
            
            if isinstance(task, queue_model_objects.DataCollection):
                view_item = queue_item.\
                            DataCollectionQueueItem(parent_tree_item,
                                                    parent_tree_item.lastItem(),
                                                    task.get_name())
                
                qe = queue_entry.DataCollectionQueueEntry(view_item, task)
                
            elif isinstance(task, queue_model_objects.Characterisation):
                view_item = queue_item.\
                            CharacterisationQueueItem(parent_tree_item,
                                                      parent_tree_item.lastItem(),
                                                      task.get_name())

                qe = queue_entry.CharacterisationGroupQueueEntry(view_item, task)
            elif isinstance(task, queue_model_objects.EnergyScan):
                view_item = queue_item.\
                            EnergyScanQueueItem(parent_tree_item,
                                                parent_tree_item.lastItem(),
                                                task.get_name())

                qe = queue_entry.EnergyScanQueueEntry(view_item, task)
            elif isinstance(task, queue_model_objects.SampleCentring):
                view_item = queue_item.\
                            SampleCentringQueueItem(parent_tree_item,
                                                    parent_tree_item.lastItem(),
                                                    task.get_name())
                
                qe = queue_entry.SampleCentringQueueEntry(view_item, task)
            elif isinstance(task, queue_model_objects.Sample):
                view_item = queue_item.SampleQueueItem(parent_tree_item,
                                                       parent_tree_item.lastItem(),
                                                       task.get_name())
            
                qe = queue_entry.SampleQueueEntry(view_item, task)
            elif isinstance(task, queue_model_objects.TaskGroup):
                view_item = queue_item.\
                            DataCollectionGroupQueueItem(parent_tree_item,
                                                         parent_tree_item.lastItem(),
                                                         task.get_name())
            
                qe = queue_entry.TaskGroupQueueEntry(view_item, task)
                
            if isinstance(task, queue_model_objects.Sample):
                self.queue_hwobj.enqueue(qe)
            else:
                parent_tree_item.get_queue_entry().enqueue(qe)

            view_item.setOpen(True)
            view_item.setOn(set_on)

            if isinstance(task, queue_model_objects.TaskNode) and task.get_children():
                self.add_to_queue(task.get_children(), view_item, set_on)

        
    def get_item_by_model(self, parent_node):
        it = QListViewItemIterator(self.sample_list_view)
        item = it.current()
    
        while item:
            if item.get_model() is parent_node:
                return item

            it += 1
            item = it.current()

        return self.sample_list_view


    def add_to_view(self, parent, task):
        view_item = None
        qe = None
        
        parent_tree_item = self.get_item_by_model(parent)
        
        cls = queue_item.MODEL_VIEW_MAPPINGS[task.__class__]
        view_item = cls(parent_tree_item, parent_tree_item.lastItem(),
                        task.get_name())
                
        view_item.setOpen(True)
        self.queue_model_hwobj.view_created(view_item, task)


    def get_selected_items(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                             queue_item.is_selected,
                                             queue_item.get_item)
        return res


    def get_selected_samples(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                          queue_item.is_selected_sample,
                                          queue_item.get_item)
        return res

    
    def get_selected_tasks(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                             queue_item.is_selected_task,
                                             queue_item.get_item)

        return res


    def get_selected_dcs(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                          queue_item.is_selected_dc,
                                          queue_item.get_item)
        return res


    def get_selected_task_nodes(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                             queue_item.is_selected_task_node,
                                             queue_item.get_item)
        return res


    def is_sample_selected(self):
         items = self.get_selected_items()
        
         for item in items:
             if isinstance(item, queue_item.SampleQueueItem):
                 return True

         return False


    def filter_sample_list(self, option):
        self.sample_list_view.clearSelection()
        if option == SC_FILTER_OPTIONS.ALL_SAMPLES:
            self.sample_list_view.clear()
            self.queue_model_hwobj.select_model('ispyb')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.MOUNTED_SAMPLE:
            loaded_sample = self.sample_changer_hwobj.\
                            getLoadedSampleLocation()

            it = QListViewItemIterator(self.sample_list_view)
            item = it.current()
        
            while item:
                if isinstance(item, queue_item.SampleQueueItem):
                    if item.get_model().location == loaded_sample:
                        item.setSelected(True)
                        item.setVisible(True)
                    else:
                        item.setVisible(False)

                it += 1
                item = it.current()

        elif option == SC_FILTER_OPTIONS.FREE_PIN:
            self.sample_list_view.clear()
            self.queue_model_hwobj.select_model('free-pin')


    def set_centring_method(self, method_number):
        self.centring_method = method_number


    def continue_button_click(self):
        if not self.queue_hwobj.is_paused():
            self.queue_hwobj.set_pause(True)
        else:
            self.queue_hwobj.set_pause(False)


    def queue_paused_handler(self, state):
        if state:
            self.continue_button.setText('Continue')
        else:
            self.continue_button.setText('Pause')


    def collect_stop_toggle(self):
        #import sys; sys.stdout = sys.__stdout__; import pdb; pdb.set_trace()
        #self.queue_model_hwobj.check_for_all_path_collisions()

        self.checked_items = self.get_checked_items()
        self.queue_hwobj.disable(False)
        
        for item in self.checked_items:
            pt = item.get_model().get_path_template()

            if pt:
                path_conflict = self.queue_model_hwobj.\
                                check_for_path_collisions(pt)
                
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
                self.sample_list_view.setSelected(item, False)
            
            if len(self.checked_items):
                self.confirm_dialog.set_items(self.checked_items)
                self.confirm_dialog.show()
            else:
                message = "No data collections selected, please select one" + \
                          " or more data collections"

                QMessageBox.information(self,
                                        "Data collection",
                                        message,
                                        "OK")
        else:
            self.stop_collection()


    def enable_sample_changer_widget(self, state):
        self.parent().sample_changer_widget.synch_button.setEnabled(state)
        self.parent().sample_changer_widget.centring_cbox.setEnabled(state)
        self.parent().sample_changer_widget.filter_cbox.setEnabled(state)


    def is_mounted_sample_item(self, item):
        if isinstance(item, queue_item.SampleQueueItem):
            if item.get_model().location == self.sample_changer_hwobj.\
                   getLoadedSampleLocation():
                return True


    def collect_items(self, items = None):
        for item in self.checked_items:
            # update the run-number text incase of re-collect
            item.setText(0, item.get_model().get_name())

            #Clear status
            item.setText(1, "")
            item.setHighlighted(False)

            if self.is_mounted_sample_item(item):
                item.setPixmap(0, self.pin_pixmap)
                # Blue background and sample pin for mounted sample.
                item.setBackgroundColor(widget_colors.SKY_BLUE)
            else:
                item.setBackgroundColor(widget_colors.WHITE)
        
        self.user_stopped = False
        self.delete_button.setEnabled(False)
        self.enable_sample_changer_widget(False)
        
        self.collecting = True
        self.collect_button.setText("      Stop   ")
        self.collect_button.setIconSet(QIconSet(self.stop_pixmap))
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
        self.collect_button.setIconSet(QIconSet(self.play_pixmap))
        self.delete_button.setEnabled(True)
        self.enable_sample_changer_widget(True)


    def get_checked_items(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                          queue_item.is_checked,
                                          queue_item.get_item)

        return res
 

    def delete_click(self):
        selected_items = self.get_selected_items()
        
        for item in selected_items:
            if item.deletable:
                if not item.parent().isSelected() or \
                   isinstance(item.parent(), queue_item.SampleQueueItem):
                    if isinstance(item, queue_item.DataCollectionGroupQueueItem):
                        self.tree_brick.show_sample_centring_tab()

                    if isinstance(item, queue_item.DataCollectionQueueItem):
                        self.tree_brick.show_sample_centring_tab()

                    parent = item.parent()
                    self.queue_model_hwobj.del_child(parent.get_model(),
                                                     item.get_model())
                    qe = item.get_queue_entry()
                    parent.get_queue_entry().dequeue(qe)
                    parent.takeItem(item)

                    if not parent.firstChild():
                        parent.setOn(False)


    def down_click(self):
        selected_items = self.get_selected_items()

        if len(selected_items) == 1:
            item = selected_items[0]

            if isinstance(item, queue_item.QueueItem):
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

            if isinstance(item, queue_item.QueueItem): 
                older_sibling = self.previous_sibling(item)
                if older_sibling :
                    older_sibling.moveItem(item)


    def languageChange(self):
        self.setCaption(self.__tr("Data collect"))
        self.collect_button.setText(self.__tr("Collect Queue"))
        self.sample_list_view.header().setLabel(0, 
                                                self.__tr("Sample location"), 
                                                280)
        self.sample_list_view.header().setLabel(1, 
                                                self.__tr("Status"), 
                                                125)


    def samples_from_sc_content(self, sc_content):
        sample_list = []
        
        for sample_info in sc_content:
            sample = queue_model_objects.Sample()
            sample.init_from_sc_sample(sample_info)
            sample_list.append(sample)

        return sample_list


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
            self.add_to_queue([sample], self.sample_list_view, False)


    def populate_free_pin(self):
        self.queue_model_hwobj.select_model('free-pin')
        sample = queue_model_objects.Sample()
        sample.free_pin_mode = True
        sample.set_name('free-pin')
        self.queue_model_hwobj.add_child(self.queue_model_hwobj.get_model_root(),
                                         sample)


    def populate_list_view(self, sample_list):
        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model('ispyb')
        self.sample_list_view.clear()
        self.queue_model_hwobj.select_model('ispyb')
        
        for sample in sample_list:
            sample.set_enabled(False)
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
        self.set_sample_pin_icon()
    

    def init_with_sc_content(self, sc_content):
        try:
            current_sample_loc = self.sample_changer_hwobj.getLoadedSampleLocation()
            self.loaded_sample = (self.sample_changer_hwobj.currentBasket,
                                  self.sample_changer_hwobj.currentSample)
        except:
            current_sample_loc = ('-1', '-1')
            self.loaded_sample = (-1, -1)

        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model('ispyb')
        self.sample_list_view.clear()
        self.queue_model_hwobj.select_model('ispyb')
        
        for sample_info in sc_content:
            sample = queue_model_objects.Sample()
            
            sample.loc_str = str(sample_info[1]) + ':' + str(sample_info[2])
            sample.location = (sample_info[1], sample_info[2])
            sample.set_name(sample.loc_str)
            sample.set_enabled(False)

            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
            
        self.set_sample_pin_icon()


    def get_mounted_sample_item(self):
        sample_items = queue_item.perform_on_children(self.sample_list_view,
                                                   queue_item.is_sample,
                                                   queue_item.get_item)
        
        for item in sample_items:
            if item.get_model().location == self.sample_changer_hwobj.\
                    getLoadedSampleLocation():
                return item


    def set_sample_pin_icon(self):
        it = QListViewItemIterator(self.sample_list_view)
        item = it.current()

        self.beamline_setup_hwobj.shape_history_hwobj.clear_all()

        while item:
            if self.is_mounted_sample_item(item):
                item.setPixmap(0, self.pin_pixmap)
                item.setBackgroundColor(widget_colors.SKY_BLUE)
                item.setSelected(True)
                self.sample_list_view_selection()
            elif isinstance(item, queue_item.SampleQueueItem):
                item.setPixmap(0, QPixmap())
                item.restoreBackgroundColor()
                item.setSelected(False)
                item.setText(1, '')

            if isinstance(item, queue_item.SampleQueueItem):
                if item.get_model().lims_location != (None, None):
                    item.setPixmap(0, self.ispyb_pixmap)
                    item.setText(0, item.get_model().loc_str + ' - ' \
                                 + item.get_model().get_name())
        
            it += 1
            item = it.current()

 

    def init_with_ispyb_data(self, lims_sample_list):
        samples = {}

        for lims_sample in lims_sample_list:
            sample = queue_model_objects.Sample()
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), sample)
            sample.init_from_lims_object(lims_sample)
            samples[(sample.lims_container_location,
                     sample.lims_sample_location)] = sample

        sample_item = self.sample_list_view.firstChild()
            
        while(sample_item):
            sample_node = samples.get(sample_item.get_model().location, None)

            if sample_node:
                sample_item.data = sample_node
                label = sample_item.data.loc_str + ' - ' + \
                        sample_item.data.get_display_name()
                sample_item.setText(0, label)
            
            sample_item = sample_item.nextSibling()


    def __select_mounted_sample(self, sc_data):
        k = 0
        for sample_info in sc_data:
            if sample_info[4] == 16:
                return k
            k += 1

            
    def __tr(self,s,c = None):
        return qApp.translate("DataCollectTree", s, c)




