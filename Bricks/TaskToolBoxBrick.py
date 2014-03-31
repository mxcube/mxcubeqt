import os
import qt
import queue_model_objects_v1 as queue_model_objects
import logging
import traceback
import ShapeHistory as shape_history

from widgets.task_toolbox_widget import TaskToolBoxWidget
from BlissFramework import BaseComponents 

__category__ = 'mxCuBE_v3'

class TaskToolBoxBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        # Framwork-2 properties
        self.addProperty("beamline_setup", "string", "/beamline-setup")
        self.addProperty("queue_model", "string", "/queue-model")

        #Data atributes
        self.shape_history = None
        self.tree_brick = None
        self.ispyb_logged_in = False
        self.diffractometer_hwobj = None
        self.beamline_setup = None
        self.queue_model_hwobj = None
        self.session_hwobj = None
        
        #Signals
        self.defineSignal("getView", ())
        self.defineSignal("getTreeBrick",())

        #Slots
        self.defineSlot("logged_in", ())
        self.defineSlot("set_session", ())
        self.defineSlot("selection_changed",())
        self.defineSlot("new_centred_position", ())
        self.defineSlot("change_pixel_calibration", ())
        self.defineSlot("change_beam_position", ())
        self.defineSlot("user_group_saved", ())

        # Layout
        self.task_tool_box_widget = TaskToolBoxWidget(self)
        qt.QVBoxLayout(self)
        self.layout().addWidget(self.task_tool_box_widget)
        self.setEnabled(self.ispyb_logged_in)


    def run(self):
        """
        Overriding BaseComponents.BlissWidget (Framework-2 object) run method. 
        """
        # Get a reference to the TreeBrick.
        tree_brick = {}
        self.emit(qt.PYSIGNAL("getTreeBrick"), (tree_brick,))
        self.tree_brick = tree_brick.get('tree_brick', None)
        self.task_tool_box_widget.set_tree_brick(self.tree_brick)

        # Get a reference to the QUB view and setup 
        # helper classes for handling centred positions.
        d = {}
        self.emit(qt.PYSIGNAL("getView"), (d, ))
        self.task_tool_box_widget.workflow_page._grid_widget.connectToView(d)
        self.task_tool_box_widget.workflow_page._grid_widget._setColor(qt.QWidget.green)
        self.task_tool_box_widget.workflow_page.\
            _grid_widget._shape_history = self.shape_history
        
        self.shape_history.set_drawing(d.get('drawing', None))
        self.shape_history.get_drawing_event_handler().\
            selection_cb = self.shape_selected
        self.shape_history.get_drawing_event_handler().\
            deletion_cb = self.shape_deleted
        
        try:
            self.shape_history.get_drawing_event_handler().\
                move_to_centred_position_cb = self.diffractometer_hwobj.\
                                              moveToCentredPosition                            
        except AttributeError:
            logging.error('Could not get diffractometer_hwobj, check your configuration')
            traceback.print_exc()

        self.session_hwobj = self.beamline_setup_hwobj.session_hwobj
        if self.session_hwobj.session_id:
            self.setEnabled(True)

    def user_group_saved(self, new_user_group):
        self.session_hwobj.set_user_group(str(new_user_group))
        self.task_tool_box_widget.update_data_path_model()
        path = self.session_hwobj.get_base_image_directory() + "/" + str(new_user_group)
        msg = 'Image path is: %s' % path
        logging.getLogger('user_level_log').info(msg)
        
    def set_session(self, session_id, t_prop_code = None, prop_number = None,
                    prop_id = None, start_date = None, prop_code = None, 
                    is_inhouse = None):
        """
        Connected to the slot set_session and is called after a request to
        get the current session from LIMS (ISPyB) is made. The signal is 
        normally emitted by the brick that handles LIMS login, 
        ie ProposalBrick.

        The session_id is '' if no session could be retrieved.
        """
        if session_id is '':
            self.logged_in(True)


    def logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles LIMS (ISPyB)
        login, ie ProposalBrick. The signal is emitted when a user was 
        succesfully logged in.
        """
        self.ispyb_logged_in = logged_in
        
        if self.session_hwobj is not None:
            self.session_hwobj.set_user_group('')
            
        self.setEnabled(logged_in)
        self.task_tool_box_widget.ispyb_logged_in(logged_in)
        
    
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object) 
        run method.
        """
        if property_name == 'beamline_setup':
            self.beamline_setup_hwobj = self.getHardwareObject(new_value)

            if self.beamline_setup_hwobj:
                self.diffractometer_hwobj = self.beamline_setup_hwobj.diffractometer_hwobj
                
                if self.diffractometer_hwobj:
                    self.diffractometer_hwobj.connect("minidiffStateChanged",
                                                      self.diffractometer_changed)
                    
                self.shape_history = self.beamline_setup_hwobj.shape_history_hwobj

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
        self.task_tool_box_widget.workflow_page.\
            _grid_widget.ChangePixelCalibration(sizex, sizey)

    def change_beam_position(self, x, y):
        self.task_tool_box_widget.workflow_page.\
            _grid_widget.ChangeBeamPosition(x, y)

    def selection_changed(self, items):
        """
        Connected to the signal "selection_changed" of the TreeBrick. 
        Called when the selection in the tree changes.
        """
        self.task_tool_box_widget.selection_changed(items)

    def shape_selected(self, selected_positions):
        """
        Callback for the DrawingEvent object called when a shape is 
        selected.  
        """
        self.task_tool_box_widget.helical_page.\
            centred_position_selection(selected_positions)
        self.task_tool_box_widget.discrete_page.\
            centred_position_selection(selected_positions)
        self.task_tool_box_widget.\
            char_page.centred_position_selection(selected_positions)

    def shape_deleted(self, shape):
        """
        Callback for the DrawingEvent object called when a shape is deleted.
        """
        self.task_tool_box_widget.helical_page.shape_deleted(shape)

    def new_centred_position(self, state, centring_status):
        """
        Adds a new centred position, connected to the brick which handles
        centring (HutchMenuBrick).
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
            #self.position_history.add_centred_position(state, cpos)
            
            try:
                screen_pos = self.diffractometer_hwobj.\
                             motor_positions_to_screen(cpos.as_dict())

                point = shape_history.Point(self.shape_history.get_drawing(), 
                                         cpos, screen_pos)
                #qub_point = self.shape_history.draw_position(screen_pos)

                if point:
                    #self.shape_history.add_point(cpos, qub_point)
                    self.shape_history.add_shape(point)
            except:
                logging.getLogger('HWR').\
                    exception('Could not get screen positons for %s' % cpos)
                traceback.print_exc()

    def diffractometer_changed(self, *args):
        """
        Handles diffractometer change events, connected to the signal 
        minidiffStateChanged of the diffractometer hardware object.
        """
        if self.diffractometer_hwobj.isReady():
            for shape in self.shape_history.get_shapes():

                new_positions = []
                for cpos in shape.get_centred_positions():
                    new_x, new_y = self.diffractometer_hwobj.\
                        motor_positions_to_screen(cpos.as_dict())

                    new_positions.append((new_x, new_y))

                shape.move(new_positions)

            for shape in self.shape_history.get_shapes():
                shape.show()

        else:
            for shape in self.shape_history.get_shapes():
                shape.hide()
