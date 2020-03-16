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

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__category__ = "General"


class ImageTrackingStatusBrick(BaseWidget):

    STATES = {
        "unknown": Colors.LIGHT_GRAY,
        "busy": Colors.LIGHT_GREEN,
        "tracking": Colors.LIGHT_GREEN,
        "disabled": Colors.LIGHT_GRAY,
        "error": Colors.LIGHT_RED,
        "ready": Colors.LIGHT_BLUE,
    }

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.image_tracking_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "/image-tracking")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_groupbox = QtImport.QGroupBox("Image tracking", self)
        self.state_label = QtImport.QLabel("<b> </b>", _main_groupbox)
        self.image_tracking_cbox = QtImport.QCheckBox(
            "Enable Adxv image tracking", _main_groupbox
        )
        self.filter_frames_cbox = QtImport.QCheckBox(
            "Filter frames based on Dozor score", _main_groupbox
        )
        self.spot_list_cbox = QtImport.QCheckBox(
            "Indicate spots in ADxV", _main_groupbox
        )

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = QtImport.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.state_label)
        _main_groupbox_vlayout.addWidget(self.image_tracking_cbox)
        _main_groupbox_vlayout.addWidget(self.filter_frames_cbox)
        _main_groupbox_vlayout.addWidget(self.spot_list_cbox)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.image_tracking_cbox.toggled.connect(self.image_tracking_cbox_toggled)
        self.filter_frames_cbox.toggled.connect(self.filter_frames_cbox_toggled)
        self.spot_list_cbox.toggled.connect(self.spot_list_cbox_toggled)

        # Other ---------------------------------------------------------------
        self.state_label.setAlignment(QtImport.Qt.AlignCenter)
        self.state_label.setFixedHeight(24)
        self.state_changed("unknown")
        # self.state_label.setFixedHeight(20)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.image_tracking_hwobj is not None:
                self.disconnect(
                    self.image_tracking_hwobj,
                    "imageTrackingStateChanged",
                    self.image_tracking_state_changed,
                )
                self.disconnect(
                    self.image_tracking_hwobj, "stateChanged", self.state_changed
                )

            self.image_tracking_hwobj = self.get_hardware_object(new_value)

            if self.image_tracking_hwobj is not None:
                self.image_tracking_cbox.blockSignals(True)
                self.image_tracking_cbox.setChecked(
                    self.image_tracking_hwobj.is_tracking_enabled() == True
                )
                self.image_tracking_cbox.blockSignals(False)
                self.connect(
                    self.image_tracking_hwobj,
                    "imageTrackingStateChanged",
                    self.image_tracking_state_changed,
                )
                self.connect(
                    self.image_tracking_hwobj, "stateChanged", self.state_changed
                )
                self.image_tracking_hwobj.update_values()
                self.setEnabled(True)
            else:
                self.setEnabled(False)

        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def image_tracking_cbox_toggled(self, state):
        self.image_tracking_hwobj.set_image_tracking_state(state)

    def filter_frames_cbox_toggled(self, state):
        self.image_tracking_hwobj.set_filter_frames_state(state)

    def image_tracking_state_changed(self, state_dict):
        self.image_tracking_cbox.setChecked(state_dict["image_tracking"])
        self.filter_frames_cbox.setChecked(state_dict["filter_frames"])
        self.spot_list_cbox.setChecked(state_dict["spot_list"])

    def spot_list_cbox_toggled(self, state):
        self.image_tracking_hwobj.set_spot_list_enabled(state)

    def state_changed(self, state, state_label=None):
        color = None
        try:
            color = self.STATES[state]
        except KeyError:
            state = "unknown"
            color = self.STATES[state]
        # if color is None:
        #    color = qt.QWidget.paletteBackgroundColor(self)

        if color:
            Colors.set_widget_color(self.state_label, color)
        if state_label is not None:
            self.state_label.setText("<b>%s</b>" % state_label)
        else:
            self.state_label.setText("<b>%s</b>" % state)
