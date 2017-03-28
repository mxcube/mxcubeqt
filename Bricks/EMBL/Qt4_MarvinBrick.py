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
__category__ = "Sample changer"


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
        self.main_gbox = QGroupBox('Marvin Status', self)
        self.status_table = QTableWidget(self) 

        # Layout --------------------------------------------------------------
        _main_gbox_gridlayout = QGridLayout(self.main_gbox)
        _main_gbox_gridlayout.addWidget(self.status_table)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(["Property", "Description", "Value"])

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'hwobj_sample_changer':
            if self.sample_changer_hwobj:
                self.disconnect(self.sample_changer_hwobj,
                                'statusChanged',
                                self.status_changed)
            self.sample_changer_hwobj = self.getHardwareObject(new_value)
            if self.sample_changer_hwobj:
                self.init_tables()
                self.connect(self.sample_changer_hwobj,
                             'statusChanged',
                             self.status_changed)
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
            

    def status_changed(self, status_list):
        for status in status_list:
            property_status_list = status.split(':')
            if len(property_status_list) < 2:
                continue

            prop_name = property_status_list[0]
            prop_value = property_status_list[1]

            if prop_name in self.status_str_desc:
                self.status_table.item(self.index_dict[prop_name], 2).setText(prop_value)
   
