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
ESRF Export Data Brick

[Description]

This brick exports data to different files:

Exported data:
    * Information related to microscope status:
        * motor positions
        * camera calibration
    * Information on graphical items:
        * beam position
        * created points/lines/ROI's positions
    * Microscope snapshots

Created files:
    * JSON file with 
    * Image file with raw microscope image
    * Image file with microscope image plus graphics items (if any)

[Properties]

[Signals]

[Slots]

data_policy_changed (dict) - slot to be connected to ESRFConfigurationBrick's
                             data_policy_changed signal.
                             param : data_policy_info_dict

[Comments]

"""

import sys
import math
import logging
import json
import os
from os.path import expanduser
from pprint import pprint
import copy
import datetime
from datetime import date
import logging
import pprint

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

from bliss.config import get_sessions_list
from bliss.scanning.scan_saving import ESRFScanSaving
        


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFExportDataBrick(BaseWidget):

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Signals ------------------------------------------------------------
    
        # Slots ---------------------------------------------------------------
        self.define_slot("data_policy_changed", ())

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Export Data", self)
        self.ui_widgets_manager = QtImport.load_ui_file("export_data_layout.ui")

        # Internal values -----------------------------------------------------
        self.__current_sample = None
        self.__data_policy_info_dict = {}

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        # Qt signal/slot connections ------------------------------------------
        self.ui_widgets_manager.export_button.clicked.connect(
            self.export_button_clicked
        )

        self.ui_widgets_manager.sample_name_tbox.textChanged.connect(
            self.set_export_file_name
        )

        self.ui_widgets_manager.filename_tbox.textChanged.connect(
            self.set_export_file_name
        )

        self.ui_widgets_manager.file_index_tbox.textChanged.connect(
            self.set_export_file_name
        )

        self.ui_widgets_manager.select_file_path_button.clicked.connect(
            self.select_file_path_button_clicked
        )

        self.ui_widgets_manager.reload_policy_data_button.clicked.connect(
            self.reload_policy_data_button_clicked
        )

    def reload_policy_data_button_clicked(self):
        """
        reload data policy: use the one recorded in self.__data_policy_info_dict
        """

        session_name = self.__data_policy_info_dict.get('session', None)

        if session_name is not None:
            scan_savings = ESRFScanSaving(session_name)

            session_info_dict = {}
            session_info_dict['session'] = session_name
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
            
            self.data_policy_changed(session_info_dict)

    def data_policy_changed(self, data_policy_info_dict):
        """
        param : data_policy_info_dict
            data policy object as given by bliss' SCAN_SAVING
        """
        self.__data_policy_info_dict = data_policy_info_dict
        
        self.set_export_file_path()

    def set_export_file_path(self):
        """
        set full path (and maybe also sample name) coming from data policy
        (changes from bliss console)
        """

        self.__current_sample = self.__data_policy_info_dict.get('sample', "no_sample_defined")
        self.ui_widgets_manager.sample_name_tbox.setText(self.__current_sample)
        
        base_path = self.__data_policy_info_dict.get('base_path', "no_data_path")
        
        extra_path_template = self.__data_policy_info_dict.get('template', "no_template")

        for k, v in self.__data_policy_info_dict.items():
            extra_path_template = extra_path_template.replace('{' + k + '}', v)

        # take off the last folder from the path : convention with ID13 staff
        extra_path_template = extra_path_template[0:extra_path_template.rfind('/')]

        full_path = os.path.join(base_path, extra_path_template, "")
        self.ui_widgets_manager.export_folder_path_tbox.setText(full_path)

    def set_export_file_name(self):
        """
        set full file name when file's sample/sub/index textboxes change
        """
        sample_name = self.ui_widgets_manager.sample_name_tbox.text()
        sample_name = sample_name.strip()

        filename = self.ui_widgets_manager.filename_tbox.text()
        filename = filename.strip()

        file_index = self.ui_widgets_manager.file_index_tbox.text()
        filename = sample_name + '_' + filename + '_' + file_index + '.json'
    
        self.ui_widgets_manager.export_filename_tbox.setText(filename)

    def select_file_path_button_clicked(self):
        """
        open file dialog to select a valid folder
        """

        file_dialog = QtImport.QFileDialog(self)
        
        old_folder_path = self.ui_widgets_manager.export_folder_path_tbox.text().strip()
        
        if not os.path.exists(old_folder_path):
            old_folder_path = "/"
        selected_dir = str(
            file_dialog.getExistingDirectory(
                self, "Select a directory", old_folder_path, QtImport.QFileDialog.ShowDirsOnly
            )
        )

        if selected_dir is not None and len(selected_dir) > 0:
            self.ui_widgets_manager.export_folder_path_tbox.setText(selected_dir)

    def export_button_clicked(self):

        """
        File to be exported.
        Format: python dict
        {
            "timestamp" : datetime.now()
            "diff_motors" : { 
                            "mot0.name": pos0
                            "mot1.name": pos1
                             ...
                            }
            "position_dict" : { 
                            "beam_pos_x" : val, int - pixels
                            "beam_pos_y" : val, int - pixels
                            "cal_x" : val, int - nm / pixel
                            "cal_y" : val, int - nm / pixel
                            "light" : val,
                            "zoom" : val,
                               }
            "selected_shapes_dict": {
                                    "selected_shape1_name":
                                        {
                                        "type" : string
                                        "index" : int
                                        "operation_mode": string ( 'visible', 'background'...)
                                        "centred_positions" : list( dict )
                                                {
                                                    "phi":
                                                    "phiz":
                                                    "phiy":
                                                    "sampx":
                                                    "sampy":
                                                }
                                        }

                                    }

        }

        """

        folder_path = self.ui_widgets_manager.export_folder_path_tbox.text().strip()
        filename = self.ui_widgets_manager.export_filename_tbox.text().strip()
        file_full_path = os.path.join(folder_path, filename)
                
        # file exists?? overwrite ??
        if self.ui_widgets_manager.overwrite_warn_cbbox.isChecked():
            
            # get full filename and check if file already exists
            if os.path.exists(file_full_path):
                if (
                    QtImport.QMessageBox.warning(
                        None,
                        "File already exists!",
                        "Are you sure you want to overwrite existing file ?",
                        QtImport.QMessageBox.Yes,
                        QtImport.QMessageBox.No,
                    )
                    == QtImport.QMessageBox.No
                    ):
                    return

        # create json file data and write
        data = self.build_data()
        
        with open(file_full_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # take snapshots
        file_full_path_no_extension = file_full_path[0:file_full_path.rfind('.')]
        if HWR.beamline.sample_view is not None:
            file_full_path_no_extension_no_index = file_full_path_no_extension[0:-4]
            raw_snapshot_file_path = (
                file_full_path_no_extension_no_index +
                "_raw_" +
                self.ui_widgets_manager.file_index_tbox.text() +
                ".png"
            )
            snapshot_file_path = (
                file_full_path_no_extension_no_index +
                "_ano_" +
                self.ui_widgets_manager.file_index_tbox.text() +
                ".png"
            )
            
            HWR.beamline.sample_view.save_scene_snapshot(snapshot_file_path)
            HWR.beamline.sample_view.save_raw_scene_snapshot(raw_snapshot_file_path)

        # update GUI
        if self.ui_widgets_manager.clean_comment_cbox.isChecked():
            self.ui_widgets_manager.comment_text_edit.clear()

        if self.ui_widgets_manager.delete_items_cbox.isChecked():
            HWR.beamline.sample_view.clear_all_shapes()

        file_index = int(self.ui_widgets_manager.file_index_tbox.text())
        file_index += 1
        file_index_formated = '{:04d}'.format(file_index)
        self.ui_widgets_manager.file_index_tbox.setText(file_index_formated)

        self.set_export_file_name()

    def build_data(self):

        data = {}
        now = datetime.datetime.now()
        data['timestamp'] = str(now)
        data['data_creator'] = "GUIApplication"
        data['comments'] = self.ui_widgets_manager.comment_text_edit.toPlainText()
        data['image_size'] = (0,0)
        motors_dict = {}
        position_dict = {}
        shapes_dict = {}

        if HWR.beamline.sample_view is not None:
            data['image_size'] = HWR.beamline.sample_view.get_image_size()

        if HWR.beamline.diffractometer is not None:

            motors_dict = HWR.beamline.diffractometer.get_motors_dict()
            position_dict = HWR.beamline.diffractometer.get_diffractometer_status()

            data['beam_pos_x'] = position_dict['beam_pos_x']
            data['beam_pos_y'] = position_dict['beam_pos_y']
            data['cal_x'] = position_dict['cal_x']
            data['cal_y'] = position_dict['cal_y']
            data['zoom_tag'] = position_dict['zoom_tag']
            data['zoom_value'] = position_dict['zoom']

            for shape in HWR.beamline.sample_view.get_shapes():
                
                display_name = shape.get_display_name()
                operation_mode = shape.get_operation_mode()
                shape_type = display_name.split()[0]
                index = display_name.split()[-1]
                global_index = shape.global_index

                centred_positions = []
                shape_dict = {}
                
                if shape_type == "Point":
                    centred_positions.append(shape.get_centred_position())
                    shape_dict["pixel_x"] = round(shape.get_start_position()[0])
                    shape_dict["pixel_y"] = round(shape.get_start_position()[1])
                elif shape_type == "Line" or shape_type == "Square":
                    centred_positions.append(list(shape.get_centred_positions()))
                    shape_dict["pixel_positions"] = shape.get_points_info()
                    shape_dict["height_pix"] = shape.get_item_height_pix()
                    shape_dict["width_pix"] = shape.get_item_width_pix()
 
                shape_dict["graphic_type"] = shape_type
                shape_dict["index"] = index
                shape_dict["index_global"] = global_index
                shape_dict["operation_mode"] = operation_mode
                
                shapes_dict[display_name.replace(" ", "_")] = shape_dict

        data['motors'] = motors_dict
        data['graphic_items_points'] = shapes_dict

        return data


        