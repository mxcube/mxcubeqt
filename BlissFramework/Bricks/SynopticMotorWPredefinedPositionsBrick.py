from qt import *

import SynopticBrick
import MotorBrick


__category__ = 'Synoptic'


class SynopticMotorWPredefinedPositionsBrick(SynopticBrick.SynopticBrick):
    def __init__(self, *args):
        SynopticBrick.SynopticBrick.__init__.im_func(self, *args)
        
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('allow_control', 'boolean', False)
        self.addProperty('mode', 'combo', ('expert', 'user'), 'user')
        self.motor = None
        self.buttons = []

        self.expertPanel = QVBox(self.containerBox)
	self.motorWidget = MotorBrick.MotorBrick(self.expertPanel)
	expertPanelButtonsBox = QGrid(2, Qt.Vertical, self.expertPanel)
        QLabel('pos. name :', expertPanelButtonsBox)
	self.txtPositionName = QLineEdit(expertPanelButtonsBox)
        QLabel('', expertPanelButtonsBox) #just a spacer in fact
	self.cmdSetPosition = QPushButton('Set pos.', expertPanelButtonsBox)
                            
        self.motorWidget['appearance'] = 'tiny'
        self.motorWidget['allowDoubleClick'] = True
	expertPanelButtonsBox.setMargin(5)
	expertPanelButtonsBox.setSpacing(5)

        QObject.connect(self.cmdSetPosition, SIGNAL('clicked()'), self.cmdSetPositionClicked)

    
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            for button in self.buttons:
                button.close(True)
            self.buttons = []

            if self.motor is not None:
                self.disconnect(self.motor, PYSIGNAL('stateChanged'), self.motorStateChanged)
                self.disconnect(self.motor, PYSIGNAL('newPredefinedPositions'), self.fillPositions)
                self.disconnect(self.motor, PYSIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)
                
            self.motor = self.getHardwareObject(newValue)

            if self.motor is not None:
                self.motorWidget.setMnemonic(newValue)
                
                self.connect(self.motor, PYSIGNAL('stateChanged'), self.motorStateChanged)
                self.connect(self.motor, PYSIGNAL('newPredefinedPositions'), self.fillPositions)
                self.connect(self.motor, PYSIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)
            
                self['title'] = self.motor.userName()

                self.fillPositions()
            else:
                self.motorWidget.setMnemonic('')
        elif propertyName == 'mode':
            if newValue == 'expert':
                self.expertPanel.show()
            else:
                self.expertPanel.hide()
        elif propertyName == 'allow_control':
            pass
        else:
            SynopticBrick.SynopticBrick.propertyChanged.im_func(self, propertyName, oldValue, newValue)
            

    def fillPositions(self):
        for button in self.buttons:
            button.close(True)
        self.buttons = []

        for position in self.motor.getPredefinedPositionsList():
            newButton = QPushButton(position, self.containerBox)
            newButton.installEventFilter(self)
            newButton.setMinimumWidth(self.fontMetrics().width('0123456789'))
            newButton.setToggleButton(True)
            newButton.show()
            
            self.buttons.append(newButton)

        if self.motor.isReady():
            self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)
        

    def eventFilter(self, object, event):
        if not event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick, QEvent.KeyPress, QEvent.KeyRelease]:
            return False
        
        if self['allow_control']:
            if object.text() == self.motor.getCurrentPositionName():
                return True
                
            self.motor.moveToPosition(str(object.text()))

            for button in self.buttons:
                button.setOn(False)
                
            return False
        else:
            return True

        
    def motorStateChanged(self, state):
	s = state == self.motor.READY
        
        for button in self.buttons:
            button.setEnabled(s)
            
        self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)


    def predefinedPositionChanged(self, positionName, offset):
        for button in self.buttons:
            if button.text() == positionName:
                button.setOn(True)
            else:
                button.setOn(False)


    def cmdSetPositionClicked(self):
        self.motor.setNewPredefinedPosition(str(self.txtPositionName.text()), self.motor.getPosition())
        self.fillPositions()












