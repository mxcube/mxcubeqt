import logging
import queue_item
import queue_entry
import queue_model_objects_v1 as queue_model_objects
import qt


from BlissFramework import Icons
from collections import namedtuple
from widgets.create_helical_widget import CreateHelicalWidget
from widgets.create_discrete_widget import CreateDiscreteWidget
from widgets.create_mesh_widget import CreateMeshWidget
from widgets.create_char_widget import CreateCharWidget
from widgets.create_energy_scan_widget import CreateEnergyScanWidget
from widgets.create_workflow_widget import CreateWorkflowWidget


class TaskToolBoxWidget(qt.QWidget):
    def __init__(self, parent = None, name = "task_toolbox"):
        qt.QWidget.__init__(self, parent, name)

        # Data atributes
        self.shape_history = None
        self.tree_brick = None

        #Layout
        self.v_layout = qt.QVBoxLayout(self)
        self.v_layout.setSpacing(10)
        self.method_group_box = qt.QVGroupBox("Collection method", self)
    
        #self.method_group_box.setFixedWidth(480)
        #self.method_group_box.setFixedHeight(850)
        self.tool_box = qt.QToolBox(self.method_group_box , "tool_box")

        self.discrete_page = CreateDiscreteWidget(self.tool_box, "Discrete",)
        self.discrete_page.setBackgroundMode(qt.QWidget.PaletteBackground)

        self.char_page = CreateCharWidget(self.tool_box, "Characterise")
        self.char_page.setBackgroundMode(qt.QWidget.PaletteBackground)

        self.helical_page = CreateHelicalWidget(self.tool_box, "helical_page")
        self.helical_page.setBackgroundMode(qt.QWidget.PaletteBackground)

        self.energy_scan_page = CreateEnergyScanWidget(self.tool_box, 
                                                       "energy_scan")

        self.workflow_page = CreateWorkflowWidget(self.tool_box,
                                                  'workflow')
        

        #self.mesh_page = CreateMeshWidget(self.tool_box, "Mesh")
        #self.mesh_page.setBackgroundMode(qt.QWidget.PaletteBackground)
      
        self.tool_box.addItem(self.discrete_page, "Discrete")
        self.tool_box.addItem(self.char_page, "Characterise")
        self.tool_box.addItem(self.helical_page, "Helical")
        self.tool_box.addItem(self.energy_scan_page, "Energy Scan")
        self.tool_box.addItem(self.workflow_page, "Workflow")
        #self.tool_box.addItem(self.mesh_page, "Mesh")

        self.add_pixmap = Icons.load("add_row.png")
        self.create_task_button = \
            qt.QPushButton("  Add to queue", self)
        self.create_task_button.setIconSet(qt.QIconSet(self.add_pixmap))

        self.v_layout.addWidget(self.method_group_box)

        self.button_hlayout = qt.QHBoxLayout(None)
        self.spacer = qt.QSpacerItem(1, 20, qt.QSizePolicy.Expanding,
                                     qt.QSizePolicy.Minimum)
        self.button_hlayout.addItem(self.spacer)
        self.button_hlayout.addWidget(self.create_task_button)
        self.method_group_box.layout().setSpacing(10)
        self.method_group_box.layout().addLayout(self.button_hlayout)
        #self.h_layout.addStretch()

        qt.QObject.connect(self.create_task_button, qt.SIGNAL("clicked()"),
                           self.create_task_button_click)


    def set_tree_brick(self, brick):
        """
        Sets the tree brick of each page in the toolbox.
        """
        self.tree_brick = brick
        self.helical_page.set_tree_brick(brick)
        self.discrete_page.set_tree_brick(brick)
        self.char_page.set_tree_brick(brick)
        self.energy_scan_page.set_tree_brick(brick)
        self.workflow_page.set_tree_brick(brick)


    def set_shape_history(self, shape_history):
        """
        Sets the shape_history of each page in the toolbox.
        """
        self.shape_history = shape_history
        self.helical_page.set_shape_history(shape_history)
        self.discrete_page.set_shape_history(shape_history)
        self.char_page.set_shape_history(shape_history)
        self.energy_scan_page.set_shape_history(shape_history)
        self.workflow_page.set_shape_history(shape_history)


    def set_session(self, session_hwobj):
        self.helical_page.set_session(session_hwobj)
        self.discrete_page.set_session(session_hwobj)
        self.char_page.set_session(session_hwobj)
        self.energy_scan_page.set_session(session_hwobj)
        self.workflow_page.set_session(session_hwobj)


    def set_bl_config(self, bl_config):
        self.helical_page.set_bl_config(bl_config)
        self.discrete_page.set_bl_config(bl_config)
        self.char_page.set_bl_config(bl_config)
        self.energy_scan_page.set_bl_config(bl_config)
        self.workflow_page.set_bl_config(bl_config)


    def ispyb_logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles LIMS (ISPyB)
        login, ie ProposalBrick. The signal is emitted when a user was 
        succesfully logged in.
        """
        self.discrete_page.ispyb_logged_in(logged_in)
        self.char_page.ispyb_logged_in(logged_in)
        self.helical_page.ispyb_logged_in(logged_in)
        self.energy_scan_page.ispyb_logged_in(logged_in)
        self.energy_scan_page.ispyb_logged_in(logged_in)
        self.workflow_page.ispyb_logged_in(logged_in)


    # def set_tunable_energy(self, state):
    #     self.tool_box.setItemEnabled(\
    #         self.tool_box.indexOf(self.energy_scan_page), state)

    #     self.helical_page.set_tunable_energy(state)
    #     self.discrete_page.set_tunable_energy(state)


    def set_energy_scan_hw_obj(self, mnemonic):
        self.energy_scan_page.set_energy_scan_hw_obj(mnemonic)

        
    def selection_changed(self, items):
        """
        Called by the parent widget when selection in the tree changes.
        """
        if items:
            item = items[0]            
            # Set current selected item in the relevant
            # toolbox widgets.
            self.discrete_page.selection_changed(item)
            self.char_page.selection_changed(item)
            self.helical_page.selection_changed(item)
            self.energy_scan_page.selection_changed(item)
            self.workflow_page.selection_changed(item)


    def create_task_button_click(self):
        items = self.tree_brick.get_selected_items()

        for item in items:
            self.create_task(item.get_model())
            self.tool_box.currentItem().selection_changed(item)


    def create_task(self, task_node):
        if self.tool_box.currentItem().approve_creation(): 
            if isinstance(task_node, queue_model_objects.Sample):
                group_task_node = self.tool_box.currentItem().\
                                  create_parent_task_node()
                self.tree_brick.queue_model_hwobj.add_child(task_node,
                                                            group_task_node)
                self.create_task(group_task_node)
                    
            elif isinstance(task_node, queue_model_objects.TaskGroup):
                sample = task_node.get_parent()
                task_list = self.tool_box.currentItem().\
                            create_task(task_node, sample)

                for child_task_node in task_list:
                    self.tree_brick.queue_model_hwobj.\
                        add_child(task_node, child_task_node)
