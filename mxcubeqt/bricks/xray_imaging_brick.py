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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.utils import qt_import
from mxcubeqt.base_components import BaseWidget
from mxcubeqt.widgets.xray_imaging_results_widget import XrayImagingResultsWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Task"


class XrayImagingBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self._xray_imaging_results_widget = XrayImagingResultsWidget(
            self, "xray_imaging_results_widget"
        )

        # Layout
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self._xray_imaging_results_widget)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.setSpacing(2)
        _main_vlayout.addStretch(10)

        # Qt-Slots
        self.define_slot("populate_parameter_widget", ({}))

    def populate_parameter_widget(self, item):
        self._xray_imaging_results_widget.populate_widget(item)
