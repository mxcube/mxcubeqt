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
from QtImport import *

PYMCA_IMPORTED = False
try:
   if qt_variant == "PyQt5":
       from PyMca5.PyMca import QPeriodicTable
   else:
       from PyMca import QPeriodicTable
   PYMCA_IMPORTED = True
except:
   pass
   

class PeriodicTableWidget(QWidget):
    """
    Descript. :
    """ 
    elementEdgeSelectedSignal = pyqtSignal(str, str)

    def __init__(self, parent=None, name=None, fl=0):

        QWidget.__init__(self, parent, Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)
        self.selected_element = None
        self.selected_edge = "L3"

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        if PYMCA_IMPORTED:
            self.periodic_table = CustomPeriodicTable(self)
            self.periodic_table.setFixedSize(470, 230)
        else:
            self.periodic_elements_combo = QComboBox(self)
            self.periodic_elements_combo.setFixedWidth(100)

        self.edge_widget = QWidget(self)
        edge_label = QLabel("Edge:", self.edge_widget)
        self.edge_combo = QComboBox(self.edge_widget)

        # Layout --------------------------------------------------------------
        _edge_hlayout = QHBoxLayout(self.edge_widget)
        if not PYMCA_IMPORTED:
            _edge_hlayout.addWidget(self.periodic_elements_combo)
        _edge_hlayout.addWidget(edge_label)
        _edge_hlayout.addWidget(self.edge_combo)  
        _edge_hlayout.addStretch(0)
        _edge_hlayout.setSpacing(2)
        _edge_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        if PYMCA_IMPORTED:
            _main_vlayout.addWidget(self.periodic_table, Qt.AlignHCenter)
        _main_vlayout.addWidget(self.edge_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        if PYMCA_IMPORTED:
            self.periodic_table.edgeSelectedSignal.connect(self.edge_selected)
        else:
            self.periodic_elements_combo.activated.connect(\
                  self.element_combo_activated)
        self.edge_combo.addItem("K")
        self.edge_combo.activated.connect(self.edge_combo_activated)
        self.edge_combo.setEnabled(False)

        # Other ---------------------------------------------------------------

    def element_combo_activated(self, element):
        self.selected_element = str(self.periodic_elements_combo.currentText())
        self.selected_edge = str(self.edge_combo.currentText())
        self.elementEdgeSelectedSignal.emit(self.selected_element,
                                            self.selected_edge)

    def edge_selected(self, element, edge):
        self.selected_element = str(element)
        self.selected_edge = str(edge)
        self.edge_widget.setEnabled(self.selected_edge != "K")

        self.edge_combo.clear()
        if edge == "K":
            edge_list = ("K")
        else:
            edge_list = ("L1", "L2", "L3")
        for item in edge_list:
            self.edge_combo.addItem(item)
        self.edge_combo.setCurrentIndex(edge_list.index(item))
        self.edge_combo.setEnabled(self.edge_combo.count() > 1)
        self.elementEdgeSelectedSignal.emit(self.selected_element, 
                                            self.selected_edge)
        
    def set_current_element_edge(self, element, edge):
        if PYMCA_IMPORTED:
            self.periodic_table.table_element_clicked(element, edge)

    def get_selected_element_edge(self):
        return self.selected_element, self.selected_edge

    def edge_combo_activated(self, item_index):
        self.selected_edge = str(self.edge_combo.currentText())
        self.elementEdgeSelectedSignal.emit(self.selected_element,
                                            self.selected_edge)

    def set_elements(self, elements):
        if PYMCA_IMPORTED:
            self.periodic_table.setElements(elements)
        else:
            for element in elements:
                self.periodic_elements_combo.addItem(element['symbol']) 

if PYMCA_IMPORTED: 
    class CustomPeriodicTable(QPeriodicTable.QPeriodicTable):

        edgeSelectedSignal = pyqtSignal(str, str)

        def __init__(self, *args):
            QPeriodicTable.QPeriodicTable.__init__(self, *args)

            self.elements_dict={}
            if qt_variant == 'PyQt5':
                self.elementClicked.connect(self.table_element_clicked)
            else:
                QObject.connect(self,
                                SIGNAL('elementClicked'),
                                self.table_element_clicked)
            for b in self.eltButton:
                self.eltButton[b].colors[0]= QColor(Qt.green)
                self.eltButton[b].colors[1]= QColor(Qt.darkGreen)
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

        def table_element_clicked(self, symbol, energy=None):
            if type(symbol) is tuple and len(symbol) > 0:
                symbol = symbol[0]

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
                #self.widgetSynchronizeSignal([symbol, energy])

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
