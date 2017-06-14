from BlissFramework import BaseComponents
from HardwareRepository import HardwareRepository
import MotorBrick
import logging

from qt import *
from qttable import QTable
from qttable import QTableItem
from qttable import QCheckTableItem
from qttable import QComboTableItem

__category__ = 'Scans'

class ScanDimensionBox(QHBox):
    def __init__(self, parent, minDim = 1, maxDim = 3):
        QHBox.__init__(self, parent)

        self.dimensions = []
        self.maxDim = maxDim
        self.minDim = minDim

        self.setSpacing(5)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QLabel('Scan dimension :', self)
        self.dimensionGroup = QHButtonGroup(self)
        self.dimensionGroup.setFrameStyle(QFrame.NoFrame)

        for i in range(self.minDim, self.maxDim + 1):
            self.dimensions.append(QRadioButton('%d-D' % i, self.dimensionGroup))
            self.dimensions[-1].setChecked(False)
            self.connect(self.dimensions[-1], SIGNAL('clicked()'), self.dimensionChanged)


    def dimensionChanged(self):
        for dim in self.dimensions:
            if dim == self.sender():
                self.emit(PYSIGNAL('dimensionChanged'), (self.dimensions.index(dim) + 1, ))
                return
            
        
    def getDimension(self):
        for dim in self.dimensions:
            if dim.isChecked():
                return self.dimensions.index(dim) + 1
        return 0

        
    def setDimension(self, dim):
        if dim >= self.minDim or dim <= self.maxDim:
            self.dimensions[dim - 1].setChecked(True)
    

class MotorPositionReminder(QTableItem):
    NOPOSITION = 13*'-'

    def __init__(self, parent):
        QTableItem.__init__(self, parent, QTableItem.Always, '')

        self.motor = None
        self.controlDialog = None
        self.cmdMotorPosition = None

        
    def createEditor(self):
        self.cmdMotorPosition = QPushButton(MotorPositionReminder.NOPOSITION, self.table().viewport())
        f = self.cmdMotorPosition.font()
        f.setFamily('courier')
        self.cmdMotorPosition.setFont(f)
        QToolTip.add(self.cmdMotorPosition, 'Click to edit motor')
        self.cmdMotorPosition.setEnabled(False)

        QObject.connect(self.cmdMotorPosition, SIGNAL('clicked()'), self.editMotorClicked)

        return self.cmdMotorPosition

        
    def setMotor(self, motor_mne):
        self.motor = HardwareRepository.HardwareRepository().getHardwareObject(motor_mne)

        if self.motor is not None:
            self.cmdMotorPosition.setEnabled(True)
            try:
              self.motor.connect('positionChanged', self.motorPositionChanged)
            except:
              logging.getLogger().exception("%s: could not get motor position", self.motor.name())  
              self.motorPositionChanged('unavailable')
            else:
              if self.motor.isReady():
                self.motorPositionChanged(self.motor.getPosition())
              else:
                self.motorPositionChanged('unavailable')
        else:
            self.cmdMotorPosition.setText(MotorPositionReminder.NOPOSITION)
            self.cmdMotorPosition.setEnabled(False)

    
    def motorPositionChanged(self, position):
        if not str(position).isalpha():
            self.cmdMotorPosition.setEnabled(True)
            self.cmdMotorPosition.setText('%+8.4f' % position)
        else:
            self.cmdMotorPosition.setEnabled(False)
            self.cmdMotorPosition.setText(str(position).center(len(MotorPositionReminder.NOPOSITION)))

        self.table().adjustColumn(self.col())
        self.table().updateGeometry()
        

    def editMotorClicked(self):
        #
        # show full motor control in another window
        #
        self.controlDialog = MotorBrick.MotorControlDialog(self.cmdMotorPosition, '')
        self.controlDialog.setMotorMnemonic(self.motor.name())
        self.controlDialog.exec_loop() #modal

           
class AxisConfigurationTable(QTable):
    def __init__(self, parent):
        QTable.__init__(self, parent)

        self.choicesList = QStringList()
        self.motors = {}

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setLeftMargin(0) # no vertical header
        self.setNumCols(5)
        self.setNumRows(0)
        self.setVScrollBarMode(QScrollView.AlwaysOff)
        
        self.horizontalHeader().setLabel(0, 'Axis')
        self.horizontalHeader().setLabel(1, 'Motor pos.')
        self.horizontalHeader().setLabel(2, 'Start pos.')
        self.horizontalHeader().setLabel(3, 'End pos.')
        self.horizontalHeader().setLabel(4, 'Nb points')
        #self.horizontalHeader().setLabel(5, 'Ct. time')
        self.adjustColumn(2)
        self.adjustColumn(3)
        self.adjustColumn(4)
        self.horizontalHeader().setResizeEnabled(False)
        #self.adjustColumn(5)

        self.connect(self, SIGNAL('valueChanged(int, int)'), self.valueChanged)

        
    def sizeHint(self):
        return QSize(self.contentsWidth() +  self.leftMargin() + 2*self.frameWidth(), self.contentsHeight() + self.topMargin() + 2*self.frameWidth())

    
    def addRows(self, rows = 1):
        row = self.numRows()

        QTable.setNumRows(self, row + rows)

        for i in range(rows):
            self.setItem(row + i, 0, QComboTableItem(self, self.choicesList))
            self.setItem(row + i, 1, MotorPositionReminder(self))

        self.adjustColumn(1)
        self.updateGeometry()
        

    def removeRows(self, fromRow):
        QTable.setNumRows(self, fromRow)
        
        self.updateGeometry()


    def setNumRows(self, n):
        nr = self.numRows()

        if nr <= n:
            self.addRows(n - nr)
        else:
            self.removeRows(n)
    

    def setMotors(self, motorSet):
        self.choicesList = QStringList()
        self.motors = {}
        
        self.choicesList.append('')
        self.motors[''] = None
        
        for motor in motorSet:
            self.motors[motor[1]] = motor[0]
            self.choicesList.append(motor[1])

        self.choicesList.sort()
        
        for i in range(self.numRows()):
            self.setItem(i, 0, QComboTableItem(self, self.choicesList))
            self.setText(i, 2, '')
            self.setText(i, 3, '')
            self.setText(i, 4, '')
            #self.setText(i, 5, '')
            
        self.updateGeometry()


    def setStartStopPositions(self, pos):
        row = self.currentRow()
        
        self.setText(row, 2, str(pos))
        self.setText(row, 3, str(pos))


    def valueChanged(self, row, col):
        if col == 0:
            #
            # motor selected
            #
            motorMne = self.motors[str(self.text(row, col))]
            self.item(row, 1).setMotor(motorMne)
            self.emit(PYSIGNAL('motorSelected'), (row, motorMne)) 
        elif col == 4:
            #
            # nb points changed
            #
            points = str(self.text(row, col))
            self.emit(PYSIGNAL('nbPointsChanged'), (row, points))
        #elif col == 5:
            #
            # count time changed
            #
        #    cttime = str(self.text(row, col))
        #    self.emit(PYSIGNAL('countTimeChanged'), (row, cttime))

        
class GenericScanBrick(BaseComponents.ProcedureBrick):
    def __init__(self, *args):
        BaseComponents.ProcedureBrick.__init__(self, *args)
       
        self.equipment = None
        self.scan = None
        experimentTab = self.addPage('Experiment')

        #
        # create GUI elements
        #
        scanParametersBox = QVBox(experimentTab)
        
        axisConfigurationBox = QVBox(experimentTab)
        QLabel('Select motor for each axis, and configure scan :', axisConfigurationBox)
        self.axisConfiguration = AxisConfigurationTable(axisConfigurationBox)
        self.scanType = QLabel('Scan type :', scanParametersBox)
        self.scanDimensionBox = ScanDimensionBox(scanParametersBox)
        countTimeBox = QHBox(experimentTab)
        QLabel('Ct. time :', countTimeBox)
        self.txtCountTime = QLineEdit(countTimeBox)
        
        #
        # configure GUI elements
        #
        countTimeBox.setSpacing(5)
        countTimeBox.setMargin(10)
        axisConfigurationBox.setSpacing(5)
        axisConfigurationBox.setMargin(10)
        scanParametersBox.setSpacing(5)
        scanParametersBox.setMargin(10)
        scanParametersBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        countTimeBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        axisConfigurationBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        #
        # connect signals / slots
        #
        self.connect(self.scanDimensionBox, PYSIGNAL('dimensionChanged'), self.dimensionChanged)
        self.connect(self.axisConfiguration, PYSIGNAL('motorSelected'), self.motorSelected)
        self.connect(self.axisConfiguration, PYSIGNAL('nbPointsChanged'), self.nbPointsChanged)
      
                    
    def dimensionChanged(self, newDim):
        self.axisConfiguration.setNumRows(newDim)
        
    
    def setProcedure(self, proc):
        self.scan = proc
                
        if self.scan is not None:
            self.scan.connect('scanStarted', self.scanStarted)
            self.scan.connect('scanAborted', self.scanAborted)
            self.scan.connect('scanDone', self.scanDone)

            dim = self.scan.scanDimension()

            if dim is None:
                self.scanDimensionBox.show()
                self.scanDimensionBox.setDimension(1)
                self.axisConfiguration.setNumRows(1)
            else:
                self.scanDimensionBox.hide()
                self.axisConfiguration.setNumRows(self.scan.scanDimension())

            if self.scan.isAbsolute():
                self.scanType.setText('Scan type : ABSOLUTE')
            else:
                self.scanType.setText('Scan type : RELATIVE')
        else:
            self.axisConfiguration.setNumRows(0)


    def setEquipment(self, equipment):
        self.equipment = equipment

        if self.equipment is not None:
            motorSet = []

            for motor in self.equipment['motors'].getDevices():
                motorSet.append((str(motor.name()), motor.userName())) 
                self.axisConfiguration.setMotors(motorSet)
        else:
            self.axisConfiguration.setMotors([])


    def motorSelected(self, row, motorMne):
        motor = self.getHardwareObject(motorMne)

        if motor is not None:
            if self.scan.isAbsolute():
                if motor.isReady():
                    pos = str(motor.getPosition())
                else:
                    return
            else:
                pos = '0'
                
            self.axisConfiguration.setStartStopPositions(pos)
                            

    def nbPointsChanged(self, row, points):
        if not self.scan.allowDifferentNbPoints():
            for i in range(self.axisConfiguration.numRows()):
                self.axisConfiguration.setText(i, 4, points)


    def launchProcedure(self):
        if self.scan is not None and self.equipment is not None:
            cttime = str(self.txtCountTime.text())
            specVer = ''
            args=()
 
            self.axisConfiguration.activateNextCell()                    
            for i in range(self.axisConfiguration.numRows()):
                motorSpecName = ''

                for motor in self.equipment['motors'].getDevices():
                    if motor.userName() ==  str(self.axisConfiguration.text(i, 0)):
                        motorSpecName = motor.specName
                        specVer = motor.specVersion
                        break
                        
                startPos = str(self.axisConfiguration.text(i, 2))
                endPos = str(self.axisConfiguration.text(i, 3))
                points = str(self.axisConfiguration.text(i, 4))
        
                if self.scan.allowDifferentNbPoints():
                    args += (motorSpecName, startPos, endPos, points)
                else:
                    args += (motorSpecName, startPos, endPos)

            if not self.scan.allowDifferentNbPoints():
                args += (points, )

            args += (cttime, )
        
            self.scan.setSpecVersion(specVer)
            print args
            self.scan.startScan(*args)
               

    def scanStarted(self):
        self.runStopPanel.disableStart()
        self.runStopPanel.enableStop()

        
    def scanDone(self):
        self.runStopPanel.enableStart()
        self.runStopPanel.disableStop()
        

    def scanAborted(self):
        self.scanDone()

        
    def stopProcedure(self):
        self.scan.abortScan()










