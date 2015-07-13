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

from PyQt4 import QtGui
from PyQt4 import QtCore

import Qt4_GraphicsManager as graphics_manager
import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_task_toolbox_widget import TaskToolBoxWidget
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_General'


class Qt4_TaskToolBoxBrick(BlissWidget):
    """
    Descript. : 
    """
    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None
        self.diffractometer_hwobj = None
        self.beamline_setup_hwobj = None
        self.queue_model_hwobj = None
        self.session_hwobj = None

        # Internal values -----------------------------------------------------
        self.ispyb_logged_in = False
        self.tree_brick = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("beamline_setup", "string", "/Qt4_beamline-setup")
        self.addProperty("queue_model", "string", "/Qt4_queue-model")
       
        # Signals ------------------------------------------------------------  
        self.defineSignal("getView", ())
        self.defineSignal("getTreeBrick",())


        # Slots ---------------------------------------------------------------
        self.defineSlot("logged_in", ())
        self.defineSlot("set_session", ())
        self.defineSlot("selection_changed",())
        self.defineSlot("new_centred_position", ())
        self.defineSlot("user_group_saved", ())

        # Graphic elements ----------------------------------------------------
        self.task_tool_box_widget = TaskToolBoxWidget(self)

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.task_tool_box_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.MinimumExpanding)

        # Other --------------------------------------------------------------- 
        self.setEnabled(self.ispyb_logged_in)


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

        tree_brick = {}
        self.emit(QtCore.SIGNAL("getTreeBrick"), tree_brick)
        self.tree_brick = tree_brick.get('tree_brick', None)
        self.task_tool_box_widget.set_tree_brick(self.tree_brick)

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
        logging.getLogger('user_level_log').info(msg)
        
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
        #self.task_tool_box_widget.ispyb_logged_in(logged_in)
        
    
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
                self.diffractometer_hwobj = self.beamline_setup_hwobj.diffractometer_hwobj
                
                if self.diffractometer_hwobj:
                    self.diffractometer_hwobj.connect("minidiffStateChanged",
                                                      self.diffractometer_changed)
                    
                self.graphics_manager_hwobj = self.beamline_setup_hwobj.shape_history_hwobj

                if self.queue_model_hwobj:
                    self.beamline_setup_hwobj.queue_model_hwobj = self.queue_model_hwobj
                    self.task_tool_box_widget.set_beamline_setup(self.beamline_setup_hwobj)
            else:
                logging.getLogger('user_level_log').error('Could not load beamline setup '+\
                                                          'check configuration !.')
        elif property_name == 'queue_model':

            self.queue_model_hwobj = self.getHardwareObject(new_value)

            if self.beamline_setup_hwobj:
                self.beamline_setup_hwobj.queue_model_hwobj = self.queue_model_hwobj
                self.task_tool_box_widget.set_beamline_setup(self.beamline_setup_hwobj)

    def change_pixel_calibration(self, sizex, sizey):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pass
        #self.task_tool_box_widget.workflow_page.\
        #    _grid_widget.ChangePixelCalibration(sizex, sizey)

    def change_beam_position(self, x, y):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pass
        #self.task_tool_box_widget.workflow_page.\
        #    _grid_widget.ChangeBeamPosition(x, y)

    def selection_changed(self, items):
        """
        Descript. : Connected to the signal "selection_changed" of the 
                    TreeBrick. Called when the selection in the tree changes.
        Args.     :
        Return    :
        """
        self.task_tool_box_widget.selection_changed(items)

    def shape_selected(self, selected_positions):
        """
        Descript. : Callback for the DrawingEvent object called when 
                    a shape is selected.  
        Args.     :
        Return    :
        """
        self.task_tool_box_widget.helical_page.\
            centred_position_selection(selected_positions)
        self.task_tool_box_widget.discrete_page.\
            centred_position_selection(selected_positions)
        self.task_tool_box_widget.\
            char_page.centred_position_selection(selected_positions)

    def shape_deleted(self, shape):
        """
        Descript. : Callback for the DrawingEvent object called when a shape
                    is deleted.
        Args.     :
        Return    :
        """
        self.task_tool_box_widget.helical_page.shape_deleted(shape)

    def new_centred_position(self, state, centring_status):
        """
        Descript. : Adds a new centred position, connected to the brick which
                    handles centring (HutchMenuBrick).
        Args.     :
        Return    :
        """
        p_dict = {}

        if 'motors' in centring_status and \
                'extraMotors' in centring_status:

            p_dict = dict(centring_status['motors'], 
                          **centring_status['extraMotors'])

        elif 'motors' in centring_status:
            p_dict = dict(centring_status['motors']) 

        if p_dict:
            cpos = queue_model_objects.CentredPosition(p_dict)
            screen_pos = self.diffractometer_hwobj.\
                    motor_positions_to_screen(cpos.as_dict())
            point = graphics_manager.GraphicsItemPoint( 
                    cpos, True, screen_pos[0], screen_pos[1])
            if point:
                self.graphics_manager_hwobj.add_shape(point)
                cpos.set_index(point.index)

    def diffractometer_changed(self, *args):
        """
        Descript. : Handles diffractometer change events, connected to the 
                    signal minidiffStateChanged of the diffractometer hardware 
                    object.
        Args.     :
        Return    :
        """
        if self.diffractometer_hwobj.isReady():
            for shape in self.graphics_manager_hwobj.get_shapes():
                for cpos in shape.get_centred_positions():
                    new_x, new_y = self.diffractometer_hwobj.\
                        motor_positions_to_screen(cpos.as_dict())
                shape.set_position(new_x, new_y)

            for shape in self.graphics_manager_hwobj.get_shapes():
                shape.show()

        else:
            for shape in self.graphics_manager_hwobj.get_shapes():
                shape.hide()
