#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui
from PyQt4 import QtCore

import logging

from HardwareRepository import HardwareRepository
from BlissFramework import Qt4_Icons

class ProcedureBoxLayout(QtGui.QBoxLayout):
    def addItem(self, item):
        item.setAlignment(QtGui.Qt.AlignLeft)
        QtGui.QBoxLayout.addItem(self, item)

          
class HorizontalSpacer(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)


class VerticalSpacer(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        

class ProcedurePanel(QtGui.QWidget):
    """Container for Procedure widgets"""
    def __init__(self, parent, orientation = QtCore.Qt.Vertical):
        """Constructor

        parent -- the parent QObject
        procedure -- the Procedure this panel belongs to (default: None)"""
        QtGui.QWidget.__init__(self, parent)

        self.currentWidget = None
        self.lastCommandID = None
        self.procedure = None

        if isinstance(parent, ProcedurePanel):
            #
            # take the procedure from the parent
            #
            self.setProcedure(parent.getProcedure())
    
        if orientation == QtCore.Qt.Vertical:
            ProcedureBoxLayout(self, QtGui.QBoxLayout.Down, 10, 5)
        else:
            ProcedureBoxLayout(self, QtGui.QBoxLayout.LeftToRight, 10, 5)
            
        self.layout().setAutoAdd(True)


    def addVerticalSpacer(self):
        VerticalSpacer(self)
        

    def addHorizontalSpacer(self):
        HorizontalSpacer(self)
        
        
    def setProcedure(self, proc):
        if proc is None:
            self.procedure = None
        else:
            import weakref
        
            self.procedure = weakref.ref(proc)()

            QtCore.QObject.connect(HardwareRepository.emitter(self.procedure), SIGNAL('replyArrived'), self.replyArrived)


    def getProcedure(self):
        return self.procedure


    def childWidgetValueChanged(self, value, w):        
        if w.isValidating:
            if self.procedure is not None:
                self.currentWidget = w
                
                try:
                    cmd = w.getCommand()
                    self.lastCommandID = eval('self.procedure.' + cmd)
                except:
                    w.validationFailed()
                    logging.getLogger().exception('%s: Cannot execute command "%s" on procedure %s', str(self.name()), cmd, str(self.procedure.name()))
                else:
                    self.procedure.waitReply()
        else:
            w.validationPassed()
                
       
    def replyArrived(self, id, reply):
        import types

        if id == self.lastCommandID:
            self.lastCommandID = None

            if type(reply) == types.StringType and reply.startswith('error:'):
                error = reply.split(':')[1]
                QMessageBox.warning(None, 'Invalid value', '%s' % str(error), QMessageBox.Ok)
                self.currentWidget.validationFailed(error)
            else:
                self.currentWidget.validationPassed(reply)

                    
class ProcedureEntryField(QtGui.QGroupBox):
    """Base class for entry widgets in Procedure panels"""
    def __init__(self, parent, caption = ''):
        """Constructor

        parent -- the parent ProcedurePanel
        caption -- caption (default: no caption)"""
        QtGui.QGroupBox.__init__(self, parent)
                            
        self.isValidating = False
        self.command = ''
        self.savedValue = None
        
        self.setSpacing(5)
        self.setMargin(10)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        QLabel(str(caption), self)

        #
        # search for a Procedure Panel in its ancestors hierarchy
        #
        p = parent
        while p is not None:
            if isinstance(p, ProcedurePanel):
                QObject.connect(self, PYSIGNAL('rawValueChanged'), p.childWidgetValueChanged)
            p = p.parent()


    def setCommand(self, command):
        """Set the command to be executed for this widget

        Each widget has a value and a command. If a command is defined,
        and the widget is validating (self.isValidating == True),
        the command is executed when the value changes. The new value is
        validated upon success.

        command -- a string representing the command to be executed ; use the %(value)s marker to indicate the value."""
        self.command = str(command)

        if self.command.find('%(value)s') < 0:
            logging.getLogger().error('Invalid command : no %(value)s placeholder')
            self.command = ''
            
    
    def getCommand(self):
        if len(self.command) > 0:
            return self.command % { 'value': str(self.getUncheckedValueAsString()) }
        else:
            return ''

        
    def setValidating(self, validate):
        if validate:
            self.isValidating = True
        else:
            self.isValidating = False
    

    def validationPassed(self, reply = None):
        self.emit(PYSIGNAL('valueChanged'), (self.getValue(), ))


    def validationFailed(self, error):
        self.emit(PYSIGNAL('validationFailed'), (error, ))
        

    def valueChanged(self, newValue):
        self.emit(PYSIGNAL('rawValueChanged'), (newValue, self, ))


    def getUncheckedValueAsString(self):
        return ''

    
    def getValue(self):
        pass


    def setValue(self, newValue):
        pass

        
class IntegerEntryField(ProcedureEntryField):
    """Provide a simple integer entry field"""
    def __init__(self, parent, caption = '', minValue = 0, maxValue = 32768, step = 1, unit = ''):
        """Constructor
        
        parent -- the parent QObject
        caption -- a caption string (default: no caption)
        minValue -- minimal accepted value (default: 0)
        maxValue -- maximal accepted value (default: 32768)
        step -- step (default: 1)
        unit -- unit string is appended to the end of the displayed value (default: no string)"""
        ProcedureEntryField.__init__(self, parent, caption)

        box = QWidget(self)
        self.spinbox = QSpinBox(minValue, maxValue, step, box)
        self.spinbox.setSuffix(' ' + str(unit))
        okCancelBox = QHBox(box)
        okCancelBox.setSpacing(0)
        okCancelBox.setMargin(0)
        self.cmdOK = QPushButton(okCancelBox)
        self.cmdCancel = QPushButton(okCancelBox)
        self.cmdOK.setPixmap(Qt4_Icons.load('button_ok_small')) #QPixmap(Icons.okXPM))
        self.cmdOK.setFixedSize(20, 20)
        self.cmdCancel.setPixmap(Qt4_Icons.load('button_cancel_small')) #QPixmap(Icons.cancelXPM))
        self.cmdCancel.setFixedSize(20, 20)
            
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.valueChanged)
        QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.cancelClicked)
        QObject.connect(self.spinbox, SIGNAL('valueChanged(int)'), self.valueChanging)
        
        QHBoxLayout(box, 0, 5)
        box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        box.layout().addWidget(self.spinbox, 0, Qt.AlignLeft)
        box.layout().addWidget(okCancelBox, 0, Qt.AlignLeft)
        box.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.setIsOk(False)


    def setIsOk(self, ok):
        self.setIsInvalid(False)
        
        if ok:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(False)
        else:
            self.cmdOK.setEnabled(True)
            self.cmdCancel.setEnabled(True)


    def setIsInvalid(self, invalid):
        if invalid:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(True)
            self.setPaletteForegroundColor(QColor(255, 0, 0)) #red
        else:
            self.unsetPalette()
                        
        self.spinbox.setFocus()

            
    def validationPassed(self, reply = None):
        self.savedValue = self.spinbox.value()
        self.setIsOk(True)
        
        ProcedureEntryField.validationPassed(self, reply)
        

    def validationFailed(self, reply = None):
        self.setIsInvalid(True)

        ProcedureEntryField.validationFailed(self, reply)
        

    def valueChanging(self):
        self.setIsOk(False)


    def valueChanged(self):
        ProcedureEntryField.valueChanged(self, self.spinbox.value())

        
    def cancelClicked(self):
        if self.savedValue is not None:
            self.spinbox.setValue(self.savedValue)
            self.valueChanged()
               
    
    def getValue(self):
        """Return the value of the widget"""
        if self.cmdOK.isEnabled() == False and self.cmdCancel.isEnabled() == False:
            return self.spinbox.value()


    def getUncheckedValueAsString(self):
        return str(self.spinbox.value())

            
    def setValue(self, newValue):
        """Set the value of the widget"""
        self.setIsOk(False)
        
        try:
            v = int(newValue)
        except:
            QMessageBox.warning(None, 'Invalid value', '%s is not a valid integer value' % str(newValue), QMessageBox.Ok)
        else:
            self.spinbox.setValue(v)
            self.valueChanged()

        return self.cmdOK.isEnabled() == False and self.cmdCancel.isEnabled() == False


class FloatEntryField(ProcedureEntryField):
    """Provide a simple float entry field"""
    def __init__(self, parent, caption = '', unit = ''):
        """Constructor
        
        parent -- the parent QObject
        caption -- a caption string (default: no caption)
        unit -- unit string is appended to the end of the displayed value (default: no string)"""
        ProcedureEntryField.__init__(self, parent, caption)
        
        box = QWidget(self)

        self.savedValue = None
        self.textbox = QLineEdit('', box)
        self.unitLabel = QLabel(str(unit), box) 
        okCancelBox = QHBox(box) 
        okCancelBox.setSpacing(0)
        okCancelBox.setMargin(0)
        self.cmdOK = QPushButton(okCancelBox)
        self.cmdCancel = QPushButton(okCancelBox)
        self.cmdOK.setFixedSize(20, 20)
        self.cmdCancel.setFixedSize(20, 20)
        self.cmdOK.setPixmap(Qt4_Icons.load('button_ok_small')) #QPixmap(Icons.okXPM))
        self.cmdCancel.setPixmap(Qt4_Icons.load('button_cancel_small')) #QPixmap(Icons.cancelXPM))
        
        QObject.connect(self.textbox, SIGNAL('returnPressed()'), self.valueChanged)
        QObject.connect(self.textbox, SIGNAL('textChanged( const QString & )'), self.valueChanging)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.valueChanged)
        QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.cancelClicked)

        self.cmdCancel.setEnabled(False)
        self.cmdOK.setEnabled(True)

        QHBoxLayout(box, 0, 5)
        box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        box.layout().addWidget(self.textbox, 0, Qt.AlignLeft)
        box.layout().addWidget(self.unitLabel, 0, Qt.AlignLeft)
        box.layout().addWidget(okCancelBox, 0, Qt.AlignLeft)
        box.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        

    def setIsOk(self, ok):
        self.setIsInvalid(False)
        
        if ok:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(False)
        else:
            self.cmdOK.setEnabled(True)
            self.cmdCancel.setEnabled(True)


    def setIsInvalid(self, invalid):
        if invalid:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(True)
            self.setPaletteForegroundColor(QColor(255, 0, 0)) #red
            self.textbox.selectAll()
        else:
            self.unsetPalette()
                        
        self.textbox.setFocus()
        

    def validationPassed(self, reply = None):
        self.setIsOk(True)
        self.savedValue = self.textbox.text()
        
        ProcedureEntryField.validationPassed(self, reply)


    def validationFailed(self, reply = None):
        self.setIsInvalid(True)

        ProcedureEntryField.validationFailed(self, reply)


    def valueChanging(self):
        self.setIsOk(False)


    def valueChanged(self):
        try:
            v = float(str(self.textbox.text()))
        except:
            QMessageBox.warning(None, 'Invalid value', '%s is not a valid float value' % str(self.textbox.text()), QMessageBox.Ok)
        else:
            ProcedureEntryField.valueChanged(self, v)


    def cancelClicked(self):
        if self.savedValue is not None:
            self.textbox.setText(self.savedValue)
            self.valueChanged()
            
    
    def getValue(self):
        """Return the value of the widget"""
        if self.cmdOK.isEnabled() == False and self.cmdCancel.isEnabled() == False:
            return float(str(self.textbox.text()))


    def getUncheckedValueAsString(self):
        return str(self.textbox.text())
    

    def setValue(self, newValue):
        """Set the value of the widget"""
        self.textbox.setText(str(v))
        self.valueChanged()

        return self.cmdOK.isEnabled() == False and self.cmdCancel.isEnabled() == False
             

class TextEntryField(ProcedureEntryField):
    """Provide a simple text entry field"""
    def __init__(self, parent, caption = ''):
        """Constructor
        
        parent -- the parent QObject
        caption -- a caption string (default: no caption)"""
        ProcedureEntryField.__init__(self, parent, caption)
        
        box = QWidget(self)

        self.savedValue = None
        self.textbox = QLineEdit('', box)
        okCancelBox = QHBox(box)
        okCancelBox.setSpacing(0)
        okCancelBox.setMargin(0)
        self.cmdOK = QPushButton(okCancelBox)
        self.cmdOK.setFixedSize(20, 20)
        self.cmdCancel = QPushButton(okCancelBox)
        self.cmdCancel.setFixedSize(20, 20)
        self.cmdOK.setPixmap(Qt4_Icons.load('button_ok_small')) #QPixmap(Icons.okXPM))
        self.cmdCancel.setPixmap(Qt4_Icons.load('button_cancel_small')) #QPixmap(Icons.cancelXPM))
        
        QObject.connect(self.textbox, SIGNAL('textChanged( const QString & )'), self.valueChanging)
        QObject.connect(self.textbox, SIGNAL('returnPressed()'), self.valueChanged)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.valueChanged)
        QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.cancelClicked)

        self.cmdCancel.setEnabled(False)
        self.cmdOK.setEnabled(True)

        QHBoxLayout(box, 0, 5)
        box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        box.layout().addWidget(self.textbox, 0, Qt.AlignLeft)
        box.layout().addWidget(okCancelBox, 0, Qt.AlignLeft)
        box.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        

    def setIsOk(self, ok):
        self.setIsInvalid(False)
        
        if ok:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(False)
        else:
            self.cmdOK.setEnabled(True)
            self.cmdCancel.setEnabled(True)


    def setIsInvalid(self, invalid):
        if invalid:
            self.cmdOK.setEnabled(False)
            self.cmdCancel.setEnabled(True)
            self.setPaletteForegroundColor(QColor(255, 0, 0))
            self.textbox.selectAll()
        else:
            self.unsetPalette()

        self.textbox.setFocus()


    def validationPassed(self, reply = None):
        self.setIsOk(True)
        self.savedValue = self.textbox.text()
        
        ProcedureEntryField.validationPassed(self, reply)


    def validationFailed(self, reply = None):
        self.setIsInvalid(True)
        
        ProcedureEntryField.validationFailed(self, reply)


    def valueChanging(self):
        self.setIsOk(False)


    def valueChanged(self):
        ProcedureEntryField.valueChanged(self, str(self.textbox.text()))
                                         
        
    def cancelClicked(self):
        if self.savedValue is not None:
            self.textbox.setText(self.savedValue)
            self.valueChanged()
            
    
    def getValue(self):
        """Return the value of the widget"""
        if self.cmdOK.isEnabled() == False:
            return str(self.textbox.text())


    def getUncheckedValueAsString(self):
        return str(self.textbox.text())
    

    def setValue(self, newValue):
        """Set the value of the widget"""
        self.textbox.setText(str(v))
        self.valueChanged()

        return self.cmdOK.isEnabled() == False and self.cmdCancel.setEnabled() == False
    

class Label(QtGui.QGroupBox):
    def __init__(self, parent, caption, value = '-'):
        QtGui.QGroupBox.__init__(self, parent)

        self.setSpacing(5)
        self.setMargin(0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        QLabel('<nobr><i>%s</i></nobr>' % str(caption), self)

        self.value = str(value)
        self.label = QLabel(self)
        self.setValue(self.value)


    def setValue(self, value):
        self.value = str(value)
        self.label.setText(self.value)


    def getValue(self):
        return self.value


class MotorPositionReminder(QtGui.QTableWidgetItem):
    NOPOSITION = 13*'-'

    def __init__(self, parent):
        QtGui.QTableWidgetItem.__init__(self, parent, QtGui.QTableWidgetItem.Always, '')

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
            from BlissFramework.Bricks import MotorBrick
            self.controlDialog = MotorBrick.MotorControlDialog(self.cmdMotorPosition, '')
            QObject.connect(self.controlDialog, PYSIGNAL('motorControlDialogClosed'), self.controlDialogClosed)
            self.controlDialog.setMotorMnemonic(self.motor.name())
            self.controlDialog.exec_loop() #modal
        else:
            self.controlDialog.setActiveWindow()


    def controlDialogClosed(self, name):
        del self.controlDialog
        self.controlDialog = None
      

class ScanConfigurationTable(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent)

        self.motorsList = QStringList()
        self.motors = {}
        self.customColumns = {}

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLeftMargin(0) # no vertical header
        self.setNumCols(5)
        self.setNumRows(1)
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


    def getTableContents(self):
        contents = {}
        
        for col in range(self.numCols()):
            columnLabel = str(self.horizontalHeader().label(col))
            contents[columnLabel] = []
            
            for row in range(self.numRows()):
                contents[columnLabel].append(str(self.text(row, col)))

        return contents


    def addColumn(self, label, type, opt = ()):
        c = self.numCols()
        self.setNumCols(c + 1)

        self.horizontalHeader().setLabel(c, str(label))

        self.customColumns[c] = {'type':str(type), 'label':str(label), 'opt':opt}
        if self.customColumns[c]['type'] == 'combo':
            optList = QStringList()
            
            try:
                for opt in self.customColumns[c]['opt']:
                    optList.append(str(opt))
            except:
                pass
            
            for i in range(self.numRows()):
                self.setItem(i, c, QComboTableItem(self, optList))

        self.adjustColumn(c)
            

    def removeColumn(self, col):
        self.hideColumn(col)

    
    def addRows(self, rows = 1):
        row = self.numRows()

        QTable.setNumRows(self, row + rows)

        for i in range(rows):
            self.setItem(row + i, 0, QComboTableItem(self, self.motorsList))
            self.setItem(row + i, 1, MotorPositionReminder(self))

            for col in self.customColumns:
                if self.customColumns[col]['type'] == 'combo':
                    optList = QStringList()
            
                    try:
                        for opt in self.customColumns[col]['opt']:
                            optList.append(str(opt))
                    except:
                        pass
            
                    self.setItem(row + i, col, QComboTableItem(self, optList)) 

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
        self.motorsList = QStringList()
        self.motors = {}
        
        #self.motorsList.append('')
        #self.motors[''] = None
        
        for motor in motorSet:
            self.motors[motor[1]] = motor[0]
            self.motorsList.append(motor[1])

        self.motorsList.sort()
        
        for i in range(self.numRows()):
            self.setItem(i, 0, QComboTableItem(self, self.motorsList))
                                 
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
       
                
    def endEdit(self, row, col, accept, replace):
        if col == 2:
            # start pos.
            motor = self.motors[str(self.text(row, 0))]
            if motor is not None and motor.isReady():
                lowlimit, highlimit = motor.getLimits()
                try:
                    if float(self.text(row, col)) < lowlimit:
                        raise
                except:
                    QMessageBox.warning(None, 'Invalid value', 'Cannot set start pos. below low limit %f' % lowlimit, QMessageBox.Ok)
                    accept = False
        elif col == 3:
            # end pos.
            motor = self.motors[str(self.text(row, 0))]
            if motor is not None and motor.isReady():
                lowlimit, highlimit = motor.getLimits()
                try:
                    if float(self.text(row, col)) > highlimit:
                        raise
                except:
                    QMessageBox.warning(None, 'Invalid value', 'Cannot set end pos. beyond high limit %f' % highlimit, QMessageBox.Ok)
                    accept = False
        elif col in self.customColumns:
            value = str(self.text(row, col))
            type = self.customColumns[col]['type']

            if type == 'integer':
                try:
                    v = int(value)
                except:
                    QMessageBox.warning(None, 'Invalid value', '%s is not a valid integer value' % value, QMessageBox.Ok)
                    accept = False
            elif type == 'float':
                try:
                    v = float(value)
                except:
                    QMessageBox.warning(None, 'Invalid value', '%s is not a valid float value' % value, QMessageBox.Ok)
                    accept = False

        return QTable.endEdit(self, row, col, accept, replace)


class Table(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self, parent)

        self.customColumns = {}

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLeftMargin(0) # no vertical header
        QTable.setNumCols(self, 0)
        QTable.setNumRows(self, 0)
        self.setVScrollBarMode(QScrollView.AlwaysOff)
        
        self.horizontalHeader().setResizeEnabled(False)
        
    
    def sizeHint(self):
        return QSize(self.contentsWidth() +  self.leftMargin() + 2*self.frameWidth(), self.contentsHeight() + self.topMargin() + 2*self.frameWidth())


    def getTableContents(self):
        contents = {}
        
        for col in range(self.numCols()):
            columnLabel = str(self.horizontalHeader().label(col))
            contents[columnLabel] = []
            
            for row in range(self.numRows()):
                contents[columnLabel].append(str(self.text(row, col)))

        return contents
    

    def addColumn(self, label, type, opt = ()):
        c = self.numCols()
        self.setNumCols(c + 1)

        self.horizontalHeader().setLabel(c, str(label))
        
        self.customColumns[c] = {'type':str(type), 'label':str(label), 'opt':opt}
        if self.customColumns[c]['type'] == 'combo':
            optList = QStringList()
            
            try:
                for opt in self.customColumns[c]['opt']:
                    optList.append(str(opt))
            except:
                raise
            
            for i in range(self.numRows()):
                self.setItem(i, c, QComboTableItem(self, optList))
        
        self.adjustColumn(c)
        
    
    def addRows(self, rows = 1):
        row = self.numRows()

        QTable.setNumRows(self, row + rows)

        for i in range(rows):
            for col in self.customColumns:
                if self.customColumns[col]['type'] == 'combo':
                    optList = QStringList()
            
                    try:
                        for opt in self.customColumns[col]['opt']:
                            optList.append(str(opt))
                    except:
                        raise
            
                    self.setItem(row + i, col, QComboTableItem(self, optList)) 

                self.adjustColumn(col)
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
          
                
    def endEdit(self, row, col, accept, replace):
        if col in self.customColumns:
            value = str(self.text(row, col))
            type = self.customColumns[col]['type']

            if type == 'integer':
                try:
                    v = int(value)
                except:
                    QMessageBox.warning(None, 'Invalid value', '%s is not a valid integer value' % value, QMessageBox.Ok)
                    accept = False
            elif type == 'float':
                try:
                    v = float(value)
                except:
                    QMessageBox.warning(None, 'Invalid value', '%s is not a valid float value' % value, QMessageBox.Ok)
                    accept = False

        return QTable.endEdit(self, row, col, accept, replace)














