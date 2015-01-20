from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
import logging
from BlissFramework.Utils import widget_colors

__category__ = 'Motor'

class KappaPhiMotorsBrick(BaseComponents.BlissWidget):

    STATE_COLORS = (widget_colors.LIGHT_RED, 
                    widget_colors.DARK_GRAY,
                    widget_colors.LIGHT_GREEN,
                    widget_colors.LIGHT_YELLOW,  
                    widget_colors.LIGHT_YELLOW,
                    widget_colors.LIGHT_YELLOW)

    MAX_HISTORY = 20

    def __init__(self,*args):
        BaseComponents.BlissWidget.__init__(self,*args)

        self.stepEditor=None
        self.diffractometer_hwobj=None
        self.demandMove=0
        self.inExpert=None

        self.addProperty('mnemonic','string','')
        self.addProperty('label','string','')
        self.addProperty('showLabel', 'boolean', True)
        self.addProperty('showBox', 'boolean', True)
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('icons', 'string', '')

        self.containerBox=QHGroupBox(self)
        self.containerBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.labelBox=QHBox(self.containerBox)
        self.motorBox=QHBox(self.containerBox)

        self.label=QLabel(self.labelBox)

        self.kappaValueEdit = QLineEdit(self.motorBox)
        self.kappaValueEdit.setFixedSize(QSize(55,25))
        self.phiValueEdit = QLineEdit(self.motorBox)
        self.phiValueEdit.setFixedSize(QSize(55,25))
        self.moveToPositionsButton = QPushButton("Apply", self.motorBox)  
        self.stopButton = QPushButton(self.motorBox)
        self.stopButton.setPixmap(Icons.load('stop_small'))
        self.stopButton.setEnabled(False)

        self.connect(self.moveToPositionsButton, SIGNAL('clicked()'), self.moveToPositions)
        self.connect(self.stopButton, SIGNAL('clicked()'), self.stopMotors)  
       
        self.stopButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)
        
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj, PYSIGNAL("kappaMoved"), self.kappaMoved) 
                self.disconnect(self.diffractometer_hwobj, PYSIGNAL("phiMoved"), self.phiMoved)
            self.diffractometer_hwobj = self.getHardwareObject(newValue)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj, PYSIGNAL("kappaMoved"), self.kappaMoved)            
                self.connect(self.diffractometer_hwobj, PYSIGNAL("phiMoved"), self.phiMoved)
        elif propertyName=='label':
            self.setLabel(newValue)
        elif propertyName=='showLabel':
            if newValue:
                self.setLabel(self['label'])
            else:
                self.setLabel(None)
        elif propertyName=='showStop':
            if newValue:
                self.stopButton.show()
            else:
                self.stopButton.hide()
        elif propertyName=='showBox':
            if newValue:
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
                self.containerBox.setInsideSpacing(0)
            else:
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                self.containerBox.setInsideMargin(0)
                self.containerBox.setInsideSpacing(0)            
            self.setLabel(self['label'])
        elif propertyName=='icons':
            icons_list=newValue.split()
            try:
                self.moveToPositionsButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass                
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def stopMotors(self):
        self.diffractometer_hwobj.stop_kappa_phi()

    def moveToPositions(self):
        try:
           kappa_value = float(self.kappaValueEdit.text())
           phi_value = float(self.phiValueEdit.text())
           self.diffractometer_hwobj.move_kapp_phi(kappa_value, phi_value)
        except:
           pass

    def kappaMoved(self, value):
        self.kappaValueEdit.setText(str(value))
    
    def phiMoved(self, value):
        self.phiValueEdit.setText(str(value))   

    def setLabel(self,label):
        if not self['showLabel']:
            label=None

        if label is None:
            self.labelBox.hide()
            self.containerBox.setTitle("")
            return

        if self['showBox']:
            self.labelBox.hide()
            self.containerBox.setTitle(label)
        else:
            if label!="":
                label+=": "
            self.containerBox.setTitle("")
            self.label.setText(label)
            self.labelBox.show()

