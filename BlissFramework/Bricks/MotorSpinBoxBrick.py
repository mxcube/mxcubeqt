from BlissFramework import BaseComponents
from BlissFramework import Icons
import math
from qt import *
import logging
from BlissFramework.Utils import widget_colors

'''
Motor control brick using a spin box (as an input field, and for the steps)
and buttons to move the motors (while pressed)
'''

__category__ = 'Motor'

class MotorSpinBoxBrick(BaseComponents.BlissWidget):

    STATE_COLORS = (widget_colors.LIGHT_RED, 
                    widget_colors.DARK_GRAY,
                    widget_colors.LIGHT_GREEN,
                    widget_colors.LIGHT_YELLOW,  
                    widget_colors.LIGHT_YELLOW,
                    widget_colors.LIGHT_YELLOW)

    MAX_HISTORY = 20

    def __init__(self,*args):
        BaseComponents.BlissWidget.__init__(self,*args)

        self.stepEditor=None
        self.motor=None
        self.demandMove=0

        self.inExpert=None

        self.addProperty('mnemonic','string','')
        self.addProperty('formatString','formatString','+##.##')
        self.addProperty('label','string','')
        self.addProperty('showLabel', 'boolean', True)
        self.addProperty('showMoveButtons', 'boolean', True)
        self.addProperty('showBox', 'boolean', True)
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('showStep', 'boolean', True)
        self.addProperty('showStepList', 'boolean', False)
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('invertButtons', 'boolean', False)
        self.addProperty('delta', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('helpDecrease', 'string', '')
        self.addProperty('helpIncrease', 'string', '')
        self.addProperty('decimalPlaces', 'string', '')
        self.addProperty('hideInUser', 'boolean', False)
        self.addProperty('defaultStep', 'string', '')

        self.containerBox=QHGroupBox(self)
        self.containerBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.labelBox=QHBox(self.containerBox)
        self.motorBox=QHBox(self.containerBox)

        self.label=QLabel(self.labelBox)
    
        self.moveLeftButton=QPushButton(self.motorBox)
        self.moveLeftButton.setPixmap(Icons.load('far_left'))
        self.moveRightButton=QPushButton(self.motorBox)
        self.moveRightButton.setPixmap(Icons.load('far_right'))
        QToolTip.add(self.moveLeftButton,"Moves the motor down (while pressed)")
        QToolTip.add(self.moveRightButton,"Moves the motor up (while pressed)")

        self.box=QHBox(self.motorBox)
        
        self.box.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        self.spinBox=mySpinBox(self.box)
        self.spinBox.setDecimalPlaces(4)
        self.spinBox.setMinValue(-10000)
        self.spinBox.setMaxValue(10000)
        self.spinBox.setMinimumSize(QSize(75,25))
        self.spinBox.setMaximumSize(QSize(75,25))
        self.spinBox.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        QToolTip.add(self.spinBox,"Moves the motor to a specific position or step by step; right-click for motor history")

        self.extraButtonsBox=QHBox(self.motorBox)
        self.extraButtonsBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.stopButton=QPushButton(self.extraButtonsBox)
        self.stopButton.setPixmap(Icons.load('stop_small'))
        self.stopButton.setEnabled(False)
        QToolTip.add(self.stopButton,"Stops the motor")
        self.stepButton=QPushButton(self.extraButtonsBox)
        self.stepButtonIcon=Icons.load('steps_small')
        self.stepButton.setPixmap(self.stepButtonIcon)
        QToolTip.add(self.stepButton,"Changes the motor step")

        self.stepList=myComboBox(self.extraButtonsBox)
        self.stepList.setValidator(QDoubleValidator(self))
        self.stepList.setDuplicatesEnabled(False)
        #self.stepList.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        pol=self.stepList.sizePolicy()
        pol.setVerData(QSizePolicy.MinimumExpanding)
        self.stepList.setSizePolicy(pol)
        QObject.connect(self.stepList,SIGNAL('activated(int)'),self.goToStep)

        self.moveLeftButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.moveRightButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.stopButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.stepButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
    
        self.connect(self.spinBox,PYSIGNAL('stepUp'),self.stepUp)
        self.connect(self.spinBox,PYSIGNAL('stepDown'),self.stepDown)
        self.connect(self.stopButton,SIGNAL('clicked()'),self.stopMotor)
        self.connect(self.stepButton,SIGNAL('clicked()'),self.openStepEditor)
        self.connect(self.spinBox,PYSIGNAL('contextMenu'),self.openHistoryMenu)
        self.connect(self.spinBox.editor(),SIGNAL('returnPressed()'),self.valueChangedStr)

        self.connect(self.moveLeftButton,SIGNAL('pressed()'),self.moveDown)
        self.connect(self.moveLeftButton,SIGNAL('released()'),self.stopMoving)
        self.connect(self.moveRightButton,SIGNAL('pressed()'),self.moveUp)
        self.connect(self.moveRightButton,SIGNAL('released()'),self.stopMoving)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.instanceSynchronize("spinBox","stepList")

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)
        
        self.defineSlot('setEnabled',())
        self.defineSlot('setDisabled',())
        self.defineSlot('toggle_enabled',())

    def setExpertMode(self,mode):
        self.inExpert=mode
        if self['hideInUser']:
            if mode:
                self.containerBox.show()
            else:
                self.containerBox.hide()

    def toggle_enabled(self):
        self.setEnabled(not self.isEnabled())

    def run(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def stop(self):
        self.containerBox.show()

    def getLineStep(self):
        return self.spinBox.lineStep()

    def setLineStep(self,val):
        self.spinBox.setLineStep(float(val))
        found=False
        for i in range(self.stepList.count()):
            if float(str(self.stepList.text(i)))==float(val):
                found=True
        if not found:
            self.stepList.insertItem(self.stepButtonIcon,str(val))
            self.stepList.setCurrentItem(self.stepList.count()-1)

    def goToStep(self,step_index):
        step=str(self.stepList.currentText())
        if step!="":
            self.stepList.changeItem(self.stepButtonIcon,step,step_index)
            self.stepList.setCurrentItem(step_index)
            self.setLineStep(step)

    def setStepButtonIcon(self,icon_name):
        self.stepButtonIcon=Icons.load(icon_name)
        self.stepButton.setPixmap(self.stepButtonIcon)
        for i in range(self.stepList.count()):
            txt=self.stepList.text(i)
            self.stepList.changeItem(self.stepButtonIcon,txt,i)

    # Stop the motor
    def stopMotor(self):
        self.motor.stop()

    def stopMoving(self):
        self.demandMove=0

    # Move motor to top limit
    def moveUp(self):
        self.demandMove=1
        self.updateGUI()
        state=self.motor.getState()
        if state==self.motor.READY:
            if self['invertButtons']:
                self.reallyMoveDown()
            else:
                self.reallyMoveUp()

    # Move motor to bottom limit
    def moveDown(self):
        self.demandMove=-1
        self.updateGUI()
        state=self.motor.getState()
        if state==self.motor.READY:
            if self['invertButtons']:
                self.reallyMoveUp()
            else:
                self.reallyMoveDown()

    def reallyMoveUp(self):
        if self['delta']!="":
            s=float(self['delta'])
        else:        
            try:
                s=self.motor.GUIstep
            except:
                s=1.0
        if self.motor is not None:
            if self.motor.isReady():
                self.motor.moveRelative(s)

    def reallyMoveDown(self):
        if self['delta']!="":
            s=float(self['delta'])
        else:
            try:
                s=self.motor.GUIstep
            except:
                s=1.0
        if self.motor is not None:
            if self.motor.isReady():
                self.setSpinBoxColor(self.motor.READY)
                self.motor.moveRelative(-s)

    # Force an update on the brick interface
    def updateGUI(self):
        if self.motor is not None: 
            self.containerBox.setEnabled(True)
            try:
                if self.motor.isReady():
                    self.limitsChanged(self.motor.getLimits())
                    self.positionChanged(self.motor.getPosition())
                self.stateChanged(self.motor.getState())
            except:
                if self.motor:
                   self.stateChanged(self.motor.UNUSABLE)
                else:
                   pass
        else:
            self.containerBox.setEnabled(False)

    # Set the limits for the spin box
    def limitsChanged(self,limits):
        self.spinBox.blockSignals(True)
        self.spinBox.setMinValue(limits[0])
        self.spinBox.setMaxValue(limits[1])
        self.spinBox.blockSignals(False)

        self.setToolTip(limits=limits)

    def openHistoryMenu(self):
        menu=QPopupMenu(self)
        menu.insertItem(QLabel('<nobr><b>%s history</b></nobr>' % self.motor.userName(), menu))
        menu.insertSeparator()
        for i in range(len(self.posHistory)):
            menu.insertItem(self.posHistory[i],i)
        menu.popup(QCursor.pos())
        QObject.connect(menu,SIGNAL('activated(int)'),self.goToHistoryPos)

    def goToHistoryPos(self,id):
        pos=self.posHistory[id]
        self.motor.move(float(pos))

    def updateHistory(self,pos):
        pos=str(pos)
        if pos not in self.posHistory:
            if len(self.posHistory)==MotorSpinBoxBrick.MAX_HISTORY:
                del self.posHistory[-1]
            self.posHistory.insert(0,pos)

    # Opens a dialog to change the motor step
    def openStepEditor(self):
        if self.isRunning():
            if self.stepEditor is None:
                self.stepEditor=StepEditorDialog(self)
                icons_list=self['icons'].split()
                try:
                    self.stepEditor.setIcons(icons_list[4],icons_list[5])
                except IndexError:
                    pass

            self.stepEditor.setMotor(self.motor,self,self['label'],self['defaultStep'])

            s=self.font().pointSize()
            f = self.stepEditor.font()
            f.setPointSize(s)
            self.stepEditor.setFont(f)
            self.stepEditor.updateGeometry()

            self.stepEditor.show()
            self.stepEditor.setActiveWindow()
            self.stepEditor.raiseW()

    # Updates the spin box when the motor moves
    def positionChanged(self,newPosition):  
        self.spinBox.setValue(float(newPosition))

    def setSpinBoxColor(self,state):
        color=MotorSpinBoxBrick.STATE_COLORS[state]
        self.spinBox.setEditorBackgroundColor(color)

    # Enables/disables the interface when the motor changes state
    def stateChanged(self,state):
        #if self.demandMove==0:
        self.setSpinBoxColor(state)

        if state==self.motor.MOVESTARTED:
            self.updateHistory(self.motor.getPosition())

        if state==self.motor.READY:
            if self.demandMove==1:
                if self['invertButtons']:
                    self.reallyMoveDown()
                else:
                    self.reallyMoveUp()
                return
            elif self.demandMove==-1:
                if self['invertButtons']:
                    self.reallyMoveUp()
                else:
                    self.reallyMoveDown()
                return

            self.spinBox.setMoving(False)
            self.stopButton.setEnabled(False)
            self.moveLeftButton.setEnabled(True)
            self.moveRightButton.setEnabled(True)
        elif state in (self.motor.NOTINITIALIZED, self.motor.UNUSABLE):
            self.spinBox.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.moveLeftButton.setEnabled(False)
            self.moveRightButton.setEnabled(False)
        elif state in (self.motor.MOVING, self.motor.MOVESTARTED):
            self.stopButton.setEnabled(True)
            self.spinBox.setMoving(True)
        elif state==self.motor.ONLIMIT:
            self.spinBox.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.moveLeftButton.setEnabled(True)
            self.moveRightButton.setEnabled(True)
        self.setToolTip(state=state)

    # Move the motor one step up
    def stepUp(self):
        if self.motor is not None:
            if self.motor.isReady():
                self.motor.moveRelative(self.spinBox.lineStep())

    # Move the motor one step down
    def stepDown(self):
        if self.motor is not None:
            if self.motor.isReady():
                self.motor.moveRelative(-self.spinBox.lineStep())

    # Moves the motor when the spin box text is changed
    def valueChangedInt(self,value):
        self.updateGUI()
        if self.motor is not None:
            self.motor.move(value)

    # Moves the motor when the spin box text is changed
    def valueChangedStr(self): #,value):
        if self.motor is not None:
            self.motor.move(float(str(self.spinBox.editor().text())))

    # Updates the tooltip in the correct widgets
    def setToolTip(self,name=None,state=None,limits=None):
        states=("NOTINITIALIZED","UNUSABLE","READY","MOVESTARTED","MOVING","ONLIMIT")
        if name is None:
            name=self['mnemonic']

        if self.motor is None:
            tip="Status: unknown motor "+name
        else:
            try:
                if state is None:
                    state=self.motor.getState()
            except:
                logging.exception("%s: could not get motor state", self.name())
                state=self.motor.UNUSABLE
                
            try:
                if limits is None and self.motor.isReady():
                    limits=self.motor.getLimits()
            except:
                logging.exception("%s: could not get motor limits", self.name())
                limits=None

            try:
                state_str=states[state]
            except IndexError:
                state_str="UNKNOWN"
                
            limits_str=""
            if limits is not None:
                l_bot=self['formatString'] % float(limits[0])
                l_top=self['formatString'] % float(limits[1])
                limits_str=" Limits:%s,%s" % (l_bot,l_top)
            tip="State:"+state_str+limits_str

        QToolTip.add(self.label,tip)
        if not self['showBox']:
            tip=""
        QToolTip.add(self.containerBox,tip)

    def setLabel(self,label):
        if not self['showLabel']:
            label=None

        if label is None:
            self.labelBox.hide()
            self.containerBox.setTitle("")
            return
    
        if label=="":
            if self.motor is not None:
                label=self.motor.username

        if self['showBox']:
            self.labelBox.hide()
            self.containerBox.setTitle(label)
        else:
            if label!="":
                label+=": "
            self.containerBox.setTitle("")
            self.label.setText(label)
            self.labelBox.show()

    def setMotor(self,motor,motor_ho_name=None):
        if self.motor is not None:
            self.disconnect(self.motor,PYSIGNAL('limitsChanged'),self.limitsChanged)
            self.disconnect(self.motor,PYSIGNAL('positionChanged'),self.positionChanged)
            self.disconnect(self.motor,PYSIGNAL('stateChanged'),self.stateChanged)

        if motor_ho_name is not None:
            motor=self.getHardwareObject(motor_ho_name)
        
        if self.motor is None:
          # first time motor is set
          try:
            s=float(self['defaultStep'])
          except:
            try:
                s=motor.GUIstep
            except:
                s=1.0
          self.setLineStep(s)

        self.motor = motor

        if self.motor is not None:
            self.connect(self.motor,PYSIGNAL('limitsChanged'),self.limitsChanged)
            self.connect(self.motor,PYSIGNAL('positionChanged'),self.positionChanged,instanceFilter=True)
            self.connect(self.motor,PYSIGNAL('stateChanged'),self.stateChanged,instanceFilter=True)

        self.posHistory=[]
        self.updateGUI()
        self['label']=self['label']
        #self['defaultStep']=self['defaultStep']

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            self.setMotor(self.motor,newValue)
        elif propertyName=='formatString':
            if self.motor is not None:
                self.updateGUI()
        elif propertyName=='label':
            self.setLabel(newValue)
        elif propertyName=='showLabel':
            if newValue:
                self.setLabel(self['label'])
            else:
                self.setLabel(None)
        elif propertyName=='showMoveButtons':
            if newValue:
                self.moveLeftButton.show()
                self.moveRightButton.show()
            else:            
                self.moveLeftButton.hide()
                self.moveRightButton.hide()
        elif propertyName=='showStop':
            if newValue:
                self.stopButton.show()
            else:
                self.stopButton.hide()
        elif propertyName=='showStep':
            if newValue:
                self.stepButton.show()
            else:
                self.stepButton.hide()
        elif propertyName=='showStepList':
            if newValue:
                self.stepList.show()
            else:
                self.stepList.hide()
        elif propertyName=='showPosition':
            if newValue:
                self.spinBox.show()
            else:
                self.spinBox.hide()
        elif propertyName=='showBox':
            if newValue:
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
                self.containerBox.setInsideSpacing(0)
            else:
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                self.containerBox.setInsideMargin(0)
                self.containerBox.setInsideSpacing(0)            
            self.setLabel(self['label'])
        elif propertyName=='icons':
            icons_list=newValue.split()
            try:
                self.moveLeftButton.setPixmap(Icons.load(icons_list[0]))
                self.moveRightButton.setPixmap(Icons.load(icons_list[1]))
                self.stopButton.setPixmap(Icons.load(icons_list[2]))
                self.setStepButtonIcon(icons_list[3])
            except IndexError:
                pass                
        elif propertyName=='helpDecrease':
            if newValue=="":
                QToolTip.add(self.moveLeftButton,"Moves the motor down (while pressed)")
            else:
                QToolTip.add(self.moveLeftButton,newValue)
        elif propertyName=='helpIncrease':
            if newValue=="":
                QToolTip.add(self.moveRightButton,"Moves the motor up (while pressed)")
            else:
                QToolTip.add(self.moveRightButton,newValue)
        elif propertyName=='decimalPlaces':
            try:
                dec_places=int(newValue)
            except ValueError:
                dec_places=2
            self.spinBox.setDecimalPlaces(dec_places)
        elif propertyName=='defaultStep':
            if newValue!="":
                self.setLineStep(float(newValue))
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

###
### Auxiliary class for a floating-point spinbox
###
class mySpinBox(QSpinBox):
    CHANGED_COLOR = QColor(255,165,0)
    def __init__(self,parent):    
        QSpinBox.__init__(self,parent)
        self.decimalPlaces=1
        self.__moving = False
        self.colorGroupDict={}
        self.setValidator(QDoubleValidator(self))
        self.editor().setAlignment(QWidget.AlignRight)
        QObject.connect(self.editor(),SIGNAL("textChanged(const QString &)"),self.textChanged)
        self.rangeChange()
        self.updateDisplay()
    def setMoving(self, moving):
        self.setEnabled(not moving)
        self.__moving = moving
    def textChanged(self):
        if self.__moving:
          return
        else:
          self.setEditorBackgroundColor(mySpinBox.CHANGED_COLOR)
    def i2d(self, v):
        return v/math.pow(10, self.decimalPlaces)
    def d2i(self, v):
        d=1 if v >= 0 else -1
        return int(d*0.5+math.pow(10, self.decimalPlaces)*v)
    def rangeChange(self):
        self.validator().setRange(self.minValue(), self.maxValue(), self.decimalPlaces)
        return QSpinBox.rangeChange(self)
    def setValue(self, value):
        if type(value)==type(0.0):
            return QSpinBox.setValue(self, self.d2i(value))
        else:
            return self.setValue(self.i2d(value)) 
    def value(self):
        return self.i2d(QSpinBox.value(self))
    def stepUp(self):
        self.emit(PYSIGNAL("stepUp"), ())
    def stepDown(self):
        self.emit(PYSIGNAL("stepDown"), ())
    def setDecimalPlaces(self,places):
        minval = self.minValue()
        maxval = self.maxValue()
        val = self.value()
        ls = self.lineStep()
        self.decimalPlaces=places
        self.setMaxValue(maxval)
        self.setMinValue(minval)
        self.setValue(val)
        self.setLineStep(ls)
        self.rangeChange()
        self.updateDisplay()
    def setMinValue(self, value):
        value = self.d2i(value) 
        if math.fabs(value) > 1E8:
          value = int(math.copysign(1E8, value))
        return QSpinBox.setMinValue(self, value)
    def setMaxValue(self, value):
        value = self.d2i(value) 
        if math.fabs(value) > 1E8:
          value = int(math.copysign(1E8, value))
        return QSpinBox.setMaxValue(self, value)
    def minValue(self):
        return self.i2d(QSpinBox.minValue(self))
    def maxValue(self):
        return self.i2d(QSpinBox.maxValue(self))
    def decimalPlaces(self):
        return self.decimalPlaces
    def mapValueToText(self,value):
        frmt="%."+"%df" % self.decimalPlaces
        return QString(frmt % self.i2d(value))
    def mapTextToValue(self):
        t = str(self.text())
        try:
          return (self.d2i(float(t)), True)
        except:
          return (0, False)
    def lineStep(self):
        return self.i2d(QSpinBox.lineStep(self))
    def setLineStep(self,step):
        return QSpinBox.setLineStep(self, self.d2i(step))
    def eventFilter(self,obj,ev):
        if isinstance(ev,QContextMenuEvent):
            self.emit(PYSIGNAL("contextMenu"),())
            return True
        else:
            return QSpinBox.eventFilter(self,obj,ev)
    def setEditorBackgroundColor(self,color):
        editor=self.editor()
        editor.setPaletteBackgroundColor(color)
        spinbox_palette=editor.palette()
        try:
            cg=self.colorGroupDict[color.rgb()]
        except KeyError:
            cg=QColorGroup(spinbox_palette.disabled())
            cg.setColor(cg.Background,color)
            self.colorGroupDict[color.rgb()]=cg
        spinbox_palette.setDisabled(cg)

###
### Dialog box to change the motor step
###
class StepEditorDialog(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent,'',False)

        self.contentsBox=QHGroupBox('Motor step',self)
        box2=QHBox(self)

        grid1=QWidget(self.contentsBox)
        QGridLayout(grid1, 2, 3, 0, 2)

        label1=QLabel("Current:",grid1)
        grid1.layout().addWidget(label1, 0, 0)
        self.currentStep=myLineEdit(grid1)
        grid1.layout().addMultiCellWidget(self.currentStep, 0, 0,1,2)
        
        label2=QLabel("Set to:",grid1)
        grid1.layout().addWidget(label2, 1, 0)
        self.newStep=QLineEdit(grid1)
        self.newStep.setAlignment(QWidget.AlignRight)
        self.newStep.setValidator(QDoubleValidator(self))
        QObject.connect(self.newStep,SIGNAL('returnPressed()'),self.applyClicked)
        grid1.layout().addWidget(self.newStep, 1, 1)
        self.applyButton=QPushButton("Apply",grid1)
        grid1.layout().addWidget(self.applyButton, 1, 2)
        QObject.connect(self.applyButton,SIGNAL('clicked()'),self.applyClicked)

        self.closeButton=QToolButton(box2)
        self.closeButton.setTextLabel("Dismiss")
        self.closeButton.setUsesTextLabel(True)
        self.closeButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.closeButton,SIGNAL("clicked()"),self.accept)
        HorizontalSpacer(box2)

        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(self.contentsBox)
        self.layout().addWidget(box2)

    def setMotor(self,motor,brick,name,default_step):
        self.motor=motor
        self.brick=brick

        if name is None or name=="":
            name=motor.userName()
        self.setCaption(name)
        self.contentsBox.setTitle('%s step' % name)

        self.currentStep.setText(str(brick.getLineStep()))

    def applyClicked(self):
        try:
            val=float(str(self.newStep.text()))
        except ValueError:
            return
        self.brick.setLineStep(val)
        self.newStep.setText('')
        self.currentStep.setText(str(val))

    def setIcons(self,apply_icon,dismiss_icon):
        self.applyButton.setPixmap(Icons.load(apply_icon))
        self.closeButton.setPixmap(Icons.load(dismiss_icon))

class myLineEdit(QLineEdit):
    def __init__(self,parent):
        QLineEdit.__init__(self,parent)
        palette=self.palette()
        self.disabledCG=QColorGroup(palette.disabled())
        self.disabledCG.setColor(QColorGroup.Text,QWidget.black)
        self.setEnabled(False)
        self.setAlignment(QWidget.AlignRight)
        palette.setDisabled(self.disabledCG)

class myComboBox(QComboBox):
    CHANGED_COLOR = QColor(255,165,0)
    
    def __init__(self,*args):
        QComboBox.__init__(self,*args)    
        self.setEditable(True)
        QObject.connect(self,SIGNAL('activated(int)'),self.stepChanged)
        QObject.connect(self,SIGNAL('textChanged(const QString &)'),self.stepEdited)

    def sizeHint(self):
        hint=QComboBox.sizeHint(self)
        hint.setWidth(1.10*hint.width())
        return hint

    def stepEdited(self,step):
        self.setEditorBackgroundColor(myComboBox.CHANGED_COLOR)

    def stepChanged(self,step):
        self.setEditorBackgroundColor(QWidget.white)

    def setEditorBackgroundColor(self,color):
        editor=self.lineEdit()
        editor.setPaletteBackgroundColor(color)
###
### Auxiliary class for positioning
###
class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
