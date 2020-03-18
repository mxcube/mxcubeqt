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

# import os
import logging
# from collections import namedtuple

from gui.BaseComponents import BaseWidget
from gui.utils import queue_item, Colors, QtImport
from gui.utils.sample_changer_helper import SC_STATE_COLOR, SampleChanger
from gui.widgets.dc_tree_widget import DataCollectTree

from HardwareRepository.HardwareObjects.queue_model_enumerables import CENTRING_METHOD

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class TreeBrick(BaseWidget):

    enable_widgets = QtImport.pyqtSignal(bool)
    hide_sample_tab = QtImport.pyqtSignal(bool)
    hide_dc_parameters_tab = QtImport.pyqtSignal(bool)
    hide_sample_centring_tab = QtImport.pyqtSignal(bool)
    hide_dcg_tab = QtImport.pyqtSignal(bool)
    hide_sample_changer_tab = QtImport.pyqtSignal(bool)
    hide_plate_manipulator_tab = QtImport.pyqtSignal(bool)
    hide_char_parameters_tab = QtImport.pyqtSignal(bool)
    hide_energy_scan_tab = QtImport.pyqtSignal(bool)
    hide_xrf_spectrum_tab = QtImport.pyqtSignal(bool)
    hide_workflow_tab = QtImport.pyqtSignal(bool)
    hide_advanced_tab = QtImport.pyqtSignal(bool)
    hide_xray_imaging_tab = QtImport.pyqtSignal(bool)
    populate_dc_parameter_widget = QtImport.pyqtSignal(object)
    populate_dc_group_widget = QtImport.pyqtSignal(object)
    populate_char_parameter_widget = QtImport.pyqtSignal(object)
    populate_sample_details = QtImport.pyqtSignal(object)
    populate_energy_scan_widget = QtImport.pyqtSignal(object)
    populate_xrf_spectrum_widget = QtImport.pyqtSignal(object)
    populate_advanced_widget = QtImport.pyqtSignal(object)
    populate_xray_imaging_widget = QtImport.pyqtSignal(object)
    populate_workflow_widget = QtImport.pyqtSignal(object)

    selection_changed = QtImport.pyqtSignal(object)
    set_directory = QtImport.pyqtSignal(str)
    set_prefix = QtImport.pyqtSignal(str)
    set_sample = QtImport.pyqtSignal(object)
    get_tree_brick = QtImport.pyqtSignal(BaseWidget)
    diffractometer_ready = QtImport.pyqtSignal(bool)
    sample_mount_started = QtImport.pyqtSignal()
    sample_mount_finished = QtImport.pyqtSignal()

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.state_machine_hwobj = None
        self.redis_client_hwobj = None

        # Internal variables --------------------------------------------------
        self.enable_collect_conditions = {}
        self.current_view = None
        self.current_queue_entry = None
        self.is_logged_in = False
        self.lims_samples = None
        self.filtered_lims_samples = None
        self.compression_state = True
        self.queue_autosave_action = None
        self.queue_undo_action = None
        self.queue_redo_action = None
        self.queue_sync_action = None

        # Properties ----------------------------------------------------------
        self.add_property("queue", "string", "/queue")
        self.add_property("queue_model", "string", "/queue-model")
        self.add_property("xml_rpc_server", "string", "/xml_rpc_server")
        self.add_property("redis_client", "string", "")
        self.add_property("useFilterWidget", "boolean", True)
        self.add_property("useSampleWidget", "boolean", True)
        self.add_property("scOneName", "string", "Sample changer")
        self.add_property("scTwoName", "string", "Plate")
        self.add_property("usePlateNavigator", "boolean", False)
        self.add_property("useHistoryView", "boolean", True)
        self.add_property("useCentringMethods", "boolean", True)
        self.add_property("enableQueueAutoSave", "boolean", True)

        # Properties to initialize hardware objects --------------------------
        self.add_property("hwobj_state_machine", "string", "")

        # Signals ------------------------------------------------------------
        self.define_signal("enable_widgets", ())
        self.define_signal("diffractometer_ready", ())

        # Hiding and showing the tabs
        self.define_signal("hide_sample_tab", ())
        self.define_signal("hide_dc_parameters_tab", ())
        self.define_signal("hide_sample_centring_tab", ())
        self.define_signal("hide_dcg_tab", ())
        self.define_signal("hide_sample_changer_tab", ())
        self.define_signal("hide_plate_manipulator_tab", ())
        self.define_signal("hide_char_parameters_tab", ())
        self.define_signal("hide_energy_scan_tab", ())
        self.define_signal("hide_xrf_spectrum_tab", ())
        self.define_signal("hide_workflow_tab", ())
        self.define_signal("hide_advanced_tab", ())
        self.define_signal("hide_xray_imaging_tab", ())
        self.define_signal("populate_dc_parameter_widget", ())
        self.define_signal("populate_dc_group_widget", ())
        self.define_signal("populate_char_parameter_widget", ())
        self.define_signal("populate_sample_details", ())
        self.define_signal("populate_energy_scan_widget", ())
        self.define_signal("populate_xrf_spectrum_widget", ())
        self.define_signal("populate_workflow_tab", ())
        self.define_signal("populate_advanced_widget", ())
        self.define_signal("populate_xray_imaging_widget", ())
        self.define_signal("selection_changed", ())
        self.define_signal("set_directory", ())
        self.define_signal("set_prefix", ())
        self.define_signal("set_sample", ())
        self.define_signal("get_tree_brick", ())
        self.define_signal("sample_mount_started", ())
        self.define_signal("sample_mount_finished", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("logged_in", ())
        self.define_slot("status_msg_changed", ())
        self.define_slot("sample_load_state_changed", ())
        self.define_slot("set_session", ())
        self.define_slot("get_selected_samples", ())
        self.define_slot("set_requested_tree_brick", ())

        # Graphic elements ----------------------------------------------------
        self.tools_menu = None
        self.queue_sync_action = None

        self.sample_changer_widget = QtImport.load_ui_file(
            "sample_changer_widget_layout.ui"
        )

        # self.refresh_pixmap = Icons.load("Refresh2.png")
        # self.sample_changer_widget.synch_button.setIcon(QtGui.QIcon(self.refresh_pixmap))
        # self.sample_changer_widget.synch_button.setText("Synch ISPyB")

        self.dc_tree_widget = DataCollectTree(self)
        self.dc_tree_widget.selection_changed_cb = self.selection_changed_cb
        self.dc_tree_widget.run_cb = self.run
        # self.dc_tree_widget.clear_centred_positions_cb = \
        #    self.clear_centred_positions

        # Layout --------------------------------------------------------------
        __main_layout = QtImport.QVBoxLayout(self)
        __main_layout.addWidget(self.sample_changer_widget)
        __main_layout.addWidget(self.dc_tree_widget)
        __main_layout.setSpacing(0)
        __main_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.sample_changer_widget.details_button.clicked.connect(
            self.toggle_sample_changer_tab
        )
        self.sample_changer_widget.filter_cbox.activated.connect(
            self.mount_mode_combo_changed
        )
        self.sample_changer_widget.centring_cbox.activated.connect(
            self.dc_tree_widget.set_centring_method
        )
        self.sample_changer_widget.synch_ispyb_button.clicked.connect(
            self.refresh_sample_list
        )
        # self.sample_changer_widget.tree_options_button.clicked.connect(\
        #     self.open_tree_options_dialog)
        self.sample_changer_widget.filter_combo.activated.connect(
            self.filter_combo_changed
        )
        self.sample_changer_widget.filter_ledit.textChanged.connect(
            self.filter_text_changed
        )
        self.sample_changer_widget.sample_combo.activated.connect(
            self.sample_combo_changed
        )

        # Other ---------------------------------------------------------------
        self.enable_collect(True)
        self.sample_changer_widget.synch_ispyb_button.setEnabled(False)
        #self.setSizePolicy(QtImport.QSizePolicy.Maximum, QtImport.QSizePolicy.Expanding)

        if HWR.beamline.sample_changer is not None:
            self.connect(
                HWR.beamline.sample_changer,
                SampleChanger.STATE_CHANGED_EVENT,
                self.sample_load_state_changed,
            )
            self.connect(
                HWR.beamline.sample_changer,
                SampleChanger.SELECTION_CHANGED_EVENT,
                self.sample_selection_changed,
            )
            self.connect(
                HWR.beamline.sample_changer,
                SampleChanger.INFO_CHANGED_EVENT,
                self.set_sample_pin_icon,
            )
            self.connect(
                HWR.beamline.sample_changer,
                SampleChanger.STATUS_CHANGED_EVENT,
                self.sample_changer_status_changed,
            )
        else:
            logging.getLogger("HWR").debug(
                "TreeBrick: Sample changer not available."
            )

        if HWR.beamline.plate_manipulator is not None:
            self.connect(
                HWR.beamline.plate_manipulator,
                SampleChanger.STATE_CHANGED_EVENT,
                self.sample_load_state_changed,
            )
            self.connect(
                HWR.beamline.plate_manipulator,
                SampleChanger.INFO_CHANGED_EVENT,
                self.plate_info_changed,
            )
            HWR.beamline.plate_manipulator.update_values()
        else:
            logging.getLogger("GUI").debug(
                "TreeBrick: plate manipulator hwobj not defined."
            )
        self.connect(
            HWR.beamline.sample_view, "shapeCreated", self.dc_tree_widget.shape_created
        )
        self.connect(
            HWR.beamline.sample_view,
            "shapeChanged",
            self.dc_tree_widget.shape_changed
        )
        self.connect(
            HWR.beamline.sample_view, "shapeDeleted", self.dc_tree_widget.shape_deleted
        )
        self.connect(
            HWR.beamline.sample_view,
            "diffractometerReady",
            self.diffractometer_ready_changed
        )
        self.connect(
            HWR.beamline.diffractometer,
            "newAutomaticCentringPoint",
            self.diffractometer_automatic_centring_done,
        )
        self.connect(
            HWR.beamline.diffractometer,
            "minidiffPhaseChanged",
            self.diffractometer_phase_changed,
        )
        self.diffractometer_phase_changed(
            HWR.beamline.diffractometer.get_current_phase()
        )

        self.connect(
            HWR.beamline.queue_manager,
            "show_workflow_tab",
            self.show_workflow_tab_from_model
        )
        self.connect(
            HWR.beamline.queue_manager,
            "queue_entry_execute_started",
            self.queue_entry_execution_started,
        )
        self.connect(
            HWR.beamline.queue_manager,
            "queue_entry_execute_finished",
            self.queue_entry_execution_finished,
        )
        self.connect(HWR.beamline.queue_manager, "queue_paused", self.queue_paused_handler)
        self.connect(
            HWR.beamline.queue_manager, "queue_execution_finished", self.queue_execution_finished
        )
        self.connect(HWR.beamline.queue_manager, "queue_stopped", self.queue_stop_handler)
        self.connect(HWR.beamline.queue_model, "child_added", self.dc_tree_widget.add_to_view)

        if hasattr(HWR.beamline, "ppu_control"):
            self.connect(
               HWR.beamline.ppu_control,
                "ppuStatusChanged",
                self.ppu_status_changed,
            )
            HWR.beamline.ppu_control.update_values()

        if HWR.beamline.safety_shutter is not None:
            self.connect(
                HWR.beamline.safety_shutter, "shutterStateChanged", self.shutter_state_changed
            )
            HWR.beamline.safety_shutter.update_values()

        if HWR.beamline.machine_info is not None:
            self.connect(
                HWR.beamline.machine_info, "machineCurrentChanged", self.machine_current_changed
            )

        has_shutter_less = HWR.beamline.detector.has_shutterless()
        if has_shutter_less:
            self.dc_tree_widget.confirm_dialog.disable_dark_current_cbx()

    def run(self):
        """Adds save, load and auto save menus to the menubar
           Emits signals to close tabs"""
        self.tools_menu = QtImport.QMenu("Queue", self)
        self.tools_menu.addAction("Save", self.save_queue)
        self.tools_menu.addAction("Load", self.load_queue)
        self.queue_autosave_action = self.tools_menu.addAction(
            "Auto save", self.queue_autosave_clicked
        )

        self.queue_autosave_action.setCheckable(True)
        self.queue_autosave_action.setChecked(self["enableQueueAutoSave"])
        self.queue_autosave_action.setEnabled(self["enableQueueAutoSave"])
        self.tools_menu.addSeparator()

        self.queue_undo_action = self.tools_menu.addAction(
            "Undo last action", self.queue_undo_clicked
        )
        self.queue_undo_action.setEnabled(False)
        self.queue_redo_action = self.tools_menu.addAction(
            "Redo last action", self.queue_redo_clicked
        )
        self.queue_redo_action.setEnabled(False)
        self.tools_menu.addSeparator()

        self.queue_sync_action = self.tools_menu.addAction(
            "Sync with ISPyB", self.queue_sync_clicked
        )
        self.queue_sync_action.setEnabled(False)

        if BaseWidget._menubar is not None:
            BaseWidget._menubar.insert_menu(self.tools_menu, 1)

        self.hide_dc_parameters_tab.emit(True)
        self.hide_dcg_tab.emit(True)
        self.hide_sample_centring_tab.emit(False)
        self.hide_char_parameters_tab.emit(True)
        self.hide_sample_changer_tab.emit(True)
        self.hide_plate_manipulator_tab.emit(True)
        self.hide_sample_tab.emit(True)
        self.hide_energy_scan_tab.emit(True)
        self.hide_xrf_spectrum_tab.emit(True)
        self.hide_workflow_tab.emit(True)
        self.hide_advanced_tab.emit(True)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "useFilterWidget":
            self.sample_changer_widget.filter_label.setVisible(new_value)
            self.sample_changer_widget.filter_ledit.setVisible(new_value)
            self.sample_changer_widget.filter_combo.setVisible(new_value)
        elif property_name == "useSampleWidget":
            self.sample_changer_widget.sample_label.setVisible(new_value)
            self.sample_changer_widget.sample_combo.setVisible(new_value)
        elif property_name == "useCentringMethods":
            self.sample_changer_widget.centring_cbox.setEnabled(new_value)
            self.sample_changer_widget.centring_mode_label.setEnabled(new_value)
        elif property_name == "xml_rpc_server":
            xml_rpc_server_hwobj = self.get_hardware_object(new_value)

            if xml_rpc_server_hwobj:
                self.connect(xml_rpc_server_hwobj, "add_to_queue", self.add_to_queue)
                self.connect(
                    xml_rpc_server_hwobj,
                    "start_queue",
                    self.dc_tree_widget.collect_items,
                )
                self.connect(
                    xml_rpc_server_hwobj, "open_dialog", self.open_xmlrpc_dialog
                )
        elif property_name == "hwobj_state_machine":
            self.state_machine_hwobj = self.get_hardware_object(
                new_value, optional=True
            )
        elif property_name == "redis_client":
            self.redis_client_hwobj = self.get_hardware_object(new_value, optional=True)
        elif property_name == "scOneName":
            self.sample_changer_widget.filter_cbox.setItemText(1, new_value)
        elif property_name == "scTwoName":
            self.sample_changer_widget.filter_cbox.setItemText(2, new_value)
        elif property_name == "usePlateNavigator":
            self.dc_tree_widget.plate_navigator_cbox.setVisible(new_value)
        elif property_name == "useHistoryView":
            # self.dc_tree_widget.history_tree_widget.setVisible(new_value)
            self.dc_tree_widget.history_enable_cbox.setVisible(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

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
        HWR.beamline.session.set_session_start_date(str(start_date))

    @QtImport.pyqtSlot()
    def set_requested_tree_brick(self):
        self.get_tree_brick.emit(self)

    @QtImport.pyqtSlot(bool)
    def logged_in(self, logged_in):
        """
        Connected to the signal loggedIn of ProposalBrick2.
        The signal is emitted when a user was succesfully logged in.
        At first free-pin mode is created
        Then it tries to initialize two sample changers and create
        two associated queue models.
        """

        self.is_logged_in = logged_in
        # self.enable_collect(logged_in)

        # if not logged_in:
        if True:
            self.dc_tree_widget.sample_mount_method = 0
            self.dc_tree_widget.populate_free_pin()
            self.dc_tree_widget.plate_navigator_cbox.setVisible(False)

            if (
                HWR.beamline.sample_changer is not None
                and HWR.beamline.diffractometer.use_sample_changer()
            ):
                sc_basket_content, sc_sample_content = self.get_sc_content()
                if sc_basket_content and sc_sample_content:
                    sc_basket_list, sc_sample_list = self.dc_tree_widget.samples_from_sc_content(
                        sc_basket_content, sc_sample_content
                    )
                    self.dc_tree_widget.sample_mount_method = 1
                    self.dc_tree_widget.populate_tree_widget(
                        sc_basket_list,
                        sc_sample_list,
                        self.dc_tree_widget.sample_mount_method,
                    )
                    self.sample_changer_widget.details_button.setText("Show SC-details")

            if (
                    HWR.beamline.plate_manipulator is not None
                    and HWR.beamline.diffractometer.in_plate_mode()
            ):
                if self["usePlateNavigator"]:
                    self.dc_tree_widget.plate_navigator_cbox.setVisible(True)
                plate_row_content, plate_sample_content = self.get_plate_content()
                if plate_sample_content:
                    plate_row_list, plate_sample_list = self.dc_tree_widget.samples_from_sc_content(
                        plate_row_content, plate_sample_content
                    )
                    self.dc_tree_widget.sample_mount_method = 2
                    self.dc_tree_widget.populate_tree_widget(
                        plate_row_list,
                        plate_sample_list,
                        self.dc_tree_widget.sample_mount_method,
                    )
                    self.sample_changer_widget.details_button.setText(
                        "Show Plate-details"
                    )

            self.sample_changer_widget.filter_cbox.setCurrentIndex(
                self.dc_tree_widget.sample_mount_method
            )
            self.dc_tree_widget.filter_sample_list(
                self.dc_tree_widget.sample_mount_method
            )

            if self.dc_tree_widget.sample_mount_method > 0:
                # Enable buttons related to sample changer
                self.sample_changer_widget.filter_cbox.setEnabled(True)
                self.sample_changer_widget.details_button.setEnabled(True)
                self.dc_tree_widget.scroll_to_item()
            if self.dc_tree_widget.sample_mount_method < 2 and logged_in:
                self.sample_changer_widget.synch_ispyb_button.setEnabled(True)

            if self.redis_client_hwobj is not None:
                self.redis_client_hwobj.load_graphics()

            self.load_queue()
            self.dc_tree_widget.samples_initialized = True

        # if not self.dc_tree_widget.samples_initialized
        #    self.dc_tree_widget.sample_tree_widget_selection()
        #    self.dc_tree_widget.set_sample_pin_icon()
        # self.dc_tree_widget.scroll_to_item()
        self.dc_tree_widget.update_basket_selection()

    def enable_collect(self, state):
        """
        Enables the collect controls.

        :param state: Enable if state is True and disable if False
        :type state: bool

        :returns: None
        """
        self.dc_tree_widget.enable_collect(state)

    def queue_entry_execution_started(self, queue_entry):
        self.current_queue_entry = queue_entry
        self.enable_widgets.emit(False)
        self.dc_tree_widget.queue_entry_execution_started(queue_entry)
        # BaseWidget.set_status_info("status", "Queue started", "running")

    def queue_entry_execution_finished(self, queue_entry, status):
        self.current_queue_entry = None
        self.dc_tree_widget.queue_entry_execution_finished(queue_entry, status)
        self.enable_widgets.emit(True)

        if queue_entry.get_type_str() not in ["Sample", "Basket", ""]:
            BaseWidget.set_status_info(
                "collect", "%s : %s" % (queue_entry.get_type_str(), status)
            )

    def queue_paused_handler(self, status):
        self.enable_widgets.emit(True)
        self.dc_tree_widget.queue_paused_handler(status)

    def queue_execution_finished(self, status):
        # self.enable_widgets.emit(True)
        self.current_queue_entry = None
        self.dc_tree_widget.queue_execution_completed(status)

    def queue_stop_handler(self, status):
        self.enable_widgets.emit(True)
        self.dc_tree_widget.queue_stop_handler(status)
        # BaseWidget.set_status_info("status", "Queue stoped")

    def diffractometer_ready_changed(self, status):
        self.diffractometer_ready.emit(HWR.beamline.diffractometer.is_ready())

        try:
            info_message = HWR.beamline.diffractometer.get_status()
        except AttributeError:
            info_message = None

        if info_message is None and status:
            info_message = "Ready"
            info_status = "ready"
        elif info_message is None:
            info_message = "Not ready"
            info_status = "running"
        else:
            info_status = "ready"

        BaseWidget.set_status_info("diffractometer", info_message, info_status)

    def diffractometer_automatic_centring_done(self, point):
        if self.dc_tree_widget.centring_method == CENTRING_METHOD.LOOP:
            message_box = QtImport.QMessageBox()
            message_box.setIcon(QtImport.QMessageBox.Question)
            message_box.setWindowTitle("Optical centring with user confirmation.")
            message_box.setText("Optical centring done. How to proceed?")
            message_box.addButton("Accept result", QtImport.QMessageBox.ApplyRole)
            message_box.addButton("Try again", QtImport.QMessageBox.RejectRole)

            if self.current_queue_entry:
                message_box.addButton(
                    "Skip following entry", QtImport.QMessageBox.NoRole
                )

            result = message_box.exec_()
            if result == QtImport.QMessageBox.AcceptRole:
                HWR.beamline.diffractometer.automatic_centring_try_count = 0
            elif result == QtImport.QMessageBox.RejectRole:
                logging.getLogger("GUI").info(
                    "Optical centring result rejected. " + "Trying once again."
                )
            else:
                HWR.beamline.diffractometer.automatic_centring_try_count = 0
                if self.current_queue_entry:
                    logging.getLogger("GUI").info(
                        "Optical centring rejected "
                        + "and the following queue entries skipped"
                    )
                    task_group_entry = self.current_queue_entry.get_container()
                    for child_entry in task_group_entry.get_queue_entry_list():
                        child_entry.set_enabled(False)

    def samples_from_lims(self, samples):
        barcode_samples, location_samples = self.dc_tree_widget.samples_from_lims(
            samples
        )
        l_samples = dict()

        # TODO: add test for sample changer type, here code is for Robodiff only
        for location, l_sample in location_samples.items():
            if l_sample.lims_location != (None, None):
                basket, sample = l_sample.lims_location
                cell = int(round((basket + 0.5) / 3.0))
                puck = basket - 3 * (cell - 1)
                new_location = (cell, puck, sample)
                l_sample.lims_location = new_location
                l_samples[new_location] = l_sample
                name = l_sample.get_name()
                l_sample.init_from_sc_sample([new_location])
                l_sample.set_name(name)

        return barcode_samples, l_samples

    def refresh_sample_list(self):
        """
        Retrives sample information from ISPyB and populates the sample list
        accordingly.
        """
        log = logging.getLogger("user_level_log")

        self.lims_samples = HWR.beamline.lims.get_samples(
            HWR.beamline.session.proposal_id, HWR.beamline.session.session_id
        )

        basket_list = []
        sample_list = []
        self.filtered_lims_samples = []
        sample_changer = None

        self.sample_changer_widget.sample_combo.clear()
        for sample in self.lims_samples:
            try:
                if sample.containerSampleChangerLocation:
                    self.filtered_lims_samples.append(sample)
                    item_text = "%s-%s" % (sample.proteinAcronym, sample.sampleName)
                    self.sample_changer_widget.sample_combo.addItem(item_text)
            except BaseException:
                pass

        self.sample_changer_widget.sample_label.setEnabled(True)
        self.sample_changer_widget.sample_combo.setEnabled(True)
        self.sample_changer_widget.sample_combo.setCurrentIndex(-1)

        if self.dc_tree_widget.sample_mount_method == 1:
            sample_changer = HWR.beamline.sample_changer
        elif self.dc_tree_widget.sample_mount_method == 2:
            sample_changer = HWR.beamline.plate_manipulator

        # if len(self.lims_samples) == 0:
        #    log.warning("No sample available in LIMS")
        #    self.mount_mode_combo_changed(self.sample_changer_widget.filter_cbox.currentIndex())
        #    return

        if sample_changer is not None:
            (barcode_samples, location_samples) = self.dc_tree_widget.samples_from_lims(
                self.lims_samples
            )
            sc_basket_content, sc_sample_content = self.get_sc_content()
            sc_basket_list, sc_sample_list = self.dc_tree_widget.samples_from_sc_content(
                sc_basket_content, sc_sample_content
            )

            basket_list = sc_basket_list

            # self.queue_sync_action.setEnabled(True)
            for sc_sample in sc_sample_list:
                # Get the sample in lims with the barcode
                # sc_sample.code
                lims_sample = barcode_samples.get(sc_sample.code)
                # There was a sample with that barcode
                if lims_sample:
                    if lims_sample.lims_location == sc_sample.location:
                        log.debug(
                            "Found sample in ISPyB for location %s"
                            % str(sc_sample.location)
                        )
                        sample_list.append(lims_sample)
                    else:
                        log.warning(
                            "The sample with the barcode (%s) exists" % sc_sample.code
                            + " in LIMS but the location does not mat"
                            + "ch. Sample changer location: %s, LIMS "
                            % sc_sample.location
                            + "location %s" % lims_sample.lims_location
                        )
                        sample_list.append(sc_sample)
                else:  # No sample with that barcode, continue with location
                    lims_sample = location_samples.get(sc_sample.location)
                    if lims_sample:
                        if lims_sample.lims_code:
                            log.warning(
                                "The sample has a barcode in LIMS, but "
                                + "the SC has no barcode information for "
                                + "this sample. For location: %s"
                                % str(sc_sample.location)
                            )
                            sample_list.append(lims_sample)
                        else:
                            log.debug(
                                "Found sample in ISPyB for location %s"
                                % str(sc_sample.location)
                            )
                            sample_list.append(lims_sample)
                    else:
                        if lims_sample:
                            if lims_sample.lims_location is not None:
                                log.warning(
                                    "No barcode was provided in ISPyB "
                                    + "which makes it impossible to verify if"
                                    + "the locations are correct, assuming "
                                    + "that the positions are correct."
                                )
                                sample_list.append(lims_sample)
                        else:
                            # log.warning("No sample in ISPyB for location %s" % \
                            #            str(sc_sample.location))
                            sample_list.append(sc_sample)
            self.dc_tree_widget.populate_tree_widget(
                basket_list, sample_list, self.dc_tree_widget.sample_mount_method
            )
            self.dc_tree_widget.de_select_items()

    def sample_combo_changed(self, index):
        """
        Assigns lims sample to manually-mounted sample
        """
        self.dc_tree_widget.filter_sample_list(0)
        root_model = HWR.beamline.queue_model.get_model_root()
        sample_model = root_model.get_children()[0]

        sample_model.init_from_lims_object(self.filtered_lims_samples[index])
        self.dc_tree_widget.sample_tree_widget.clear()
        self.dc_tree_widget.populate_free_pin(sample_model)

    def get_sc_content(self):
        """
        Gets the 'raw' data from the sample changer.

        :returns: A list with tuples, containing the sample information.
        """
        sc_basket_content = []
        sc_sample_content = []

        for basket in HWR.beamline.sample_changer.getBasketList():
            basket_index = basket.getIndex()
            basket_name = basket.getName()
            sc_basket_content.append((basket_index + 1, basket, basket_name))

        for sample in HWR.beamline.sample_changer.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            sample_index = sample.getIndex()
            sample_name = sample.getName()
            sc_sample_content.append(
                (matrix, basket_index + 1, sample_index + 1, sample_name)
            )
        return sc_basket_content, sc_sample_content

    def get_plate_content(self):
        """
        """
        plate_row_content = []
        plate_sample_content = []

        for row in HWR.beamline.plate_manipulator.getBasketList():
            row_index = row.getIndex()
            row_name = row.getName()
            plate_row_content.append((row_index, row, row_name))

        for sample in HWR.beamline.plate_manipulator.getSampleList():
            row_index = sample.getCell().getRowIndex()
            sample_name = sample.getName()
            coords = sample.getCoords()
            matrix = sample.getID() or ""
            plate_sample_content.append((matrix, coords[0], coords[1], sample_name))

        return plate_row_content, plate_sample_content

    def status_msg_changed(self, msg, color):
        """
        Status message from the SampleChangerBrick.

        :param msg: The message
        :type msg: str

        :returns: None
        """
        logging.getLogger("GUI").info(msg)

    def set_sample_pin_icon(self):
        """
        Updates the location of the sample pin when the
        matrix code information changes. The matrix code information
        is updated, but not exclusively, when a sample is changed.
        """
        self.dc_tree_widget.set_sample_pin_icon()

    def sample_load_state_changed(self, state, *args):
        """
        The state in the sample loading procedure changed.
        Ie from Loading to mounted

        :param state: str (Enumerable)
        :returns: None
        """
        s_color = SC_STATE_COLOR.get(state, "UNKNOWN")
        Colors.set_widget_color(
            self.sample_changer_widget.details_button, QtImport.QColor(s_color)
        )
        self.dc_tree_widget.scroll_to_item()
        if HWR.beamline.diffractometer.in_plate_mode():
            self.dc_tree_widget.plate_navigator_widget.refresh_plate_location()

    def sample_selection_changed(self):
        """
        Updates the selection of pucks. Method is called when the selection
        of pucks in the dewar has been changed.
        """
        self.dc_tree_widget.update_basket_selection()

    def sample_changer_status_changed(self, state):
        BaseWidget.set_status_info("sc", state)

    def plate_info_changed(self):
        self.set_sample_pin_icon()
        self.dc_tree_widget.plate_navigator_widget.refresh_plate_location()
        self.dc_tree_widget.scroll_to_item()

    def show_sample_centring_tab(self):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_sample_centring_tab.emit(False)

    def show_sample_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_sample_tab.emit(False)

    def show_dcg_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_dcg_tab.emit(False)
        self.populate_dc_group_tab(item)

    def populate_dc_group_tab(self, item=None):
        self.populate_dc_group_widget.emit(item)

    def show_datacollection_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_dc_parameters_tab.emit(False)
        self.populate_dc_parameters_tab(item)

    def populate_dc_parameters_tab(self, item=None):
        self.populate_dc_parameter_widget.emit(item)

    def show_char_parameters_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_char_parameters_tab.emit(False)

    def populate_char_parameters_tab(self, item):
        self.populate_char_parameter_widget.emit(item)

    def show_energy_scan_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_energy_scan_tab.emit(False)
        self.populate_energy_scan_tab(item)

    def populate_energy_scan_tab(self, item):
        self.populate_energy_scan_widget.emit(item)

    def show_xrf_spectrum_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_xrf_spectrum_tab.emit(False)
        self.populate_xrf_spectrum_tab(item)

    def populate_xrf_spectrum_tab(self, item):
        self.populate_xrf_spectrum_widget.emit(item)

    def show_advanced_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_advanced_tab.emit(False)
        self.populate_advanced_tab(item)

    def populate_advanced_tab(self, item):
        self.populate_advanced_widget.emit(item)

    def show_workflow_tab_from_model(self):
        self.show_workflow_tab(None)

    def show_workflow_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")

        running = HWR.beamline.queue_manager.is_executing()
        self.populate_workflow_tab(item, running=running)

    def populate_workflow_tab(self, item, running=False):
        self.populate_workflow_widget.emit(item, running)

    def show_xray_imaging_tab(self, item):
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.hide_xray_imaging_tab.emit(False)
        self.populate_xray_imaging_tab(item)

    def populate_xray_imaging_tab(self, item):
        self.populate_xray_imaging_widget.emit(item)

    def mount_mode_combo_changed(self, index):
        self.dc_tree_widget.filter_sample_list(index)
        self.sample_changer_widget.details_button.setEnabled(index > 0)
        self.sample_changer_widget.synch_ispyb_button.setEnabled(
            index < 2 and self.is_logged_in
        )
        # self.sample_changer_widget.sample_label.setEnabled(False)
        # self.sample_changer_widget.sample_combo.setEnabled(index == 0)
        if index == 0:
            self.hide_sample_changer_tab.emit(True)
            self.hide_plate_manipulator_tab.emit(True)

    def toggle_sample_changer_tab(self):
        if self.current_view == self.sample_changer_widget:
            self.current_view = None
            if self.dc_tree_widget.sample_mount_method == 1:
                self.hide_sample_changer_tab.emit(True)
                self.sample_changer_widget.details_button.setText("Show SC-details")
            else:
                self.hide_plate_manipulator_tab.emit(True)
                self.sample_changer_widget.details_button.setText("Show Plate-details")
            self.dc_tree_widget.sample_tree_widget_selection()
        else:
            self.current_view = self.sample_changer_widget
            self.hide_dc_parameters_tab.emit(True)
            self.hide_dcg_tab.emit(True)
            if self.dc_tree_widget.sample_mount_method == 1:
                self.hide_sample_changer_tab.emit(False)
                self.sample_changer_widget.details_button.setText("Hide SC-details")
            else:
                self.hide_plate_manipulator_tab.emit(False)
                self.sample_changer_widget.details_button.setText("Hide Plate-details")
            self.hide_sample_tab.emit(True)

    def selection_changed_cb(self, items):
        if len(items) == 1:
            item = items[0]
            if isinstance(item, queue_item.SampleQueueItem):
                self.populate_sample_details.emit(item.get_model())
                self.emit_set_sample(item)
                self.emit_set_directory()
                self.emit_set_prefix(item)
                # self.populate_edna_parameter_widget(item)
            elif isinstance(item, queue_item.DataCollectionQueueItem):
                data_collection = item.get_model()
                if data_collection.is_mesh():
                    self.populate_advanced_tab(item)
                else:
                    self.populate_dc_parameters_tab(item)
            elif isinstance(item, queue_item.CharacterisationQueueItem):
                self.populate_char_parameters_tab(item)
            elif isinstance(item, queue_item.EnergyScanQueueItem):
                self.populate_energy_scan_tab(item)
            elif isinstance(item, queue_item.XRFSpectrumQueueItem):
                self.populate_xrf_spectrum_tab(item)
            elif isinstance(item, queue_item.GenericWorkflowQueueItem):
                self.populate_workflow_tab(item)
            elif isinstance(item, queue_item.DataCollectionGroupQueueItem):
                self.populate_dc_group_tab(item)
            elif isinstance(item, queue_item.XrayCenteringQueueItem):
                self.populate_advanced_tab(item)
            elif isinstance(item, queue_item.XrayImagingQueueItem):
                self.populate_xray_imaging_tab(item)

        self.selection_changed.emit(items)

    def emit_set_directory(self):
        directory = str(HWR.beamline.session.get_base_image_directory())
        self.set_directory.emit(directory)

    def emit_set_prefix(self, item):
        prefix = HWR.beamline.session.get_default_prefix(item.get_model())
        self.set_prefix.emit(prefix)

    def emit_set_sample(self, item):
        self.set_sample.emit(item)

    def get_selected_items(self):
        items = self.dc_tree_widget.get_selected_items()
        return items

    def add_to_queue(self, task_list, parent_tree_item=None, set_on=True):
        if not parent_tree_item:
            parent_tree_item = self.dc_tree_widget.get_mounted_sample_item()
        self.dc_tree_widget.add_to_queue(task_list, parent_tree_item, set_on)

    def open_xmlrpc_dialog(self, dialog_dict):
        QtImport.QMessageBox.information(
            self,
            "Message from beamline operator",
            dialog_dict["msg"],
            QtImport.QMessageBox.Ok,
        )

    def select_last_added_item(self):
        self.dc_tree_widget.select_last_added_item()

    def filter_combo_changed(self, filter_index):
        """Filters sample treewidget based on the selected filter criteria:
           0 : No filter
           1 : Star
           2 : Sample name
           3 : Protein name
           4 : Basket index
           5 : Executed
           6 : Not executed
           7 : OSC
           8 : Helical
           9 : Characterisation
           10: Energy Scan
           11: XRF spectrum
        """
        self.sample_changer_widget.filter_ledit.setEnabled(filter_index in (2, 3, 4))
        self.clear_filter()
        if filter_index > 0:
            item_iterator = QtImport.QTreeWidgetItemIterator(
                self.dc_tree_widget.sample_tree_widget
            )
            item = item_iterator.value()
            while item:
                hide = False
                item_model = item.get_model()
                if filter_index == 1:
                    hide = not item.has_star()
                elif filter_index == 5:
                    if isinstance(item, queue_item.DataCollectionQueueItem):
                        hide = not item_model.is_executed()
                elif filter_index == 6:
                    if isinstance(item, queue_item.DataCollectionQueueItem):
                        hide = item_model.is_executed()
                elif filter_index == 7:
                    if isinstance(item, queue_item.DataCollectionQueueItem):
                        hide = item_model.is_helical()
                    else:
                        hide = True
                elif filter_index == 8:
                    if isinstance(item, queue_item.DataCollectionQueueItem):
                        hide = not item_model.is_helical()
                    else:
                        hide = True
                elif filter_index == 9:
                    hide = not isinstance(item, queue_item.CharacterisationQueueItem)
                elif filter_index == 10:
                    hide = not isinstance(item, queue_item.EnergyScanQueueItem)
                elif filter_index == 11:
                    hide = not isinstance(item, queue_item.XRFSpectrumQueueItem)
                # elif filter_index == 11:
                #    hide = not isinstance(item, queue_item.AdvancedQueueItem)
                if type(item) not in (
                    queue_item.TaskQueueItem,
                    queue_item.SampleQueueItem,
                    queue_item.BasketQueueItem,
                    queue_item.DataCollectionGroupQueueItem,
                ):
                    item.set_hidden(hide)
                item_iterator += 1
                item = item_iterator.value()

        self.dc_tree_widget.hide_empty_baskets()

    def filter_text_changed(self, new_text):
        item_iterator = QtImport.QTreeWidgetItemIterator(
            self.dc_tree_widget.sample_tree_widget
        )
        item = item_iterator.value()
        filter_index = self.sample_changer_widget.filter_combo.currentIndex()

        while item:
            hide = False
            new_text = str(new_text)
            if filter_index == 2:
                if isinstance(item, queue_item.SampleQueueItem):
                    hide = not new_text in item.text(0)
            elif filter_index == 3:
                if isinstance(item, queue_item.SampleQueueItem):
                    hide = not new_text in item.get_model().crystals[0].protein_acronym
            elif filter_index == 4:
                if isinstance(item, queue_item.BasketQueueItem):
                    if new_text.isdigit():
                        # Display one basket
                        hide = int(new_text) != item.get_model().location[0]
                    else:
                        # Display several baskets. Separated with ","
                        enable_baskat_list = new_text.split(",")
                        if len(enable_baskat_list) > 1:
                            hide = (
                                item.get_model().location[0] not in enable_baskat_list
                            )
            item.set_hidden(hide)
            item_iterator += 1
            item = item_iterator.value()

        if filter_index != 3:
            self.dc_tree_widget.hide_empty_baskets()

    def clear_filter(self):
        item_iterator = QtImport.QTreeWidgetItemIterator(
            self.dc_tree_widget.sample_tree_widget
        )
        item = item_iterator.value()
        while item:
            item.set_hidden(False)
            item_iterator += 1
            item = item_iterator.value()

    def diffractometer_phase_changed(self, phase):
        if self.enable_collect_conditions.get("diffractometer") != (
            phase != "BeamLocation"
        ):
            self.enable_collect_conditions["diffractometer"] = phase != "BeamLocation"
        if phase:
            self.update_enable_collect()

    def ppu_status_changed(self, in_error, status_msg):
        if self.enable_collect_conditions.get("ppu") != (in_error != True):
            self.enable_collect_conditions["ppu"] = in_error != True
            self.update_enable_collect()

    def shutter_state_changed(self, state, msg=None):
        # NBNB TODO HACK.
        #  Necessary because shutter states can be both 'opened', 'OPEN'. (and more?)
        # NBNB fixme
        #is_open = bool(state and state.lower().startswith('open'))
        is_open = bool(state and state.name.lower().startswith('open'))
        if self.enable_collect_conditions.get("shutter") != is_open:
            self.enable_collect_conditions["shutter"] = is_open
            self.update_enable_collect()

    def machine_current_changed(self, value, in_range):
        return
        if self.enable_collect_conditions.get("machine_current") != in_range:
            self.enable_collect_conditions["machine_current"] = in_range
            self.update_enable_collect()

    def update_enable_collect(self):
        if self.current_queue_entry is not None:
            #Do not enable/disable collect button if queue is executing
            return

        # Do not allow to start xray imaging from BeamLocation and DataCollection phase
        self.enable_collect_conditions["imaging"] = True
        for item in self.get_selected_items():
            if isinstance(
                item, queue_item.XrayImagingQueueItem
            ) and HWR.beamline.diffractometer.get_current_phase() in (
                "BeamLocation",
                "DataCollection",
            ):
                self.enable_collect_conditions["imaging"] = False

        enable_collect = all(
            item == True for item in self.enable_collect_conditions.values()
        )

        if enable_collect != self.dc_tree_widget.enable_collect_condition:
            if enable_collect:
                logging.getLogger("GUI").info("Data collection is enabled")
            else:
                msg = ""
                logging.getLogger("GUI").warning("Data collect is disabled")
                for key, value in self.enable_collect_conditions.items():
                    if value == False:
                        if key == "diffractometer":
                            logging.getLogger("GUI").warning(
                                "  - Diffractometer is in beam location phase"
                            )
                        elif key == "shutter":
                            logging.getLogger("GUI").warning(
                                "  - Safety shutter is closed "
                                + "(Open the safety shutter to enable collections)"
                            )
                        elif key == "ppu":
                            logging.getLogger("GUI").error("  - PPU is in error state")
                        elif key == "machine_current":
                            logging.getLogger("GUI").error(
                                "  - Machine current is to low "
                                + "(Wait till the machine current reaches 90 mA)"
                            )
                        elif key == "imaging":
                            logging.getLogger("GUI").warning(
                                "To start an imaging collection "
                                + "diffractometer has to be in SampleCentering or in Transfer phase"
                            )
            self.dc_tree_widget.enable_collect_condition = enable_collect
            self.dc_tree_widget.toggle_collect_button_enabled()

    def save_queue(self):
        """Saves queue in the file"""
        if self.redis_client_hwobj is not None:
            self.redis_client_hwobj.save_queue()
        # else:
        #    self.dc_tree_widget.save_queue()

    def auto_save_queue(self):
        """Saves queue in the file"""
        if self.queue_autosave_action is not None:
            if (
                self.queue_autosave_action.isChecked()
                and self.dc_tree_widget.samples_initialized
            ):
                if self.redis_client_hwobj is not None:
                    self.redis_client_hwobj.save_queue()
                # else:
                #    self.dc_tree_widget.save_queue()

    def load_queue(self):
        """Loads queue from file"""

        loaded_model = None
        if self.redis_client_hwobj is not None:
            loaded_model = self.redis_client_hwobj.load_queue()

            if loaded_model is not None:
                self.dc_tree_widget.sample_tree_widget.clear()
                model_map = {"free-pin": 0, "ispyb": 1, "plate": 2}
                self.sample_changer_widget.filter_cbox.setCurrentIndex(
                    model_map[loaded_model]
                )
                self.mount_mode_combo_changed(model_map[loaded_model])
                self.select_last_added_item()
                self.dc_tree_widget.scroll_to_item(self.dc_tree_widget.last_added_item)

        return loaded_model

    def queue_autosave_clicked(self):
        """Enable/disable queue autosave"""
        pass

    def queue_undo_clicked(self):
        """If queue autosave is enabled then undo last change"""

        self.dc_tree_widget.undo_queue()

    def queue_redo_clicked(self):
        """If queue autosave is enable then redo last changed"""

        self.dc_tree_widget.redo_queue()

    def queue_sync_clicked(self):
        """Add diffraction plan from ISPyB to all samples"""
        self.dc_tree_widget.sample_tree_widget.selectAll()
        self.dc_tree_widget.sync_diffraction_plan()

    def data_path_changed(self, conflict):
        """Data path changed event. Used in state machine"""
        self.dc_tree_widget.item_parameters_changed()
        self.set_condition_state("data_path_valid", not conflict)

    def acq_parameters_changed(self, conflict):
        """Acq parameter changed event. Used in state machine"""
        self.dc_tree_widget.item_parameters_changed()
        self.set_condition_state("acq_parameters_valid", len(conflict) == 0)

    def set_condition_state(self, condition_name, value):
        """Sets condition to defined state"""
        if self.state_machine_hwobj is not None:
            self.state_machine_hwobj.condition_changed(condition_name, value)
