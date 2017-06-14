
'''
Motor with predefined positions
'''

__category__ = 'Motor'

__author__ = 'Matias Guijarro'
__version__ = '1.0'

from qt import *
from HardwareRepository import HardwareRepository
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Bricks import MotorBrick
import logging


class MotorWPredefinedPositionsBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.motor = None #Hardware Object
        
        #
        # add properties and brick signals
        #
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('showButtons', 'boolean', False)
	self.addProperty('mode', 'combo', ('expert', 'user'), 'user')
 
        #
        # create GUI components
        #
        self.buttons = []
	self.lblUsername = QLabel('motor :', self)
	self.posButtonsPanel = QVButtonGroup(self)
        self.lstPositions = QComboBox(self)
        self.expertPanel = QVBox(self)
	self.motorWidget = MotorBrick.MotorBrick(self.expertPanel)
	expertPanelButtonsBox = QGrid(2, Qt.Vertical, self.expertPanel)
        QLabel('pos. name :', expertPanelButtonsBox)
	self.txtPositionName = QLineEdit(expertPanelButtonsBox)
        QLabel('', expertPanelButtonsBox) #just a spacer in fact
	self.cmdSetPosition = QPushButton('Set pos.', expertPanelButtonsBox)

        #
        # configure GUI components
        #
        self.lstPositions.setEditable(False)
        QToolTip.add(self.lstPositions, 'Select a predefined position to move motor to')
        self.motorWidget['appearance'] = 'tiny'
        self.motorWidget['allowDoubleClick'] = True
	self.posButtonsPanel.setInsideMargin(5)
	self.posButtonsPanel.setInsideSpacing(0)
	self.posButtonsPanel.setFrameStyle(QFrame.NoFrame)
	self.posButtonsPanel.setExclusive(True)
	expertPanelButtonsBox.setMargin(5)
	expertPanelButtonsBox.setSpacing(5)        

        #
        # connect signals / slots
        #
        QObject.connect(self.lstPositions, SIGNAL('activated( int )'), self.lstPositionsClicked)
        QObject.connect(self.cmdSetPosition, SIGNAL('clicked()'), self.cmdSetPositionClicked)

        #
        # layout
        #
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed) 

        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(self.lblUsername, 0)
        self.layout().addWidget(self.lstPositions, 0)
        self.layout().addWidget(self.posButtonsPanel, 0)
        self.layout().addWidget(self.expertPanel, 0)


    def lstPositionsClicked(self, index):
        if index > 0:
            if self.motor.isReady():
                self.motor.moveToPosition(str(self.lstPositions.text(index)))
            else:
                self.lstPositions.setCurrentItem(0)
  
    
    def posButtonClicked(self):
        for button in self.buttons:
            if button.isOn():
                if self.motor.isReady():
                    self.motor.moveToPosition(str(button.text()))
                else:
                    button.setOn(False)
                break
        

    def motorStateChanged(self, state):
	s = state == self.motor.READY
        
        for button in self.buttons:
            button.setEnabled(s)
            
        self.lstPositions.setEnabled(s)

        if s:
            self.lstPositions.setEnabled(True)
        else:
            self.lstPositions.setEnabled(False)

        try:
            self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)
        except:
            pass
        
    
    def predefinedPositionChanged(self, positionName, offset):
        self.lstPositions.setCurrentItem(0)

        for button in self.buttons:
            button.show()
            button.setOn(False)
            
        for i in range(1, self.lstPositions.count()):
            if self.lstPositions.text(i) == positionName:
                self.lstPositions.setCurrentItem(i)
		if len(self.buttons) > 0:
                    self.buttons[i - 1].setOn(True)
                break
                

    def cleanPositions(self):
        self.lstPositions.clear()
        self.lstPositions.insertItem('')
        for button in self.buttons:
            button.close()

        self.buttons = []

      
    def fillPositions(self, positions = None): 
      self.cleanPositions()

      if self.motor is not None:
	  if positions is None:
              positions = self.motor.getPredefinedPositionsList()
	  
	  for p in positions:
              self.lstPositions.insertItem(p)

              if self['showButtons']:
                  b = QPushButton(p, self.posButtonsPanel)
                  b.setToggleButton(True)
                  QObject.connect(b, SIGNAL('clicked()'), self.posButtonClicked) 
                  self.buttons.append(b)                                           
                  b.show()

          if self.motor.isReady():
              self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)
          
      if self['showButtons']:
          self.lstPositions.hide()
          self.posButtonsPanel.show()
      else:
          self.lstPositions.show()
          self.posButtonsPanel.hide()	      


    def cmdSetPositionClicked(self):
        self.motor.setNewPredefinedPosition(str(self.txtPositionName.text()), self.motor.getPosition())
        self.fillPositions()
        
  
    def setMnemonic(self, mne):
        self.getProperty('mnemonic').setValue(mne)
        
	if self.motor is not None:
            self.disconnect(self.motor, PYSIGNAL('stateChanged'), self.motorStateChanged)
            self.disconnect(self.motor, PYSIGNAL('newPredefinedPositions'), self.fillPositions)
            self.disconnect(self.motor, PYSIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)

        self.motor = self.getHardwareObject(mne)
        
	if self.motor is not None:
            self.motorWidget.setMnemonic(mne)
            self.lblUsername.setText(self.motor.userName() + ' :')

            self.connect(self.motor, PYSIGNAL('newPredefinedPositions'), self.fillPositions)
	    self.connect(self.motor, PYSIGNAL('stateChanged'), self.motorStateChanged)
            self.connect(self.motor, PYSIGNAL('predefinedPositionChanged'), self.predefinedPositionChanged)
            
	    self.fillPositions()
 
            if self.motor.isReady():
                self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)
	else:
            self.lblUsername.setText('motor :')
            self.cleanPositions()
          

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mode':
            if newValue == 'expert':
                self.expertPanel.show()
            else:
                self.expertPanel.hide()
        elif property == 'showButtons':
            self.fillPositions()
	elif property == 'mnemonic':	
            self.setMnemonic(newValue)
        
        
        










