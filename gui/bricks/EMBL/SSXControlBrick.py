#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software
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

import os
import sys
import unicodedata
from decimal import Decimal

import HWR.beamline

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class SSXControlBrick(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.ssx_control_hwobj = None

        # Internal values -----------------------------------------------------
        self.current_chip_config = None
        self.chip_file_dir = ""
        self.chip_filenames_list = []
        self.shortlist_dir = ""

        # Properties ----------------------------------------------------------

        # Properties to initialize hardware objects --------------------------
        self.add_property("hwobj_ssx_control", "string", "")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.ssx_widget_layout = QtImport.load_ui_file("ssx_control_widget_layout.ui")

        # Layout --------------------------------------------------------------
        _main_layout = QtImport.QVBoxLayout(self)
        _main_layout.addWidget(self.ssx_widget_layout)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.ssx_widget_layout.start_button.clicked.connect(self.start_experiment)
        self.ssx_widget_layout.chip_file_dir_browse_button.clicked.connect(
            self.get_chip_file_directory
        )
        self.ssx_widget_layout.shortlist_dir_browse_button.clicked.connect(
            self.get_shortlist_directory
        )
        self.ssx_widget_layout.save_chip_data_button.clicked.connect(
            self.save_chip_data
        )
        self.ssx_widget_layout.create_shortlist_button.clicked.connect(
            self.create_short_list
        )
        self.ssx_widget_layout.enable_all_button.clicked.connect(self.enable_all)
        self.ssx_widget_layout.disable_all_button.clicked.connect(self.disable_all)
        self.ssx_widget_layout.color_table.itemSelectionChanged.connect(
            self.change_cell_color
        )
        self.ssx_widget_layout.quarter_density_checkbox.stateChanged.connect(
            self.quarter_density_enabled
        )
        self.ssx_widget_layout.quarter_density_checkbox.setEnabled(False)
        self.ssx_widget_layout.meandering_checkbox.stateChanged.connect(
            self.meandering_enabled
        )

        # Other ---------------------------------------------------------------
        self.ssx_widget_layout.crystal_h_pitch_spinbox.valueChanged.connect(
            self.crystal_h_pitch_changed
        )
        self.ssx_widget_layout.crystal_v_pitch_spinbox.valueChanged.connect(
            self.crystal_v_pitch_changed
        )
        self.ssx_widget_layout.comp_h_pitch_spinbox.valueChanged.connect(
            self.comp_h_pitch_changed
        )
        self.ssx_widget_layout.comp_v_pitch_spinbox.valueChanged.connect(
            self.comp_v_pitch_changed
        )
        self.ssx_widget_layout.num_crystal_h_spinbox.valueChanged.connect(
            self.num_crystal_h_changed
        )
        self.ssx_widget_layout.num_crystal_v_spinbox.valueChanged.connect(
            self.num_crystal_v_changed
        )
        self.ssx_widget_layout.num_comp_h_spinbox.valueChanged.connect(
            self.num_comp_h_changed
        )
        self.ssx_widget_layout.num_comp_v_spinbox.valueChanged.connect(
            self.num_copm_v_changed
        )

        self.ssx_widget_layout.meandering_checkbox.setEnabled(False)

        # connect exposures per feature
        self.ssx_widget_layout.exp_per_feature_spinbox.valueChanged[unicode].connect(
            self.set_exposures_per_feature
        )
        # show names and one column at exposures per feature
        self.ssx_widget_layout.dg_channels_table.setRowCount(4)
        self.ssx_widget_layout.dg_channels_table.setColumnCount(1)
        # headers names
        self.ssx_widget_layout.dg_channels_table.setVerticalHeaderLabels(
            QtImport.QString("Detector;Excitation;Aux1;Aux2").split(";")
        )
        # set first column of checkboxes
        dg_channels_list = []

        for row in range(0, 4):
            checkbox_item = QtImport.QTableWidgetItem()
            checkbox_item.setFlags(
                QtImport.Qt.ItemIsUserCheckable | QtImport.Qt.ItemIsEnabled
            )
            checkbox_item.setCheckState(QtImport.Qt.Unchecked)
            dg_channels_list.append(checkbox_item)
            self.ssx_widget_layout.dg_channels_table.setItem(row, 0, checkbox_item)

        # set a color table with 3 by 3 cells
        self.ssx_widget_layout.color_table.setRowCount(3)
        self.ssx_widget_layout.color_table.setColumnCount(3)
        # set min size of cells
        self.ssx_widget_layout.color_table.horizontalHeader().setDefaultSectionSize(25)
        self.ssx_widget_layout.color_table.verticalHeader().setDefaultSectionSize(25)
        # table is non editable
        self.ssx_widget_layout.color_table.setEditTriggers(
            QtImport.QAbstractItemView.NoEditTriggers
        )
        # fill the table with empty items
        for row in range(0, 3):
            for column in range(0, 3):
                self.ssx_widget_layout.color_table.setItem(
                    row, column, QtImport.QTableWidgetItem()
                )
                self.ssx_widget_layout.color_table.item(row, column).setBackground(
                    Colors.GREEN
                )

        # connect scan rate
        self.ssx_widget_layout.scan_rate_ledit.textEdited.connect(
            self.scan_rate_text_changed
        )

    def property_changed(self, property_name, old_value, new_value):
        """
        Defines the behaviour
        :param property_name: str
        :param old_value: value
        :param new_value: value
        :return:
        """
        if property_name == "hwobj_ssx_control":
            self.ssx_control_hwobj = self.get_hardware_object(new_value)
            self.update_chip_config()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def update_chip_config(self):
        self.current_chip_config = (
            HWR.beamline.online_processing.ssx_setup.get_current_chip_config()
        )
        self.ssx_widget_layout.chip_template_list.blockSignals(True)
        self.ssx_widget_layout.chip_template_list.addItems(HWR.beamline.online_processing.ssx_setup.get_chip_config_str_list())
        self.ssx_widget_layout.chip_template_list.setCurrentRow(HWR.beamline.online_processing.ssx_setup.get_current_chip_index())
        self.ssx_widget_layout.chip_template_list.blockSignals(False)

        self.ssx_widget_layout.crystal_h_pitch_spinbox.blockSignals(True)
        self.ssx_widget_layout.crystal_v_pitch_spinbox.blockSignals(True)
        self.ssx_widget_layout.comp_h_pitch_spinbox.blockSignals(True)
        self.ssx_widget_layout.comp_v_pitch_spinbox.blockSignals(True)
        self.ssx_widget_layout.num_crystal_h_spinbox.blockSignals(True)
        self.ssx_widget_layout.num_crystal_v_spinbox.blockSignals(True)
        self.ssx_widget_layout.num_comp_h_spinbox.blockSignals(True)
        self.ssx_widget_layout.num_comp_v_spinbox.blockSignals(True)

        self.ssx_widget_layout.crystal_h_pitch_spinbox.setValue(self.current_chip_config["crystal_h_pitch"])
        self.ssx_widget_layout.crystal_v_pitch_spinbox.setValue(self.current_chip_config["crystal_v_pitch"])
        self.ssx_widget_layout.comp_h_pitch_spinbox.setValue(self.current_chip_config["comp_h_pitch"])
        self.ssx_widget_layout.comp_v_pitch_spinbox.setValue(self.current_chip_config["comp_v_pitch"])
        self.ssx_widget_layout.num_crystal_h_spinbox.setValue(self.current_chip_config["num_crystal_h"])
        self.ssx_widget_layout.num_crystal_v_spinbox.setValue(self.current_chip_config["num_crystal_v"])
        self.ssx_widget_layout.num_comp_h_spinbox.setValue(self.current_chip_config["num_comp_h"])
        self.ssx_widget_layout.num_comp_v_spinbox.setValue(self.current_chip_config["num_comp_v"])

        self.ssx_widget_layout.crystal_h_pitch_spinbox.blockSignals(False)
        self.ssx_widget_layout.crystal_v_pitch_spinbox.blockSignals(False)
        self.ssx_widget_layout.comp_h_pitch_spinbox.blockSignals(False)
        self.ssx_widget_layout.comp_v_pitch_spinbox.blockSignals(False)
        self.ssx_widget_layout.num_crystal_h_spinbox.blockSignals(False)
        self.ssx_widget_layout.num_crystal_v_spinbox.blockSignals(False)
        self.ssx_widget_layout.num_comp_h_spinbox.blockSignals(False)
        self.ssx_widget_layout.num_comp_v_spinbox.blockSignals(False)

    def enable_all(self):
        for row in range(0, self.ssx_widget_layout.color_table.rowCount()):
            for column in range(0, self.ssx_widget_layout.color_table.columnCount()):
                self.ssx_widget_layout.color_table.item(row, column).setBackground(
                    Colors.GREEN
                )

    # set all cells to red
    def disable_all(self):
        for row in range(0, self.ssx_widget_layout.color_table.rowCount()):
            for column in range(0, self.ssx_widget_layout.color_table.columnCount()):
                self.ssx_widget_layout.color_table.item(row, column).setBackground(
                    Colors.RED
                )

    # change cell color
    def change_cell_color(self):
        cell = self.ssx_widget_layout.color_table.selectedItems()[0]

        # check cell color
        if cell.background().color() == Colors.GREEN:
            cell.setBackground(Colors.RED)
        else:
            cell.setBackground(Colors.GREEN)

    # opens a folder with chip files
    def get_chip_file_directory(self):
        self.chip_file_dir = QtImport.QFileDialog.getExistingDirectory(
            self, "Select chip files folder"
        )
        self.ssx_widget_layout.chip_file_dir_ledit.setText(self.chip_file_dir)
        self.update_found_chip_files()
        self.ssx_control_hwobj.create_descriptors_list()

    # displays chip files on the user page with ability to choose them
    def update_found_chip_files(self):
        self.chip_filenames_list = os.listdir(
            self.chip_file_dir
        )  # list of all chip files

        # put chip files into chipFile_list
        self.chip_files_listwidget = QtImport.QListWidget(
            self.ssx_widget_layout.chip_file_list
        )
        self.chip_files_listwidget.addItems(self.chip_filenames_list)

        # add connection to the chipFiles_widget
        self.chip_files_listwidget.itemClicked.connect(self.chip_selected)

    # gives the name of the chip file and calls function to fill the chip data
    def chip_selected(self):
        self.file_name = self.chip_files_listwidget.currentItem().text()
        self.fill_chip_data(self.file_name)

        # creates the corresponding color table
        self.ssx_widget_layout.color_table.setRowCount(
            self.template.num_comp_h_spinbox.value()
        )
        self.ssx_widget_layout.color_table.setColumnCount(
            self.template.num_comp_v_spinbox.value()
        )
        # fill the table with empty items
        for row in range(0, self.ssx_widget_layout.color_table.rowCount()):
            for col in range(0, self.ssx_widget_layout.color_table.columnCount()):
                self.ssx_widget_layout.color_table.setItem(
                    row, col, QtImport.QTableWidgetItem()
                )
                self.ssx_widget_layout.color_table.item(row, col).setBackground(
                    Colors.GREEN
                )

    # fill the chip data
    def fill_chip_data(self, file_name):
        f = open(chip_file_dir + "/" + file_name, "r")
        file_content = f.readlines()

        # set chip data values into chip data fields
        text_line_comma = file_content[1].split('=')[1]
        text_line_dot = text_line_comma.replace(',', '.')
        self.template.crystal_h_pitch_spinbox.setValue(float(text_line_dot))

        text_line_comma = file_content[2].split('=')[1]
        text_line_dot = text_line_comma.replace(',', '.')
        self.template.crystal_v_pitch_spinbox.setValue(float(text_line_dot))

        text_line_comma = file_content[3].split('=')[1]
        text_line_dot = text_line_comma.replace(',', '.')
        self.template.comp_h_pitch_spinbox.setValue(float(text_line_dot))

        text_line_comma = file_content[4].split('=')[1]
        text_line_dot = text_line_comma.replace(',', '.')
        self.template.comp_v_pitch_spinbox.setValue(float(text_line_dot))

        self.template.num_crystal_h_spinbox.setValue(int(file_content[5].split('=')[1]))
        self.template.num_crystal_v_spinbox.setValue(int(file_content[6].split('=')[1]))
        self.template.num_comp_h_spinbox.setValue(int(file_content[7].split('=')[1]))
        self.template.num_comp_v_spinbox.setValue(int(file_content[8].split('=')[1]))

        # calls function to fill the table
        self.update_table()

        f.close()

    # sets the folder to save short list
    def get_shortlist_directory(self):
        self.shortlist_dir = QtImport.QFileDialog.getExistingDirectory(
            self, "Select chip files folder"
        )
        self.ssx_widget_layout.shortlist_dir_ledit.setText(self.shortlist_dir)

    def quarter_density_enabled(self):
        self.update_config()
        self.update_table()

    def meandering_enabled(self):
        self.update_config()

    def scan_rate_text_changed(self):
        self.update_config()

    def crystal_h_pitch_changed(self, value):
        self.update_config()

    def crystal_v_pitch_changed(self, value):
        self.update_config()

    def comp_h_pitch_changed(self, value):
        self.update_config()

    def comp_v_pitch_changed(self, value):
        self.update_config()

    def num_crystal_h_changed(self, value):
        self.update_config()

    def num_crystal_v_changed(self, value):
        self.update_config()

    def num_comp_h_changed(self, value):
        self.update_config()

    def num_copm_v_changed(self, value):
        self.update_config()

    def update_config(self):
        self.ssx_control_hwobj.set_config_item(
            "quarter_density",
            int(self.ssx_widget_layout.quarter_density_checkbox.isChecked()),
        )
        self.ssx_control_hwobj.set_config_item(
            "meandering", self.ssx_widget_layout.meandering_checkbox.isChecked()
        )
        if len(self.ssx_widget_layout.scan_rate_ledit.text()) == 0:
            self.ssx_control_hwobj.set_config_item("scan_rate", 0.0)
        else:
            self.ssx_control_hwobj.set_config_item(
                "scan_rate", float(self.ssx_widget_layout.scan_rate_ledit.text())
            )
        self.ssx_control_hwobj.set_config_item(
            "crystal_h_pitch", self.ssx_widget_layout.crystal_h_pitch_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "crystal_v_pitch", self.ssx_widget_layout.crystal_v_pitch_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "comp_h_pitch", self.ssx_widget_layout.comp_h_pitch_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "comp_v_pitch", self.ssx_widget_layout.comp_v_pitch_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "num_crystal_h", self.ssx_widget_layout.num_crystal_h_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "num_crystal_v", self.ssx_widget_layout.num_crystal_v_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "num_comp_h", self.ssx_widget_layout.num_comp_h_spinbox.value()
        )
        self.ssx_control_hwobj.set_config_item(
            "num_comp_v", self.ssx_widget_layout.num_comp_v_spinbox.value()
        )

    def update_table(self):
        header = self.ssx_widget_layout.interlacings_tableWidget.horizontalHeader()
        self.ssx_widget_layout.quarter_density_checkbox.setEnabled(True)
        self.ssx_widget_layout.meandering_checkbox.setEnabled(True)
        # gets the list of interlacings

        interlacings_list = self.ssx_control_hwobj.get_interlacings_list()

        # update interlacings_textEdit
        self.ssx_widget_layout.interlacings_text_edit.setText(
            str(len(interlacings_list))
        )

        # set number of rows and columns
        self.ssx_widget_layout.interlacings_tableWidget.setRowCount(
            len(interlacings_list)
        )
        self.ssx_widget_layout.interlacings_tableWidget.setColumnCount(2)

        # resize columns respectively
        header.setResizeMode(QtImport.QHeaderView.Stretch)

        # headers names
        self.ssx_widget_layout.interlacings_tableWidget.setHorizontalHeaderLabels(
            QtImport.QString("interlace;est. delay (s)").split(";")
        )

        # set non editable
        self.ssx_widget_layout.interlacings_tableWidget.setEditTriggers(
            QtImport.QAbstractItemView.NoEditTriggers
        )

        # fill the table
        for element in range(0, len(interlacingsList)):
            self.ssx_widget_layout.interlacings_tableWidget.setItem(
                element, 0, QtImport.QTableWidgetItem(str(interlacingsList[element]))
            )
            self.ssx_widget_layout.interlacings_tableWidget.setItem(
                element,
                1,
                QtImport.QTableWidgetItem(
                    str(round(interlacingsList[element] / scan_rate, 3))
                ),
            )

    # sets number of exposures and passes it to a function DG Channels create
    def set_exposures_per_feature(self):
        num_exp = self.ssx_widget_layout.exp_per_feature_spinbox.value()
        self.create_dg_channels_list(num_exp)

    # creates blocks of checkboxes
    def create_dg_channels_list(self, num_exp):

        chip_config = self.ssx_control_hwobj.get_config()
        # set number of columns
        self.ssx_widget_layout.dg_channels_table.setColumnCount(num_exp)

        # add checkboxes if a new number of exposures is bigger than the old one
        dg_channels_list = []
        if num_exp > chip_config["old_num_of_exp"]:
            for row in range(0, 4):
                checkbox_item = QtImport.QTableWidgetItem()
                checkbox_item.setFlags(
                    QtImport.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                )
                checkbox_item.setCheckState(QtImport.Qt.Unchecked)
                # add checkboxes to the list
                dg_channels_list.append(checkbox_item)
                self.ssx_widget_layout.dg_channels_table.setItem(
                    row, num_exp - 1, checkbox_item
                )

        # remove checkboxes from the list if a new number of exposures is bigger
        # than the old one
        if num_exp < chip_config["old_num_of_exp"]:
            for row in range(0, 4):
                del dg_channels_list[len(dg_channels_list) - 1]
        self.ssx_control_hwobj.set_dg_channels_list(dg_channels_list)

        # update old number of exposures
        self.ssx_control_hwobj.set_config_item("old_num_of_exp", num_exp)

    # saves chip data in a new file
    def save_chip_data(self):
        # opens input dialod to enter file_name
        new_chip_filename, ok = QtImport.QInputDialog.getText(
            self, "Enter chip file name", "name  +  .txt:"
        )
        if ok:
            # creates a file
            new_chip_filename = os.path.join(self.chip_file_dir, new_chip_filename)
            self.ssx_control_hwobj.save_chip_data(new_chip_filename)
            self.update_found_chip_files()

    def create_short_list(self):
        # fill the list with enabled ompartments
        self.enable_fill_compartment_list()
        self.ssx_widget_layout.shortlist_textedit.clear()

        # writes a header
        line_keeper = "item nr;descr;skip?;comp V;comp H;feat V;feat H;offset V (%);offset H (%);ch AB;ch CD;ch EF;ch GH;interval (ms)\n"
        self.ssx_widget_layout.shortlist_textedit.insertPlainText(line_keeper)

        text_line = self.ssx_control_hwobj.get_short_list()
        self.ssx_widget_layout.shortlist_textedit.insertPlainText(text_line)

    """
    def remove_disabled_compartments(self, text):
        output_string = ""
        with_present_descriptors_list = []

        # split the text with \n delimiter
        list_with_all_lines = text.split("\n")
        # delete last line with only \n
        del list_with_all_lines[len(listWithAllLines) - 1]
        # add lines which has enabled compartment
        for line in list_with_all_lines:
            if self.compartment_enable_list.__contains__(
                line.split(";")[1].split("_")[0]) == True:
                with_present_descriptors_list.append(line)

        # renumerate all lines with enabled compartments
        for line_number in range(0, len(with_present_descriptors_list)):
            with_present_descriptors_list[line_number].split(
                ";")[0] = str(line_number + 1)

            # add lines to the output string
            output_string = output_string + \
                with_present_descriptors_list[line_number] + "\n"

        return output_string
    """

    # creates short list by using a function which converts loop iterators to string
    def export_short_list(self):
        # opens input dialod to enter file_name
        new_shortlist_name, ok = QtImport.QInputDialog.getText(
            self, "Enter short list name", "name  +  .txt:"
        )
        if ok:
            # creates a file
            f = open(self.shortlist_dir + "/" + new_shortlist_name, "w+")
            f.write(self.ssx_widget_layout.shortlist_textedit.toPlainText())
            f.close()

    def enable_fill_compartment_list(self):
        self.compartment_enable_list = []  # set to empty

        # fill the list of enabled compartments
        for row in range(0, self.ssx_widget_layout.color_table.rowCount()):
            for column in range(0, self.ssx_widget_layout.color_table.columnCount()):
                if (
                    self.ssx_widget_layout.color_table.item(row, column).background()
                    == Colors.GREEN
                ):
                    tup = (row, column)
                    self.compartment_enable_list.append(tup)
                    # compartment_enable_list.append(chr(ord('A') + row) + str(column + 1))
        # print len(compartment_enable_list)

    def start_experiment(self):
        # print "Start button has been pressed!"
        pass
