"""Motor brick

The standard Motor brick.
"""
__category__ = 'Motor'

import logging

from qt import *
import Qwt5 as qwt

from BlissFramework import BaseComponents
from BlissFramework import Icons
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
from BlissFramework.Utils import widget_colors

class MotorControlDialog(QDialog):
    def __init__(self, parent, caption):
        QDialog.__init__(self, parent, '', False)
        
        QVBoxLayout(self)
        self.motorWidget = MotorBrick(self)
        buttonsBox=DialogButtonsBar(self,None,"Dismiss",None,self.closeClicked,DialogButtonsBar.DEFAULT_MARGIN,DialogButtonsBar.DEFAULT_SPACING)

        self.setCaption(caption)
        
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(self.motorWidget)
        self.layout().addWidget(buttonsBox)


    def setMotorMnemonic(self, mne):
        self.motorWidget.getProperty('allowConfigure').setValue(True)
        self.motorWidget.readProperties()
        self.motorWidget.setMnemonic(mne)


    def setMotorObject(self, obj):
        self.motorWidget.getProperty('allowConfigure').setValue(True)
        self.motorWidget.readProperties()
        self.motorWidget.setMotorObject(obj)

    def setPositionFormatString(self, format):
        self.motorWidget['formatString'] = format


    def closeClicked(self,action):
        self.accept()

        
    def run(self):
        self.motorWidget.run()



class stepEditor(QVBox):
    (LeftLayout, RightLayout) = (0, 1)

    def __init__(self, parent, layout, initialValue, title = '', prefix = ''):
        QVBox.__init__(self, parent)

        self.prefix = prefix
        self.value = initialValue
        
        self.lblTitle = QLabel(title, self)
        selectionBox = QHBox(self)
        self.editionBox = QHBox(selectionBox)

        if layout == stepEditor.RightLayout:
            self.cmdSelectValue = QPushButton(prefix + str(initialValue), selectionBox)
            self.cmdEditValue = QPushButton('...', selectionBox)
        else:
            self.cmdEditValue = QPushButton('...', selectionBox) 
            self.cmdSelectValue = QPushButton(prefix + str(initialValue), selectionBox)
        self.txtNewValue = QLineEdit(self.editionBox)
        self.cmdOK = QPushButton(self.editionBox)
        self.cmdCancel = QPushButton(self.editionBox)
            
        self.cmdCancel.setPixmap(Icons.load('button_cancel_small')) #QPixmap(Icons.tinyCancel))
        self.cmdOK.setPixmap(Icons.load('button_ok_small')) #Icons.tinyOK))
        self.editionBox.hide()
        self.lblTitle.hide()
        self.setFocusProxy(self.txtNewValue)
        self.txtNewValue.setFixedWidth(self.fontMetrics().width(' 888.888 '))
        self.cmdEditValue.setFixedWidth(self.fontMetrics().width(' ... '))
        self.cmdSelectValue.setFixedWidth(self.fontMetrics().width(prefix + ' 888.888 '))
        self.cmdSelectValue.setAutoDefault(False)
        self.cmdOK.setFixedWidth(20)
        self.cmdCancel.setFixedWidth(20)
        self.editionBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.connect(self.cmdSelectValue, SIGNAL('clicked()'), self.cmdSelectValueClicked)
        self.connect(self.cmdEditValue, SIGNAL('clicked()'), self.cmdEditValueClicked)
        self.connect(self.txtNewValue, SIGNAL('returnPressed()'), self.validateNewValue)
        self.connect(self.cmdOK, SIGNAL('clicked()'), self.validateNewValue)
        self.connect(self.cmdCancel, SIGNAL('clicked()'), self.endEdit)
        

    def setTitle(self, title):
        self.lblTitle.setText(title)


    def setPrefix(self, prefix):
        self.prefix = prefix
        self.cmdSelectValue.setText(self.prefix + str(self.value))


    def setValue(self, value):
        self.value = value
        self.cmdSelectValue.setText(self.prefix + str(self.value))
      

    def allowChangeValue(self, allow):
        if allow:
            self.cmdEditValue.show()
        else:
            self.cmdEditValue.hide()

            
    def cmdSelectValueClicked(self):
        self.emit(PYSIGNAL('clicked'), (self.value, ))


    def cmdEditValueClicked(self):
        self.cmdEditValue.hide()
        self.cmdSelectValue.hide()
        self.editionBox.show()
        self.lblTitle.show()
        self.txtNewValue.setText(str(self.value))
        self.txtNewValue.selectAll()
        self.txtNewValue.setFocus()
        

    def endEdit(self):
        self.cmdEditValue.show()
        self.cmdSelectValue.show()
        self.lblTitle.hide()
        self.editionBox.hide()
        self.emit(PYSIGNAL('valueChanged'), (self.value, ))


    def validateNewValue(self):
        try:
            self.value = float(str(self.txtNewValue.text()))
        except:
            logging.getLogger().error("%s is not a valid float value" % str(self.txtNewValue.text()))
        else:
            self.cmdSelectValue.setText(self.prefix + str(self.value))
            self.endEdit()


class MotorSlider(qwt.QwtSlider):
    def __init__(self, parent):
        qwt.QwtSlider.__init__(self, parent)
        self.setReadOnly(True)
        self.setBgStyle(qwt.QwtSlider.BgSlot)
        
        self.tickHeight = 3
        
        self.lblPosition = QLabel('', self)
        self.lblPosition.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.lblPosition.setLineWidth(1)
        self.lblPosition.setMidLineWidth(0)
        self.lblPosition.setAlignment(Qt.AlignCenter)
        self.positionFormatString = '%+8.4f'
      

    def minimumSizeHint(self):
        w = qwt.QwtSlider.minimumSizeHint(self).width()
        th = self.fontMetrics().height()
        h = self.thumbWidth() + th + (2 * self.tickHeight)
        return QSize(w, h)


    def setPositionFormatString(self, format):
        self.positionFormatString = format
        self.repaint()
        
        
    def setValue(self, value):
        if value is None:
            self.repaint()
        else:
            qwt.QwtSlider.setValue(self, value)
        

    def paintEvent(self, paintEvent):
        p = QPainter(self)

        th = p.fontMetrics().height() 
        self.setThumbWidth(th)
                
        #
        # erase previous
        #
        p.fillRect(0, 0, self.width(), self.height(), QBrush(self.colorGroup().background()))
        
        #
        # draw limits
        #
        
        minValueText = self.positionFormatString % self.minValue()
        maxValueText = self.positionFormatString % self.maxValue()
        llw = p.fontMetrics().width(minValueText)
        hlw = p.fontMetrics().width(maxValueText)
        xmargin = max(llw, hlw) / 2
        self.setMargins(xmargin, 0)
        
        p.drawText(QRect(xmargin, 0, llw, th), Qt.AlignAuto | Qt.SingleLine, minValueText)
        p.drawText(QRect(self.width() - xmargin - hlw , 0, hlw, th), Qt.AlignAuto | Qt.SingleLine, maxValueText)

        #
        # draw ticks for current slider position
        #
        sliderRect = QRect(xmargin, th + self.tickHeight, self.width() - (2*xmargin), self.thumbWidth())
        p.setPen(QPen(self.colorGroup().text()))
        x = self.xyPosition(self.value())
        p.drawLine(x, sliderRect.y() - self.tickHeight, x, self.height())
        
        #
        # draw slider
        #
        qwt.QwtSlider.drawSlider(self, p, sliderRect)

        #
        # move text label
        #
        positionText = self.positionFormatString % self.value()
        self.lblPosition.setText(positionText)
        x = self.xyPosition(self.value())
        w = max(p.fontMetrics().width(positionText), self.thumbLength())
        self.lblPosition.setFixedSize(w + 2*(self.lblPosition.lineWidth() + self.lblPosition.midLineWidth()), p.fontMetrics().height())
        self.lblPosition.move(x - (self.lblPosition.width() / 2), sliderRect.y())
        

class MoveBox(QWidget):
    """Helper class"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.oldPositions = [] #history of motor positions

        lblMove = QLabel('go to ', self)
        self.txtMove = QLineEdit('', self)
        self.cmdMove = QPushButton('', self)
        self.cmdGoBack = QPushButton('', self)
        self.cmdStop = QPushButton('', self)

        self.txtMove.setFixedWidth(self.txtMove.fontMetrics().width('8888.8888'))
        self.cmdMove.setToggleButton(True)
        self.cmdStop.setPixmap(Icons.load('stop_small')) #QPixmap(Icons.stopXPM_small))
        self.cmdStop.setEnabled(False)
        self.cmdGoBack.setPixmap(Icons.load('goback_small')) #QPixmap(Icons.gobackXPM_small))
        self.cmdMove.setPixmap(Icons.load('move_small')) #QPixmap(Icons.moveXPM_small))
        self.cmdGoBack.setEnabled(False)

        self.connect(self.cmdMove, SIGNAL('clicked()'), self.cmdMoveClicked)
        self.connect(self.cmdStop, SIGNAL('clicked()'), PYSIGNAL('stopMotor'))
        self.connect(self.txtMove, SIGNAL('returnPressed()'), self.txtMoveReturnPressed)
        self.connect(self.txtMove, SIGNAL('textChanged(const QString &)'), self.txtMoveTextChanged)
        self.connect(self.cmdGoBack, SIGNAL('clicked()'), self.cmdGoBackClicked)
    
        QHBoxLayout(self)
        self.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.layout().addWidget(lblMove)
        self.layout().addWidget(self.txtMove)
        self.layout().addWidget(self.cmdMove)
        self.layout().addWidget(self.cmdGoBack)
        self.layout().addWidget(self.cmdStop)
        self.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))


    def cmdMoveClicked(self):
        self.txtMoveReturnPressed()

        
    def setOldPosition(self, position):
        position = str(position)
        
        if len(self.oldPositions) == 20:
            del self.oldPositions[-1]

        if position in self.oldPositions:
            return
            
        self.oldPositions.insert(0, position)
  

    def txtMoveReturnPressed(self):
        try:
            movePosition = float(str(self.txtMove.text()))
        except:
            self.cmdMove.setOn(False)
        else:
            self.emit(PYSIGNAL('moveMotor'), (movePosition, ))


    def txtMoveTextChanged(self, text):
        if len(text) > 0 and not self.cmdMove.isOn():
            self.cmdMove.setEnabled(True)
        else:
            self.cmdMove.setEnabled(False)


    def cmdGoBackClicked(self):
        #show popup menu with all recorded previous positions
        oldPositionsMenu = QPopupMenu(self)
        oldPositionsMenu.insertItem(QLabel('<nobr><b>Last positions :</b></nobr>', oldPositionsMenu))
        oldPositionsMenu.insertSeparator()
        for i in range(len(self.oldPositions)):
            oldPositionsMenu.insertItem(self.oldPositions[i], i)
        QObject.connect(oldPositionsMenu, SIGNAL('activated(int)'), self.goToOldPosition)
        oldPositionsMenu.exec_loop(QCursor.pos())


    def goToOldPosition(self, id):
        pos = self.oldPositions[id]

        self.txtMove.setText(pos)
        self.txtMoveReturnPressed()
        

    def setIsMoving(self, moving):
        if moving:
            self.txtMove.setText('')
            self.cmdMove.setOn(True)
            self.cmdMove.setEnabled(False)
            self.cmdGoBack.setEnabled(False)
            self.cmdStop.setEnabled(True)
        else:
            self.cmdMove.setOn(False)
            if len(self.txtMove.text()) > 0:
                self.cmdMove.setEnabled(True)
            else:
                self.cmdMove.setEnabled(False)
            if len(self.oldPositions) > 0:
                self.cmdGoBack.setEnabled(True)
            self.cmdStop.setEnabled(False)

      
class MotorBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.motor = None # hardware object
        self.controlDialog = None

        #
        # create GUI elements
        #
        self.frame = QVGroupBox(self)
        self.bottomPanel = QHBox(self.frame)
        self.stepBackward = stepEditor(self.bottomPanel, stepEditor.LeftLayout, 1, 'new step:', '-')
        self.moveBox = MoveBox(self.frame)
        self.slider = MotorSlider(self.bottomPanel)
        self.stepForward = stepEditor(self.bottomPanel, stepEditor.RightLayout, 1, 'new step:', '+')
        self.lblMotorPosition = self.slider.lblPosition
        self.namePositionBox = QFrame(self)
        self.lblMotorName = QLabel(self.namePositionBox)
        self.lblPosition = QLabel(self.namePositionBox)
             
        #
        # configure elements
        #
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.frame.setInsideMargin(5)
        self.frame.setInsideSpacing(5)
        self.stepBackward.allowChangeValue(False)
        self.bottomPanel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.namePositionBox.hide()
        self.namePositionBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.namePositionBox.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.namePositionBox.setLineWidth(1)
        self.namePositionBox.setMidLineWidth(0)
        self.lblMotorName.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lblPosition.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
        #
        # connect signals and slots
        #
        self.connect(self.moveBox, PYSIGNAL('moveMotor'), self.moveMotor)
        self.connect(self.moveBox, PYSIGNAL('stopMotor'), self.stopMotor)
        self.connect(self.stepForward, PYSIGNAL('clicked'), self.stepForwardClicked)
        self.connect(self.stepForward, PYSIGNAL('valueChanged'), self.stepForwardValueChanged)
        self.connect(self.stepBackward, PYSIGNAL('clicked'), self.stepBackwardClicked)

        #
        # layout
        #
        QHBoxLayout(self.namePositionBox, 1, 0)
        self.namePositionBox.layout().addWidget(self.lblMotorName)
        self.namePositionBox.layout().addWidget(self.lblPosition)
        
        QVBoxLayout(self, 5, 5) #GridLayout(self, 2, 1, 5, 5)
        self.layout().addWidget(self.namePositionBox, 0, Qt.AlignTop)
        self.layout().addWidget(self.frame, 0, Qt.AlignCenter)
       
        #
        # define properties, signals and slots
        #
        self.addProperty('appearance', 'combo', ('tiny', 'normal'), 'normal')
        self.addProperty('allowConfigure', 'boolean', True)
        self.addProperty('mnemonic', 'string', '')        
        self.addProperty('allowDoubleClick', 'boolean', False)
        self.addProperty('formatString', 'formatString', '+##.####') #%+8.4f
        self.addProperty('dialogCaption', 'string', '', hidden=True)
        

    def slotPosition(self, newPosition):
        #print "MotorBrick.slotPosition",newPosition
        #uname = self.motor.userName().ljust(6).replace(' ', '&nbsp;')

        if newPosition is None:
            pos = self.getProperty('formatString').getUserValue()
        else:           
            pos = self['formatString'] % newPosition
            #pos.replace(' ', '&nbsp;')
            
        self.slider.setValue(newPosition)
        self.lblPosition.setText('<nobr><font face="courier">%s</font></nobr>' % pos)
 

    def slotStatus(self, state):
        state = state - 1
        color = [self.colorGroup().background(), widget_colors.LIGHT_GREEN,
                 Qt.yellow, Qt.yellow, widget_colors.LIGHT_RED, self.colorGroup().background()]
        self.lblMotorName.setPaletteBackgroundColor(color[state])
        self.lblPosition.setPaletteBackgroundColor(color[state])
        self.lblMotorPosition.setPaletteBackgroundColor(color[state])

        if state == 2: #start moving
            self.moveBox.setOldPosition(self.motor.getPosition())
        elif state == 3: #moving
            self.stepForward.setEnabled(False)
            self.stepBackward.setEnabled(False)
            self.moveBox.setIsMoving(True)
        else:
            self.stepForward.setEnabled(True)
            self.stepBackward.setEnabled(True)
            self.moveBox.setIsMoving(False)    

               
    def limitChanged(self, limits):
        self.slider.setRange(limits[0], limits[1])


    def moveMotor(self, movePosition):
        self.motor.move(movePosition)
        

    def stopMotor(self):
        self.motor.stop()
        

    def cmdConfigureClicked(self):
        configureDialog = ConfigureDialog(self, self.motor)
        configureDialog.exec_loop()
        

    def stepForwardClicked(self, value):
        currentPosition = self.motor.getPosition()
        self.moveMotor(currentPosition + value) 
        

    def stepForwardValueChanged(self, value):
        self.stepBackward.setValue(value)
        self.motor.GUIstep = value
                

    def stepBackwardClicked(self, value):
        currentPosition = self.motor.getPosition()
        self.moveMotor(currentPosition - value)
               

    def motorReady(self):
        self.setEnabled(True)
        

    def motorNotReady(self):
        self.setEnabled(False)
            

    def stop(self):
        if self.controlDialog is not None:
            self.controlDialog.hide()
       
               
    def setMnemonic(self, mne):
        self['mnemonic'] = mne


    def setMotorObject(self, obj):
        if self.motor is not None:
            self.disconnect(self.motor, PYSIGNAL('deviceReady'), self.motorReady)
            self.disconnect(self.motor, PYSIGNAL('deviceNotReady'), self.motorNotReady)
            self.disconnect(self.motor, PYSIGNAL('positionChanged'), self.slotPosition)
            self.disconnect(self.motor, PYSIGNAL('stateChanged'), self.slotStatus)
            self.disconnect(self.motor, PYSIGNAL('limitsChanged'), self.limitChanged)
            if self.controlDialog is not None:
                self.controlDialog.close(True)
                self.controlDialog = None
        
        self.motor = obj

        if self.motor is not None:
            self.setEnabled(True)
            
            self.connect(self.motor, PYSIGNAL('deviceReady'), self.motorReady)
            self.connect(self.motor, PYSIGNAL('deviceNotReady'), self.motorNotReady)
            self.connect(self.motor, PYSIGNAL('positionChanged'), self.slotPosition)
            self.connect(self.motor, PYSIGNAL('stateChanged'), self.slotStatus)
            self.connect(self.motor, PYSIGNAL('limitsChanged'), self.limitChanged)

            self.frame.setTitle(self.motor.userName() + ' :')
            self.lblMotorName.setText('<nobr><font face="courier"><b>%s</b></font></nobr>' % self.motor.userName())
            
            try:
                s = self.motor.GUIstep
            except:
                s = 1

            self.stepBackward.setValue(s)
            self.stepForward.setValue(s)
        
            if self.motor.isReady():
                self.limitChanged(self.motor.getLimits())
                self.slotPosition(self.motor.getPosition())
                self.slotStatus(self.motor.getState())
                self.motorReady()
            else:
                self.motorNotReady()


    def mouseDoubleClickEvent(self, mouseEvent):
        if self.isRunning() and self.propertyBag['allowDoubleClick'] and self.propertyBag['appearance'] == 'tiny':
            #
            # show full motor control in another window
            #
            if self.controlDialog is None:
                self.controlDialog = MotorControlDialog(self, self['dialogCaption'] or self.motor.userName())
                self.controlDialog.setMotorMnemonic(self['mnemonic'])

            self.controlDialog.setPositionFormatString(self['formatString'])
            self.controlDialog.show()
            self.controlDialog.setActiveWindow()
            self.controlDialog.raiseW()

        
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'appearance':
            if newValue == 'tiny':
                self.layout().setMargin(0)
                self.layout().setSpacing(0)
                self.frame.hide()
                self.namePositionBox.show()
                self.updateGeometry()
            elif newValue == 'normal':
                self.bottomPanel.show()
                self.layout().setMargin(5)
                self.layout().setSpacing(5)
                self.frame.show()
                self.namePositionBox.hide()
                self.updateGeometry()
        elif propertyName == 'formatString':
            self.slider.setPositionFormatString(self['formatString'])

            if self.motor is not None and self.motor.isReady():
                self.slotPosition(self.motor.getPosition())
                return
            
            self.slotPosition(None)
        elif propertyName == 'allowConfigure':
            pass
        elif propertyName == 'allowDoubleClick':
            pass
        elif propertyName == 'mnemonic':
            if self.motor is not None:
                self.disconnect(self.motor, PYSIGNAL('deviceReady'), self.motorReady)
                self.disconnect(self.motor, PYSIGNAL('deviceNotReady'), self.motorNotReady)
                self.disconnect(self.motor, PYSIGNAL('positionChanged'), self.slotPosition)
                self.disconnect(self.motor, PYSIGNAL('stateChanged'), self.slotStatus)
                self.disconnect(self.motor, PYSIGNAL('limitsChanged'), self.limitChanged)
                if self.controlDialog is not None:
                    self.controlDialog.close(True)
                    self.controlDialog = None
        
            self.motor = self.getHardwareObject(newValue)

            if self.motor is not None:
                self.setEnabled(True)
            
                self.connect(self.motor, PYSIGNAL('deviceReady'), self.motorReady)
                self.connect(self.motor, PYSIGNAL('deviceNotReady'), self.motorNotReady)
                self.connect(self.motor, PYSIGNAL('positionChanged'), self.slotPosition)
                self.connect(self.motor, PYSIGNAL('stateChanged'), self.slotStatus)
                self.connect(self.motor, PYSIGNAL('limitsChanged'), self.limitChanged)

                self.frame.setTitle(self.motor.userName() + ' :')
                self.lblMotorName.setText('<nobr><font face="courier"><b>%s</b></font></nobr>' % self.motor.userName())
            
                try:
                    s = self.motor.GUIstep
                except:
                    s = 1

                self.stepBackward.setValue(s)
                self.stepForward.setValue(s)
        
                if self.motor.isReady():
                    self.limitChanged(self.motor.getLimits())
                    self.slotPosition(self.motor.getPosition())
                    self.slotStatus(self.motor.getState())
                    self.motorReady()
                else:
                    self.motorNotReady()
            else:
                self.frame.setTitle('motor :')
                self.lblMotorName.setText('<nobr><font face="courier"><b>-</b></font></nobr>')
                self.stepBackward.setValue(1)
                self.stepForward.setValue(1)
                self.setEnabled(False)
