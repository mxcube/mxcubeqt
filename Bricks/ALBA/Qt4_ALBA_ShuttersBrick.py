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

import os
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework import Qt4_Icons
from BlissFramework.Qt4_BaseComponents import BlissWidget

from widgets.QLed import QLed

__category__ = 'ALBA'

# 
# These state list is as in ALBAEpsActuator.py
# 
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = \
         (0,1,9,11,13,23)

STATES = {STATE_IN: Qt4_widget_colors.LIGHT_GREEN,
          STATE_OUT: Qt4_widget_colors.LIGHT_GRAY,
          STATE_MOVING: Qt4_widget_colors.LIGHT_YELLOW,
          STATE_FAULT: Qt4_widget_colors.LIGHT_RED,
          STATE_ALARM: Qt4_widget_colors.LIGHT_RED,
          STATE_UNKNOWN: Qt4_widget_colors.LIGHT_GRAY}

class Qt4_ALBA_ShuttersBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
        self.logger = logging.getLogger("HWR").info("Creating GUI Alba Shutters State")

        # Hardware objects ----------------------------------------------------
        self.fast_shut_ho = None
        self.slow_shut_ho = None
        self.photon_shut_ho = None
        self.fe_ho = None

        self.default_led_size = 30 

        # Properties ---------------------------------------------------------- 
        self.addProperty('fast_shutter', 'string', '')
        self.addProperty('slow_shutter', 'string', '')
        self.addProperty('photon_shutter', 'string', '')
        self.addProperty('frontend', 'string', '')
        self.addProperty('led_size', 'string', '')

        # Graphic elements ----------------------------------------------------
        self.shutter_box = QtGui.QGroupBox()
        self.shutter_box.setTitle("Beam on Sample")
        self.leds_layout = QtGui.QHBoxLayout(self.shutter_box)
        
        self.fast_led = QLed.QLed()
        self.fast_led.setUserName("Fast Shutter")

        self.slow_led = QLed.QLed()
        self.slow_led.setUserName("Slow Shutter")

        self.photon_led = QLed.QLed()
        self.photon_led.setUserName("Photon Shutter")

        self.fe_led = QLed.QLed()
        self.fe_led.setUserName("Front End")
    
        self.leds_layout.addWidget(self.fast_led)
        self.leds_layout.addWidget(self.slow_led)
        self.leds_layout.addWidget(self.photon_led)
        self.leds_layout.addWidget(self.fe_led)

        QtGui.QHBoxLayout(self)
    
        self.layout().addWidget(self.shutter_box)
        self.layout().setContentsMargins(0,0,0,0)
        self.leds_layout.setContentsMargins(2,2,2,2)

        self.set_led_size(self.default_led_size)
        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)

        # Other --------------------------------------------------------------- 
        self.setToolTip("Beam on Sample. Shutters status")

        #self.slow_state_changed(True)
        #self.fast_state_changed(False)
        #self.frontend_state_changed(False)
#
#        self.fast_led.setShapeAndColor("circle","orange")
#        self.fast_led.setMessage("in down position. X-Ray will go through")
        self.setEnabled(True)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.fast_shut_ho = None
        self.slow_shut_ho = None
        self.photon_shut_ho = None
        self.fe_ho = None

        print("setting %s property to %s", property_name, new_value)

        if property_name == 'fast_shutter':
            if self.fast_shut_ho is not None:
                self.disconnect(self.fast_shut_ho, QtCore.SIGNAL('stateChanged'), self.fast_state_changed)

            self.fast_shut_ho = self.getHardwareObject(new_value)

            if self.fast_shut_ho is not None:
                self.connect(self.fast_shut_ho, QtCore.SIGNAL('stateChanged'), self.fast_state_changed)

        elif property_name == 'slow_shutter':
            if self.slow_shut_ho is not None:
                self.disconnect(self.slow_shut_ho, QtCore.SIGNAL('stateChanged'), self.slow_state_changed)

            self.slow_shut_ho = self.getHardwareObject(new_value)

            if self.slow_shut_ho is not None:
                self.connect(self.slow_shut_ho, QtCore.SIGNAL('stateChanged'), self.slow_state_changed)

        elif property_name == 'photon_shutter':
            if self.photon_shut_ho is not None:
                self.disconnect(self.photon_shut_ho, QtCore.SIGNAL('stateChanged'), self.photon_state_changed)

            self.photon_shut_ho = self.getHardwareObject(new_value)

            if self.photon_shut_ho is not None:
                self.connect(self.photon_shut_ho, QtCore.SIGNAL('stateChanged'), self.photon_state_changed)

        elif property_name == 'frontend':
            if self.fe_ho is not None:
                self.disconnect(self.fe_ho, QtCore.SIGNAL('stateChanged'), self.frontend_state_changed)

            self.fe_ho = self.getHardwareObject(new_value)

            if self.fe_ho is not None:
                self.connect(self.fe_ho, QtCore.SIGNAL('stateChanged'), self.frontend_state_changed)

        elif property_name == 'led_size':
            if new_value != '':
                self.set_led_size(int(new_value))
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_led_size(self, newsize):
        self.led_size = newsize

        self.fast_led.setFixedSize(self.led_size,self.led_size)
        self.slow_led.setFixedSize(self.led_size,self.led_size)
        self.photon_led.setFixedSize(self.led_size,self.led_size)
        self.fe_led.setFixedSize(self.led_size,self.led_size)

    def fast_state_changed(self,value):
        led = self.fe_led
        self._update_led(led, value)
        
    def slow_state_changed(self,value):
        led = self.slow_led
        self._update_led(led, value)

    def photon_state_changed(self,value):
        led = self.photon_led
        self._update_led(led, value)

    def frontend_state_changed(self,value):
        led = self.fe_led
        self._update_led(led, value)

    def _update_led(self, led, value):
        led.setState(value)

def test_brick(brick):
    """ Run test by running from command line test_mxcube <name of this file> """
    brick.setProperty("frontend", "/photonshut")
