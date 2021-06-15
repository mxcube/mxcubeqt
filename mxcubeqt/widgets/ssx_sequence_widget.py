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
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class SSXSequenceWidget(qt_import.QWidget):

    def __init__(self, parent=None, name=None, fl=0):

        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))

        # Internal values -----------------------------------------------------
        self.metadata_dict = {}
        self.chan_config = {}
        self.chan_seq = []
        self.chan_combo_items = []

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _channels_gbox = qt_import.QGroupBox("Channels", self)
        self.chan_table = qt_import.QTableWidget(_channels_gbox)

        self.metadata_gbox = qt_import.QGroupBox("Metadata", self)

        # Layout --------------------------------------------------------------
        _channels_gbox_vlayout = qt_import.QGridLayout(_channels_gbox)
        _channels_gbox_vlayout.addWidget(self.chan_table, 0, 0)
        _channels_gbox_vlayout.setSpacing(0)
        _channels_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        self.metadata_gbox_glayout = qt_import.QGridLayout(self.metadata_gbox)
        self.metadata_gbox_glayout.setSpacing(0)
        self.metadata_gbox_glayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(_channels_gbox)
        _main_vlayout.addWidget(self.metadata_gbox)

        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.chan_table.cellChanged.connect(
             self.chan_table_cell_changed)

        if hasattr(HWR.beamline, "ssx_setup"):
            if HWR.beamline.ssx_setup is not None:
                self.chan_seq_graphics_view = HWR.beamline.ssx_setup.get_graphics_view()
                _channels_gbox_vlayout.addWidget(self.chan_seq_graphics_view, 0, 1, 2, 1)
                self.init_view()
                HWR.beamline.ssx_setup.connect("valueChanged", self.metadata_values_changed)
        _channels_gbox.setCheckable(True)
        _channels_gbox.setChecked(False)

    def init_view(self):
        self.chan_config = HWR.beamline.ssx_setup.get_config()
     
        self.chan_table.blockSignals(True)
        self.chan_table.setColumnCount(3)
        for index, header_text in enumerate(("Name", "Delay", "Length")):
            self.chan_table.setHorizontalHeaderItem(
                index, qt_import.QTableWidgetItem(header_text)
            )
            if index > 0:
                self.chan_table.resizeColumnToContents(index)

        self.chan_table.setRowCount(
            self.chan_config["num_channels"])
        self.chan_seq = [None] * self.chan_config["num_channels"]
        self.chan_table.verticalHeader().setDefaultSectionSize(20)
        self.chan_table.setFixedHeight(20 * (self.chan_config["num_channels"] + 2) + 10)
        
        for index in range(self.chan_config["num_channels"]):
            combo = qt_import.QComboBox()
            combo.activated.connect(self.chan_seq_combo_activated)

            for chan_name in self.chan_config["channels"].keys():
                combo.addItem(chan_name)
            combo.addItem("")

            combo.setCurrentIndex(-1)
            self.chan_table.setCellWidget(index, 0, combo)
            self.chan_combo_items.append(combo)

            for col in (1, 2):
                self.chan_table.setItem(index, col, qt_import.QTableWidgetItem("")) 

            if index < len(self.chan_config["default_seq"]):
                def_chan_item_name = self.chan_config["default_seq"][index]
                combo.setCurrentIndex(combo.findText(def_chan_item_name))
                self.chan_table.setItem(index, 1, qt_import.QTableWidgetItem(
                    str(self.chan_config["channels"][def_chan_item_name][0])))
                self.chan_table.setItem(index, 2, qt_import.QTableWidgetItem(
                    str(self.chan_config["channels"][def_chan_item_name][1])))

        self.chan_table.blockSignals(False)
        self.refresh_chan_sequence()

        self.metadata_dict = HWR.beamline.ssx_setup.get_metadata_dict()
                 
        for index, key in enumerate(self.metadata_dict.keys()):            
            row = index // 2
            value = self.metadata_dict[key]
            metadata_title_ledit = qt_import.QLabel(value["descr"] + ":  ")
            self.metadata_gbox_glayout.addWidget(metadata_title_ledit, row, index % 2 * 2)

            metadata_value_ledit = qt_import.QLineEdit(str(value["value"]))
            metadata_value_ledit.setObjectName(key)
            if value.get("limits"):
                limits = value.get("limits")
                metadata_value_ledit.setValidator(
                    qt_import.QDoubleValidator(
                        limits[0],
                        limits[1],
                        2,
                        metadata_value_ledit
                    )
                )
                tooltip = "%s limits: %s - %s" % (
                    value["descr"],
                    str(limits[0]),
                    str(limits[1])
                )
                metadata_value_ledit.setToolTip(tooltip)
            metadata_value_ledit.textChanged.connect(self.metadata_value_changed)
            self.metadata_gbox_glayout.addWidget(metadata_value_ledit, row, index % 2 * 2 + 1)
            metadata_title_ledit.setDisabled(value.get("read_only", False))
            metadata_value_ledit.setDisabled(value.get("read_only", False))

    def metadata_value_changed(self, value):
        validator = self.sender().validator()
        if validator:
            if validator.validate(value, 0)[0] == qt_import.QValidator.Acceptable:
                HWR.beamline.ssx_setup.set_metadata_item(self.sender().objectName(), value)
                colors.set_widget_color(
                    self.sender(), colors.WHITE, qt_import.QPalette.Base
                )
            else:
                colors.set_widget_color(
                    self.sender(), colors.LINE_EDIT_ERROR, qt_import.QPalette.Base
                )
        else:
            HWR.beamline.ssx_setup.set_metadata_item(self.sender().objectName(), value)
    
    def metadata_values_changed(self, metadata_dict):
        for children in self.metadata_gbox.children():
            for key, value in metadata_dict.items():
                if key == children.objectName():
                    children.setText(str(value["value"]))

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
        HWR.beamline.ssx_setup.set_exp_sequence(self.chan_seq)

    def chan_table_cell_changed(self, row, col):
        self.refresh_chan_sequence()

    def get_chan_item(self, name):
        for item_key in self.chan_config["channels"].keys():
            if str(name) == item_key:
                return self.chan_config["channels"][str(name)]
