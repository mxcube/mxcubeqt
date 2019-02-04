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

"""
BeamAlignBrick
"""

from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class BeamAlignBrick(BaseWidget):

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beam_align_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QtImport.QGroupBox("Beam align", self)
        self.align_button = QtImport.QPushButton("Align", self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_vlayout = QtImport.QVBoxLayout(self.group_box)
        _group_box_vlayout.addWidget(self.align_button)
        _group_box_vlayout.addStretch()
        _group_box_vlayout.setSpacing(0)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.align_button.clicked.connect(self.align_beam_clicked)

        # Other ---------------------------------------------------------------

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            self.beam_align_hwobj = self.get_hardware_object(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def align_beam_clicked(self):
        self.beam_align_hwobj.align_beam_test()
