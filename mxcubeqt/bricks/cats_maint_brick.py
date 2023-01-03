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

import string
import logging
import sys
import os

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, sample_changer_helper, qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"


class CatsMaintBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        self.add_property("mnemonic", "string", "")
        self.define_slot("setExpertMode", ())

        self.expert_mode = False

        self.widget = qt_import.load_ui_file("catsmaint_widget.ui")

        qt_import.QHBoxLayout(self)
        self.layout().addWidget(self.widget)

        self.widget.btPowerOn.clicked.connect(self.power_on)
        self.widget.btPowerOff.clicked.connect(self.power_off)
        self.widget.btLid1Open.clicked.connect(self.lid1_open)
        self.widget.btLid1Close.clicked.connect(self.lid1_close)
        self.widget.btLid2Open.clicked.connect(self.lid2_open)
        self.widget.btLid2Close.clicked.connect(self.lid2_close)
        self.widget.btLid3Open.clicked.connect(self.lid3_open)
        self.widget.btLid3Close.clicked.connect(self.lid3_close)
        self.widget.btRegulationOn.clicked.connect(self.regulation_set_on)

        self.widget.btOpenTool.clicked.connect(self.tool_open)
        self.widget.btCloseTool.clicked.connect(self.tool_close)
        self.widget.btToolCalib.clicked.connect(self.tool_calibrate)
        self.widget.btMagnetOn.clicked.connect(self.magnet_on)
        self.widget.btMagnetOff.clicked.connect(self.magnet_off)

        # self.widget.btSoak.clicked.connect(self.soak)
        self.widget.btBack.clicked.connect(self.back_traj)
        self.widget.btSafe.clicked.connect(self.safe_traj)
        self.widget.btDry.clicked.connect(self.dry)
        self.widget.btHome.clicked.connect(self.home)

        # self.widget.btRestart.clicked.connect(self.restart)
        self.widget.btResetPutGet.clicked.connect(self.reset_put_get)
        self.widget.btResetMotion.clicked.connect(self.reset_motion)
        self.widget.btMemClear.clicked.connect(self.clear_memory)
        self.widget.btClear.clicked.connect(self.clear_memory)
        self.widget.btMore.clicked.connect(self.command_prompt)

        self.widget.btAbort.clicked.connect(self.abort)
        # self.widget.btPanic.clicked.connect(self.panic)

        self.device = None
        self.state = None
        self.status = None

        self.path_running = None
        self.powered = None
        self.regulation_on = None

        self.lid1_state = False
        self.lid2_state = False
        self.lid3_state = False

        self.tool_state = False

        self.widget.lblMessage.setStyleSheet("background-color: white;")

        self.update_buttons()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.device is not None:
                self.disconnect(self.device, "lid1StateChanged", self.update_lid1_state)
                self.disconnect(self.device, "lid2StateChanged", self.update_lid2_state)
                self.disconnect(self.device, "lid3StateChanged", self.update_lid3_state)
                self.disconnect(
                    self.device, "runningStateChanged", self.update_path_running
                )
                self.disconnect(self.device, "powerStateChanged", self.update_powered)
                self.disconnect(self.device, "messageChanged", self.update_message)
                self.disconnect(
                    self.device, "regulationStateChanged", self.update_regulation
                )
                self.disconnect(self.device, "barcodeChanged", self.update_barcode)
                self.disconnect(self.device, "toolStateChanged", self.update_tool_state)
                self.disconnect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATUS_CHANGED_EVENT,
                    self.update_status,
                )
                self.disconnect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATE_CHANGED_EVENT,
                    self.update_state,
                )

            # load the new hardware object
            self.device = self.get_hardware_object(new_value)
            if self.device is not None:
                self.connect(
                    self.device, "regulationStateChanged", self.update_regulation
                )
                self.connect(self.device, "messageChanged", self.update_message)
                self.connect(self.device, "powerStateChanged", self.update_powered)
                self.connect(
                    self.device, "runningStateChanged", self.update_path_running
                )
                self.connect(self.device, "lid1StateChanged", self.update_lid1_state)
                self.connect(self.device, "lid2StateChanged", self.update_lid2_state)
                self.connect(self.device, "lid3StateChanged", self.update_lid3_state)
                self.connect(self.device, "toolStateChanged", self.update_tool_state)
                self.connect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATUS_CHANGED_EVENT,
                    self.update_status,
                )
                self.connect(
                    self.device,
                    sample_changer_helper.SampleChanger.STATE_CHANGED_EVENT,
                    self.update_state,
                )

    def set_expert_mode(self, expert):
        self.expert_mode = bool(expert)
        self.update_buttons()

    def update_state(self, state):
        logging.getLogger().debug("CATS update state : " + str(state))
        if state != self.state:
            self.state = state
            self.update_buttons()

    def update_status(self, status):
        logging.getLogger().debug("CATS update status : " + str(status))
        if status != self.status:
            self.status = status

    def update_regulation(self, value):
        self.regulation_on = value
        if value:
            light_green = str(colors.LIGHT_GREEN.name())
            self.widget.lblRegulationState.setStyleSheet(
                "background-color: %s;" % light_green
            )
        else:
            light_red = str(colors.LIGHT_RED.name())
            self.widget.lblRegulationState.setStyleSheet(
                "background-color: %s;" % light_red
            )
        self.update_buttons()

    def update_powered(self, value):
        logging.getLogger().debug("CATS update powered : " + str(value))
        self.powered = value
        if value:
            light_green = str(colors.LIGHT_GREEN.name())
            self.widget.lblPowerState.setStyleSheet(
                "background-color: %s;" % light_green
            )
        else:
            light_red = str(colors.LIGHT_RED.name())
            self.widget.lblPowerState.setStyleSheet("background-color: %s;" % light_red)
        self.update_buttons()

    def update_message(self, value):
        logging.getLogger().debug("CATS update message : " + str(value))
        self.widget.lblMessage.setText(str(value))

    def update_barcode(self, value):
        if value is not None and value != "":
            barcode = value
        else:
            barcode = "----"
        logging.getLogger().debug("CATS update barcode : " + str(barcode))
        self.widget.lblMessage.setText(str(value))

    def update_path_running(self, value):
        self.path_running = value
        self.update_buttons()

    def update_lid1_state(self, value):
        self.lid1_state = value
        if self.device is not None and not self.path_running:
            self.widget.btLid1Open.setEnabled(not value)
            self.widget.btLid1Close.setEnabled(value)
        else:
            self.widget.btLid1Open.setEnabled(False)
            self.widget.btLid1Close.setEnabled(False)

    def update_lid2_state(self, value):
        self.lid2_state = value
        if self.device is not None and not self.path_running:
            self.widget.btLid2Open.setEnabled(not value)
            self.widget.btLid2Close.setEnabled(value)
        else:
            self.widget.btLid2Open.setEnabled(False)
            self.widget.btLid2Close.setEnabled(False)

    def update_lid3_state(self, value):
        self.lid3_state = value
        if self.device is not None and not self.path_running:
            self.widget.btLid3Open.setEnabled(not value)
            self.widget.btLid3Close.setEnabled(value)
        else:
            self.widget.btLid3Open.setEnabled(False)
            self.widget.btLid3Close.setEnabled(False)

    def update_tool_state(self, value):
        self.tool_state = value
        if self.device is not None and not self.path_running:
            self.widget.btOpenTool.setEnabled(not value)
            self.widget.btCloseTool.setEnabled(value)
        else:
            self.widget.btOpenTool.setEnabled(False)
            self.widget.btCloseTool.setEnabled(False)

    def update_buttons(self):

        if self.device is None:
            # disable all buttons
            self.widget.boxPower.setEnabled(False)
            self.widget.boxRegulation.setEnabled(False)
            self.widget.boxLid1.setEnabled(False)
            self.widget.boxLid2.setEnabled(False)
            self.widget.boxLid3.setEnabled(False)
            self.widget.lblMessage.setText("")
            self.widget.btAbort.setEnabled(False)
        else:
            self.widget.boxPower.setEnabled(True)
            self.widget.boxRegulation.setEnabled(True)

            ready = not self.path_running
            powered = self.powered and True or False  # handles init state None as False

            if not self.expert_mode:
                self.widget.boxTools.hide()
                self.widget.btMore.hide()
                self.widget.btBarcodeRead.hide()
                self.widget.btBack.hide()
                self.widget.btSafe.hide()
                self.widget.btSafe.hide()
                self.widget.btClear.hide()
            else:
                self.widget.boxTools.show()
                self.widget.btMore.show()
                self.widget.btBarcodeRead.show()
                self.widget.btBack.show()
                self.widget.btSafe.show()
                self.widget.btClear.show()
                self.widget.btMemClear.show()

            # Open for users
            self.widget.btPowerOn.setEnabled(ready and not powered)
            self.widget.btPowerOff.setEnabled(ready and powered)

            if ready:
                color = str(colors.LIGHT_GRAY.name())
                self.widget.btAbort.setEnabled(False)
            else:
                color = str(colors.LIGHT_RED.name())
                self.widget.btAbort.setEnabled(True)
            self.widget.btAbort.setStyleSheet("background-color: %s;" % color)

            self.widget.boxLid1.setEnabled(True)
            self.widget.boxLid2.setEnabled(True)
            self.widget.boxLid3.setEnabled(True)

            self.widget.btClear.setEnabled(ready)
            self.widget.btBack.setEnabled(ready and powered)
            self.widget.btSafe.setEnabled(ready and powered)

            regulOn = self.regulation_on and True or False
            self.widget.btRegulationOn.setEnabled(ready and not regulOn)

            self.update_lid1_state(self.lid1_state)
            self.update_lid2_state(self.lid2_state)
            self.update_lid3_state(self.lid3_state)
            self.update_tool_state(self.tool_state)

    def regulation_set_on(self):
        try:
            if self.device is not None:
                self.device._do_enable_regulation()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def regulation_set_off(self):
        try:
            if self.device is not None:
                self.device._do_disable_regulation()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def power_on(self):
        try:
            if self.device is not None:
                self.device._do_power_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def power_off(self):
        try:
            if self.device is not None:
                self.device._do_power_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid1_open(self):
        try:
            if self.device is not None:
                self.device._do_lid1_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid1_close(self):
        try:
            if self.device is not None:
                self.device._do_lid1_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid2_open(self):
        try:
            if self.device is not None:
                self.device._do_lid2_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid2_close(self):
        try:
            if self.device is not None:
                self.device._do_lid2_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid3_open(self):
        try:
            if self.device is not None:
                self.device._do_lid3_state(True)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def lid3_close(self):
        try:
            if self.device is not None:
                self.device._do_lid3_state(False)
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_open(self):
        try:
            if self.device is not None:
                self.device._do_tool_open()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_close(self):
        try:
            if self.device is not None:
                self.device._do_tool_close()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def tool_calibrate(self):
        try:
            if self.device is not None:
                self.device._do_calibration()  # adds a parameter 2 (for tool) in device
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def magnet_on(self):
        try:
            if self.device is not None:
                self.device._do_magnet_on()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def magnet_off(self):
        try:
            if self.device is not None:
                self.device._do_magnet_off()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def resetError(self):
        try:
            if self.device is not None:
                self.device._do_reset()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def home(self):
        try:
            if self.device is not None:
                self.device._do_home()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def dry(self):
        try:
            if self.device is not None:
                self.device._do_dry_gripper()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def soak(self):
        try:
            if self.device is not None:
                self.device._do_soak()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def back_traj(self):
        try:
            if self.device is not None:
                # self.device._do_back()
                self.device.back_traj()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def safe_traj(self):
        try:
            if self.device is not None:
                # self.device._do_safe()
                self.device.safe_traj()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def abort(self):
        try:
            if self.device is not None:
                self.device._do_abort()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def panic(self):
        try:
            if self.device is not None:
                self.device._do_panic()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def restart(self):
        try:
            if self.device is not None:
                self.device._do_restart()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def reset_motion(self):
        try:
            if self.device is not None:
                self.device._do_reset_motion()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def reset_put_get(self):
        try:
            if self.device is not None:
                self.device._doResetPutGet()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def clear(self):
        try:
            if self.device is not None:
                self.device._doClear()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def clear_memory(self):
        try:
            if self.device is not None:
                self.device._do_reset_memory()
        except BaseException:
            qt_import.QMessageBox.warning(self, "Error", str(sys.exc_info()[1]))

    def command_prompt(self, index):
        self.command_dialog = CatsCommandDialog(self)
        self.command_dialog.set_cats_device(self.device)
        self.command_dialog.show()


class CatsCommandDialog(qt_import.QDialog):

    cmds = [
        "put(mount)",
        "get(un-mount)",
        "getput",
        "get_brcd",
        "getput_brcd",
        "barcode",
        "gotodif",
        "get HT",
        "put HT",
        "getput HT",
    ]

    args = {
        "put(mount)": ["tool", "from_cassette", "from_puck"],
        "get(un-mount)": ["tool"],
        "getput": ["tool", "from_cassette", "from_puck"],
        "get_brcd": ["tool"],
        "getput_brcd": ["tool", "from_cassette", "from_puck"],
        "barcode": [],
        "gotodif": [],
        "get HT": [],
        "put HT": [],
        "getput HT": [],
    }

    def __init__(self, *args):

        qt_import.QDialog.__init__(self, *args)
        layout = qt_import.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.widget = qt_import.load_ui_file("catscommand_dialog.ui")

        layout.addWidget(self.widget)

        self.btSend = self.widget.buttonBox.addButton(
            "Send", qt_import.QDialogButtonBox.ApplyRole
        )
        self.btSend.clicked.connect(self.send_command)

        self.widget.cbCommand.clear()
        self.widget.cbCommand.insertItems(0, self.cmds)
        self.widget.cbCommand.activated.connect(self.command_selected)
        self.widget.buttonBox.rejected.connect(self.rejected)

    def show(self):
        self.widget.cbCommand.setCurrentIndex(2)
        qt_import.QDialog.show(self)

    def set_cats_device(self, device):
        self.device = device

    def command_selected(self, cb_idx):
        logging.getLogger("GUI").info("command selected %s" % cb_idx)

    def build_command(self):
        cmd_str = ""

    def send_command(self):
        cmd = self.widget.leCommand.text()
        logging.getLogger("GUI").info("sending command %s" % cmd)

    def rejected(self):
        logging.getLogger("GUI").info("button rejected")
        self.close()

    def accepted(self):
        logging.getLogger("GUI").info("button accepted")

    def close_me(self):
        pass

    def run_cmd(self):
        pass
