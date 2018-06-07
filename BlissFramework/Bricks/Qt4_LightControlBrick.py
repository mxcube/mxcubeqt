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

from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Bricks import Qt4_MotorSpinBoxBrick
from BlissFramework import Qt4_Icons

import logging

from QtImport import *

'''
Controls both the light on/off (light_actuator) and intensity (motor)
'''
__category__ = 'General'

STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = \
         (0,1,9,11,13,23)

class Qt4_LightControlBrick(Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick):
    def __init__(self, *args):

        Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.__init__(self, *args)

        self.light_actuator_hwo = None
        self.light_saved_pos=None

        self.addProperty('light_actuator', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('out_delta', 'string', '')

        self.light_off_button=QPushButton(self.main_gbox)
        self.light_off_button.setIcon(Qt4_Icons.load_icon('BulbDelete'))
        self.light_off_button.setFixedSize(27, 27)
        
        self.light_on_button=QPushButton(self.main_gbox)
        self.light_on_button.setIcon(Qt4_Icons.load_icon('BulbCheck'))
        self.light_on_button.setFixedSize(27, 27)
        
        self.light_off_button.clicked.connect(self.lightButtonOffClicked)
        self.light_on_button.clicked.connect(self.lightButtonOnClicked)

        self._gbox_hbox_layout.addWidget(self.light_off_button)
        self._gbox_hbox_layout.addWidget(self.light_on_button)

        self.light_off_button.setToolTip("Switches off the light and sets the intensity to zero")
        self.light_on_button.setToolTip("Switches on the light and sets the intensity back to the previous setting")        

        self.light_off_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.light_on_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

               
    ### Light off pressed: switch off lamp and set out the wago
    def lightButtonOffClicked(self):
        if self.motor_hwobj is not None and hasattr(self.motor_hwobj, 'move_in'):
            self.motor_hwobj.move_in()
            return
        #self.lightOffButton.setDown(True)
        if self.light_actuator_hwo is not None:
            if self.light_actuator_hwo.getState() != STATE_OUT:
                if self.motor_hwobj is not None:
                    try:
                        self.light_saved_pos=self.motor_hwobj.getPosition()
                    except:
                        logging.exception("could not get light actuator position")
                        self.light_saved_pos=None

                    if self['out_delta']!="":
                        delta=float(self['out_delta'])
                    else:
                        delta=0.0

                    light_limits=self.motor_hwobj.getLimits()
                    self.motor_hwobj.move(light_limits[0]+delta)

                self.lightStateChanged(STATE_UNKNOWN)
                self.light_actuator_hwo.cmdOut()
            else:
                self.light_off_button.setDown(True)

    ### Light on pressed: set in the wago and set lamp to previous position
    def lightButtonOnClicked(self):
        if self.motor_hwobj is not None and hasattr(self.motor_hwobj, 'move_out'):
            self.motor_hwobj.move_out()
            return
        if self.light_actuator_hwo is not None:
            if self.light_actuator_hwo.getState() != STATE_IN:
                self.lightStateChanged(STATE_UNKNOWN)
                self.light_actuator_hwo.cmdIn()
                if self.light_saved_pos is not None and self.motor_hwobj is not None:
                    self.motor_hwobj.move(self.light_saved_pos)
            else:
                self.light_on_button.setDown(True)

    ### Wago light events
    def lightStateChanged(self,state):
        #print "LightControlBrick.wagoLightStateChanged",state
        if state== STATE_IN:
            self.light_on_button.setDown(True)
            self.light_off_button.setDown(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        elif state== STATE_OUT:
            self.light_on_button.setDown(False)
            self.light_off_button.setDown(True)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        else:
            self.light_on_button.setDown(False)
            self.light_off_button.setDown(False)

    def propertyChanged(self,property,oldValue,newValue):

        if property=='light_actuator':
            if self.light_actuator_hwo is not None:
                self.disconnect(self.light_actuator_hwo,'wagoStateChanged',self.lightStateChanged)

            self.light_actuator_hwo=self.getHardwareObject(newValue)
            if self.light_actuator_hwo is not None:
                self.connect(self.light_actuator_hwo,'wagoStateChanged',self.lightStateChanged)
                self.lightStateChanged(self.light_actuator_hwo.getState())

        elif property=='icons':
            icons_list=newValue.split()
            try:
                self.light_off_button.setIcon(Qt4_Icons.load_icon(icons_list[0]))
                self.light_on_button.setIcon(Qt4_Icons.load_icon(icons_list[1]))
            except IndexError:
                pass
        elif property=='mnemonic':
            Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
            if self.motor_hwobj is not None:
                if self.motor_hwobj.isReady():
                    limits=self.motor_hwobj.getLimits()
                    motor_range=float(limits[1]-limits[0])
                    self['delta']=str(motor_range/10.0)
                else:
                    self['delta']=1.0
        else:
            Qt4_MotorSpinBoxBrick.Qt4_MotorSpinBoxBrick.propertyChanged(self,property,oldValue,newValue)
