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
from HardwareRepository.HardwareRepository import dispatcher
from widgets.Qt4_dc_tree_widget import DataCollectTree
from Qt4_sample_changer_helper import SC_STATE_COLOR, SampleChanger
from widgets.Qt4_tree_options_dialog import TreeOptionsDialog

__category__ = 'Qt4_General'

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
        self.beamline_config_hwobj = None
        self.session_hwobj = None
        self.lims_hwobj = None
        self.sample_changer_one_hwobj = None
        self.sample_changer_two_hwobj = None
        self.queue_hwobj = None

        # Internal variables --------------------------------------------------
        #self.current_cpos = None
        self.__collection_stopped = False 
        self.current_view = None
        self.item_iterator = None

        # Properties ---------------------------------------------------------- 
        self.addProperty("holderLengthMotor", "string", "")
        self.addProperty("queue", "string", "/Qt4_queue")
        self.addProperty("queue_model", "string", "/Qt4_queue-model")
        self.addProperty("beamline_setup", "string", "/Qt4_beamline-setup-break")
        self.addProperty("xml_rpc_server", "string", "/Qt4_xml_rpc_server")
        #names of sample changers could come from hwobj
        self.addProperty("scOneName", "string", "Sample changer")
        self.addProperty("scTwoName", "string", "Plate")

        # Signals ------------------------------------------------------------
        self.defineSignal("enable_hutch_menu", ())
        self.defineSignal("enable_command_menu", ())
        self.defineSignal("enable_task_toolbox", ())

        # Hiding and showing the tabs
        self.defineSignal("hide_sample_tab", ())
        self.defineSignal("hide_dc_parameters_tab", ())
        self.defineSignal("hide_sample_centring_tab", ())
        self.defineSignal("hide_dcg_tab", ())
        self.defineSignal("hide_sample_changer_one_tab", ())
        self.defineSignal("hide_sample_changer_two_tab", ())
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
        self.sample_changer_widget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                                 QtGui.QSizePolicy.Fixed)

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

        # Other --------------------------------------------------------------- 
        self.enable_collect(False)
        #self.setFixedWidth(315) 
        #self.sample_changer_widget.child('centring_cbox').setCurrentItem(1)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True) 
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

        elif property_name == 'queue':            
            self.queue_hwobj = self.getHardwareObject(new_value)
            self.dc_tree_widget.queue_hwobj = self.queue_hwobj
            self.connect(self.queue_hwobj, 'show_workflow_tab',
                         self.show_workflow_tab_from_model)

            self.connect(self.queue_hwobj, 'queue_entry_execute',
                         self.dc_tree_widget.queue_entry_execution_started)

            self.connect(self.queue_hwobj, 'queue_paused', 
                         self.dc_tree_widget.queue_paused_handler)

            self.connect(self.queue_hwobj, 'queue_execution_finished', 
                         self.dc_tree_widget.queue_execution_completed)

            self.connect(self.queue_hwobj, 'queue_stopped', 
                         self.dc_tree_widget.queue_stop_handler)
        elif property_name == 'queue_model':
            self.queue_model_hwobj = self.getHardwareObject(new_value)

            self.dc_tree_widget.queue_model_hwobj = self.queue_model_hwobj
            self.dc_tree_widget.confirm_dialog.queue_model_hwobj = self.queue_model_hwobj
            self.connect(self.queue_model_hwobj, 'child_added',
                         self.dc_tree_widget.add_to_view)
        elif property_name == 'beamline_setup':
            bl_setup = self.getHardwareObject(new_value)
            self.dc_tree_widget.beamline_setup_hwobj = bl_setup
            self.sample_changer_one_hwobj = bl_setup.sample_changer_one_hwobj
            self.sample_changer_two_hwobj = bl_setup.sample_changer_two_hwobj
            self.session_hwobj = bl_setup.session_hwobj
            self.lims_hwobj = bl_setup.lims_client_hwobj

            if self.sample_changer_one_hwobj is not None:
                self.connect(self.sample_changer_one_hwobj, SampleChanger.STATE_CHANGED_EVENT,
                             self.sample_load_state_changed)
                self.connect(self.sample_changer_one_hwobj, SampleChanger.INFO_CHANGED_EVENT, 
                             self.set_sample_pin_icon)
            if self.sample_changer_two_hwobj is not None:
                self.connect(self.sample_changer_two_hwobj, SampleChanger.STATE_CHANGED_EVENT,
                             self.sample_load_state_changed)
                self.connect(self.sample_changer_two_hwobj, SampleChanger.INFO_CHANGED_EVENT,
                             self.set_sample_pin_icon)

            has_shutter_less = bl_setup.detector_has_shutterless()

            if has_shutter_less:
                self.dc_tree_widget.confirm_dialog.disable_dark_current_cbx()
        elif property_name == 'xml_rpc_server':
            xml_rpc_server_hwobj = self.getHardwareObject(new_value)

            if xml_rpc_server_hwobj:
                self.connect(xml_rpc_server_hwobj, 'add_to_queue',
                             self.add_to_queue)

                self.connect(xml_rpc_server_hwobj, 'start_queue',
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
          
            if self.sample_changer_one_hwobj: 
                sc_basket_content, sc_sample_content = self.get_sc_content(\
                    self.sample_changer_one_hwobj)
                if sc_basket_content and sc_sample_content:
                    sc_basket_list, sc_sample_list = self.dc_tree_widget.\
                         samples_from_sc_content(sc_basket_content, sc_sample_content)
                    self.dc_tree_widget.sample_mount_method = 1
                    self.dc_tree_widget.populate_tree_widget(sc_basket_list, sc_sample_list, 
                         self.dc_tree_widget.sample_mount_method)
   
            if self.sample_changer_two_hwobj:        
                sc_basket_content, sc_sample_content = self.get_sc_content(\
                    self.sample_changer_two_hwobj)
                if sc_basket_content and sc_sample_content:
                    sc_basket_list, sc_sample_list = self.dc_tree_widget.\
                         samples_from_sc_content(sc_basket_content, sc_sample_content)
                    self.dc_tree_widget.sample_mount_method = 2
                    self.dc_tree_widget.populate_tree_widget(sc_basket_list, sc_sample_list, 
                         self.dc_tree_widget.sample_mount_method)    

            #if self.dc_tree_widget.sample_mount_method > 0:
            #self.sample_changer_widget.synch_combo.setEnabled()
            #self.sample_changer_widget.synch_label.setEnabled(True)

            self.sample_changer_widget.filter_cbox.setCurrentIndex(\
                 self.dc_tree_widget.sample_mount_method)
            self.dc_tree_widget.filter_sample_list(\
                 self.dc_tree_widget.sample_mount_method)

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

    def samples_from_lims(self, samples):
        """
        Descript. :
        """
        barcode_samples, location_samples = self.dc_tree_widget.samples_from_lims(samples)
        l_samples = dict()            
   
        # TODO: add test for sample changer type, here code is for Robodiff only
        for location, l_sample in location_samples.iteritems():
          if l_sample.lims_location != (None, None):
            basket, sample = l_sample.lims_location
            cell = int(round((basket+0.5)/3.0))
            puck = basket-3*(cell-1)
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
        if True:
            lims_client = self.lims_hwobj
            samples = lims_client.get_samples(self.session_hwobj.proposal_id,
                                              self.session_hwobj.session_id)
            sample_list = []
          
            if samples:
                sample_changer = None
                if self.dc_tree_widget.sample_mount_method == 1:
                    sample_changer = self.sample_changer_one_hwobj
                else:
                    sample_changer = self.sample_changer_two_hwobj     
 
                (barcode_samples, location_samples) = \
                    self.dc_tree_widget.samples_from_lims(samples)
                sc_basket_content, sc_sample_content = self.get_sc_content(\
                  sample_changer)
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
                            logging.getLogger("user_level_log").\
                                warning("Found sample in ISPyB for location %s" % str(sc_sample.location))
                            sample_list.append(lims_sample)
                        else:
                            logging.getLogger("user_level_log").\
                                warning("The sample with the barcode (%s) exists"+\
                                        " in LIMS but the location does not mat" +\
                                        "ch. Sample changer location: %s, LIMS " +\
                                        "location %s" % (sc_sample.code,
                                                         sc_sample.location,
                                                         lims_sample.lims_location))
                            sample_list.append(sc_sample)
                    else: # No sample with that barcode, continue with location
                        lims_sample = location_samples.get(sc_sample.location)
                        if lims_sample:
                            if lims_sample.lims_code:
                                logging.getLogger("user_level_log").\
                                    warning("The sample has a barcode in LIMS, but "+\
                                            "the SC has no barcode information for "+\
                                            "this sample. For location: %s" % str(sc_sample.location))
                                sample_list.append(lims_sample)
                            else:
                                logging.getLogger("user_level_log").\
                                    warning("Found sample in ISPyB for location %s" % str(sc_sample.location))
                                sample_list.append(lims_sample)
                        else:
                            if lims_sample:
                                if lims_sample.lims_location != None:
                                    logging.getLogger("user_level_log").\
                                        warning("No barcode was provided in ISPyB "+\
                                                "which makes it impossible to verify if"+\
                                                "the locations are correct, assuming "+\
                                                "that the positions are correct.")
                                    sample_list.append(lims_sample)
                            else:
                                logging.getLogger("user_level_log").\
                                    warning("No sample in ISPyB for location %s" % str(sc_sample.location))
                                sample_list.append(sc_sample)
            self.dc_tree_widget.populate_tree_widget(basket_list, sample_list, 
                 self.dc_tree_widget.sample_mount_method)

    def open_tree_options_dialog(self):
        self.tree_options_dialog.set_filter_lists(\
             self.dc_tree_widget.sample_tree_widget)
        self.tree_options_dialog.show()

    def get_sc_content(self, sample_changer):
        """
        Gets the 'raw' data from the sample changer.
        
        :returns: A list with tuples, containing the sample information.
        """
        sc_basket_content = []
        sc_sample_content = []
        for basket in sample_changer.getBasketList():
            basket_index = basket.getIndex()
            basket_code = basket.getID() or ""
            basket_name = basket.getName()
            is_present = basket.isPresent()
            sc_basket_content.append((basket_index+1, basket, basket_name))
             
        for sample in sample_changer.getSampleList():
            matrix = sample.getID() or ""
            basket_index = sample.getContainer().getIndex()
            sample_index = sample.getIndex()
            basket_code = sample.getContainer().getID() or ""
            sample_name = sample.getName()
            sc_sample_content.append((matrix, basket_index + 1, sample_index + 1, sample_name))
        return sc_basket_content, sc_sample_content


    def status_msg_changed(self, msg, color):
        """
        Status message from the SampleChangerBrick.
        
        :param msg: The message
        :type msg: str

        :returns: None
        """
        logging.getLogger("user_level_log").info(msg)

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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
        self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
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
        
    def toggle_sample_changer_tab(self): 
        """
        Descript. :
        """
        if self.current_view == self.sample_changer_widget:
            self.current_view = None
            self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), True)
            self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), True)
            self.dc_tree_widget.sample_tree_widget_selection()
            self.sample_changer_widget.details_button.setText("Show SC-details")
        else:
            self.current_view = self.sample_changer_widget
            self.emit(QtCore.SIGNAL("hide_dc_parameters_tab"), True)
            self.emit(QtCore.SIGNAL("hide_dcg_tab"), True)
            if self.dc_tree_widget.sample_mount_method == 1:
                self.emit(QtCore.SIGNAL("hide_sample_changer_one_tab"), False)
            else:
                self.emit(QtCore.SIGNAL("hide_sample_changer_two_tab"), False)
            self.sample_changer_widget.details_button.setText("Hide SC-details")
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
                self.populate_dc_parameters_tab(item)
            elif isinstance(item, Qt4_queue_item.CharacterisationQueueItem):
                self.populate_char_parameters_tab(item)
            elif isinstance(item, Qt4_queue_item.EnergyScanQueueItem):
                self.populate_energy_scan_tab(item)
            elif isinstance(item, Qt4_queue_item.XRFSpectrumQueueItem):
                self.populate_xrf_spectrum_tab(item)
            elif isinstance(item, Qt4_queue_item.GenericWorkflowQueueItem):
                self.populate_workflow_tab(item)
            elif isinstance(item, Qt4_queue_item.AdvancedQueueItem):
                self.populate_advanced_widget(item)
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
           11: Advanced

        """
        self.item_iterator = QtGui.QTreeWidgetItemIterator(\
             self.dc_tree_widget.sample_tree_widget) 
        self.sample_changer_widget.filter_ledit.setEnabled(\
             filter_index in (1, 2, 3))
        if filter_index == 0:
            self.clear_filter() 
        elif filter_index == 4:
            pass
        elif filter_index == 5:
            pass
        elif filter_index == 6:
            pass
        elif filter_index == 7:
            pass
        elif filter_index == 8:
            pass

    def filter_text_changed(self, new_text):
        self.item_iterator = QtGui.QTreeWidgetItemIterator(\
             self.dc_tree_widget.sample_tree_widget) 
        item = self.item_iterator.value()
        while item:
              hide = False
              new_text = str(new_text)
              if self.sample_changer_widget.filter_combo.currentIndex() == 1:
                  if isinstance(item, Qt4_queue_item.SampleQueueItem):
                      hide = not new_text in item.text(0)
              elif self.sample_changer_widget.filter_combo.currentIndex() == 2:
                  if isinstance(item, Qt4_queue_item.SampleQueueItem):
                      hide = not new_text in item.get_model().crystals[0].protein_acronym
              
            
              item.set_hidden(hide) 
              self.item_iterator += 1
              item = self.item_iterator.value()

        self.hide_empty_baskets()
        
    def clear_filter(self):
        item = self.item_iterator.value()
        while item:
              item.setHidden(False)
              self.item_iterator += 1
              item = self.item_iterator.value() 

    def hide_empty_baskets(self):
        self.item_iterator = QtGui.QTreeWidgetItemIterator(\
             self.dc_tree_widget.sample_tree_widget) 
        item = self.item_iterator.value()
        while item:
              hide = True
              
              if isinstance(item, Qt4_queue_item.BasketQueueItem): 
                  for index in range(item.childCount()):
                      if not item.child(index).isHidden():
                          hide = False
                          break
                  item.setHidden(hide) 
                 
              self.item_iterator += 1
              item = self.item_iterator.value()
 
