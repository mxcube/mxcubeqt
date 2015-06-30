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

"""
[Name] Qt4_MDApertureBrick

[Description]
The Qt4_MDApertureBrick displays checkbox with available apertures. 
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

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_General'


class Qt4_MDApertureBrick(BlissWidget):
    """
    Descript. :
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.aperture_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = QtGui.QGroupBox("Aperture", self)
        self.aperture_cbox = QtGui.QComboBox(self.main_gbox)
        self.aperture_cbox.setMinimumWidth(100)

        # Layout --------------------------------------------------------------
        _main_gbox_gridlayout = QtGui.QGridLayout(self.main_gbox)
        _main_gbox_gridlayout.addWidget(self.aperture_cbox, 0, 0)
        _main_gbox_gridlayout.setSpacing(0)
        _main_gbox_gridlayout.setContentsMargins(0, 0, 0, 0)
        self.main_gbox.setLayout(_main_gbox_gridlayout)  

        _main_vlayout = QtGui.QVBoxLayout()
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------

        self.aperture_cbox.activated.connect(self.change_aperture)
 
        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.aperture_cbox,
                                           Qt4_widget_colors.LIGHT_GREEN)

    def propertyChanged(self, property, oldValue, newValue):
        """
        Descript. :
        """
        if property == "mnemonic":
            if self.aperture_hwobj is not None:
                self.disconnect(self.aperture_hwobj, QtCore.SIGNAL('apertureChanged'), 
                     self.apertureChanged)
            self.aperture_hwobj = self.getHardwareObject(newValue)
            if self.aperture_hwobj is not None:
                self.init_aperture_list()
                self.connect(self.aperture_hwobj, QtCore.SIGNAL('apertureChanged'), 
                     self.apertureChanged)
                self.aperture_hwobj.update_value()
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)
    
    def change_aperture(self):
        """
        Descript. :
        """
        self.aperture_hwobj.set_active_position(self.aperture_cbox.currentItem())

    def init_aperture_list(self):
        aperture_list = self.aperture_hwobj.get_aperture_list()
        self.aperture_cbox.clear()
        for aperture in aperture_list:
            self.aperture_cbox.insertItem(aperture)

    def apertureChanged(self, activePos, gapSize):
        """
        Descript. :
        """
        if activePos is None:
            self.aperture_cbox.setEnabled(False)
        else:
            self.aperture_cbox.setEnabled(True)
            self.aperture_cbox.blockSignals(True)
            self.aperture_cbox.setCurrentItem(activePos)
            self.aperture_cbox.blockSignals(False)

