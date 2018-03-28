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

import os
import logging
import traceback

from QtImport import *

import Qt4_GraphicsManager as graphics_manager
import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_task_toolbox_widget import TaskToolBoxWidget
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


class Qt4_TaskToolBoxBrick(BlissWidget):
    """
    Descript. : 
    """

    request_tree_brick = pyqtSignal()

    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        #self.graphics_manager_hwobj = None
        self.diffractometer_hwobj = None
        self.beamline_setup_hwobj = None
        self.queue_model_hwobj = None
        self.session_hwobj = None

        # Internal values -----------------------------------------------------
        self.ispyb_logged_in = False
        self.tree_brick = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("beamline_setup", "string", "/beamline-setup")
        self.addProperty("queue_model", "string", "/queue-model")
        self.addProperty("useOscStartCbox", "boolean", False)
        self.addProperty("useCompression", "boolean", False)
       
        # Signals -------------------------------------------------------------
        self.defineSignal("request_tree_brick", ())

        # Slots ---------------------------------------------------------------
        self.defineSlot("logged_in", ())
        self.defineSlot("set_session", ())
        self.defineSlot("selection_changed",())
        self.defineSlot("user_group_saved", ())
        self.defineSlot("set_tree_brick", ())

        # Graphic elements ----------------------------------------------------
        self.task_tool_box_widget = TaskToolBoxWidget(self)

        # Layout --------------------------------------------------------------
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.task_tool_box_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

        # Other --------------------------------------------------------------- 
        self.setEnabled(self.ispyb_logged_in)

    def set_expert_mode(self, state):
        self.task_tool_box_widget.set_expert_mode(state)

    def run(self):
        """
        Descript. : Overriding BaseComponents.BlissWidget (Framework-2 object) 
                    run method. 
        Args.     :
        Return.   : 
        """
        self.session_hwobj = self.beamline_setup_hwobj.session_hwobj
        if self.session_hwobj.session_id:
            self.setEnabled(True)

        self.request_tree_brick.emit() 

    def user_group_saved(self, new_user_group):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.session_hwobj.set_user_group(str(new_user_group))
        self.task_tool_box_widget.update_data_path_model()
        path = self.session_hwobj.get_base_image_directory() + "/" + str(new_user_group)
        msg = 'Image path is: %s' % path
        logging.getLogger('GUI').info(msg)

    @pyqtSlot(BlissWidget)
    def set_tree_brick(self, brick):
        self.tree_brick = brick
        self.task_tool_box_widget.set_tree_brick(brick)
    
    @pyqtSlot(int, str, str, int, str, str, bool)
    def set_session(self, session_id, t_prop_code = None, prop_number = None,
                    prop_id = None, start_date = None, prop_code = None, 
                    is_inhouse = None):
        """
        Descript. : Connected to the slot set_session and is called after a
                    request to get the current session from LIMS (ISPyB) is  
                    made. The signal is normally emitted by the brick that 
                    handles LIMS login, ie ProposalBrick.
                    The session_id is '' if no session could be retrieved.
        Args.     :
        Return.   :
        """
        if session_id is '':
            self.logged_in(True)


    @pyqtSlot(bool)
    def logged_in(self, logged_in):
        """
        Descript. : Handels the signal logged_in from the brick the handles 
                    LIMS (ISPyB) login, ie ProposalBrick. The signal is 
                    emitted when a user was succesfully logged in.
        Args.     :
        Return    :
        """
        self.ispyb_logged_in = logged_in
        
        if self.session_hwobj is not None:
            self.session_hwobj.set_user_group('')

        self.setEnabled(logged_in)
        self.task_tool_box_widget.ispyb_logged_in(logged_in)
    
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Overriding BaseComponents.BlissWidget (propertyChanged
                    obj.) run method.
        Args.     :
        Return    :
        """
        if property_name == 'beamline_setup':
            self.beamline_setup_hwobj = self.getHardwareObject(new_value)
            if self.beamline_setup_hwobj:
                if self.queue_model_hwobj:
                    self.beamline_setup_hwobj.queue_model_hwobj = self.queue_model_hwobj
                    self.task_tool_box_widget.set_beamline_setup(self.beamline_setup_hwobj)
                graphics_manager_hwobj = self.beamline_setup_hwobj.shape_history_hwobj
                if graphics_manager_hwobj:
                    graphics_manager_hwobj.connect('pointSelected', self.point_selected)
                    graphics_manager_hwobj.connect('pointDeleted', self.point_deleted) 
            else:
                logging.getLogger('GUI').error('Could not load beamline setup '+\
                                                          'check configuration !.')
        elif property_name == 'queue_model':
            self.queue_model_hwobj = self.getHardwareObject(new_value)
            if self.beamline_setup_hwobj:
                self.beamline_setup_hwobj.queue_model_hwobj = self.queue_model_hwobj
                self.task_tool_box_widget.set_beamline_setup(self.beamline_setup_hwobj)

        elif property_name == 'useOscStartCbox':
            self.task_tool_box_widget.use_osc_start_cbox(new_value)
        #elif property_name == 'useCompression':
        #    self.task_tool_box_widget.enable_compression(new_value)

    def selection_changed(self, items):
        """
        Descript. : Connected to the signal "selection_changed" of the 
                    TreeBrick. Called when the selection in the tree changes.
        Args.     :
        Return    :
        """
        self.task_tool_box_widget.selection_changed(items)

    def point_selected(self, selected_position):
        """
        Descript. : slot when point selected
        Args.     :
        Return    :
        """
        self.task_tool_box_widget.helical_page.\
            centred_position_selection(selected_position)
        self.task_tool_box_widget.discrete_page.\
            centred_position_selection(selected_position)
        self.task_tool_box_widget.char_page.\
            centred_position_selection(selected_position)
        self.task_tool_box_widget.energy_scan_page.\
            centred_position_selection(selected_position)
        self.task_tool_box_widget.xrf_spectrum_page.\
            centred_position_selection(selected_position)

        self.task_tool_box_widget.discrete_page.refresh_current_item()
        self.task_tool_box_widget.helical_page.refresh_current_item()
        self.task_tool_box_widget.char_page.refresh_current_item()
        self.task_tool_box_widget.energy_scan_page.refresh_current_item()
        self.task_tool_box_widget.xrf_spectrum_page.refresh_current_item()

    def point_deleted(self, shape):
        """
        Callback for the DrawingEvent object called when a shape is deleted.
        """
        self.task_tool_box_widget.helical_page.shape_deleted(shape) 
