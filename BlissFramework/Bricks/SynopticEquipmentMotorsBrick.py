import logging

from qt import *

import MotorBrick 
import SynopticBrick

__category__ = 'Synoptic'

class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        

class SynopticEquipmentMotorsBrick(SynopticBrick.SynopticBrick):
    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.__func__(self, *args)
        
        self.motors = {}
        self.hardwareObject = None
        
        self.addProperty('mnemonic', 'string')
        self.addProperty('allowControl', 'boolean', True)
        self.addProperty('formatString', 'formatString', '+##.####')
        self.addProperty('displayMode', 'combo', ('tabs', 'list'), 'list')
                   
        self.motorPanel = QVBox(self.containerBox)
                           

    def setMnemonic(self, mne):
        self['mnemonic'] = mne
                    
        
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            self.hardwareObject = self.getHardwareObject(newValue)

            if len(self['title']) == 0:
                if self.hardwareObject is None:
                    self['title'] = ''
                else:
                    self['title'] = self.hardwareObject.userName()+' :'
                            
            self.showMotors(self['displayMode'])
        elif propertyName == 'allowControl':
            for motor in self.motors.values():
                motor['allowDoubleClick'] = newValue
        elif propertyName == 'formatString':
            for motor in self.motors.values():
                motor['formatString'] = newValue
        elif propertyName == 'displayMode':
            self.showMotors(newValue)
        else:
            SynopticBrick.SynopticBrick.propertyChanged.__func__(self, propertyName, oldValue, newValue)


    def showMotors(self, displayMode):
        self.motors = {}
        self.motorPanel.close(True) #destroy motor panel
        self.motorPanel = QVBox(self.containerBox)

        if self.hardwareObject is None:
            return
        else:
            if self.hardwareObject.hasObject('motors'):
                #an equipment should have a 'motors' section
                motors = self.hardwareObject['motors']
            else:
                logging.getLogger().warning('Equipment %s does not have motors', self.hardwareObject.userName())
            
        if displayMode == 'tabs':
            self.motorPanel.close(True)
            self.motorPanel = QTabWidget(self.containerBox)
        
            for motorCategory in motors.objectsNames():
                motorTab = QVBox(self.motorPanel)

                self.motorPanel.addTab(motorTab, motorCategory)

                for motor in motors[motorCategory].getDevices():
                    newMotorWidget = MotorBrick.MotorBrick(motorTab, motor.name()) 
                    self.motors[motor.name()] = newMotorWidget

                    newMotorWidget.getProperty('mnemonic').setValue(str(motor.name())) #['mnemonic'] = str(motor.name())
                    newMotorWidget.getProperty('appearance').setValue('tiny')
                    newMotorWidget.getProperty('formatString').setValue(self.getProperty('formatString').getUserValue())
                    newMotorWidget.getProperty('allowConfigure').setValue(True)
                    newMotorWidget.getProperty('allowDoubleClick').setValue(self['allowControl'])
		    newMotorWidget.getProperty('dialogCaption').setValue("%s [%s] - %s" % (self['title'], motorCategory, motor.userName()))
                    newMotorWidget.readProperties()

                    if self.isRunning():
                        newMotorWidget.run()

                    newMotorWidget.show()    

                VerticalSpacer(motorTab)
        else:  
            for motor in motors.getDevices():
                newMotorWidget = MotorBrick.MotorBrick(self.motorPanel, motor.name()) 
                self.motors[motor.name()] = newMotorWidget
                
                #newMotorWidget['mnemonic'] = str(motor.name())
                newMotorWidget.getProperty('mnemonic').setValue(str(motor.name()))
                newMotorWidget.getProperty('appearance').setValue('tiny')
                newMotorWidget.getProperty('formatString').setValue(self.getProperty('formatString').getUserValue())
                newMotorWidget.getProperty('allowConfigure').setValue(True)
                newMotorWidget.getProperty('allowDoubleClick').setValue(self['allowControl'])
                newMotorWidget.readProperties()

                if self.isRunning():
                    newMotorWidget.run()

                newMotorWidget.show()

        self.motorPanel.show()
               
                













