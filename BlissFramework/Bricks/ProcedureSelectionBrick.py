'''
Doc please ...
'''

from BlissFramework import BaseComponents
from HardwareRepository import HardwareRepository
from qt import *

# ?
__category__ = 'GuiUtils'

class ProcedureSelectionBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.equipment = None
        self.equipmentsList = []
        self.proceduresList = []
        self.procedureGUI = {}
        self.procedure = None
        self.currentGUI = None

        #
        # add properties
        # 
        self.addProperty('equipment', 'string', '')
        self.addProperty('procedure', 'string', '')

        #
        # create GUI elements
        #
        self.procedureSelectorBox = QFrame(self)
        self.equipmentBox = QHBox(self.procedureSelectorBox)
        self.procedureBox = QHBox(self.procedureSelectorBox)
        self.lblEquipment = QLabel('Equipment :', self.equipmentBox)
        self.lstEquipment = QComboBox(self.equipmentBox)
        self.lblProcedure = QLabel('Procedure :', self.procedureBox)
        self.lstProcedure = QComboBox(self.procedureBox)
        self.procedurePanel = QVBox(self)
        
        #
        # configure GUI elements
        #
        self.equipmentBox.setMargin(5)
        self.equipmentBox.setSpacing(10)
        self.procedureBox.setMargin(5)
        self.procedureBox.setSpacing(10)
        self.procedureSelectorBox.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.procedureSelectorBox.setMidLineWidth(1)
        
        #
        # connect signals / slots
        #
        self.connect(self.lstEquipment, SIGNAL('activated(int)'), self.equipmentChanged)
        self.connect(self.lstProcedure, SIGNAL('activated(int)'), self.procedureChanged)

        #
        # layout
        #
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        QHBoxLayout(self.procedureSelectorBox, 5, 5)
        self.procedureSelectorBox.layout().addWidget(self.equipmentBox, 0, Qt.AlignLeft | Qt.AlignTop)
        self.procedureSelectorBox.layout().addWidget(self.procedureBox, 0, Qt.AlignRight | Qt.AlignTop)
        self.procedureSelectorBox.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        QGridLayout(self, 2, 3, 5, 5)
        self.layout().addWidget(self.procedureSelectorBox, 0, 0, Qt.AlignTop)
        self.layout().addMultiCellWidget(self.procedurePanel, 1, 1, 0, 2)

        self.updateGUI()
               

    def createProceduresList(self):
        self.procedure = None
        self.lstProcedure.clear()
        self.proceduresList = []
        self.procedureChanged(0)
            
        if self.equipment is not None:
            l = QStringList()
            l.append('')
            self.proceduresList.append(None)
            
            for p in self.equipment['procedures']:
                l.append(QString(p.userName()))
                self.proceduresList.append(p) 

            self.lstProcedure.insertStringList(l)

            #
            # force combo box to adjust its size
            #
            self.lstProcedure.setFont(self.lstProcedure.font())
            self.lstProcedure.updateGeometry()
        
            if self.lstProcedure.count() >= 2:
                self.lstProcedure.setCurrentItem(1)
                self.procedureChanged(1)
                

    def createEquipmentsList(self, equipments):
        l = QStringList()
        self.equipment = None
        self.lstEquipment.clear()
        self.lstProcedure.clear()
        self.procedurePanel.hide()
        self.equipmentsList = []
        
        l.append('')
        self.equipmentsList.append(None)
        
        for e in [_f for _f in [self.getHardwareObject(x) for x in equipments] if _f]:
            if len(e['procedures']) > 0:
                l.append(e.userName())
                self.equipmentsList.append(e)

        self.lstEquipment.insertStringList(l)

        #
        # force combo box to adjust its size
        #
        self.lstEquipment.setFont(self.lstEquipment.font())
        self.lstEquipment.updateGeometry()
        
        if self.lstEquipment.count() >= 2:
            self.lstEquipment.setCurrentItem(1)
            self.equipmentChanged(1)
                
                
    def updateGUI(self):
        self.createEquipmentsList(self['equipment'].split())
        self.createProceduresList()
  

    def propertyChanged(self, name, oldValue, newValue):
        self.updateGUI()


    def equipmentChanged(self, index):
        self.equipment = self.equipmentsList[index]
        self.createProceduresList()

        
    def procedureChanged(self, index):
        if self.currentGUI is not None:
            self.currentGUI.hide()

        self.procedurePanel.show()
              
        if index > 0 and len(self.proceduresList) > index:            
            self.procedure = self.proceduresList[index]
            equipmentName = str(self.equipment.name())
                
            if not equipmentName in self.procedureGUI:
                self.procedureGUI[equipmentName] = {}

            if not index in self.procedureGUI[equipmentName]:
                self.procedureGUI[equipmentName][index] = self.procedure.GUI(self.procedurePanel, equipmentName)

            self.currentGUI = self.procedureGUI[equipmentName][index]
            
            if self.currentGUI is not None:
                self.currentGUI.show()
        
        












