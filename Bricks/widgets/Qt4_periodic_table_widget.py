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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors

PERIODIC_ELEMENTS = [['H', '', '', '', '', '', '', '', '', '', '', '', '',
                      '', '', '', '', '', 'He'],
                     ['Li', 'Be', '', '', '', '', '', '', '', '', '', '',
                      '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
                     ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '',
                      '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
                     ['K',  'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe','Co', 
                      'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se','Br', 'Kr'], 
                     ['Rb', 'Sr', 'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 
                      'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn','Sb', 'Te', 'I', 'Xe'], 
                     ['Cs', 'Ba', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 
                      'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'], 
                     ['Fr', 'Ra', 'Lr', 'Rf', 'Db', 'Sg','Bh', 'Hs', 'Mt']]

class PeriodicTableWidget(QtGui.QWidget):
    """
    Descript. :
    """ 
    def __init__(self, parent = None, name = None, fl = 0):

        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.periodic_table = QtGui.QTableWidget(7, 19, self)

        # Layout --------------------------------------------------------------
        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(self.periodic_table)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)  

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------
        self.connect(self.periodic_table, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"),
                     self.periodic_table_element_changed) 

        # Other ---------------------------------------------------------------
        self.prepare_periodic_table()
        self.selected_element = None
        self.selected_edge = None

    def prepare_periodic_table(self):
        self.periodic_table.verticalHeader().setVisible(False)        
        self.periodic_table.horizontalHeader().setVisible(False)
        self.periodic_table.setShowGrid(False)
        for row_index, row in enumerate(PERIODIC_ELEMENTS):
            for col_index, element_symbol in enumerate(row):
                if len(element_symbol) > 0:
                   self.periodic_table.setItem(row_index, col_index, QtGui.QTableWidgetItem(element_symbol))
                   self.periodic_table.item(row_index, col_index).setBackground(QtGui.QBrush(Qt4_widget_colors.LIGHT_GRAY)) 
                   self.periodic_table.item(row_index, col_index).setTextAlignment(QtCore.Qt.AlignHCenter)
                   self.periodic_table.setColumnWidth(col_index, 30)
            self.periodic_table.setRowHeight (row_index, 30)

    def periodic_table_element_changed(self, current_item):
        self.selected_element = current_item.text() 

    def get_selected_element_edge(self):
        return self.selected_element, self.selected_edge
  
