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
Qt4_CRLBrick
"""

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Beam definition"


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

        # Internal values -----------------------------------------------------
        self.crl_value = []

        # Properties ----------------------------------------------------------
        self.addProperty('lenseCount', 'integer', 6)
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '#.#')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = QGroupBox('CRL', self) 
        self.mode_combo = QComboBox(self.main_gbox)
        self.set_according_to_energy_button = QPushButton("Set", self.main_gbox)
        self.set_out_button = QPushButton("Out", self.main_gbox)
        #self.align_beam_button = QtGui.QPushButton("Align", self.main_gbox)
        self.crl_value_table = QTableWidget(self.main_gbox)
        self.move_up_button = QPushButton("", self.main_gbox)
        self.move_down_button = QPushButton("", self.main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_gridlayout = QGridLayout(self.main_gbox)
        _main_gbox_gridlayout.addWidget(self.mode_combo, 0, 0)
        _main_gbox_gridlayout.addWidget(self.set_according_to_energy_button, 0, 1)
        _main_gbox_gridlayout.addWidget(self.set_out_button, 1, 1)
        _main_gbox_gridlayout.addWidget(self.crl_value_table, 1, 0)
        #_main_gbox_gridlayout.addWidget(self.align_beam_button, 1, 1)
        _main_gbox_gridlayout.addWidget(self.move_up_button, 0, 2)
        _main_gbox_gridlayout.addWidget(self.move_down_button, 1, 2)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.mode_combo.activated.connect(self.set_crl_mode)
        self.crl_value_table.itemDoubleClicked.connect(\
             self.crl_table_item_doubleclicked)
        self.set_according_to_energy_button.clicked.connect(\
             self.set_according_to_energy)
        #self.align_beam_button.clicked.connect(self.align_beam)
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button.clicked.connect(self.move_down)    

        # Other ---------------------------------------------------------------
        self.mode_combo.setCurrentIndex(1)
        self.crl_value_table.setRowCount(1)
        self.crl_value_table.verticalHeader().hide()
        self.crl_value_table.horizontalHeader().hide()
        self.crl_value_table.setRowHeight(0, 20)
        self.crl_value_table.setFixedHeight(26)
	self.crl_value_table.setShowGrid(True)

        #self.set_according_to_energy_button.setIcon(Qt4_Icons.load_icon("Up2"))
        #self.set_out_button.setIcon(Qt4_Icons.load_icon("Up2"))
        self.move_up_button.setIcon(Qt4_Icons.load_icon("Up2"))
        self.move_up_button.setFixedWidth(25)
        self.move_down_button.setIcon(Qt4_Icons.load_icon("Down2"))
        self.move_down_button.setFixedWidth(25)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'mnemonic':
            if self.crl_hwobj:
                self.disconnect(self.crl_hwobj, 'crlModeChanged', self.crl_mode_changed)
                self.disconnect(self.crl_hwobj, 'crlValueChanged', self.crl_value_changed)
            self.crl_hwobj = self.getHardwareObject(new_value)
            if self.crl_hwobj:
                self.connect(self.crl_hwobj, 'crlModeChanged', self.crl_mode_changed)
                self.connect(self.crl_hwobj, 'crlValueChanged', self.crl_value_changed)
                self.crl_hwobj.update_values()
        elif property_name == 'lenseCount':
            self.crl_value_table.setColumnCount(new_value)
            for col_index in range(new_value):
                temp_item = QTableWidgetItem("")
                temp_item.setFlags(Qt.ItemIsEnabled)
                temp_item.setBackground(Qt4_widget_colors.LIGHT_GRAY)
                self.crl_value_table.setItem(0, col_index, temp_item)
                self.crl_value_table.setColumnWidth(col_index, 20)
                self.crl_value.append(0)
            self.crl_value_table.setFixedWidth(20 * new_value + 6)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_crl_mode(self):
        """
        Descript. :
        """
        self.crl_hwobj.set_mode(self.mode_combo.currentText())

    def crl_mode_changed(self, mode):
        """
        Descript. :
        """
        self.mode_combo.clear()
        crl_modes = self.crl_hwobj.get_modes()

        self.setEnabled(False)
        if crl_modes:
            self.setEnabled(True)
            for crl_mode in crl_modes:
                self.mode_combo.addItem(crl_mode)
            self.mode_combo.blockSignals(True)
            if mode:
                self.mode_combo.setCurrentIndex(self.mode_combo.findText(mode))
            else:
                self.mode_combo.setCurrentIndex(-1)
            self.mode_combo.blockSignals(False)
            self.crl_value_table.setEnabled(mode == "Manual")
            self.move_up_button.setEnabled(mode == "Manual")
            self.move_down_button.setEnabled(mode == "Manual")
            self.set_according_to_energy_button.setEnabled(mode == "Manual")
                

    def crl_value_changed(self, value):
        """
        Descript. :
        """
        if value:
            self.setEnabled(True)
            for col_index in range(self.crl_value_table.columnCount()): 
                if value[col_index]:
                   self.crl_value_table.item(0, col_index).\
                        setBackground(Qt4_widget_colors.LIGHT_GREEN) 
                   self.crl_value[col_index] = 1
                else:
                   self.crl_value_table.item(0, col_index).\
                        setBackground(Qt4_widget_colors.LIGHT_GRAY)
                   self.crl_value[col_index] = 0
        else:
            self.setEnabled(False)
             

    def crl_table_item_doubleclicked(self, tablewidget_item):
        """
        Descript. :
        """
        self.crl_value[tablewidget_item.column()] = \
             1 - self.crl_value[tablewidget_item.column()]
        self.crl_hwobj.set_crl_value(self.crl_value)

    def set_according_to_energy(self):
        """
        Descript. :
        """
        self.crl_hwobj.set_according_to_energy()

    def move_up(self):
        self.crl_hwobj.move_up()

    def move_down(self):
        self.crl_hwobj.move_down()
