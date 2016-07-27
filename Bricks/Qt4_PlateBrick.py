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

from widgets.Qt4_plate_navigator_widget import PlateNavigatorWidget
from Qt4_sample_changer_helper import SampleChanger


__category__ = "Sample changer"


class Qt4_PlateBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
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

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.plate_navigator_widget = PlateNavigatorWidget(self)
        self.crims_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             'widgets/ui_files/Qt4_plate_crims_widget_layout.ui'))

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.plate_navigator_widget)
        _main_vlayout.addWidget(self.crims_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.crims_widget.search_button.clicked.connect(\
             self.search_button_clicked)
        self.crims_widget.move_button.clicked.connect(\
             self.move_to_xtal_clicked)
        self.crims_widget.abort_button.clicked.connect(\
             self.abort_clicked)

        self.crims_widget.xtal_treewidget.currentItemChanged.connect(\
             self.xtal_treewidget_current_item_changed)
        # Other ---------------------------------------------------------------
        self.xtal_image_graphicsscene = QtGui.QGraphicsScene(self)
        self.crims_widget.xtal_image_graphicsview.setScene(\
             self.xtal_image_graphicsscene)
        self.xtal_image_pixmap = QtGui.QPixmap()  
        self.xtal_image_graphics_pixmap = QtGui.QGraphicsPixmapItem()
        self.xtal_image_graphicsscene.addItem(\
             self.xtal_image_graphics_pixmap)

    def propertyChanged(self, propertyName, oldValue, newValue):
        """
        Descript. :
        """
        if propertyName == 'mnemonic':
            self.plate_manipulator_hwobj = self.getHardwareObject(newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

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
        """
        Descript. :
        """
        self.plate_widget.xtal_treewidget.clear()
        #self.plate_widget.xtal_image_label_pixmap.fill(qt.Qt.white) 
        #self.xtal_image_label.setPixmap(self.xtal_image_label_pixmap)

    def move_to_xtal_clicked(self):
        """
        Descript. :
        """
        xtal_item = self.xtal_map.get(self.plate_widget.xtal_treewidget.currentItem())
        if xtal_item:
            self.plate_manipulator_hwobj.load(xtal_item), 
            #     self.plate_widget.child('reposition_cbox').isChecked())

    def abort_clicked(self):
        """
        Descript. :
        """
        if self.plate_manipulator_hwobj:
            self.plate_manipulator_hwobj.abort()
  
    def xtal_treewidget_current_item_changed(self, current_item):
        """
        Descript. :
        """
        xtal_item = self.xtal_map.get(current_item)
        if xtal_item:
            xtal_image_string = xtal_item.get_image()
            #self.xtal_image_label_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_graphics_pixmap.setPixmap(self.xtal_image_pixmap)
            #xtal_image_width = self.xtal_image_pixmap.width()
            #xtal_image_height = self.xtal_image_pixmap.height()
            #self.xtal_image_pixmap.setFixedWidth(xtal_image_width)
            #self.xtal_image_pixmap.setFixedHeight(xtal_image_height)
            #pos_x = int(xtal_image_width * xtal_item.offsetX)
            #pos_y = int(xtal_image_height * xtal_item.offsetY)

    def refresh_plate_content(self):
        """
        Descript. :
        """
        self.plate_widget.xtal_treewidget.clear()
        info_str_list = QtCore.QStringList()
        info_str_list.append(self.plate_content.plate.barcode)
        info_str_list.append(self.plate_content.plate.plate_type)
        root_item = QtGui.QTreeWidgetItem(self.plate_widget.xtal_treewidget,
                                          info_str_list)
        root_item.setExpanded(True)
        for xtal in self.plate_content.plate.xtal_list:
            xtal_address = "%s:%d" % (xtal.row, xtal.column + 1)
            cell_treewidget_item = None
            #cell_treewidget_item = self.plate_widget.xtal_treewidget.\
            #    findItems(xtal_address, QtCore.Qt.MatchExactly, 0)[0]
            if not cell_treewidget_item:
                cell_treewidget_item = root_item

            info_str_list = QtCore.QStringList()
            info_str_list.append(xtal.sample)
            info_str_list.append(xtal.label)
            info_str_list.append(xtal.login)
            info_str_list.append(xtal.row)  
            info_str_list.append(str(xtal.column))
            if xtal.comments:
                info_str_list.append(str(xtal.comments))
            xtal_treewidget_item = QtGui.QTreeWidgetItem(\
                 cell_treewidget_item, info_str_list)
            #self.plate_widget.xtal_treewidget.ensureItemVisible(xtal_treewidget_item) 
            self.xtal_map[xtal_treewidget_item] = xtal
