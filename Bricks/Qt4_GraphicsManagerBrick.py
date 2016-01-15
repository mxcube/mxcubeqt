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

"""
"""
import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Graphics'


class Qt4_GraphicsManagerBrick(BlissWidget):
    """
    Descript. :
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None

        # Internal values -----------------------------------------------------
        self.__shape_map = {}
        self.__point_map = {}
        self.__line_map = {}
        self.__grid_map = {}
        self.__original_height = 300

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtGui.QGroupBox("Graphics items", self)
        self.manager_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
            'widgets/ui_files/Qt4_graphics_manager_layout.ui'))

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtGui.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.manager_widget)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
        self.main_groupbox.toggled.connect(\
             self.main_groupbox_toggled)
        self.manager_widget.change_color_button.clicked.connect(\
            self.change_color_clicked)
        self.manager_widget.display_all_button.clicked.connect(\
             self.display_all_button_clicked)
        self.manager_widget.hide_all_button.clicked.connect(\
             self.hide_all_button_clicked)
        self.manager_widget.clear_all_button.clicked.connect(\
             self.clear_all_button_clicked)

        self.manager_widget.create_point_start_button.clicked.connect(\
             self.create_point_start_button_clicked)
        self.manager_widget.create_point_accept_button.clicked.connect(\
             self.create_point_accept_button_clicked)
        self.manager_widget.create_line_button.clicked.connect(\
             self.create_line_button_clicked)
        self.manager_widget.draw_grid_button.clicked.connect(\
             self.draw_grid_button_clicked)

        #self.manager_widget.shapes_treewidget.currentItemChanged.connect(\
        #     self.shape_treewiget_current_item_changed)
        self.manager_widget.shapes_treewidget.itemClicked.connect(\
             self.shape_treewiget_item_clicked)
        self.manager_widget.shapes_treewidget.customContextMenuRequested.\
             connect(self.show_shape_treewidget_popup)

        self.manager_widget.hor_spacing_ledit.textChanged.connect(\
             self.grid_spacing_changed)
        self.manager_widget.ver_spacing_ledit.textChanged.connect(\
             self.grid_spacing_changed)
        self.manager_widget.move_left_button.clicked.connect(\
             self.grid_move_left_clicked)
        self.manager_widget.move_right_button.clicked.connect(\
             self.grid_move_right_clicked)
        self.manager_widget.move_up_button.clicked.connect(\
             self.grid_move_up_clicked)
        self.manager_widget.move_down_button.clicked.connect(\
             self.grid_move_down_clicked) 
 
        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        # by default manager is closed
        self.main_groupbox.setCheckable(True)
        self.main_groupbox.setChecked(False)
        self.main_groupbox_toggled(False)
        self.main_groupbox.setToolTip("Click to open/close item manager")

    def propertyChanged(self, property, oldValue, newValue):
        """
        Descript. :
        """
        if property == "mnemonic":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeCreated"), self.shape_created)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeDeleted"), self.shape_deleted)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeSelected"), self.shape_selected)
                self.disconnect(self.graphics_manager_hwobj, QtCore.SIGNAL("centringInProgress"), self.centring_in_progress_changed)
            self.graphics_manager_hwobj = self.getHardwareObject(newValue)
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeCreated"), self.shape_created)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeDeleted"), self.shape_deleted)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL("shapeSelected"), self.shape_selected)
                self.connect(self.graphics_manager_hwobj, QtCore.SIGNAL("centringInProgress"), self.centring_in_progress_changed)
            else:
                self.setEnabled(False)
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)

    def shape_created(self, shape, shape_type):
        """ 
        Descript. : adds information about shape in all shapes treewidget
                    and depending on shape type also information to
                    treewidget of all points/lines/grids
        """
        info_str_list = QtCore.QStringList()
        info_str_list.append(str(self.manager_widget.shapes_treewidget.topLevelItemCount() + 1))
        info_str_list.append(shape.get_display_name())
        info_str_list.append(str(True))
        info_str_list.append(str(True))
        info_str_list.append(str(shape.used_count)) 
        self.__shape_map[shape] = QtGui.QTreeWidgetItem(self.manager_widget.\
             shapes_treewidget, info_str_list)
        self.toggle_buttons_enabled()

        info_str_list = QtCore.QStringList()
        info_str_list.append(str(shape.index))
        if shape_type == "Point":
            info_str_list.append(str(shape.get_start_position())) 
            self.manager_widget.point_treewidget.clearSelection()
            point_treewidget_item = QtGui.QTreeWidgetItem(\
                 self.manager_widget.point_treewidget, info_str_list)
            point_treewidget_item.setSelected(True)
            self.__point_map[shape] = point_treewidget_item
        elif shape_type == "Line":
            (start_index, end_index) = shape.get_points_index()
            info_str_list.append("Point %d" % start_index)
            info_str_list.append("Point %d" % end_index)
            self.manager_widget.line_treewidget.clearSelection()
            line_treewidget_item = QtGui.QTreeWidgetItem(\
                 self.manager_widget.line_treewidget, info_str_list)
            line_treewidget_item.setSelected(True)
            self.__line_map[shape] = line_treewidget_item
        elif shape_type == "Grid":
            self.manager_widget.grid_treewidget.clearSelection()
            grid_treewidget_item = QtGui.QTreeWidgetItem(\
                 self.manager_widget.grid_treewidget, info_str_list)
            grid_treewidget_item.setSelected(True)
            self.__grid_map[shape] = grid_treewidget_item

    def shape_deleted(self, shape, shape_type):
        if self.__shape_map.get(shape): 
            item_index = self.manager_widget.shapes_treewidget.\
                 indexOfTopLevelItem(self.__shape_map[shape])
            self.__shape_map.pop(shape)
            self.manager_widget.shapes_treewidget.\
                 takeTopLevelItem(item_index) 
            if shape_type == "Point":
                item_index = self.manager_widget.point_treewidget.\
                    indexOfTopLevelItem(self.__point_map[shape])
                self.__point_map.pop(shape)
                self.manager_widget.point_treewidget.\
                    takeTopLevelItem(item_index)
            elif shape_type == "Line":
                item_index = self.manager_widget.line_treewidget.\
                    indexOfTopLevelItem(self.__line_map[shape])
                self.__line_map.pop(shape)
                self.manager_widget.line_treewidget.\
                     takeTopLevelItem(item_index)
            elif shape_type == "Grid":
                item_index = self.manager_widget.grid_treewidget.\
                    indexOfTopLevelItem(self.__grid_map[shape])
                self.__grid_map.pop(shape)
                self.manager_widget.grid_treewidget.\
                    takeTopLevelItem(item_index)
        self.toggle_buttons_enabled()

    def shape_selected(self, shape, selected_state):
        if shape in self.__shape_map:
            self.__shape_map[shape].setData(4, QtCore.Qt.DisplayRole, str(selected_state)) 
            self.__shape_map[shape].setSelected(selected_state)
            if self.__point_map.get(shape):
                self.__point_map[shape].setSelected(selected_state)
            if self.__line_map.get(shape):
                self.__line_map[shape].setSelected(selected_state)
            if self.__grid_map.get(shape):
                self.__grid_map[shape].setSelected(selected_state)
            self.manager_widget.change_color_button.setEnabled(\
                 len(self.graphics_manager_hwobj.get_selected_shapes()) > 0)

    def centring_in_progress_changed(self, centring_in_progress):
        if centring_in_progress:
            self.manager_widget.create_point_start_button.setIcon(\
             Qt4_Icons.load_icon("Delete"))
        else:
            self.manager_widget.create_point_start_button.setIcon(\
             Qt4_Icons.load_icon("VCRPlay2"))

    def main_groupbox_toggled(self, is_on):
        if is_on:
            self.setFixedHeight(self.__original_height)
        else:
            self.setFixedHeight(20)
  
    def change_color_clicked(self):
        color = QtGui.QColorDialog.getColor()
        if color.isValid():
            for item in self.graphics_manager_hwobj.get_selected_shapes():
                item.set_base_color(color)

    def display_all_button_clicked(self):
        for shape, treewidget_item in self.__shape_map.iteritems():
            shape.show()
            treewidget_item.setData(3, QtCore.Qt.DisplayRole, "True")

    def hide_all_button_clicked(self):
        for shape, treewidget_item in self.__shape_map.iteritems():
            shape.hide()
            treewidget_item.setData(3, QtCore.Qt.DisplayRole, "False")

    def clear_all_button_clicked(self):
        self.graphics_manager_hwobj.clear_all()
        
    def create_point_start_button_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=True)

    def create_point_accept_button_clicked(self):
        self.graphics_manager_hwobj.start_centring()

    def create_line_button_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def draw_grid_button_clicked(self):
        self.graphics_manager_hwobj.create_grid(self.get_spacing())

    def show_shape_treewidget_popup(self, item, point, col):
        menu = QtGui.QMenu(self.manager_widget.shapes_treewidget)

    def get_spacing(self):
        spacing = [0, 0]
        try:
           spacing[0] = float(self.manager_widget.hor_spacing_ledit.text())
           spacing[1] = float(self.manager_widget.ver_spacing_ledit.text())
        except:
           pass 
        return spacing

    def toggle_buttons_enabled(self):
        self.manager_widget.display_points_cbox.\
             setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_lines_cbox.\
             setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_grids_cbox.\
             setEnabled(len(self.__shape_map) > 0)

        self.manager_widget.display_all_button.\
             setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.hide_all_button.\
             setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.clear_all_button.\
             setEnabled(len(self.__shape_map) > 0)
 
    def shape_treewiget_item_clicked(self, current_item, column): 
        for key, value in self.__shape_map.iteritems():
            if value == current_item:
                key.toggle_selected()
        self.manager_widget.change_color_button.setEnabled(current_item is not None)

    def grid_spacing_changed(self, value):
        spacing = self.get_spacing()
        for grid_treewidget_item in self.manager_widget.grid_treewidget.selectedItems():
            grid_item = self.__grid_map.keys()[self.__grid_map.values().\
                        index(grid_treewidget_item)]
            grid_item.set_spacing(spacing) 

    def grid_move_left_clicked(self):
        self.move_selected_grids("left")

    def grid_move_right_clicked(self):
        self.move_selected_grids("right")

    def grid_move_up_clicked(self):
        self.move_selected_grids("up")
   
    def grid_move_down_clicked(self):
        self.move_selected_grids("down")

    def move_selected_grids(self, direction):
        spacing = self.get_spacing()
        for grid_treewidget_item in self.manager_widget.grid_treewidget.selectedItems():
            grid_item = self.__grid_map.keys()[self.__grid_map.values().\
                        index(grid_treewidget_item)]
            grid_item.move_by_pix(direction)
