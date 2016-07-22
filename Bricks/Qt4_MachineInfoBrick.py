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
        self.graphics_initialized = None
        self.value_label_list = []

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('diskThreshold', 'float', '200')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setColDir', ())
         
        # Graphic elements ----------------------------------------------------

        # Layout --------------------------------------------------------------
        self.main_vlayout = QtGui.QVBoxLayout(self)
        self.main_vlayout.setSpacing(2)
        self.main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        self.setToolTip("Main information about the beamline")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == 'mnemonic':
            if self.mach_info_hwobj is not None:
                self.disconnect(self.mach_info_hwobj, 'valuesChanged', self.set_value)
            self.mach_info_hwobj = self.getHardwareObject(new_value)
            if self.mach_info_hwobj is not None:
                self.setEnabled(True)
                self.connect(self.mach_info_hwobj, 'valuesChanged', self.set_value)
                self.mach_info_hwobj.update_values() 
            else:
                self.setEnabled(False)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_value(self, values_list):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if not self.graphics_initialized:
            for item in values_list:
                temp_label = QtGui.QLabel(item["title"], self)
                temp_value_label = QtGui.QLabel(self)
                temp_value_label.setAlignment(QtCore.Qt.AlignCenter)
                if "bold" in item:
                    bold_font = temp_value_label.font()
                    bold_font.setPointSize(14)
                    temp_value_label.setFont(bold_font)
                self.main_vlayout.addWidget(temp_label)
                self.main_vlayout.addWidget(temp_value_label)
                self.value_label_list.append(temp_value_label)

            self.disc_label = QtGui.QLabel("Storage disc space", self)
            self.disc_value_label = QtGui.QLabel(self)
            self.main_vlayout.addWidget(self.disc_label)
            self.main_vlayout.addWidget(self.disc_value_label)
            self.graphics_initialized = True

       
        for index in range(len(values_list)):
            self.value_label_list[index].setText(str(values_list[index]['value'])) 
            if values_list[index]['in_range'] is None:
                 Qt4_widget_colors.set_widget_color(\
                     self.value_label_list[index], 
                     STATES['unknown'])
            elif values_list[index]['in_range']:
                 Qt4_widget_colors.set_widget_color(\
                     self.value_label_list[index],
                     STATES['ready'])
            else:
                 Qt4_widget_colors.set_widget_color(\
                     self.value_label_list[index],
                     STATES['error'])


        return

        txt = '??? mA' if values.get("current") is None else '<b>%s</b> mA' % \
	       str(self['formatString'] % abs(values.get("current")))
        self.current_value_label.setText(txt)
        self.state_text_value_label.setText(values.get("stateText"))
        txt = '??? photons/s' if values["flux"] is None else '%1.2e photons/s' % \
	       (values["flux"] * 1.0)   	
        self.intensity_value_label.setText(txt)
        if values.get("cryo") == 1:
            self.cryo_value_label.setText(" In place ")
        elif values.get("cryo") == 0:
            self.cryo_value_label.setText("NOT IN PLACE")
        else:
            self.cryo_value_label.setText("Unknown")

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
