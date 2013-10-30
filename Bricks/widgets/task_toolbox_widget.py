import logging
import qt
import queue_model_objects_v1 as queue_model_objects
import queue_item


from BlissFramework import Icons
from widgets.create_helical_widget import CreateHelicalWidget
from widgets.create_discrete_widget import CreateDiscreteWidget
from widgets.create_char_widget import CreateCharWidget
from widgets.create_energy_scan_widget import CreateEnergyScanWidget
from widgets.create_workflow_widget import CreateWorkflowWidget


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
        font = self.tool_box.font()
        font.setPointSize(10)
        self.tool_box.setFont(font)
        
        self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete",)
        self.discrete_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        self.char_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page")
        self.helical_page.setBackgroundMode(qt.QWidget.PaletteBackground)
        self.energy_scan_page = CreateEnergyScanWidget(self.tool_box, "energy_scan")
        self.workflow_page = CreateWorkflowWidget(self.tool_box, 'workflow')
        
        self.tool_box.addItem(self.discrete_page, "Discrete")
        self.tool_box.addItem(self.char_page, "Characterise")
        self.tool_box.addItem(self.helical_page, "Helical")
        self.tool_box.addItem(self.energy_scan_page, "Energy Scan")
        self.tool_box.addItem(self.workflow_page, "Advanced")

        self.add_pixmap = Icons.load("add_row.png")
        self.create_task_button = qt.QPushButton("  Add to queue", self)
        self.create_task_button.setIconSet(qt.QIconSet(self.add_pixmap))

        self.v_layout.addWidget(self.method_group_box)

        self.button_hlayout = qt.QHBoxLayout(None)
        self.spacer = qt.QSpacerItem(1, 20, qt.QSizePolicy.Expanding,
                                     qt.QSizePolicy.Minimum)
        self.button_hlayout.addItem(self.spacer)
        self.button_hlayout.addWidget(self.create_task_button)
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

        for i in range(0, self.tool_box.count()):
            self.tool_box.item(i).set_tree_brick(brick)

    def set_beamline_setup(self, beamline_setup_hwobj):
        self._beamline_setup_hwobj = beamline_setup_hwobj
        for i in range(0, self.tool_box.count()):
            self.tool_box.item(i).set_beamline_setup(beamline_setup_hwobj)

        self.shape_history = beamline_setup_hwobj.shape_history_hwobj
        self.workflow_page.set_workflow(beamline_setup_hwobj.workflow_hwobj)
        self.workflow_page.set_shape_history(beamline_setup_hwobj.shape_history_hwobj)
        self.energy_scan_page.set_energy_scan_hwobj(beamline_setup_hwobj.energy_hwobj)

        # Remove energy scan page from non tunable wavelentgh beamlines
        if not beamline_setup_hwobj.tunable_wavelength():
            self.tool_box.removeItem(self.energy_scan_page)
            self.energy_scan_page.hide()

    def ispyb_logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles LIMS (ISPyB)
        login, ie ProposalBrick. The signal is emitted when a user was 
        succesfully logged in.
        """
        for i in range(0, self.tool_box.count()):
            self.tool_box.item(i).ispyb_logged_in(logged_in)
            
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
                new_pt.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                    get_next_run_number(new_pt)

            self.tool_box.item(page_index).selection_changed(tree_items)
            self.previous_page_index = page_index

    def selection_changed(self, items):
        """
        Called by the parent widget when selection in the tree changes.
        """
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

                    if len(shapes):
                        for shape in shapes:
                            self.create_task(item.get_model(), shape)
                    else:
                        self.create_task(item.get_model())

            self.tool_box.currentItem().update_selection()

    def create_task(self, task_node, shape = None):
        # Selected item is a sample
        if isinstance(task_node, queue_model_objects.Sample):
            group_task_node = queue_model_objects.TaskGroup()
            current_item = self.tool_box.currentItem()

            if current_item is self.workflow_page:
                group_name = current_item._workflow_cbox.currentText()
            else:
                group_name = current_item._task_node_name

            group_task_node.set_name(group_name)
            num = task_node.get_next_number_for_name(group_name)
            group_task_node.set_number(num)

            self.tree_brick.queue_model_hwobj.add_child(task_node, group_task_node)
            self.create_task(group_task_node, shape)

        # Selected item is a task group
        elif isinstance(task_node, queue_model_objects.TaskGroup):
            sample = task_node.get_parent()
            task_list = self.tool_box.currentItem().create_task(sample, shape)

            for child_task_node in task_list:
                self.tree_brick.queue_model_hwobj.add_child(task_node, child_task_node)

        # The selected item is a task
        else:
            new_node = self.tree_brick.queue_model_hwobj.copy_node(task_node)
            self.tree_brick.queue_model_hwobj.add_child(task_node.get_parent(), new_node)

        pt = self.tool_box.currentItem()._path_template
        pt.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
            get_next_run_number(pt)
