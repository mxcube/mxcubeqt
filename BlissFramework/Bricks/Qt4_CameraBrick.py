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
        self.image_size = []
        self.graphics_items_initialized = None
        self.graphics_scene_size = None
        self.graphics_view = None
        self.graphics_camera_frame = None 
        self.display_beam = None

        # Properties ----------------------------------------------------------       
        self.addProperty("graphicsManager", "string", "/Qt4_graphics-manager")
        self.addProperty("camera", "string", "")
        self.addProperty("fixedSize", "string", "")
        self.addProperty('displayBeam', 'boolean', True)
        self.addProperty('displayScale', 'boolean', True)
        self.addProperty('displayOmegaAxis', 'boolean', True)

        # Graphic elements-----------------------------------------------------

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout() 
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)   

        # Qt signal/slot connections -----------------------------------------

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

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
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
            self.graphics_camera_frame = self.graphics_manager_hwobj.get_camera_frame() 
            self.main_layout.addWidget(self.graphics_view) 
        elif property_name == 'camera':
            if self.camera_hwobj is not None:
                self.disconnect(self.camera_hwobj, QtCore.SIGNAL('imageReceived'), self.image_received)
            self.camera_hwobj = self.getHardwareObject(new_value)
            if self.camera_hwobj is not None:
                self.graphics_scene_size = self.camera_hwobj.get_image_dimensions()
                self.camera_hwobj.start_camera()
                self.connect(self.camera_hwobj, QtCore.SIGNAL('imageReceived'), self.image_received)
        elif property_name == 'fixedSize':
            try:
                self.use_fixed_size = True
                scene_size = new_value.split()
                self.graphics_scene.setSceneRect(0, 0, 
                                                 int(self.scene_size[0]),
                                                 int(self.scene_size[1])) 
                self.graphics_scene_size = scene_size 
            except:
                pass 
        elif property_name == 'displayBeam':              
            self.display_beam = new_value
        elif property_name == 'displayScale':
            pass
            #self.graphics_scene_scale_item.set_visible(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

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

    def init_graphics_scene_items(self): 
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.graphics_manager_hwobj.set_graphics_scene_size(self.graphics_scene_size)
        self.graphics_scene_beam_item = self.graphics_manager_hwobj.get_graphics_beam_item()
        self.graphics_scene_scale_item = self.graphics_manager_hwobj.get_scale_item()
        self.graphics_scene_omega_reference_item = self.graphics_manager_hwobj.get_omega_reference_item()
