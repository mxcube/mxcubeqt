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


__category__ = 'General'


class Qt4_BeamFocusingBrick(BlissWidget):
    """
    Descript. :
    """
 
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beam_focusing_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = QtGui.QGroupBox("Beam focusing", self)
        self.beam_focusing_combo = QtGui.QComboBox(_main_groupbox)
        self.beam_focusing_combo.setMinimumWidth(100)

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QtGui.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.beam_focusing_combo)
        _main_groupbox_vlayout.addStretch()
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.beam_focusing_combo.activated.connect(self.change_focus_mode)
 
        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.beam_focusing_combo,
                                           Qt4_widget_colors.LIGHT_GREEN,
                                           QtGui.QPalette.Button)
        self.setEnabled(False)

    def propertyChanged(self, property, oldValue, newValue):
        """
        Descript. :
        """
        if property == "mnemonic":
            if self.beam_focusing_hwobj is not None:
                self.disconnect(self.beam_focusing_hwobj, 
                                QtCore.SIGNAL('definerPosChanged'), 
                                self.focus_mode_changed)
            self.beam_focusing_hwobj = self.getHardwareObject(newValue)
            if self.beam_focusing_hwobj is not None:
                self.connect(self.beam_focusing_hwobj, 
                             QtCore.SIGNAL('definerPosChanged'), 
                             self.focus_mode_changed)
                self.setEnabled(True) 
                self.focus_mode_changed(self.beam_focusing_hwobj.get_active_focus_mode(), None)
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)
    
    def init_focus_mode_combo(self):
        self.beam_focusing_combo.blockSignals(True)
        self.beam_focusing_combo.clear()
        self.beam_focusing_combo.setEnabled(False)
        modes = self.beam_focusing_hwobj.get_focus_mode_names()
        if len(modes) > 0:
            for m in modes:
                self.beam_focusing_combo.addItem(m)
        self.beam_focusing_combo.blockSignals(False)

    def change_focus_mode(self):
        focus_mode_name = str(self.beam_focusing_combo.currentText())
        txt = self.beam_focus_hwobj.get_focus_mode_message(focus_mode_name)

        return
        if len(txt) > 0:
            confDialog = QtGui.QMessageBox.warning(None, "Focus mode", txt,
                  QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
            if confDialog == QtGui.QMessageBox.Ok:
                self.beam_focus_hwobj.set_focus_mode(focus_mode_name)
            else:
                self.beam_focusing_combo.setCurrentText(self.active_focus_mode)
        else:
            self.beam_focus_hwobj.set_focus_mode(focus_mode_name)

    def focus_mode_changed(self, new_focus_mode, beam_size):
        print 111, new_focus_mode, beam_size
        self.active_focus_mode = new_focus_mode
        self.beam_focusing_combo.blockSignals(True)
        if self.active_focus_mode is None:
            self.beam_focusing_combo.clear()
            self.beam_focusing_combo.setEnabled(False)
            self.beam_focusing_combo.setCurrentIndex(-1) 
        else:
            self.init_focus_mode_combo()
            self.beam_focusing_combo.setEnabled(True)
            index = self.beam_focusing_combo.findData(self.active_focus_mode) 
            self.beam_focusing_combo.setCurrentIndex(index)

        self.beam_focusing_combo.blockSignals(False)
