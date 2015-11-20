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

EDGE_LIST = ["L1", "L2", "L3"]

class PeriodicTableWidget(QtGui.QWidget):
    """
    Descript. :
    """ 
    elementEdgeSelectedSignal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent = None, name = None, fl = 0):

        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.periodic_table = CustomPeriodicTable(self)
        self.periodic_table.setFixedSize(470, 230)

        self.edge_widget = QtGui.QWidget(self)
        edge_label = QtGui.QLabel("Edge:", self.edge_widget)
        self.edge_combo = QtGui.QComboBox(self.edge_widget)

        # Layout --------------------------------------------------------------
        _edge_hlayout = QtGui.QHBoxLayout(self.edge_widget)
        _edge_hlayout.addStretch(0)
        _edge_hlayout.addWidget(edge_label)
        _edge_hlayout.addWidget(self.edge_combo)  
        _edge_hlayout.setSpacing(2)
        _edge_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.periodic_table, QtCore.Qt.AlignHCenter)
        _main_vlayout.addWidget(self.edge_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.periodic_table.edgeSelectedSignal.connect(self.edge_selected)
        self.edge_combo.activated.connect(self.edge_combo_activated)

        # Other ---------------------------------------------------------------
        for edge in EDGE_LIST:
            self.edge_combo.addItem(edge)
        self.edge_widget.setEnabled(False)
        self.selected_element = None
        self.selected_edge = "L3"

    def edge_selected(self, element, edge):
        self.selected_element = str(element)
        self.selected_edge = str(edge)
        self.edge_widget.setEnabled(edge != "K")
        if edge != "K":
            self.edge_combo.setCurrentIndex(EDGE_LIST.index(edge))
        self.elementEdgeSelectedSignal.emit(self.selected_element, 
                                            self.selected_edge)
        
    def set_current_element_edge(self, element, edge):
        self.periodic_table.tableElementChanged(element, edge)

    def get_selected_element_edge(self):
        return self.selected_element, self.selected_edge

    def edge_combo_activated(self, item_index):
        self.selected_edge = str(self.edge_combo.currentText())
        self.periodic_table.tableElementChanged(self.selected_element,
                                                self.selected_edge)
  
class CustomPeriodicTable(QPeriodicTable.QPeriodicTable):
    edgeSelectedSignal = QtCore.pyqtSignal(str, str)

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
            self.edgeSelectedSignal.emit(symbol ,energy)
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
