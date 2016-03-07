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

"""
"""

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'General'


class Qt4_CRLBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
	
        # Hardware objects ----------------------------------------------------
        self.crl_hwobj = None
        self.focusing_hwobj = None

        # Internal values -----------------------------------------------------
        self.crl_value = []

        # Properties ----------------------------------------------------------
        self.addProperty('lenseCount', 'integer', 6)
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('focusing', 'string', '')
        self.addProperty('formatString', 'formatString', '#.#')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        #self.main_gbox = QtGui.QGroupBox('Compound Refractive Lenses', self)
        self.main_gbox = QtGui.QGroupBox('CRL', self) 
        top_widget = QtGui.QWidget(self.main_gbox)
        self.mode_combo = QtGui.QComboBox(top_widget)
        #self.status_label = QtGui.QLabel("status", top_widget)
        self.crl_value_table = QtGui.QTableWidget(self.main_gbox)


        # Layout --------------------------------------------------------------
        _top_hlayout = QtGui.QHBoxLayout(top_widget)
        _top_hlayout.addWidget(self.mode_combo)
        #_top_hlayout.addWidget(self.status_label)
        _top_hlayout.setSpacing(2)
        _top_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_gbox_vlayout = QtGui.QVBoxLayout(self.main_gbox)
        _main_gbox_vlayout.addWidget(top_widget)
        _main_gbox_vlayout.addWidget(self.crl_value_table)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.crl_value_table.itemDoubleClicked.connect(\
             self.crl_table_item_doubleclicked)

        # Other ---------------------------------------------------------------
        self.main_gbox.setCheckable(True)
        self.mode_combo.addItem("Out") 
        self.mode_combo.addItem("Automatic")
        self.mode_combo.addItem("Manual")
        self.mode_combo.setCurrentIndex(1)
        self.crl_value_table.setRowCount(1)
        self.crl_value_table.verticalHeader().hide()
        self.crl_value_table.horizontalHeader().hide()
        self.crl_value_table.setRowHeight(0, 20)
        self.crl_value_table.setFixedHeight(26)
	self.crl_value_table.setShowGrid(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'mnemonic':
            if self.crl_hwobj:
                self.disconnect(self.crl_hwobj, 'crlValueChanged', self.crl_value_changed)
            self.crl_hwobj = self.getHardwareObject(new_value)
            if self.crl_hwobj:
                self.connect(self.crl_hwobj, 'crlValueChanged', self.crl_value_changed)
        if property_name == 'focusing':
            if self.focusing_hwobj:
                self.disconnect(self.focusing_hwobj, 'definerPosChanged', self.focusing_mode_changed)
            self.focusing_hwobj = self.getHardwareObject(new_value)
            if self.focusing_hwobj:
                self.connect(self.focusing_hwobj, 'definerPosChanged', self.focusing_mode_changed)
                self.focusing_mode_changed(self.focusing_hwobj.get_focus_mode())
        elif property_name == 'lenseCount':
            self.crl_value_table.setColumnCount(new_value)
            for col_index in range(new_value):
                temp_item = QtGui.QTableWidgetItem("")
                temp_item.setFlags(QtCore.Qt.ItemIsEnabled)
                temp_item.setBackground(Qt4_widget_colors.LIGHT_GRAY)
                self.crl_value_table.setItem(0, col_index, temp_item)
                self.crl_value_table.setColumnWidth(col_index, 20)
                self.crl_value.append(0)
            self.crl_value_table.setFixedWidth(20 * new_value + 6)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def crl_value_changed(self, value):
        for col_index in range(self.crl_value_table.columnCount()): 
            if value[col_index]:
               self.crl_value_table.item(0, col_index).\
                    setBackground(Qt4_widget_colors.LIGHT_GREEN) 
               self.crl_value[col_index] = 1
            else:
               self.crl_value_table.item(0, col_index).\
                    setBackground(Qt4_widget_colors.LIGHT_GRAY)
               self.crl_value[col_index] = 0

    def focusing_mode_changed(self, value):
        self.setEnabled(value == 'unfocused')

    def crl_table_item_doubleclicked(self, tablewidget_item):
        #if > 1
        self.crl_value[tablewidget_item.column()] = \
             1 - self.crl_value[tablewidget_item.column()]
        self.crl_hwobj.set_crl_value(self.crl_value)
