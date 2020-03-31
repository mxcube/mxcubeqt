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

"""Turret brick

The standard Turret brick.
"""

import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class TurretBrick(BaseWidget):
    """ Brick to handle a Turret.

    So far, 5 possible different positions.
    A QDial to handle it.
    """

    def __init__(self, *args):
        """TurretBrick constructor

        Arguments:
        :params args: 
        """
        super(TurretBrick, self).__init__(*args)

        # Hardware objects ----------------------------------------------------

        self.turret_hwobj = None  # hardware object
        
        # Graphic elements-----------------------------------------------------

        self.frame = QtImport.QGroupBox()
        self.frame_layout = QtImport.QVBoxLayout()
        
        self.dial = QtImport.QDial()
        self.dial.setMinimum(1)
        self.dial.setMaximum(5)
        self.dial.setSingleStep(1)
        self.dial.setNotchesVisible(True)
        
        # Layout --------------------------------------------------------------
        
        self.frame_layout.addWidget(self.dial)
        self.frame.setLayout(self.frame_layout)
        
        self.main_layout = QtImport.QVBoxLayout()
        self.main_layout.addWidget(self.frame, 0, QtImport.Qt.AlignCenter)

        self.setLayout(self.main_layout)

        # Qt signal/slot connections -----------------------------------------
        self.dial.valueChanged.connect(self.value_changed)
        
        # define properties
        self.add_property("mnemonic", "string", "")

    def value_changed(self, new_position):
        """Move turret to new position."""
        self.turret_hwobj.set_value(new_position)
        
    def set_mnemonic(self, mne):
        """set mnemonic."""
        self["mnemonic"] = mne

    def set_turret_object(self, turret_ho_name=None):
        """set turret's hardware object."""
        if self.turret_hwobj is not None:
            
            self.disconnect(self.turret_hwobj, "positionChanged", self.slot_position)
            self.disconnect(self.turret_hwobj, "modeChanged", self.slot_mode)
        
        if turret_ho_name is not None:
            self.turret_hwobj = self.get_hardware_object(turret_ho_name)

        if self.turret_hwobj is not None:
            self.setEnabled(True)
            
            self.connect(self.turret_hwobj, "positionChanged", self.slot_position)
            self.connect(self.turret_hwobj, "modeChanged", self.slot_mode)

            # if self.turret_hwobj.is_ready():
            #     self.slot_position(self.turret_hwobj.get_position())
            #     self.slot_status(self.turret_hwobj.get_state())
            #     self.turret_ready()
            # else:
            #     self.turret_not_ready()

        self.update_gui()

    def slot_position(self, new_pos):
        self.dial.setValue(new_pos)

    def slot_mode(self,new_mode):
        self.mode = new_mode
        
    def turret_ready(self):
        """Set turret enable."""
        self.setEnabled(True)
    
    def turret_not_ready(self):
        """Set turret not enable."""
        self.setEnabled(False)
    
    def property_changed(self, property_name, old_value, new_value):
        """Property changed in GUI designer and when launching app."""
        if property_name == "mnemonic":
                self.set_turret_object(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
    
    def update_gui(self):
        if self.turret_hwobj is not None:
            self.frame.setEnabled(True)
            if self.turret_hwobj.is_ready():
                self.turret_hwobj.update_values()
        else:
            self.frame.setEnabled(False)
