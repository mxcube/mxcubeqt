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

from PyQt4 import QtGui

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_xrf_scan_parameters_widget import XRFScanParametersWidget


__category__ = 'Task'


class Qt4_XRFScanParametersBrick(BlissWidget):
    """
    Descript. :
    """
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty('xrf-scan', 'string', '')        
        self.addProperty("session", "string", "/session")
        self.session_hwobj = None
        self.xrf_scan_hwobj = None
        
        self.xrf_scan_widget = XRFScanParametersWidget(self)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.xrf_scan_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.defineSlot("populate_xrf_widget", ({}))

    def populate_xrf_widget(self, item):
        """
        Descript. :
        """
        self.xrf_scan_widget.data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.xrf_scan_widget.data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()
        self.xrf_scan_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Overriding BaseComponents.BlissWidget (propertyChanged
                    object) run method.
        """
        if property_name == 'xrf-scan':
            self.xrf_scan_hwobj = self.getHardwareObject(new_value) 	 
            self.xrf_scan_widget.set_xrf_scan_hwobj(\
                 self.getHardwareObject(new_value))
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)

