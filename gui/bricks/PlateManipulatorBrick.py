#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
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
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os

import QtImport

from gui.BaseComponents import BaseWidget
from gui.utils import Icons
from gui.utils.sample_changer_helper import SampleChanger
from gui.widgets.plate_navigator_widget import PlateNavigatorWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class PlateManipulatorBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

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
        self.add_property("mnemonic", "string", "")
        self.add_property("icons", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.plate_navigator_widget = PlateNavigatorWidget(self)
        self.crims_widget = QtImport.load_ui_file("plate_crims_widget_layout.ui")

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.plate_navigator_widget)
        _main_vlayout.addWidget(self.crims_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.crims_widget.search_button.clicked.connect(self.search_button_clicked)
        self.crims_widget.move_button.clicked.connect(self.move_to_xtal_clicked)
        self.crims_widget.abort_button.clicked.connect(self.abort_clicked)

        self.crims_widget.xtal_treewidget.currentItemChanged.connect(
            self.xtal_treewidget_current_item_changed
        )

        # Other ---------------------------------------------------------------
        self.xtal_image_graphicsscene = QtImport.QGraphicsScene(self)
        self.crims_widget.xtal_image_graphicsview.setScene(
            self.xtal_image_graphicsscene
        )
        self.xtal_image_pixmap = QtImport.QPixmap()
        self.xtal_image_graphics_pixmap = QtImport.QGraphicsPixmapItem()
        self.xtal_image_graphicsscene.addItem(self.xtal_image_graphics_pixmap)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.plate_manipulator_hwobj is not None:
                self.disconnect(
                    self.plate_manipulator_hwobj,
                    SampleChanger.INFO_CHANGED_EVENT,
                    self.plate_navigator_widget.refresh_plate_location,
                )

            self.plate_manipulator_hwobj = self.get_hardware_object(new_value)

            if self.plate_manipulator_hwobj is not None:
                self.plate_navigator_widget.init_plate_view(
                    self.plate_manipulator_hwobj
                )
                self.connect(
                    self.plate_manipulator_hwobj,
                    SampleChanger.INFO_CHANGED_EVENT,
                    self.plate_navigator_widget.refresh_plate_location,
                )
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def search_button_clicked(self):
        if self.plate_manipulator_hwobj:
            # processing_plan = self.plate_manipulator_hwobj.
            self.plate_content = self.plate_manipulator_hwobj.sync_with_crims(
                self.plate_widget.barcode_ledit.text()
            )
            if self.plate_content:
                self.xtal_map = {}
                self.refresh_plate_content()
            else:
                self.clear_view()

    def clear_view(self):
        self.plate_widget.xtal_treewidget.clear()
        # self.plate_widget.xtal_image_label_pixmap.fill(qt.Qt.white)
        # self.xtal_image_label.setPixmap(self.xtal_image_label_pixmap)

    def move_to_xtal_clicked(self):
        xtal_item = self.xtal_map.get(self.plate_widget.xtal_treewidget.currentItem())
        if xtal_item:
            self.plate_manipulator_hwobj.load(xtal_item),
            #     self.plate_widget.child('reposition_cbox').isChecked())

    def abort_clicked(self):
        if self.plate_manipulator_hwobj:
            self.plate_manipulator_hwobj.abort()

    def xtal_treewidget_current_item_changed(self, current_item):
        xtal_item = self.xtal_map.get(current_item)
        if xtal_item:
            xtal_image_string = xtal_item.get_image()
            # self.xtal_image_label_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_pixmap.loadFromData(xtal_image_string)
            self.xtal_image_graphics_pixmap.setPixmap(self.xtal_image_pixmap)
            # xtal_image_width = self.xtal_image_pixmap.width()
            # xtal_image_height = self.xtal_image_pixmap.height()
            # self.xtal_image_pixmap.setFixedWidth(xtal_image_width)
            # self.xtal_image_pixmap.setFixedHeight(xtal_image_height)
            # pos_x = int(xtal_image_width * xtal_item.offsetX)
            # pos_y = int(xtal_image_height * xtal_item.offsetY)

    def refresh_plate_content(self):
        self.plate_widget.xtal_treewidget.clear()
        info_str_list = QtImport.QStringList()
        info_str_list.append(self.plate_content.plate.barcode)
        info_str_list.append(self.plate_content.plate.plate_type)
        root_item = QtImport.QTreeWidgetItem(
            self.plate_widget.xtal_treewidget, info_str_list
        )
        root_item.setExpanded(True)
        for xtal in self.plate_content.plate.xtal_list:
            xtal_address = "%s:%d" % (xtal.row, xtal.column + 1)
            cell_treewidget_item = None
            # cell_treewidget_item = self.plate_widget.xtal_treewidget.\
            #    findItems(xtal_address, QtCore.Qt.MatchExactly, 0)[0]
            if not cell_treewidget_item:
                cell_treewidget_item = root_item

            info_str_list = QtImport.QStringList()
            info_str_list.append(xtal.sample)
            info_str_list.append(xtal.label)
            info_str_list.append(xtal.login)
            info_str_list.append(xtal.row)
            info_str_list.append(str(xtal.column))
            if xtal.comments:
                info_str_list.append(str(xtal.comments))
            xtal_treewidget_item = QtImport.QTreeWidgetItem(
                cell_treewidget_item, info_str_list
            )
            # self.plate_widget.xtal_treewidget.ensureItemVisible(xtal_treewidget_item)
            self.xtal_map[xtal_treewidget_item] = xtal
