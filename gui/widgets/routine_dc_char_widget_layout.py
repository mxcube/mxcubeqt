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


from gui.utils import QtImport

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class RoutineDCWidgetLayout(QtImport.QWidget):
    def __init__(self, parent=None, name=None, flags=0):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(flags))

        if not name:
            self.setObjectName("RoutineDCWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.min_dose_radio = QtImport.QRadioButton(self)
        self.min_time_radio = QtImport.QRadioButton(self)
        self.dose_time_bgroup = QtImport.QButtonGroup(self)
        self.dose_time_bgroup.addButton(self.min_dose_radio)
        self.dose_time_bgroup.addButton(self.min_time_radio)
        self.dose_limit_cbx = QtImport.QCheckBox(self)
        self.time_limit_cbx = QtImport.QCheckBox(self)
        self.dose_ledit = QtImport.QLineEdit(self)
        self.dose_ledit.setMinimumSize(50, 0)
        self.dose_ledit.setMaximumSize(50, 32767)
        self.time_ledit = QtImport.QLineEdit(self)
        self.time_ledit.setMinimumSize(50, 0)
        self.time_ledit.setMaximumSize(50, 32767)
        self.radiation_damage_cbx = QtImport.QCheckBox(self)

        # Layout --------------------------------------------------------------
        _main_gridlayout = QtImport.QGridLayout(self)
        _main_gridlayout.addWidget(self.min_dose_radio, 0, 0)  # , 2, 1)
        _main_gridlayout.addWidget(self.min_time_radio, 1, 0)
        _main_gridlayout.addWidget(self.dose_limit_cbx, 0, 1)
        _main_gridlayout.addWidget(self.time_limit_cbx, 1, 1)
        _main_gridlayout.addWidget(self.dose_ledit, 0, 2)
        _main_gridlayout.addWidget(self.time_ledit, 1, 2)
        _main_gridlayout.addWidget(self.radiation_damage_cbx, 2, 0, 1, 2)
        _main_gridlayout.setColumnStretch(3, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.languageChange()
        # self.resize(QtCore.QSize(380,114).expandedTo(self.minimumSizeHint()))
        # self.setAttribute(QtCore.Qt.WA_WState_Polished)

    def languageChange(self):
        self.setWindowTitle(self.__tr("RoutineDCWidget"))
        # self.dose_time_bgroup.setTitle(QtGui.QString.null)
        self.min_dose_radio.setText(self.__tr("Use min dose"))
        self.min_time_radio.setText(self.__tr("Use min time"))
        self.dose_limit_cbx.setText(self.__tr("Dose limit MGy:"))
        self.time_limit_cbx.setText(self.__tr("Total time limit (s):"))
        self.radiation_damage_cbx.setText(self.__tr("Account for radiation damage"))

    def __tr(self, s, c=None):
        return QtImport.QApplication.translate("RoutineDCWidgetLayout", s, c)
