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

    def __init__(self, *args):
        """
        Descrip. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beam_info_hwobj = None
        self.graphics_manager_hwobj = None
        self.collect_hwobj = None
        self.queue_hwobj = None

        # Internal values -----------------------------------------------------
        self.beam_position = [0, 0]
        self.beam_size = [0, 0]
        self.beam_shape = "Rectangular"
        self.pixels_per_mm = [0, 0]
        self.inside_data_collection =  None
        self.full_centring_done = None  
        self.directory = "/tmp"
        self.prefix = "snapshot"
        self.file_index = 1
        self.format_type = "png"

        # Properties ----------------------------------------------------------
        self.addProperty('collection', 'string', '')
        self.addProperty('graphicsManager', 'string', '')
        self.addProperty('useAutoCentringButton', 'boolean', True)
        self.addProperty('useBeamMarkMoveButtons', 'boolean', True)

        # Signals -------------------------------------------------------------
        
        # Slots ---------------------------------------------------------------
       
        # Graphic elements ----------------------------------------------------
        self.centre_button = DuoStateButton(self, "Centre")
        self.centre_button.set_icons("VCRPlay2", "Delete")
        self.accept_button = MonoStateButton(self, "Save", "ThumbUp")
        self.standard_color = self.accept_button.palette().\
             color(QtGui.QPalette.Window)
        self.reject_button = MonoStateButton(self, "Reject", "ThumbDown")
        self.reject_button.hide()
        self.create_line_button = MonoStateButton(self, "Line", "Line")
        self.draw_grid_button = MonoStateButton(self, "Grid", "Grid")
        self.snapshot_button = MonoStateButton(self, "Snapshot", "Camera")
        self.refresh_camera_button = MonoStateButton(self, "Refresh", "Refresh")
        self.visual_align_button = MonoStateButton(self, "Align", "Align")
        self.select_all_button = MonoStateButton(self, "Select all", "Check")
        self.clear_all_button = MonoStateButton(self, "Clear", "Delete")
        self.auto_center_button = MonoStateButton(self, "Auto", "VCRPlay2")

        self.beam_position_widget = QtGui.QWidget(self)
        _move_mark_label = QtGui.QLabel("Beam mark", self.beam_position_widget)
        _move_left_button = MonoStateButton(self.beam_position_widget,
             None, "left_small.png", (23, 23))
        _move_left_button.setAutoRepeat(True)
        _move_right_button = MonoStateButton(self.beam_position_widget,
             None, "right_small.png", (23, 23))
        _move_right_button.setAutoRepeat(True)
        _move_up_button = MonoStateButton(self.beam_position_widget,
             None, "up_small.png", (23, 23))
        _move_up_button.setAutoRepeat(True)
        _move_down_button = MonoStateButton(self.beam_position_widget,
             None, "down_small.png", (23, 23))
        _move_down_button.setAutoRepeat(True)

        # Layout -------------------------------------------------------------- 
        _beam_position_widget_gridlayout = QtGui.QGridLayout(self.beam_position_widget)
        _beam_position_widget_gridlayout.addWidget(_move_mark_label, 0, 0, 1, 3, QtCore.Qt.AlignHCenter)
        _beam_position_widget_gridlayout.addWidget(_move_left_button, 2, 0)
        _beam_position_widget_gridlayout.addWidget(_move_up_button, 1, 1)
        _beam_position_widget_gridlayout.addWidget(_move_right_button, 2, 2)
        _beam_position_widget_gridlayout.addWidget(_move_down_button, 3, 1) 
        _beam_position_widget_gridlayout.setHorizontalSpacing(0)
        _beam_position_widget_gridlayout.setVerticalSpacing(0)
        _beam_position_widget_gridlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.centre_button)
        _main_vlayout.addWidget(self.accept_button)
        _main_vlayout.addWidget(self.reject_button)
        _main_vlayout.addWidget(self.create_line_button)
        _main_vlayout.addWidget(self.draw_grid_button)
        _main_vlayout.addWidget(self.snapshot_button)
        _main_vlayout.addWidget(self.refresh_camera_button)
        _main_vlayout.addWidget(self.visual_align_button)
        _main_vlayout.addWidget(self.select_all_button)
        _main_vlayout.addWidget(self.clear_all_button)
        _main_vlayout.addWidget(self.auto_center_button)
        _main_vlayout.addWidget(self.beam_position_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.centre_button.commandExecuteSignal.connect(self.centre_button_clicked)
        self.accept_button.clicked.connect(self.accept_clicked)
        self.reject_button.clicked.connect(self.reject_clicked)
        self.create_line_button.clicked.connect(self.create_line_clicked)
        self.draw_grid_button.clicked.connect(self.draw_grid_clicked)
        self.snapshot_button.clicked.connect(self.save_snapshot_clicked)
        self.refresh_camera_button.clicked.connect(self.refresh_camera_clicked)
        self.visual_align_button.clicked.connect(self.visual_align_clicked)
        self.select_all_button.clicked.connect(self.select_all_clicked)
        self.clear_all_button.clicked.connect(self.clear_all_clicked)
        self.auto_center_button.clicked.connect(self.auto_center_clicked)
        _move_left_button.clicked.connect(self.move_left_clicked)
        _move_right_button.clicked.connect(self.move_right_clicked)
        _move_up_button.clicked.connect(self.move_up_clicked)
        _move_down_button.clicked.connect(self.move_down_clicked)

        # Other ---------------------------------------------------------------
        self.centre_button.setToolTip("3 click centring (Ctrl+1)")
        self.accept_button.setToolTip("Accept 3 click centring or " \
             "create a point\nbased on current position (Ctrl+2)")
        self.reject_button.setToolTip("Reject centring")
        self.create_line_button.setToolTip("Create helical line between \n" + \
             "two points (Ctrl+3)")
        self.draw_grid_button.setToolTip("Create grid with drag and drop (Ctrl+4)")
        self.select_all_button.setToolTip("Select all centring points (Ctrl+7)")
        self.clear_all_button.setToolTip("Clear all items (Ctrl+8)")
        #self.instanceSynchronize("")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Event triggered when user property changed in the property
                    editor. 
        Args.     : property_name (string), old_value, new_value
        Return    : None
        """
        if property_name == "graphicsManager":
            if self.graphics_manager_hwobj:  
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringStarted'), self.centring_started)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringFailed'), self.centring_failed)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringSuccessful'), self.centring_successful)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('minidiffReady'), self.diffractometer_ready_changed)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value) 
            if self.graphics_manager_hwobj:
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringStarted'), self.centring_started)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringFailed'), self.centring_failed)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('centringSuccessful'), self.centring_successful)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('minidiffReady'), self.diffractometer_ready_changed)
        elif property_name == "collection":
            self.collect_hwobj = self.getHardwareObject(new_value)
        elif property_name == "useBeamMarkMoveButtons":
            self.beam_position_widget.setVisible(new_value) 
        elif property_name == "useAutoCentringButton":
            self.auto_center_button.setVisible(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def centre_button_clicked(self, state):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if state:
            self.graphics_manager_hwobj.start_centring(tree_click = True)
        else:
            self.graphics_manager_hwobj.cancel_centring(reject = False)
            self.accept_button.setEnabled(True)

    def save_snapshot_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        formats = ["*.%s" % unicode(format).lower() for format in \
                   QtGui.QImageWriter.supportedImageFormats()]

        current_filename = os.path.join(self.directory, self.prefix)
        current_filename = current_filename + '_%d%s%s' % (self.file_index, \
                           os.path.extsep, self.format_type)

        #dialog = QtGui.QFileDialog(self, "Open Directory", current_filename)
        #dialog.exec()  

        filename = QtCore.QString(QtGui.QFileDialog.getSaveFileName(\
            self, "Choose a filename to save under",
            current_filename, "Image files (%s)" % " ".join(formats)))

        if not filename.isEmpty():
            image_type = os.path.splitext(filename)[1].strip('.').upper()
            try:
                img = self.graphics_manager_hwobj.get_snapshot([])
                img.save(filename)
                logging.getLogger().info("Saving snapshot : %s", filename)
                #QubImageSave.save(filename, img, self.__drawing.canvas(), zoom, image_type)
            except:
                logging.getLogger().exception("HutchMenuBrick: error saving snapshot!")
                logging.getLogger().error("HutchMenuBrick: error saving snapshot!")
            else:
                self.formatType = image_type.lower()
                self.file_index += 1 

    def refresh_camera_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.graphics_manager_hwobj is not None:
            self.graphics_manager_hwobj.refresh_camera()

    def visual_align_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.graphics_manager_hwobj.start_visual_align()

    def select_all_clicked(self):
        """
        Descript. : Clears all shapes (points, lines and meshes)
        Args.     : 
        Return    : 
        """
        self.graphics_manager_hwobj.select_all_points()

    def clear_all_clicked(self):
        """
        Descript. : Clears all shapes (points, lines and meshes)
        Args.     : 
        Return    : 
        """
        self.graphics_manager_hwobj.clear_all() 

    def accept_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if self.full_centring_done:
            Qt4_widget_colors.set_widget_color(self.accept_button, 
                                               self.standard_color)
            self.reject_button.setEnabled(False)
            self.graphics_manager_hwobj.accept_centring()
            self.full_centring_done = False
        else:
            self.graphics_manager_hwobj.start_centring(tree_click=False)

    def reject_clicked(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        Qt4_widget_colors.set_widget_color(self.accept_button, 
                                           self.standard_color)
        self.reject_button.setEnabled(False)
        self.graphics_manager_hwobj.reject_centring()

    def centring_snapshots(self, state):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        if state is None:
            self.is_shooting = True
            self.setEnabled(False)
        else:
            self.is_shooting = False
            self.setEnabled(True)

    def centring_started(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.setEnabled(True)
        self.emit(QtCore.SIGNAL("enableMinidiff"), (False,))
        if self.inside_data_collection:
            self.emit(QtCore.SIGNAL("centringStarted"), ())
        self.centre_button.command_started()
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(True)

    def centring_successful(self, method, centring_status):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.full_centring_done = True
        self.centre_button.command_done()
        self.accept_button.setEnabled(True)
        self.reject_button.setEnabled(True)
        if self.inside_data_collection:
            Qt4_widget_colors.set_widget_color(self.accept_button, 
                                               Qt4_widget_colors.LIGHT_GREEN)
            Qt4_widget_colors.set_widget_color(self.reject_button, 
                                               Qt4_widget_colors.LIGHT_RED)

        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(centring_status)
        self.setEnabled(True)
        self.emit(QtCore.SIGNAL("enableMinidiff"), (True,))

    def centring_failed(self, method, centring_status):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.centre_button.command_failed()
        self.accept_button.setEnabled(False)
        if self.inside_data_collection:
            Qt4_widget_colors.set_widget_color(self.accept_button, self.button_standart_color)
            self.reject_button.setEnabled(True)
            Qt4_widget_colors.set_widget_color(self.reject_button, QtCore.Qt.red)
        else:
            self.reject_button.setEnabled(False)
        if self.collect_hwobj is not None:
            self.collect_hwobj.setCentringStatus(centring_status)
        #self.emit(QtCore.SIGNAL("enableMinidiff"), (True,))

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def draw_grid_clicked(self):
        self.graphics_manager_hwobj.create_grid()

    def diffractometer_ready_changed(self, is_ready):
        self.setEnabled(is_ready)

    def auto_center_clicked(self):
        self.graphics_manager_hwobj.start_auto_centring(self)

    def move_left_clicked(self):
        self.graphics_manager_hwobj.move_beam_mark("left")

    def move_right_clicked(self):
        self.graphics_manager_hwobj.move_beam_mark("right")

    def move_up_clicked(self):
        self.graphics_manager_hwobj.move_beam_mark("up")

    def move_down_clicked(self):
        self.graphics_manager_hwobj.move_beam_mark("down")    

class MonoStateButton(QtGui.QToolButton):

    def __init__(self, parent, caption=None, icon=None, fixed_size=(70, 50)):
        QtGui.QToolButton.__init__(self, parent)
        self.setUsesTextLabel(True)
        if fixed_size: 
            self.setFixedSize(fixed_size[0], fixed_size[1])
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        if caption:
            self.setText(caption)
        if icon:
            self.setIcon(Qt4_Icons.load_icon(icon))
            
class DuoStateButton(QtGui.QToolButton):
    """
    Descript. : 
    Args.     : 
    Return    : 
    """
    commandExecuteSignal = QtCore.pyqtSignal(bool)

    def __init__(self, parent, caption):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        QtGui.QToolButton.__init__(self, parent)
        self.executing = False
        self.run_icon = None
        self.stop_icon = None
        self.standard_color = self.palette().color(QtGui.QPalette.Window)
        self.setUsesTextLabel(True)
        self.setText(caption)
        self.setFixedSize(70, 50)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.clicked.connect(self.button_clicked)

    def set_icons(self, icon_run, icon_stop):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        self.run_icon = Qt4_Icons.load_icon(icon_run)
        self.stop_icon = Qt4_Icons.load_icon(icon_stop)
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
        self.commandExecuteSignal.emit(not self.executing)
        #if not self.executing:
        #    self.setEnabled(False)

    def command_started(self):
        """
        Descript. : 
        Args.     : 
        Return    : 
        """
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.LIGHT_YELLOW,
            QtGui.QPalette.Button) 
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
        Qt4_widget_colors.set_widget_color(self, self.standard_color,
            QtGui.QPalette.Button)
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
