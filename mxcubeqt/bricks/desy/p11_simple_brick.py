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
File: CatsSimpleBrick.py

Description
-------------
The CatsSimpleBrick.py is a simplified version of the SampleChangerBrick3.py

It presents the samples in the same way as SampleChangerBrick3.py. It allows to
select a sample by single clicking on it then perform the Load/Unload and Abort
operations on the Cats sample changer.

"""

import logging

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, qt_import
from mxcubeqt.utils import sample_changer_helper as sc_helper
from mxcubeqt.bricks.sample_changer_brick import SampleChangerBrick, BasketView, VialView, StatusView
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class P11SCStatusView(qt_import.QWidget):

    # statusMsgChangedSignal = qt_import.pyqtSignal(str, qt_import.QColor)
    # resetSampleChangerSignal = qt_import.pyqtSignal()

    def __init__(self, parent, brick):

        qt_import.QWidget.__init__(self, parent)
        self._parent = brick

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.in_expert_mode = False

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots --------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.contents_widget = qt_import.QGroupBox("State", self)
        self.box1 = qt_import.QWidget(self.contents_widget)

        self.status_label = qt_import.QLabel("", self.box1)
        self.status_label.setAlignment(qt_import.Qt.AlignCenter)

        # flags=self.status_label.alignment()|QtCore.Qt.WordBreak
        # self.status_label.setAlignment(flags)

        # Layout --------------------------------------------------------------
        _box1_hlayout = qt_import.QHBoxLayout(self.box1)
        _box1_hlayout.addWidget(self.status_label)
        _box1_hlayout.setSpacing(2)
        _box1_hlayout.setContentsMargins(2, 2, 2, 2)

        _contents_widget_vlayout = qt_import.QVBoxLayout(self.contents_widget)
        _contents_widget_vlayout.addWidget(self.box1)
        _contents_widget_vlayout.setSpacing(2)
        _contents_widget_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.contents_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------


    def set_expert_mode(self, expert):
        pass

    def setStatusMsg(self, status):
        self.status_label.setToolTip(status)
        status = status.strip()
        self.setToolTip(status)

    def setState(self, state):

        color = sc_helper.SC_STATE_COLOR.get(state, None)

        if color is None:
            color = colors.LINE_EDIT_ORIGINAL

        colors.set_widget_color(self.status_label, color)

        enabled = sc_helper.SC_STATE_GENERAL.get(state, False)
        self.status_label.setEnabled(enabled)
        state_str = sc_helper.SampleChangerState.tostring(state)
        self.status_label.setText(state_str)
        self._parent.set_status_info("sc", state_str)

    def setIcons(self, *args):
        pass

class P11SimpleBrick(SampleChangerBrick):
    def __init__(self, *args):

        super(P11SimpleBrick,self).__init__(*args)

        self._powered_on = None
        self.state = sc_helper.SampleChangerState.Ready

        # display operations widget
        self.operations_widget.show()

        # remove all unwanted controls
        self.switch_to_sample_transfer_button.hide()
        self.test_sample_changer_button.hide()
        self.scan_baskets_view.hide()
        self.reset_baskets_samples_button.hide()
        self.double_click_loads_cbox.hide()

        self.current_basket_view.hide()
        #self.current_sample_view.hide()

        if HWR.beamline.sample_changer is not None:
            #self.connect(
                #HWR.beamline.sample_changer,
                #"runningStateChanged",
                #self._updatePathRunning,
            #)
            self.connect(
                HWR.beamline.sample_changer,
                "powerStateChanged",
                self._update_power_state
            )

            self._powered_on = HWR.beamline.sample_changer.is_powered()
            self._update_buttons()

    def build_status_view(self, container):
        return P11SCStatusView(container, self)
        #return StatusView(container)

    def build_operations_widget(self):
        self.buttons_layout = qt_import.QHBoxLayout()
        self.operation_buttons_layout = qt_import.QVBoxLayout()

        self.load_button = qt_import.QPushButton("Load", self)
        self.unload_button = qt_import.QPushButton("Unload", self)
        self.wash_button = qt_import.QPushButton("Wash", self)
        self.abort_button = qt_import.QPushButton("Abort", self)

        self.load_button.clicked.connect(self.load_selected_sample)
        self.unload_button.clicked.connect(self.unload_sample)
        self.wash_button.clicked.connect(self.wash_sample)
        self.abort_button.clicked.connect(self.abort_mounting)

        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.unload_button)
        self.buttons_layout.addWidget(self.wash_button)
        self.operation_buttons_layout.addLayout(self.buttons_layout)
        self.operation_buttons_layout.addWidget(self.abort_button)
        self.operations_widget.setLayout(self.operation_buttons_layout)

    def sc_state_changed(self, state, previous_state=None):
        logging.getLogger().debug("SC State changed %s" % str(state))
        super(P11SimpleBrick, self).sc_state_changed(state, previous_state)

        self.state = state
        self._update_buttons()

    def _update_power_state(self, value):
        self._powered_on = value
        self._update_buttons()

    def _update_buttons(self):
        # running = self._pathRunning and True or False
        running = False

        if self.state in [
            sc_helper.SampleChangerState.Ready,
            sc_helper.SampleChangerState.StandBy,
        ]:
            ready = not running
        else:
            ready = False

        powered_on = (
            self._powered_on and True or False
        )  # handles init state None as False

        logging.getLogger().debug(
            "updating buttons %s / %s / %s" % (running, powered_on, self.state)
        )

        if not powered_on:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.wash_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = colors.LIGHT_GRAY
        elif ready:
            self.load_button.setEnabled(True)
            if HWR.beamline.sample_changer.has_loaded_sample():
                self.unload_button.setEnabled(True)
                self.wash_button.setEnabled(True)
            else:
                self.unload_button.setEnabled(False)
                self.wash_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = colors.LIGHT_GRAY
        else:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.wash_button.setEnabled(False)
            self.abort_button.setEnabled(True)
            abort_color = colors.LIGHT_RED

        self.abort_button.setStyleSheet("background-color: %s;" % abort_color.name())

        # colors.set_widget_color(self.abort_button, abort_color)

    def load_selected_sample(self):
        basket, vial = self.user_selected_sample
        logging.getLogger("GUI").info("Loading sample: %s / %s" % (basket, vial))

        if basket is not None and vial is not None:
             sample_loc = "%d:%d" % (basket, vial)
             HWR.beamline.sample_changer.load(sample_loc, wait=False)

    def unload_sample(self):
        logging.getLogger("GUI").info("Unloading sample")
        HWR.beamline.sample_changer.unload()

    def wash_sample(self):
        logging.getLogger("GUI").info("Washing sample")
        HWR.beamline.sample_changer.wash()


    def abort_mounting(self):
        HWR.beamline.sample_changer._do_abort()


def test_brick(brick):
    brick.property_changed("singleClickSelection", None, True)
    brick.property_changed("basketCount", None, "9:3")
