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

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget

from mx3core import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class DetectorStatusBrick(BaseWidget):

    STATES = {
        "unknown": Colors.LIGHT_GRAY,
        "OK": Colors.LIGHT_BLUE,
        "BAD": Colors.LIGHT_RED,
    }
    DETECTOR_STATES = {
        "busy": Colors.LIGHT_GREEN,
        "error": Colors.LIGHT_RED,
        "initializing": Colors.LIGHT_YELLOW,
        "calibrating": Colors.LIGHT_YELLOW,
        "configuring": Colors.LIGHT_YELLOW,
        "slave": Colors.LIGHT_RED,
        "exposing": Colors.LIGHT_GREEN,
        "ready": Colors.LIGHT_BLUE,
        "uninitialized": Colors.LIGHT_GRAY,
    }

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = QtImport.QGroupBox("Detector status", self)
        self.status_label = QtImport.QLabel("<b>unknown status</b>", _main_groupbox)
        self.frame_rate_label = QtImport.QLabel("   Frame rate     : ", _main_groupbox)
        self.temperature_label = QtImport.QLabel("   Temperature:", _main_groupbox)
        self.humidity_label = QtImport.QLabel("   Humidity:     ", _main_groupbox)

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QtImport.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.status_label)
        _main_groupbox_vlayout.addWidget(self.frame_rate_label)
        _main_groupbox_vlayout.addWidget(self.temperature_label)
        _main_groupbox_vlayout.addWidget(self.humidity_label)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        main_layout = QtImport.QVBoxLayout(self)
        main_layout.addWidget(_main_groupbox)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        Colors.set_widget_color(
            self.status_label, DetectorStatusBrick.DETECTOR_STATES["uninitialized"]
        )
        Colors.set_widget_color(
            self.temperature_label, DetectorStatusBrick.STATES["unknown"]
        )
        Colors.set_widget_color(
            self.humidity_label, DetectorStatusBrick.STATES["unknown"]
        )
        Colors.set_widget_color(self.frame_rate_label, DetectorStatusBrick.STATES["OK"])

        self.status_label.setMinimumHeight(20)
        self.status_label.setAlignment(QtImport.Qt.AlignCenter)
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
            Colors.set_widget_color(
                self.status_label,
                DetectorStatusBrick.DETECTOR_STATES.get(status, Colors.LIGHT_GRAY),
            )
            self.setToolTip(status_message)

    def temperature_changed(self, value, status_ok):
        if value is not None:
            unit = u"\N{DEGREE SIGN}"
            self.temperature_label.setText("   Temperature : %0.1f%s" % (value, unit))
        if status_ok:
            Colors.set_widget_color(
                self.temperature_label, DetectorStatusBrick.STATES["OK"]
            )
        else:
            Colors.set_widget_color(
                self.temperature_label, DetectorStatusBrick.STATES["BAD"]
            )

    def humidity_changed(self, value, status_ok):
        if value is not None:
            self.humidity_label.setText(
                "   Humidity         : %0.1f%s" % (value, chr(37))
            )
        if status_ok:
            Colors.set_widget_color(
                self.humidity_label, DetectorStatusBrick.STATES["OK"]
            )
        else:
            Colors.set_widget_color(
                self.humidity_label, DetectorStatusBrick.STATES["BAD"]
            )

    def frame_rate_changed(self, value):
        if value is not None:
            self.frame_rate_label.setText("   Frame rate     : %d Hz" % value)
