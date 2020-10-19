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
Camera Calibration Brick

[Description]

This brick allows to calibrate the display of a frame grabber.
The different features are:
    - 2 clicks calibration procedure using 2 motors displacement defined in
      the interface
    - Display of the calibration in both axis for different zoom values
    - Saving of the calibration of both axis for different zoom values

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save calibration for both axis
                for each zoom positions

vertical motor - string - XML file of the Motor used to calibrate vertical axis

horizontal motor - string - XML file of the Motor used to calibrate horizontal axis

[Signals]

[Slots]

beam_pos_cal_data_changed           Connected to multipos_hwobj beam_pos_cal_data_changed signal
                                    Change table data and hightlight changes

beam_cal_pos_data_saved             Connected to multipos_hwobj beam_pos_cal_data_saved signal
                                    Save table data to xml file. Clear table.

beam_cal_pos_data_cancelled         Connected to multipos_hwobj beam_pos_cal_data_cancelled signal
                                    Set table data to the one  in xml file. Clear table.

diffractometer_manual_calibration_done  - {two_calibration_points}
                                    - Connected to diffractometer's new_calibration_done signal

[Comments]

See also MultiplePositions.py documentation on HardwareRepository submodule

"""

import sys
import math
import logging
import os

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCameraCalibrationBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.y_calib = None # metres/pixel
        self.z_calib = None # metres/pixel
        self.current_zoom_pos_name = None
        self.multipos_file_xml_path = None
        self.table_created = False

        # Hardware objects ----------------------------------------------------
        self.multipos_hwobj = None
        self.h_motor_hwobj = None
        self.v_motor_hwobj = None

        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        self.add_property("vertical motor", "string", "")
        self.add_property("horizontal motor", "string", "")
        
        # Signals ------------------------------------------------------------
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Pixel Size Calibration", self)
        self.ui_widgets_manager = QtImport.load_ui_file("camera_calibration.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.calibration_table.setSizePolicy(
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
       
        self.ui_widgets_manager.save_calibration_pushbutton.clicked.connect(
            self.save_new_calibration_value
        )

        self.ui_widgets_manager.start_new_calibration_pushbutton.clicked.connect(
            self.start_new_calibration
        )

        self.ui_widgets_manager.cancel_calibration_pushbutton.clicked.connect(
            self.cancel_calibration
        )

        # Other hardware object connections --------------------------
        self.connect(
            HWR.beamline.diffractometer,
            "new_calibration_done",
            self.diffractometer_manual_calibration_done,
        )

    def property_changed(self, property_name, old_value, new_value):
        
        if property_name == "zoom":
            
            if self.multipos_hwobj is not None:
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

            if new_value is not None:
                self.multipos_hwobj = self.get_hardware_object(new_value)
                if new_value.startswith("/"):
                    new_value = new_value[1:]
                self.multipos_file_xml_path = os.path.join(
                    HWR.getHardwareRepositoryConfigPath(),
                    new_value + ".xml"
                )

            if self.multipos_hwobj is not None:

                self.connect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

            self.update_gui()

        if property_name == "vertical motor":
            self.v_motor_hwobj = self.get_hardware_object(new_value)
            name = self.v_motor_hwobj.name()
            self.ui_widgets_manager.delta_z_label.setText(f"Delta on {name}:")
            
        if property_name == "horizontal motor":
            self.h_motor_hwobj = self.get_hardware_object(new_value)
            name = self.h_motor_hwobj.name()
            self.ui_widgets_manager.delta_y_label.setText(f"Delta on {name}:")
            
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def beam_cal_pos_data_changed(self, who_changed, new_data_dict):
        """
        Change data in table.
        Set background color to highlight changes
        if who_changed == 1 : changes from calibration
        if who_changed == 0 : changes from beam position
        """
        if who_changed == 0:
            return

        self.update_gui()

        if new_data_dict:
            pos_name = new_data_dict["zoom_tag"]
        else:
            pos_name = self.multipos_hwobj.get_value()
        
        table = self.ui_widgets_manager.calibration_table

        for index_row in range(table.rowCount()):
            if table.item(index_row, 0).text() == pos_name:
                table.item(index_row, 1).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                table.item(index_row, 2).setBackground(QtImport.QColor(QtImport.Qt.yellow))
            
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
        self.update_gui()

    def update_gui(self):
        
        tmp_dict = self.multipos_hwobj.get_positions()
        if tmp_dict:

            if not self.table_created:
                # create table items for first and only time
                
                self.ui_widgets_manager.calibration_table.setRowCount(len(tmp_dict))

                for row in range(len(tmp_dict)):
                    for col in range(3):
                        tmp_item = QtImport.QTableWidgetItem()
                        tmp_item.setFlags(tmp_item.flags() ^ QtImport.Qt.ItemIsEditable)
                        self.ui_widgets_manager.calibration_table.setItem(
                            row,
                            col,
                            tmp_item
                        )
                self.table_created = True

            table = self.ui_widgets_manager.calibration_table
            for i, (position, position_dict) in enumerate(tmp_dict.items()):
                
                if position_dict["cal_x"] == 1:
                    y_calib = "Not defined"
                else:
                    y_calib = str(abs(int(position_dict["cal_x"])))
                if position_dict["cal_y"] == 1:
                    z_calib = "Not defined"
                else:
                    z_calib = str(abs(int(position_dict["cal_y"])))
                """
                resolution are displayed in nanometer/pixel and saved in metre/pixel
                """
                table.item(i, 0).setText(str(position))
                table.item(i, 1).setText(y_calib)
                table.item(i, 2).setText(z_calib)
            
    def zoom_state_changed(self):
        pass

    def clean_cells_background(self):
        """
        clean cells background color
        """
        table = self.ui_widgets_manager.calibration_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)

    def save_new_calibration_value(self):
        """
        send signal to self.multipos_hwobj to save data to file
        clean cells background color
        """

        if self.multipos_hwobj is not None:
            self.multipos_hwobj.save_data_to_file(self.multipos_file_xml_path)

        self.clean_cells_background()

    def cancel_calibration(self):
        """
        Cancel current calibration
        """
        HWR.beamline.diffractometer.cancel_manual_calibration()

    def start_new_calibration(self):
        """
        Start new calibration
        """

        hor_motor_delta = float(self.ui_widgets_manager.delta_y_textbox.text())
        ver_motor_delta = float(self.ui_widgets_manager.delta_z_textbox.text())
        
        if HWR.beamline.sample_view is not None:
            HWR.beamline.sample_view.start_calibration()
            if HWR.beamline.diffractometer is not None:
                HWR.beamline.diffractometer.set_calibration_parameters(
                    hor_motor_delta,
                    ver_motor_delta
                )
        
                HWR.beamline.diffractometer.start_manual_calibration()

    def diffractometer_manual_calibration_done(self, two_calibration_points):
        """
        Calibration done.
        Update table, hightlight changes
        """
        
        HWR.beamline.sample_view.stop_calibration()
        
        delta_x_pixels = abs(two_calibration_points[0][0] - two_calibration_points[1][0])
        delta_y_pixels = abs(two_calibration_points[0][1] - two_calibration_points[1][1])

        hor_motor_delta = float(self.ui_widgets_manager.delta_y_textbox.text()) # milimeters
        ver_motor_delta = float(self.ui_widgets_manager.delta_z_textbox.text())
        
        self.y_calib = float(hor_motor_delta/delta_x_pixels) * 1e-3 # metres/pixel
        self.z_calib = float(ver_motor_delta/delta_y_pixels) * 1e-3

        self.multipos_hwobj.calibration_data_changed(
            (self.y_calib * 1e9, self.z_calib * 1e9)
        )

    def clear_table(self):
        """
        clear table from content
        """
        table = self.ui_widgets_manager.aligment_table
        table.clearContents()
            
