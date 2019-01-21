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

import QtImport

from gui.BaseComponents import BaseWidget
from gui.widgets.xrf_spectrum_parameters_widget import XRFSpectrumParametersWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class XRFSpectrumParametersBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.add_property("xrf-spectrum", "string", "")
        self.add_property("session", "string", "/session")

        self.define_slot("populate_xrf_widget", ({}))

        self.session_hwobj = None

        self.xrf_spectrum_widget = XRFSpectrumParametersWidget(self)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.xrf_spectrum_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def populate_xrf_widget(self, item):
        self.xrf_spectrum_widget.data_path_widget._base_image_dir = (
            self.session_hwobj.get_base_image_directory()
        )
        self.xrf_spectrum_widget.data_path_widget._base_process_dir = (
            self.session_hwobj.get_base_process_directory()
        )
        self.xrf_spectrum_widget.populate_widget(item)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "xrf-spectrum":
            self.xrf_spectrum_widget.set_xrf_spectrum_hwobj(
                self.get_hardware_object(new_value)
            )
        elif property_name == "session":
            self.session_hwobj = self.get_hardware_object(new_value)
