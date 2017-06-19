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
from widgets.Qt4_energy_scan_parameters_widget import EnergyScanParametersWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Task"


class Qt4_EnergyScanParametersBrick(BlissWidget):
    """
    Descript. :
    """ 
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty('energy-scan', 'string', '')        
        self.addProperty("session", "string", "/session")
        self.session_hwobj = None
        
        # Layout
        self.energy_scan_widget = EnergyScanParametersWidget(self)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.energy_scan_widget)

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        """
        Descript. :
        """
        self.energy_scan_widget.data_path_widget._base_image_dir = \
            self.session_hwobj.get_base_image_directory()
        self.energy_scan_widget.data_path_widget._base_process_dir = \
            self.session_hwobj.get_base_process_directory()
        self.energy_scan_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Overriding BaseComponents.BlissWidget (propertyChanged 
                    object) run method.
        """
        if property_name == 'energy-scan':
            self.energy_scan_widget.set_enegy_scan_hwobj(\
                 self.getHardwareObject(new_value))
        elif property_name == 'session':
            self.session_hwobj = self.getHardwareObject(new_value)
