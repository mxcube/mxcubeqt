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
[Name] ApertureBrick

[Description]
The ApertureBrick displays checkbox with available apertures.
Apertures are allowed according the bam focusing mode.

[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| defAperture  | string | name of the BeamAperture Hardware Object
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]
-----------------------------------------------------------------------
| name            | signals         | functions
-----------------------------------------------------------------------
| aperture_hwobj  | apertureChanged |
-----------------------------------------------------------------------
"""

try:
    unichr
except NameError:
    unichr = chr

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Beam"


class ApertureBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = qt_import.QGroupBox("Aperture", self)
        self.aperture_diameter_combo = qt_import.QComboBox(self.main_gbox)
        self.aperture_diameter_combo.setMinimumWidth(100)
        self.aperture_position_combo = qt_import.QComboBox(self.main_gbox)
        self.aperture_position_combo.setMinimumWidth(100)

        # Layout --------------------------------------------------------------
        _main_gbox_vlayout = qt_import.QVBoxLayout(self.main_gbox)
        _main_gbox_vlayout.addWidget(self.aperture_diameter_combo)
        _main_gbox_vlayout.addWidget(self.aperture_position_combo)
        _main_gbox_vlayout.addStretch()
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        # _main_vlayout.addSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.aperture_diameter_combo.activated.connect(self.change_diameter)
        self.aperture_position_combo.activated.connect(self.change_position)

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        colors.set_widget_color(
            self.aperture_diameter_combo, colors.LIGHT_GREEN, qt_import.QPalette.Button
        )
        colors.set_widget_color(
            self.aperture_position_combo, colors.LIGHT_GREEN, qt_import.QPalette.Button
        )

        self.aperture_diameter_combo.setMinimumWidth(100)
        self.aperture_position_combo.setMinimumWidth(100)

        self.init_aperture()
        self.connect(
                HWR.beamline.beam.aperture, "diameterIndexChanged", self.diameter_changed
        )
        self.connect(
                HWR.beamline.beam.aperture, "valueChanged", self.position_changed
        )

    def change_diameter(self):
        HWR.beamline.beam.aperture.set_diameter_index(
            self.aperture_diameter_combo.currentIndex()
        )

    def change_position(self):
        HWR.beamline.beam.aperture.set_position(self.aperture_position_combo.currentIndex())

    def init_aperture(self):
        aperture_size_list = HWR.beamline.beam.aperture.get_diameter_size_list()
        self.aperture_diameter_combo.clear()
        for aperture_size in aperture_size_list:
            self.aperture_diameter_combo.addItem("%d%s" % (aperture_size, unichr(956)))

        aperture_position_list = HWR.beamline.beam.aperture.get_position_list()
        self.aperture_position_combo.clear()
        for aperture_position in aperture_position_list:
            self.aperture_position_combo.addItem(aperture_position)

        self.aperture_diameter_combo.blockSignals(True)
        self.aperture_diameter_combo.setCurrentIndex(-1)
        self.aperture_diameter_combo.blockSignals(False)

        self.aperture_position_combo.blockSignals(True)
        self.aperture_position_combo.setCurrentIndex(-1)
        self.aperture_position_combo.blockSignals(False)

    def diameter_changed(self, diameter_index, diameter_size):
        self.aperture_diameter_combo.blockSignals(True)
        if diameter_index is None:
            self.aperture_diameter_combo.setEnabled(False)
            self.aperture_diameter_combo.setCurrentIndex(-1)
        else:
            self.aperture_diameter_combo.setEnabled(True)
            self.aperture_diameter_combo.setCurrentIndex(diameter_index)
        self.aperture_diameter_combo.blockSignals(False)

    def position_changed(self, position):
        self.aperture_position_combo.blockSignals(True)
        if position is None:
            # self.aperture_position_combo.setEnabled(False)
            self.aperture_position_combo.setCurrentIndex(-1)
        else:
            # self.aperture_position_combo.setEnabled(True)
            self.aperture_position_combo.setCurrentIndex(
                self.aperture_position_combo.findText(position)
            )
        self.aperture_position_combo.blockSignals(False)
