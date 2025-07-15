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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import icons, colors, qt_import
from mxcubeqt.widgets.matplot_widget import TwoAxisPlotWidget

from mxcubecore import HardwareRepository as HWR
import logging

from PyQt5.QtWidgets import QLineEdit

STATES = {"unknown": colors.GRAY, "ready": colors.LIGHT_BLUE, "error": colors.LIGHT_RED}


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "DESY"

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import qt_import
import logging
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
)


class P11MachineInfoBrick(BaseWidget):
    """Brick to display information about synchrotron and beamline as simple text lines."""

    def __init__(self, *args):
        super().__init__(*args)

        self.current_label_text = qt_import.QLabel(self)
        self.current_label = qt_import.QLabel(self)

        self.message_label_text = qt_import.QLabel(self)
        self.message_label = qt_import.QLabel(self)

        self.lifetime_label_text = qt_import.QLabel(self)
        self.lifetime_label = qt_import.QLabel(self)

        self.energy_label_text = qt_import.QLabel(self)
        self.energy_label = qt_import.QLabel(self)

        # Set default values
        self.current_label_text.setText("Machine current")
        self.current_label.setText("N/A mA")
        self.current_label.setStyleSheet("background-color: #6cb2f8;")
        self.current_label.setAlignment(Qt.AlignCenter)

        self.message_label_text.setText("Machine state")
        self.message_label.setStyleSheet("background-color: #6cb2f8;")
        self.message_label.setText("N/A")
        self.message_label.setAlignment(Qt.AlignCenter)

        self.lifetime_label_text.setText("Lifetime")
        self.lifetime_label.setText("N/A hours")
        self.lifetime_label.setStyleSheet("background-color: #6cb2f8;")
        self.lifetime_label.setAlignment(Qt.AlignCenter)

        self.energy_label_text.setText("Energy")
        self.energy_label.setText("N/A GeV")
        self.energy_label.setStyleSheet("background-color: #6cb2f8;")
        self.energy_label.setAlignment(Qt.AlignCenter)

        # Add labels to layout
        self.main_layout = qt_import.QVBoxLayout(self)

        self.main_layout.addWidget(self.current_label_text)
        self.main_layout.addWidget(self.current_label)

        self.main_layout.addWidget(self.message_label_text)
        self.main_layout.addWidget(self.message_label)

        self.main_layout.addWidget(self.lifetime_label_text)
        self.main_layout.addWidget(self.lifetime_label)

        self.main_layout.addWidget(self.energy_label_text)
        self.main_layout.addWidget(self.energy_label)

    def update_labels_in_ui_thread(self, current_value):
        QMetaObject.invokeMethod(
            self.current_label, "setText", Qt.QueuedConnection, f"{current_value} mA"
        )

    def run(self):
        """Connect the signal from the hardware object."""
        if HWR.beamline.machine_info is not None:
            HWR.beamline.machine_info.valuesChanged.connect(self.set_value)
        else:
            logging.error("Machine info object not available")

    def set_value(self, values_dict):
        """Update the labels in the MachineInfoBrick with machine values."""

        current_value = values_dict.get("current", {}).get("value", "N/A")
        lifetime_value = values_dict.get("lifetime", {}).get("value", "N/A")
        energy_value = values_dict.get("energy", {}).get("value", "N/A")
        message_value = values_dict.get("message", {}).get("value", "N/A")

        # Update the UI labels
        self.current_label.setText(f"{current_value} mA")
        self.lifetime_label.setText(f"{lifetime_value} hours")
        self.energy_label.setText(f"{energy_value} GeV")
        self.message_label.setText(f"{message_value}")

        # Check if machine current is <= 99, change color
        if current_value != "N/A" and float(current_value) <= 99:
            self.set_all_labels_color("salmon")
        else:
            self.reset_all_labels_color()

    def set_all_labels_color(self, color):
        """Set all label backgrounds to the specified color."""
        self.current_label.setStyleSheet(f"background-color: {color};")
        self.message_label.setStyleSheet(f"background-color: {color};")
        self.lifetime_label.setStyleSheet(f"background-color: {color};")
        self.energy_label.setStyleSheet(f"background-color: {color};")

    def reset_all_labels_color(self):
        """Reset all label backgrounds to their default color."""
        default_color = "#6cb2f8"
        self.current_label.setStyleSheet(f"background-color: {default_color};")
        self.message_label.setStyleSheet(f"background-color: {default_color};")
        self.lifetime_label.setStyleSheet(f"background-color: {default_color};")
        self.energy_label.setStyleSheet(f"background-color: {default_color};")
