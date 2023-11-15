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

"""
[Name] BeamSizeBrick

[Description]
The Beam size brick displays beam horizontal and vertical sizes.
Sizes are estimated by related HO

[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| beamSizeDev  | string | name of the BeamSize Hardware Object
| formatString | string | format string for size display (defaults to #.###)
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]
-----------------------------------------------------------------------
| name		| signals         | functions
-----------------------------------------------------------------------
| BeamSize      | beamSizeChanged |
-----------------------------------------------------------------------
"""



from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR

try:
    unichr
except NameError:
    unichr = chr

__credits__ = ["MXCuBE collaboration"]
__category__ = "Beam definition"

import logging
log = logging.getLogger("HWR")


class BeamSizeBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("formatString", "formatString", "#.#")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = qt_import.QGroupBox("Beam size", self)
        hor_label = qt_import.QLabel("Horizontal:", self.main_gbox)
        self.hor_size_ledit = qt_import.QLineEdit(self.main_gbox)
        self.hor_size_ledit.setMaximumWidth(120)
        self.hor_size_ledit.setEnabled(False)
        self.hor_size_ledit.setAlignment(qt_import.Qt.AlignRight)

        ver_label = qt_import.QLabel("Vertical:", self.main_gbox)
        self.ver_size_ledit = qt_import.QLineEdit(self.main_gbox)
        self.ver_size_ledit.setMaximumWidth(120)
        self.ver_size_ledit.setEnabled(False)
        self.ver_size_ledit.setAlignment(qt_import.Qt.AlignRight)

        bold_font = self.hor_size_ledit.font()
        bold_font.setBold(True)
        self.hor_size_ledit.setFont(bold_font)
        self.ver_size_ledit.setFont(bold_font)

        # Layout --------------------------------------------------------------
        _main_gbox_gridlayout = qt_import.QGridLayout(self.main_gbox)
        _main_gbox_gridlayout.addWidget(hor_label, 0, 0)
        _main_gbox_gridlayout.addWidget(self.hor_size_ledit, 0, 1)
        _main_gbox_gridlayout.addWidget(ver_label, 1, 0)
        _main_gbox_gridlayout.addWidget(self.ver_size_ledit, 1, 1)
        _main_gbox_gridlayout.setRowStretch(2, 10)
        _main_gbox_gridlayout.setSpacing(2)
        _main_gbox_gridlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

        self.connect(HWR.beamline.beam, "beamInfoChanged", self.beam_info_changed)
        self.connect(HWR.beamline.beam, "stateChanged", self.beam_info_state_changed)

        log.debug(f"  BEAM INFO connected")
        log.debug(f"     current size is: {HWR.beamline.beam.get_beam_size()}")
        self.beam_info_changed()
        self.beam_info_state_changed()

    def beam_info_changed(self, beam_info=None):
        """
        beam size is in mm. It is displayed in microns
        """
        if beam_info is None:
            beam_info = HWR.beamline.beam.get_beam_info_dict()

        log.debug(f"     current size is: {HWR.beamline.beam.get_beam_size()}")
        log.debug(f"  BEAM INFO updated on beam_info brick: {beam_info}")
        hor_size = beam_info.get("size_x", None)
        ver_size = beam_info.get("size_y", None)

        if hor_size is None:
            self.hor_size_ledit.setText("")
        else:
            size_str = self["formatString"] % (hor_size * 1000)
            self.hor_size_ledit.setText("%s %sm" % (size_str, unichr(956)))
        if ver_size is None:
            self.ver_size_ledit.setText("")
        else:
            # ver_size *= 1000
            size_str = self["formatString"] % (ver_size * 1000)
            self.ver_size_ledit.setText("%s %sm" % (size_str, unichr(956)))
 
    def beam_info_state_changed(self, state=None):
        if state is None:
            try:
                state = HWR.beamline.beam.get_beam_info_state()
            except AttributeError:
                return

        self._update_color(colors.COLOR_STATES[state])

    def _update_color(self, color):
        colors.set_widget_color(self.ver_size_ledit, color, qt_import.QPalette.Base)
        colors.set_widget_color(self.hor_size_ledit, color, qt_import.QPalette.Base)
