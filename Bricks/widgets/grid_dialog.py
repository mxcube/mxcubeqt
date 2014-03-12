import os
import qt
import qtui
import random

from ShapeHistory import CanvasGrid
from Qub.Objects.QubDrawingManager import Qub2PointSurfaceDrawingMgr
from HardwareRepository.HardwareRepository import dispatcher

class GridDialog(qt.QDialog):
    def __init__(self, parent = None, name = "Grid Dialog", canvas = None,
                 matrix = None, event_mgr = None, drawing_object_layer = None):
        super(GridDialog, self).__init__(parent, name)
        self.__cell_width = 0
        self.__cell_height = 0
        self.__list_items = {}
        self.__item_counter = 0
        self.__grid_list = []
        self.__main_layout = qt.QVBoxLayout(self, 10, 11, 'main_layout')

        self.__canvas = canvas
        self.__matrix = matrix
        self.__event_mgr = event_mgr
        self.__drawing_object_layer = drawing_object_layer
        self.__drawing_mgr = None
        self.__x_pixel_size = 1
        self.__y_pixel_size = 1
        self.__beam_pos = (0, 0, 0, 0)

        ui_file = 'ui_files/grid_row_widget.ui'
        current_dir = os.path.dirname(__file__)
        widget = qtui.QWidgetFactory.create(os.path.join(current_dir, ui_file))
        widget.reparent(self, qt.QPoint(0,0))
        self.__main_layout.add(widget)
        self.__list_view = widget.child("list_view")

        qt.QObject.connect(widget.child("add_button"), qt.SIGNAL("clicked()"),
                           self.__add_drawing)

        qt.QObject.connect(widget.child("remove_button"), qt.SIGNAL("clicked()"),
                           self.__delete_drawing)

        dispatcher.connect(self._get_grid_info, "grid")

        qt.QObject.connect(widget.child("list_view"),
                           qt.SIGNAL("selectionChanged(QListViewItem * )"),
                           self.__selection_changed)
        
    def set_qub_event_mgr(self, a_qub_image):
        self.__canvas = a_qub_image.canvas()
        self.__matrix = a_qub_image.matrix()
        self.__event_mgr = a_qub_image

    def showEvent(self, show_event):
        super(GridDialog, self).showEvent(show_event)
        self.__drawing_mgr = Qub2PointSurfaceDrawingMgr(self.__canvas, self.__matrix)
        self.__start_surface_drawing()

    def closeEvent(self, close_event):
        super(GridDialog, self).closeEvent(close_event)
        self.__stop_surface_drawing()

    def __end_surface_drawing(self, drawing_mgr = None):
        drawing_mgr.reshape()

    def __start_surface_drawing(self):
        self.__drawing_mgr.setAutoDisconnectEvent(False)
        drawing_object = CanvasGrid(self.__canvas)
        self.__drawing_mgr.addDrawingObject(drawing_object)
        self.__event_mgr.addDrawingMgr(self.__drawing_mgr)
        self.__drawing_mgr.set_x_pixel_size(self.__x_pixel_size)
        self.__drawing_mgr.set_y_pixel_size(self.__y_pixel_size)
        self.__drawing_mgr.set_beam_position(*self.__beam_pos)
        self.__drawing_mgr.startDrawing()
        self.__drawing_mgr.setEndDrawCallBack(self.__end_surface_drawing)
        self.__drawing_mgr.setColor(qt.Qt.green)

    def __stop_surface_drawing(self):
        self.__drawing_mgr.stopDrawing()
        self.__drawing_mgr = None

    def __add_drawing(self):
        if self.__drawing_mgr.isVisible()[0]:
            self.__item_counter += 1
            name = ("Grid - %i" % self.__item_counter)
            width = str(self.__beam_pos[2]*1000)
            height = str(self.__beam_pos[3]*1000)
            list_view_item = qt.QListViewItem(self.__list_view, name, width, height)
            self.__list_items[list_view_item] = self.__drawing_mgr
            self.__drawing_mgr.stopDrawing()
            self.__drawing_mgr.set_label(name)

            num_cells = self.__drawing_mgr.get_nummer_of_cells()[0]
            data = {}

            for cell in range(1, num_cells + 1):
                random.seed()
                data[cell] = (cell, (255, random.randint(0, 255), 0))

            self.__drawing_mgr.set_data(data)
            grid_info = self.__drawing_mgr._get_grid()[0]
            print grid_info
            self.__list_view.setSelected(list_view_item, True)

            self.__drawing_mgr = Qub2PointSurfaceDrawingMgr(self.__canvas, self.__matrix)
            self.__start_surface_drawing()

    def __delete_drawing(self):
        if len(self.__list_items):
            list_view_item = self.__list_view.selectedItem()
            del self.__list_items[list_view_item]
            self.__list_view.takeItem(list_view_item)

            list_view_item = self.__list_view.lastItem()
            self.__list_view.setSelected(list_view_item, True)

    def set_x_pixel_size(self, x_size):
        x_size = 1e-3/x_size

        if self.__x_pixel_size != x_size:
            zoom_factor = x_size / self.__x_pixel_size
            beam_width_mm =  self.__beam_pos[2]
            self.__x_pixel_size = x_size
            self.__cell_width = int(beam_width_mm * self.__x_pixel_size)

            try:
                if self.__drawing_mgr:
                    self.__drawing_mgr.set_x_pixel_size(x_size)
                for drawing_mgr in self.__list_items.values():
                    drawing_mgr.set_x_pixel_size(x_size)
                    drawing_mgr.reposition(scale_factor_x = zoom_factor)
            except AttributeError:
                # Drawing manager not set when called
                pass

    def set_y_pixel_size(self, y_size):
        y_size = 1e-3/y_size

        if self.__y_pixel_size != y_size:
            zoom_factor = y_size / self.__y_pixel_size
            beam_height_mm =  self.__beam_pos[3]
            self.__y_pixel_size = y_size
            self.__cell_height = int(beam_height_mm * self.__y_pixel_size)

            try:
                if self.__drawing_mgr:
                    self.__drawing_mgr.set_y_pixel_size(y_size)
                    self.__drawing_mgr.reshape()

                for drawing_mgr in self.__list_items.values():
                    drawing_mgr.set_y_pixel_size(y_size)
                    drawing_mgr.reshape()
                    drawing_mgr.reposition(scale_factor_y = zoom_factor)
            except:
                # Drawing manager not set when called
                pass

    def set_beam_position(self, beam_c_x, beam_c_y, beam_width_mm,
                          beam_height_mm):
        self.__beam_pos = (beam_c_x, beam_c_y, beam_width_mm, beam_height_mm)
        
        self.__cell_height = int(beam_height_mm * self.__y_pixel_size)
        self.__cell_width = int(beam_width_mm * self.__x_pixel_size)
        try:
            self.__drawing_mgr.set_beam_position(beam_c_x, beam_c_y,
                                                 beam_width_mm, beam_height_mm)
            for drawing_mgr in self.__list_items.itervalues():
                drawing_mgr.set_beam_position(beam_c_x, beam_c_y)
        except:
            # Drawing manager not set when called
            pass

    def _get_grid_info(self, grid_dict):
        list_view_item = self.__list_view.selectedItem()
        drawing_mgr = self.__list_items[list_view_item]
        grid_dict.update(drawing_mgr._get_grid()[0])

    def __selection_changed(self, item):
        for current_item in self.__list_items.iterkeys():
            drawing_mgr = self.__list_items[current_item]
            if current_item == item:
                drawing_mgr.highlight(True)
            else:
                drawing_mgr.highlight(False)

    def move_grid_hor(self, displacement_mm):
        displacement_px = displacement_mm * self.__x_pixel_size
        #print "hor: %f" % displacement_px
        beam_pos_x = self.__beam_pos[0]
        try:
            for drawing_mgr in self.__list_items.itervalues():
                drawing_mgr.moveBy(displacement_px, 0)
        except:
            # Drawing manager not set when called
            pass
        
    def move_grid_ver(self, displacement_mm):
        displacement_px = displacement_mm * self.__x_pixel_size
        #print "ver: %f" % displacement_px
        beam_pos_y = self.__beam_pos[1]
        try:
            for drawing_mgr in self.__list_items.itervalues():
                drawing_mgr.moveBy(0, displacement_px)
        except:
            # Drawing manager not set when called
            pass
        
