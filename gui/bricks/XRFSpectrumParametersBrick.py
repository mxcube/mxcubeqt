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
from gui.widgets.xrf_spectrum_parameters_widget import XRFSpectrumParametersWidget

from mx3core import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class XRFSpectrumParametersBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.define_slot("populate_xrf_widget", ({}))

        self.xrf_spectrum_widget = XRFSpectrumParametersWidget(self)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.xrf_spectrum_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def populate_xrf_widget(self, item):
        self.xrf_spectrum_widget.data_path_widget.set_base_image_directory(
            HWR.beamline.session.get_base_image_directory()
        )
        self.xrf_spectrum_widget.data_path_widget.set_base_process_directory(
            HWR.beamline.session.get_base_process_directory()
        )
        self.xrf_spectrum_widget.populate_widget(item)
