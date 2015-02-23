import qt
import logging
import gevent
import queue_model_objects_v1 as queue_model_objects
import queue_item
import queue_entry

from collections import namedtuple
from BlissFramework import Icons
from BlissFramework.Utils import widget_colors
from widgets.confirm_dialog import ConfirmDialog
from queue_model_enumerables_v1 import CENTRING_METHOD

SCFilterOptions = namedtuple('SCFilterOptions', 
                             ['SAMPLE_CHANGER', 'MOUNTED_SAMPLE', 'FREE_PIN', 'PLATE'])

SC_FILTER_OPTIONS = SCFilterOptions(0, 1, 2, 3)


class DataCollectTree(qt.QWidget):
    def __init__(self, parent = None, name = "data_collect", 
                 selection_changed = None):
        qt.QWidget.__init__(self, parent, name)

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
        self.setCaption("Data collect")

        self.confirm_dialog = ConfirmDialog(self, 'Confirm Dialog')
        self.confirm_dialog.setModal(True)

        self.pin_pixmap = Icons.load("sample_axis.png")
        self.task_pixmap = Icons.load("task.png")
        self.play_pixmap = Icons.load("VCRPlay.png")
        self.stop_pixmap = Icons.load("Stop.png")
        self.up_pixmap = Icons.load("Up2.png")
        self.down_pixmap = Icons.load("Down2.png")
        self.delete_pixmap = Icons.load("bin_small.png")
        self.ispyb_pixmap = Icons.load("SampleChanger2.png")
        self.caution_pixmap = Icons.load("Caution2.png")
                        
        self.up_button = qt.QPushButton(self, "up_button")
        self.up_button.setPixmap(self.up_pixmap)
        self.up_button.setFixedHeight(25)

        self.delete_button = qt.QPushButton(self, "delete_button")
        self.delete_button.setPixmap(self.delete_pixmap)
        self.delete_button.setDisabled(True)
        qt.QToolTip.add(self.delete_button, "Delete highlighted queue entries")

        self.down_button = qt.QPushButton(self, "down_button")
        self.down_button.setPixmap(self.down_pixmap)
        self.down_button.setFixedHeight(25)

        self.collect_button = qt.QPushButton(self, "collect_button")
        self.collect_button.setText("Collect Queue")
        self.collect_button.setFixedWidth(125)
        self.collect_button.setIconSet(qt.QIconSet(self.play_pixmap))
        self.collect_button.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)

        self.continue_button = qt.QPushButton(self, "ok_button")
        self.continue_button.setText('Pause')
        self.continue_button.setEnabled(True)
        self.continue_button.setFixedWidth(75)
        qt.QToolTip.add(self.continue_button, "Pause after current data collection")

        self.sample_list_view = qt.QListView(self, "sample_list_view")
        self.sample_list_view.setSelectionMode(qt.QListView.Extended)

        self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Fixed,
                                          qt.QSizePolicy.Expanding))   
        self.sample_list_view.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Fixed,
                                                           qt.QSizePolicy.Expanding))
    
        self.sample_list_view.setSorting(-1)
        self.sample_list_view.addColumn("", 280)
        self.sample_list_view.addColumn("", 130)
        self.sample_list_view.header().hide()

        self.sample_list_view.header().hide()
        self.sample_list_view.setFrameShape(qt.QListView.StyledPanel)
        self.sample_list_view.setFrameShadow(qt.QListView.Sunken)
        self.sample_list_view.setRootIsDecorated(1)
        self.sample_list_view.setSelected(self.sample_list_view.firstChild(), True)
        
        layout = qt.QVBoxLayout(self,0,0, 'main_layout')
        button_layout = qt.QHBoxLayout(None, 0, 0, 'button_layout')
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        layout.setSpacing(10)
        layout.addWidget(self.sample_list_view)
        self.buttons_grid_layout = qt.QGridLayout(2, 5)
        layout.addLayout(self.buttons_grid_layout)
        self.buttons_grid_layout.addLayout(button_layout, 0, 0)
        self.buttons_grid_layout.addWidget(self.delete_button, 0, 4)
        self.buttons_grid_layout.addWidget(self.collect_button, 1, 0)
        self.buttons_grid_layout.addWidget(self.continue_button, 1, 4)

        self.clearWState(qt.Qt.WState_Polished)
        
        qt.QObject.connect(self.up_button, qt.SIGNAL("clicked()"), self.up_click)
        qt.QObject.connect(self.down_button, qt.SIGNAL("clicked()"), self.down_click)
        qt.QObject.connect(self.delete_button, qt.SIGNAL("clicked()"), self.delete_click)
        qt.QObject.connect(self.collect_button, qt.SIGNAL("clicked()"), self.collect_stop_toggle)

        qt.QObject.connect(self.sample_list_view, qt.SIGNAL("selectionChanged()"),
                           self.sample_list_view_selection)

        qt.QObject.connect(self.sample_list_view,
                           qt.SIGNAL("contextMenuRequested(QListViewItem *, const QPoint& , int)"),
                           self.show_context_menu)

        qt.QObject.connect(self.sample_list_view, 
                           qt.SIGNAL("itemRenamed(QListViewItem *, int , const QString& )"),
                           self.item_renamed)

        qt.QObject.connect(self.sample_list_view,
                           qt.SIGNAL("doubleClicked(QListViewItem *, const QPoint &, int)"),
                           self.item_double_click)

        qt.QObject.connect(self.sample_list_view,
                           qt.SIGNAL("mouseButtonClicked(int, QListViewItem *, const QPoint &, int)"),
                           self.item_click)

        qt.QObject.connect(self.confirm_dialog, qt.PYSIGNAL("continue_clicked"),
                           self.collect_items)

        qt.QObject.connect(self.continue_button, qt.SIGNAL("clicked()"),
                           self.continue_button_click)

        self.sample_list_view.viewport().installEventFilter(self)
        self.setFixedWidth(415)

        self.collect_button.setDisabled(True)

    def eventFilter(self, _object, event):
        if event.type() == qt.QEvent.MouseButtonDblClick:
            self.show_details()
            return True
        else:
            return False

    def enable_collect(self, state):
        self.sample_list_view.setDisabled(not state)
        self.collect_button.setDisabled(not state)
        self.up_button.setDisabled(not state)
        self.down_button.setDisabled(not state)
        self.delete_button.setDisabled(not state)

    def show_context_menu(self, item, point, col):
        menu = qt.QPopupMenu(self.sample_list_view, "popup_menu")

        if item:
            if isinstance(item, queue_item.DataCollectionGroupQueueItem):
                menu.insertItem(qt.QString("Rename"), self.rename_list_view_item)
                menu.insertSeparator(1)
                menu.insertItem(qt.QString("Remove"), self.delete_click)
                menu.popup(point);
            elif isinstance(item, queue_item.SampleQueueItem):
                if not item.get_model().free_pin_mode:
                    if self.is_mounted_sample_item(item): 
                        menu.insertItem(qt.QString("Un-Mount"), self.unmount_sample)
                    else:
                        menu.insertItem(qt.QString("Mount"), self.mount_sample)
                       
                menu.insertSeparator(3)
                menu.insertItem(qt.QString("Details"), self.show_details) 
                menu.popup(point);
            else:
                menu.popup(point);
                menu.insertSeparator(2)
                menu.insertItem(qt.QString("Remove"), self.delete_click)
                menu.insertSeparator(4)
                menu.insertItem(qt.QString("Details"), self.show_details)
            
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
            if isinstance(item, queue_item.SampleQueueItem):
                self.tree_brick.show_sample_tab(item)
            elif isinstance(item, queue_item.DataCollectionQueueItem):
                self.tree_brick.show_datacollection_tab(item)
            elif isinstance(item, queue_item.CharacterisationQueueItem):
                self.tree_brick.show_edna_tab(item)
            elif isinstance(item, queue_item.EnergyScanQueueItem):
                self.tree_brick.show_energy_scan_tab(item)
            elif isinstance(item, queue_item.XRFScanQueueItem):
                self.tree_brick.show_xrf_scan_tab(item) 
            elif isinstance(item, queue_item.GenericWorkflowQueueItem):
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
                if 'SC3' in self.beamline_setup_hwobj.sample_changer_hwobj.__class__.__name__:
                  self.beamline_setup_hwobj.sample_changer_hwobj.\
                      unload(22, sample_location = location, wait = False)
                else:
                  self.beamline_setup_hwobj.sample_changer_hwobj.\
                      unload_sample(22, sample_location = location, wait = False)

            items[0].setOn(False)
            items[0].set_mounted_style(False)

    def sample_list_view_selection(self):
        items = self.get_selected_items()

        if len(items) == 1:
            item = items[0]
            
            #if item.deletable:
            #    self.delete_button.setDisabled(False)
            #else:
            #    self.delete_button.setDisabled(True)

        if len(items) > 1:
            for item in items:
                if isinstance(item, queue_item.DataCollectionGroupQueueItem) or \
                       isinstance(item, queue_item.DataCollectionQueueItem):
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
        queue_item.DataCollectionGroupQueueItem(samples[0], 
                                                samples[0].lastItem(),
                                                task_node.get_name())

    def get_item_by_model(self, parent_node):
        it = qt.QListViewItemIterator(self.sample_list_view)
        item = it.current()
    
        while item:
            if item.get_model() is parent_node:
                return item

            it += 1
            item = it.current()

        return self.sample_list_view

    def last_top_level_item(self):
        sibling = self.sample_list_view.firstChild()
        last_child = None

        while(sibling):
            last_child = sibling
            sibling = sibling.nextSibling()
            
        return last_child
        
    def add_to_view(self, parent, task):
        view_item = None
        parent_tree_item = self.get_item_by_model(parent)

        if parent_tree_item is self.sample_list_view:
            last_item = self.last_top_level_item()
        else:
            last_item = parent_tree_item.lastItem()
        
        cls = queue_item.MODEL_VIEW_MAPPINGS[task.__class__]

        if parent_tree_item.lastItem():
            view_item = cls(parent_tree_item, last_item,
                            task.get_display_name())
        else:
            view_item = cls(parent_tree_item, task.get_display_name())

        if isinstance (task, queue_model_objects.Basket):
            view_item.setOpen(False) #task.get_is_present())
        else:
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
        self.beamline_setup_hwobj.set_plate_mode(False)
        self.confirm_dialog.set_plate_mode(False)       
 
        if option == SC_FILTER_OPTIONS.SAMPLE_CHANGER:
            self.sample_list_view.clear()
            self.queue_model_hwobj.select_model('ispyb')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.MOUNTED_SAMPLE:
            loaded_sample = self.sample_changer_hwobj.\
                                 getLoadedSample()
            try:
                loaded_sample_loc = loaded_sample.getCoords()
            except:
                loaded_sample_loc = None

            it = qt.QListViewItemIterator(self.sample_list_view)
            item = it.current()
        
            while item:
                if isinstance(item, queue_item.SampleQueueItem):
                    if item.get_model().location == loaded_sample_loc:
                        item.setSelected(True)
                        item.setVisible(True)
                    else:
                        item.setVisible(False)

                it += 1
                item = it.current()

        elif option == SC_FILTER_OPTIONS.FREE_PIN:
            self.sample_list_view.clear()
            self.queue_model_hwobj.select_model('free-pin')
            self.set_sample_pin_icon()
        elif option == SC_FILTER_OPTIONS.PLATE:
            #self.sample_list_view.clear()
            #self.sample_list_view.setDisabled(True)
            self.beamline_setup_hwobj.set_plate_mode(True)
            self.confirm_dialog.set_plate_mode(True)       

        self.sample_list_view_selection()
        
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
            self.continue_button.setPaletteBackgroundColor(widget_colors.LIGHT_YELLOW)
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
                self.sample_list_view.setSelected(item, False)
            
            if len(checked_items):
                self.confirm_dialog.set_items(checked_items)
                self.confirm_dialog.show()
            else:
                message = "No data collections selected, please select one" + \
                          " or more data collections"

                qt.QMessageBox.information(self,
                                        "Data collection",
                                        message,
                                        "OK")
        else:
            self.stop_collection()

    def enable_sample_changer_widget(self, state):
        self.parent().sample_changer_widget.child('synch_button').setEnabled(state)
        self.parent().sample_changer_widget.child('centring_cbox').setEnabled(state)
        self.parent().sample_changer_widget.child('filter_cbox').setEnabled(state)

    def is_mounted_sample_item(self, item):
        result = False

        if isinstance(item, queue_item.SampleQueueItem):
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
        self.collect_button.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
        self.collect_button.setIconSet(qt.QIconSet(self.stop_pixmap))
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
        self.collect_button.setIconSet(qt.QIconSet(self.play_pixmap))
        self.collect_button.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.delete_button.setEnabled(True)
        self.enable_sample_changer_widget(True)
        self.parent().enable_hutch_menu(True)
        self.parent().enable_command_menu(True)
        self.parent().enable_task_toolbox(True)
        self.set_sample_pin_icon()

    def get_checked_items(self):
        res = queue_item.perform_on_children(self.sample_list_view,
                                          queue_item.is_checked,
                                          queue_item.get_item)

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

    def set_first_element(self):
        selected_items = self.get_selected_items()
        if len(selected_items) == 0:
            it = qt.QListViewItemIterator(self.sample_list_view)
            item = it.current()
            if item.get_model().free_pin_mode:
                self.sample_list_view.setSelected(self.sample_list_view.firstChild(), True)

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

    def samples_from_sc_content(self, sc_basket_content, sc_sample_content):
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
        self.queue_model_hwobj.clear_model('free-pin')
        self.queue_model_hwobj.select_model('free-pin')
        sample = queue_model_objects.Sample()
        sample.free_pin_mode = True
        sample.set_name('manually-mounted')
        self.queue_model_hwobj.add_child(self.queue_model_hwobj.get_model_root(),
                                         sample)

    def populate_list_view(self, basket_list, sample_list):
        self.queue_hwobj.clear()
        self.queue_model_hwobj.clear_model('ispyb')
        self.sample_list_view.clear()
        self.queue_model_hwobj.select_model('ispyb')
        for basket in basket_list:
            self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
                                             get_model_root(), basket)
            basket.set_enabled(False)
            basket.clear_sample_list()
            for sample in sample_list:
                if sample.location[0] == basket.get_location():
                     basket.add_sample(sample)
                     self.queue_model_hwobj.add_child(basket, sample)
                     sample.set_enabled(False)
            #sample.set_enabled(False)
            #self.queue_model_hwobj.add_child(self.queue_model_hwobj.\
            #                                 get_model_root(), sample)
        self.set_sample_pin_icon()
    
    def set_sample_pin_icon(self):
        it = qt.QListViewItemIterator(self.sample_list_view)
        item = it.current()

        while item:
            if self.is_mounted_sample_item(item):
                item.setSelected(True)
                item.set_mounted_style(True)
                #self.sample_list_view_selection()
            elif isinstance(item, queue_item.SampleQueueItem):
                item.set_mounted_style(False)
            if isinstance(item, queue_item.SampleQueueItem):
                if item.get_model().lims_location != (None, None):
                    item.setPixmap(0, self.ispyb_pixmap)
                    item.setText(0, item.get_model().loc_str + ' - ' \
                                 + item.get_model().get_display_name())
            elif isinstance(item, queue_item.BasketQueueItem):
                do_it = True
                child_item = item.firstChild()
                while child_item:
                    if child_item.firstChild():
                        do_it = False
                        break
                    child_item = child_item.nextSibling()
                if do_it:
                    item.setOn(False)
                #item.setText(0, item.get_model().get_display_name())
                #item.setEnabled(item.get_model().get_is_present())
                #print 'should %s %s %s %s' % ("open" if item.get_model().get_is_present() else "close", item.get_model(), item.get_model().location, item)
                #item.setOpen(item.get_model().get_is_present())
 
            it += 1
            item = it.current()

    def check_for_path_collisions(self):
        conflict = False
        it = qt.QListViewItemIterator(self.sample_list_view)
        item = it.current()

        while item:
            if item.isOn():
                pt = item.get_model().get_path_template()
                
                if pt:
                     path_conflict = self.queue_model_hwobj.\
                                check_for_path_collisions(pt)

                     if path_conflict:
                         conflict = True
                         item.setPixmap(0, self.caution_pixmap)
                     else:
                         item.setPixmap(0, qt.QPixmap())
                         
            it += 1
            item = it.current()

        return conflict
        
