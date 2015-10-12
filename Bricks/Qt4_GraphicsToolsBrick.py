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

from copy import deepcopy

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_Graphics'


class Qt4_GraphicsToolsBrick(BlissWidget):
    """
    Descript. : Brick is like a menu in the menuBar or/and in the toolbar
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None

        # Internal values -----------------------------------------------------
        self.target_menu = None

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '/Qt4_graphics-manager')
        self.addProperty('targetMenu', 'combo', ("menuBar", "toolBar", "both"), "menuBar")
        self.addProperty('menuPosition', 'integer', 1)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------

        # Layout --------------------------------------------------------------

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def run(self):
        self.tools_menu = QtGui.QMenu("Graphics tools", self)
        self.measure_distance_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("measure_distance"),
             "Measure distance", 
             self.measure_distance_clicked)
        self.measure_distance_action.setCheckable(True)
        self.measure_angle_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("measure_angle"),
             "Measure angle", 
             self.measure_angle_clicked)
        self.measure_angle_action.setCheckable(True)
        self.measure_area_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("measure_area"),
             "Measure area", 
             self.measure_area_clicked) 
        self.measure_area_action.setCheckable(True)

        self.tools_menu.addSeparator()
        self.create_point_click_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("VCRPlay2"),
             "Create point with 3 clicks",
             self.create_point_click_clicked)
        self.create_point_current_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("ThumpUp"),
             "Create point on current position", 
             self.create_point_current_clicked)
        self.create_line_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("Line.png"),
             "Create line",
             self.create_line_clicked)
        self.create_grid_drag_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("GridDrag"),
             "Create grid with drag and drop",
             self.create_grid_drag_clicked)
        self.create_grid_click_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("GridClick"),
             "Create grid with 2 clicks",
             self.create_grid_click_clicked) 
        self.create_grid_auto_action = self.tools_menu.addAction(
             Qt4_Icons.load_icon("GridAuto"),
             "Create auto grid",
             self.create_grid_auto_clicked) 

        if self.target_menu == "menuBar":
            BlissWidget._menuBar.addMenu(self.tools_menu)
        elif self.target_menu == "toolBar":
            for action in self.tools_menu.actions():
                BlissWidget._toolBar.addAction(action)
        else:
            BlissWidget._menuBar.addMenu(self.tools_menu)
            toolbar_actions = []
            for action in self.tools_menu.actions():
                BlissWidget._toolBar.addAction(action)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == "mnemonic":
            if self.graphics_manager_hwobj:
                self.disconnect(self.graphics_manager_hwobj, 
                                QtCore.SIGNAL('measureDistanceStateChanged'),
                                self.measure_distance_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('measureAngleStateChanged'),
                                self.measure_angle_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('measureAreaStateChanged'),
                                self.measure_area_state_changed)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            if self.graphics_manager_hwobj:
                self.connect(self.graphics_manager_hwobj, 
                                QtCore.SIGNAL('measureDistanceStateChanged'),
                                self.measure_distance_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('measureAngleStateChanged'),
                             self.measure_angle_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('measureAreaStateChanged'),
                             self.measure_area_state_changed)
           
        elif property_name == "targetMenu":
            self.target_menu = new_value
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def measure_distance_clicked(self):
        if self.measure_distance_action.isChecked():
            self.graphics_manager_hwobj.start_measure_distance(wait_click = True)
        else:
            self.graphics_manager_hwobj.stop_measure_distance() 

    def measure_angle_clicked(self):
        if self.measure_angle_action.isChecked():
            self.graphics_manager_hwobj.start_measure_angle(wait_click = True)
        else:
            self.graphics_manager_hwobj.stop_measure_angle() 

    def measure_area_clicked(self):
        if self.measure_area_action.isChecked():
            self.graphics_manager_hwobj.start_measure_area(wait_click = True)
        else:
            self.graphics_manager_hwobj.stop_measure_area()

    def measure_distance_state_changed(self, state):
        self.measure_distance_action.setChecked(state)
        self.measure_angle_action.setChecked(False)
        self.measure_area_action.setChecked(False)

    def measure_angle_state_changed(self, state):
        self.measure_distance_action.setChecked(False)
        self.measure_angle_action.setChecked(state)
        self.measure_area_action.setChecked(False)

    def measure_area_state_changed(self, state):
        self.measure_distance_action.setChecked(False)
        self.measure_angle_action.setChecked(False)
        self.measure_area_action.setChecked(state)

    def create_point_click_clicked(self): 
        self.graphics_manager_hwobj.start_centring(tree_click=True)

    def create_point_current_clicked(self):
        self.graphics_manager_hwobj.start_centring()

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def create_grid_drag_clicked(self):
        self.graphics_manager_hwobj.create_grid_drag()

    def create_grid_click_clicked(self):
        self.graphics_manager_hwobj.create_grid_click()

    def create_grid_auto_clicked(self):
        self.graphics_manager_hwobj.create_grid_auto()
    
