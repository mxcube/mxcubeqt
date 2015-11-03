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
        self.navigation_label_pixmap = None
        self.num_cols = None
        self.num_rows = None
        self.num_drops = None
        self.current_location = None
        self.plate_content = None
        self.xtal_listview_map = None

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

        #qt.QObject.connect(self.plate_widget.xtal_treewidget, 
        #                   qt.SIGNAL('selectionChanged(QListViewItem *)'), 
        #                   self.xtal_selected)
        # Other ---------------------------------------------------------------
        self.navigation_graphicsscene = QtGui.QGraphicsScene(\
             self.plate_widget.navigation_graphicsview)
        self.navigation_item = NavigationItem(self.navigation_graphicsscene)
        self.navigation_graphicsscene.addItem(self.navigation_item)
        self.navigation_graphicsscene.update()
 
        self.xtal_image_graphicsscene = QtGui.QGraphicsScene(\
             self.plate_widget.xtal_image_graphicsview)
        self.xtal_image_pixmap = QtGui.QGraphicsPixmapItem()
        self.xtal_image_graphicsscene.addItem(self.xtal_image_pixmap)

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
                self.init_plate_view(self.plate_manipulator_hwobj.get_plate_info())
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
        item = "%s%d:%d" %(chr(65 + table_item.row()), table_item.column() + 1, 1) 
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
                self.xtal_listview_map = {}
                self.refresh_plate_content()
            else:
                self.clear_view()

    def clear_view(self):
        self.plate_widget.xtal_treewidget.clear()
        self.plate_widget.xtal_image_label_pixmap.fill(qt.Qt.white) 
        self.xtal_image_label.setPixmap(self.xtal_image_label_pixmap)

    def move_to_xtal_clicked(self):
        xtal_item = self.xtal_listview_map.get(\
              self.plate_widget.xtal_treewidget.currentItem())
        if xtal_item:
            self.plate_manipulator_hwobj._doLoad(xtal_item), 
            #     self.plate_widget.child('reposition_cbox').isChecked())

    def abort_clicked(self):
        if self.plate_manipulator_hwobj:
            self.plate_manipulator_hwobj.abort()
  
    def xtal_selected(self, xtal_treewidget_item):
        xtal_item = self.xtal_listview_map.get(xtal_treewidget_item)
        xtal_image_string = None
        if xtal_item:
            xtal_image_string = xtal_item.getImage()

        self.xtal_image_label_pixmap.fill(qt.Qt.white)
        if xtal_image_string:
             self.xtal_image_label_pixmap.loadFromData(xtal_image_string)
             xtal_image_width = self.xtal_image_label_pixmap.width()
             xtal_image_height = self.xtal_image_label_pixmap.height()
             self.xtal_image_label.setFixedWidth(xtal_image_width)
             self.xtal_image_label.setFixedHeight(xtal_image_height)
             pos_x = int(xtal_image_width * xtal_item.offsetX)
             pos_y = int(xtal_image_height * xtal_item.offsetY)

             self.xtal_image_painter.setBrush(QtGui.QBrush(\
                  QtGui.QColor(0, 0, 150), QtCore.Qt.SolidPattern))
             self.xtal_image_painter.setPen(QtGui.QPen(\
                  QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine))
             self.xtal_image_painter.drawLine(0, pos_y,
                  self.xtal_image_label_pixmap.width(), pos_y)
             self.xtal_image_painter.drawLine(pos_x, 0, 
                  pos_x, self.xtal_image_label_pixmap.height())
        self.xtal_image_label.setPixmap(self.xtal_image_label_pixmap)

    def refresh_plate_content(self):
        self.plate_widget.xtal_treewidget.clear()
        info_str_list = QtCore.QStringList()
        info_str_list.append(self.plate_content.Plate.Barcode)
        info_str_list.append(self.plate_content.Plate.PlateType)
        root_item = QtGui.QTreeWidgetItem(self.plate_widget.xtal_treewidget,
                                          info_str_list)
        root_item.setExpanded(True)
        for xtal in self.plate_content.Plate.Xtal:
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
            self.xtal_listview_map[xtal_treewidget_item] = xtal
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

    def init_plate_view(self, plate_info):
        """
        Descript. : initalizes plate info
        """
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
        self.refresh_plate_location()

class NavigationItem(QtGui.QGraphicsItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self)
        self.rect = QtCore.QRectF(0, 0, 0, 0)
        self.setMatrix = QtGui.QMatrix()
    
    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def set_size(self, width, height):
        self.rect.setWidth(width)
        self.rect.setHeight(height)

    def paint(self, painter, option, widget):
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(QtCore.Qt.black)
        painter.setPen(pen)
        painter.drawRect(2, 2, 20, 20)  
        painter.drawRect(self.rect) 
  
   
    def set_navigation_pos(self, pos_x, pos_y):
        self.navigation_posx = pos_x
        self.navigation_posy = pos_y
