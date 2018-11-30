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

from widgets.Qt4_xray_imaging_parameters_widget import XrayImagingParametersWidget
from widgets.Qt4_xray_imaging_results_widget import XrayImagingResultsWidget
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Task"


class Qt4_XrayImagingBrick(BlissWidget):
    """
    Descript. :
    """ 
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("hwobj_beamline_setup", "string", "/beamline-setup")

        self._xray_imaging_results_widget = XrayImagingResultsWidget(\
            self, 'xray_imaging_results_widget')
        #self._xray_imaging_parameters_widget = XrayImagingParametersWidget(\
        #    self, 'xray_imaging_parameters_widget')

        # Layout
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self._xray_imaging_results_widget)
        #_main_vlayout.addWidget(self._xray_imaging_parameters_widget)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.setSpacing(2)
        _main_vlayout.addStretch(10)

        # Qt-Slots
        self.defineSlot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self._xray_imaging_results_widget.populate_widget(item)
        #self._xray_imaging_parameters_widget.populate_widget(item)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'hwobj_beamline_setup':
            self._xray_imaging_results_widget.set_beamline_setup_hwobj(
                self.getHardwareObject(new_value))
