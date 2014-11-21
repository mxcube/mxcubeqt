from HardwareRepository.BaseHardwareObjects import Device
import math
import logging
import time
import gevent
import types
import emotion
import os

class EmotionMotor(Device):      
    (NOTINITIALIZED, UNUSABLE, READY, MOVESTARTED, MOVING, ONLIMIT) = (0,1,2,3,4,5)

    @staticmethod
    def load_config(config_file):
        emotion.load_cfg(config_file,clear=False)    

    def __init__(self, name):
        Device.__init__(self, name)

    def init(self): 
        self.motorState = EmotionMotor.NOTINITIALIZED
        self.username = self.motor_name

        EmotionMotor.load_config(self.config_file)
        self.motor = emotion.get_axis(self.motor_name)
        self.connect(self.motor, "position", self.positionChanged)
        self.connect(self.motor, "state", self.updateState)
        self.connect(self.motor, "move_done", self._move_done)

    def connectNotify(self, signal):
        if signal == 'positionChanged':
                self.emit('positionChanged', (self.getPosition(), ))
        elif signal == 'stateChanged':
                self.updateState()
        elif signal == 'limitsChanged':
                self.motorLimitsChanged()  

    def _move_done(self, move_done):
        if move_done:
          self.updateState("READY")
        else:
          self.updateState("MOVING")
 
    def updateState(self, state=None):
        if state is None:
            state = self.motor.state()
        # convert from grob state to Hardware Object motor state
        if state == "MOVING":
            state = EmotionMotor.MOVING
        elif state == "READY":
            state = EmotionMotor.READY
        elif state == "ONLIMIT":
            state = EmotionMotor.ONLIMIT
        else:
            state = EmotionMotor.UNUSABLE

        self.setIsReady(state > EmotionMotor.UNUSABLE)

        if self.motorState != state:
            self.motorState = state
            self.emit('stateChanged', (self.motorState, ))

    def getState(self):
        self.updateState()
        return self.motorState
    
    def motorLimitsChanged(self):
        self.emit('limitsChanged', (self.getLimits(), ))
                     
    def getLimits(self):
        return self.motor.limits()

    def positionChanged(self, absolutePosition):
        #print self.name(), absolutePosition
        self.emit('positionChanged', (absolutePosition, ))

    def getPosition(self):
        return self.motor.position()

    def getDialPosition(self):
        return self.getPosition()

    def move(self, position):
        #self.updateState("MOVING")
        self.motor.move(position, wait=False) #.link(self.updateState)

    def moveRelative(self, relativePosition):
        self.move(self.getPosition() + relativePosition)

    def syncMoveRelative(self, relative_position, timeout=None):
        return self.syncMove(self.getPosition() + relative_position)

    def waitEndOfMove(self, timeout=None):
        with gevent.Timeout(timeout):
           self.motor.wait_move()

    def syncMove(self, position, timeout=None):
        self.move(position)
        self.waitEndOfMove(timeout)

    def motorIsMoving(self):
        return self.motorState == EmotionMotor.MOVING
 
    def getMotorMnemonic(self):
        return self.motor_name

    def stop(self):
        self.motor.stop()
