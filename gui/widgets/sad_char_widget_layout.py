#
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

import QtImport


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class SADWidgetLayout(QtImport.QWidget):

    def __init__(self, parent=None, name=None, flags=0):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(flags))

        if not name:
            self.setObjectName("SADWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.optimised_sad_cbx = QtImport.QCheckBox("Optimised SAD", self)
        self.automatic_resolution_radio = QtImport.QRadioButton(self)
        _optimal_sad_widget = QtImport.QWidget(self)
        self.optimal_sad_radio = QtImport.QRadioButton(
            "Optimal SAD for given resolution:", _optimal_sad_widget
        )
        self.sad_bgroup = QtImport.QButtonGroup(self)
        self.sad_bgroup.addButton(self.automatic_resolution_radio)
        self.sad_bgroup.addButton(self.optimal_sad_radio)
        self.sad_resolution_ledit = QtImport.QLineEdit(_optimal_sad_widget)
        self.sad_resolution_ledit.setMinimumSize(50, 0)
        self.sad_resolution_ledit.setMaximumSize(50, 32767)

        # Layout --------------------------------------------------------------
        _optimal_sad_widget_hlayout = QtImport.QHBoxLayout(_optimal_sad_widget)
        _optimal_sad_widget_hlayout.addWidget(self.optimal_sad_radio)
        _optimal_sad_widget_hlayout.addWidget(self.sad_resolution_ledit)
        _optimal_sad_widget_hlayout.setSpacing(0)
        _optimal_sad_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.optimised_sad_cbx)
        _main_vlayout.addWidget(self.automatic_resolution_radio)
        _main_vlayout.addWidget(_optimal_sad_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        self.automatic_resolution_radio.setText(
            self.trUtf8(
                "\x52\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x20\x73\x65\x6c\x65\x63\x74\x65\x64\x20\x61\x75\x74\x6f\x6d\x61\x74\x69\x63\x61\x6c\x6c\x79\x2c\x20\x72\x6f\x74\x61\x74\x69\x6f\x6e\x20\x69\x6e\x74\x65\x72\x76\x61\x6c\x3a\x20\x33\x36\x30\xc2\xb0"
            )
        )

    def trUtf8(self, s, c=None):
        return QtImport.QApplication.translate("SADWidgetLayout", s, c)
