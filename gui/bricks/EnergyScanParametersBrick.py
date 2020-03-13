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

from gui.utils import QtImport
from gui.BaseComponents import BaseWidget
from gui.widgets.energy_scan_parameters_widget import EnergyScanParametersWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class EnergyScanParametersBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Layout
        self.energy_scan_widget = EnergyScanParametersWidget(self)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.energy_scan_widget)

        # Qt-Slots
        self.define_slot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self.energy_scan_widget.data_path_widget.set_base_image_directory(
            HWR.beamline.session.get_secondary_image_directory()
        )
        self.energy_scan_widget.data_path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )
        self.energy_scan_widget.populate_widget(item)
