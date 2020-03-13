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

"""EMBL specific brick to control Marvin SC"""

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "EMBL"

PUCK_COUNT = 19

class MarvinBrick(BaseWidget):
    """
    MarvinBrick based on BaseWidget
    """

    def __init__(self, *args):
        """
        Main init
        :param args:
        """

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("formatString", "formatString", "#.#")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.status_gbox = QtImport.QGroupBox("Status", self)
        self.mounted_sample_ledit = QtImport.QLineEdit("", self)
        self.sample_detected_ledit = QtImport.QLineEdit("", self)
        self.focus_mode_ledit = QtImport.QLineEdit("", self)

        self.puck_switches_gbox = QtImport.QGroupBox("Puck switches", self)
        self.puck_switches_table = QtImport.QTableWidget(self.puck_switches_gbox)
        self.central_puck_ledit = QtImport.QLineEdit("No center puck",
                                                     self.puck_switches_gbox)

        self.control_gbox = QtImport.QGroupBox("Control", self)
        self.open_lid_button = QtImport.QPushButton("Open lid", self.control_gbox)
        self.close_lid_button = QtImport.QPushButton("Close lid", self.control_gbox)
        self.base_to_center_button = QtImport.QPushButton("Base to center",
                                                          self.control_gbox)
        self.center_to_base_button = QtImport.QPushButton("Center to base",
                                                          self.control_gbox)
        self.dry_gripper_button = QtImport.QPushButton("Dry gripper",
                                                       self.control_gbox)

        self.status_list_gbox = QtImport.QGroupBox("Status list", self)
        self.status_table = QtImport.QTableWidget(self)

        # Layout --------------------------------------------------------------
        _status_gbox_gridlayout = QtImport.QGridLayout(self.status_gbox)
        _status_gbox_gridlayout.addWidget(
            QtImport.QLabel("Mounted sample", self.status_list_gbox), 0, 0
        )
        _status_gbox_gridlayout.addWidget(
            QtImport.QLabel("Sample detected", self.status_list_gbox), 1, 0
        )
        _status_gbox_gridlayout.addWidget(
            QtImport.QLabel("Focus mode", self.status_list_gbox), 2, 0
        )
        _status_gbox_gridlayout.addWidget(self.mounted_sample_ledit, 0, 1)
        _status_gbox_gridlayout.addWidget(self.sample_detected_ledit, 1, 1)
        _status_gbox_gridlayout.addWidget(self.focus_mode_ledit, 2, 1)
        _status_gbox_gridlayout.setSpacing(2)
        _status_gbox_gridlayout.setContentsMargins(0, 0, 0, 0)
        _status_gbox_gridlayout.setColumnStretch(2, 10)

        _puck_switches_gbox_vlayout = QtImport.QHBoxLayout(self.puck_switches_gbox)
        _puck_switches_gbox_vlayout.addWidget(self.puck_switches_table)
        _puck_switches_gbox_vlayout.addWidget(self.central_puck_ledit)
        _puck_switches_gbox_vlayout.setSpacing(2)
        _puck_switches_gbox_vlayout.setContentsMargins(0, 0, 0, 0)

        _status_vbox_layout = QtImport.QVBoxLayout(self.status_list_gbox)
        _status_vbox_layout.addWidget(self.status_table)
        _status_vbox_layout.setSpacing(2)
        _status_vbox_layout.setContentsMargins(0, 0, 0, 0)

        _control_gbox_hlayout = QtImport.QHBoxLayout(self.control_gbox)
        _control_gbox_hlayout.addWidget(self.open_lid_button)
        _control_gbox_hlayout.addWidget(self.close_lid_button)
        _control_gbox_hlayout.addWidget(self.base_to_center_button)
        _control_gbox_hlayout.addWidget(self.center_to_base_button)
        _control_gbox_hlayout.addWidget(self.dry_gripper_button)
        _control_gbox_hlayout.setSpacing(2)
        _control_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.status_gbox)
        _main_vlayout.addWidget(self.puck_switches_gbox)
        _main_vlayout.addWidget(self.control_gbox)
        _main_vlayout.addWidget(self.status_list_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.open_lid_button.clicked.connect(open_lid_clicked)
        self.close_lid_button.clicked.connect(close_lid_clicked)
        self.base_to_center_button.clicked.connect(base_to_center_clicked)
        self.center_to_base_button.clicked.connect(center_to_base_clicked)
        self.dry_gripper_button.clicked.connect(dry_gripper_clicked)

        # Other ---------------------------------------------------------------
        self.mounted_sample_ledit.setFixedWidth(80)
        self.sample_detected_ledit.setFixedWidth(80)
        self.focus_mode_ledit.setFixedWidth(80)

        self.puck_switches_table.setRowCount(1)
        self.puck_switches_table.setColumnCount(PUCK_COUNT)
        self.puck_switches_table.verticalHeader().hide()
        self.puck_switches_table.horizontalHeader().hide()
        self.puck_switches_table.setRowHeight(0, 28)
        self.puck_switches_table.setFixedHeight(28)
        self.puck_switches_table.setShowGrid(True)
        self.puck_switches_table.setFixedWidth(33 * PUCK_COUNT + 4)

        for col_index in range(PUCK_COUNT):
            temp_item = QtImport.QTableWidgetItem(str(col_index + 1))
            temp_item.setFlags(QtImport.Qt.ItemIsEnabled)
            temp_item.setBackground(Colors.WHITE)
            self.puck_switches_table.setItem(0, col_index, temp_item)
            self.puck_switches_table.setColumnWidth(col_index, 33)

        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(
            ["Property", "Description", "Value"]
        )

        self.puck_switches_gbox.setSizePolicy(
            QtImport.QSizePolicy.Preferred, QtImport.QSizePolicy.Fixed
        )
        self.init_tables()
        self.connect(
            HWR.beamline.sample_changer,
            "statusListChanged",
            self.status_list_changed
        )
        self.connect(
            HWR.beamline.sample_changer, "infoDictChanged", self.info_dict_changed
        )

        HWR.beamline.sample_changer.update_values()

    def init_tables(self):
        """
        Inits table with status info
        :return:
        """
        self.status_str_desc = HWR.beamline.sample_changer.get_status_str_desc()
        self.index_dict = {}
        self.status_table.setRowCount(len(self.status_str_desc))
        for row, key in enumerate(self.status_str_desc.keys()):
            temp_item = QtImport.QTableWidgetItem(key)
            self.status_table.setItem(row, 0, temp_item)
            temp_item = QtImport.QTableWidgetItem(self.status_str_desc[key])
            self.status_table.setItem(row, 1, temp_item)
            temp_item = QtImport.QTableWidgetItem("")
            self.status_table.setItem(row, 2, temp_item)
            self.index_dict[key] = row

        self.status_table.resizeColumnToContents(0)
        self.status_table.resizeColumnToContents(1)

    def status_list_changed(self, status_list):
        """
        Updates status table
        :param status_list: list of str
        :return:
        """
        for status in status_list:
            property_status_list = status.split(":")
            if len(property_status_list) < 2:
                continue

            prop_name = property_status_list[0]
            prop_value = property_status_list[1]

            if prop_name in self.status_str_desc:
                self.status_table.item(self.index_dict[prop_name], 2).setText(
                    prop_value
                )

    def info_dict_changed(self, info_dict):
        """
        Updates table with sc info
        :param info_dict: dict
        :return:
        """
        self.mounted_sample_ledit.setText(
            "%s : %s" % (info_dict.get("mounted_puck"), info_dict.get("mounted_sample"))
        )
        if info_dict.get("focus_mode"):
            self.focus_mode_ledit.setText(info_dict.get("focus_mode"))

        for index in range(self.puck_switches_table.columnCount()):
            self.puck_switches_table.item(0, index).setBackground(
                Colors.LIGHT_GRAY
            )
            if info_dict.get("puck_switches", 0) & pow(2, index) > 0:
                self.puck_switches_table.item(0, index).setBackground(
                    Colors.LIGHT_GREEN
                )

        if info_dict.get("centre_puck"):
            Colors.set_widget_color(
                self.central_puck_ledit, Colors.LIGHT_GREEN, QtImport.QPalette.Base
            )
            if info_dict.get("mounted_puck"):
                self.central_puck_ledit.setText(
                    "Center puck: %d" % info_dict.get("mounted_puck")
                )
            else:
                self.central_puck_ledit.setText("No center puck")
            if info_dict.get("mounted_puck", 0) - 1 >= 0:
                self.puck_switches_table.item(
                    0, info_dict.get("mounted_puck", 0) - 1
                ).setBackground(Colors.LIGHT_GREEN)

        else:
            Colors.set_widget_color(
                self.central_puck_ledit, Colors.LIGHT_GRAY, QtImport.QPalette.Base
            )

        if info_dict.get("sample_detected"):
            self.sample_detected_ledit.setText("True")
            Colors.set_widget_color(
                self.sample_detected_ledit, Colors.LIGHT_GREEN, QtImport.QPalette.Base
            )
        else:
            self.sample_detected_ledit.setText("False")
            Colors.set_widget_color(
                self.sample_detected_ledit, Colors.LIGHT_GRAY, QtImport.QPalette.Base
            )

        self.base_to_center_button.setDisabled(info_dict.get("centre_puck", True))
        self.center_to_base_button.setEnabled(info_dict.get("centre_puck", False))
        self.open_lid_button.setDisabled(info_dict.get("lid_opened", True))
        self.close_lid_button.setEnabled(info_dict.get("lid_opened", False))

def open_lid_clicked():
    """
    Opens SC lid
    :return:
    """
    HWR.beamline.sample_changer.open_lid()

def close_lid_clicked():
    """
    Closes SC lid
    :return:
    """
    HWR.beamline.sample_changer.close_lid()

def base_to_center_clicked():
    """
    Calls base-to-center function
    :return:
    """
    HWR.beamline.sample_changer.base_to_center()

def center_to_base_clicked():
    """
    Calls center-to-base function
    :return:
    """
    HWR.beamline.sample_changer.center_to_base()

def dry_gripper_clicked():
    """
    Calls dry-gripper function
    :return:
    """
    HWR.beamline.sample_changer.dry_gripper()
