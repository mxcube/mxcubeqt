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
#  GNU Lsser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import QtImport

from gui.utils import Icons
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"
__category__ = 'General'


class ToolsBrick(BaseWidget):
    """Adds a tool menu to the toolbar. Actions are configured via xml.
       Action call method from hwobj.
    """
 
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.tools_hwobj = None
        self.action_dict = {}

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property('mnemonic', 'string', '')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------

        # Layout --------------------------------------------------------------

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def run(self):
        """Adds menu to the tool bar"""
        self.tools_menu = QtImport.QMenu("Tools", self)
        self.tools_menu.addSeparator()
        BaseWidget._menuBar.insert_menu(self.tools_menu, 2)
        self.init_tools()

    def property_changed(self, property_name, old_value, new_value):
        """Defines behaviour of the brick"""
        if property_name == "mnemonic":
            self.tools_hwobj = self.get_hardware_object(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def set_expert_mode(self, is_expert_mode):
        """Enables/Disables action if in/not in export mode and
           action has expertMode=True
        """
        for key in self.action_dict.keys():
            tool = self.action_dict[key]
            if tool.get("expertMode") is not None:
               key.setEnabled(is_expert_mode)

    def init_tools(self):
        """Gets available methods and populates menubar with methods
           If icon name exists then adds icon
        """
        self.tools_list = self.tools_hwobj.get_tools_list()
        for index, tool in enumerate(self.tools_list):
            if tool == "separator":
                self.tools_menu.addSeparator()
            elif hasattr(tool["hwobj"], tool["method"]):
                temp_action = self.tools_menu.addAction(\
                    tool["display"],
                    self.execute_tool)
                if tool.get("icon"):
                    temp_action.setIcon(Icons.load_icon(tool["icon"]))
                temp_action.setDisabled(tool.get("expertMode", False))
                self.action_dict[temp_action] = tool

    def execute_tool(self):
        """Executes tool asigned to the menu action
           Asks for a confirmation if a tool has a conformation msg.
        """
        for key in self.action_dict.keys():
            if key == self.sender():
                tool = self.action_dict[key]
                if tool.get("confirmation"):
                    conf_dialog = QtImport.QMessageBox(QtImport.QMessageBox.Question, "Question",
                         str(tool["confirmation"]), QtImport.QMessageBox.Ok | QtImport.QMessageBox.Cancel)
                    rec = QtImport.QApplication.desktop().screenGeometry()
                    pos_x = rec.right() + rec.width() / 2 - conf_dialog.width() / 2
                    pos_y = rec.height() / 2
                    conf_dialog.move(pos_x, pos_y)
                    if conf_dialog.exec_() == QtImport.QMessageBox.Ok:
                        getattr(tool["hwobj"], tool["method"])()
                else:
                    getattr(tool["hwobj"], tool["method"])()
