from BlissFramework.Bricks import Qt4_MotorSpinBoxBrick
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework import Qt4_Icons
#from BlissFramework.Utils import Qt4_widget_colors
#from BlissFramework.Qt4_BaseComponents import BlissWidget

'''
Controls both the light on/off (wago) and intensity (motor)
'''
__category__ = 'SOLEIL'

class Qt4_LightControlBrick(Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick):
    def __init__(self, *args):
        Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.__init__(self, *args)
        
        self.wagoLight =None
        self.addProperty('wagolight', 'string', '')
        self.addProperty('wagoicons', 'string', '')
        self.addProperty('out_delta', 'string', '')
        
        self.light_button_box = QtGui.QWidget(self.main_gbox)
        
        self.lightOffButton=QtGui.QPushButton(self.light_button_box)
        self.lightOffButton.setIcon(Qt4_Icons.load_icon('far_left'))
        self.lightOffButton.setToolTip("Switches off the light and sets the intensity to zero")
        
        self.lightOnButton=QtGui.QPushButton(self.light_button_box)
        self.lightOnButton.setIcon(Qt4_Icons.load_icon('far_right'))
        self.lightOnButton.setToolTip("Switches on the light and sets the intensity back to the previous setting")
        

        self.light_button_box_layout = QtGui.QHBoxLayout(self.light_button_box)
        self.light_button_box_layout.addWidget(self.lightOffButton)
        self.light_button_box_layout.addWidget(self.lightOnButton)
        self.light_button_box_layout.setSpacing(2)
        self.light_button_box_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_gbox_layout.addWidget(self.light_button_box)
                
        self.lightOffButton.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                            QtGui.QSizePolicy.Minimum)
        self.lightOnButton.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                            QtGui.QSizePolicy.Minimum)

        self.defineSlot('wagoLightStateChanged',())
        self.lightOffButton.clicked.connect(self.lightButtonOffClicked)
        self.lightOnButton.clicked.connect(self.lightButtonOnClicked)
        
        logging.info("init Qt4_LightControlBrick")
    
    ### Light off pressed: switch off lamp and set out the wago
    def lightButtonOffClicked(self):
        if self.wagoLight is not None:
            if self.wagoLight.getWagoState()!="out":
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
                #if self.lightSavedPosition is not None and self.motor is not None:
                #    self.motor.move(self.lightSavedPosition)
            else:
                self.lightOnButton.setDown(True)

    ### Wago light events
    def wagoLightStateChanged(self,state):
        #print "LightControlBrick.wagoLightStateChanged",state
        if state=='in':
            self.lightOnButton.setDown(True)
            self.lightOffButton.setDown(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        elif state=='out':
            self.lightOnButton.setDown(False)
            self.lightOffButton.setDown(True)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        else:
            self.lightOnButton.setDown(False)
            self.lightOffButton.setDown(False)

    def propertyChanged(self,property,oldValue,newValue):
        #print "LightControlBrick2.propertyChanged",property,newValue

        if property=='wagolight':
            if self.wagoLight is not None:
                self.disconnect(self.wagoLight,'wagoStateChanged',self.wagoLightStateChanged)
            self.wagoLight=self.getHardwareObject(newValue)
            if self.wagoLight is not None:
                self.connect(self.wagoLight,'wagoStateChanged',self.wagoLightStateChanged)
                self.wagoLightStateChanged(self.wagoLight.getWagoState())
        elif property=='wagoicons':
            icons_list=newValue.split()
            try:
                self.lightOffButton.setIcon(Qt4_Icons.load_icon(icons_list[0]))
                self.lightOnButton.setIcon(Qt4_Icons.load_icon(icons_list[1]))
            except IndexError:
                pass
        elif property=='mnemonic':
            Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
            try:
                if self.motor is not None:
                    if self.motor.isReady():
                        limits=self.motor.getLimits()
                        motor_range=float(limits[1]-limits[0])
                        self['delta']=str(motor_range/10.0)
                    else:
                        self['delta']=1.0
            except :
                pass
        else:
            Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
        
