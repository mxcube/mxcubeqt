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

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'General'

STATES = {'unknown': Qt4_widget_colors.GRAY,
          'ready': Qt4_widget_colors.LIGHT_BLUE,
          'error': Qt4_widget_colors.LIGHT_RED}

class Qt4_MachineInfoBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.mach_info_hwobj = None

        # Internal values -----------------------------------------------------
        self.last_value = None

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('diskThreshold', 'float', '200')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setColDir', ())
         
        # Graphic elements ----------------------------------------------------
        self.current_label = QtGui.QLabel("Machine current", self)
        self.current_value_label = QtGui.QLabel(self)
        self.current_value_label.setAlignment(QtCore.Qt.AlignCenter)
        bold_font = self.current_value_label.font()
        bold_font.setPointSize(14)
        self.current_value_label.setFont(bold_font)
        #State text
        self.state_text_label = QtGui.QLabel("Machine state text", self)
        self.state_text_value_label = QtGui.QLabel(self)
        self.state_text_value_label.setAlignment(QtCore.Qt.AlignCenter)
        #Intensity
        self.intensity_label = QtGui.QLabel("Intensity monitor", self)
        self.intensity_value_label = QtGui.QLabel(self)
        self.intensity_value_label.setAlignment(QtCore.Qt.AlignCenter)
	#Hutch temperature
        self.temperature_label = QtGui.QLabel("Hutch temperature", self)
        self.temperature_value_label = QtGui.QLabel(self)
        self.temperature_value_label.setAlignment(QtCore.Qt.AlignCenter)
        #Hutch humidity
        self.humidity_label = QtGui.QLabel("Hutch humidity", self)
        self.humidity_value_label = QtGui.QLabel(self) 
        self.humidity_value_label.setAlignment(QtCore.Qt.AlignCenter)  
        #Available disc space
        self.disc_label = QtGui.QLabel("Storage disc space", self)
        self.disc_value_label = QtGui.QLabel(self)
        #Cryostream position
        self.cryo_label = QtGui.QLabel("Cryojet position", self)
        self.cryo_value_label = QtGui.QLabel(self)
        self.cryo_value_label.setFont(bold_font)
        self.cryo_value_label.setAlignment(QtCore.Qt.AlignCenter)
        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.current_label)
        _main_vlayout.addWidget(self.current_value_label)
        _main_vlayout.addWidget(self.state_text_label)
        _main_vlayout.addWidget(self.state_text_value_label)
        _main_vlayout.addWidget(self.intensity_label)
        _main_vlayout.addWidget(self.intensity_value_label)
        _main_vlayout.addWidget(self.temperature_label)
        _main_vlayout.addWidget(self.temperature_value_label) 
        _main_vlayout.addWidget(self.humidity_label)
        _main_vlayout.addWidget(self.humidity_value_label)
        _main_vlayout.addWidget(self.disc_label)
        _main_vlayout.addWidget(self.disc_value_label)
        _main_vlayout.addWidget(self.cryo_label)
        _main_vlayout.addWidget(self.cryo_value_label)
        _main_vlayout.setSpacing(1)
        _main_vlayout.setContentsMargins(1, 1, 1, 1)

        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        self.setToolTip("Main information about current, state, " + \
                        "intensity, temperature, humidity, storage disc" + \
                        "and cryo")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == 'mnemonic':
            if self.mach_info_hwobj is not None:
                self.disconnect(self.mach_info_hwobj, 'valuesChanged', self.set_value)
                self.disconnect(self.mach_info_hwobj, 'inRangeChanged', self.set_color)
                self.disconnect(self.mach_info_hwobj, 'tempHumChanged', self.temp_hum_changed)

            self.mach_info_hwobj = self.getHardwareObject(new_value)
            if self.mach_info_hwobj is not None:
                self.setEnabled(True)
                self.connect(self.mach_info_hwobj, 'valuesChanged', self.set_value)
                self.connect(self.mach_info_hwobj, 'inRangeChanged', self.set_color)
                self.connect(self.mach_info_hwobj, 'tempHumChanged', self.temp_hum_changed)
                if self.mach_info_hwobj.has_cryo() is False:
                    self.cryo_label.hide()
                    self.cryo_value_label.hide()
                self.mach_info_hwobj.update_values() 
            else:
                self.setEnabled(False)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_value(self, values):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        txt = '??? mA' if values.get("current") is None else '<b>%s</b> mA' % \
	       str(self['formatString'] % abs(values.get("current")))
        self.current_value_label.setText(txt)
        self.state_text_value_label.setText(values.get("stateText"))
        txt = '??? A' if values["intens"]["value"] is None else '%1.2e A' % \
	       (values["intens"]["value"] * 1.0)   	
        self.intensity_value_label.setText(txt)
        if values.get("cryo") == 1:
            self.cryo_value_label.setText(" In place ")
        elif values.get("cryo") == 0:
            self.cryo_value_label.setText("NOT IN PLACE")
        else:
            self.cryo_value_label.setText("Unknown")

    def set_color(self, value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if value.get('current') is None:
            Qt4_widget_colors.set_widget_color(self.current_value_label, STATES['unknown'])
        elif value.get('current'):
            Qt4_widget_colors.set_widget_color(self.current_value_label, STATES['ready'])
        else:
            Qt4_widget_colors.set_widget_color(self.current_value_label, STATES['error'])
        Qt4_widget_colors.set_widget_color(self.state_text_value_label, STATES['ready'])
        if value.get('intens') is None:
            Qt4_widget_colors.set_widget_color(self.intensity_value_label, STATES['unknown'])
        elif value.get('intens'):
            Qt4_widget_colors.set_widget_color(self.intensity_value_label, STATES['ready'])
        else:
            Qt4_widget_colors.set_widget_color(self.intensity_value_label, STATES['error'])
        self.cryo_value_label.setEnabled(True)
        if value.get('cryo') is None:
            self.cryo_value_label.setEnabled(False)
            Qt4_widget_colors.set_widget_color(self.cryo_value_label, STATES['unknown'])
        elif value.get('cryo'):
            Qt4_widget_colors.set_widget_color(self.cryo_value_label, STATES['ready'])
        else:
            Qt4_widget_colors.set_widget_color(self.cryo_value_label, STATES['error'])

    def sizeof_fmt(self, num):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')
   
    def sizeof_num(self, num):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        for x in ['m', unichr(181), 'n']:
            if num > 0.001:
                num *= 1000.0 
                return "%0.1f%s" % (num, x)
            num *= 1000.0
        return "%3.1f%s" % (num, ' n')

    def setColDir(self, dataDir):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        p = '/' + dataDir.split('/')[1]
        dataDir = p
        if os.path.exists(dataDir):
            st = os.statvfs(dataDir)
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            perc = st.f_bavail / float(st.f_blocks)
            txt = 'Total: %s\nFree:  %s (%s)' % (self.sizeof_fmt(total),
                                               self.sizeof_fmt(free),
                                               '{0:.0%}'.format(perc))  
            if free / 2 ** 30 > self['diskThreshold']:
                Qt4_widget_colors.set_widget_color(self.disc_value_label,
                                                   STATES['ready'])
            else:
                Qt4_widget_colors.set_widget_color(self.disc_value_label,
                                                   STATES['error'])
        else:
            txt = 'Not available'
            Qt4_widget_colors.set_widget_color(self.disc_value_label,
                                                   STATES['unknown'])
        self.disc_value_label.setText(txt)

    def temp_hum_changed(self, values, valuesInRange):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        txt = '??? C' if values[0] is None else '%s C' % \
	      str(self['formatString'] % values[0])
        self.temperature_value_label.setText(txt)
        txt = '??? %' if values[1] is None else '%s %%' % \
	      str(self['formatString'] % values[1])
        self.humidity_value_label.setText(txt)	           
        if valuesInRange[0] is None:
            Qt4_widget_colors.set_widget_color(self.temperature_value_label, 
                                               STATES['unknown'])
        elif valuesInRange[0]:
            Qt4_widget_colors.set_widget_color(self.temperature_value_label, 
                                               STATES['ready'])
        else:
            Qt4_widget_colors.set_widget_color(self.temperature_value_label, 
                                               STATES['error'])
        if valuesInRange[1] is None:
            Qt4_widget_colors.set_widget_color(self.humidity_value_label, 
                                               STATES['unknown'])
        elif valuesInRange[1]:
            Qt4_widget_colors.set_widget_color(self.humidity_value_label, 
                                               STATES['ready'])
        else:
            Qt4_widget_colors.set_widget_color(self.humidity_value_label, STATES['error'])
