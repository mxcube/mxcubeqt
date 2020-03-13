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

import logging

from gui.utils import QtImport
from gui.BaseComponents import BaseWidget
from gui.widgets.task_toolbox_widget import TaskToolBoxWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class TaskToolBoxBrick(BaseWidget):

    request_tree_brick = QtImport.pyqtSignal()

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.ispyb_logged_in = False
        self.tree_brick = None

        # Properties ----------------------------------------------------------
        self.add_property("useOscStartCbox", "boolean", False)
        self.add_property("useCompression", "boolean", False)
        #self.add_property("availableTasks", "string", "discrete char helical")
        self.add_property("showDiscreetTask", "boolean", True)
        self.add_property("showHelicalTask", "boolean", True)
        self.add_property("showCharTask", "boolean", True)
        self.add_property("showAdvancedTask", "boolean", True)
        self.add_property("showStillScanTask", "boolean", False)
        self.add_property("showCollectNowButton", "boolean", False)

        # Signals -------------------------------------------------------------
        self.define_signal("request_tree_brick", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("logged_in", ())
        self.define_slot("set_session", ())
        self.define_slot("selection_changed", ())
        self.define_slot("user_group_saved", ())
        self.define_slot("set_tree_brick", ())

        # Graphic elements ----------------------------------------------------
        self.task_tool_box_widget = TaskToolBoxWidget(self)

        # Layout --------------------------------------------------------------
        self.main_layout = QtImport.QVBoxLayout(self)
        self.main_layout.addWidget(self.task_tool_box_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # SizePolicies --------------------------------------------------------
        # self.setSizePolicy(QtImport.QSizePolicy.MinimumExpanding,
        #                   QtImport.QSizePolicy.MinimumExpanding)

        # Other ---------------------------------------------------------------
        HWR.beamline.sample_view.connect("pointSelected", self.point_selected)

    def set_expert_mode(self, expert):
        self.task_tool_box_widget.set_expert_mode(expert)

    def run(self):
        if HWR.beamline.session.session_id:
            self.setEnabled(True)

        #self.task_tool_box_widget.set_available_tasks(self["availableTasks"])
        self.request_tree_brick.emit()
        self.task_tool_box_widget.adjust_width(self.width())

    def user_group_saved(self, new_user_group):
        HWR.beamline.session.set_user_group(str(new_user_group))
        self.task_tool_box_widget.update_data_path_model()
        path = (
            HWR.beamline.session.get_base_image_directory()
            + "/"
            + str(new_user_group)
        )
        msg = "Image path is: %s" % path
        logging.getLogger("GUI").info(msg)

    @QtImport.pyqtSlot(BaseWidget)
    def set_tree_brick(self, brick):
        self.tree_brick = brick
        self.tree_brick.compression_state = self["useCompression"] == 1
        self.task_tool_box_widget.set_tree_brick(brick)

    @QtImport.pyqtSlot(int, str, str, int, str, str, bool)
    def set_session(
        self,
        session_id,
        t_prop_code=None,
        prop_number=None,
        prop_id=None,
        start_date=None,
        prop_code=None,
        is_inhouse=None,
    ):
        """
        Connected to the slot set_session and is called after a
        request to get the current session from LIMS (ISPyB) is
        made. The signal is normally emitted by the brick that
        handles LIMS login, ie ProposalBrick.
        The session_id is '' if no session could be retrieved.
        """
        if session_id is "":
            self.logged_in(True)

    @QtImport.pyqtSlot(bool)
    def logged_in(self, logged_in):
        """
        Handels the signal logged_in from the brick the handles
        LIMS (ISPyB) login, ie ProposalBrick. The signal is
        emitted when a user was succesfully logged in.
        """
        logged_in = True

        self.ispyb_logged_in = logged_in

        if HWR.beamline.session is not None:
            HWR.beamline.session.set_user_group("")

        self.setEnabled(logged_in)
        self.task_tool_box_widget.ispyb_logged_in(logged_in)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "useOscStartCbox":
            self.task_tool_box_widget.use_osc_start_cbox(new_value)
        elif property_name == "useCompression":
            self.task_tool_box_widget.enable_compression(new_value)
        elif property_name == "showCollectNowButton":
            self.task_tool_box_widget.collect_now_button.setVisible(new_value)
        elif property_name == "showDiscreetTask":
            if not new_value:
                self.task_tool_box_widget.hide_task(
                    self.task_tool_box_widget.discrete_page
                )
        elif property_name == "showHelicalTask":
            if not new_value:
                self.task_tool_box_widget.hide_task(
                    self.task_tool_box_widget.helical_page
                )
        elif property_name == "showCharTask":
            if not new_value:
                self.task_tool_box_widget.hide_task(self.task_tool_box_widget.char_page)
        elif property_name == "showAdvancedTask":
            if not new_value:
                self.task_tool_box_widget.hide_task(
                    self.task_tool_box_widget.advanced_page
                )
        elif property_name == "showStillScanTask":
            if not new_value:
                self.task_tool_box_widget.hide_task(
                    self.task_tool_box_widget.still_scan_page
                )

    def selection_changed(self, items):
        """
        Connected to the signal "selection_changed" of the TreeBrick.
        Called when the selection in the tree changes.
        """
        self.task_tool_box_widget.selection_changed(items)

    def point_selected(self, selected_position):
        self.task_tool_box_widget.helical_page.centred_position_selection(
            selected_position
        )
        self.task_tool_box_widget.discrete_page.centred_position_selection(
            selected_position
        )
        self.task_tool_box_widget.char_page.centred_position_selection(
            selected_position
        )
        self.task_tool_box_widget.energy_scan_page.centred_position_selection(
            selected_position
        )
        self.task_tool_box_widget.xrf_spectrum_page.centred_position_selection(
            selected_position
        )

        self.task_tool_box_widget.discrete_page.refresh_current_item()
        self.task_tool_box_widget.helical_page.refresh_current_item()
        self.task_tool_box_widget.char_page.refresh_current_item()
        self.task_tool_box_widget.energy_scan_page.refresh_current_item()
        self.task_tool_box_widget.xrf_spectrum_page.refresh_current_item()
