import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from PyMca import QPeriodicTable

__category__ = 'mxCuBE'

class PeriodicTableBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.current_element = None
        self.current_edge = None

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('title', 'string', '')
        self.addProperty('kevFormatString','formatString','##.####')
        self.addProperty('maximumWidth', 'integer', 525)

        self.defineSignal('edgeSelected',())
        self.defineSlot('setDisabled',())
        self.defineSlot('setEnabled',())
        self.defineSlot('setSession',())

        #self.topBox = QHBox(self)
        self.topBox = QVBox(self)
        #self.topBox.setInsideMargin(4)
        #self.topBox.setInsideSpacing(2)

        self.holeBox = QWidget(self.topBox)
        QGridLayout(self.holeBox)

        HOLE = ["Not selected", "L3","L2","L1"]
        self.hole_label = QLabel("Hole:", self.holeBox)
        self.holeBox.layout().addWidget(self.hole_label , 1, 0)
        self.hole = QComboBox(self.holeBox)
        self.holeBox.layout().addWidget(self.hole, 1, 1)
        for item_name in HOLE:
            self.hole.insertItem(item_name)
        QObject.connect(self.hole, SIGNAL('activated(int)'), self.hole_activated)
        #self.hole_label.setEnabled(False)
        #self.hole.setEnabled(False)
        self.hole_label.hide()
        self.hole.hide()

        self.periodicTable=myPeriodicTable(self.topBox)
        self.connect(self.periodicTable,PYSIGNAL('edgeSelected'),self.edgeSelected)
        self.instanceSynchronize("periodicTable")

        QHBoxLayout(self)
        self.layout().addWidget(self.topBox)

    def hole_activated(self, value):
        if value == 3:
            self.current_edge = "L1"
        elif value == 2:
            self.current_edge = "L2"
        else:
            self.current_edge = "L3"
        self.periodicTable.tableElementChanged(self.current_element, self.current_edge)

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            energy = self.getHardwareObject(newValue)
            if energy is not None:
                #self.setElements(energy.getElements())
                self.periodicTable.setElements(energy.getElements())
            else:
                #self.setElements(())
                self.periodicTable.setElements(())
        elif property == 'title':
            self.topBox.setTitle(newValue)
        elif property == 'kevFormatString':
            pass
        elif property == 'maximumWidth':
            self.setMaximumWidth(newValue)
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    def edgeSelected(self, symbol, energy):
        self.emit(PYSIGNAL('edgeSelected'), (symbol, energy))
        self.current_element = symbol

        if energy != "K":
            #self.hole_label.setEnabled(True)
            #self.hole.setEnabled(True)
            self.hole_label.show()
            self.hole.show()
        else:
            #self.hole_label.setEnabled(False)
            #self.hole.setEnabled(False)
            self.hole_label.hide()
            self.hole.hide()
            self.current_edge = energy

    def setSession(self,session_id):
        if session_id is None:
            if self.periodicTable.eltCurrent is not None:
                self.periodicTable.eltCurrent.setCurrent(False)
                self.periodicTable.eltCurrent.setSelected(False)
                self.periodicTable.eltCurrent.leaveEvent(None)
                self.periodicTable.eltCurrent=None
            self.emit(PYSIGNAL('edgeSelected'), (None,None))

class myPeriodicTable(QPeriodicTable.QPeriodicTable):
    def __init__(self, *args):
        QPeriodicTable.QPeriodicTable.__init__(self, *args)

        self.elementsDict={}
        QObject.connect(self,PYSIGNAL('elementClicked'),self.tableElementChanged)
        for b in self.eltButton:
            self.eltButton[b].colors[0]=QColor(Qt.green)
            self.eltButton[b].colors[1]=QColor(Qt.darkGreen)
            self.eltButton[b].setEnabled(False)
        for el in QPeriodicTable.Elements:
            symbol=el[0]
            self.elementsDict[symbol]=el

    def elementEnter(self,symbol,z,name):
        b=self.eltButton[symbol]
        if b.isEnabled():
            b.setCurrent(True)

    def elementLeave(self,symbol):
        b=self.eltButton[symbol]
        if b.isEnabled():
            b.setCurrent(False)

    def tableElementChanged(self,symbol,energy=None):
        if energy is None:
            energy=self.energiesDict[symbol]
        self.setSelection((symbol,))

        if energy is None:
            energy=self.energiesDict[symbol]
        else:
            index=self.elementsDict[symbol][1]
            name=self.elementsDict[symbol][4]
            txt="<large>%s - %s </large>(%s,%s)" % (symbol,energy,index,name)
            self.eltLabel.setText(txt)
            self.emit(PYSIGNAL('edgeSelected'), (symbol,energy))
            self.emit(PYSIGNAL("widgetSynchronize"),((symbol,energy),))
            
    def setElements(self,elements):
        self.energiesDict={}
        for b in self.eltButton:
            self.eltButton[b].setEnabled(False)

        first_el=None
        for el in elements:
            symbol=el["symbol"]
            if first_el is None:
                first_el=symbol
            energy=el["energy"]
            self.energiesDict[symbol]=energy
            b=self.eltButton[symbol]
            b.setEnabled(True)

    def widgetSynchronize(self,state):
        symbol=state[0]
        self.tableElementChanged(symbol,energy)
