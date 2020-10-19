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
Camera Beam Brick

[Description]

This brick displays and saves for different zoom values a beam position.

It displays information from:
* xml file ( at origin, called multiple-positions )
    * For each zoom motor position, user can see and edit:
        * Beam position values
IMPORTANT!! : this data is delivered by the MultiplePositions HWRObject:
MultiplePositions object handles data (load/edit/save) and delivers it to
different bricks to be displayed/edited like ESRFCameraBeamBrick / ESRFCameraCalibrationBrick

[Properties]

zoom - string - MultiplePositions hardware object which reference the different
                zoom position and allows to save beam position for each of them

[Signals]

[Slots]

beam_position_data_changed          new_beam_data (tuple) - slot used to turnarround an
                                    initialization problem: object creation order in
                                    beamline_config.yml file

beam_pos_cal_data_changed           Connected to multipos_hwobj beam_pos_cal_data_changed signal
                                    Change table data and hightlight changes

beam_cal_pos_data_saved             Connected to multipos_hwobj beam_pos_cal_data_saved signal
                                    Save table data to xml file. Clear table.

beam_cal_pos_data_cancelled         Connected to multipos_hwobj beam_pos_cal_data_cancelled signal
                                    Set table data to the one  in xml file. Clear table.
                                        
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

class ESRFCameraBeamBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # variables -----------------------------------------------------------

        self.current_beam_position = None
        self.current_zoom_pos_name = None
        self.current_zoom_idx = -1
        self.multipos_file_xml_path = None

        # Hardware objects ----------------------------------------------------
        self.multipos_hwobj = None
        
        # Internal values -----------------------------------------------------
        self.table_created = False
        
        # Properties ----------------------------------------------------------
        self.add_property("zoom", "string", "")
        
        # Signals ------------------------------------------------------------
        
        # Slots ---------------------------------------------------------------
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Beam Position", self)
        self.ui_widgets_manager = QtImport.load_ui_file("camera_beam_brick.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.beam_positions_table.setSizePolicy(
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
       
        self.ui_widgets_manager.save_current_beam_pos_pushbutton.clicked.connect(
            self.save_beam_position
        )

        # Other hardware object connections --------------------------

        # Wanted to connect directly HWR.beamline.sample_view signal to
        # self.multipos_hwobj but sample_view is not created by the time
        # self.multipos_hwobj.init() is executed : create a pass by way
        # not very elegant...

        # if HWR.beamline.sample_view is not None:
        #     self.connect(HWR.beamline.sample_view,
        #                 "beam_position_data_changed",
        #                 self.beam_position_data_changed
        #     )
        # else:
        #     logging.getLogger("HWR").warning("CameraBeamBrick : HWR.beamline.sample_view NONE")

    # def beam_position_data_changed(self, new_beam_data):
    #     """
    #     auxiliar function to link HWR.beamline.sample_view to multipos_hwobj
    #     """        
    #     self.multipos_hwobj.beam_position_data_changed(new_beam_data)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "zoom":
            if self.multipos_hwobj is not None:

                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.disconnect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

            self.multipos_hwobj = self.get_hardware_object(new_value)

            # get zoom xml file path
            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.multipos_file_xml_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")

            if self.multipos_hwobj is not None:
                
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_changed",
                                self.beam_cal_pos_data_changed)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_saved",
                                self.beam_cal_pos_data_saved)
                self.connect(self.multipos_hwobj, "beam_pos_cal_data_cancelled",
                                self.beam_cal_pos_data_cancelled)

            self.init_interface()
        
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

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
        self.init_interface()
        self.clean_cells_background()
                
    def beam_cal_pos_data_changed(self, who_changed, new_data_dict):
        """
        Change data in table.
        Set background color to highlight changes
        if who_changed == 1 : changes from calibration
        if who_changed == 0 : changes from beam position
        """

        if who_changed == 1:
            return
        
        self.init_interface()

        if new_data_dict:
            pos_name = new_data_dict["zoom_tag"]
        else:
            pos_name = self.multipos_hwobj.get_value()
        
        table = self.ui_widgets_manager.beam_positions_table

        for index_row in range(table.rowCount()):
            if table.item(index_row, 0).text() == pos_name:
                table.item(index_row, 1).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                table.item(index_row, 2).setBackground(QtImport.QColor(QtImport.Qt.yellow))
                
    def init_interface(self):
        """
        Build up GUI
        """

        tmp_dict = self.multipos_hwobj.get_positions()

        if tmp_dict:
            if not self.table_created:
                # create table items for first and only time
                self.ui_widgets_manager.beam_positions_table.setRowCount(len(tmp_dict))

                for row in range(len(tmp_dict)):
                    for col in range(3):
                        tmp_item = QtImport.QTableWidgetItem()
                        tmp_item.setFlags(tmp_item.flags() ^ QtImport.Qt.ItemIsEditable)
                        self.ui_widgets_manager.beam_positions_table.setItem(
                            row,
                            col,
                            tmp_item
                        )
                self.table_created = True

            table = self.ui_widgets_manager.beam_positions_table

            for i, (position, position_dict) in enumerate(tmp_dict.items()):
                beam_pos_x = position_dict["beam_pos_x"]
                beam_pos_y = position_dict["beam_pos_y"]
            
                table.item(i, 0).setText(str(position))
                table.item(i, 1).setText(str(beam_pos_x))
                table.item(i, 2).setText(str(beam_pos_y))

    def clean_cells_background(self):
        """
        clean cells background color
        """
        table = self.ui_widgets_manager.beam_positions_table

        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.item(row, col).setData(QtImport.Qt.BackgroundRole, None)

    def save_beam_position(self):
        """
        send signal to self.multipos_hwobj to save data to file
        clean cells background color
        """
        if self.multipos_hwobj is not None:
            self.multipos_hwobj.save_data_to_file(self.multipos_file_xml_path)

        self.clean_cells_background()
    
    def clear_table(self):
        """
        Adapt
        """
        self.ui_widgets_manager.beam_positions_table.clearContents()