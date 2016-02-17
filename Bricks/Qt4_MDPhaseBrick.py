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
        _group_box_vlayout = QtGui.QVBoxLayout(self)
        _group_box_vlayout.addWidget(self.phase_combobox)
        _group_box_vlayout.addStretch()
        _group_box_vlayout.setSpacing(0)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)
        self.group_box.setLayout(_group_box_vlayout)

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
                                           Qt4_widget_colors.LIGHT_GREEN,
                                           QtGui.QPalette.Button)
 
    def propertyChanged(self, property, oldValue, newValue):
        """
        Descript. :
        """
        if property == "mnemonic":
            if self.minidiff_hwobj is not None:
                self.disconnect(self.minidiff_hwobj, QtCore.SIGNAL('minidiffPhaseChanged'), 
                     self.phase_changed)
            self.minidiff_hwobj = self.getHardwareObject(newValue)

            if self.minidiff_hwobj is not None:
                self.init_phase_list()
                
                self.connect(self.minidiff_hwobj, QtCore.SIGNAL('minidiffPhaseChanged'), 
                     self.phase_changed)
                self.minidiff_hwobj.update_values()
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

    def phase_changed(self, phase):
        """
        Descript. :
        """
        if (phase.lower() != "unknown" and
            self.phase_combobox.count() > 0):
            #index = self.phase_combobox.findText(phase) 
            #self.phase_combobox.setEditText(phase)
            self.phase_combobox.setCurrentIndex(self.phase_combobox.findText(phase))
            self.phase_combobox.setEnabled(True)
        else:
            self.phase_combobox.setEnabled(False) 
