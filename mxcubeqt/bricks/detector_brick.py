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

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"

STATES = {
    "unknown": colors.LIGHT_GRAY,
    "OK": colors.LIGHT_BLUE,
    "BAD": colors.LIGHT_RED,
}
    
DETECTOR_STATES = {
    "busy": colors.LIGHT_GREEN,
    "error": colors.LIGHT_RED,
    "initializing": colors.LIGHT_YELLOW,
    "calibrating": colors.LIGHT_YELLOW,
    "configuring": colors.LIGHT_YELLOW,
    "slave": colors.LIGHT_RED,
    "exposing": colors.LIGHT_GREEN,
    "ready": colors.LIGHT_BLUE,
    "uninitialized": colors.LIGHT_GRAY,
}

class DetectorBrick(BaseWidget):



    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = qt_import.QGroupBox("Detector status", self)
        self.status_label = qt_import.QLabel("<b>unknown status</b>", _main_groupbox)
        self.frame_rate_label = qt_import.QLabel("   Frame rate     : ", _main_groupbox)
        self.temperature_label = qt_import.QLabel("   Temperature:", _main_groupbox)
        self.humidity_label = qt_import.QLabel("   Humidity:     ", _main_groupbox)

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = qt_import.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.status_label)
        _main_groupbox_vlayout.addWidget(self.frame_rate_label)
        _main_groupbox_vlayout.addWidget(self.temperature_label)
        _main_groupbox_vlayout.addWidget(self.humidity_label)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        main_layout = qt_import.QVBoxLayout(self)
        main_layout.addWidget(_main_groupbox)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        colors.set_widget_color(
            self.status_label, DETECTOR_STATES["uninitialized"]
        )
        colors.set_widget_color(
            self.temperature_label, STATES["unknown"]
        )
        colors.set_widget_color(
            self.humidity_label, STATES["unknown"]
        )
        colors.set_widget_color(self.frame_rate_label, STATES["OK"])

        self.status_label.setMinimumHeight(20)
        self.status_label.setAlignment(qt_import.Qt.AlignCenter)
        self.temperature_label.setMinimumHeight(20)
        self.humidity_label.setMinimumHeight(20)
        self.frame_rate_label.setMinimumHeight(20)

        self.connect(
            HWR.beamline.detector, "temperatureChanged", self.temperature_changed
        )
        self.connect(HWR.beamline.detector, "humidityChanged", self.humidity_changed)
        self.connect(HWR.beamline.detector, "statusChanged", self.status_changed)
        self.connect(
            HWR.beamline.detector, "frameRateChanged", self.frame_rate_changed
        )

    def status_changed(self, status, status_message):
        if status:
            self.status_label.setText("<b>%s</b>" % status.title())
            colors.set_widget_color(
                self.status_label,
                DETECTOR_STATES.get(status, colors.LIGHT_GRAY),
            )
            self.setToolTip(status_message)

    def temperature_changed(self, value, status_ok):
        if value is not None:
            unit = u"\N{DEGREE SIGN}"
            self.temperature_label.setText("   Temperature : %0.1f%s" % (value, unit))
        if status_ok:
            colors.set_widget_color(
                self.temperature_label, STATES["OK"]
            )
        else:
            colors.set_widget_color(
                self.temperature_label, STATES["BAD"]
            )

    def humidity_changed(self, value, status_ok):
        if value is not None:
            self.humidity_label.setText(
                "   Humidity         : %0.1f%s" % (value, chr(37))
            )
        if status_ok:
            colors.set_widget_color(
                self.humidity_label, STATES["OK"]
            )
        else:
            colors.set_widget_color(
                self.humidity_label, STATES["BAD"]
            )

    def frame_rate_changed(self, value):
        if value is not None:
            self.frame_rate_label.setText("   Frame rate     : %d Hz" % value)
