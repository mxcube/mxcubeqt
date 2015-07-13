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

"""
Qt4_GraphicsManager keeps track of the current shapes the user has created. The
shapes handled are any that inherits the Shape base class. There are currently
two shapes implemented Point and Line.

Point is the graphical representation of a centred position. A point can be
stored and managed by the ShapeHistory. the Line object represents a line
between two Point objects.

"""
import copy
import types
import logging
import traceback
from math import sqrt

from PyQt4 import QtGui
from PyQt4 import QtCore

import queue_model_objects_v1 as queue_model_objects

from HardwareRepository.BaseHardwareObjects import HardwareObject
from HardwareRepository.HardwareRepository import dispatcher

SELECTED_COLOR = QtCore.Qt.green
NORMAL_COLOR = QtCore.Qt.yellow


class Qt4_GraphicsManager(HardwareObject):
    """
    Keeps track of the current shapes the user has created. The
    shapes handled are any that inherits the Shape base class.
    """
    def __init__(self, name):
        HardwareObject.__init__(self, name)

        self.diffractometer_hwobj = None
     
        self.pixels_per_mm = [0, 0]
        self.beam_size = [0, 0]
        self.beam_position = [0, 0]
        self.beam_shape = None
        self.graphics_scene_size = [0, 0]
        self.mouse_position = [0, 0] 

        self.beam_info_dict = {}
        self.omega_axis_info_dict = {}
        #self.centring_points = []
        self.centring_state = False
        self.mesh_drawing_state = False
        self.measure_state = None
        self.point_count = 0
        self.mesh_count = 0
        self.selected_centring_points = []

        self.graphics_view = None
        self.graphics_camera_frame = None
        self.graphics_beam_item = None
        self.graphics_scale_item = None
        self.graphics_omega_reference_item = None
        self.graphics_centring_lines_item = None
        self.graphics_mesh_draw_item = None
 
    def init(self):
        self.graphics_view = GraphicsView()
         
        self.graphics_camera_frame = GraphicsCameraFrame()
        self.graphics_scale_item = GraphicsItemScale(self)
        self.graphics_omega_reference_item = GraphicsItemOmegaReference(self)
        self.graphics_beam_item = GraphicsItemBeam(self)
        self.graphics_centring_lines_item = GraphicsItemCentringLines(self)
        self.graphics_centring_lines_item.hide()
        self.graphics_measure_line_item = GraphicsItemMeasureLine(self)
        self.graphics_measure_line_item.hide()
         
        self.graphics_view.graphics_scene.addItem(self.graphics_camera_frame) 
        self.graphics_view.graphics_scene.addItem(self.graphics_omega_reference_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_beam_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_centring_lines_item) 
        self.graphics_view.graphics_scene.addItem(self.graphics_scale_item)
        self.graphics_view.graphics_scene.addItem(self.graphics_measure_line_item)

        self.graphics_view.scene().mouseClickedSignal.connect(\
             self.mouse_clicked)
        self.graphics_view.scene().mouseDoubleClickedSignal.connect(\
             self.mouse_double_clicked)
        self.graphics_view.scene().mouseReleasedSignal.connect(\
             self.mouse_released)
        self.graphics_view.scene().itemClickedSignal.connect(\
             self.item_clicked)
        self.graphics_view.scene().itemDoubleClickedSignal.connect(\
             self.item_double_clicked)
        self.graphics_view.mouseMovedSignal.connect(self.mouse_moved)
        self.graphics_view.keyPressedSignal.connect(self.key_pressed)

        self.diffractometer_hwobj = self.getObjectByRole("diffractometer")
        self.pixels_per_mm = self.diffractometer_hwobj.get_pixels_per_mm()
        self.set_pixels_per_mm(self.pixels_per_mm)
        
    def mouse_clicked(self, x, y):
        self.selected_centring_points = [] 
        if self.centring_state:
            self.graphics_centring_lines_item.set_coordinates(x, y)
        elif self.mesh_drawing_state:
            self.graphics_mesh_draw_item.show()
            self.graphics_mesh_draw_item.set_draw_mode(True)
            self.graphics_mesh_draw_item.set_draw_start_position(x, y)
        elif self.measure_state:
            QtGui.QApplication.restoreOverrideCursor()
            self.measure_state = None
        else:
            for graphics_item in self.graphics_view.scene().items():
                graphics_item.setSelected(False)
        self.diffractometer_hwobj.image_clicked(x, y)

    def mouse_double_clicked(self, x, y): 
        self.diffractometer_hwobj.move_to_coord(x, y)

    def mouse_released(self, x, y):
        if self.mesh_drawing_state:
           self.graphics_mesh_draw_item.set_draw_mode(False)
           self.emit("meshCreated", self.graphics_mesh_draw_item)
           self.mesh_drawing_state = False
           self.graphics_mesh_draw_item.set_draw_mode(False)

    def mouse_moved(self, x, y):
        self.emit("graphicsMouseMoved", x, y)
        self.mouse_position = [x, y]
        if self.centring_state:
            self.graphics_centring_lines_item.set_coordinates(x, y)
        elif self.mesh_drawing_state:
            if self.graphics_mesh_draw_item.is_draw_mode():
                self.graphics_mesh_draw_item.set_draw_end_position(x, y)
        elif self.measure_state:
            self.graphics_measure_line_item.set_end_coord(self.mouse_position)

    def key_pressed(self, key_event):
        if key_event == "Delete":
            for item in self.graphics_view.graphics_scene.items():
                if item.isSelected():
                    self.delete_shape(item)
 
    def item_clicked(self, item, state):
        # before changing state this signal is emited
        # so we hve to revert state
        # TODO fix this correct state
        if isinstance(item, GraphicsItemPoint):
            if not state:
                self.selected_centring_points.append(item)
            else:
                self.selected_centring_points.remove(item)

    def item_double_clicked(self, item):
        if isinstance(item, GraphicsItemPoint):
            self.diffractometer_hwobj.move_to_centred_position(item.centred_position)

    def get_graphics_view(self):
        return self.graphics_view

    def get_camera_frame(self):
        return self.graphics_camera_frame 

    def set_graphics_scene_size(self, size):
        self.graphics_scene_size = size
        self.graphics_scale_item.set_position(10, 
             self.graphics_scene_size[1] - 10)
        self.graphics_view.setFixedSize(size[0], size[1])

    def get_graphics_beam_item(self):
        return self.graphics_beam_item

    def get_scale_item(self):
        return self.graphics_scale_item

    def get_omega_reference_item(self):
        return self.graphics_omega_reference_item

    def set_centring_state(self, state):
        self.centring_state = state
        self.graphics_centring_lines_item.set_visible(state)

    def get_shapes(self):
        """
        :returns: All the shapes currently handled.
        """
        shapes_list = []
        for shape in self.graphics_view.graphics_scene.items():
            if type(shape) in (GraphicsItemPoint, GraphicsItemLine, GraphicsItemMesh):
                shapes_list.append(shape)                 
        return shapes_list

    def get_points(self):
        """
        :returns: All points currently handled
        """
        current_points = []

        for shape in self.get_shapes():
            if isinstance(shape, GraphicsItemPoint):
                current_points.append(shape)

        return current_points
        
    def add_shape(self, shape):
        """
        Adds the shape <shape> to the list of handled objects.

        :param shape: Shape to add.
        :type shape: Shape object.
        """
        self.de_select_all()

        if isinstance(shape, GraphicsItemPoint):
            self.point_count += 1
            shape.index = self.point_count
            self.selected_centring_points.append(shape)
        self.graphics_view.graphics_scene.addItem(shape)
        shape.setSelected(True)

    def delete_shape(self, shape):
        """
        Removes the shape <shape> from the list of handled shapes.

        :param shape: The shape to remove
        :type shape: Shape object.
        """
        if isinstance(shape, GraphicsItemPoint):
            for s in self.get_shapes():
                if isinstance(s, GraphicsItemLine):
                    if shape in (s.cp_start, s.cp_end):
                        self._delete_shape(s)
                        break
        self.emit("shapeDeleted", shape)
        self.graphics_view.graphics_scene.removeItem(shape)
        self.graphics_view.graphics_scene.update()

    def clear_all(self):
        """
        Clear the shape history, remove all contents.
        """
        self.point_count = 0
        self.mesh_count = 0

        for shape in self.get_shapes():
            self.delete_shape(shape)
        self.graphics_view.graphics_scene.update()

    def de_select_all(self):
        self.graphics_view.graphics_scene.clearSelection()

    def select_shape_with_cpos(self, cpos):
        self.de_select_all()
        for shape in self.get_shapes():
            if isinstance(shape, GraphicsItemPoint):
                if shape.get_centred_positions()[0] == cpos:
                    shape.setSelected(True)

    def get_grid(self):
        """
        Returns the current grid object.
        """
        grid_dict = dict()
        dispatcher.send("grid", self, grid_dict)
        return grid_dict

    def set_grid_data(self, key, result_data):
        dispatcher.send("set_grid_data", self, key, result_data)

    def get_selected_shapes(self):
        selected_shapes = []
        for item in self.graphics_view.graphics_scene.items():
            if (type(item) in [GraphicsItemPoint, GraphicsItemMesh, GraphicsItemLine] and
                item.isSelected()):
                selected_shapes.append(item) 
        return selected_shapes

    def get_selected_points(self):
        return self.selected_centring_points

    def update_beam_position(self, beam_position):
        if beam_position is not None:
            self.graphics_beam_item.set_position(beam_position[0],
                                                 beam_position[1])

    def set_pixels_per_mm(self, pixels_per_mm):
        if pixels_per_mm is not None:
            self.pixels_per_mm = pixels_per_mm

            for item in self.graphics_view.graphics_scene.items():
                if isinstance(item, GraphicsItem):
                    item.set_pixels_per_mm(self.pixels_per_mm)

            #self.graphics_beam_item.set_size(self.beam_size[0] * self.pixels_per_mm[0],
            #                                 self.beam_size[1] * self.pixels_per_mm[1])
            #self.graphics_measure_line_item.set_pixels_per_mm(self.pixels_per_mm)
            #self.graphics_scale_item.set_pixels_per_mm(self.pixels_per_mm)
            self.graphics_view.graphics_scene.update()

    def update_beam_info(self, beam_info):
        if beam_info is not None:
            self.graphics_beam_item.set_beam_info(beam_info)
            self.graphics_view.graphics_scene.update()

    def update_omega_reference(self, omega_reference):
        self.graphics_omega_reference_item.set_reference(omega_reference)  

    def add_new_centring_point(self, state, centring_status, beam_info):
        new_point = GraphicsItemPoint(self)
        self.centring_points.append(new_point)
        self.graphics_view.graphics_scene.addItem(new_point)        

    def get_snapshot(self, shape_list=None):
        if shape_list:
            self.de_select_all()
            for shape in shape_list:
                shape.setSelected(True)

        image = QtGui.QImage(self.graphics_view.graphics_scene.sceneRect().size().toSize(), 
                             QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        image_painter = QtGui.QPainter(image)
        self.graphics_view.render(image_painter)
        image_painter.end()
        return image

    def set_mesh_draw_state(self, state):
        self.mesh_drawing_state = state

    def start_mesh_draw(self, beam_size, spacing):
	self.graphics_mesh_draw_item = GraphicsItemMesh(self, beam_size, spacing, self.pixels_per_mm)
        self.mesh_count += 1
        self.graphics_mesh_draw_item.index = self.mesh_count 
        self.graphics_view.graphics_scene.addItem(self.graphics_mesh_draw_item)
        self.graphics_mesh_draw_item.show()
        self.mesh_drawing_state = True

    def stop_mesh_draw(self):
        return

    def start_measure(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
        self.measure_state = True
        self.graphics_measure_line_item.set_start_coord(self.mouse_position)
        self.graphics_measure_line_item.show()
        self.graphics_view.graphics_scene.update()

    def stop_measure(self):
        self.measure_state = False
        self.graphics_measure_line_item.hide()
        self.graphics_view.graphics_scene.update()
  
class GraphicsItem(QtGui.QGraphicsItem):
    """
    Descript. : Base class for shapes.
    """
    _index = None

    def __init__(self, parent=None, position_x = 0, position_y = 0):
        QtGui.QGraphicsItem.__init__(self)
        rect = QtCore.QRectF(0, 0, 0, 0)
        self.rect = rect
        self.style = QtCore.Qt.SolidLine
        self.setMatrix = QtGui.QMatrix()
        self.pixels_per_mm = [None, None]
        self.setPos(position_x, position_y)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def set_position(self, position_x, position_y):
        if (position_x is not None and
            position_y is not None):
            self.setPos(position_x, position_y)

    def set_visible(self, is_visible):
        if is_visible: 
            self.show()
        else:
            self.hide()

    def set_pixels_per_mm(self, pixels_per_mm):
        self.pixels_per_mm = pixels_per_mm

class GraphicsItemBeam(GraphicsItem):
    """
    Descrip. : 
    """
    def __init__(self, parent, position_x = 0, position_y= 0):
        GraphicsItem.__init__(self, parent, position_x = 0, position_y= 0)
        self.shape_is_rectangle = True
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | \
                      QtGui.QGraphicsItem.ItemIsSelectable)
        self.__size_pix = [0, 0]
        self.__position_x = position_x
        self.__position_y = position_y
        
    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)
        if option.state & QtGui.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.red)
        else:
            pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        if self.shape_is_rectangle:
            painter.drawRect(self.__position_x - self.__size_pix[0] / 2,
                             self.__position_y - self.__size_pix[1] / 2,
                             self.__size_pix[0], self.__size_pix[1])
        else:
            painter.drawEllipse(self.__position_x - self.__size_pix[0] / 2,
                                self.__position_y - self.__size_pix[1] / 2,
                                self.__size_pix[0], self.__size_pix[1])
        pen.setColor(QtCore.Qt.red) 
        painter.setPen(pen)
        painter.drawLine(self.__position_x - 15, self.__position_y,
                         self.__position_x + 15, self.__position_y)
        painter.drawLine(self.__position_x, self.__position_y - 15, 
                         self.__position_x, self.__position_y + 15)  

    def set_position(self, position_x, position_y):
        self.__position_x = position_x
        self.__position_y = position_y
 
    def set_beam_info(self, beam_info_dict):
        self.shape_is_rectangle = beam_info_dict.get("shape") == "rectangular"
        self.__size_pix = [beam_info_dict.get("size_x") * self.pixels_per_mm[0],
                           beam_info_dict.get("size_y") * self.pixels_per_mm[1]]

class GraphicsItemMesh(GraphicsItem):
    """
    Descrip. : 
    """
    def __init__(self, parent, beam_info, spacing, pixels_per_mm):
        GraphicsItem.__init__(self, parent)

        self.pixels_per_mm = pixels_per_mm
        self.__beam_size_microns = [beam_info.get("size_x"), 
                                    beam_info.get("size_y")]
        self.__beam_size_pix = [0, 0] 
        self.__beam_is_rectangle = beam_info.get("shape") == "rectangle"
        self.__spacing_microns = spacing
        self.__spacing_pix = [0, 0]
        self.__cell_size_microns = [0, 0]
        self.__cell_size_pix = [0, 0]
        self.__corner_points = []
        self.__corner_coord = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.__num_colls = 0      
        self.__num_rows = 0
        self.__num_lines = 0
        self.__num_images_per_line = 0
        self.__first_image_num = 1
        self.__centred_point = None
        self.__draw_mode = False
        self.__draw_projection = False

        self.__motor_pos_corner = None
        self.__motor_pos_center = None
        #By default md3 case
        self.__grid_range = {}
        self.__grid_direction = {"fast": (0,1), "slow": (1,0)}
         
        self.update_grid()

    def set_pixels_per_mm(self, pixels_per_mm):
        self.pixels_per_mm = pixels_per_mm
        self.update_grid()

    def update_grid(self):
        self.__cell_size_microns = [self.__beam_size_microns[0] + self.__spacing_microns[0] * 2,
                                    self.__beam_size_microns[1] + self.__spacing_microns[1] * 2]
        self.__spacing_pix = [self.pixels_per_mm[0] * self.__spacing_microns[0],
                              self.pixels_per_mm[1] * self.__spacing_microns[1]]
        self.__beam_size_pix = [self.pixels_per_mm[0] * self.__beam_size_microns[0],
                                self.pixels_per_mm[1] * self.__beam_size_microns[1]]
        self.__cell_size_pix = [self.pixels_per_mm[0] * self.__cell_size_microns[0],
                                self.pixels_per_mm[1] * self.__cell_size_microns[1]]

    def set_draw_start_position(self, pos_x, pos_y):
        self.__corner_coord[0][0] = pos_x
        self.__corner_coord[0][1] = pos_y
        self.__corner_coord[1][1] = pos_y
        self.__corner_coord[2][0] = pos_x
        self.scene().update()

    def set_draw_end_position(self, pos_x, pos_y):
        self.__corner_coord[1][0] = pos_x
        self.__corner_coord[2][1] = pos_y
        self.__corner_coord[3][0] = pos_x
        self.__corner_coord[3][1] = pos_y
        self.scene().update()

    def set_draw_mode(self, draw_mode):
        self.__draw_mode = draw_mode 

    def is_draw_mode(self):
        return self.__draw_mode

    def get_properties(self):
        return {"name": "Grid %d" % self._index,
                "beam_hor" : self.__beam_size_microns[0],
                "beam_ver" : self.__beam_size_microns[1],
                "spacing_hor": self.__spacing_microns[0],
                "spacing_ver": self.__spacing_microns[1],  
                "corner_points" : self.__corner_points,
                "corner_coord" : self.__corner_coord,
                "num_col" : self.__num_colls,
                "num_row" : self.__num_rows,
                "num_lines": self.__num_lines,
                "num_images_per_line": self.__num_images_per_line,
                "first_image_num": self.__first_image_num}

    def set_centred_point(self, centred_point):
        self.__centred_point = centred_point

    def set_properties(self, properties_dict):
        self.__beam_size_hor = properties_dict.get("beam_hor")
        self.__beam_size_ver = properties_dict.get("beam_ver")
        self.__cell_width = properties_dict.get("cell_width")
        self.__cell_height = properties_dict.get("cell_height")
        self.__corner_points = properties_dict.get("corner_pos") 
        self.__corner_coord = properties_dict.get("corner_coord")
        self.__num_col = properties_dict.get("num_col")
        self.__num_row = properties_dict.get("num_row")

    def get_corner_coord(self):
        return self.__corner_coord

    def set_motor_pos_corner(self, motor_pos_corner):
        self.__motor_pos_corner = motor_pos_corner

    def get_motor_pos_corner(self):
        return self.__motor_pos_corner

    def set_motor_pos_center(self, motor_pos_center):
        self.__motor_pos_center = motor_pos_center

    def get_motor_pos_center(self):
        return self.__motor_pos_center

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)
        brush = QtGui.QBrush(self.style)
        brush.setColor(QtGui.QColor(70,70,165))
        brush.setStyle(QtCore.Qt.Dense4Pattern)

        if self.__draw_mode or self.isSelected():
            pen.setColor(QtCore.Qt.green)
        else:
            pen.setColor(QtCore.Qt.darkGray)

        painter.setPen(pen)
        painter.setBrush(brush)
       
        self.__num_cells = 0
        self.__num_rows = 0
        self.__num_colls = 0

        #During the drawing estimates number of colls and rows
        if self.__cell_size_pix[0] <> 0:
            self.__num_colls = int((abs(self.__corner_coord[1][0] - \
                 self.__corner_coord[0][0]) / self.__cell_size_pix[0]))
        if self.__cell_size_pix[1] <> 0:
            self.__num_rows = int(abs((self.__corner_coord[3][1] - \
                 self.__corner_coord[1][1]) / self.__cell_size_pix[1]))

        if not self.__draw_projection:
            if self.__num_rows * self.__num_colls > pow(2, 16):
                msg_text = "Unable to draw grid containing more than %d cells!" % pow(2, 16)
                logging.getLogger("user_level_log").info(msg_text)
                return

            grid_size_pix = [self.__num_colls * self.__cell_size_pix[0],
                             self.__num_rows * self.__cell_size_pix[1]]

            self.__num_cells = self.__num_rows * self.__num_colls
            #Based on the grid directions estimates number of lines and 
            #number of images per line
            self.__num_lines =  abs(self.__grid_direction['fast'][1] * \
                 self.__num_colls) + abs(self.__grid_direction['slow'][1] * \
                 self.__num_rows)
            self.__num_images_per_line = abs(self.__grid_direction['fast'][0] * \
                self.__num_colls) + abs(self.__grid_direction['slow'][0] * \
                self.__num_rows)

            #Also grid range is estimated 
            self.__grid_range["fast"] = abs(self.__grid_direction['fast'][0] * \
                 (grid_size_pix[0] - self.__cell_size_pix[0])) + \
                 abs(self.__grid_direction['fast'][1] * \
                 (grid_size_pix[1] - self.__cell_size_pix[1]))
            self.__grid_range["slow"] = abs(self.__grid_direction['slow'][0] * \
                 (grid_size_pix[0] - self.__cell_size_pix[0])) + \
                 abs(self.__grid_direction['slow'][1] * \
                 (grid_size_pix[1] - self.__cell_size_pix[1]))

            #cell width and height for drawing are estimated
            self.__x_mid = self.__corner_coord[0][0] + grid_size_pix[0]  / 2
            self.__y_mid = self.__corner_coord[0][1] + grid_size_pix[1] / 2

            pen.setStyle(QtCore.Qt.SolidLine)
            painter.setPen(pen)
            for i in range(0, self.__num_colls + 1):
                offset = i * self.__cell_size_pix[0]
                painter.drawLine(self.__corner_coord[0][0] + offset,
                                 self.__corner_coord[0][1],
                                 self.__corner_coord[0][0] + offset,
                                 self.__corner_coord[0][1] + self.__num_rows * self.__cell_size_pix[1])
            for i in range(0, self.__num_rows + 1):
                offset = i * self.__cell_size_pix[1]
                painter.drawLine(self.__corner_coord[0][0],
                                 self.__corner_coord[0][1] + offset,
                                 self.__corner_coord[0][0] + self.__num_colls * self.__cell_size_pix[0],
                                 self.__corner_coord[0][1] + offset)    

            #Draws beam shape and displays number of image if 
            #less than 1000 cells and size is greater than 20px
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            cell_index = 0
            if self.__num_cells < 1000 and self.__cell_size_pix[1] > 20:
                for col in range(self.__num_colls):
                    coll_offset = col * self.__cell_size_pix[0]
                    for row in range(self.__num_rows):
                        row_offset = row * self.__cell_size_pix[1]
                        if self.__beam_is_rectangle:
                            painter.drawRect(self.__corner_coord[0][0] + coll_offset + self.__spacing_pix[0],
                                             self.__corner_coord[0][1] + row_offset + self.__spacing_pix[1],
                                             self.__beam_size_pix[0], self.__beam_size_pix[1])
                        else:
                            painter.drawEllipse(self.__corner_coord[0][0] + coll_offset + self.__spacing_pix[0],
                                                self.__corner_coord[0][1] + row_offset + self.__spacing_pix[1],
                                                self.__beam_size_pix[0], self.__beam_size_pix[1])
                        """line, image = self.get_line_image_num(cell_index + self.__first_image_number)
                        x, y = self.get_coord_from_line_image(line, image)
                        tr = QtGui.QRect(x - self.__ / 2, y - self.__cell_height / 2,
                                         self.__cell_width, self.__cell_height)
                        if self.__display_score:
                            painter.drawText(tr, qt.Qt.AlignCenter, "%0.3f" %self.__score[cell_index - 1])
                        else:
                            painter.drawText(tr, qt.Qt.AlignCenter, str(cell_index + self.__first_image_number))"""
                        cell_index += 1
            painter.drawText(self.__corner_coord[0][0] + grid_size_pix[0] + 3,
                             self.__corner_coord[1][1] - 3,
                             "Grid %d" %self.index) 
 
        else:
            print "draw projection"
 
class GraphicsItemScale(GraphicsItem):
    """
    Descrip. : Displays vertical and horizontal scale on the bottom, left 
               corner. Horizontal scale is scaled to 50 or 100 microns and
               vertical scale is two times shorter.
    """
    HOR_LINE_LEN = [500, 200, 100, 50]

    def __init__(self, parent, position_x = 0, position_y= 0):
        GraphicsItem.__init__(self, parent, position_x = 0, position_y= 0)
        self.scale_len = 0

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(3)
        pen.setColor(QtCore.Qt.green)
        painter.setPen(pen)
       
        hor_scale_len_pix = self.pixels_per_mm[0] * self.scale_len / 1000 
        ver_scale_len_pix = self.pixels_per_mm[1] * self.scale_len / 1000 / 2

        painter.drawLine(0, 0, hor_scale_len_pix, 0)
        painter.drawText(hor_scale_len_pix + 3, - 5, "%d" %self.scale_len)
        painter.drawLine(0, 0, 0, - ver_scale_len_pix)
        painter.drawText(3, - ver_scale_len_pix, "%d" %(self.scale_len / 2))

    def set_pixels_per_mm(self, pixels_per_mm):
        self.pixels_per_mm = pixels_per_mm
        
        for line_len in GraphicsItemScale.HOR_LINE_LEN:
            if self.pixels_per_mm[0] * line_len / 1000 <= 250:
               self.scale_len = line_len
               break

class GraphicsItemOmegaReference(GraphicsItem):
    """
    Descrip. : 
    """
    def __init__(self, parent, position_x = 0, position_y= 0):
        GraphicsItem.__init__(self, parent, position_x = 0, position_y= 0)
        self.parent = parent
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)
        pen.setColor(QtCore.Qt.white)
        painter.setPen(pen)
        painter.drawLine(self.start_x, self.start_y, self.end_x, self.end_y)

    def set_reference(self, omega_reference):
        line_length = self.parent.graphics_scene_size
        if omega_reference[0] > 0:
            #Omega reference is a vertical axis
            self.start_x = omega_reference[0]
            self.end_x = omega_reference[0]
            self.start_y = 0
            self.end_y = line_length[1]
        else:
            self.start_x = 0
            self.end_x = line_length[0]
            self.start_y = omega_reference[1]
            self.end_y = omega_reference[1]

class GraphicsItemCentringLines(GraphicsItem):
    """
    Descrip. : 
    """
    def __init__(self, parent, position_x = 0, position_y= 0):
        GraphicsItem.__init__(self, parent, position_x = 0, position_y= 0)
        self.parent = parent

        self.coord_x = 200
        self.coord_y = 100

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)
        pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        painter.drawLine(self.coord_x, 0, self.coord_x, self.scene().height())
        painter.drawLine(0, self.coord_y, self.scene().width(), self.coord_y)

    def set_coordinates(self, x, y):
        self.coord_x = x
        self.coord_y = y 
        self.scene().update()        

class GraphicsItemMeasureLine(GraphicsItem):
    """
    Descrip. : 
    """
    def __init__(self, parent):
        GraphicsItem.__init__(self, parent)
        self.start_x = 0 
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.dist_microns = 0

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)
        if option.state & QtGui.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.green)
        else:
            pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        painter.drawLine(self.start_x, self.start_y,
                         self.end_x, self.end_y)
        self.dist_microns = sqrt(pow((self.start_x - self.end_x) / self.pixels_per_mm[0], 2) + \
                                 pow((self.start_y - self.end_y) / self.pixels_per_mm[1], 2)) * 1000
        painter.drawText(self.end_x + 10, self.end_y + 10, "%.2f microns" % self.dist_microns)
 
    def set_start_coord(self, coord):
        self.start_x = coord[0]
        self.start_y = coord[1]

    def set_end_coord(self, coord):
        self.end_x = coord[0]
        self.end_y = coord[1]
        self.scene().update()

class GraphicsItemPoint(GraphicsItem):
    """
    Descrip. : Centred point class.
    Args.    : parent, centred position (motors position dict, 
               full_centring (True if 3click centring), initial position)
    """
    def __init__(self, centred_position = None, full_centring = True,
                 position_x = 0, position_y = 0):
        GraphicsItem.__init__(self, position_x, position_y)

        self.full_centring = full_centring
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable) 

        if centred_position is None:
            self.centred_position = queue_model_objects.CentredPosition()
            self.centred_position.centring_method = False
        else:
            self.centred_position = centred_position
        self.set_size(20, 20)
        self.set_position(position_x, position_y)

    def get_centred_positions(self):
        return [self.centred_position]

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(1)

        if option.state & QtGui.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.green)
        else:
            pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        painter.drawEllipse(self.rect.left(), self.rect.top(),
                            20, 20)
        painter.drawLine(self.rect.left(), self.rect.top(),
                         self.rect.right(), self.rect.bottom())
        painter.drawLine(self.rect.right(), self.rect.top(),
                         self.rect.left(), self.rect.bottom())
        if self._index:
            display_str = str(self._index)
        else:
            display_str = "#"
        if self.isSelected():
            display_str += " selected" 

        painter.drawText(self.rect.right() + 2, self.rect.top(), display_str)

    def get_position(self):
        return self.__position_x, self.__position_y

    def set_position(self, position_x, position_y):
        self.__position_x = position_x
        self.__position_y = position_y
        self.setPos(self.__position_x - 10, self.__position_y - 10)

    def mouseDoubleClickEvent(self, event):
        position = QtCore.QPointF(event.pos())
        self.scene().itemDoubleClickedSignal.emit(self)
        self.update()

    def mousePressEvent(self, event):
        self.update()
        self.scene().itemClickedSignal.emit(self, self.isSelected())

class GraphicsItemLine(GraphicsItem):
    """
    Descrip. : Line class.
    """
    def __init__(self, cp_start, cp_end):
        GraphicsItem.__init__(self)

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.cp_start = cp_start
        self.cp_end = cp_end
        self.setPos(0, 0)

    def get_graphics_points(self):
        return [self.cp_start, self.cp_end]

    def get_centred_positions(self):
        return [self.cp_start.centred_position, self.cp_end.centred_position]

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.style)
        pen.setWidth(2)

        if option.state & QtGui.QStyle.State_Selected:
            pen.setColor(QtCore.Qt.green)
        else:
            pen.setColor(QtCore.Qt.yellow)
        painter.setPen(pen)
        (start_cp_x, start_cp_y) = self.cp_start.get_position()
        (end_cp_x, end_cp_y) = self.cp_end.get_position()

        painter.drawLine(start_cp_x, start_cp_y,
                         end_cp_x, end_cp_y)
        if self._index:
            painter.drawText(self.rect.right() + 2, self.rect.top(), str(self.index))
        else:
            painter.drawText(self.rect.right() + 2, self.rect.top(), "#")

    def setSelected(self, state):
        GraphicsItem.setSelected(self, state)
        self.cp_start.setSelected(state)
        self.cp_end.setSelected(state)

    def get_points_index(self):
        return (self.cp_start.index, self.cp_end.index)

    def set_position(self, position_x, position_y):
        return

class GraphicsView(QtGui.QGraphicsView):
    mouseMovedSignal = QtCore.pyqtSignal(int, int)
    keyPressedSignal = QtCore.pyqtSignal(str)

    def __init__ (self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.graphics_scene = GraphicsScene(self)
        self.setScene(self.graphics_scene)  
        self.graphics_scene.clearSelection()
        self.setMouseTracking(True)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def mouseMoveEvent(self, event):
        position = QtCore.QPointF(event.pos())
        self.mouseMovedSignal.emit(position.x(), position.y())
        self.update()
 
    def keyPressEvent(self, event):
        key_type = None
        if event.key() in(QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):  
            key_type = "Delete"
        if key_type:
            self.keyPressedSignal.emit(key_type)


class GraphicsScene(QtGui.QGraphicsScene):
    mouseClickedSignal = QtCore.pyqtSignal(int, int)
    mouseDoubleClickedSignal = QtCore.pyqtSignal(int, int)  
    mouseReleasedSignal = QtCore.pyqtSignal(int, int)
    itemDoubleClickedSignal = QtCore.pyqtSignal(GraphicsItem)
    itemClickedSignal = QtCore.pyqtSignal(GraphicsItem, bool) 

    def __init__ (self, parent=None):
        super(GraphicsScene, self).__init__ (parent)


class GraphicsCameraFrame(QtGui.QGraphicsPixmapItem):
    def __init__ (self, parent=None):
        super(GraphicsCameraFrame, self).__init__(parent)

    def mousePressEvent(self, event):
        position = QtCore.QPointF(event.pos())
        self.scene().mouseClickedSignal.emit(position.x(), position.y())
        self.update()  

    def mouseDoubleClickEvent(self, event):
        position = QtCore.QPointF(event.pos())
        self.scene().mouseDoubleClickedSignal.emit(position.x(), position.y())
        self.update()

    def mouseReleaseEvent(self, event):
        position = QtCore.QPointF(event.pos())
        self.scene().mouseReleasedSignal.emit(position.x(), position.y())
        self.update()
        self.setSelected(True)
