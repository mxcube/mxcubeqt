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
from widgets.Qt4_dc_group_widget import DCGroupWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Task"


class Qt4_DCGBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.dc_group_widget = DCGroupWidget(self)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.dc_group_widget)

        # Qt-Slots
        self.defineSlot("populate_dc_group_widget", ({}))

    def populate_dc_group_widget(self, item):
        """
        Descript. :
        """
        self.dc_group_widget.populate_widget(item)
