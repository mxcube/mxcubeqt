#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.


from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "EMBL"


class Qt4_MarvinBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
	
        # Hardware objects ----------------------------------------------------
        self.sample_changer_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.addProperty('formatString', 'formatString', '#.#')
        self.addProperty('hwobj_sample_changer', '', '/sc-generic')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.status_gbox = QGroupBox('Status', self)
        self.state_ledit = QLabel('Unknown', self)
        self.mounted_sample_ledit = QLineEdit('', self)
        self.sample_detected_ledit = QLineEdit('', self)
        self.last_command_ledit = QLineEdit('', self)
        self.current_command_ledit = QLineEdit('', self) 

        self.puck_switches_gbox = QGroupBox('Puck switches', self)
        self.puck_switches_table = QTableWidget(self)

        self.control_gbox = QGroupBox('Control', self)

        self.status_list_gbox = QGroupBox('Status list', self)
        self.status_table = QTableWidget(self)

        # Layout --------------------------------------------------------------
        _status_gbox_gridlayout = QGridLayout(self.status_gbox)
        _status_gbox_gridlayout.addWidget(QLabel("Status", self.status_list_gbox), 1, 0)
        _status_gbox_gridlayout.addWidget(QLabel("Mounted sample", self.status_list_gbox), 2, 0)
        _status_gbox_gridlayout.addWidget(QLabel("Sample detected", self.status_list_gbox), 3, 0)
        _status_gbox_gridlayout.addWidget(QLabel("Last command", self.status_list_gbox), 4, 0)
        _status_gbox_gridlayout.addWidget(QLabel("Current command", self.status_list_gbox), 5, 0)

        _status_gbox_gridlayout.addWidget(self.state_ledit, 1, 1)
        _status_gbox_gridlayout.addWidget(self.mounted_sample_ledit, 2, 1)
        _status_gbox_gridlayout.addWidget(self.sample_detected_ledit, 3, 1)
        _status_gbox_gridlayout.addWidget(self.last_command_ledit, 4, 1)
        _status_gbox_gridlayout.addWidget(self.current_command_ledit, 5, 1)
        _status_gbox_gridlayout.setSpacing(2)
        _status_gbox_gridlayout.setContentsMargins(0, 0, 0, 0)

        _puck_switches_gbox_vlayout = QVBoxLayout(self.puck_switches_gbox)
        _puck_switches_gbox_vlayout.addWidget(self.puck_switches_table)

        _status_vbox_layout = QVBoxLayout(self.status_list_gbox)
        _status_vbox_layout.addWidget(self.status_table)

        _control_gbox_gridlayout = QGridLayout(self.control_gbox)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.status_gbox)
        _main_vlayout.addWidget(self.puck_switches_gbox)
        _main_vlayout.addWidget(self.control_gbox)
        _main_vlayout.addWidget(self.status_list_gbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        #self.state_ledit.setFixedWidth(100)
        #self.mounted_sample_ledit.setFixedWidth(100)
        #self.sample_detected_ledit.setFixedWidth(100)
        #self.last_command_ledit.setFixedWidth(100)
        #self.current_command_ledit.setFixedWidth(100)

        """
        self.state_ledit.setReadOnly(True)
        self.mounted_sample_ledit.setReadOnly(True)
        self.sample_detected_ledit.setReadOnly(True)
        self.last_command_ledit.setReadOnly(True)
        self.current_command_ledit.setReadOnly(True)
        """

        self.puck_switches_table.setRowCount(1)
        self.puck_switches_table.setColumnCount(16)
        self.puck_switches_table.verticalHeader().hide()
        self.puck_switches_table.horizontalHeader().hide()
        self.puck_switches_table.setRowHeight(0, 20)
        self.puck_switches_table.setFixedHeight(26)
        self.puck_switches_table.setShowGrid(True)

        for col_index in range(16):
            temp_item = QTableWidgetItem(str(col_index + 1))
            temp_item.setFlags(Qt.ItemIsEnabled)
            temp_item.setBackground(Qt4_widget_colors.WHITE)
            self.puck_switches_table.setItem(0, col_index, temp_item)
            self.puck_switches_table.setColumnWidth(col_index, 22)
            self.puck_switches_table.setFixedWidth(22 * 16 + 6)

        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(["Property", "Description", "Value"])

        self.puck_switches_gbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'hwobj_sample_changer':
            if self.sample_changer_hwobj:
                self.disconnect(self.sample_changer_hwobj,
                                'statusListChanged',
                                self.status_list_changed)
                self.disconnect(self.sample_changer_hwobj,
                                'infoDictChanged',
                                self.info_dict_changed)
            self.sample_changer_hwobj = self.getHardwareObject(new_value)
            if self.sample_changer_hwobj:
                self.init_tables()
                self.connect(self.sample_changer_hwobj,
                             'statusListChanged',
                             self.status_list_changed)
                self.connect(self.sample_changer_hwobj,
                             'infoDictChanged',
                             self.info_dict_changed)
                self.sample_changer_hwobj.update_values()
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def init_tables(self):
        self.status_str_desc = self.sample_changer_hwobj.get_status_str_desc()
        self.index_dict = {}
        self.status_table.setRowCount(len(self.status_str_desc))
        for row, key in enumerate(self.status_str_desc.keys()):
            temp_item = QTableWidgetItem(key)
            self.status_table.setItem(row, 0, temp_item)
            temp_item = QTableWidgetItem(self.status_str_desc[key])
            self.status_table.setItem(row, 1, temp_item)
            temp_item = QTableWidgetItem("")
            self.status_table.setItem(row, 2, temp_item)
            self.index_dict[key] = row
            

    def status_list_changed(self, status_list):
        for status in status_list:
            property_status_list = status.split(':')
            if len(property_status_list) < 2:
                continue

            prop_name = property_status_list[0]
            prop_value = property_status_list[1]

            if prop_name in self.status_str_desc:
                self.status_table.item(self.index_dict[prop_name], 2).setText(prop_value)
  
    def info_dict_changed(self, info_dict):
        self.state_ledit.setText(info_dict.get('state', ''))
        self.mounted_sample_ledit.setText("%s : %s" % (info_dict.get('mounted_puck'),
                                                       info_dict.get('mounted_sample')))
        #for index in range(16):
        #    (int(self._puck_switches) & pow(2, basket_index) > 0) or
        #self.crl_value_table.item(0, col_index).\
        #                setBackground(Qt4_widget_colors.LIGHT_GREEN)


        #self.sample_detected_ledit = QLineEdit('', self)
        #self.last_command_ledit = QLineEdit('', self)
        #self.current_command_ledit = QLineEdit('', self)
