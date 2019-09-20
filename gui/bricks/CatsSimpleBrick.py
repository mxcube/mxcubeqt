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

The CatsSimpleBrick.py adds a new property "use_basket_HT", to declare a "High Temperature"
puck. This HT puck has special handling by the Cats sample changer.

"""

import logging

from gui.BaseComponents import BaseWidget
from gui.utils import Colors, QtImport
from gui.utils import sample_changer_helper as sc_helper
from gui.bricks.SampleChangerBrick import SampleChangerBrick, BasketView, VialView
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class CatsStatusView(QtImport.QGroupBox, BaseWidget):
    def __init__(self, parent, brick):

        QtImport.QGroupBox.__init__(self, "State", parent)
        BaseWidget.__init__(self, parent)
        # Graphic elements ----------------------------------------------------
        # self.contents_widget = QGroupBox("Sample Changer State", self)

        self._parent = brick
        self.status_label = QtImport.QLabel("")
        self.status_label.setAlignment(QtImport.Qt.AlignCenter)

        # Layout --------------------------------------------------------------

        _layout = QtImport.QHBoxLayout(self)
        _layout.addWidget(self.status_label)
        _layout.setSpacing(2)
        _layout.setContentsMargins(6, 6, 6, 10)

    def setStatusMsg(self, status):
        self.status_label.setToolTip(status)
        status = status.strip()
        self.setToolTip(status)

    def setState(self, state):

        logging.getLogger().debug("SC StatusView. State changed %s" % str(state))
        color = sc_helper.SC_STATE_COLOR.get(state, None)

        if color is None:
            color = Colors.LINE_EDIT_ORIGINAL

        Colors.set_widget_color(self.status_label, color)

        enabled = sc_helper.SC_STATE_GENERAL.get(state, False)
        self.status_label.setEnabled(enabled)
        state_str = sc_helper.SampleChangerState.tostring(state)
        self.status_label.setText(state_str)
        self._parent.set_status_info("sc", state_str)

    def setIcons(self, *args):
        pass


class CatsSimpleBrick(SampleChangerBrick):
    def __init__(self, *args):

        SampleChangerBrick.__init__(self, *args)

        self.device = None
        self.has_basket_HT = None

        self._pathRunning = None
        self._poweredOn = None

        self.addProperty("use_basket_HT", "boolean", False)

        # display operations widget
        self.operations_widget.show()

        # remove all unwanted controls
        self.switch_to_sample_transfer_button.hide()
        self.test_sample_changer_button.hide()
        self.scan_baskets_view.hide()
        self.current_basket_view.hide()
        self.current_sample_view.hide()
        self.reset_baskets_samples_button.hide()
        self.double_click_loads_cbox.hide()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if HWR.beamline.sample_changer is not None:
                self.disconnect(
                    self.device, "runningStateChanged", self._updatePathRunning
                )
                self.disconnect(
                    self.device, "powerStateChanged", self._updatePowerState
                )

        SampleChangerBrick.property_changed(self, property_name, old_value, new_value)

        if property_name == "mnemonic":
            # load the new hardware object

            if HWR.beamline.sample_changer is not None:
                self.connect(
                    HWR.beamline.sample_changer,
                    "runningStateChanged",
                    self._updatePathRunning,
                )
                self.connect(
                    HWR.beamline.sample_changer,
                    "powerStateChanged",
                    self._updatePowerState,
                )

                self._poweredOn = HWR.beamline.sample_changer.isPowered()
                self._pathRunning = HWR.beamline.sample_changer.isPathRunning()
                self._updateButtons()

        elif property_name == "basketCount":
            # make sure that HT basket is added after Parent class has created all
            # baskets
            if self.has_basket_HT:
                self.add_basket_HT()
        elif property_name == "use_basket_HT":
            if new_value:
                if self.basket_count is not None:
                    self.has_basket_HT = True
                    self.add_basket_HT()
                else:
                    self.has_basket_HT = True

    def build_status_view(self, container):
        return CatsStatusView(container, self)

    def build_operations_widget(self):
        self.buttons_layout = QtImport.QHBoxLayout()
        self.operation_buttons_layout = QtImport.QVBoxLayout()

        self.load_button = QtImport.QPushButton("Load", self)
        self.unload_button = QtImport.QPushButton("Unload", self)
        self.abort_button = QtImport.QPushButton("Abort", self)

        self.load_button.clicked.connect(self.load_selected_sample)
        self.unload_button.clicked.connect(self.unload_selected_sample)
        self.abort_button.clicked.connect(self.abort_mounting)

        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.unload_button)
        self.operation_buttons_layout.addLayout(self.buttons_layout)
        self.operation_buttons_layout.addWidget(self.abort_button)
        self.operations_widget.setLayout(self.operation_buttons_layout)

    def add_basket_HT(self):
        # add one extra basket (next row, first colum) for HT samples. basket
        # index is 100
        ht_basket = BasketView(self.sc_contents_gbox, 100)
        ht_basket.setChecked(False)
        ht_basket.setEnabled(True)
        ht_basket.set_title("HT")
        ht_basket.selectSampleSignal.connect(self.user_select_this_sample)
        self.baskets.append(ht_basket)

        basket_row = int(self.basket_count / self.basket_per_column) + 1
        basket_column = 0
        self.baskets_grid_layout.addWidget(ht_basket, basket_row, basket_column)

    def select_sample(self, basket_no, sample_no):
        if self.has_basket_HT and basket_no == 100:
            basket_no = -1

        SampleChangerBrick.select_sample(self, basket_no, sample_no)

    def infoChanged(self):

        SampleChangerBrick.infoChanged(self)

        if self.has_basket_HT:
            vials = [[VialView.VIAL_BARCODE]] * 10
            self.baskets[-1].set_matrices(vials)

    def sc_state_changed(self, state, previous_state=None):
        logging.getLogger().debug("SC State changed %s" % str(state))
        SampleChangerBrick.sc_state_changed(self, state, previous_state)

        self.state = state
        self._updateButtons()

    def _updatePowerState(self, value):
        self._poweredOn = value
        self._updateButtons()

    def _updatePathRunning(self, value):
        self._pathRunning = value
        self._updateButtons()

    def _updateButtons(self):
        running = self._pathRunning and True or False

        if self.state in [
            sc_helper.SampleChangerState.Ready,
            sc_helper.SampleChangerState.StandBy,
        ]:
            ready = not running
        else:
            ready = False

        poweredOn = (
            self._poweredOn and True or False
        )  # handles init state None as False

        logging.getLogger().debug(
            "updating buttons %s / %s / %s" % (running, poweredOn, self.state)
        )

        if not poweredOn:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = Colors.LIGHT_GRAY
        elif ready:
            logging.getLogger().info("CatsSimpleBrick update buttons (ready)")
            self.load_button.setEnabled(True)
            if HWR.beamline.sample_changer.hasLoadedSample():
                self.unload_button.setEnabled(True)
            else:
                self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = Colors.LIGHT_GRAY
        else:
            logging.getLogger().info("CatsSimpleBrick update buttons (other)")
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(True)
            abort_color = Colors.LIGHT_RED

        self.abort_button.setStyleSheet("background-color: %s;" % abort_color.name())

        # Colors.set_widget_color(self.abort_button, abort_color)

    def load_selected_sample(self):

        basket, vial = self.user_selected_sample
        logging.getLogger("GUI").info("Loading sample: %s / %s" % (basket, vial))

        if basket is not None and vial is not None:
            if basket != 100:
                sample_loc = "%d:%02d" % (basket + 1, vial)
                HWR.beamline.sample_changer.load(sample_loc, wait=False)
            else:
                HWR.beamline.sample_changer.load_ht(vial, wait=False)
                logging.getLogger("GUI").info(
                    "Is an HT sample: idx=%s (not implemented yet)" % (vial)
                )

    def unload_selected_sample(self):
        logging.getLogger("GUI").info("Unloading sample")
        HWR.beamline.sample_changer.unload()

    def abort_mounting(self):
        HWR.beamline.sample_changer._doAbort()


def test_brick(brick):
    brick.property_changed("use_basket_HT", None, True)
    brick.property_changed("singleClickSelection", None, True)
    brick.property_changed("basketCount", None, "9:3")
