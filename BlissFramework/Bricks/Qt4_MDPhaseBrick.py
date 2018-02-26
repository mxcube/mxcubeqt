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

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "General"


class Qt4_MDPhaseBrick(BlissWidget):
    """
    Descript. :
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QGroupBox("Phase", self) 
        self.phase_combobox = QComboBox(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_vlayout = QVBoxLayout(self.group_box)
        _group_box_vlayout.addWidget(self.phase_combobox)
        _group_box_vlayout.addStretch()
        _group_box_vlayout.setSpacing(2)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.phase_combobox.activated.connect(self.change_phase)
 
        # Other ---------------------------------------------------------------
        Qt4_widget_colors.set_widget_color(self.phase_combobox,
                                           Qt4_widget_colors.LIGHT_GREEN,
                                           QPalette.Button)
 
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == "mnemonic":
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj,
                                'minidiffPhaseChanged', 
                                self.phase_changed)
            self.diffractometer_hwobj = self.getHardwareObject(new_value)

            if self.diffractometer_hwobj is not None:
                self.init_phase_list()
                
                self.connect(self.diffractometer_hwobj,
                             'minidiffPhaseChanged', 
                             self.phase_changed)
                self.diffractometer_hwobj.update_values()
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def init_phase_list(self):
        """
        Descript. :
        """
        self.phase_combobox.clear()
        phase_list = self.diffractometer_hwobj.get_phase_list()
        if len(phase_list) > 0:
           for phase in phase_list:
               self.phase_combobox.addItem(phase)           
           self.setEnabled(True)
        else:
           self.setEnabled(False)
    
    def change_phase(self):
        """
        Descript. :
        """
        if self.diffractometer_hwobj is not None:
            self.diffractometer_hwobj.set_phase(self.phase_combobox.currentText(), timeout=None)

    def phase_changed(self, phase):
        """
        Descript. :
        """
        if (phase.lower() != "unknown" and
            self.phase_combobox.count() > 0):
            #index = self.phase_combobox.findText(phase) 
            #self.phase_combobox.setEditText(phase)
            self.phase_combobox.setCurrentIndex(self.phase_combobox.findText(phase))
        else:
            self.phase_combobox.setCurrentIndex(-1) 
