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

import os
import sys

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors


class RadiationDamageModelWidgetLayout(QWidget):
    def __init__(self, parent = None, name = None, fl = 0):
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("RadiationDamageModelWidgetLayout")

        
        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.rad_damage_widget = loadUi(os.path.join(os.path.dirname(__file__),
             "ui_files/Qt4_radiation_damage_model_widget_layout.ui"))

        # Layout --------------------------------------------------------------
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.rad_damage_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Size policies -------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.languageChange()
        self.setAttribute(Qt.WA_WState_Polished) 
        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.GROUP_BOX_GRAY)

    def languageChange(self):
        self.setWindowTitle(self.__tr("RadiationDamageModelWidget"))
        self.rad_damage_widget.main_groupbox.setTitle(self.__tr("Radiation damage model"))
        self.rad_damage_widget.beta_over_gray_label.\
             setText(self.__trUtf8("\xce\xb2\xc3\x85\x3c\x73\x75\x70\x3e\x32\x3c\x2f\x73\x75\x70\x3e\x2f\x4d\x47\x79\x3a"))
        self.rad_damage_widget.gamma_over_gray_label.\
             setText(self.__trUtf8("\xce\xb3\x20\x31\x2f\x4d\x47\x79\x3a"))
        self.rad_damage_widget.sensetivity_label.\
             setText(self.__tr("Sensetivity:"))

    def __tr(self, s, c = None):
        return QApplication.translate("RadiationDamageModelWidgetLayout", s, c)

    def __trUtf8(self, s, c = None):
        return QApplication.translate("RadiationDamageModelWidgetLayout",\
                     s, c, QApplication.UnicodeUTF8)
