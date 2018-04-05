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
from widgets.Qt4_routine_dc_char_widget_layout import RoutineDCWidgetLayout
from widgets.Qt4_sad_char_widget_layout import SADWidgetLayout
from widgets.Qt4_radiation_damage_char_widget_layout import \
     RadiationDamageWidgetLayout


class CharTypeWidget(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent=None, name=None, fl=0):
        """
        Descript. :
        """
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))
        self.setObjectName("char_type_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.charact_type_gbox = QGroupBox(self)

        # Fix the widths of the widgets to make the layout look nicer,
        # and beacuse the qt layout engine is so tremendosly good.
        self.charact_type_gbox.setFixedWidth(800)
        self.charact_type_gbox.setFixedHeight(220)

        self.charact_type_tbox = QToolBox(self.charact_type_gbox)
        self.routine_dc_page = RoutineDCWidgetLayout(self.charact_type_tbox)
        self.sad_page = SADWidgetLayout(self.charact_type_tbox)
        self.rad_damage_page = RadiationDamageWidgetLayout(self.charact_type_tbox)

        self.charact_type_tbox.addItem(self.routine_dc_page, "Routine-DC")
        self.charact_type_tbox.addItem(self.sad_page, "SAD")
        self.charact_type_tbox.addItem(self.rad_damage_page, "Radiation damage")

        # Layout --------------------------------------------------------------
        _charact_type_gbox_vlayout = QVBoxLayout(self.charact_type_gbox)
        _charact_type_gbox_vlayout.addWidget(self.charact_type_tbox)
        _charact_type_gbox_vlayout.addStretch(0)
        _charact_type_gbox_vlayout.setSpacing(0)
        _charact_type_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.charact_type_gbox)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.routine_dc_page.dose_limit_cbx.toggled.connect(\
             self.enable_dose_ledit)
        self.routine_dc_page.time_limit_cbx.toggled.connect(\
             self.enable_time_ledit)
        self.routine_dc_page.dose_time_bgroup.buttonClicked.connect(\
             self._toggle_time_dose)

        # Other ---------------------------------------------------------------
        self._toggle_time_dose(\
             self.routine_dc_page.dose_time_bgroup.checkedId())


    def enable_time_ledit(self, state):
        """
        Descript. :
        """
        self.routine_dc_page.time_ledit.setEnabled(state)

    def enable_dose_ledit(self, state):
        """
        Descript. :
        """
        self.routine_dc_page.dose_ledit.setEnabled(state)

    def _toggle_time_dose(self, index):
        """
        Descript. :
        """
        if index is 1:
            self.routine_dc_page.dose_ledit.setEnabled(False)
            self.routine_dc_page.dose_limit_cbx.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(True)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(True)
            self.enable_time_ledit(self.routine_dc_page.time_limit_cbx.isChecked())
        elif index is 0:
            self.routine_dc_page.dose_limit_cbx.setEnabled(True)
            self.enable_dose_ledit(self.routine_dc_page.dose_limit_cbx.isChecked())
            self.routine_dc_page.time_ledit.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setOn(True)
        elif index is -1:
            self.routine_dc_page.dose_ledit.setEnabled(False)
            self.routine_dc_page.time_ledit.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(False)
            self.routine_dc_page.dose_limit_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(False)

    def toggle_time_dose(self):
        """
        Descript. :
        """
        index = self.routine_dc_page.dose_time_bgroup.checkedId()
        self._toggle_time_dose(index)
