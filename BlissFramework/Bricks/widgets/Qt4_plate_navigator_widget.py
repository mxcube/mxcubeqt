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

from QtImport import *

from BlissFramework import Qt4_Icons
from Qt4_sample_changer_helper import SampleChanger


class PlateNavigatorWidget(QWidget):
    """
    """

    def __init__(self, parent, realtime_plot = False):
        """
        """
        QWidget.__init__(self, parent)
      
        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.__current_location = None
 
        # Graphic elements ----------------------------------------------------
        self.plate_navigator_table = QTableWidget(self)
        self.plate_navigator_cell = QGraphicsView(self)

        # Layout --------------------------------------------------------------
        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(self.plate_navigator_table)
        _main_hlayout.addWidget(self.plate_navigator_cell)
        _main_hlayout.addStretch()
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        #self.plate_navigator_cell.setSizePolicy

        # Qt signal/slot connections ------------------------------------------
        self.plate_navigator_table.itemDoubleClicked.\
             connect(self.navigation_table_double_clicked)

        # Other ---------------------------------------------------------------
        self.navigation_graphicsscene = QGraphicsScene(self)
        self.plate_navigator_cell.setScene(self.navigation_graphicsscene)
        self.navigation_item = NavigationItem(self)
        #self.navigation_item.mouseDoubleClickedSignal.connect(\
        #     self.navigation_item_double_clicked)
        self.navigation_graphicsscene.addItem(self.navigation_item)
        self.navigation_graphicsscene.update()
        self.plate_navigator_cell.setEnabled(False)
        font = self.plate_navigator_table.font()
        font.setPointSize(8)
        self.plate_navigator_table.setFont(font)
        self.plate_navigator_table.setEditTriggers(\
             QAbstractItemView.NoEditTriggers)

        self.plate_navigator_table.setHorizontalScrollBarPolicy(\
                 Qt.ScrollBarAlwaysOff)
        self.plate_navigator_table.setVerticalScrollBarPolicy(\
                 Qt.ScrollBarAlwaysOff)
        self.plate_navigator_cell.setHorizontalScrollBarPolicy(\
                 Qt.ScrollBarAlwaysOff)
        self.plate_navigator_cell.setVerticalScrollBarPolicy(\
                 Qt.ScrollBarAlwaysOff)

    def sample_table_double_clicked(self, table_item):
        """
        Descript. : when user double clicks on plate table then sample in
                    corresponding cell is loaded
        """
        self.plate_manipulator_hwobj.load_sample(\
            (table_item.row() + 1, table_item.column() * self.num_drops + 1))

    def refresh_plate_location(self):
        """
        Descript. :
        """
        loaded_sample = self.plate_manipulator_hwobj.getLoadedSample()
        new_location = self.plate_manipulator_hwobj.get_plate_location()
        self.plate_navigator_cell.setEnabled(True)

        if new_location and self.__current_location != new_location:
            row = new_location[0]
            col = new_location[1]
            pos_x = new_location[2]
            pos_y = new_location[3]
            #pos_x *= self.plate_navigator_cell.width()
            #pos_y *= self.plate_navigator_cell.height()
            self.navigation_item.set_navigation_pos(pos_x, pos_y)
            self.plate_navigator_cell.update()
            if self.__current_location:
                empty_item = QTableWidgetItem(QIcon(), "")
                self.plate_navigator_table.setItem(self.__current_location[0],
                                                   self.__current_location[1],
                                                   empty_item)
            new_item = QTableWidgetItem(Qt4_Icons.load_icon("sample_axis"), "")
            self.plate_navigator_table.setItem(row, col, new_item)
            self.__current_location = new_location

    def init_plate_view(self, plate_manipulator_hwobj):
        """Initalizes plate info
        """
        self.plate_manipulator_hwobj = plate_manipulator_hwobj
        plate_info = self.plate_manipulator_hwobj.get_plate_info()

        self.num_cols = plate_info.get("num_cols", 12)
        self.num_rows = plate_info.get("num_rows", 8)
        self.num_drops = plate_info.get("num_drops", 3)

        self.plate_navigator_table.setColumnCount(self.num_cols)
        self.plate_navigator_table.setRowCount(self.num_rows)

        for col in range(self.num_cols):
            temp_header_item = QTableWidgetItem("%d" % (col + 1))
            self.plate_navigator_table.setHorizontalHeaderItem(\
                 col, temp_header_item)
            self.plate_navigator_table.setColumnWidth(col, 20)

        for row in range(self.num_rows):
            temp_header_item = QTableWidgetItem(chr(65 + row))
            self.plate_navigator_table.setVerticalHeaderItem(\
                 row, temp_header_item)
            self.plate_navigator_table.setRowHeight(row, 20)

        for col in range(self.num_cols):
            for row in range(self.num_rows):
                temp_item = QTableWidgetItem()
                self.plate_navigator_table.setItem(row, col, temp_item)

        table_height = 20 * (self.num_rows + 1)
        table_width = 20 * (self.num_cols + 1)
        self.plate_navigator_table.setFixedWidth(table_width)
        self.plate_navigator_table.setFixedHeight(table_height)
        #self.plate_navigator_cell.setFixedHeight(table_height)
        #self.plate_navigator_cell.setFixedWidth(55)
        self.setFixedHeight(table_height + 2)

        # TODO replace 150 with actual size
        self.navigation_item.set_size(20, table_height)
        self.navigation_item.set_num_drops_per_cell(plate_info['num_drops'])
        self.refresh_plate_location()

    def navigation_item_double_clicked(self, pos_x, pos_y):
        """
        Descript. :
        """
        #TODO replace this with pos_x, pos_y
        drop = int(pos_y * self.num_drops) + 1
        self.plate_manipulator_hwobj.load_sample(\
             (int(self.__current_location[0] + 1),
              int((self.__current_location[1]) * self.num_drops + drop)))

    def navigation_table_double_clicked(self, table_item):
        """Moves to the col/row double clicked by user
        """
        self.plate_manipulator_hwobj.load_sample(\
            (table_item.row() + 1, table_item.column() * self.num_drops + 1))

    #def set_navigation_cell_width(self, width):
    #    self.plate_navigator_cell.setFixedWidth(width)
    #    self.navigation_item.rect.setWidth(width)

class NavigationItem(QGraphicsItem):

    def __init__(self, parent=None):
        """
        Descript. :
        """

        QGraphicsItem.__init__(self)

        self.parent = parent
        self.rect = QRectF(0, 0, 0, 0)
        self.setPos(0, 0)
        #self.setMatrix = QtGui.QMatrix()

        self.__num_drops = None
        self.__navigation_posx = None
        self.__navigation_posy = None

    def boundingRect(self):
        """
        Descript. :
        """
        return self.rect.adjusted(0, 0, 0, 0)

    def set_size(self, width, height):
        """
        Descript. :
        """
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def paint(self, painter, option, widget):
        """
        Descript. :
        """
        pen = QPen(Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)

        if self.__num_drops:
            for drop_index in range(self.__num_drops):
                pos_x = self.scene().width() / 2
                pos_y = float(drop_index + 1) / (self.__num_drops + 1) * \
                     self.scene().height()
                painter.drawLine(58, pos_y - 2, 62, pos_y + 2)
                painter.drawLine(62, pos_y - 2, 58, pos_y + 2)
        pen.setColor(Qt.blue)
        #        painter.drawLine(pos_x - 2, pos_y - 2,
        #                         pos_x + 2, pos_y + 2)
        #        painter.drawLine(pos_x - 2, pos_y + 2,
        #                         pos_x + 2, pos_y - 2)
        #pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        if self.__navigation_posx and self.__navigation_posy:
            painter.drawLine(self.__navigation_posx - 5, self.__navigation_posy,
                             self.__navigation_posx + 5, self.__navigation_posy)
            painter.drawLine(self.__navigation_posx, self.__navigation_posy - 5,
                             self.__navigation_posx, self.__navigation_posy + 5)

    def set_navigation_pos(self, pos_x, pos_y):
        """
        Descript. :
        """
        self.__navigation_posx = pos_x * self.scene().width()
        self.__navigation_posy = pos_y * self.scene().height()
        self.scene().update()

    def set_num_drops_per_cell(self, num_drops):
        """
        Descript. :
        """
        self.__num_drops = num_drops

    def mouseDoubleClickEvent(self, event):
        """
        Descript. :
        """
        position = QPointF(event.pos())
        #this is ugly.
        self.parent.navigation_item_double_clicked(\
              0.5 + 0.5 * position.x() / self.scene().width(),
              position.y() / self.scene().height())
