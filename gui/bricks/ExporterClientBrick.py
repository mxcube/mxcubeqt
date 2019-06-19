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

from gui.utils import QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ExporterClientBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.exporter_client_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.info_widget = QtImport.QWidget(self)
        self.info_address_ledit = QtImport.QLineEdit(self.info_widget)
        self.info_refresh_button = QtImport.QPushButton("Refresh", self.info_widget)
        self.method_table = QtImport.QTableWidget(self)
        self.property_table = QtImport.QTableWidget(self)

        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QtImport.QHBoxLayout(self.info_widget)
        _info_widget_hlayout.addWidget(self.info_address_ledit)
        _info_widget_hlayout.addWidget(self.info_refresh_button)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.info_widget)
        _main_vlayout.addWidget(self.method_table)
        _main_vlayout.addWidget(self.property_table)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.method_table.setColumnCount(2)
        self.method_table.setHorizontalHeaderLabels(["Type", "Method (Parameters)"])
        self.property_table.setColumnCount(4)
        self.property_table.setHorizontalHeaderLabels(
            ["Type", "Property", "Access", "Value"]
        )
        self.setFixedWidth(600)

    def set_expert_mode(self, expert):
        self.setEnabled(expert)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            self.exporter_client_hwobj = self.get_hardware_object(new_value)
            if self.exporter_client_hwobj is not None:
                self.init_tables()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def init_tables(self):
        client_info = self.exporter_client_hwobj.get_client_info()
        self.info_address_ledit.setText("%s:%d" % (client_info[0], client_info[1]))

        method_list = self.exporter_client_hwobj.get_method_list()
        self.method_table.setRowCount(len(method_list))

        for index, method in enumerate(method_list):
            string_list = method.split(" ")
            temp_item = QtImport.QTableWidgetItem(string_list[0])
            self.method_table.setItem(index, 0, temp_item)
            temp_item = QtImport.QTableWidgetItem(string_list[1])
            self.method_table.setItem(index, 1, temp_item)

        property_list = self.exporter_client_hwobj.get_property_list()
        self.property_table.setRowCount(len(property_list))

        for index, prop in enumerate(property_list):
            string_list = prop.split(" ")
            temp_item = QtImport.QTableWidgetItem(string_list[0])
            self.property_table.setItem(index, 0, temp_item)
            temp_item = QtImport.QTableWidgetItem(string_list[1])
            self.property_table.setItem(index, 1, temp_item)
            temp_item = QtImport.QTableWidgetItem(string_list[2])
            self.property_table.setItem(index, 2, temp_item)
            temp_item = QtImport.QTableWidgetItem()
            self.property_table.setItem(index, 3, temp_item)
        self.refresh_property_values()

    def refresh_property_values(self):
        for row in range(self.property_table.rowCount()):
            value = str(
                self.exporter_client_hwobj.read_property(
                    str(self.property_table.item(row, 1).text())
                )
            )
            if len(value) > 100:
                value = value[:100] + "..."
            self.property_table.item(row, 3).setText(value)
