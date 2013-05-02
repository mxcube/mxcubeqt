from BlissFramework import BaseComponents

import GenericScanBrick

from qt import *

__category__ = 'Scans'

class ZapScanBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.scan = None
        self.equipment = None

        #
        # add properties
        #
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('equipment', 'string', '')

        #
        # create GUI elements
        #
        parametersBox = QVBox(self)
        self.scanDimensionBox = GenericScanBrick.ScanDimensionBox(parametersBox)
        self.chkConstantSpeed = QCheckBox('Constant speed', parametersBox)
        self.chkBidirectional = QCheckBox('Bidirectional', parametersBox)
        axisConfigurationBox = QVBox(self)
        QLabel('Select motor for each axis, and configure scan :', axisConfigurationBox)
        self.fastAxisConfiguration = GenericScanBrick.AxisConfigurationTable(axisConfigurationBox)
        self.axisConfiguration = GenericScanBrick.AxisConfigurationTable(axisConfigurationBox)
        self.countTimeBox = GenericScanBrick.CountTimeBox(self)

        #
        # configure elements
        #
        parametersBox.setSpacing(5)
        parametersBox.setMargin(5)
        axisConfigurationBox.setMargin(5)
        self.fastAxisConfiguration.setNumRows(1)
        self.axisConfiguration.setTopMargin(0) # no header
    
        #
        # connect signals / slots
        #
        self.connect(self.axisConfiguration, PYSIGNAL('motorSelected'), self.motorSelected)
        self.connect(self.scanDimensionBox, PYSIGNAL('dimensionChanged'), self.dimensionChanged)
        self.connect(self.countTimeBox, PYSIGNAL('countTimeChanged'), self.countTimeChanged)
        self.connect(self.axisConfiguration, PYSIGNAL('nbPointsChanged'), self.nbPointsChanged)
        self.connect(self.fastAxisConfiguration, PYSIGNAL('motorSelected'), self.fastAxisMotorSelected)
        self.connect(self.fastAxisConfiguration, PYSIGNAL('nbPointsChanged'), self.nbPointsChanged)
        

        #
        # layout
        #
        QVBoxLayout(self, 10, 10)
        self.layout().addWidget(parametersBox, 0, Qt.AlignLeft)
        self.layout().addWidget(axisConfigurationBox, 0, Qt.AlignLeft)
        self.layout().addWidget(self.countTimeBox, 0, Qt.AlignLeft)


    def dimensionChanged(self, newDim):
        dim = newDim - 1

        self.axisConfiguration.setNumRows(dim)

        if newDim > 1:
            self.chkBidirectional.show()
        else:
            self.chkBidirectional.hide()

            
    def motorSelected(self, row, motorMne):
        motor = self.getHardwareObject(motorMne)

        if motor is not None:
            if self.scan.isAbsolute():
                if motor.isReady():
                    pos = str(motor.getPosition())
                else:
                    return
            else:
                pos = 0
                
            self.axisConfiguration.setText(row, 2, pos)
            self.axisConfiguration.setText(row, 3, pos)
                

    def nbPointsChanged(self, row, points):
        if not self.scan.allowDifferentNbPoints():
            self.fastAxisConfiguration.setText(0, 4, points)
            
            for i in range(self.axisConfiguration.numRows()):
                self.axisConfiguration.setText(i, 4, points)


    def countTimeChanged(self, cttime):
        pass
        

    def fastAxisMotorSelected(self, row, motorMne):
        motor = self.getHardwareObject(motorMne)

        if motor is not None:
            if self.scan.isAbsolute():
                if motor.isReady():
                    pos = str(motor.getPosition())
                else:
                    return
            else:
                pos = '0'
                
            self.fastAxisConfiguration.setText(row, 2, pos)
            self.fastAxisConfiguration.setText(row, 3, pos)

        
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            scan = self.getHardwareObject(newValue)
       	    self.setScan(scan)
        elif property == 'equipment':
            self.equipmentMnemonicChanged()


    def setMnemonic(self, mne):
	self['mnemonic'] = mne


    def setScan(self, scan):
        self.scan = scan

        if self.scan is not None:
            dim = self.scan.scanDimension()

            if dim is None:
                self.scanDimensionBox.setEnabled(True)
                self.scanDimensionBox.setDimension(1)
                self.axisConfiguration.setNumRows(0)
                self.chkBidirectional.hide()
            else:
                self.scanDimensionBox.setEnabled(False) #dimension is defined
                self.scanDimensionBox.setDimension(dim)
                self.axisConfiguration.setNumRows(dim - 1)
                if dim <= 1:
                    self.chkBidirectional.hide()
                
            constantSpeed = self.scan.isConstantSpeed()

            if constantSpeed is None:
                self.chkConstantSpeed.setEnabled(True)
                self.chkConstantSpeed.setChecked(False)
            else:
                self.chkConstantSpeed.setEnabled(False)
                self.chkConstantSpeed.setChecked(constantSpeed)

            bidirectional = self.scan.isBidirectional()

            if bidirectional is None:
                self.chkBidirectional.setEnabled(True)
                self.chkBidirectional.setChecked(False)
            else:
                self.chkBidirectional.setEnabled(False)
                self.chkBidirectional.setChecked(bidirectional)
            
        self.equipmentMnemonicChanged()
            

    def setEquipmentMnemonic(self, mne):
        self.getProperty('equipment').setValue(mne)
        self.equipmentMnemonicChanged()


    def equipmentMnemonicChanged(self):
        self.equipment = self.getHardwareObject(self.propertyBag['equipment'])

        if self.equipment is not None:
            motorSet = []
            fastAxisMotorSet = []
            
            for motor in self.equipment['motors']:
                motorSet.append((str(motor.name()), motor.userName())) 
                if motor.getProperty('zapScanCompatible'):
                    fastAxisMotorSet.append(motorSet[-1])

            self.axisConfiguration.setMotors(motorSet)
            self.fastAxisConfiguration.setMotors(fastAxisMotorSet)
        else:
            self.axisConfiguration.setMotors([])
            self.fastAxisConfiguration.setMotors([])


    def launchScan(self):
        if self.scan is not None:
            self.axisConfiguration.activateNextCell()
            self.fastAxisConfiguration.activateNextCell()

            self.scanConfig = {}
            self.scanConfig['dimension'] = self.scanDimensionBox.getDimension()
            self.scanConfig['fastAxis'] = self.fastAxisConfiguration.getScanConfiguration()
            self.scanConfig['axis'] = self.axisConfiguration.getScanConfiguration()
            self.scanConfig['constantSpeed'] = self.chkConstantSpeed.isChecked()
            self.scanConfig['bidirectional'] = self.chkBidirectional.isChecked()
            self.scanConfig['countTime'] = self.countTimeBox.countTime()

            self.scan.launchScan(self.scanConfig)
            
       
    def stopScan(self):
        if self.scan is not None:
            self.scan.stopScan()











