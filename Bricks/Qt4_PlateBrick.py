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

import os
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic


from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from Qt4_sample_changer_helper import *


__category__ = "Sample changer"


class Qt4_PlateBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.plate_manipulator_hwobj = None

        # Internal values -----------------------------------------------------
        self.num_cols = None
        self.num_rows = None
        self.num_drops = None
        self.current_location = None
        self.plate_content = None
        self.xtal_map = None

        # Properties ----------------------------------------------------------
        self.addProperty("mnemonic", "string", "")
        self.addProperty("icons", "string", "")
        self.addProperty("doubleClickLoads", "boolean", True)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.plate_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'widgets/ui_files/Qt4_plate_manipulator_layout.ui'))
        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.plate_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.plate_widget.search_button.clicked.connect(\
             self.search_button_clicked)
        self.plate_widget.move_button.clicked.connect(\
             self.move_to_xtal_clicked)
        self.plate_widget.abort_button.clicked.connect(\
             self.abort_clicked)

        self.plate_widget.sample_table.itemDoubleClicked.connect(\
             self.sample_table_double_clicked)
        self.plate_widget.xtal_treewidget.currentItemChanged.connect(\
             self.xtal_treewidget_current_item_changed)
        # Other ---------------------------------------------------------------
        self.navigation_graphicsscene = QtGui.QGraphicsScene(self)
        self.plate_widget.navigation_graphicsview.setScene(\
             self.navigation_graphicsscene)
        self.navigation_item = NavigationItem(self)
        #self.navigation_item.mouseDoubleClickedSignal.connect(\
        #     self.navigation_item_double_clicked)
        self.navigation_graphicsscene.addItem(self.navigation_item)
        self.navigation_graphicsscene.update()
 
        self.xtal_image_graphicsscene = QtGui.QGraphicsScene(self)
        self.plate_widget.xtal_image_graphicsview.setScene(\
             self.xtal_image_graphicsscene)
        self.xtal_image_pixmap = QtGui.QPixmap()  
        self.xtal_image_graphics_pixmap = QtGui.QGraphicsPixmapItem()
        self.xtal_image_graphicsscene.addItem(\
             self.xtal_image_graphics_pixmap)

        self.plate_widget.sample_table.setEditTriggers(\
             QtGui.QAbstractItemView.NoEditTriggers)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'icons':
            icons_list=newValue.split()

        elif propertyName == 'mnemonic':
            if self.plate_manipulator_hwobj:
                self.disconnect(self.plate_manipulator_hwobj, 
                                SampleChanger.INFO_CHANGED_EVENT,
                                self.refresh_plate_location)
            self.plate_manipulator_hwobj = self.getHardwareObject(newValue)
            if self.plate_manipulator_hwobj:
                self.init_plate_view()
                #self.connect(self.plate_manipulator_hwobj, SampleChanger.STATE_CHANGED_EVENT,
                #             self.sample_load_state_changed)
                self.connect(self.plate_manipulator_hwobj, 
                             SampleChanger.INFO_CHANGED_EVENT,
                             self.refresh_plate_location)
                #lf.refresh_plate_location()
        #elif propertyName == 'doubleClickLoads':
        #    self.doubleClickLoads.setChecked(False) #newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def sample_table_double_clicked(self, table_item):
        """
        Descript. : when user double clicks on plate table then sample in
                    corresponding cell is loaded
        """
        item = "%s%d:2" % (chr(65 + table_item.row()),
                           table_item.column() + 1)  
        self.plate_manipulator_hwobj.load(item)

    def search_button_clicked(self):
        """
        Descript. : Searches
        """
        if self.plate_manipulator_hwobj:
            #processing_plan = self.plate_manipulator_hwobj.
            self.plate_content = self.plate_manipulator_hwobj.sync_with_crims(\
                 self.plate_widget.barcode_ledit.text())
            if self.plate_content:
                self.xtal_map = {}
                self.refresh_plate_content()
            else:
                self.clear_view()

    def clear_view(self):
        self.plate_widget.xtal_treewidget.clear()
        self.plate_widget.xtal_image_label_pixmap.fill(qt.Qt.white) 
        self.xtal_image_label.setPixmap(self.xtal_image_label_pixmap)

    def move_to_xtal_clicked(self):
        xtal_item = self.xtal_map.get(\
              self.plate_widget.xtal_treewidget.currentItem())
        if xtal_item:
            self.plate_manipulator_hwobj.load(xtal_item), 
            #     self.plate_widget.child('reposition_cbox').isChecked())

    def abort_clicked(self):
        if self.plate_manipulator_hwobj:
            self.plate_manipulator_hwobj.abort()
  
    def xtal_treewidget_current_item_changed(self, current_item):
        xtal_item = self.xtal_map.get(current_item)
        xtal_image_string = xtal_item.getImage()
        if xtal_image_string:
            #self.xtal_image_label_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_graphics_pixmap.setPixmap(self.xtal_image_pixmap)
            return
            
            xtal_image_width = self.xtal_image_label_pixmap.width()
            xtal_image_height = self.xtal_image_label_pixmap.height()
            self.xtal_image_label.setFixedWidth(xtal_image_width)
            self.xtal_image_label.setFixedHeight(xtal_image_height)
            pos_x = int(xtal_image_width * xtal_item.offsetX)
            pos_y = int(xtal_image_height * xtal_item.offsetY)
            self.xtal_image_label.set_image(xtal_image)

    def refresh_plate_content(self):
        self.plate_widget.xtal_treewidget.clear()
        info_str_list = QtCore.QStringList()
        info_str_list.append(self.plate_content.Plate.Barcode)
        info_str_list.append(self.plate_content.Plate.PlateType)
        root_item = QtGui.QTreeWidgetItem(self.plate_widget.xtal_treewidget,
                                          info_str_list)
        root_item.setExpanded(True)
        for xtal in self.plate_content.Plate.xtal_list:
            xtal_address = "%s:%d" % (xtal.Row, xtal.Column + 1)
            cell_treewidget_item = None
            #cell_treewidget_item = self.plate_widget.xtal_treewidget.\
            #    findItems(xtal_address, QtCore.Qt.MatchExactly, 0)[0]
            if not cell_treewidget_item:
                cell_treewidget_item = root_item

            info_str_list = QtCore.QStringList()
            info_str_list.append(xtal.Sample)
            info_str_list.append(xtal.Label)
            info_str_list.append(xtal.Login)
            info_str_list.append(xtal.Row)  
            info_str_list.append(str(xtal.Column))
            if xtal.Comments:
                info_str_list.append(str(xtal.Comments))
            xtal_treewidget_item = QtGui.QTreeWidgetItem(\
                 cell_treewidget_item, info_str_list)
            #self.plate_widget.xtal_treewidget.ensureItemVisible(xtal_treewidget_item) 
            self.xtal_map[xtal_treewidget_item] = xtal

            self.plate_widget.sample_table.item(\
                 ord(xtal.Row.upper()) - ord('A'), xtal.Column - 1).\
                 setBackground(Qt4_widget_colors.LIGHT_GREEN)

    def refresh_plate_location(self):
        """
        Descript. :
        """
        loaded_sample = self.plate_manipulator_hwobj.getLoadedSample()
        new_location = self.plate_manipulator_hwobj.get_current_location() 
        if self.current_location != new_location:
            #self.plate_widget.navigation_label_painter.setBrush(.QBrush(qt.QWidget.white, qt.Qt.SolidPattern))

            #for drop_index in range(self.num_drops):
            #    pos_y = float(drop_index + 1) / (self.num_drops + 1) * \
            #         self.plate_widget.navigation_graphicsview.height()
            #    self.navigation_graphicsscene.drawLine(58, pos_y - 2, 62, pos_y + 2)
            #    self.navigation_graphicsscene.drawLine(62, pos_y - 2, 58, pos_y + 2)

            if new_location:
                row = new_location[0]
                col = new_location[1]
                pos_x = new_location[2]
                pos_y = new_location[3]
                self.plate_widget.current_location_ledit.setText(\
                     "Col: %d Row: %d X: %.2f Y: %.2f" % (col, row, pos_x, pos_y))
                pos_x *= self.plate_widget.navigation_graphicsview.width()
                pos_y *= self.plate_widget.navigation_graphicsview.height()
                self.navigation_item.set_navigation_pos(pos_x, pos_y)
                self.navigation_graphicsscene.update()    
                if self.current_location:
                    empty_item = QtGui.QTableWidgetItem("")
                    #     QtGui.QTableWidget.Item.Never)
                    self.plate_widget.sample_table.setItem(self.current_location[0],
                                              self.current_location[1],
                                              empty_item)
                new_item = QtGui.QTableWidgetItem(Qt4_Icons.load_icon("sample_axis.png"), "")
                self.plate_widget.sample_table.setItem(row, col, new_item)
            self.current_location = new_location  
            #self.plate_widget.xtal_treewidget.setCurrentItem(\
            #     self.xtal_.firstChild())

    def init_plate_view(self):
        """
        Descript. : initalizes plate info
        """
        plate_info = self.plate_manipulator_hwobj.get_plate_info()

        self.num_cols = plate_info.get("num_cols", 12)
        self.num_rows = plate_info.get("num_rows", 8)
        self.num_drops = plate_info.get("num_drops", 3)

        self.plate_widget.sample_table.setColumnCount(self.num_cols)
        self.plate_widget.sample_table.setRowCount(self.num_rows)

        for col in range(self.num_cols):
            temp_header_item = QtGui.QTableWidgetItem("%d" % (col + 1))
            self.plate_widget.sample_table.setHorizontalHeaderItem(\
                 col, temp_header_item)
            self.plate_widget.sample_table.setColumnWidth(col, 25)

        for row in range(self.num_rows):
            temp_header_item = QtGui.QTableWidgetItem(chr(65 + row))
            self.plate_widget.sample_table.setVerticalHeaderItem(\
                 row, temp_header_item)
            self.plate_widget.sample_table.setRowHeight(row, 25)

        for col in range(self.num_cols):
            for row in range(self.num_rows):
                temp_item = QtGui.QTableWidgetItem()
                self.plate_widget.sample_table.setItem(row, col, temp_item)
        table_height = 25 * (self.num_rows + 1) + 20
        table_width = 25 * (self.num_cols + 1) + 15
        self.plate_widget.sample_table.setFixedWidth(table_width)
        self.plate_widget.sample_table.setFixedHeight(table_height)
        self.plate_widget.navigation_graphicsview.setFixedHeight(table_height)
        self.navigation_item.set_size(120, table_height)
        #self.navigation_graphicsscene.setSceneRect(0, 0, 116, table_height - 4)
        self.navigation_item.set_num_drops_per_cell(\
             self.plate_manipulator_hwobj.get_num_drops_per_cell())
        self.refresh_plate_location()

    def navigation_item_double_clicked(self, pos_x, pos_y):
        self.plate_manipulator_hwobj.move_to_xy(pos_x, pos_y)

class NavigationItem(QtGui.QGraphicsItem):

    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self)

        self.parent = parent
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        self.setPos(0, 0)
        self.setMatrix = QtGui.QMatrix()
 
        self.__num_drops = None
        self.__navigation_posx = None
        self.__navigation_posy = None
    
    def boundingRect(self):
        return self.rect.adjusted(0, 0, 0, 0)

    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtCore.Qt.black)
        painter.setPen(pen)
        if self.__num_drops:
            for drop_index in range(self.__num_drops):
                pos_y = float(drop_index + 1) / (self.__num_drops + 1) * \
                     self.scene().height()
                painter.drawLine(58, pos_y - 2, 62, pos_y + 2)
                painter.drawLine(62, pos_y - 2, 58, pos_y + 2)             
        pen.setColor(QtCore.Qt.blue)
        painter.setPen(pen)
        if self.__navigation_posx and self.__navigation_posy:
            painter.drawLine(self.__navigation_posx - 10, self.__navigation_posy, 
                             self.__navigation_posx + 10, self.__navigation_posy)
            painter.drawLine(self.__navigation_posx, self.__navigation_posy - 10, 
                             self.__navigation_posx, self.__navigation_posy + 10)

    def set_navigation_pos(self, pos_x, pos_y):
        self.__navigation_posx = pos_x
        self.__navigation_posy = pos_y
        self.scene().update()
 
    def set_num_drops_per_cell(self, num_drops):
        self.__num_drops = num_drops 
 
    def mouseDoubleClickEvent(self, event):
        position = QtCore.QPointF(event.pos())
        #this is ugly.
        self.parent.navigation_item_double_clicked(\
              position.x() / self.scene().width(), 
              position.y() / self.scene().height())
