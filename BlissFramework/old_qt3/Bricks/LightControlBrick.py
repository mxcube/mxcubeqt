from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Bricks import MotorSpinBoxBrick
from BlissFramework import Icons
import logging

'''
Controls both the light on/off (wago) and intensity (motor)
'''
__category__ = 'blcomp'

class LightControlBrick(MotorSpinBoxBrick.MotorSpinBoxBrick):
    def __init__(self, *args):
        MotorSpinBoxBrick.MotorSpinBoxBrick.__init__(self, *args)
        self.wagoLight =None
        self.lightSavedPosition=None

        self.addProperty('wagolight', 'string', '')
        self.addProperty('wagoicons', 'string', '')
        self.addProperty('out_delta', 'string', '')

        self.lightOffButton=QPushButton("0",self.extraButtonsBox)
        self.lightOffButton.setPixmap(Icons.load('far_left'))
        self.connect(self.lightOffButton,SIGNAL('clicked()'),self.lightButtonOffClicked)
        self.lightOnButton=QPushButton("1",self.extraButtonsBox)
        self.lightOnButton.setPixmap(Icons.load('far_right'))
        self.connect(self.lightOnButton,SIGNAL('clicked()'),self.lightButtonOnClicked)

        self.spinBox.close()
        self.stepButton.close()
        self.stopButton.close()

        QToolTip.add(self.lightOffButton,"Switches off the light and sets the intensity to zero")
        QToolTip.add(self.lightOnButton,"Switches on the light and sets the intensity back to the previous setting")        

        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lightOffButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.lightOnButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        #self.defineSlot('wagoLightStateChanged',())

    ### Light off pressed: switch off lamp and set out the wago
    def lightButtonOffClicked(self):
        #self.lightOffButton.setDown(True)
        if self.wagoLight is not None:
            if self.wagoLight.getWagoState()!="out":
                if self.motor is not None:
                    try:
                        self.lightSavedPosition=self.motor.getPosition()
                    except:
                        logging.exception("could not get light actuator position")
                        self.lightSavedPosition=None
                    if self['out_delta']!="":
                        delta=float(self['out_delta'])
                    else:
                        delta=0.0
                    light_limits=self.motor.getLimits()
                    self.motor.move(light_limits[0]+delta)
                self.wagoLightStateChanged('unknown')
                self.wagoLight.wagoOut()
            else:
                self.lightOffButton.setDown(True)

    ### Light on pressed: set in the wago and set lamp to previous position
    def lightButtonOnClicked(self):
        #self.lightOnButton.setDown(True)
        if self.wagoLight is not None:
            if self.wagoLight.getWagoState()!="in":
                self.wagoLightStateChanged('unknown')
                self.wagoLight.wagoIn()
                if self.lightSavedPosition is not None and self.motor is not None:
                    self.motor.move(self.lightSavedPosition)
            else:
                self.lightOnButton.setDown(True)

    ### Wago light events
    def wagoLightStateChanged(self,state):
        #print "LightControlBrick.wagoLightStateChanged",state
        if state=='in':
            self.lightOnButton.setDown(True)
            self.lightOffButton.setDown(False)
            self.moveLeftButton.setEnabled(True)
            self.moveRightButton.setEnabled(True)
        elif state=='out':
            self.lightOnButton.setDown(False)
            self.lightOffButton.setDown(True)
            self.moveLeftButton.setEnabled(False)
            self.moveRightButton.setEnabled(False)
        else:
            self.lightOnButton.setDown(False)
            self.lightOffButton.setDown(False)

    def propertyChanged(self,property,oldValue,newValue):
        #print "LightControlBrick2.propertyChanged",property,newValue

        if property=='wagolight':
            if self.wagoLight is not None:
                self.disconnect(self.wagoLight,PYSIGNAL('wagoStateChanged'),self.wagoLightStateChanged)
            self.wagoLight=self.getHardwareObject(newValue)
            if self.wagoLight is not None:
                self.connect(self.wagoLight,PYSIGNAL('wagoStateChanged'),self.wagoLightStateChanged)
                self.wagoLightStateChanged(self.wagoLight.getWagoState())
        elif property=='wagoicons':
            icons_list=newValue.split()
            try:
                self.lightOffButton.setPixmap(Icons.load(icons_list[0]))
                self.lightOnButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass
        elif property=='mnemonic':
            MotorSpinBoxBrick.MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
            if self.motor is not None:
                if self.motor.isReady():
                    limits=self.motor.getLimits()
                    motor_range=float(limits[1]-limits[0])
                    self['delta']=str(motor_range/10.0)
                else:
                    self['delta']=1.0
        else:
            MotorSpinBoxBrick.MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
