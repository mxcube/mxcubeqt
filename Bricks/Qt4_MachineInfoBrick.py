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

import BlissFramework
if BlissFramework.get_gui_version() == "QT5":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import *
else:
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import *

from widgets.Qt4_matplot_widget import TwoAxisPlotWidget

from BlissFramework import Qt4_Icons
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
        self.disc_label = None
        self.disc_value_label = None
        self.value_label_list = []

        # Properties (name, type, default value, comment)---------------------- 
        self.addProperty('diskThreshold',
                         'float',
                         200,
                         comment='Disk threshold')
        self.addProperty('maxPlotPoints',
                         'integer',
                         100,
                         comment="Maximal number of plot points")
        self.addProperty('showDiskSize',
                         'boolean',
                         True,
                         comment="Display information about disk size")

        # Properties for hwobj initialization ---------------------------------
        self.addProperty('hwobj_mach_info', 'string', '')

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setColDir', ())
         
        # Graphic elements ----------------------------------------------------
        self.disc_value_label = None

        # Layout --------------------------------------------------------------
        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.setSpacing(1)
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
        if property_name == 'hwobj_mach_info':
            if self.mach_info_hwobj is not None:
                self.disconnect(self.mach_info_hwobj,
                                'valuesChanged',
                                self.set_value)
            self.mach_info_hwobj = self.getHardwareObject(new_value)
            if self.mach_info_hwobj is not None:
                self.setEnabled(True)
                self.connect(self.mach_info_hwobj,
                             'valuesChanged',
                             self.set_value)
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
        if self.graphics_initialized is None:
            for item in values_list:
                temp_widget = CustomInfoWidget(self)
                temp_widget.init_info(item, self['maxPlotPoints'])
                self.value_label_list.append(temp_widget)
                self.main_vlayout.addWidget(temp_widget)
            if self['showDiskSize']:
                self.disc_label = QLabel("Storage disc space", self)
                self.disc_value_label = QLabel(self)
                self.main_vlayout.addWidget(self.disc_label)
                self.main_vlayout.addWidget(self.disc_value_label)
        self.graphics_initialized = True
        for index, value in enumerate(values_list):
            self.value_label_list[index].update_info(value)

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
        if self.disc_label:
            p = '/' + dataDir.split('/')[1]
            dataDir = str(p)
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


class CustomInfoWidget(QWidget):

    def __init__(self, *args):
        """
        Descript. :
        """
        QWidget.__init__(self, *args)

        self.value_plot = None

        self.title_label = QLabel(self)
        self.value_widget = QWidget(self)
        self.value_label = QLabel(self.value_widget)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.history_button = QPushButton(\
             Qt4_Icons.load_icon("LineGraph"), "", self.value_widget)
        self.history_button.hide()
        self.history_button.setFixedWidth(22)
        self.history_button.setFixedHeight(22)

        _value_widget_hlayout = QHBoxLayout(self.value_widget)
        _value_widget_hlayout.addWidget(self.value_label)
        _value_widget_hlayout.addWidget(self.history_button) 
        _value_widget_hlayout.setSpacing(2)
        _value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        self.main_vlayout = QVBoxLayout(self)
        self.main_vlayout.addWidget(self.title_label)
        self.main_vlayout.addWidget(self.value_widget)
        self.main_vlayout.setSpacing(1)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.history_button.clicked.connect(self.open_history_view)

    def init_info(self, info_dict, max_plot_points=None):
        self.title_label.setText(info_dict.get("title", "???"))
        self.history_button.setVisible(info_dict.get("history", False))
        font = self.value_label.font()
        if info_dict.get("font"): 
            font.setPointSize(info_dict.get("font"))
        if info_dict.get("bold"): 
            font.setBold(True)
        self.value_label.setFont(font)

        if info_dict.get("history"):
            self.history_button.show() 
            self.value_plot = TwoAxisPlotWidget(self, realtime_plot=True)
            self.value_plot.hide()
            self.main_vlayout.addWidget(self.value_plot)
            self.value_plot.set_tight_layout()
            self.value_plot.clear()
            self.value_plot.set_max_plot_point(max_plot_points)
        self.update_info(info_dict)

    def update_info(self, info_dict):
        if info_dict.get("value_str"): 
            self.value_label.setText(info_dict.get("value_str"))
        else:
            self.value_label.setText(str(info_dict.get("value"))) 

        if info_dict.get('in_range') is None:
            Qt4_widget_colors.set_widget_color(self.value_label,
                                               Qt4_widget_colors.GRAY)
        elif info_dict.get('in_range') == True:
            Qt4_widget_colors.set_widget_color(self.value_label,
                                               Qt4_widget_colors.LIGHT_BLUE)
        else:
            Qt4_widget_colors.set_widget_color(self.value_label,
                                               Qt4_widget_colors.LIGHT_RED)
        value = info_dict.get('value')
        if type(value) in (int, float) and self.value_plot:
            self.value_plot.add_new_plot_value(value)

    def open_history_view(self):
        self.value_plot.setVisible(not self.value_plot.isVisible())
