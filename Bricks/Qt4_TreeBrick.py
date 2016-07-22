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

import os
import logging
from collections import namedtuple

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import Qt4_queue_item
from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_dc_tree_widget import DataCollectTree
from Qt4_sample_changer_helper import SC_STATE_COLOR, SampleChanger
from widgets.Qt4_tree_options_dialog import TreeOptionsDialog


__category__ = 'General'


#ViewType = namedtuple('ViewType', ['ISPYB', 'MANUAL', 'SC'])
#TREE_VIEW_TYPE = ViewType(0, 1, 2)


class Qt4_TreeBrick(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None
        self.session_hwobj = None
        self.lims_hwobj = None
        self.sample_changer_hwobj = None
        self.plate_manipulator_hwobj = None
        self.queue_hwobj = None

        # Internal variables --------------------------------------------------
        self.enable_collect_conditions = {}
        self.current_view = None
        self.lims_samples = None
        self.filtered_lims_samples = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("holderLengthMotor", "string", "")
        self.addProperty("queue", "string", "/queue")
        self.addProperty("queue_model", "string", "/queue-model")
        self.addProperty("beamline_setup", "string", "/beamline-setup")
        self.addProperty("xml_rpc_server", "string", "/xml_rpc_server")
        self.addProperty("useFilterWidget", "boolean", True)
        self.addProperty("useSampleWidget", "boolean", True)
        self.addProperty("scOneName", "string", "Sample changer")
        self.addProperty("scTwoName", "string", "Plate")

        # Signals ------------------------------------------------------------
        self.defineSignal("enable_hutch_menu", ())
        self.defineSignal("enable_command_menu", ())
        self.defineSignal("enable_task_toolbox", ())
        self.defineSignal("queue_is_executing", ())

        # Hiding and showing the tabs
        self.defineSignal("hide_sample_tab", ())
        self.defineSignal("hide_dc_parameters_tab", ())
        self.defineSignal("hide_sample_centring_tab", ())
        self.defineSignal("hide_dcg_tab", ())
        self.defineSignal("hide_sample_changer_tab", ())
        self.defineSignal("hide_plate_manipulator_tab", ())
        self.defineSignal("hide_char_parameters_tab", ())
        self.defineSignal("hide_energy_scan_tab",())
        self.defineSignal("hide_xrf_spectrum_tab",())
        self.defineSignal("hide_workflow_tab", ())
        self.defineSignal("hide_advanced_tab", ())

        # Populating the tabs with data
        self.defineSignal("populate_dc_parameter_widget", ())
        self.defineSignal("populate_dc_group_widget", ())
        self.defineSignal("populate_char_parameter_widget",())
        self.defineSignal("populate_sample_details",())
        self.defineSignal("populate_energy_scan_widget", ())
        self.defineSignal("populate_xrf_spectrum_widget", ())
        self.defineSignal("populate_workflow_tab", ())
        self.defineSignal("populate_advanced_widget", ())

        # Handle selection
        self.defineSignal("selection_changed",())
        self.defineSignal("set_directory", ())
        self.defineSignal("set_prefix", ())
        self.defineSignal("set_sample", ())

        # Slots ---------------------------------------------------------------
        self.defineSlot("logged_in", ())
        self.defineSlot("status_msg_changed", ())
        self.defineSlot("sample_load_state_changed", ())
        self.defineSlot("set_session", ())

        self.defineSlot("get_tree_brick",())
        self.defineSlot("get_selected_samples", ())

        #self.defineSlot("get_mounted_sample", ())
        #self.defineSlot("new_centred_position", ())
        #self.defineSlot("add_dcg", ())
        #self.defineSlot("add_data_collection", ())
        #self.defineSlot("set_session", ())

        # Graphic elements ----------------------------------------------------
        self.sample_changer_widget = uic.loadUi(os.path.join(\
             os.path.dirname(__file__),
             "widgets/ui_files/Qt4_sample_changer_widget_layout.ui"))

        #self.refresh_pixmap = Qt4_Icons.load("Refresh2.png")
        #self.sample_changer_widget.synch_button.setIcon(QtGui.QIcon(self.refresh_pixmap))
        #self.sample_changer_widget.synch_button.setText("Synch ISPyB")

        self.dc_tree_widget = DataCollectTree(self)
        self.dc_tree_widget.selection_changed_cb = self.selection_changed
        self.dc_tree_widget.run_cb = self.run
        #self.dc_tree_widget.clear_centred_positions_cb = \
        #    self.clear_centred_positions
        self.tree_options_dialog = TreeOptionsDialog(self, 'Tree options Dialog')
        self.tree_options_dialog.setModal(True)

        # Layout --------------------------------------------------------------
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addWidget(self.sample_changer_widget)
        main_layout.addWidget(self.dc_tree_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0) 

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.sample_changer_widget.details_button.clicked.connect(\
             self.toggle_sample_changer_tab)
        self.sample_changer_widget.filter_cbox.activated.connect(\
             self.mount_mode_combo_changed)
        self.sample_changer_widget.centring_cbox.activated.connect(\
             self.dc_tree_widget.set_centring_method)
        self.sample_changer_widget.synch_ispyb_button.clicked.connect(\
             self.refresh_sample_list)
        #self.sample_changer_widget.tree_options_button.clicked.connect(\
        #     self.open_tree_options_dialog)
        self.sample_changer_widget.filter_combo.activated.connect(\
             self.filter_combo_changed)
        self.sample_changer_widget.filter_ledit.textChanged.connect(\
             self.filter_text_changed)
        self.sample_changer_widget.sample_combo.activated.connect(\
             self.sample_combo_changed)

        # Other --------------------------------------------------------------- 
        self.enable_collect(False)
        #self.setFixedWidth(315) 
        self.dc_tree_widget.set_centring_method(1)

    # Framework 2 method
    def run(self):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_centring_tab"), False)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True) 
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)

    # Framework 2 method
    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        """
        if property_name == 'holder_length_motor':
            self.dc_tree_widget.hl_motor_hwobj = self.getHardwareObject(new_value)
        elif property_name == "useFilterWidget":
            self.sample_changer_widget.filter_label.setVisible(new_value)
            self.sample_changer_widget.filter_ledit.setVisible(new_value)
            self.sample_changer_widget.filter_combo.setVisible(new_value)
        elif property_name == "useSampleWidget":
            self.sample_changer_widget.sample_label.setVisible(new_value)
            self.sample_changer_widget.sample_combo.setVisible(new_value)
        elif property_name == 'queue':            
            self.queue_hwobj = self.getHardwareObject(new_value)
            self.dc_tree_widget.queue_hwobj = self.queue_hwobj
            self.connect(self.queue_hwobj, 'show_workflow_tab',
                         self.show_workflow_tab_from_model)

            self.connect(self.queue_hwobj, 'queue_entry_execute_started',
                         self.queue_entry_execution_started)

            self.connect(self.queue_hwobj, 'queue_entry_execute_finished',
                         self.queue_entry_execution_finished)

            self.connect(self.queue_hwobj, 'queue_paused', 
                         self.queue_paused_handler)

            self.connect(self.queue_hwobj, 'queue_execution_finished', 
                         self.queue_execution_finished)

            self.connect(self.queue_hwobj, 'queue_stopped', 
                         self.queue_stop_handler)
        elif property_name == 'queue_model':
            self.queue_model_hwobj = self.getHardwareObject(new_value)

            self.dc_tree_widget.queue_model_hwobj = self.queue_model_hwobj
            self.dc_tree_widget.confirm_dialog.queue_model_hwobj = self.queue_model_hwobj
            self.connect(self.queue_model_hwobj, 'child_added',
                         self.dc_tree_widget.add_to_view)
        elif property_name == 'beamline_setup':
            bl_setup = self.getHardwareObject(new_value)
            self.dc_tree_widget.beamline_setup_hwobj = bl_setup
            self.diffractometer_hwobj = bl_setup.diffractometer_hwobj
            self.session_hwobj = bl_setup.session_hwobj
            self.lims_hwobj = bl_setup.lims_client_hwobj

            try:
               self.sample_changer_hwobj = bl_setup.sample_changer_hwobj
            except AttributeError:
               logging.getLogger("GUI").\
                    debug("Qt4_TreeBrick: sample changer hwobj not defined.")
               self.sample_changer_hwobj = None
            try:
               self.plate_manipulator_hwobj = bl_setup.plate_manipulator_hwobj
               logging.getLogger("GUI").\
                    debug("Qt4_TreeBrick: plate manipulator hwobj not defined.")
            except:
               self.plate_manipulator_hwobj = None 

            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, 
                             SampleChanger.STATE_CHANGED_EVENT,
                             self.sample_load_state_changed)
                self.connect(self.sample_changer_hwobj,
                             SampleChanger.INFO_CHANGED_EVENT, 
                             self.set_sample_pin_icon)
            if self.plate_manipulator_hwobj is not None:
                self.connect(self.plate_manipulator_hwobj,
                             SampleChanger.STATE_CHANGED_EVENT,
                             self.sample_load_state_changed)
                self.connect(self.plate_manipulator_hwobj,
                             SampleChanger.INFO_CHANGED_EVENT,
                             self.set_sample_pin_icon)

            # This is to enable/disable collection button
            # Could be much more generic
            if hasattr(bl_setup, "diffractometer_hwobj"):
                self.connect(bl_setup.diffractometer_hwobj, 
                             "minidiffPhaseChanged",
                             self.diffractometer_phase_changed)
                self.diffractometer_phase_changed(\
                     bl_setup.diffractometer_hwobj.get_current_phase())

            if hasattr(bl_setup, "ppu_control_hwobj"):
                self.connect(bl_setup.ppu_control_hwobj,
                             'ppuStatusChanged',
                             self.ppu_status_changed)
                bl_setup.ppu_control_hwobj.update_values()
            if hasattr(bl_setup, "safety_shutter_hwobj"):
                self.connect(bl_setup.safety_shutter_hwobj,
                             'shutterStateChanged',
                             self.shutter_state_changed)
                self.shutter_state_changed(bl_setup.safety_shutter_hwobj.getShutterState())

            has_shutter_less = bl_setup.detector_has_shutterless()
            if has_shutter_less:
                self.dc_tree_widget.confirm_dialog.disable_dark_current_cbx()
        elif property_name == 'xml_rpc_server':
            xml_rpc_server_hwobj = self.getHardwareObject(new_value)

            if xml_rpc_server_hwobj:
                self.connect(xml_rpc_server_hwobj,
                             'add_to_queue',
                             self.add_to_queue)
                self.connect(xml_rpc_server_hwobj,
                             'start_queue',
                             self.dc_tree_widget.collect_items)
        elif property_name == 'scOneName':
              self.sample_changer_widget.filter_cbox.setItemText(1, new_value)
        elif property_name == 'scTwoName':
              self.sample_changer_widget.filter_cbox.setItemText(2, new_value) 
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def set_session(self, session_id, t_prop_code = None, prop_number = None,
                    prop_id = None, start_date = None, prop_code = None,
                    is_inhouse = None):
        """
        Descript. :
        """
        self.session_hwobj.set_session_start_date(start_date)

    def logged_in(self, logged_in):
        """
        Descript. :Connected to the signal loggedIn of ProposalBrick2.
                   The signal is emitted when a user was succesfully logged in.
                   At first free-pin mode is created
                   Then it tries to initialize two sample changers and create
                   two associated queue models.
        """
        self.enable_collect(logged_in)
        if not logged_in:
            self.dc_tree_widget.sample_mount_method = 0
            self.dc_tree_widget.populate_free_pin()
         
            if self.sample_changer_hwobj is not None and \
               self.diffractometer_hwobj.use_sample_changer():
                sc_basket_content, sc_sample_content = self.get_sc_content()
                if sc_basket_content and sc_sample_content:
                    sc_basket_list, sc_sample_list = self.dc_tree_widget.\
                         samples_from_sc_content(sc_basket_content, sc_sample_content)
                    self.dc_tree_widget.sample_mount_method = 1
                    self.dc_tree_widget.populate_tree_widget(sc_basket_list, sc_sample_list, 
                         self.dc_tree_widget.sample_mount_method)
                    self.sample_changer_widget.details_button.setText("Show SC-details")
   
            if self.plate_manipulator_hwobj is not None and \
               self.diffractometer_hwobj.in_plate_mode():
                plate_row_content, plate_sample_content = self.get_plate_content()
                self.dc_tree_widget.beamline_setup_hwobj.set_plate_mode(True)
                if plate_sample_content:
                     plate_row_list, plate_sample_list = self.dc_tree_widget.\
                        samples_from_sc_content(plate_row_content, plate_sample_content)
                     self.dc_tree_widget.sample_mount_method = 2
                     self.dc_tree_widget.populate_tree_widget(plate_row_list, 
                         plate_sample_list, self.dc_tree_widget.sample_mount_method)
                     self.sample_changer_widget.details_button.setText("Show Plate-details")

            self.sample_changer_widget.filter_cbox.setCurrentIndex(\
                 self.dc_tree_widget.sample_mount_method)
            self.dc_tree_widget.filter_sample_list(\
                 self.dc_tree_widget.sample_mount_method)

            if self.dc_tree_widget.sample_mount_method > 0:
                #Enable buttons related to sample changer
                self.sample_changer_widget.filter_cbox.setEnabled(True)
                self.sample_changer_widget.details_button.setEnabled(True)
            if self.dc_tree_widget.sample_mount_method < 2:
                self.sample_changer_widget.synch_ispyb_button.setEnabled(True)

        self.dc_tree_widget.sample_tree_widget_selection()
        self.dc_tree_widget.set_sample_pin_icon()

    def enable_collect(self, state):
        """
        Enables the collect controls.

        :param state: Enable if state is True and disable if False
        :type state: bool

        :returns: None
        """
        self.dc_tree_widget.enable_collect(state)

    def enable_hutch_menu(self, state):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("enable_hutch_menu"), state)

    def enable_command_menu(self, state):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("enable_command_menu"), state)

    def enable_task_toolbox(self, state):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("enable_task_toolbox"), state)

    def get_tree_brick(self, tree_brick):
        """
        Gets the reference to the tree brick. Used to get a reference from
        another brick via the signal get_tree_brick. The attribute tree_brick
        of the passed dictionary will contain the reference.

        :param tree_brick: A dictonary to contain the reference.
        :type tree_brick: dict

        :returns: None
        """
        tree_brick['tree_brick'] = self

    def queue_entry_execution_started(self, queue_entry):
        self.emit(QtCore.SIGNAL("queue_is_executing"), True)
        self.dc_tree_widget.queue_entry_execution_started(queue_entry)

    def queue_entry_execution_finished(self, queue_entry, status):
        self.dc_tree_widget.queue_entry_execution_finished(queue_entry, status)

    def queue_paused_handler(self, status):
        self.dc_tree_widget.queue_paused_handler(status)

    def queue_execution_finished(self, status):
        self.emit(QtCore.SIGNAL("queue_is_executing"), False)
        self.dc_tree_widget.queue_execution_completed(status)

    def queue_stop_handler(self, status):
        self.emit(QtCore.SIGNAL("queue_is_executing"), False)
        self.dc_tree_widget.queue_stop_handler(status)

    def samples_from_lims(self, samples):
        """
        Descript. :
        """
        barcode_samples, location_samples = \
            self.dc_tree_widget.samples_from_lims(samples)
        l_samples = dict()            
   
        # TODO: add test for sample changer type, here code is for Robodiff only
        for location, l_sample in location_samples.iteritems():
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
        lims_client = self.lims_hwobj
        log = logging.getLogger("GUI") 

        self.lims_samples = lims_client.get_samples(\
             self.session_hwobj.proposal_id,
             self.session_hwobj.session_id)

        basket_list = []
        sample_list = []        
        self.filtered_lims_samples = [] 
        sample_changer = None

        self.sample_changer_widget.sample_combo.clear()
        for sample in self.lims_samples:
            if sample.containerSampleChangerLocation:
                self.filtered_lims_samples.append(sample)
                item_text = "%s-%s" %(sample.proteinAcronym, sample.sampleName)
                if sample.code:
                    item_text += " (%s)" % sample.code
                self.sample_changer_widget.sample_combo.addItem(item_text)
        self.sample_changer_widget.sample_combo.setEnabled(True)
        self.sample_changer_widget.sample_combo.setCurrentIndex(-1)
                 
        if self.dc_tree_widget.sample_mount_method == 1:
            sample_changer = self.sample_changer_hwobj
        elif self.dc_tree_widget.sample_mount_method == 2:
            sample_changer = self.plate_manipulator_hwobj
     
        if self.lims_samples and sample_changer is not None:
            (barcode_samples, location_samples) = \
             self.dc_tree_widget.samples_from_lims(self.lims_samples)
            sc_basket_content, sc_sample_content = self.get_sc_content()
            sc_basket_list, sc_sample_list = self.dc_tree_widget.\
              samples_from_sc_content(sc_basket_content, sc_sample_content)

            basket_list = sc_basket_list
            for sc_sample in sc_sample_list:
                # Get the sample in lims with the barcode
                # sc_sample.code
                lims_sample = barcode_samples.get(sc_sample.code)
                # There was a sample with that barcode
                if lims_sample:
                    if lims_sample.lims_location == sc_sample.location:
                        log.debug("Found sample in ISPyB for location %s" % \
                                  str(sc_sample.location))
                        sample_list.append(lims_sample)
                    else:
                        log.warning("The sample with the barcode (%s) exists" + \
                                    " in LIMS but the location does not mat"  + \
                                    "ch. Sample changer location: %s, LIMS "  + \
                                    "location %s" % (sc_sample.code,
                                                     sc_sample.location,
                                                     lims_sample.lims_location))
                        sample_list.append(sc_sample)
                else: # No sample with that barcode, continue with location
                    lims_sample = location_samples.get(sc_sample.location)
                    if lims_sample:
                        if lims_sample.lims_code:
                            log.warning("The sample has a barcode in LIMS, but " + \
                                        "the SC has no barcode information for " + \
                                        "this sample. For location: %s" % \
                                        str(sc_sample.location))
                            sample_list.append(lims_sample)
                        else:
                            log.debug("Found sample in ISPyB for location %s" % \
                                      str(sc_sample.location))
                            sample_list.append(lims_sample)
                    else:
                        if lims_sample:
                            if lims_sample.lims_location != None:
                                log.warning("No barcode was provided in ISPyB " + \
                                            "which makes it impossible to verify if" + \
                                            "the locations are correct, assuming " + \
                                            "that the positions are correct.")
                                sample_list.append(lims_sample)
                        else:
                            log.warning("No sample in ISPyB for location %s" % \
                                        str(sc_sample.location))
                            sample_list.append(sc_sample)
            self.dc_tree_widget.populate_tree_widget(basket_list, sample_list, 
                 self.dc_tree_widget.sample_mount_method)
            self.dc_tree_widget.de_select_items()

    def sample_combo_changed(self, index):
        """
        Assigns lims sample to manually-mounted sample
        """
        self.dc_tree_widget.filter_sample_list(0)
        root_model = self.queue_model_hwobj.get_model_root()
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

        for basket in self.sample_changer_hwobj.getBasketList():
            basket_index = basket.getIndex()
            basket_code = basket.getID() or ""
            basket_name = basket.getName()
            is_present = basket.isPresent()
            sc_basket_content.append((basket_index+1, basket, basket_name))
             
        for sample in self.sample_changer_hwobj.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            sample_index = sample.getIndex()
            basket_code = sample.getContainer().getID() or ""
            sample_name = sample.getName()
            sc_sample_content.append((matrix, basket_index + 1, 
                                      sample_index + 1, sample_name))
        return sc_basket_content, sc_sample_content

    def get_plate_content(self):
        """
        """
        plate_row_content = []
        plate_sample_content = []

        for row in self.plate_manipulator_hwobj.getBasketList():
            row_index = row.getIndex() 
            row_code = row.getID() or ""
            row_name = row.getName()
            is_present = row.isPresent()
            plate_row_content.append((row_index, row, row_name))

        for sample in self.plate_manipulator_hwobj.getSampleList():
            row_index = sample.getCell().getRowIndex()
            col_index = sample.getCell().getCol()
            drop_index = sample.getDrop().getWellNo()
            sample_name = sample.getName()
            coords = sample.getCoords()
            matrix = sample.getID() or ""
            #vial_index = ":".join(map(str, coords[1:]))
            plate_sample_content.append((matrix, coords[0], 
                                         coords[1], sample_name))
 
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
        Qt4_widget_colors.set_widget_color(self.sample_changer_widget.details_button,
                                           QtGui.QColor(s_color))

    def show_sample_centring_tab(self):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_centring_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)

    def show_sample_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("populate_sample_details"), item.get_model())
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_centring_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)

    def show_dcg_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)

    def populate_dc_parameters_tab(self, item = None):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_dc_parameter_widget"), item)
        
    def show_datacollection_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)
        self.populate_dc_parameters_tab(item)

    def populate_dc_group_tab(self, item = None):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_dc_group_widget"), item)

    def show_char_parameters_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), False)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)
        self.populate_char_parameters_tab(item)

    def populate_char_parameters_tab(self, item):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_char_parameter_widget"), item)

    def show_energy_scan_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True) 
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), False)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)
        self.populate_energy_scan_tab(item)

    def populate_energy_scan_tab(self, item):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_energy_scan_widget"), item)

    def show_xrf_spectrum_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), False)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)
        self.populate_xrf_spectrum_tab(item)

    def populate_xrf_spectrum_tab(self, item):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_xrf_spectrum_widget"), item)

    def show_advanced_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), True)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), True)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), False)
        self.populate_advanced_widget(item)

    def populate_advanced_widget(self, item):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_advanced_widget"), item)

    def show_workflow_tab_from_model(self):
        """
        Descript. :
        """
        self.show_workflow_tab(None)
        
    def show_workflow_tab(self, item):
        """
        Descript. :
        """
        self.sample_changer_widget.details_button.setText("Show SC-details")
        self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
        self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
        self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        self.emit(QtCore.SIGNAL("hide_char_parameters_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_tab"), True) 
        self.emit(QtCore.SIGNAL("hide_energy_scan_tab"), True)
        self.emit(QtCore.SIGNAL("hide_xrf_spectrum_tab"), False)
        self.emit(QtCore.SIGNAL("hide_workflow_tab"), False)
        self.emit(QtCore.SIGNAL("hide_advanced_tab"), True)

        running = self.queue_hwobj.is_executing() 
        self.populate_workflow_tab(item, running=running)

    def populate_workflow_tab(self, item, running = False):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("populate_workflow_tab"), item, running)

    def mount_mode_combo_changed(self, index):
        self.dc_tree_widget.filter_sample_list(index)
        self.sample_changer_widget.details_button.setEnabled(index > 0) 
        self.sample_changer_widget.synch_ispyb_button.setEnabled(index < 2)
        self.sample_changer_widget.sample_label.setEnabled(index == 0)
        self.sample_changer_widget.sample_combo.setEnabled(index == 0)
        if index == 0:
            self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
            self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
        
    def toggle_sample_changer_tab(self): 
        """
        Descript. :
        """
        if self.current_view == self.sample_changer_widget:
            self.current_view = None
            if self.dc_tree_widget.sample_mount_method == 1:
                self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), True)
                self.sample_changer_widget.details_button.setText("Show SC-details")
            else:
                self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), True)
                self.sample_changer_widget.details_button.setText("Show Plate-details")
            self.dc_tree_widget.sample_tree_widget_selection()
        else:
            self.current_view = self.sample_changer_widget
            self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
            self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
            if self.dc_tree_widget.sample_mount_method == 1:
                self.emit(QtCore.SIGNAL("hide_sample_changer_tab"), False)
                self.sample_changer_widget.details_button.setText("Hide SC-details")
            else:
                self.emit(QtCore.SIGNAL("hide_plate_manipulator_tab"), False)
                self.sample_changer_widget.details_button.setText("Hide Plate-details")
            self.emit(QtCore.SIGNAL("hide_sample_tab"), True)
        
    def selection_changed(self, items):
        """
        Descript. :
        """
        if len(items) == 1:
            item = items[0]
            if isinstance(item, Qt4_queue_item.SampleQueueItem):
                self.emit(QtCore.SIGNAL("populate_sample_details"), item.get_model())
                self.emit_set_sample(item)
                self.emit_set_directory()
                self.emit_set_prefix(item)
                #self.populate_edna_parameter_widget(item)
            elif isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                data_collection = item.get_model()
                if data_collection.is_mesh():
                    self.populate_advanced_widget(item)
                else:
                    self.populate_dc_parameters_tab(item)
            elif isinstance(item, Qt4_queue_item.CharacterisationQueueItem):
                self.populate_char_parameters_tab(item)
            elif isinstance(item, Qt4_queue_item.EnergyScanQueueItem):
                self.populate_energy_scan_tab(item)
            elif isinstance(item, Qt4_queue_item.XRFSpectrumQueueItem):
                self.populate_xrf_spectrum_tab(item)
            elif isinstance(item, Qt4_queue_item.GenericWorkflowQueueItem):
                self.populate_workflow_tab(item)
            elif isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                self.populate_dc_group_tab(item)

        self.emit(QtCore.SIGNAL("selection_changed"), items)

    def emit_set_directory(self):
        """
        Descript. :
        """
        directory = self.session_hwobj.get_base_image_directory()
        self.emit(QtCore.SIGNAL("set_directory"), directory)

    def emit_set_prefix(self, item):
        """
        Descript. :
        """
        prefix = self.session_hwobj.get_default_prefix(item.get_model())
        self.emit(QtCore.SIGNAL("set_prefix"), prefix)

    def emit_set_sample(self, item):
        """
        Descript. :
        """
        self.emit(QtCore.SIGNAL("set_sample"), item)

    def get_selected_items(self):
        """
        Descript. :
        """
        items = self.dc_tree_widget.get_selected_items()
        return items

    def add_to_queue(self, task_list, parent_tree_item = None, set_on = True):
        """
        Descript. :
        """
        if not parent_tree_item :
            parent_tree_item = self.dc_tree_widget.get_mounted_sample_item()
        self.dc_tree_widget.add_to_queue(task_list, parent_tree_item, set_on)

    def select_last_added_item(self):
        self.dc_tree_widget.select_last_added_item()

    def filter_combo_changed(self, filter_index):
        """Filters sample treewidget based on the selected filter criteria:
           0 : No filter
           1 : Sample name
           2 : Protein name
           3 : Basket index
           4 : Executed
           5 : Not executed
           6 : OSC
           7 : Helical
           8 : Characterisation
           9 : Energy Scan
           10: XRF spectrum            
        """
        self.sample_changer_widget.filter_ledit.setEnabled(\
             filter_index in (1, 2, 3))
        self.clear_filter()
        if filter_index == 0:
            self.clear_filter() 
        else:
            item_iterator = QtGui.QTreeWidgetItemIterator(\
                  self.dc_tree_widget.sample_tree_widget)
            item = item_iterator.value()
            while item:
                  hide = False
                  item_model = item.get_model() 
                  if filter_index == 4:
                      if isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                          hide = not item_model.is_executed()
                  elif filter_index == 5:
                      if isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                          hide = item_model.is_executed()
                  elif filter_index == 6:
                      if isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                          hide = item_model.is_helical()
                      else:
                          hide = True
                  elif filter_index == 7:
                      if isinstance(item, Qt4_queue_item.DataCollectionQueueItem):
                          hide = not item_model.is_helical()
                      else:
                          hide = True
                  elif filter_index == 8:
                      hide = not isinstance(item, Qt4_queue_item.CharacterisationQueueItem)
                  elif filter_index == 9:
                      hide = not isinstance(item, Qt4_queue_item.EnergyScanQueueItem)
                  elif filter_index == 10:
                      hide = not isinstance(item, Qt4_queue_item.XRFSpectrumQueueItem)
                  #elif filter_index == 11:
                  #    hide = not isinstance(item, Qt4_queue_item.AdvancedQueueItem)

                  if isinstance(item, Qt4_queue_item.TaskQueueItem):
                      item.set_hidden(hide)
                  item_iterator += 1
                  item = item_iterator.value()

        self.dc_tree_widget.hide_empty_baskets()     

    def filter_text_changed(self, new_text):
        item_iterator = QtGui.QTreeWidgetItemIterator(\
             self.dc_tree_widget.sample_tree_widget) 
        item = item_iterator.value()
        filter_index = self.sample_changer_widget.filter_combo.currentIndex()
        while item:
              hide = False
              new_text = str(new_text)
              if filter_index == 1:
                  if isinstance(item, Qt4_queue_item.SampleQueueItem):
                      hide = not new_text in item.text(0)
              elif filter_index == 2:
                  if isinstance(item, Qt4_queue_item.SampleQueueItem):
                      hide = not new_text in item.get_model().crystals[0].protein_acronym
              elif filter_index == 3:
                  if isinstance(item, Qt4_queue_item.BasketQueueItem):
                      if new_text.isdigit(): 
                          # Display one basket
                          hide = item.get_model().location != int(new_text)
                      else: 
                          # Display several baskets. Separated with ","
                          enable_baskat_list = new_text.split(',')
                          if len(enable_baskat_list) > 1:
                              hide = str(item.get_model().location) not in enable_baskat_list
              item.set_hidden(hide) 
              item_iterator += 1
              item = item_iterator.value()

        if filter_index != 3:
            self.dc_tree_widget.hide_empty_baskets()
        
    def clear_filter(self):
        item_iterator = QtGui.QTreeWidgetItemIterator(\
             self.dc_tree_widget.sample_tree_widget)
        item = item_iterator.value()
        while item:
              item.setHidden(False)
              item_iterator += 1
              item = item_iterator.value() 

    def diffractometer_phase_changed(self, phase):
        self.enable_collect_conditions["diffractometer"] = \
             phase != "BeamLocation"
        self.update_enable_collect()

    def ppu_status_changed(self, in_error, status_msg):
        self.enable_collect_conditions["ppu"] = in_error != True
        self.update_enable_collect()

    def shutter_state_changed(self, state):
        if state == "closed":
            self.enable_collect_conditions["shutter"] = False
        else:
            self.enable_collect_conditions["shutter"] = True
        self.update_enable_collect()

    def update_enable_collect(self):
        enable_collect = all(item == True for item in self.enable_collect_conditions.values())
        if enable_collect != self.dc_tree_widget.enable_collect_condition:
            if enable_collect:
                logging.getLogger("GUI").info("Data collection is enabled")    
            else:
                logging.getLogger("GUI").warning("Data collect is disabled")
                for key, value in self.enable_collect_conditions.iteritems():
                    if value == False:
                        if key == "diffractometer":
                            logging.getLogger("GUI").info("Diffractometer is in beam location phase")
                        elif key == "shutter":
                            logging.getLogger("GUI").info("Safety shutter is closed")
                        elif key == "ppu":
                            logging.getLogger("GUI").error("PPU is in error state")
            self.dc_tree_widget.enable_collect_condition = enable_collect
            self.dc_tree_widget.sample_tree_widget_selection()
