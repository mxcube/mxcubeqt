import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Bricks import MotorSpinBoxBrick
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar

__category__ = 'mxCuBE'

class SlitsBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.inExpert=None
        self.slitbox=None
        self.minidiff=None

        self.motorsDialog=MotorsDialog(self)

        self.addProperty('slitbox', 'string', '')
        self.addProperty('minidiff', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('motorIcons', 'string', '')
        self.addProperty('title', 'string', 'Beam size')
        self.addProperty('formatString','formatString','##.####')
        self.addProperty('decimalPlaces', 'string', '4')
        self.addProperty('expertOnly', 'boolean', False)

        self.topBox = QHGroupBox('Beam size',self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.beamHorSize=MotorSpinBoxBrick.MotorSpinBoxBrick(self.topBox)
        self.beamHorSize['showMoveButtons']=False
        self.beamHorSize['showBox']=False
        self.beamHorSize['showLabel']=True
        self.beamHorSize['label']="Hor"
        self.beamHorSize['showStep']=False
        self.beamHorSize['showStepList']=True
        
        self.beamVerSize=MotorSpinBoxBrick.MotorSpinBoxBrick(self.topBox)
        self.beamVerSize['showMoveButtons']=False
        self.beamVerSize['showBox']=False
        self.beamVerSize['showLabel']=True
        self.beamVerSize['label']="Ver"
        self.beamVerSize['showStep']=False
        self.beamVerSize['showStepList']=True

        self.topBox.addSpace(10)
        self.offsetsLabel=QLabel("Move:",self.topBox)
        self.offsetsButton=QToolButton(self.topBox)
        self.offsetsButton.setTextLabel("Offsets")
        self.offsetsButton.setUsesTextLabel(True)
        self.offsetsButton.setTextPosition(QToolButton.BesideIcon)
        QObject.connect(self.offsetsButton, SIGNAL('clicked()'), self.openOffsetsDialog)

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.motorsDialog.reject()

    def openOffsetsDialog(self):
        s=self.font().pointSize()
        f=self.motorsDialog.font()
        f.setPointSize(s)
        self.motorsDialog.setFont(f)
        self.motorsDialog.updateGeometry()
        self.motorsDialog.show()
        self.motorsDialog.setActiveWindow()
        self.motorsDialog.raiseW()

    def run(self):
        if self.slitbox is None:
            self.topBox.hide()
        elif self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def stop(self):
        self.topBox.show()

    def setIcons(self,icons):
        icons_list=icons.split()
        try:
            self.offsetsButton.setPixmap(Icons.load(icons_list[0]))
        except IndexError:
            pass

    def setExpertMode(self,state):
          if not self["expertOnly"]:
            return
          self.inExpert=state
          self.offsetsLabel.setEnabled(state)
          self.offsetsButton.setEnabled(state)
          self.motorsDialog.setEnabled(state)
          self.beamHorSize.setEnabled(state)
          self.beamVerSize.setEnabled(state)
          self.topBox.setEnabled(state)

    def propertyChanged(self, property, oldValue, newValue):
        #print "SlitsBrick.propertyChanged",property,newValue
        if property == 'slitbox':
            self.slitbox=self.getHardwareObject(newValue)
            if self.slitbox is not None:
                s1v = self.slitbox.getDeviceByRole('s1v')
                s1h = self.slitbox.getDeviceByRole('s1h')
            else:
                s1v = None
                s1h = None
            self.beamHorSize.setMotor(s1h)
            self.beamVerSize.setMotor(s1v)
            self.motorsDialog.setSlitbox(self.slitbox)
        elif property == 'minidiff':
            if self.minidiff is not None:
                pass
            self.minidiff=self.getHardwareObject(newValue)
            if self.minidiff is not None:
                pass
        elif property == 'icons':
            self.setIcons(newValue)
        elif property == 'title':
            self.topBox.setTitle(newValue)
        elif property == 'motorIcons':
            self.beamHorSize['icons']=newValue
            self.beamVerSize['icons']=newValue
            self.motorsDialog.setMotorIcons(newValue)
        elif property == 'formatString':
            self.beamHorSize['formatString']=newValue
            self.beamVerSize['formatString']=newValue
        elif property == 'decimalPlaces':
            self.beamHorSize['decimalPlaces']=newValue
            self.beamVerSize['decimalPlaces']=newValue
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

class MotorsDialog(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent,'',False)
        self.setCaption('Beam size')
        
        self.motorsBox = QWidget(self)
        QGridLayout(self.motorsBox, 2, 2, 6, 6)

        self.slit1OffBox = QVGroupBox('Slit 1 offsets', self.motorsBox)
        self.motorsBox.layout().addWidget(self.slit1OffBox, 0, 0)
        self.t1hMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit1OffBox)
        self.t1hMotor['showMoveButtons']=False
        self.t1hMotor['showBox']=False
        self.t1hMotor['showLabel']=True
        self.t1hMotor['label']="t1h"
        self.t1hMotor['showStep']=False
        self.t1hMotor['showStepList']=True
        self.t1vMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit1OffBox)
        self.t1vMotor['showMoveButtons']=False
        self.t1vMotor['showBox']=False
        self.t1vMotor['showLabel']=True
        self.t1vMotor['label']="t1v"
        self.t1vMotor['showStep']=False
        self.t1vMotor['showStepList']=True

        self.slit1GapBox = QVGroupBox('Slit 1 gaps', self.motorsBox)
        self.motorsBox.layout().addWidget(self.slit1GapBox, 0, 1)
        self.s1hMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit1GapBox)
        self.s1hMotor['showMoveButtons']=False
        self.s1hMotor['showBox']=False
        self.s1hMotor['showLabel']=True
        self.s1hMotor['label']="s1h"
        self.s1hMotor['showStep']=False
        self.s1hMotor['showStepList']=True
        self.s1vMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit1GapBox)
        self.s1vMotor['showMoveButtons']=False
        self.s1vMotor['showBox']=False
        self.s1vMotor['showLabel']=True
        self.s1vMotor['label']="s1v"
        self.s1vMotor['showStep']=False
        self.s1vMotor['showStepList']=True

        self.slit2OffBox = QVGroupBox('Slit 2 offsets', self.motorsBox)
        self.motorsBox.layout().addWidget(self.slit2OffBox, 1, 0)
        self.t2hMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit2OffBox)
        self.t2hMotor['showMoveButtons']=False
        self.t2hMotor['showBox']=False
        self.t2hMotor['showLabel']=True
        self.t2hMotor['label']="t2h"
        self.t2hMotor['showStep']=False
        self.t2hMotor['showStepList']=True
        self.t2vMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit2OffBox)
        self.t2vMotor['showMoveButtons']=False
        self.t2vMotor['showBox']=False
        self.t2vMotor['showLabel']=True
        self.t2vMotor['label']="t2v"
        self.t2vMotor['showStep']=False
        self.t2vMotor['showStepList']=True

        self.slit2GapBox = QVGroupBox('Slit 2 gaps', self.motorsBox)
        self.motorsBox.layout().addWidget(self.slit2GapBox, 1, 1)
        self.s2hMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit2GapBox)
        self.s2hMotor['showMoveButtons']=False
        self.s2hMotor['showBox']=False
        self.s2hMotor['showLabel']=True
        self.s2hMotor['label']="s2h"
        self.s2hMotor['showStep']=False
        self.s2hMotor['showStepList']=True
        self.s2vMotor=MotorSpinBoxBrick.MotorSpinBoxBrick(self.slit2GapBox)
        self.s2vMotor['showMoveButtons']=False
        self.s2vMotor['showBox']=False
        self.s2vMotor['showLabel']=True
        self.s2vMotor['label']="s2v"
        self.s2vMotor['showStep']=False
        self.s2vMotor['showStepList']=True

        buttonsBox=DialogButtonsBar(self,"Dismiss",None,None,self.buttonClicked,DialogButtonsBar.DEFAULT_MARGIN,DialogButtonsBar.DEFAULT_SPACING)

        QVBoxLayout(self)        
        self.layout().addWidget(self.motorsBox)
        self.layout().addWidget(VerticalSpacer2(self))
        self.layout().addWidget(buttonsBox)

    def buttonClicked(self,action):
        self.accept()

    def setMotorIcons(self,icons):
        self.t1hMotor['icons']=icons
        self.t1vMotor['icons']=icons
        self.s1hMotor['icons']=icons
        self.s1vMotor['icons']=icons
        self.t2hMotor['icons']=icons
        self.t2vMotor['icons']=icons
        self.s2hMotor['icons']=icons
        self.s2vMotor['icons']=icons

    def setSlitbox(self,slitbox):
        if slitbox is not None:
            t1h = slitbox.getDeviceByRole('t1h')
            t1v = slitbox.getDeviceByRole('t1v')
            s1h = slitbox.getDeviceByRole('s1h')
            s1v = slitbox.getDeviceByRole('s1v')
            t2h = slitbox.getDeviceByRole('t2h')
            t2v = slitbox.getDeviceByRole('t2v')
            s2h = slitbox.getDeviceByRole('s2h')
            s2v = slitbox.getDeviceByRole('s2v')
        else:
            t1h = None
            t1v = None
            s1h = None
            s1v = None
            t2h = None
            t2v = None
            s2h = None
            s2v = None

        self.t1hMotor.setMotor(t1h)
        self.t1vMotor.setMotor(t1v)
        self.s1hMotor.setMotor(s1h)
        self.s1vMotor.setMotor(s1v)
        self.t2hMotor.setMotor(t2h)
        self.t2vMotor.setMotor(t2v)
        self.s2hMotor.setMotor(s2h)
        self.s2vMotor.setMotor(s2v)

class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

class VerticalSpacer2(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
