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
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
import traceback

from PyQt4 import QtGui
from PyQt4 import QtCore

import queue_model_objects_v1 as queue_model_objects
import Qt4_GraphicsManager as graphics_manager

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_General'


class Qt4_HutchMenuBrick(BlissWidget):
    """
    Descript. : HutchMenuBrick is used to perform sample centring
    """ 
    SNAPSHOT_FORMATS = ('png', 'jpeg')

    def __init__(self, *args):
        """
        Descrip. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None
        self.beam_info_hwobj = None
        self.graphics_manager_hwobj = None
        self.collect_hwobj = None
        self.queue_hwobj = None

        # Internal values -----------------------------------------------------
        self.beam_position = [0, 0]
        self.beam_size = [0, 0]
        self.beam_shape = "Rectangular"
        self.pixels_per_mm = [0, 0]
        self.inside_data_collection =  False
        self.current_centring = None
        self.reset_methods = None
        self.successful_methods = None

        # Properties ----------------------------------------------------------
        self.addProperty('minidiff', 'string', '')
        self.addProperty('beamInfo', 'string', '')
        self.addProperty('collection', 'string', '')
        self.addProperty('graphicsManager', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('label', 'string', 'Sample centring')

        # Signals ------------------------------------------------------------
        self.defineSignal('newCentredPos', ())
        
        # Slots ---------------------------------------------------------------
       
        # Graphic elements ----------------------------------------------------
        self.main_frame = QtGui.QFrame()  
        self.main_frame.setFrameStyle(QtGui.QFrame.StyledPanel)
         
        self.button_centre = MenuButton(self.main_frame, "Centre")
        self.button_centre.setMinimumSize(QtCore.QSize(75, 50))

        self.button_accept = QtGui.QToolButton(self.main_frame)
        self.button_accept.setUsesTextLabel(True)
        self.button_accept.setText("Save")
        self.button_accept.setFixedSize(QtCore.QSize(75, 50))
        self.button_standard_color = \
             self.button_accept.palette().color(QtGui.QPalette.Window)

        self.button_reject = QtGui.QToolButton(self.main_frame)
        self.button_reject.setUsesTextLabel(True)
        self.button_reject.setText("Reject")
        self.button_reject.setFixedSize(QtCore.QSize(75, 50))
        self.button_reject.hide()

        self.button_snapshot = QtGui.QToolButton(self.main_frame)
        self.button_snapshot.setUsesTextLabel(True)
        self.button_snapshot.setText("Snapshot")
        self.button_snapshot.setFixedSize(QtCore.QSize(75, 50))

        self.button_toogle_phase = QtGui.QToolButton(self.main_frame)
        self.button_toogle_phase.setUsesTextLabel(True)
        self.button_toogle_phase.setText("MD phase")
        self.button_toogle_phase.setFixedSize(QtCore.QSize(75, 50))

        self.button_refresh_camera = QtGui.QToolButton(self.main_frame)
        self.button_refresh_camera.setUsesTextLabel(True)
        self.button_refresh_camera.setText("Camera")
        self.button_refresh_camera.setFixedSize(QtCore.QSize(75, 50))

        self.button_visual_align = QtGui.QToolButton(self.main_frame)
        self.button_visual_align.setUsesTextLabel(True)
        self.button_visual_align.setText("Realign")
        self.button_visual_align.setFixedSize(QtCore.QSize(75, 50))

        # Layout -------------------------------------------------------------- 
        self.main_frame_layout = QtGui.QVBoxLayout()
        self.main_frame_layout.addWidget(self.button_centre)
        self.main_frame_layout.addWidget(self.button_accept)
        self.main_frame_layout.addWidget(self.button_reject)
        self.main_frame_layout.addWidget(self.button_snapshot)
        self.main_frame_layout.addWidget(self.button_toogle_phase)
        self.main_frame_layout.addWidget(self.button_refresh_camera)
        self.main_frame_layout.addWidget(self.button_visual_align)
        self.main_frame_layout.addStretch(0)
        self.main_frame_layout.setSpacing(0)
        self.main_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.main_frame.setLayout(self.main_frame_layout)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.main_frame)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Qt signal/slot connections ------------------------------------------
        self.connect(self.button_centre, 
                     QtCore.SIGNAL("executeCommand"), 
                     self.centring_started_clicked)
        self.connect(self.button_centre, 
                     QtCore.SIGNAL("cancelCommand"), 
                     self.centring_cancel_clicked)
        self.button_accept.clicked.connect(self.accept_clicked)
        self.button_reject.clicked.connect(self.reject_clicked)
        self.button_snapshot.clicked.connect(self.save_snapshot_clicked)
        self.button_toogle_phase.clicked.connect(self.toggle_phase_clicked) 
        self.button_refresh_camera.clicked.connect(self.refresh_camera_clicked)
        self.button_visual_align.clicked.connect(self.visual_align_clicked)

        # Other ---------------------------------------------------------------
        self.instanceSynchronize("")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Event triggered when user property changed in the property
                    editor. 
        Args.     : property_name (string), old_value, new_value
        Return    : None
        """
        if property_name == 'minidiff':
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffReady'), self.minidiff_ready)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffNotReady'), self.minidiff_not_ready)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffStateChanged'), self.minidiff_state_changed)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringStarted'), self.centring_started)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringSuccessful'), self.centring_successful)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringAccepted'), self.centring_accepted)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringFailed'), self.centring_failed)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringMoving'), self.centring_moving)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringInvalid'), self.centring_invalid)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('centringSnapshots'), self.centring_snapshots)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('progressMessage'), self.minidiff_message)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('omegaReferenceChanged'), self.omega_reference_changed)
                self.disconnect(self.diffractometer_hwobj, QtCore.SIGNAL('zoomMotorPredefinedPositionChanged'), self.zoom_position_changed)
            self.diffractometer_hwobj = self.getHardwareObject(new_value)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffReady'), self.minidiff_ready)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffNotReady'), self.minidiff_not_ready)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('minidiffStateChanged'), self.minidiff_state_changed)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringStarted'), self.centring_started)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringSuccessful'), self.centring_successful)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringAccepted'), self.centring_accepted)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringFailed'), self.centring_failed)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringMoving'), self.centring_moving)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringInvalid'), self.centring_invalid)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('centringSnapshots'), self.centring_snapshots)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('progressMessage'), self.minidiff_message)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('omegaReferenceChanged'), self.omega_reference_changed)
                self.connect(self.diffractometer_hwobj, QtCore.SIGNAL('zoomMotorPredefinedPositionChanged'), self.zoom_position_changed)
                if self.diffractometer_hwobj.isReady():
                    self.minidiff_ready()
                else:
                    self.minidiff_not_ready()

                self.reset_methods = {self.diffractometer_hwobj.MANUAL3CLICK_MODE: self.manual_centre_reset}
                self.successful_methods = {self.diffractometer_hwobj.MANUAL3CLICK_MODE:None}
            else:
                self.minidiff_not_ready()
        elif property_name == "beamInfo":
            if self.beam_info_hwobj is not None:
                self.disconnect(self.beam_info_hwobj, QtCore.SIGNAL('beamInfoChanged'), self.beam_info_changed)
                self.disconnect(self.beam_info_hwobj, QtCore.SIGNAL('beamPosChanged'), self.beam_position_changed)
            self.beam_info_hwobj = self.getHardwareObject(new_value)
            if self.beam_info_hwobj is not None:
                self.connect(self.beam_info_hwobj, QtCore.SIGNAL('beamInfoChanged'), self.beam_info_changed)
                self.connect(self.beam_info_hwobj, QtCore.SIGNAL('beamPosChanged'), self.beam_position_changed)
        elif property_name == "graphicsManager":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('graphicsClicked'), self.image_clicked)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value) 
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('graphicsClicked'), self.image_clicked)
        elif property_name == "collection":
            self.collect_hwobj = self.getHardwareObject(new_value)
        elif property_name == 'icons':
            self.set_icons(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_icons(self, icons):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        icons_list = icons.split()
        try:
            self.button_centre.set_Icons(icons_list[0], icons_list[1])
            self.button_accept.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[2])))
            self.button_snapshot.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[3])))
            self.button_reject.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[4])))
            self.button_toogle_phase.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[5])))
            self.button_refresh_camera.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[6])))
            self.button_visual_align.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[7])))
        except IndexError:
            logging.getLogger().error("HutchMenuBrick: Unable to set icons")            

    def centring_started_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if (self.diffractometer_hwobj is not None and
            self.graphics_manager_hwobj is not None):
            self.diffractometer_hwobj.start_centring_method(\
                 self.diffractometer_hwobj.MANUAL3CLICK_MODE)
        else:
            logging.getLogger().error("HutchMenuBrick: Unable to start " +\
                                      "centring.Diffractometer or/and" +\
                                      " graphics hardware object are not defined")

    def save_snapshot_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        formats = ""
        for image_format in Qt4_HutchMenuBrick.SNAPSHOT_FORMATS:
            formats += "*.%s " % image_format
        formats = formats.strip()

        current_filename = os.path.join(self.directory, self.prefix)
        current_filename = current_filename + '_%d%s%s' % (self.file_index, \
                           os.path.extsep, self.formatType)
        filename = str(QtGui.QFileDialog.getSaveFileName(current_filename, \
            "Images (%s)" % formats, self, None, \
            "Choose a filename to save under", None, False))
        if len(filename):
            image_type = os.path.splitext(filename)[1].strip('.').upper()
            try:
                matrix = self.__drawing.matrix()
                zoom = 1
                if matrix is not None:
                    zoom = matrix.m11()
                img = self.__drawing.getPPP()
                logging.getLogger().info("Saving snapshot : %s", filename)
                #QubImageSave.save(filename, img, self.__drawing.canvas(), zoom, image_type)
            except:
                logging.getLogger().exception("HutchMenuBrick: error saving snapshot!")
                logging.getLogger().error("HutchMenuBrick: error saving snapshot!")
            else:
                self.formatType = image_type.lower()
                self.fileIndex += 1 

    def toggle_phase_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.diffractometer_hwobj is not None:
            self.diffractometer_hwobj.toggle_phase()

    def refresh_camera_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.diffractometer_hwobj is not None:
            self.diffractometer_hwobj.refresh_video()

    def visual_align_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.diffractometer_hwobj is not None:
            selected_shapes = self.shape_history_hwobj.selected_shapes.values()
            if len(selected_shapes) == 2:
                p1 = selected_shapes[0]
                p2 = selected_shapes[1]
                self.diffractometer_hwobj.visual_align(p1, p2)
            else:
                logging.getLogger("user_level_log").\
                                error("Select two centred position (CTRL click) to continue")

    def centring_cancel_clicked(self, reject=False):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.diffractometer_hwobj.cancel_centring_method(reject = reject)

    def accept_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        Qt4_widget_colors.set_widget_color(self.button_accept, 
                                           self.button_standard_color)
        self.button_accept.setEnabled(False)
        self.button_reject.setEnabled(False)
        self.diffractometer_hwobj.accept_centring()

    def reject_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        Qt4_widget_colors.set_widget_color(self.button_accept, 
                                           self.button_standard_color)
        self.button_reject.setEnabled(False)
        self.button_accept.setEnabled(False)
        self.diffractometer_hwobj.reject_centring()

    def centring_moving(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.is_moving = True
        self.button_accept.setEnabled(False)
        self.button_reject.setEnabled(False)

    def centring_invalid(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(None)
        self.button_accept.setEnabled(False)
        self.button_reject.setEnabled(False)

    def centring_accepted(self, state, centring_status):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.graphics_manager_hwobj.set_centring_state(False) 
        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(centring_status)
        self.button_accept.setEnabled(False)
        self.button_reject.setEnabled(False)
        if self.inside_data_collection:
            self.inside_data_collection = False
        beam_info = self.beam_info_hwobj.get_beam_info()	
	#if beam_info is not None:
	#    beam_info['size_x'] = beam_info['size_x'] * self.pixels_per_mm[0]
	#    beam_info['size_y'] = beam_info['size_y'] * self.pixels_per_mm[1]

        p_dict = {}
        if 'motors' in centring_status and \
                'extraMotors' in centring_status:
            p_dict = dict(centring_status['motors'],
                          **centring_status['extraMotors'])
        elif 'motors' in centring_status:
            p_dict = dict(centring_status['motors'])

        if p_dict:
            cpos = queue_model_objects.CentredPosition(p_dict)
            try:
                screen_pos = self.diffractometer_hwobj.\
                             motor_positions_to_screen(cpos.as_dict())

                point = graphics_manager.GraphicsItemCentredPoint(\
                        cpos, True, screen_pos[0], screen_pos[1])
                if point:
                    self.graphics_manager_hwobj.add_shape(point)
            except:
                logging.getLogger('HWR').\
                    exception('Could not get screen positons for %s' % cpos)
                traceback.print_exc()

        if self.queue_hwobj is not None:
            if self.queue_hwobj.is_executing():
                self.setEnabled(False)

    def centring_snapshots(self, state):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if state is None:
            self.is_shooting = True
            self.main_frame.setEnabled(False)
        else:
            self.is_shooting = False
            self.main_frame.setEnabled(True)

    def centring_started(self, method, flexible):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.setEnabled(True)
        self.emit(QtCore.SIGNAL("enableMinidiff"), (False,))
        if self.inside_data_collection:
            self.emit(QtCore.SIGNAL("centringStarted"), ())

        self.is_centring = True
        self.current_centring = method
        self.button_centre.command_started()
        self.button_accept.setEnabled(False)
        self.button_reject.setEnabled(False)

        if method == self.diffractometer_hwobj.MANUAL3CLICK_MODE:
            self.graphics_manager_hwobj.set_centring_state(True)
            #self.graphics_manager_hwobj.set_centring_state(True)

    def centring_successful(self, method, centring_status):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.button_centre.command_done()
        if self.current_centring is not None:
            self.current_centring = None

        self.button_accept.setEnabled(True)
        self.button_reject.setEnabled(True)
        if self.inside_data_collection:
            Qt4_widget_colors.set_widget_color(self.button_accept, 
                                               Qt4_widget_colors.LIGHT_GREEN)
            Qt4_widget_colors.set_widget_color(self.button_reject, 
                                               Qt4_widget_colors.LIGHT_RED)

        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(centring_status)

        self.is_moving = False
        self.main_frame.setEnabled(True)
        self.emit(QtCore.SIGNAL("enableMinidiff"), (True,))

        try:
            successful_method = self.successful_methods[method]
        except KeyError, diag:
            pass
        else:
            try:
                successful_method()
            except:
                pass

    def centring_failed(self, method, centring_status):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.clickedPoints = []

        self.button_centre.command_failed()
        if self.current_centring is not None:
            #    self.current_centring.setPaletteBackgroundColor(self.defaultBackgroundColor)
            self.current_centring = None

        self.button_accept.setEnabled(False)
        if self.inside_data_collection:
            Qt4_widget_colors.set_widget_color(self.button_accept, self.button_standart_color)
            self.button_reject.setEnabled(True)
            Qt4_widget_colors.set_widget_color(self.button_reject, QtCore.Qt.red)
        else:
            self.button_reject.setEnabled(False)

        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(centring_status)

        self.emit(QtCore.SIGNAL("enableMinidiff"), (True,))

        try:
            reset_method = self.reset_methods[method]
        except KeyError, diag:
            pass
        else:
            try:
                reset_method()
            except:
                pass

    def manual_centre_reset(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.resetPoints()

    # Handler for clicking the video when doing the 3-click centring
    def image_clicked(self, x, y):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.current_centring is not None:
            if (self.current_centring == self.diffractometer_hwobj.MANUAL3CLICK_MODE and
                self.diffractometer_hwobj.isReady()):
                points = self.diffractometer_hwobj.image_clicked(x, y)
                #    self.addPoint(x,y)
 
    def addPoint(self, x, y, xi, yi):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.clickedPoints.append((x, y, xi, yi))
        self.emitWidgetSynchronize()

    def resetPoints(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.clickedPoints = []
        self.emitWidgetSynchronize()

    def minidiff_ready(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.main_frame.setEnabled(True)

    def minidiff_not_ready(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if not self.button_centre.is_executing():
            self.main_frame.setEnabled(False)

    def minidiff_state_changed(self, state):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.button_centre.is_executing():
            return
        try:
            self.main_frame.setEnabled(state == self.diffractometer_hwobj.phiMotor.READY)
        except:
            pass

    def minidiff_message(self, msg = None):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        logging.getLogger().info(msg)

    def beam_position_changed(self, position):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if (self.diffractometer_hwobj is not None and 
            self.graphics_manager_hwobj is not None and
            position is not None):
            self.graphics_manager_hwobj.update_beam_position(position)

    def beam_info_changed(self, beam_info):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if (self.diffractometer_hwobj is not None and
            self.graphics_manager_hwobj is not None and
            beam_info is not None):
            self.graphics_manager_hwobj.update_beam_info(beam_info)

    def zoom_position_changed(self, position, offset):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.graphics_manager_hwobj is not None:
            self.pixels_per_mm = self.diffractometer_hwobj.get_pixels_per_mm()
            self.graphics_manager_hwobj.update_pixels_per_mm(self.pixels_per_mm) 

    def omega_reference_changed(self, omega_reference):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.graphics_manager_hwobj is not None:
            self.graphics_manager_hwobj.update_omega_reference(omega_reference)
            
class MenuButton(QtGui.QToolButton):
    """
    Descript. : 
    Args.     : 
    Return    : 
    """
    def __init__(self, parent, caption):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        QtGui.QToolButton.__init__(self, parent)
        self.executing = None
        self.run_icon = None
        self.stop_icon = None
        self.standard_color = self.palette().color(QtGui.QPalette.Window)
        self.setUsesTextLabel(True)
        self.setText(caption)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked()'), self.button_clicked)

    def set_Icons(self, icon_run, icon_stop):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.run_icon = QtGui.QIcon(Qt4_Icons.load(icon_run))
        self.stop_icon = QtGui.QIcon(Qt4_Icons.load(icon_stop))
        if self.executing:
            self.setIcon(self.stop_icon)
        else:
            self.setIcon(self.run_icon)

    def button_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.executing:
            self.emit(QtCore.SIGNAL('cancelCommand'), ())
        else:
            self.setEnabled(False)
            self.emit(QtCore.SIGNAL('executeCommand'), ())

    def command_started(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        Qt4_widget_colors.set_widget_color(self, QtCore.Qt.yellow)
        if self.stop_icon is not None:
            self.setIcon(self.stop_icon)
        self.executing = True
        self.setEnabled(True)

    def is_executing(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        return self.executing

    def command_done(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.executing = False
        Qt4_widget_colors.set_widget_color(self, self.standard_color)
        if self.run_icon is not None:
            self.setIcon(self.run_icon)
        self.setEnabled(True)

    def command_failed(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.command_done()
