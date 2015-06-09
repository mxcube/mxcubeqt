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
from PyMca import QPeriodicTable

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

        self.periodic_table = CustomPeriodicTable(self)

        _main_gbox = QtGui.QGroupBox("Periodic table", self)
        #self.periodic_table = QtGui.QTableWidget(7, 19, _main_gbox)

        # Layout --------------------------------------------------------------
        _main_gbox_vlayout = QtGui.QVBoxLayout(self)
        _main_gbox_vlayout.addWidget(self.periodic_table)
        _main_gbox_vlayout.setSpacing(0)
        _main_gbox_vlayout.setContentsMargins(2, 2, 0, 0)
        _main_gbox.setLayout(_main_gbox_vlayout)

        self.main_layout = QtGui.QVBoxLayout(self)
        self.main_layout.addWidget(_main_gbox)
        self.main_layout.addStretch(0)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)  

        # SizePolicies --------------------------------------------------------
        self.periodic_table.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                          QtGui.QSizePolicy.Fixed)
        self.periodic_table.setFixedSize(450, 300)

        # Qt signal/slot connections ------------------------------------------
        self.connect(self.periodic_table,
                     QtCore.SIGNAL("edgeSelected"),
                     self.edge_selected)

        # Other ---------------------------------------------------------------
        #self.prepare_periodic_table()
        self.selected_element = None
        self.selected_edge = "L3"

    def edge_selected(self, element, edge):
        self.selected_element = element
        self.selected_edge = edge

    def set_current_element_edge(self, element, edge):
        self.periodic_table.tableElementChanged(element, edge)

    def get_selected_element_edge(self):
        return self.selected_element, self.selected_edge
  
class CustomPeriodicTable(QPeriodicTable.QPeriodicTable):
    def __init__(self, *args):
        QPeriodicTable.QPeriodicTable.__init__(self, *args)

        self.elements_dict={}
        QtCore.QObject.connect(self, 
                               QtCore.SIGNAL('elementClicked'),
                               self.tableElementChanged)
        for b in self.eltButton:
            self.eltButton[b].colors[0]= QtGui.QColor(QtCore.Qt.green)
            self.eltButton[b].colors[1]= QtGui.QColor(QtCore.Qt.darkGreen)
            self.eltButton[b].setEnabled(False)
        for el in QPeriodicTable.Elements:
            symbol=el[0]
            self.elements_dict[symbol]=el

    def elementEnter(self, symbol, z, name):
        b = self.eltButton[symbol]
        if b.isEnabled():
            b.setCurrent(True)

    def elementLeave(self, symbol):
        b = self.eltButton[symbol]
        if b.isEnabled():
            b.setCurrent(False)

    def tableElementChanged(self, symbol, energy = None):
        if energy is None:
            energy = self.energies_dict[symbol]
        self.setSelection((symbol,))

        if energy is None:
            energy = self.energies_dict[symbol]
        else:
            index = self.elements_dict[symbol][1]
            name = self.elements_dict[symbol][4]
            txt = "%s - %s (%s,%s)" % (symbol, energy, index, name)
            self.eltLabel.setText(txt)
            self.emit(QtCore.SIGNAL('edgeSelected'), symbol, energy)
            self.emit(QtCore.SIGNAL("widgetSynchronize"), symbol, energy)

    def setElements(self,elements):
        self.energies_dict = {}
        for b in self.eltButton:
            self.eltButton[b].setEnabled(False)

        first_element = None
        for element in elements:
            symbol = element["symbol"]
            if first_element is None:
                first_element = symbol
            energy = element["energy"]
            self.energies_dict[symbol] = energy
            b = self.eltButton[symbol]
            b.setEnabled(True)

    def widgetSynchronize(self,state):
        symbol = state[0]
        self.tableElementChanged(symbol)
