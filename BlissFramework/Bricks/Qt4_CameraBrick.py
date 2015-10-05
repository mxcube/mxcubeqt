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

from BlissFramework import Qt4_Icons
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
        self.measure_angle_action = self.popup_menu.addAction(\
             "Measure angle", self.measure_angle_clicked)
        self.measure_angle_action.setCheckable(True)
        self.measure_area_action = self.popup_menu.addAction(\
             "Measure area", self.measure_area_clicked)
        self.measure_area_action.setCheckable(True)         

        self.popup_menu.addSeparator()
        self.popup_menu.addAction("Display histogram", 
                                  self.display_histogram_toggled)
        self.popup_menu.addAction("Define histogram", 
                                  self.define_histogram_clicked)
        self.popup_menu.addSeparator()
        self.popup_menu.addAction(Qt4_Icons.load_icon("Point"),
                                  "Create centring point",
                                  self.create_centring_point_clicked)
        self.popup_menu.addAction(Qt4_Icons.load_icon("Line"),
                                  "Create helical line",
                                  self.create_line_clicked)
        self.popup_menu.addAction(Qt4_Icons.load_icon("GridDrag"),
                                  "Create grid with drag and drop",
                                  self.create_grid_drag_clicked)
        self.popup_menu.addAction(Qt4_Icons.load_icon("GridClick"),
                                  "Create grid with 2 click",
                                  self.create_grid_drag_clicked)

        self.popup_menu.popup(QtGui.QCursor.pos())

        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QtGui.QHBoxLayout(self.info_widget)
        _info_widget_hlayout.addWidget(self.coord_label)
        _info_widget_hlayout.addStretch(0)
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
        self.info_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Fixed)

        # Scene elements ------------------------------------------------------
        self.setMouseTracking(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == "graphicsManager":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, 
                                QtCore.SIGNAL('graphicsMouseMoved'),  
                                self.mouse_moved)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, 
                             QtCore.SIGNAL('graphicsMouseMoved'), 
                             self.mouse_moved)
                self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
                self.graphics_camera_frame = self.graphics_manager_hwobj.get_camera_frame() 
                self.main_layout.addWidget(self.graphics_view) 
                self.main_layout.addWidget(self.info_widget)
                self.set_fixed_size()
        elif property_name == 'fixedSize':
            try:
                fixed_size = map(int, new_value.split())
                if len(fixed_size) == 2:
                    self.fixed_size = fixed_size
                    self.set_fixed_size()
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

    def set_fixed_size(self):
        if self.fixed_size and self.graphics_manager_hwobj:
            self.graphics_manager_hwobj.set_graphics_scene_size(\
                 self.fixed_size, True)
            #self.setFixedSize(self.fixed_size[0], self.fixed_size[1])

    def contextMenuEvent(self, event):
        self.popup_menu.popup(QtGui.QCursor.pos())

    def measure_distance_clicked(self):
        if self.measure_distance_action.isChecked():
            self.graphics_manager_hwobj.start_measure_distance()
        else:
            self.graphics_manager_hwobj.stop_measure_distance()

    def measure_angle_clicked(self):
        if self.measure_angle_action.isChecked():
            self.graphics_manager_hwobj.start_measure_angle()
        else:
            self.graphics_manager_hwobj.stop_measure_angle()

    def measure_area_clicked(self):
        if self.measure_area_action.isChecked():
            self.graphics_manager_hwobj.start_measure_area()
        else:
            self.graphics_manager_hwobj.stop_measure_area()

    def display_histogram_toggled(self):
        print "ff"

    def define_histogram_clicked(self):
        print 2

    def mouse_moved(self, x, y):
        """
        Descript. :
        Args.     :
        Return    : 
        """
        self.coord_label.setText("X: <b>%d</b> Y: <b>%d</b>" %(x, y))

    def create_centring_point_clicked(self):
        self.graphics_manager_hwobj.create_point()

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def create_grid_drag_clicked(self):
        self.graphics_manager_hwobj.create_grid_drag()

    def create_grid_click_clicked(self):
        self.graphics_manager_hwobj.create_grid_click()
 
