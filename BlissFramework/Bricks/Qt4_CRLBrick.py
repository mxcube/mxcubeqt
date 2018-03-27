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
        _main_gbox_gridlayout.setSpacing(2)
        _main_gbox_gridlayout.setContentsMargins(2, 2, 2, 2)

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
        self.set_out_button.clicked.connect(self.set_out_clicked)
        self.move_up_button.clicked.connect(self.move_up_clicked)
        self.move_down_button.clicked.connect(self.move_down_clicked)    

        # Other ---------------------------------------------------------------
        self.mode_combo.setCurrentIndex(1)
        self.crl_value_table.setRowCount(1)
        self.crl_value_table.verticalHeader().hide()
        self.crl_value_table.horizontalHeader().hide()
        self.crl_value_table.setRowHeight(0, 20)
        self.crl_value_table.setFixedHeight(24)
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
                crl_modes = self.crl_hwobj.get_modes()
                for crl_mode in crl_modes:
                    self.mode_combo.addItem(crl_mode)
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

    #def set_expert_mode(self, is_expert_mode):
    #    """In the expert mode crl position table is enabled"""
    #    self.crl_value_table.setEnabled(is_expert_mode)

    def set_crl_mode(self):
        """Sets crl mode based on the selected combobox element"""
        self.crl_hwobj.set_mode(self.mode_combo.currentText())

    def crl_mode_changed(self, mode):
        """Updates modes combobox and enables/disables control buttons"""
        self.mode_combo.blockSignals(True)
        if mode:
            self.mode_combo.setCurrentIndex(self.mode_combo.findText(mode))
        else:
            self.mode_combo.setCurrentIndex(-1)
        self.mode_combo.blockSignals(False)
        self.crl_value_table.setEnabled(mode=="Manual")
        self.move_up_button.setEnabled(mode=="Manual")
        self.move_down_button.setEnabled(mode=="Manual")
        self.set_according_to_energy_button.setEnabled(mode=="Manual")

    def crl_value_changed(self, value):
        """Updates crl value table"""
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
        """Double click on the table sets crl value"""
        self.crl_value[tablewidget_item.column()] = \
             1 - self.crl_value[tablewidget_item.column()]
        self.crl_hwobj.set_crl_value(self.crl_value)

    def set_according_to_energy(self):
        """Sets crl value according to current energy"""
        self.crl_hwobj.set_according_to_energy()

    def set_out_clicked(self):
        """Moves all lenses out"""
        self.crl_hwobj.set_crl_value(0)

    def move_up_clicked(self):
        """Moves once up"""
        self.crl_hwobj.move_up()

    def move_down_clicked(self):
        """Moves lenses setting by one down"""
        self.crl_hwobj.move_down()
