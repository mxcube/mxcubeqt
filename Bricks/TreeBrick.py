import os
import logging
import qt
import qtui
import queue_item

from collections import namedtuple
from BlissFramework import Icons, BaseComponents
from HardwareRepository.HardwareRepository import dispatcher
from sample_changer_helper import *

from widgets.dc_tree_widget import DataCollectTree

__category__ = 'mxCuBE_v3'

#ViewType = namedtuple('ViewType', ['ISPYB', 'MANUAL', 'SC'])
#TREE_VIEW_TYPE = ViewType(0, 1, 2)

class TreeBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        # Internal members
        self.current_cpos = None
        self.__collection_stopped = False 
        self.current_view = None

        # Framework 2 hardware objects
        self.beamline_config_hwobj = None
        self._lims_hwobj = None
        self.sample_changer = None
        self.queue_hwobj = None

        # Properties
        self.addProperty("holderLengthMotor", "string", "")
        self.addProperty("queue", "string", "/queue")
        self.addProperty("queue_model", "string", "/queue-model")
        self.addProperty("beamline_setup", "string", "/beamline-setup")
        self.addProperty("xml_rpc_server", "string", "/xml_rpc_server")

        # Qt - Slots
        # From ProposalBrick2
        self.defineSlot("logged_in", ())

        # Used from TaskToolBoxBrick
        self.defineSlot("get_tree_brick",())
        self.defineSlot("get_selected_samples", ())

        # From SampleChangerBrick3, signal emitted when
        # the status of the hwobj changes.
        self.defineSlot("status_msg_changed", ())

        # From sample changer hwobj, emitted when the
        # load state changes.
        self.defineSlot("sample_load_state_changed", ())
        
        #self.defineSlot("get_mounted_sample", ())
        #self.defineSlot("new_centred_position", ())
        #self.defineSlot("add_dcg", ())
        #self.defineSlot("add_data_collection", ())
        #self.defineSlot("set_session", ())

        # Qt - Signals
        self.defineSignal("enable_hutch_menu", ())
        self.defineSignal("enable_command_menu", ())
        self.defineSignal("enable_task_toolbox", ())

        # Hiding and showing the tabs
        self.defineSignal("hide_sample_tab", ())
        self.defineSignal("hide_dc_parameters_tab", ())
        self.defineSignal("hide_sample_centring_tab", ())
        self.defineSignal("hide_dcg_tab", ())
        self.defineSignal("hide_sample_changer_tab", ())
        self.defineSignal("hide_edna_tab", ())
        self.defineSignal("hide_energy_scan_tab",())
        self.defineSignal("hide_xrf_spectrum_tab",())
        self.defineSignal("hide_workflow_tab", ())

        # Populating the tabs with data
        self.defineSignal("populate_parameter_widget", ())
        self.defineSignal("populate_edna_parameter_widget",())
        self.defineSignal("populate_sample_details",())
        self.defineSignal("populate_energy_scan_widget", ())
        self.defineSignal("populate_xrf_spectrum_widget", ())
        self.defineSignal("populate_workflow_tab", ())

        # Handle selection
        self.defineSignal("selection_changed",())
        self.defineSignal("set_directory", ())
        self.defineSignal("set_prefix", ())
        self.defineSignal("set_sample", ())

        #self.defineSignal("clear_centred_positions", ())

        # Layout
        #self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Fixed,
        #                                  qt.QSizePolicy.Expanding))

        widget = qtui.QWidgetFactory.\
                 create(os.path.join(os.path.dirname(__file__),
                                     'widgets/ui_files/sample_changer_widget_layout.ui'))

        widget.reparent(self, qt.QPoint(0, 0))
        self.sample_changer_widget = widget
                                       
        self.refresh_pixmap = Icons.load("Refresh2.png")
        self.sample_changer_widget.child('synch_button').\
            setIconSet(qt.QIconSet(self.refresh_pixmap))
        self.sample_changer_widget.child('synch_button').setText("Synch ISPyB")
        

        self.dc_tree_widget = DataCollectTree(self)
        self.dc_tree_widget.selection_changed_cb = self.selection_changed
        self.dc_tree_widget.run_cb = self.run
        #self.dc_tree_widget.clear_centred_positions_cb = \
        #    self.clear_centred_positions

        qt.QObject.connect(self.sample_changer_widget.child('details_button'), 
                           qt.SIGNAL("clicked()"),
                           self.toggle_sample_changer_tab)

        qt.QObject.connect(self.sample_changer_widget.child('filter_cbox'),
                           qt.SIGNAL("activated(int)"),
                           self.dc_tree_widget.filter_sample_list)
        
        qt.QObject.connect(self.sample_changer_widget.child('centring_cbox'),
                           qt.SIGNAL("activated(int)"),
                           self.dc_tree_widget.set_centring_method)

        qt.QObject.connect(self.sample_changer_widget.child('synch_button'),
                           qt.SIGNAL("clicked()"),
                           self.refresh_sample_list)

        vlayout = qt.QVBoxLayout(self, 0, 0, 'main_layout')
        vlayout.setSpacing(10)
        self.layout().addWidget(self.sample_changer_widget)
        self.layout().addWidget(self.dc_tree_widget)
        self.enable_collect(False)

        self.sample_changer_widget.child('centring_cbox').setCurrentItem(1)
        self.dc_tree_widget.set_centring_method(1)

    # Framework 2 method
    def run(self):
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_centring_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))

    def eventFilter(self, _object, event):
        if event.type() == qt.QEvent.MouseButtonPress:
            if event.state() & qt.Qt.ShiftButton:
                return True
        return False

    # Framework 2 method
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'holder_length_motor':
            self.dc_tree_widget.hl_motor_hwobj = self.getHardwareObject(new_value)

        elif property_name == 'queue':            
            self.queue_hwobj = self.getHardwareObject(new_value)
            self.dc_tree_widget.queue_hwobj = self.queue_hwobj
            
            self.connect(self.queue_hwobj, 'show_workflow_tab',
                         self.show_workflow_tab_from_model)

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
            self.sample_changer_hwobj = bl_setup.sample_changer_hwobj
            self.dc_tree_widget.sample_changer_hwobj = self.sample_changer_hwobj
            self.session_hwobj = bl_setup.session_hwobj
            self._lims_hwobj = bl_setup.lims_client_hwobj

            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, SampleChanger.STATE_CHANGED_EVENT,
                             self.sample_load_state_changed)
                self.connect(self.sample_changer_hwobj, SampleChanger.INFO_CHANGED_EVENT, 
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

    def set_session(self, session_id, t_prop_code = None, prop_number = None,
                    prop_id = None, start_date = None, prop_code = None,
                    is_inhouse = None):

         self.session_hwobj.set_session_start_date(start_date)

    def logged_in(self, logged_in):
        """
        Connected to the signal loggedIn of ProposalBrick2.
        The signal is emitted when a user was succesfully logged in.
        """
        self.enable_collect(logged_in)
        
        if not logged_in:
            self.dc_tree_widget.populate_free_pin()
        else:
            sc_basket_content, sc_sample_content = self.get_sc_content()

            if sc_sample_content:
              self.sample_changer_widget.child('filter_cbox').setCurrentItem(0)
              
              if sc_basket_content:
                  sc_basket_list, sc_sample_list = self.dc_tree_widget.samples_from_sc_content(
                      sc_basket_content, sc_sample_content)
                  self.dc_tree_widget.populate_list_view(sc_basket_list, sc_sample_list)
              
              self.sample_changer_widget.child('filter_cbox').setCurrentItem(0)
            else:
              self.sample_changer_widget.child('filter_cbox').setCurrentItem(2) 

        #if self.sample_changer_hwobj:
        #  if not self.sample_changer_hwobj.hasLoadedSample():

        self.dc_tree_widget.sample_list_view_selection()

    def enable_collect(self, state):
        """
        Enables the collect controls.

        :param state: Enable if state is True and disable if False
        :type state: bool

        :returns: None
        """
        self.dc_tree_widget.enable_collect(state)

    def enable_hutch_menu(self, state):
        self.emit(qt.PYSIGNAL("enable_hutch_menu"), (state,))

    def enable_command_menu(self, state):
        self.emit(qt.PYSIGNAL("enable_command_menu"), (state,))

    def enable_task_toolbox(self, state):
        self.emit(qt.PYSIGNAL("enable_task_toolbox"), (state,))

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
        barcode_samples, location_samples = self.dc_tree_widget.samples_from_lims(samples)
        l_samples = dict()            
   
        if self.sample_changer_hwobj.__class__.__TYPE__ == 'Robodiff':
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
        else:
          l_samples.update(location_samples)

        return barcode_samples, l_samples

    def refresh_sample_list(self):
        """
        Retrives sample information from ISPyB and populates the sample list
        accordingly.
        """
        lims_client = self._lims_hwobj
        samples = lims_client.get_samples(self.session_hwobj.proposal_id,
                                          self.session_hwobj.session_id)
        sample_list = []
        
        if samples:
            (barcode_samples, location_samples) = self.samples_from_lims(samples)

            sc_basket_content, sc_samples_content = self.get_sc_content()
            sc_basket_list, sc_sample_list = self.dc_tree_widget.\
                samples_from_sc_content(sc_basket_content, sc_samples_content)
           
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

            self.dc_tree_widget.populate_list_view(basket_list, sample_list)

    def get_sc_content(self):
        """
        Gets the 'raw' data from the sample changer.
        
        :returns: A list with tuples, containing the sample information.
        """
        sc_basket_content = []
        sc_sample_content = []
      
        try: 
            for basket in self.sample_changer_hwobj.getBasketList():
                basket_index = basket.getIndex()
                basket_code = basket.getID() or ""
                is_present = basket.isPresent()
                sc_basket_content.append((basket_index+1, basket)) #basket_code, is_present)) 

            for sample in self.sample_changer_hwobj.getSampleList():
                coords = sample.getCoords()
                matrix = sample.getID() or ""
                basket_index = str(coords[0])
                vial_index = ":".join(map(str, coords[1:]))
                basket_code = sample.getContainer().getID() or ""
            
                sc_sample_content.append((matrix, basket_index, vial_index, basket_code, 0, coords))
        except:
            logging.getLogger("user_level_log").\
                info("Could not connect to sample changer,"  + \
                     " unable to list contents. Make sure that" + \
                     " the sample changer is turned on. Using free pin mode")

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
        self.sample_changer_widget.child('details_button').\
            setPaletteBackgroundColor(qt.QColor(s_color))

    def show_sample_centring_tab(self):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_centring_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))

    def show_sample_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("populate_sample_details"), (item.get_model(),))
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_centring_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))

    def show_dcg_tab(self):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))

    def populate_parameters_tab(self, item = None):
        self.emit(qt.PYSIGNAL("populate_parameter_widget"),
                  (item,))
        
    def show_datacollection_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))
        self.populate_parameters_tab(item)

    def show_edna_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))
        self.populate_edna_parameters_tab(item)

    def populate_edna_parameters_tab(self, item):
        self.emit(qt.PYSIGNAL("populate_edna_parameter_widget"),
                  (item,))

    def show_energy_scan_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,)) 
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))
        self.populate_energy_scan_tab(item)

    def populate_energy_scan_tab(self, item):
        self.emit(qt.PYSIGNAL("populate_energy_scan_widget"), (item,))

    def show_xrf_spectrum_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC")
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (False,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (True,))
        self.populate_xrf_spectrum_tab(item)

    def populate_xrf_spectrum_tab(self, item):
        self.emit(qt.PYSIGNAL("populate_xrf_spectrum_widget"), (item,))

    def show_workflow_tab_from_model(self):
        self.show_workflow_tab(None)
        
    def show_workflow_tab(self, item):
        self.sample_changer_widget.child('details_button').setText("Show SC-details")
        self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_edna_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,)) 
        self.emit(qt.PYSIGNAL("hide_energy_scan_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_xrf_spectrum_tab"), (True,))
        self.emit(qt.PYSIGNAL("hide_workflow_tab"), (False,))

        running = self.queue_hwobj.is_executing() 
        self.populate_workflow_tab(item, running=running)

    def populate_workflow_tab(self, item, running = False):
        self.emit(qt.PYSIGNAL("populate_workflow_tab"), (item, running))
        
    def toggle_sample_changer_tab(self): 
        if self.current_view == self.sample_changer_widget:
            self.current_view = None
            self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (True,))
            self.dc_tree_widget.sample_list_view_selection()
            self.sample_changer_widget.child('details_button').setText("Show SC-details")

        else:
            self.current_view = self.sample_changer_widget
            self.emit(qt.PYSIGNAL("hide_dc_parameters_tab"), (True,))
            self.emit(qt.PYSIGNAL("hide_dcg_tab"), (True,))
            self.emit(qt.PYSIGNAL("hide_sample_changer_tab"), (False,))
            self.sample_changer_widget.child('details_button').setText("Hide SC-details")
            self.emit(qt.PYSIGNAL("hide_sample_tab"), (True,))
        
    def selection_changed(self, items):
        if len(items) == 1:
            item = items[0]
            if isinstance(item, queue_item.SampleQueueItem):
                self.emit(qt.PYSIGNAL("populate_sample_details"), (item.get_model(),))
                self.emit_set_sample(item)
                self.emit_set_directory()
                self.emit_set_prefix(item)
                #self.populate_edna_parameter_widget(item)
            elif isinstance(item, queue_item.DataCollectionQueueItem):
                self.populate_parameters_tab(item)
            elif isinstance(item, queue_item.CharacterisationQueueItem):
                self.populate_edna_parameters_tab(item)
            elif isinstance(item, queue_item.EnergyScanQueueItem):
                self.populate_energy_scan_tab(item)
            elif isinstance(item, queue_item.XRFSpectrumQueueItem):
                self.populate_xrf_spectrum_tab(item)
            elif isinstance(item, queue_item.GenericWorkflowQueueItem):
                self.populate_workflow_tab(item)

        self.emit(qt.PYSIGNAL("selection_changed"), (items,))

    def emit_set_directory(self):
        directory = self.session_hwobj.get_base_image_directory()
        self.emit(qt.PYSIGNAL("set_directory"), (directory,))

    def emit_set_prefix(self, item):
        prefix = self.session_hwobj.get_default_prefix(item.get_model())
        self.emit(qt.PYSIGNAL("set_prefix"), (prefix,))

    def emit_set_sample(self, item):
        self.emit(qt.PYSIGNAL("set_sample"), (item,))

    def get_selected_items(self):
        items = self.dc_tree_widget.get_selected_items()
        return items

    def add_to_queue(self, task_list, parent_tree_item = None, set_on = True):
        if not parent_tree_item :
            parent_tree_item = self.dc_tree_widget.get_mounted_sample_item()
        
        self.dc_tree_widget.add_to_queue(task_list, parent_tree_item, set_on)
