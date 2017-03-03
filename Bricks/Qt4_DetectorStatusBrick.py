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

from QtImport import *

from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework import Qt4_Icons


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


class Qt4_DetectorStatusBrick(BlissWidget):
 
    STATES = {'unknown': Qt4_widget_colors.LIGHT_GRAY,
              'OK': Qt4_widget_colors.LIGHT_BLUE,
              'BAD': Qt4_widget_colors.LIGHT_RED}
    DETECTOR_STATES = {'busy': Qt4_widget_colors.LIGHT_GREEN,
                       'error': Qt4_widget_colors.LIGHT_RED,
                       'initializing': Qt4_widget_colors.LIGHT_RED,
                       'calibrating': Qt4_widget_colors.LIGHT_YELLOW,
                       'slave': Qt4_widget_colors.LIGHT_RED,
                       'exposing': Qt4_widget_colors.LIGHT_GREEN,
                       'ready': Qt4_widget_colors.LIGHT_BLUE,
                       'uninitialized': Qt4_widget_colors.LIGHT_GRAY} 
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.detector_hwobj = None 

        # Internal variables --------------------------------------------------

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        #self.defineSlot('collectStarted',())

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = QGroupBox("Detector status", self) 
        self.status_label = QLabel("<b>unknown status</b>", _main_groupbox)
        self.temperature_label = QLabel("Temperature:", _main_groupbox)
        self.humidity_label = QLabel("Humidity:     ", _main_groupbox)

        # Layout -------------------------------------------------------------- 
        _main_groupbox_vlayout = QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.status_label)
        _main_groupbox_vlayout.addWidget(self.temperature_label)
        _main_groupbox_vlayout.addWidget(self.humidity_label)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(_main_groupbox)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.status_label, 
           Qt4_DetectorStatusBrick.DETECTOR_STATES['uninitialized'])
        Qt4_widget_colors.set_widget_color(self.temperature_label, 
           Qt4_DetectorStatusBrick.STATES['unknown'])
        Qt4_widget_colors.set_widget_color(self.humidity_label, 
            Qt4_DetectorStatusBrick.STATES['unknown']) 

        self.status_label.setMinimumHeight(20)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setMinimumHeight(20)
        self.humidity_label.setMinimumHeight(20)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.detector_hwobj is not None:
                self.disconnect(self.detector_hwobj,
                                'temperatureChanged',
                                self.temperature_changed)
                self.disconnect(self.detector_hwobj,
                                'humidityChanged',
                                self.humidity_changed)
                self.disconnect(self.detector_hwobj,
                                'statusChanged',
                                self.status_changed)
	    self.detector_hwobj = self.getHardwareObject(new_value)
            if self.detector_hwobj is not None:
                self.connect(self.detector_hwobj,
                             'temperatureChanged',
                             self.temperature_changed)
                self.connect(self.detector_hwobj,
                             'humidityChanged',
                             self.humidity_changed)
                self.connect(self.detector_hwobj,
                             'statusChanged',
                             self.status_changed)
                self.detector_hwobj.update_values()             
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)
     
    def status_changed(self, status, status_message):
        """
        """
        if status:
            self.status_label.setText("<b>%s</b>" % status.title())
            Qt4_widget_colors.set_widget_color(self.status_label,
               Qt4_DetectorStatusBrick.DETECTOR_STATES[status])
            self.setToolTip(status_message)

    def temperature_changed(self, value, status_ok):
        """
        """
        if value is not None:
            unit = u'\N{DEGREE SIGN}'
            self.temperature_label.setText("   Temperature : %0.1f%s" %(value, unit))
        if status_ok: 
            Qt4_widget_colors.set_widget_color(self.temperature_label,
                Qt4_DetectorStatusBrick.STATES['OK'])
        else:
            Qt4_widget_colors.set_widget_color(self.temperature_label,
                Qt4_DetectorStatusBrick.STATES['BAD'])

    def humidity_changed(self, value, status_ok):
        """
        """
        if value is not None:
            self.humidity_label.setText("   Humidity         : %0.1f%s" %(value, chr(37)))
        if status_ok:
            Qt4_widget_colors.set_widget_color(self.humidity_label,
                Qt4_DetectorStatusBrick.STATES['OK'])
        else:
            Qt4_widget_colors.set_widget_color(self.humidity_label,
                Qt4_DetectorStatusBrick.STATES['BAD'])
