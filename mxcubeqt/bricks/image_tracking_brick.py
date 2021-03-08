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

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__category__ = "General"


class ImageTrackingBrick(BaseWidget):

    STATES = {
        "unknown": colors.LIGHT_GRAY,
        "busy": colors.LIGHT_GREEN,
        "tracking": colors.LIGHT_GREEN,
        "disabled": colors.LIGHT_GRAY,
        "error": colors.LIGHT_RED,
        "ready": colors.LIGHT_BLUE,
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
        _main_groupbox = qt_import.QGroupBox("Image tracking", self)
        self.state_label = qt_import.QLabel("<b> </b>", _main_groupbox)
        self.image_tracking_cbox = qt_import.QCheckBox(
            "Enable Adxv image tracking", _main_groupbox
        )
        self.filter_frames_cbox = qt_import.QCheckBox(
            "Filter frames based on Dozor score", _main_groupbox
        )
        self.spot_list_cbox = qt_import.QCheckBox(
            "Indicate spots in ADxV", _main_groupbox
        )

        # Layout --------------------------------------------------------------
        _main_groupbox_vlayout = qt_import.QVBoxLayout(_main_groupbox)
        _main_groupbox_vlayout.addWidget(self.state_label)
        _main_groupbox_vlayout.addWidget(self.image_tracking_cbox)
        _main_groupbox_vlayout.addWidget(self.filter_frames_cbox)
        _main_groupbox_vlayout.addWidget(self.spot_list_cbox)
        _main_groupbox_vlayout.setSpacing(2)
        _main_groupbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.image_tracking_cbox.toggled.connect(self.image_tracking_cbox_toggled)
        self.filter_frames_cbox.toggled.connect(self.filter_frames_cbox_toggled)
        self.spot_list_cbox.toggled.connect(self.spot_list_cbox_toggled)

        # Other ---------------------------------------------------------------
        self.state_label.setAlignment(qt_import.Qt.AlignCenter)
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
                self.image_tracking_hwobj.force_emit_signals()
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
        if "spot_list" in state_dict.keys():
            self.spot_list_cbox.setChecked(state_dict["spot_list"])
        else:
            self.spot_list_cbox.setEnabled(False)

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
            colors.set_widget_color(self.state_label, color)
        if state_label is not None:
            self.state_label.setText("<b>%s</b>" % state_label)
        else:
            self.state_label.setText("<b>%s</b>" % state)
