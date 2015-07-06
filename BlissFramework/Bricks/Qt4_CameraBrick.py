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

from PyQt4 import QtGui
from PyQt4 import QtCore 

import Qt4_GraphicsManager

from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_Graphics'


class Qt4_CameraBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.camera_hwobj = None
        self.graphics_manager_hwobj = None

        # Internal values -----------------------------------------------------
        self.use_fixed_size = False
        self.graphics_items_initialized = None
        self.graphics_scene_size = None
        self.graphics_scene_fixed_size = None
        self.graphics_view = None
        self.graphics_camera_frame = None
        self.use_fixed_size = None 
        self.display_beam = None

        # Properties ----------------------------------------------------------       
        self.addProperty("graphicsManager", "string", "/Qt4_graphics-manager")
        self.addProperty("camera", "string", "")
        self.addProperty("fixedSize", "string", "")
        self.addProperty('displayBeam', 'boolean', True)
        self.addProperty('displayScale', 'boolean', True)
        self.addProperty('displayOmegaAxis', 'boolean', True)

        # Graphic elements-----------------------------------------------------
        self.info_widget = QtGui.QWidget(self)
        self.coord_label = QtGui.QLabel(":", self)
        self.info_label = QtGui.QLabel(self)

        self.popup_menu = QtGui.QMenu(self)
        self.measure_distance_action = self.popup_menu.addAction(\
             "Measure distance", self.measure_distance_clicked)
        self.measure_distance_action.setCheckable(True)
        self.popup_menu.addAction("Display histogram", self.display_histogram_toggled)
        self.popup_menu.addAction("Define histogram", self.define_histogram_clicked)
        self.popup_menu.popup(QtGui.QCursor.pos())

        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QtGui.QHBoxLayout(self.info_widget)
        _info_widget_hlayout.addWidget(self.coord_label)
        _info_widget_hlayout.addSpacing(10)
        _info_widget_hlayout.addWidget(self.info_label)
        _info_widget_hlayout.setSpacing(0)
        _info_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.info_widget.setLayout(_info_widget_hlayout)

        self.main_layout = QtGui.QVBoxLayout(self) 
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)   

        # Qt signal/slot connections -----------------------------------------

        # SizePolicies --------------------------------------------------------

        # Scene elements ------------------------------------------------------
        self.graphics_scene_centring_points = []
        self.setMouseTracking(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == "graphicsManager":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL('graphicsMouseMoved'), self.mouse_moved)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL('graphicsMouseMoved'), self.mouse_moved)
                self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
                self.graphics_camera_frame = self.graphics_manager_hwobj.get_camera_frame() 
                self.main_layout.addWidget(self.graphics_view) 
                self.main_layout.addWidget(self.info_widget)
        elif property_name == 'camera':
            if self.camera_hwobj is not None:
                self.disconnect(self.camera_hwobj, QtCore.SIGNAL('imageReceived'), self.image_received)
            self.camera_hwobj = self.getHardwareObject(new_value)
            if self.camera_hwobj is not None:
                self.graphics_scene_size = self.camera_hwobj.get_image_dimensions()
                self.set_scene_size()
                self.camera_hwobj.start_camera()
                self.connect(self.camera_hwobj, QtCore.SIGNAL('imageReceived'), self.image_received)
        elif property_name == 'fixedSize':
            try:
                self.graphics_scene_fixed_size = new_value.split()
                if len(self.graphics_scene_fixed_size) == 2:
                    self.graphics_scene_fixed_size = map(int, self.graphics_scene_fixed_size)
                    self.use_fixed_size = True
                    self.set_scene_size()
            except:
                pass 
        elif property_name == 'displayBeam':              
            self.display_beam = new_value
        elif property_name == 'displayScale':
            self.display_scale = new_value
            if self.graphics_manager_hwobj is not None:
                self.graphics_manager_hwobj.set_scale_visible(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def contextMenuEvent(self, event):
        self.popup_menu.popup(QtGui.QCursor.pos())

    def measure_distance_clicked(self):
        if self.measure_distance_action.isChecked():
            self.graphics_manager_hwobj.start_measure()
        else:
            self.graphics_manager_hwobj.stop_measure()

    def display_histogram_toggled(self):
        print "ff"

    def define_histogram_clicked(self):
        print 2

    def image_received(self, image):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pixmap_image = QtGui.QPixmap.fromImage(image)
        self.graphics_camera_frame.setPixmap(pixmap_image)
        if self.graphics_items_initialized is None:
            self.init_graphics_scene_items()
            self.graphics_items_initialized = True 

    def mouse_moved(self, x, y):
        self.coord_label.setText("%d : %d" %(x, y))

    def init_graphics_scene_items(self): 
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.set_scene_size()
        self.graphics_scene_beam_item = self.graphics_manager_hwobj.get_graphics_beam_item()
        self.graphics_scene_scale_item = self.graphics_manager_hwobj.get_scale_item()
        self.graphics_scene_omega_reference_item = self.graphics_manager_hwobj.get_omega_reference_item()

    def set_scene_size(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.use_fixed_size:
            scene_size = self.graphics_scene_fixed_size
        else:
            scene_size = self.graphics_scene_size
        if self.graphics_manager_hwobj:
            self.graphics_manager_hwobj.set_graphics_scene_size(scene_size)
