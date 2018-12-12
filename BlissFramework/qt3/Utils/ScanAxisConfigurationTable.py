#$Id: ScanAxisConfigurationTable.py,v 1.1 2004/08/10 10:05:46 guijarro Exp $
from HardwareRepository import HardwareRepository
from BlissFramework.Bricks import MotorBrick

from qt import *
from qttable import QTable
from qttable import QTableItem
from qttable import QCheckTableItem
from qttable import QComboTableItem


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
        if self.motor is not None:
            QObject.disconnect(self.motor, PYSIGNAL('positionChanged'), self.motorPositionChanged)
            
        self.motor = HardwareRepository.HardwareRepository().getHardwareObject(motor_mne)

        if self.motor is not None:
            self.cmdMotorPosition.setEnabled(True)
            QObject.connect(self.motor, PYSIGNAL('positionChanged'), self.motorPositionChanged)
            if self.motor.isReady():
                self.motorPositionChanged(self.motor.getPosition())
            else:
                self.motorPositionChanged('unavailable')
        else:
            self.cmdMotorPosition.setText(MotorPositionReminder.NOPOSITION)
            self.cmdMotorPosition.setEnabled(False)

    
    def motorPositionChanged(self, position):
        if not str(position).isalpha():
            self.cmdMotorPosition.setText('%+8.4f' % position)
        else:
            self.cmdMotorPosition.setText(str(position).center(len(MotorPositionReminder.NOPOSITION)))

        self.table().adjustColumn(self.col())
        self.table().updateGeometry()
        

    def editMotorClicked(self):
        #
        # show full motor control in another window
        #
        if self.controlDialog is None:
            self.controlDialog = MotorBrick.MotorControlDialog(self.cmdMotorPosition, '')
            QObject.connect(self.controlDialog, PYSIGNAL('motorControlDialogClosed'), self.controlDialogClosed)
            self.controlDialog.setMotorMnemonic(self.motor.name())
            self.controlDialog.exec_loop() #modal
        else:
            self.controlDialog.setActiveWindow()


    def controlDialogClosed(self, name):
        del self.controlDialog
        self.controlDialog = None


class ScanAxisConfigurationTable(QTable):
    def __init__(self, parent):
        QTable.__init__(self, parent)

        self.motorList = QStringList()
        self.motors = {}

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setLeftMargin(0) # no vertical header
        self.setNumCols(5)
        self.setNumRows(0)
        self.setVScrollBarMode(QScrollView.AlwaysOff)
        
        self.horizontalHeader().setLabel(0, 'Motor')
        self.horizontalHeader().setLabel(1, 'Motor pos.')
        self.horizontalHeader().setLabel(2, 'Start pos.')
        self.horizontalHeader().setLabel(3, 'End pos.')
        self.horizontalHeader().setLabel(4, 'Nb points')

        self.adjustColumn(2)
        self.adjustColumn(3)
        self.adjustColumn(4)
        self.horizontalHeader().setResizeEnabled(False)
        
        QObject.connect(self, SIGNAL('valueChanged(int, int)'), self.valueChanged)

        
    def sizeHint(self):
        return QSize(self.contentsWidth() +  self.leftMargin() + 2*self.frameWidth(), self.contentsHeight() + self.topMargin() + 2*self.frameWidth())

    
    def addRows(self, rows = 1):
        row = self.numRows()

        QTable.setNumRows(self, row + rows)

        for i in range(rows):
            self.setItem(row + i, 0, QComboTableItem(self, self.motorList))
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
        self.motorList = QStringList()
        self.motors = {}
        
        self.motorList.append('')
        self.motors[''] = None
        
        for motor in motorSet:
            self.motors[motor[1]] = motor[0]
            self.motorList.append(motor[1])

        self.motorList.sort()
        
        for i in range(self.numRows()):
            self.setItem(i, 0, QComboTableItem(self, self.motorList))
            self.setText(i, 2, '')
            self.setText(i, 3, '')
            self.setText(i, 4, '')
                        
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
