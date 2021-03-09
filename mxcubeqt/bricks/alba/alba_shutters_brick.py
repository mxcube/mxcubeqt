#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.utils.QLed import QLed
from mxcubeqt.base_components import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ALBA"


#
# These state list is as in ALBAEpsActuator.py
#
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)

STATES = {
    STATE_IN: colors.LIGHT_GREEN,
    STATE_OUT: colors.LIGHT_GRAY,
    STATE_MOVING: colors.LIGHT_YELLOW,
    STATE_FAULT: colors.LIGHT_RED,
    STATE_ALARM: colors.LIGHT_RED,
    STATE_UNKNOWN: colors.LIGHT_GRAY,
}


class AlbaShuttersBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)
        self.logger = logging.getLogger("HWR").info("Creating GUI Alba Shutters State")

        # Hardware objects ----------------------------------------------------
        self.fast_shut_ho = None
        self.slow_shut_ho = None
        self.photon_shut_ho = None
        self.fe_ho = None

        self.default_led_size = 30

        # Properties ----------------------------------------------------------
        self.add_property("fast_shutter", "string", "")
        self.add_property("slow_shutter", "string", "")
        self.add_property("photon_shutter", "string", "")
        self.add_property("frontend", "string", "")
        self.add_property("led_size", "string", "")

        # Graphic elements ----------------------------------------------------
        self.shutter_box = qt_import.QGroupBox()
        self.shutter_box.setTitle("Beam on Sample")
        self.leds_layout = qt_import.QHBoxLayout(self.shutter_box)

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

        qt_import.QHBoxLayout(self)

        self.layout().addWidget(self.shutter_box)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.leds_layout.setContentsMargins(2, 2, 2, 2)

        self.set_led_size(self.default_led_size)
        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.MinimumExpanding
        )

        # Other ---------------------------------------------------------------
        self.setToolTip("Beam on Sample. Shutters status")

        # self.slow_state_changed(True)
        # self.fast_state_changed(False)
        # self.frontend_state_changed(False)
        #
        #        self.fast_led.setShapeAndColor("circle","orange")
        #        self.fast_led.setMessage("in down position. X-Ray will go through")
        self.setEnabled(True)

    def property_changed(self, property_name, old_value, new_value):
        self.fast_shut_ho = None
        self.slow_shut_ho = None
        self.photon_shut_ho = None
        self.fe_ho = None

        print("setting %s property to %s", property_name, new_value)

        if property_name == "fast_shutter":
            if self.fast_shut_ho is not None:
                self.disconnect(
                    self.fast_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.fast_state_changed,
                )

            self.fast_shut_ho = self.get_hardware_object(new_value)

            if self.fast_shut_ho is not None:
                self.connect(
                    self.fast_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.fast_state_changed,
                )

        elif property_name == "slow_shutter":
            if self.slow_shut_ho is not None:
                self.disconnect(
                    self.slow_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.slow_state_changed,
                )

            self.slow_shut_ho = self.get_hardware_object(new_value)

            if self.slow_shut_ho is not None:
                self.connect(
                    self.slow_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.slow_state_changed,
                )

        elif property_name == "photon_shutter":
            if self.photon_shut_ho is not None:
                self.disconnect(
                    self.photon_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.photon_state_changed,
                )

            self.photon_shut_ho = self.get_hardware_object(new_value)

            if self.photon_shut_ho is not None:
                self.connect(
                    self.photon_shut_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.photon_state_changed,
                )

        elif property_name == "frontend":
            if self.fe_ho is not None:
                self.disconnect(
                    self.fe_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.frontend_state_changed,
                )

            self.fe_ho = self.get_hardware_object(new_value)

            if self.fe_ho is not None:
                self.connect(
                    self.fe_ho,
                    qt_import.SIGNAL("stateChanged"),
                    self.frontend_state_changed,
                )

        elif property_name == "led_size":
            if new_value != "":
                self.set_led_size(int(new_value))
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def set_led_size(self, newsize):
        self.led_size = newsize

        self.fast_led.setFixedSize(self.led_size, self.led_size)
        self.slow_led.setFixedSize(self.led_size, self.led_size)
        self.photon_led.setFixedSize(self.led_size, self.led_size)
        self.fe_led.setFixedSize(self.led_size, self.led_size)

    def fast_state_changed(self, value):
        led = self.fe_led
        self._update_led(led, value)

    def slow_state_changed(self, value):
        led = self.slow_led
        self._update_led(led, value)

    def photon_state_changed(self, value):
        led = self.photon_led
        self._update_led(led, value)

    def frontend_state_changed(self, value):
        led = self.fe_led
        self._update_led(led, value)

    def _update_led(self, led, value):
        led.setState(value)


def test_brick(brick):
    """ Run test by running from command line test_mxcube <name of this file> """
    brick.setProperty("frontend", "/photonshut")
