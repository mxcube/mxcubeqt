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
        self.graphics_items_initialized = None
        self.graphics_scene_size = None
        self.graphics_scene_fixed_size = None
        self.graphics_view = None
        self.graphics_camera_frame = None
        self.fixed_size = None 
        self.use_fixed_size = None 
        self.display_beam = None

        # Properties ----------------------------------------------------------       
        self.addProperty("mnemonic", "string", "/Qt4_graphics-manager")
        self.addProperty("fixedSize", "string", "")
        self.addProperty('displayBeam', 'boolean', True)
        self.addProperty('displayScale', 'boolean', True)
        self.addProperty('displayOmegaAxis', 'boolean', True)

        # Graphic elements-----------------------------------------------------
        self.info_widget = QtGui.QWidget(self)
        self.coord_label = QtGui.QLabel(":", self)
        self.info_label = QtGui.QLabel(self)

        self.popup_menu = QtGui.QMenu(self)
        create_menu = self.popup_menu.addMenu("Create")
        temp_action = create_menu.addAction("Centring point with 3 clicks",
            self.create_point_click_clicked)
        temp_action.setShortcut("Ctrl+1")
        temp_action = create_menu.addAction("Centring point on current position",
            self.create_point_current_clicked)
        temp_action.setShortcut("Ctrl+2")
        temp_action = create_menu.addAction("Helical line",
            self.create_line_clicked)
        temp_action.setShortcut("Ctrl+3")
        temp_action = create_menu.addAction("Grid with drag and drop",
            self.create_grid_drag_clicked)
        temp_action.setShortcut("Ctrl+4")

        measure_menu = self.popup_menu.addMenu("Measure")
        self.measure_distance_action = measure_menu.addAction(\
             "Distance", self.measure_distance_clicked)
        self.measure_distance_action.setCheckable(True)
        self.measure_angle_action = measure_menu.addAction(\
             "Angle", self.measure_angle_clicked)
        self.measure_angle_action.setCheckable(True)
        self.measure_area_action = measure_menu.addAction(\
             "Area", self.measure_area_clicked)
        self.measure_area_action.setCheckable(True)         

        self.popup_menu.addSeparator()

        self.move_beam_mark_action = self.popup_menu.addAction(\
             "Move beam mark", self.move_beam_mark_toggled)
        self.display_histogram_action = self.popup_menu.addAction(\
             "Display histogram", self.display_histogram_toggled)
        self.define_histogram_action = self.popup_menu.addAction(\
             "Define histogram", self.define_histogram_clicked)
        self.popup_menu.addSeparator()

        temp_action = self.popup_menu.addAction(\
             "Select all centring points",
             self.select_all_points_clicked)
        temp_action.setShortcut("Ctrl+7")
        temp_action = self.popup_menu.addAction(\
             "Deselect all items",
             self.deselect_all_items_clicked)
        temp_action.setShortcut("Ctrl+8")
        temp_action = self.popup_menu.addAction(\
             "Clear all items",
             self.clear_all_items_clicked)
        temp_action.setShortcut("Ctrl+9")

        self.display_histogram_action.setEnabled(False)
        self.define_histogram_action.setEnabled(False)

        self.image_scale_menu = self.popup_menu.addMenu("Image scale")
        self.image_scale_menu.setEnabled(False) 
        
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
        if property_name == "mnemonic":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(self.graphics_manager_hwobj, 
                                QtCore.SIGNAL('mouseMoved'),  
                                self.mouse_moved)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('measureDistanceStateChanged'),
                                self.measure_distance_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('measureAngleStateChanged'),
                                self.measure_angle_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('measureAreaStateChanged'),
                                self.measure_area_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('moveBeamMarkStateChanged'),
                                self.move_beam_mark_state_changed)
                self.disconnect(self.graphics_manager_hwobj,
                                QtCore.SIGNAL('imageScaleChanged'),        
                                self.image_scaled)
            self.graphics_manager_hwobj = self.getHardwareObject(new_value)
            if self.graphics_manager_hwobj is not None:
                self.connect(self.graphics_manager_hwobj, 
                             QtCore.SIGNAL('mouseMoved'), 
                             self.mouse_moved)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('measureDistanceStateChanged'),
                             self.measure_distance_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('measureAngleStateChanged'),
                             self.measure_angle_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('measureAreaStateChanged'),
                             self.measure_area_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('moveBeamMarkStateChanged'),
                             self.move_beam_mark_state_changed)
                self.connect(self.graphics_manager_hwobj,
                             QtCore.SIGNAL('imageScaleChanged'),
                             self.image_scaled)
                self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
                self.graphics_camera_frame = self.graphics_manager_hwobj.get_camera_frame() 
                self.main_layout.addWidget(self.graphics_view) 
                self.main_layout.addWidget(self.info_widget)
                self.set_fixed_size()
                self.init_image_zoom_list()
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

    def image_scaled(self, scale_value):
        for index, action in enumerate(self.image_scale_menu.actions()):
            action.setChecked(scale_value == self.image_scale_list[index])

    def init_image_zoom_list(self):
        self.image_scale_list = self.graphics_manager_hwobj.get_image_scale_list()
        if len(self.image_scale_list) > 0:
            self.image_scale_menu.setEnabled(True)
            self.image_scale_menu.triggered.connect(self.image_scale_triggered)
            for scale in self.image_scale_list:
                #probably there is a way to use a single method for all actions
                # by passing index. lambda function at first try did not work  
                self.image_scale_menu.addAction("%d %%" % (scale * 100), self.not_used_function)
            for action in self.image_scale_menu.actions():
                action.setCheckable(True)
            self.image_scaled(self.graphics_manager_hwobj.get_image_scale())

    def not_used_function(self, *arg):
        pass

    def image_scale_triggered(self, selected_action):
        for index, action in enumerate(self.image_scale_menu.actions()):
            if selected_action == action:
                self.graphics_manager_hwobj.set_image_scale(self.image_scale_list[index], action.isChecked())
                
    def contextMenuEvent(self, event):
        self.popup_menu.popup(QtGui.QCursor.pos())

    def measure_distance_clicked(self):
        if self.measure_distance_action.isChecked():
            self.graphics_manager_hwobj.start_measure_distance(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_distance()

    def measure_angle_clicked(self):
        if self.measure_angle_action.isChecked():
            self.graphics_manager_hwobj.start_measure_angle(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_angle()

    def measure_area_clicked(self):
        if self.measure_area_action.isChecked():
            self.graphics_manager_hwobj.start_measure_area(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_area()

    def display_histogram_toggled(self):
        return

    def define_histogram_clicked(self):
        return

    def create_point_click_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=True)

    def create_point_current_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=False)

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def create_grid_drag_clicked(self):
        self.graphics_manager_hwobj.create_grid_drag()

    def move_beam_mark_toggled(self):
        self.graphics_manager_hwobj.start_move_beam_mark()

    def mouse_moved(self, x, y):
        self.coord_label.setText("X: <b>%d</b> Y: <b>%d</b>" %(x, y))

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

    def move_beam_mark_state_changed(self, state):
        self.move_beam_mark_action.setChecked(False)
        self.move_beam_mark_action.setChecked(False)
        self.move_beam_mark_action.setChecked(state)

    def select_all_points_clicked(self):
        self.graphics_manager_hwobj.select_all_points()

    def deselect_all_items_clicked(self):
        self.graphics_manager_hwobj.de_select_all()

    def clear_all_items_clicked(self):
        self.graphics_manager_hwobj.clear_all()
