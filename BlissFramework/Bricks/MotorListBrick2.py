from BlissFramework import BaseComponents
from BlissFramework.Bricks import MotorBrick
from BlissFramework import Icons
from qt import *
import os
import logging
from HardwareRepository.HardwareObjects import SpecMotor

'''
Displays a combo-box with all the motors from spec and opens a
dedicated motor dialog box with the click of a button
'''

__category__ = 'Motor'

class MotorListBrick2(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.inExpert=None

        self.addProperty('mnemonic','string','')
        self.addProperty('icons','string','')
        self.addProperty('hideInUser', 'boolean', False)
        self.addProperty('disableInUser', 'boolean', False)
        self.addProperty('defaultWhenUserDisabled', 'boolean', False)
        self.addProperty('showDialogButton', 'boolean', True)
        self.addProperty('defaultSpecMotor', 'string', '')
        self.addProperty('showBox', 'boolean', True)
        self.defineSlot('setEnabled',())
        self.defineSignal('specMotorSelected',())

        self.containerBox=QHGroupBox('Available motors',self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.motorsList=QComboBox(self.containerBox)
        self.motorsList.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        QObject.connect(self.motorsList,SIGNAL('activated(int)'),self.motorSelected)
        self.openButton=QToolButton(self.containerBox)
        self.openButton.setUsesTextLabel(True)
        self.openButton.setTextLabel("Open")
        self.openButton.setTextPosition(QToolButton.BesideIcon)
        self.connect(self.openButton,SIGNAL('clicked()'),self.openCurrentMotor)
        self.openButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        QToolTip.add(self.containerBox,"Lists the available motors")
        QToolTip.add(self.openButton,"Opens a dialog box to control the selected motor")
 
        self.motors={}
        self.dialogs={}
        self.listObj=None

        self.instanceSynchronize("motorsList")

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    # Open a motor dialog box
    def openCurrentMotor(self):
        motor_username=str(self.motorsList.currentText())
        try:
            motor_specname=self.motors[motor_username]
        except KeyError:
            pass
        else:
            if not self.dialogs.has_key(motor_username):
                m=SpecMotor.SpecVersionMotor(self.listObj.getSpecVersion(),motor_specname,motor_username)
                dialog=MotorBrick.MotorControlDialog(self,motor_username)

                s=self.font().pointSize()
                f = dialog.font()
                f.setPointSize(s)
                dialog.setFont(f)
                dialog.motorWidget['fontSize']=s
                dialog.updateGeometry()
                dialog.setFixedSize(dialog.sizeHint())

                dialog.setMotorObject(m)
                self.dialogs[motor_username]=dialog
            else:
                dialog=self.dialogs[motor_username]
            dialog.show()
            dialog.setActiveWindow()
            dialog.raiseW()

    def setEnabled(self,state):
        override=False
        try:
            if state and not self.inExpert and self['disableInUser']:
                override=True
        except:
            override=False
        if not override:
            BaseComponents.BlissWidget.setEnabled(self,state)

    def motorSelected(self,motor_index):
        motor_username=str(self.motorsList.currentText())
        try:
            motor_specname=self.motors[motor_username]
        except KeyError:
            self.emit(PYSIGNAL('specMotorSelected'), (None,None,None))
        else:
            self.emit(PYSIGNAL('specMotorSelected'), (self.listObj.getSpecVersion(),motor_specname,motor_username))

    def run(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def stop(self):
        self.containerBox.show()

    def closeAllMotors(self):
        for d in self.dialogs:
            dialog=self.dialogs[d]
            dialog.reject()
        self.dialogs={}

    def instanceModeChanged(self,mode):
        if mode==BaseComponents.BlissWidget.INSTANCE_MODE_SLAVE:
            self.closeAllMotors()

    # Hide or show the brick
    def setExpertMode(self,state):
        self.inExpert=state
        #print "MotorListBrick.setExpertMode",state

        if self['hideInUser']:
            if state:
                self.containerBox.show()
            else:
                self.closeAllMotors()
                self.containerBox.hide()

        if self['disableInUser']:
            if state:
                self.setEnabled(True)
                QToolTip.add(self.containerBox,"Select the motor you desire to control")
            else:
                self.setEnabled(False)

                if self['defaultWhenUserDisabled']:
                    def_motor=self['defaultSpecMotor']
                    if def_motor!="":
                        for m in self.motors:
                            if self.motors[m]==def_motor:
                                self.motorsList.setCurrentText(m)
                                self.motorSelected(self.motorsList.currentItem())
                                
                QToolTip.add(self.containerBox,"Only in expert mode you're allowed to change this motor")

    def connected(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def disconnected(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def motorsChanged(self,specversion,motors):
        #print "motorsChanged",specversion,motors
        self.motors={}
        self.motorsList.clear()
        for d in self.dialogs:
            self.dialogs[d].accept()
        self.dialogs={}

        if motors is not None:
            motors2={}
            for motor_mne in motors:
                motors2[motors[motor_mne]]=motor_mne
            
            keys=motors2.keys()
            keys.sort()
            for motor_username in keys:
                self.motors[motor_username]=motors2[motor_username]
                self.motorsList.insertItem(motor_username)

            def_motor=self['defaultSpecMotor']
            if def_motor!="":
                try:
                    username=motors[def_motor]
                    self.motorsList.setCurrentText(username)
                except KeyError:
                    pass

            self.motorSelected(self.motorsList.currentItem())

    def propertyChanged(self,propertyName,oldValue,newValue):
        #print "propertyChanged",propertyName,newValue

        if propertyName=='mnemonic':
            if self.listObj is not None:
                self.disconnect(self.listObj,PYSIGNAL('connected'),self.connected)
                self.disconnect(self.listObj,PYSIGNAL('disconnected'),self.disconnected)
                self.disconnect(self.listObj,PYSIGNAL('motorListChanged'),self.motorsChanged)
            self.listObj=self.getHardwareObject(newValue)
            if self.listObj is not None:
                self.connect(self.listObj,PYSIGNAL('connected'),self.connected)
                self.connect(self.listObj,PYSIGNAL('disconnected'),self.disconnected)
                self.connect(self.listObj,PYSIGNAL('motorListChanged'),self.motorsChanged)
                if self.listObj.isConnected():
                    self.connected()
                else:
                    self.disconnected()
                self.motorsChanged(self.listObj.getSpecVersion(),self.listObj.getMotorList())
            else:
                self.disconnected()
                self.motorsChanged(None,None)
        elif propertyName=='icons':
            icons_list=newValue.split()
            try:
                self.openButton.setPixmap(Icons.load(icons_list[0]))
                self.motorsList.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
                self.openButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            except IndexError:
                pass
        elif propertyName=='showDialogButton':
            if newValue:
                self.openButton.show()
            else:
                self.openButton.hide()
        elif propertyName=='showBox':
            if newValue:
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
                self.containerBox.setInsideSpacing(0)
                self.containerBox.setTitle("Available motors")
            else:
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                self.containerBox.setInsideMargin(0)
                self.containerBox.setInsideSpacing(0)
                self.containerBox.setTitle("")
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
