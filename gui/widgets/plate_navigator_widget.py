#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from gui.utils import Icons, QtImport

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class PlateNavigatorWidget(QtImport.QWidget):

    def __init__(self, parent, realtime_plot=False):

        QtImport.QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.__current_location = [0, 0]

        # Graphic elements ----------------------------------------------------
        self.plate_navigator_table = QtImport.QTableWidget(self)
        self.plate_navigator_cell = QtImport.QGraphicsView(self)

        # Layout --------------------------------------------------------------
        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(self.plate_navigator_table)
        _main_hlayout.addWidget(self.plate_navigator_cell)
        _main_hlayout.addStretch()
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        # self.plate_navigator_cell.setSizePolicy

        # Qt signal/slot connections ------------------------------------------
        self.plate_navigator_table.itemDoubleClicked.\
            connect(self.navigation_table_double_clicked)

        # Other ---------------------------------------------------------------
        self.navigation_graphicsscene = QtImport.QGraphicsScene(self)
        self.plate_navigator_cell.setScene(self.navigation_graphicsscene)
        self.navigation_item = NavigationItem(self)
        # self.navigation_item.mouseDoubleClickedSignal.connect(\
        #     self.navigation_item_double_clicked)
        self.navigation_graphicsscene.addItem(self.navigation_item)
        self.navigation_graphicsscene.update()
        self.plate_navigator_cell.setEnabled(False)
        #font = self.plate_navigator_table.font()
        # font.setPointSize(8)
        # self.plate_navigator_table.setFont(font)
        self.plate_navigator_table.setEditTriggers(
            QtImport.QAbstractItemView.NoEditTriggers)

        self.plate_navigator_table.setHorizontalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff)
        self.plate_navigator_table.setVerticalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff)
        self.plate_navigator_cell.setHorizontalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff)
        self.plate_navigator_cell.setVerticalScrollBarPolicy(
            QtImport.Qt.ScrollBarAlwaysOff)
    
        if HWR.beamline.plate_manipulator is not None:
            self.init_plate_view()

    def refresh_plate_location(self):
        new_location = HWR.beamline.plate_manipulator.get_plate_location()
        self.plate_navigator_cell.setEnabled(True)
 
        if new_location:
            row = new_location[0]
            col = new_location[1]
            pos_x = new_location[2]
            pos_y = new_location[3]
            self.navigation_item.set_navigation_pos(pos_x, pos_y)
            self.plate_navigator_cell.update()
            if self.__current_location != new_location:
                empty_item = QtImport.QTableWidgetItem(QtImport.QIcon(), "")
                self.plate_navigator_table.setItem(self.__current_location[0],
                                                   self.__current_location[1],
                                                   empty_item)
                new_item = QtImport.QTableWidgetItem(Icons.load_icon("sample_axis"), "")
                self.plate_navigator_table.setItem(row, col, new_item)
                self.__current_location = new_location
            

    def init_plate_view(self):
        """Initalizes plate info
        """
        cell_width = 25
        cell_height = 23

        plate_info = HWR.beamline.plate_manipulator.get_plate_info()

        self.num_cols = plate_info.get("num_cols", 12)
        self.num_rows = plate_info.get("num_rows", 8)
        self.num_drops = plate_info.get("num_drops", 3)

        self.plate_navigator_table.setColumnCount(self.num_cols)
        self.plate_navigator_table.setRowCount(self.num_rows)

        for col in range(self.num_cols):
            temp_header_item = QtImport.QTableWidgetItem("%d" % (col + 1))
            self.plate_navigator_table.setHorizontalHeaderItem(
                col, temp_header_item)
            self.plate_navigator_table.setColumnWidth(col, cell_width)

        for row in range(self.num_rows):
            temp_header_item = QtImport.QTableWidgetItem(chr(65 + row))
            self.plate_navigator_table.setVerticalHeaderItem(
                row, temp_header_item)
            self.plate_navigator_table.setRowHeight(row, cell_height)

        for col in range(self.num_cols):
            for row in range(self.num_rows):
                temp_item = QtImport.QTableWidgetItem()
                self.plate_navigator_table.setItem(row, col, temp_item)

        table_width = cell_width * (self.num_cols + 1)
        table_height = (cell_height + 2) * (self.num_rows + 1)
        self.plate_navigator_table.setFixedWidth(table_width)
        self.plate_navigator_table.setFixedHeight(table_height)
        self.plate_navigator_cell.setFixedHeight(table_height)
        self.plate_navigator_cell.setFixedWidth(200)
        self.setFixedHeight(table_height + 2)
        self.navigation_graphicsscene.setSceneRect(0, 0, table_height, 200)
        

        self.navigation_item.set_size(200, table_height)
        self.navigation_item.set_num_drops_per_cell(plate_info['num_drops'])
        self.refresh_plate_location()

    def navigation_item_double_clicked(self, pos_x, pos_y):
        drop = int(pos_y * self.num_drops) + 1
        HWR.beamline.plate_manipulator.load_sample(
            (int(self.__current_location[0] + 1),
             int((self.__current_location[1]) * self.num_drops + drop)),
            pos_x, pos_y, wait=False)

    def navigation_table_double_clicked(self, table_item):
        """Moves to the col/row double clicked by user
        """
        HWR.beamline.plate_manipulator.load_sample(
            (table_item.row() + 1, table_item.column() * self.num_drops + 1),
            wait=False)

    # def set_navigation_cell_width(self, width):
    #    self.plate_navigator_cell.setFixedWidth(width)
    #    self.navigation_item.rect.setWidth(width)


class NavigationItem(QtImport.QGraphicsItem):

    def __init__(self, parent=None):

        QtImport.QGraphicsItem.__init__(self)

        self.parent = parent
        self.rect = QtImport.QRectF(0, 0, 0, 0)
        self.setPos(0, 0)
        #self.setMatrix = QtGui.QMatrix()

        self.__num_drops = None
        self.__navigation_posx = None
        self.__navigation_posy = None

    def boundingRect(self):
        return self.rect.adjusted(0, 0, 0, 0)

    def set_size(self, width=None, height=None):
        if width:
            self.rect.setWidth(width)
        if height:
            self.rect.setHeight(height)

    def paint(self, painter, option, widget):
        pen = QtImport.QPen(QtImport.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtImport.Qt.black)
        painter.setPen(pen)

        if self.__num_drops:
            for drop_index in range(self.__num_drops):
                pos_x = self.scene().width() / 2
                pos_y = float(drop_index + 1) / (self.__num_drops + 1) * \
                    self.scene().height()
                painter.drawLine(pos_x - 4, pos_y - 4,
                                 pos_x + 4, pos_y + 4)
                painter.drawLine(pos_x + 4, pos_y - 4,
                                 pos_x - 4, pos_y + 4)
                
        pen.setColor(QtImport.Qt.blue)
        pen.setWidth(2)
        #        painter.drawLine(pos_x - 2, pos_y - 2,
        #                         pos_x + 2, pos_y + 2)
        #        painter.drawLine(pos_x - 2, pos_y + 2,
        #                         pos_x + 2, pos_y - 2)
        # pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        if self.__navigation_posx and self.__navigation_posy:
            painter.drawLine(self.__navigation_posx - 8, self.__navigation_posy,
                             self.__navigation_posx + 8, self.__navigation_posy)
            painter.drawLine(self.__navigation_posx, self.__navigation_posy - 8,
                             self.__navigation_posx, self.__navigation_posy + 8)

    def set_navigation_pos(self, pos_x, pos_y):
        self.__navigation_posx = (pos_x - 0.5) * 2 * self.scene().width()
        self.__navigation_posy = pos_y * self.scene().height()
        #self.__navigation_posx = pos_x
        #self.__navigation_posy = pos_y
        self.scene().update()

    def set_num_drops_per_cell(self, num_drops):
        self.__num_drops = num_drops

    def mouseDoubleClickEvent(self, event):
        position = QtImport.QPointF(event.pos())
        # this is ugly.
        self.parent.navigation_item_double_clicked(
            0.5 + 0.5 * position.x() / self.scene().width(),
            position.y() / self.scene().height())
