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
__category__ = "Beam definition"


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
        _main_groupbox = QGroupBox("Beam focusing", self)
        self.beam_focusing_combo = QComboBox(_main_groupbox)
        self.beam_focusing_combo.setMinimumWidth(100)

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.beam_focusing_combo)
        _main_groupbox_vlayout.addStretch()
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # Qt signal/slot connections ------------------------------------------
        self.beam_focusing_combo.activated.connect(self.change_focus_mode)
 
        # SizePolicies --------------------------------------------------------

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.beam_focusing_combo,
                                           Qt4_widget_colors.LIGHT_GREEN,
                                           QPalette.Button)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == "mnemonic":
            if self.beam_focusing_hwobj is not None:
                self.disconnect(self.beam_focusing_hwobj, 
                                'focusingModeChanged', 
                                self.focus_mode_changed)
            self.beam_focusing_hwobj = self.getHardwareObject(new_value)
            if self.beam_focusing_hwobj is not None:
                self.connect(self.beam_focusing_hwobj, 
                             'focusingModeChanged', 
                             self.focus_mode_changed)
                mode, beam_size = self.beam_focusing_hwobj.get_active_focus_mode()
                self.focus_mode_changed(mode, beam_size)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)
    
    def init_focus_mode_combo(self):
        self.beam_focusing_combo.blockSignals(True)
        self.beam_focusing_combo.clear()
        modes = self.beam_focusing_hwobj.get_focus_mode_names()
        for mode in modes:
            self.beam_focusing_combo.addItem(mode)
        self.beam_focusing_combo.blockSignals(False)

    def change_focus_mode(self):
        focus_mode_name = str(self.beam_focusing_combo.currentText())
        txt = self.beam_focusing_hwobj.get_focus_mode_message(focus_mode_name)

        if len(txt) > 0:
            confDialog = QMessageBox.warning(None, "Focus mode", txt,
                  QMessageBox.Ok, QMessageBox.Cancel)
            if confDialog == QMessageBox.Ok:
                self.beam_focusing_combo.setCurrentIndex(-1)
                self.beam_focusing_hwobj.set_focus_mode(focus_mode_name)
            else:
                self.beam_focusing_combo.setCurrentIndex(\
                    self.beam_focusing_combo.findText(self.active_focus_mode))
        else:
            self.beam_focusing_combo.setCurrentIndex(-1)
            self.beam_focusing_hwobj.set_focus_mode(focus_mode_name)

    def focus_mode_changed(self, new_focus_mode, beam_size):
        self.active_focus_mode = new_focus_mode
        self.beam_focusing_combo.blockSignals(True)
        if self.active_focus_mode is None:
            self.beam_focusing_combo.clear()
            self.setEnabled(False)
            self.beam_focusing_combo.setCurrentIndex(-1) 
        else:
            self.init_focus_mode_combo()
            self.setEnabled(True)
            index = self.beam_focusing_combo.findText(self.active_focus_mode) 
            self.beam_focusing_combo.setCurrentIndex(index)

        self.beam_focusing_combo.blockSignals(False)
