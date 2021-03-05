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

from mxcubeqt.utils import Colors, QtImport


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class RadiationDamageModelWidgetLayout(QtImport.QWidget):
    def __init__(self, parent=None, name=None, fl=0):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("RadiationDamageModelWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.rad_damage_widget = QtImport.load_ui_file(
            "radiation_damage_model_widget_layout.ui"
        )

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.rad_damage_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Size policies -------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.languageChange()
        self.setAttribute(QtImport.Qt.WA_WState_Polished)
        Colors.set_widget_color(self, Colors.GROUP_BOX_GRAY)

    def languageChange(self):
        self.setWindowTitle(self.__tr("RadiationDamageModelWidget"))
        self.rad_damage_widget.main_groupbox.setTitle(
            self.__tr("Radiation damage model")
        )
        self.rad_damage_widget.beta_over_gray_label.setText(
            self.__trUtf8(
                "\xce\xb2\xc3\x85\x3c\x73\x75\x70\x3e\x32\x3c\x2f\x73\x75\x70\x3e\x2f\x4d\x47\x79\x3a"
            )
        )
        self.rad_damage_widget.gamma_over_gray_label.setText(
            self.__trUtf8("\xce\xb3\x20\x31\x2f\x4d\x47\x79\x3a")
        )
        self.rad_damage_widget.sensetivity_label.setText(self.__tr("Sensetivity:"))

    def __tr(self, s, c=None):
        return QtImport.QApplication.translate("RadiationDamageModelWidgetLayout", s, c)

    def __trUtf8(self, s, c=None):
        return QtImport.QApplication.translate(
            "RadiationDamageModelWidgetLayout", s, c, QtImport.QApplication.UnicodeUTF8
        )
