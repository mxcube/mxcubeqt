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

import logging
from os.path import expanduser

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, icons, qt_import

from mxcubecore import HardwareRepository as HWR

from sample_control_brick import SampleControlBrick

__credits__ = ["MXCuBE colaboration"]
__version__ = "0.0.2"
__category__ = "SOLEIL"

class SoleilSampleControlBrick(SampleControlBrick):
    """
    Descript. : SampleControlBrick is used to align and reorient sample
    """

    def create_layout(self):
        _main_layout = qt_import.QHBoxLayout(self)
        _main_layout.addWidget(self.centre_button)
        _main_layout.addWidget(self.accept_button)
        _main_layout.addWidget(self.reject_button)
        _main_layout.addWidget(self.create_line_button)
        _main_layout.addWidget(self.draw_grid_button)
        _main_layout.addWidget(self.auto_focus_button)
        _main_layout.addWidget(self.snapshot_button)
        _main_layout.addWidget(self.refresh_camera_button)
        _main_layout.addWidget(self.visual_align_button)
        _main_layout.addWidget(self.select_all_button)
        _main_layout.addWidget(self.clear_all_button)
        _main_layout.addWidget(self.auto_center_button)
        _main_layout.addWidget(self.realign_button)

        self.snapshot_button.setVisible(False)
        self.select_all_button.setVisible(False)
        self.clear_all_button.setVisible(False)
        self.auto_center_button.setVisible(False)
        _main_layout.addStretch(0)
        _main_layout.setSpacing(0)
        _main_layout.setContentsMargins(0, 0, 0, 0)
        return _main_layout
