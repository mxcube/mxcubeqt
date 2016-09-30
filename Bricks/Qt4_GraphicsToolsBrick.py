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

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Graphics'


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
        self.addProperty('beamDefiner', 'boolean', False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.define_beam_action = None
        self.move_beam_mark_manual_action = None
        self.move_beam_mark_auto_action = None

        # Layout --------------------------------------------------------------

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def run(self):
        self.tools_menu = QtGui.QMenu("Graphics", self)
        _measure_menu = self.tools_menu.addMenu("Measure")

        self.measure_distance_action = _measure_menu.addAction(
             Qt4_Icons.load_icon("measure_distance"),
             "Distance", 
             self.measure_distance_clicked)
        self.measure_angle_action = _measure_menu.addAction(
             Qt4_Icons.load_icon("measure_angle"),
             "Angle", 
             self.measure_angle_clicked)
        self.measure_area_action = _measure_menu.addAction(
             Qt4_Icons.load_icon("measure_area"),
             "Area", 
             self.measure_area_clicked) 

        _create_menu = self.tools_menu.addMenu("Create")
        aa_action = _create_menu.addAction(Qt4_Icons.load_icon("VCRPlay2"),
             "Centring point with 3 clicks", self.create_point_click_clicked)
        aa_action.setShortcut("Ctrl+1")
        temp_action = _create_menu.addAction(Qt4_Icons.load_icon("ThumbUp"),
             "Centring point on current position", self.create_point_current_clicked)
        temp_action.setShortcut("Ctrl+2")
        temp_action = _create_menu.addAction(Qt4_Icons.load_icon("Line.png"),
             "Helical line",self.create_line_clicked)
        temp_action.setShortcut("Ctrl+L")
        temp_action = _create_menu.addAction(Qt4_Icons.load_icon("Grid"),
             "Grid", self.create_grid_clicked)
        temp_action.setShortcut("Ctrl+G")
         
        self.tools_menu.addSeparator()

        temp_action = self.tools_menu.addAction("Select all centring points",
             self.select_all_points_clicked)
        temp_action.setShortcut("Ctrl+A")
        temp_action = self.tools_menu.addAction("Deselect all items",
             self.deselect_all_items_clicked)
        temp_action.setShortcut("Ctrl+D")
        temp_action = self.tools_menu.addAction("Clear all items",
             self.clear_all_items_clicked)
        temp_action.setShortcut("Ctrl+X")

        self.tools_menu.addSeparator()

        self.move_beam_mark_manual_action = self.tools_menu.addAction(
             "Set beam mark manualy", self.move_beam_mark_manual)
        self.move_beam_mark_manual_action.setEnabled(False)
        self.move_beam_mark_auto_action = self.tools_menu.addAction(
             "Set beam mark automaticaly", self.move_beam_mark_auto)
        self.move_beam_mark_auto_action.setEnabled(False)
        self.define_beam_action = self.tools_menu.addAction(\
             "Define beam size", self.define_beam_size)
        self.define_beam_action.setEnabled(self['beamDefiner'])

        self.tools_menu.addSeparator()

        self.display_grid_action = self.tools_menu.addAction(\
             "Display grid", self.display_grid_toggled)
        self.display_grid_action.setCheckable(True)

        self.image_scale_menu = self.tools_menu.addMenu("Image scale")
        self.image_scale_menu.setEnabled(False)

        #self.camera_control_action = self.tools_menu.addAction(\
        #     "Camera control", self.open_camera_control_dialog)
        #self.camera_control_action.setEnabled(False)

        if self.target_menu == "menuBar":
            BlissWidget._menuBar.insert_menu(self.tools_menu, 3)
        elif self.target_menu == "toolBar":
            for action in self.tools_menu.actions():
                BlissWidget._toolBar.addAction(action)
        else:
         
            BlissWidget._menuBar.insert_menu(self.tools_menu, 2)
            toolbar_actions = []
            for action in self.tools_menu.actions():
                BlissWidget._toolBar.addAction(action)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == "mnemonic":
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
        elif property_name == "targetMenu":
            self.target_menu = new_value
        #elif property_name == 'cameraControls':
        #    self.camera_control_action.setEnabled(new_value)
        #elif property_name == 'beamDefiner':
        #     self.define_beam_action.setEnabled(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_expert_mode(self, is_expert_mode):
        if self.move_beam_mark_manual_action:
            self.move_beam_mark_manual_action.setEnabled(is_expert_mode)
        if self.move_beam_mark_auto_action:
            self.move_beam_mark_auto_action.setEnabled(is_expert_mode)

    def measure_distance_clicked(self):
        self.graphics_manager_hwobj.start_measure_distance(wait_click = True)

    def measure_angle_clicked(self):
        self.graphics_manager_hwobj.start_measure_angle(wait_click = True)

    def measure_area_clicked(self):
        self.graphics_manager_hwobj.start_measure_area(wait_click = True)

    def create_point_click_clicked(self): 
        if self.isEnabled():
            self.graphics_manager_hwobj.start_centring(tree_click=True)

    def create_point_current_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.start_centring()

    def create_line_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.create_line()

    def create_grid_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.create_grid()

    def select_all_points_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.select_all_points()

    def deselect_all_items_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.de_select_all() 

    def clear_all_items_clicked(self):
        if self.isEnabled():
            self.graphics_manager_hwobj.clear_all()

    def move_beam_mark_manual(self):
        self.graphics_manager_hwobj.start_move_beam_mark()

    def move_beam_mark_auto(self):
        self.graphics_manager_hwobj.move_beam_mark_auto()

    def display_grid_toggled(self):
        self.graphics_manager_hwobj.display_grid(\
             self.display_grid_action.isChecked())

    def define_beam_size(self):
        self.graphics_manager_hwobj.start_define_beam()

    def open_camera_control_dialog(self):
        self.camera_control_dialog.show()
