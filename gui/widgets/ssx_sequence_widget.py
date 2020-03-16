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


from gui.utils import Colors, Icons, QtImport


from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class SSXSequenceWidget(QtImport.QWidget):

    def __init__(self, parent=None, name=None, fl=0):

        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        # Internal values -----------------------------------------------------
        self.chan_config = {}
        self.chan_seq = []
        self.chan_combo_items = []

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_gbox = QtImport.QGroupBox("Channels", self)
        self.chan_table = QtImport.QTableWidget(_main_gbox)

        # Layout --------------------------------------------------------------
        _gbox_vlayout = QtImport.QGridLayout(_main_gbox)
        _gbox_vlayout.addWidget(self.chan_table, 0, 0)
        _gbox_vlayout.setSpacing(0)
        _gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(_main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.chan_table.cellChanged.connect(
             self.chan_table_cell_changed)

        if HWR.beamline.online_processing.ssx_setup is not None:
            self.chan_seq_graphics_view = HWR.beamline.online_processing.ssx_setup.get_graphics_view()
            _gbox_vlayout.addWidget(self.chan_seq_graphics_view, 0, 1, 2, 1)
            self.init_view()
        _main_gbox.setCheckable(True)
        _main_gbox.setChecked(False)

    def init_view(self):
        self.chan_config = HWR.beamline.online_processing.ssx_setup.get_current_chip_config()
     
        self.chan_table.blockSignals(True)
        self.chan_table.setColumnCount(3)
        for index, header_text in enumerate(("Name", "Delay", "Length")):
            self.chan_table.setHorizontalHeaderItem(
                index, QtImport.QTableWidgetItem(header_text)
            )
            if index > 0:
                self.chan_table.resizeColumnToContents(index)

        self.chan_table.setRowCount(
            self.chan_config["num_channels"])
        self.chan_seq = [None] * self.chan_config["num_channels"]
        self.chan_table.setFixedHeight(30 * (self.chan_config["num_channels"] + 1))
        

        for index in range(self.chan_config["num_channels"]):
            combo = QtImport.QComboBox()
            combo.activated.connect(self.chan_seq_combo_activated)

            for chan_name in self.chan_config["channels"].keys():
                combo.addItem(chan_name)
            combo.addItem("")

            combo.setCurrentIndex(-1)
            self.chan_table.setCellWidget(index, 0, combo)
            self.chan_combo_items.append(combo)

            for col in (1, 2):
                self.chan_table.setItem(index, col,  QtImport.QTableWidgetItem("")) 

            if index < len(self.chan_config["default_seq"]):
                def_chan_item_name = self.chan_config["default_seq"][index]
                combo.setCurrentIndex(combo.findText(def_chan_item_name))
                self.chan_table.setItem(index, 1, QtImport.QTableWidgetItem(
                    str(self.chan_config["channels"][def_chan_item_name][0])))
                self.chan_table.setItem(index, 2, QtImport.QTableWidgetItem(
                    str(self.chan_config["channels"][def_chan_item_name][1])))

        self.chan_table.blockSignals(False)
        self.refresh_chan_sequence()

    def chan_seq_combo_activated(self, index):
        self.chan_table.blockSignals(True)
        for row in range(self.chan_config["num_channels"]):
            if self.chan_combo_items[row].currentText():
                # Populate row with default values
                chan_item = self.get_chan_item(self.chan_combo_items[row].currentText())
                self.chan_table.item(row, 1).setText(str(chan_item[0]))
                self.chan_table.item(row, 2).setText(str(chan_item[1])) 
            else:
                # Clear row
                self.chan_table.item(row, 1).setText("")
                self.chan_table.item(row, 2).setText("")
        self.chan_table.blockSignals(False)
        self.refresh_chan_sequence()

    def refresh_chan_sequence(self):
        for index in range(self.chan_config["num_channels"]):
            if self.chan_combo_items[index].currentText():
                name = self.chan_combo_items[index].currentText()
                delay = float(self.chan_table.item(index, 1).text())
                length = float(self.chan_table.item(index, 2).text())
                self.chan_seq[index] = (name, delay, length)
            else:
                self.chan_seq[index] = None
        HWR.beamline.online_processing.ssx_setup.set_channels(self.chan_seq)

    def chan_table_cell_changed(self, row, col):
        self.refresh_chan_sequence()

    def get_chan_item(self, name):
        for item_key in self.chan_config["channels"].keys():
            if str(name) == item_key:
                return self.chan_config["channels"][str(name)]
