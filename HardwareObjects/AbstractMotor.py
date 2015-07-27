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
#   You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""
Descript. : AbstractMotor represent motor.
"""

import abc

class AbstractMotor(object):      
    __metaclass__ = abc.ABCMeta

    (NOTINITIALIZED, UNUSABLE, READY, MOVESTARTED, MOVING, ONLIMIT) = (0,1,2,3,4,5)
    EXPORTER_TO_MOTOR_STATE = { "Invalid": NOTINITIALIZED,
                                "Fault": UNUSABLE,
                                "Ready": READY,
                                "Moving": MOVING,
                                "Created": NOTINITIALIZED,
                                "Initializing": NOTINITIALIZED,
                                "Unknown": UNUSABLE }

    def __init__(self):
        """
        Descript. :
        """
        self.motor_name = None
        self.motor_state = AbstractMotor.NOTINITIALIZED
 
        self.static_limits = (-1E4, 1E4)
        self.limits = (None, None)

    def getMotorMnemonic(self):
        """
        Descript. :
        """
        return self.motor_name

    def updateState(self):
        """
        Descript. :
        """
        self.setIsReady(self.motor_state > MicrodiffMotor.UNUSABLE)

    @abc.abstractmethod
    def getState(self):
        """
        Descript. : return motor state
        """
        return
    
    @abc.abstractmethod
    def getLimits(self):
        """
        Descript. : returns motor limits. If no limits channel defined then
                    static_limits is returned
        """
        return
 
    @abc.abstractmethod
    def getPosition(self):
        """
        Descript. :
        """
        return

    def getDialPosition(self):
        """
        Descript. :
        """
        return self.getPosition()

    @abc.abstractmethod
    def move(self, absolute_position):
        """
        Descript. :
        """
        return

    @abc.abstractmethod
    def moveRelative(self, relative_position):
        """
        Descript. :
        """
        return

    @abc.abstractmethod
    def syncMove(self, position, timeout=None):
        """
        Descript. :
        """
        return

    @abc.abstractmethod
    def syncMoveRelative(self, relative_position, timeout=None):
        """
        Descript. :
        """
        return

    @abc.abstractmethod
    def stop(self):
        """
        Descript. :
        """
        return
