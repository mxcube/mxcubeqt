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

"""
Shutter brick provides access to a shutter like device.
Interface is based on the AbstractNState hardware object
"""

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.base_components import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ShutterBrick(BaseWidget):
    """Widget contains state label and two buttons to open and close the shutter"""

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------
        self.add_property("hwobj_shutter", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self.shutter_hwobj = None

        # Internal values -----------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = qt_import.QGroupBox("Shutter", self)
        self.main_groupbox.setAlignment(qt_import.Qt.AlignCenter)
        self.state_label = qt_import.QLabel("<b>unknown</b>", self.main_groupbox)
        self.state_label.setAlignment(qt_import.Qt.AlignCenter)
        self.state_label.setFixedHeight(24)
        colors.set_widget_color(self.state_label, colors.LIGHT_GRAY)
        _button_widget = qt_import.QWidget(self.main_groupbox)

        self.open_button = qt_import.QPushButton(
            icons.load_icon("ShutterOpen"), "Open", _button_widget
        )
        self.close_button = qt_import.QPushButton(
            icons.load_icon("ShutterClose"), "Close", _button_widget
        )

        # Layout --------------------------------------------------------------
        _button_widget_hlayout = qt_import.QHBoxLayout(_button_widget)
        _button_widget_hlayout.addWidget(self.open_button)
        _button_widget_hlayout.addWidget(self.close_button)
        _button_widget_hlayout.setSpacing(2)
        _button_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_gbox_vlayout = qt_import.QVBoxLayout(self.main_groupbox)
        _main_gbox_vlayout.addWidget(self.state_label)
        _main_gbox_vlayout.addWidget(_button_widget)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.open_button.clicked.connect(self.open_button_clicked)
        self.close_button.clicked.connect(self.close_button_clicked)

        # Other ---------------------------------------------------------------

    def open_button_clicked(self):
        """Opens the shutter"""
        self.shutter_hwobj.open()

    def close_button_clicked(self):
        """Closes the shutter"""
        self.shutter_hwobj.close()

    def property_changed(self, property_name, old_value, new_value):
        """Initates the shutter hwobj"""
        if property_name == "hwobj_shutter":
            if self.shutter_hwobj is not None:
                self.disconnect(
                    self.shutter_hwobj, "valueChanged", self.value_changed
                )
            else:
                self.shutter_hwobj = self.get_hardware_object(new_value)
                self.connect(
                    self.shutter_hwobj, "valueChanged", self.value_changed
                )
                self.shutter_hwobj.force_emit_signals()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def value_changed(self, value):
        """Based on the shutter state enables/disables open and close buttons"""
        self.state_label.setText(str(value.name.capitalize()))
        if value in ("UNKOWN", "AUTOMATIC", "DISABLED"):
            colors.set_widget_color(self.state_label, colors.LIGHT_GRAY)
        elif value in ("FAULT", "ERROR"):
            colors.set_widget_color(self.state_label, colors.LIGHT_RED)
        else:
            colors.set_widget_color(self.state_label, colors.LIGHT_GREEN)
        self.open_button.setEnabled(self.shutter_hwobj.is_closed())
        self.close_button.setEnabled(self.shutter_hwobj.is_open())
