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
ESRF Configuration Brick

[Description]

This brick displays configuation information (beam position and calibration)
related to beamlines at ESRF.
It displays information from:
* xml file ( at origin, called multiple-positions )

    * For each zoom motor position, user can see and edit:
        * Beam position values
        * Camera calibration ( nm / pixel )
        * light emiting device value
IMPORTANT!! : this data is delivered by the MultiplePositions HWRObject:
this object handles (load/edit/save) and delivers to different bricks to be 
displayed/edited like CameraBeamBrick / CameraBeamBrick

    * A list of editable 'tags' of different 'operation mode' (ex: signal, background, empty)
        this operation mode will be lately used by ESRFDataExportBrick to tag exported data.

* BLISS/ESRF data policy : data saving paths of current experiment

[Properties]

mnemonic - xml file with calibration and beam position data

[Signals]

data_policy_changed - emited when the combobox with the list of sessions
                        changes its index, or when 'reload policy' button
                        is pressed
                        params : session data policy as dictionnary


operation_modes_edited - emitted when operation mode list edited (not yet saved)
                        params : freshly edited graphic data as dict
operation_modes_saved - emitted when operation mode list is saved in xml file
                        params : freshly edited graphic data as dict


[Slots]

beam_pos_cal_data_changed - connected to MultiplePositions hwr_object

beam_cal_pos_data_saved     Connected to multipos_hwobj beam_pos_cal_data_saved signal
                            Save table data to xml file. Clear table.

beam_cal_pos_data_cancelled Connected to multipos_hwobj beam_pos_cal_data_cancelled signal
                            Set table data to the one  in xml file. Clear table.
                                    
[Comments]
See also MultiplePositions.py documentation on HardwareRepository submodule

"""

import sys
import math
import logging
import os

import copy
from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

from bliss.config import get_sessions_list

from bliss.scanning.scan_saving import ESRFScanSaving

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFConfigurationBrick(BaseWidget):
 
    operation_modes_edited = QtImport.pyqtSignal(list)
    operation_modes_saved = QtImport.pyqtSignal(list)
    data_policy_changed = QtImport.pyqtSignal(dict)
    
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------
        
        self.list_of_operational_modes = []
        self.default_session = None

        self.multipos_file_xml_path = None
        self.bliss_session_list = None
        
        # Hardware objects ----------------------------------------------------
        self.multipos_hwobj = None

        # Internal values -----------------------------------------------------
        self.table_created = False

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "/multiple-positions")
        
        # Signals ------------------------------------------------------------
        
        self.define_signal("operation_modes_edited", ())
        self.define_signal("operation_modes_saved", ())
        self.define_signal("data_policy_changed", ())
        
        
        # Slots ---------------------------------------------------------------
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Configuration", self)
        self.ui_widgets_manager = QtImport.load_ui_file("esrf_id13_configuration_widget.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.configuration_table.setSizePolicy(
            QtImport.QSizePolicy.Minimum,
            QtImport.QSizePolicy.Minimum,
        )

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.ui_widgets_manager.save_table_changes.clicked.connect(
            self.save_table_changes
        )

        self.ui_widgets_manager.cancel_table_changes.clicked.connect(
            self.cancel_table_changes
        )

        self.ui_widgets_manager.bliss_session_combo_box.currentIndexChanged.connect(
            self.display_data_policy
        )

        self.ui_widgets_manager.configuration_table.itemChanged.connect(
            self.configuration_table_item_changed
        )

        self.ui_widgets_manager.add_label_button.clicked.connect(
            self.add_op_mode_to_list
        )

        self.ui_widgets_manager.delete_label_button.clicked.connect(
            self.delete_op_mode_from_list
        )

        self.ui_widgets_manager.save_labels_button.clicked.connect(
            self.save_op_mode_list
        )

        self.ui_widgets_manager.label_list.itemSelectionChanged.connect(
            self.label_list_selection_changed
        )

        self.ui_widgets_manager.reload_data_policy_button.clicked.connect(
            self.reload_data_policy
        )
    
    def configuration_table_item_changed(self, item):

        validated_value = self.validate_cell_value(
            item.text()
        )
        item.setText(str(validated_value))
        item.setBackground(QtImport.QColor(QtImport.Qt.yellow))

        # create new dict from new data
        table = self.ui_widgets_manager.configuration_table
        item_row = item.row()
        item_col = item.column()

        if item_col in (1, 2):
            who_changed = 0
        elif item_col in (3, 4):
            who_changed = 1
        else:
            who_changed = 2

        edited_key = table.item(item_row, 0).text()

        dict_elem = {}
        
        dict_elem["zoom_tag"] = edited_key
        dict_elem["beam_pos_x"] = int(self.validate_cell_value(table.item(item_row, 1).text()))
        dict_elem["beam_pos_y"] = int(self.validate_cell_value(table.item(item_row, 2).text()))
        
        resox = self.validate_cell_value(table.item(item_row, 3).text())
        dict_elem["cal_x"] = float(resox)

        resoy = self.validate_cell_value(table.item(item_row, 4).text())
        dict_elem["cal_y"] = float(resoy)
        
        dict_elem["light"] = int(self.validate_cell_value(table.item(item_row, 5).text()))
        dict_elem["zoom"] = int(self.validate_cell_value(table.item(item_row, 6).text()))
        
        self.multipos_hwobj.edit_data(dict_elem, edited_key, who_changed)
        
    def load_default_session(self):
        """
        Parse xml file and search for 'default_session' tag
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)
        xml_tree = xml_file_tree.getroot()
        if xml_tree.find("default_session") is not None:
            self.default_session = xml_tree.find("default_session").text
            
    def load_list_of_operational_modes(self):
        """
        Parse xml file and load list of operational modes :

        'tag0', 'tag1', ...
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)

        xml_tree = xml_file_tree.getroot()
        mode_list = []
        if xml_tree.find("operational_modes") is not None:
            mode_list = xml_tree.find("operational_modes").text
            self.list_of_operational_modes = eval(mode_list)
        else:
            #if no operational_mode, hide all related controls
            self.ui_widgets_manager.add_label_button.hide()
            self.ui_widgets_manager.delete_label_button.hide()
            self.ui_widgets_manager.label_list.hide()
            self.ui_widgets_manager.label_3.hide()
            self.ui_widgets_manager.new_label_edit.hide()
            self.ui_widgets_manager.save_labels_button.hide()
        
    def property_changed(self, property_name, old_value, new_value):
        
        if property_name == "mnemonic":
            if self.multipos_hwobj is not None:
                # disconnect signal/slots
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_pos_cal_data_changed)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)
                pass
            
            if new_value is not None:
                self.multipos_hwobj = self.get_hardware_object(new_value)
            
            #search xml file so it handles the 'tags'
            # TODO : create a separate xml file for tags!!

            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.multipos_file_xml_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")
            
            if self.multipos_hwobj is not None:
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_pos_cal_data_changed)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)              
            # self.load_zoom_positions_dict()
            self.load_list_of_operational_modes()
            self.load_default_session()
            
            self.init_interface()

        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def beam_pos_cal_data_changed(self, who_changed, new_data_dict):
        self.fill_config_table()

        if new_data_dict:
            current_pos_name = new_data_dict["zoom_tag"]
        else:
            current_pos_name = self.multipos_hwobj.get_value()

        table = self.ui_widgets_manager.configuration_table

        self.ui_widgets_manager.configuration_table.itemChanged.disconnect(
                self.configuration_table_item_changed
        )

        for row_index in range(table.rowCount()):
            if table.item(row_index, 0).text() == current_pos_name:
                if who_changed == 0:
                    table.item(row_index, 1).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                    table.item(row_index, 2).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                elif who_changed == 1:
                    table.item(row_index, 3).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                    table.item(row_index, 4).setBackground(QtImport.QColor(QtImport.Qt.yellow))
        
        self.ui_widgets_manager.configuration_table.itemChanged.connect(
                self.configuration_table_item_changed
        )
    

    def fill_op_modes_list(self):
        if self.list_of_operational_modes is not None:
            self.ui_widgets_manager.label_list.clear()

            for tag_text in self.list_of_operational_modes:
                self.ui_widgets_manager.label_list.addItem(tag_text)


    def fill_config_table(self):
        tmp_dict = self.multipos_hwobj.get_positions()
        if tmp_dict is not None:
        
            self.ui_widgets_manager.configuration_table.itemChanged.disconnect(
                self.configuration_table_item_changed
            )

            if not self.table_created:
                # create table items for first and only time
                
                self.ui_widgets_manager.configuration_table.setRowCount(len(tmp_dict))

                for row in range(len(tmp_dict)):
                    for col in range(7):
                        tmp_item = QtImport.QTableWidgetItem()
                        if col == 0:
                            #zoom position name not editable
                            tmp_item.setFlags(tmp_item.flags() ^ QtImport.Qt.ItemIsEditable)
                        self.ui_widgets_manager.configuration_table.setItem(
                            row,
                            col,
                            tmp_item
                        )
                self.table_created = True
            
            table = self.ui_widgets_manager.configuration_table
            for i, (position, position_dict_elem) in enumerate(tmp_dict.items()):
                
                table.item(i, 0).setText(str(position))

                table.item(i, 1).setText(str(position_dict_elem["beam_pos_x"]))
                table.item(i, 2).setText(str(position_dict_elem["beam_pos_y"]))

                
                if position_dict_elem["cal_x"] == 1:
                    y_calib = "Not defined"
                else:
                    y_calib = str(abs(int(position_dict_elem["cal_x"])))
                if position_dict_elem["cal_y"] == 1:
                    z_calib = "Not defined"
                else:
                    z_calib = str(abs(int(position_dict_elem["cal_y"])))

                table.item(i, 3).setText(y_calib)
                table.item(i, 4).setText(z_calib)

                table.item(i, 5).setText(str(position_dict_elem['light']))
                table.item(i, 6).setText(str(position_dict_elem['zoom']))

            self.ui_widgets_manager.configuration_table.itemChanged.connect(
                self.configuration_table_item_changed
            )
            
            self.ui_widgets_manager.configuration_table.horizontalHeader().setSectionResizeMode(
                QtImport.QHeaderView.ResizeToContents
            )

    def beam_cal_pos_data_saved(self):
        """
        data saved: clean cell background
        """
        self.clean_cells_background()

    def beam_cal_pos_data_cancelled(self):
        """
        data cancelled:
        clean cell background
        reload data from hardware object
        """
        self.clean_cells_background()
        self.fill_config_table()

    def init_interface(self):
        """
        Fill table and combobox and make them functional
        """
        if self.multipos_hwobj is not None:
            self.fill_config_table()
            self.fill_op_modes_list()
            self.load_sessions()
            self.reload_data_policy()
            
    def load_sessions(self):
        """
        Load list of sessions and populate combobox
        """
        self.bliss_session_list = get_sessions_list()
        self.ui_widgets_manager.bliss_session_combo_box.clear()

        self.ui_widgets_manager.bliss_session_combo_box.currentIndexChanged.disconnect(
            self.display_data_policy
        )

        for session in self.bliss_session_list:
            self.ui_widgets_manager.bliss_session_combo_box.addItem(
                session
            )

        if self.default_session in self.bliss_session_list:
            index = self.ui_widgets_manager.bliss_session_combo_box.findText(self.default_session)
            if index != -1:
                self.ui_widgets_manager.bliss_session_combo_box.setCurrentIndex(index)
        else:
            self.ui_widgets_manager.bliss_session_combo_box.setCurrentIndex(-1)

        self.ui_widgets_manager.bliss_session_combo_box.currentIndexChanged.connect(
            self.display_data_policy
        )
            
    def reload_data_policy(self):
        
        self.display_data_policy(
            self.ui_widgets_manager.bliss_session_combo_box.currentIndex()
        )

    def display_data_policy(self, index):
        """
        Display data policy of selected session in combobox
        """
        
        if index > -1:
            new_session = self.bliss_session_list[index]
            
            scan_savings = ESRFScanSaving(new_session)

            session_info_string = ''
            session_info_dict = {}
            session_info_dict['session'] = new_session
            session_info_dict['base_path'] = scan_savings.base_path
            session_info_dict['data_filename'] = scan_savings.data_filename
            session_info_dict['data_path'] = scan_savings.data_path
            session_info_dict['dataset'] = scan_savings.dataset
            session_info_dict['date'] = scan_savings.date
            session_info_dict['sample'] = scan_savings.sample
            session_info_dict['proposal'] = scan_savings.proposal
            session_info_dict['template'] = scan_savings.template
            session_info_dict['beamline'] = scan_savings.beamline
            
            # waiting to https://gitlab.esrf.fr/bliss/bliss/-/merge_requests/2948
            # be part of current BLISS version
            #session_info_dict['filename'] = scan_savings.filename
            #session_info_dict['data_fullpath'] = scan_savings.data_fullpath
            for key, val in session_info_dict.items():
                
                info_str = ' ' + key + ' : ' + val
                session_info_string += info_str + ' \n'
            
            self.data_policy_changed.emit(session_info_dict)
            self.ui_widgets_manager.data_policy_label.setText(
                session_info_string
            )
   
    def save_op_mode_list(self):
        """
        Save data to xml file
        Clean cell background
        """
        xml_file_tree = cElementTree.parse(self.multipos_file_xml_path)
        xml_tree = xml_file_tree.getroot()
                
        xml_tree.find("operational_modes").text = str(self.list_of_operational_modes)

        xml_file_tree.write(self.multipos_file_xml_path)

        self.operation_modes_saved.emit(self.list_of_operational_modes)
    
    def add_op_mode_to_list(self):
        """
        add lable list to list
        and to self.list_of_operational_modes
        Data not saved yet
        """
        new_label_list_full = self.ui_widgets_manager.new_label_edit.text().strip()
        new_label_list = new_label_list_full.split()

        if not new_label_list:
            return
        # check if label already exist
        for new_label in new_label_list:
            if new_label not in self.list_of_operational_modes:
                self.list_of_operational_modes.append(new_label)
                self.ui_widgets_manager.label_list.addItem(new_label)
                #select newly added item
                self.ui_widgets_manager.label_list.setCurrentRow(
                    self.ui_widgets_manager.label_list.count() - 1
                )
                
        self.operation_modes_edited.emit(self.list_of_operational_modes)

    def delete_op_mode_from_list(self):
        """
        delete lable from list
        detele from self.list_of_operational_modes
        changes not saved yet
        """
        label_to_delete_list_full = self.ui_widgets_manager.new_label_edit.text().strip()
        label_to_delete_list = label_to_delete_list_full.split()
        
        if not label_to_delete_list:
            return
        for label_to_delete in label_to_delete_list:
            if label_to_delete not in self.list_of_operational_modes:
                continue
            index = self.list_of_operational_modes.index(label_to_delete)
            self.ui_widgets_manager.label_list.takeItem(index)
            self.list_of_operational_modes.remove(label_to_delete)
            #select first item
        if self.list_of_operational_modes:
            self.ui_widgets_manager.label_list.setCurrentRow(0)
        self.operation_modes_edited.emit(self.list_of_operational_modes)
        
    def label_list_selection_changed(self):
        selected_label_list = self.ui_widgets_manager.label_list.selectedItems()
        
        label_text_list = []
        for label in selected_label_list:
            label_text_list.append(label.text())
        self.ui_widgets_manager.new_label_edit.setText(
                ' '.join(label_text_list)
            )

        # if selected_row != -1:
        #     selected_item = self.ui_widgets_manager.label_list.item(selected_row)
        #     self.ui_widgets_manager.new_label_edit.setText(
        #         selected_item.text()
        #     )

    def clean_cells_background(self):
        """
        clean cells background color
        """
        table = self.ui_widgets_manager.configuration_table
        
        table.itemChanged.disconnect(
                self.configuration_table_item_changed
        )

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)
        
        table.itemChanged.connect(
                self.configuration_table_item_changed
        )
                
    def save_table_changes(self):
        """
        send signal to self.multipos_hwobj to save data to file
        clean cells background color
        """
        if self.multipos_hwobj is not None:
            self.multipos_hwobj.save_data_to_file(self.multipos_file_xml_path)
            
    def validate_cell_value(self, input_val):
        """
        return value adapted according to input
        """
        try:
            output = int(input_val)
        except ValueError:
            output = 1

        return output
               
    def cancel_table_changes(self):
        """
        cancel any change in config table.
        reload data from last saved version of xml file:
            recover data from multipos_hwobj and display it
        """
        self.multipos_hwobj.cancel_edited_data()

        # self.load_zoom_positions_dict()
        self.fill_config_table()
  
    def clear_table(self):
        """
        clean table of contents. keep headers
        """
        #table = self.ui_widgets_manager.findChild(QtI
        # mport.QTableWidget, "aligment_table")
        self.ui_widgets_manager.configuration_table.clearContents()
    
    def from_text_to_int(self, input_str, factor=1):
        if input_str is None:
            return 0
        return abs(int(float(input_str) * factor))

    def from_text_to_float(self, input_str, factor=1):
        if input_str is None:
            return 0
        return abs((float(input_str) * factor))
