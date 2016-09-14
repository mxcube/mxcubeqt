import logging
import qt
import queue_item
import queue_model_objects_v1 as queue_model_objects

from BlissFramework import Icons
from widgets.create_helical_widget import CreateHelicalWidget
from widgets.create_discrete_widget import CreateDiscreteWidget
from widgets.create_char_widget import CreateCharWidget
from widgets.create_energy_scan_widget import CreateEnergyScanWidget
from widgets.create_xrf_spectrum_widget import CreateXRFSpectrumWidget
from widgets.create_workflow_widget import CreateWorkflowWidget
from queue_model_enumerables_v1 import EXPERIMENT_TYPE


class TaskToolBoxWidget(qt.QWidget):
    def __init__(self, parent = None, name = "task_toolbox"):
        qt.QWidget.__init__(self, parent, name)

        # Data atributes
        self.shape_history = None
        self.tree_brick = None
        self.previous_page_index = 0

        #Layout
        self.v_layout = qt.QVBoxLayout(self)
        self.v_layout.setSpacing(10)
        self.method_group_box = qt.QVGroupBox("Collection method", self)
        font = self.method_group_box.font()
        font.setPointSize(12)
        self.method_group_box.setFont(font)
    
        self.tool_box = qt.QToolBox(self.method_group_box , "tool_box")
        self.tool_box.setFixedWidth(475)
        font = self.tool_box.font()
        font.setPointSize(10)
        self.tool_box.setFont(font)

        self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete",)
        self.discrete_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        self.char_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page")
        self.helical_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        try:
            self.energy_scan_page = CreateEnergyScanWidget(self.tool_box, "energy_scan")
        except NameError:
            self.energy_scan_page = None

        self.xrf_spectrum_page = CreateXRFSpectrumWidget(self.tool_box, "xrf_spectrum")
        self.workflow_page = CreateWorkflowWidget(self.tool_box, 'workflow')
        
        self.tool_box.addItem(self.discrete_page, "Standard Collection")
        self.tool_box.addItem(self.char_page, "Characterisation")
        self.tool_box.addItem(self.helical_page, "Helical Collection")
        self.tool_box.addItem(self.energy_scan_page, "Energy Scan")
        self.tool_box.addItem(self.xrf_spectrum_page, "XRF Spectrum")
        self.tool_box.addItem(self.workflow_page, "Advanced")

        self.add_pixmap = Icons.load("add_row.png")
        self.create_task_button = qt.QPushButton("Add to queue", self)
        self.create_task_button.setIconSet(qt.QIconSet(self.add_pixmap))
        msg = "Add the collection method to the selected sample"
        qt.QToolTip.add(self.create_task_button, msg)
        
        self.v_layout.addWidget(self.method_group_box)

        self.button_hlayout = qt.QHBoxLayout(None)
        self.spacer = qt.QSpacerItem(1, 20, qt.QSizePolicy.Expanding,
                                     qt.QSizePolicy.Minimum)
        self.button_hlayout.addWidget(self.create_task_button)
        self.button_hlayout.addItem(self.spacer)
        self.method_group_box.layout().setSpacing(10)
        self.method_group_box.layout().addLayout(self.button_hlayout)

        qt.QObject.connect(self.create_task_button, qt.SIGNAL("clicked()"),
                           self.create_task_button_click)

        qt.QObject.connect(self.tool_box, qt.SIGNAL("currentChanged( int )"),
                           self.current_page_changed)

    def set_tree_brick(self, brick):
        """
        Sets the tree brick of each page in the toolbox.
        """
        self.tree_brick = brick

        self.tool_box.item(0).set_tree_brick(brick)
        #for i in range(0, self.tool_box.count()):
        #    self.tool_box.item(i).set_tree_brick(brick)

    def set_beamline_setup(self, beamline_setup_hwobj):
        self._beamline_setup_hwobj = beamline_setup_hwobj
        
        #for i in range(0, self.tool_box.count()):
        #    self.tool_box.item(i).set_beamline_setup(beamline_setup_hwobj)
        self.tool_box.item(0).set_beamline_setup(beamline_setup_hwobj)

        self.shape_history = beamline_setup_hwobj.shape_history_hwobj
        if beamline_setup_hwobj.workflow_hwobj:
            self.workflow_page.set_workflow(beamline_setup_hwobj.workflow_hwobj)
            self.workflow_page.set_shape_history(beamline_setup_hwobj.shape_history_hwobj)
        else:
            self.tool_box.removeItem(self.workflow_page)
            self.workflow_page.hide()

        if not beamline_setup_hwobj.data_analysis_hwobj:
            self.tool_box.removeItem(self.char_page)
            self.char_page.hide()
        self.tool_box.removeItem(self.helical_page)
        self.helical_page.hide()
        if not beamline_setup_hwobj.xrf_spectrum_hwobj:
            self.tool_box.removeItem(self.xrf_spectrum_page)
            self.xrf_spectrum_page.hide()

        # Remove energy scan page from non tunable wavelentgh beamlines
        if not beamline_setup_hwobj.tunable_wavelength():
            self.tool_box.removeItem(self.energy_scan_page)
            self.energy_scan_page.hide()
        else:
            self.energy_scan_page.set_energy_scan_hwobj(beamline_setup_hwobj.energyscan_hwobj)

    def update_data_path_model_multi(self):
        for i in range(0, self.tool_box.count()):
            item = self.tool_box.item(i)
            item.init_data_path_model()
            item.update_selection()

    def update_data_path_model(self):
        item = self.tool_box.item(0)
        item.init_data_path_model()
        item.update_selection()

            
    def ispyb_logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles LIMS (ISPyB)
        login, ie ProposalBrick. The signal is emitted when a user was 
        succesfully logged in.
        """
        self.tool_box.item(0).ispyb_logged_in(logged_in)
        #for i in range(0, self.tool_box.count()):
        #    self.tool_box.item(i).ispyb_logged_in(logged_in)
            
    def current_page_changed(self, page_index):
        tree_items =  self.tree_brick.get_selected_items()

        if len(tree_items) > 0:        
            tree_item = tree_items[0]

            # Get the directory form the previous page and update 
            # the new page with the direcotry and run_number from the old.
            # IFF sample or group selected.
            if isinstance(tree_item, queue_item.DataCollectionGroupQueueItem) or\
                    isinstance(tree_item, queue_item.SampleQueueItem):
                new_pt = self.tool_box.item(page_index)._path_template
                previous_pt = self.tool_box.item(self.previous_page_index)._path_template
                new_pt.directory = previous_pt.directory
                #issu #91 - carry over file prefix. Remove this comment later
                new_pt.base_prefix = previous_pt.base_prefix
                new_pt.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                    get_next_run_number(new_pt)

            self.tool_box.item(page_index).selection_changed(tree_items)
            self.previous_page_index = page_index

    def selection_changed(self, items):
        """
        Descript. : Called by the parent widget when selection in the tree changes.
                    It also enables/disables add to queue button.
                    If one tree item is selected then tool_box current page is set 
                    to the page associated to the item. For example if a energy scan 
                    item is selected then create_energy_scan tool box page is selected.
                    Add to queue is disable if sample centring is selected
        """
        if len(items) == 1:
            if isinstance(items[0], queue_item.SampleCentringQueueItem):
                self.create_task_button.setEnabled(False)
            else:
                self.create_task_button.setEnabled(True)   
            if isinstance(items[0], queue_item.DataCollectionQueueItem):
                data_collection = items[0].get_model()
                if data_collection.experiment_type == EXPERIMENT_TYPE.HELICAL:
                    self.tool_box.setCurrentItem(self.helical_page)
                else:
                    self.tool_box.setCurrentItem(self.discrete_page)
            elif isinstance(items[0], queue_item.CharacterisationQueueItem):
                self.tool_box.setCurrentItem(self.char_page)
            elif isinstance(items[0], queue_item.EnergyScanQueueItem):
                self.tool_box.setCurrentItem(self.energy_scan_page)
            elif isinstance(items[0], queue_item.XRFSpectrumQueueItem):
                self.tool_box.setCurrentItem(self.xrf_spectrum_page)
            elif isinstance(items[0], queue_item.GenericWorkflowQueueItem):
                self.tool_box.setCurrentItem(self.workflow_page)

        current_page = self.tool_box.currentItem()
        current_page.selection_changed(items)

    def create_task_button_click(self):
        if self.tool_box.currentItem().approve_creation():
            items = self.tree_brick.get_selected_items()

            if not items:
                logging.getLogger("user_level_log").\
                    warning("Select the sample or group you "\
                            "would like to add to.")
            else:
                for item in items:
                    shapes = self.shape_history.selected_shapes
                    task_model = item.get_model()

                    # Create a new group if sample is selected
                    if isinstance(task_model, queue_model_objects.Sample):
                        task_model = self.create_task_group(task_model)
                        if len(shapes):
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                            self.create_task(task_model)
                    elif isinstance(task_model, queue_model_objects.Basket):
                        for sample_node in task_model.get_sample_list():
                            child_task_model = self.create_task_group(sample_node)
                            if len(shapes):
                                for shape in shapes:
                                    self.create_task(child_task_model, shape)
                            else:
                                self.create_task(child_task_model) 
                    else:
                        if len(shapes):
                            for shape in shapes:
                                self.create_task(task_model, shape)
                        else:
                            self.create_task(task_model)


            self.tool_box.currentItem().update_selection()

    def create_task_group(self, task_model):
        group_task_node = queue_model_objects.TaskGroup()
        current_item = self.tool_box.currentItem()

        if current_item is self.workflow_page:
            group_name = current_item._workflow_cbox.currentText()
        else:
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
            task_list = self.tool_box.currentItem().create_task(sample, shape)

            for child_task_node in task_list:
                if isinstance(child_task_node, queue_model_objects.DataCollection):
                    for acq in child_task_node.acquisitions:
                        acq.acquisition_parameters.overlap = 0
                self.tree_brick.queue_model_hwobj.add_child(task_node, child_task_node)
        # The selected item is a task, make a copy.
        else:
            new_node = self.tree_brick.queue_model_hwobj.copy_node(task_node)
            self.tree_brick.queue_model_hwobj.add_child(task_node.get_parent(), new_node)
