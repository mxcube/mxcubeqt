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


from mxcubeqt.utils import qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class RadiationDamageWidgetLayout(qt_import.QWidget):

    def __init__(self, parent=None, name=None, flags=0):

        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(flags))

        if not name:
            self.setObjectName("RadiationDamageWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.rad_damage_cbx = qt_import.QCheckBox(self)
        _label_widget = qt_import.QWidget(self)
        self.burn_osc_start_label = qt_import.QLabel(_label_widget)
        self.burn_osc_start_ledit = qt_import.QLineEdit(_label_widget)
        self.burn_osc_start_ledit.setMinimumSize(50, 0)
        self.burn_osc_start_ledit.setMaximumSize(50, 32767)

        _value_widget = qt_import.QWidget(self)
        self.burn_osc_interval_label = qt_import.QLabel(_value_widget)
        self.burn_osc_interval_ledit = qt_import.QLineEdit(_value_widget)
        self.burn_osc_interval_ledit.setMinimumSize(50, 0)
        self.burn_osc_interval_ledit.setMaximumSize(50, 32767)

        # Layout --------------------------------------------------------------
        _label_widget_hlayout = qt_import.QHBoxLayout(self)
        _label_widget_hlayout.addWidget(self.burn_osc_start_label)
        _label_widget_hlayout.addWidget(self.burn_osc_start_ledit)
        _label_widget_hlayout.addStretch(0)
        _label_widget_hlayout.setSpacing(0)
        _label_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        _label_widget.setLayout(_label_widget_hlayout)

        _value_hlayout = qt_import.QHBoxLayout(self)
        _value_hlayout.addWidget(self.burn_osc_interval_label)
        _value_hlayout.addWidget(self.burn_osc_interval_ledit)
        _value_hlayout.addStretch(0)
        _value_hlayout.setSpacing(0)
        _value_hlayout.setContentsMargins(0, 0, 0, 0)
        _value_widget.setLayout(_value_hlayout)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.rad_damage_cbx)
        _main_vlayout.addWidget(_label_widget)
        _main_vlayout.addWidget(_value_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.languageChange()

    def languageChange(self):
        self.setWindowTitle(self.__tr("RadiationDamageWidget"))
        self.rad_damage_cbx.setText(self.__tr("Determine radiation damage parameters"))
        self.burn_osc_start_label.setText(
            self.__tr("Oscillation start for burn strategy:")
        )
        self.burn_osc_interval_label.setText(
            self.__tr("Oscillation interval for burn:")
        )

    def __tr(self, s, c=None):
        return qt_import.QApplication.translate("RadiationDamageWidgetLayout", s, c)
