"""
EquipmentMotorsBrick

[Description]

The EquipmentMotors brick displays the motors found in an Equipment.

[Properties]

-----------------------------------------
|  name         |  type  | description 
-----------------------------------------
|  mnemonic     | string | Equipment Hardware Object
|  title        | string | title to be shown on top of the brick
|  formatString | string | format string for motor positions
-----------------------------------------

[Signals]

[Slots]

[HardwareObjects]
Any Equipment-derived Hardware Object can be used with the brick.

Example of a valid Equipment XML file :
=======================================
<equipment>
  <username>Slitbox</username>
  <motors>
    <back>
      <device hwrid="/eh2/motors/s2v" role="s2v"/>
      <device hwrid="/eh2/motors/t2v" role="t2v"/>
      <device hwrid="/eh2/motors/s2h" role="s2h"/>
      <device hwrid="/eh2/motors/t2h" role="t2h"/>
    </back>
    <front>
      <device hwrid="/eh2/motors/s1v" role="s1v"/>
      <device hwrid="/eh2/motors/t1v" role="t1v"/>
      <device hwrid="/eh2/motors/s1h" role="s1h"/>
      <device hwrid="/eh2/motors/t1h" role="t1h"/>
    </front>
  </motors>
</equipment>
"""
from BlissFramework import BaseComponents
from HardwareRepository import HardwareRepository
from BlissFramework.Bricks import MotorBrick
from qt import *

__category__ = ''

class EquipmentMotorsBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.panels = {}
        self.motors = []
        self.hardwareObject = None

        self.addProperty('mnemonic', 'string')
        self.addProperty('title', 'string', str(self.name()))
        self.addProperty('formatString', 'formatString', '+##.####')
        
        #
        # create GUI elements
        #
        self.frame = QFrame(self)
        self.lblTitle = QLabel(self)

        #
        # configure GUI elements
        #
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.frame.setFrameStyle(QFrame.NoFrame)
        self.lblTitle.setText('<nobr><h3>%s</h3></nobr>' % str(self.name()))
            
        #
        # layout
        #
        QHBoxLayout(self.frame, 5, 5)
         
        QVBoxLayout(self, 5, 0)
        self.layout().addWidget(self.lblTitle, 0, Qt.AlignTop | Qt.AlignLeft)
        self.layout().addWidget(self.frame, 1, Qt.AlignTop | Qt.AlignLeft)

        
    def updateGUI(self):  
        self.hardwareObject = self.getHardwareObject(self['mnemonic'])

        for motor in self.motors:
            motor.close()

        for panel in self.panels.itervalues():
            self.frame.layout().remove(panel)
            panel.close()

        self.panels = {}
        self.motors = []
         
        if self.hardwareObject:
            if self.hardwareObject.hasObject('motors'):
                ho = self.hardwareObject['motors']
            else:
                print self.hardwareObject.userName(), 'is not an Equipment : no <motors> section.'
                return
                
            for panelName in ho.objectsNames():
                newPanel = QWidget(self.frame)
                newPanel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
                QVBoxLayout(newPanel, 0, 0)
                lbl = QLabel('<b>%s</b>' % panelName, newPanel)
                lbl.setAlignment(Qt.AlignCenter)
                self.panels[panelName] = newPanel
                self.frame.layout().addWidget(newPanel, 0, Qt.AlignTop)
                
                container = QGrid(4, Qt.Vertical, newPanel)
                container.setMargin(0)
                container.setSpacing(5)

                newPanel.layout().addWidget(lbl)
                newPanel.layout().addWidget(container)
                                
                for motor in ho[panelName].getDevices():
                    newMotorWidget = MotorBrick.MotorBrick(container, motor.name())
                    newMotorWidget['mnemonic'] = str(motor.name())
                    newMotorWidget['formatString'] = self.getProperty('formatString').getUserValue()
                    newMotorWidget['appearance'] = 'normal'
                    newMotorWidget['allowConfigure'] = True
                    self.motors.append(newMotorWidget)
                    if self.isRunning():
                        newMotorWidget.run()

                newPanel.show()

            if len(self.panels) == 0:
                #
                # object has no sections defined
                #
                newPanel = QWidget(self.frame)
                newPanel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
                QVBoxLayout(newPanel, 5, 5)
                self.panels[' '] = newPanel
                self.frame.layout().addWidget(newPanel, 0, Qt.AlignTop)

                container = QGrid(4, Qt.Vertical, newPanel)
                container.setMargin(0)
                container.setSpacing(5)

                newPanel.layout().addWidget(container)
                
                for motor in ho.getDevices():
                    newMotorWidget = MotorBrick.MotorBrick(container, motor.name())
                    newMotorWidget.setMnemonic(motor.name())
                    newMotorWidget.getProperty('formatString').setValue(self.getProperty('formatString').getUserValue())
                    newMotorWidget.getProperty('appearance').setValue('normal')
                    newMotorWidget.getProperty('allowConfigure').setValue(True)
                    newMotorWidget.readProperties()
                    self.motors.append(newMotorWidget)
                    if self.isRunning():
                        newMotorWidget.run()

                newPanel.show()
                

    def setMnemonic(self, mne):
        self['mnemonic'] = str(mne)


    
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'title':
            title = '<nobr><h3>%s</h3></nobr>' % newValue
            self.lblTitle.setText(title)

            if len(newValue) == 0:
                self.lblTitle.hide()
            else:
                self.lblTitle.show()
        elif propertyName == 'showBorder':
            if newValue:
                 self.frame.setMidLineWidth(0)
                 self.frame.setLineWidth(1)
                 self.frame.setFrameStyle(QFrame.GroupBoxPanel | QFrame.Sunken)
            else:
                 self.frame.setFrameStyle(QFrame.NoFrame)
        elif propertyName == 'formatString':
            for motor in self.motors:
                motor['formatString'] = newValue
        elif propertyName == 'mnemonic':
            self.updateGUI()














