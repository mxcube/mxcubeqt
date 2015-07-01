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

from PyQt4 import QtGui
from PyQt4 import QtCore

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = 'Qt4_General'


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
        self.minidiff_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QtGui.QGroupBox("Phase", self) 
        self.phase_combobox = QtGui.QComboBox(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_layout = QtGui.QVBoxLayout(self)
        _group_box_layout.addWidget(self.phase_combobox)
        _group_box_layout.setSpacing(0)
        _group_box_layout.setContentsMargins(0, 0, 0, 0)
        self.group_box.setLayout(_group_box_layout)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.phase_combobox.activated.connect(self.change_phase)
 
        # Other ---------------------------------------------------------------
        Qt4_widget_colors.set_widget_color(self.phase_combobox,
                                           Qt4_widget_colors.LIGHT_GREEN)

 
    def propertyChanged(self, property, oldValue, newValue):
        """
        Descript. :
        """
        if property == "mnemonic":
            if self.minidiff_hwobj is not None:
                self.disconnect(self.minidiff_hwobj, QtCore.SIGNAL('minidiffPhaseChanged'), 
                     self.minidiffPhaseChanged)
            self.minidiff_hwobj = self.getHardwareObject(newValue)

            if self.minidiff_hwobj is not None:
                self.connect(self.minidiff_hwobj, QtCore.SIGNAL('minidiffPhaseChanged'), 
                     self.minidiffPhaseChanged)
                self.init_phase_list() 
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)

    def init_phase_list(self):
        """
        Descript. :
        """
        self.phase_combobox.clear()
        phase_list = self.minidiff_hwobj.get_phase_list()
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
        if self.minidiff_hwobj is not None:
            self.minidiff_hwobj.start_set_phase(self.phase_combobox.currentText())

    def minidiffPhaseChanged(self, phase):
        """
        Descript. :
        """
        if (phase.lower() != "unknown" and
            self.phase_combobox.count() > 0):
            self.phase_combobox.setEditText(phase)
            self.phase_combobox.setEnabled(True)
        else:
            self.phase_combobox.setEnabled(False) 
