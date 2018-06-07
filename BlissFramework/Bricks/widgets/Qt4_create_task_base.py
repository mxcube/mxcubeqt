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
import abc
import copy
import logging
from copy import deepcopy

from QtImport import *

import Qt4_queue_item
import Qt4_GraphicsManager
import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables


class CreateTaskBase(QWidget):
    """
    Base class for widgets that are used to create tasks.
    Contains methods for handling the PathTemplate,
    AcqusitionParameters object, and other functionalty for
    creating Task objects.

    The members self._acq_widget and self._data_path_widget
    are used to reference the widgets for respective widgets.

    Tests for self.acq_widgets and self._data_path_widget is
    be made, to make this class generic for widgets not using
    the objects PathTemplate and AcquisitionParameters.
    """
    acqParametersConflictSignal = pyqtSignal(bool)
    pathTempleConflictSignal = pyqtSignal(bool)

    def __init__(self, parent, name, fl, task_node_name = 'Unamed task-node'):
         QWidget.__init__(self, parent, Qt.WindowFlags(fl))
         self.setObjectName(name)
        
         self._tree_brick = None
         self._task_node_name = task_node_name

         # Centred positons that currently are selected in the parent
         # widget, position_history_brick.
         self._selected_positions = []

         # Abstract attributes
         self._acq_widget = None
         self._data_path_widget = None
         self._current_selected_items = []
         self._path_template = None
         self._energy_scan_result = None
         self._session_hwobj = None
         self._beamline_setup_hwobj = None
         self._graphics_manager_hwobj = None
         self._in_plate_mode = None
        
    def set_expert_mode(self, state):
        if self._acq_widget:
            self._acq_widget.acq_widget_layout.energy_label.setEnabled(state)
            self._acq_widget.acq_widget_layout.energy_ledit.setEnabled(state)

    def enable_compression(self, state):
        if self._data_path_widget:
            self._data_path_widget.data_path_layout.compression_cbox.setChecked(state)
            self._data_path_widget.data_path_layout.compression_cbox.setEnabled(state)
            self._data_path_widget.update_file_name()

    def init_models(self):
        self.init_acq_model()
        self.init_data_path_model()

    def init_acq_model(self):
        bl_setup = self._beamline_setup_hwobj

        if bl_setup is not None:
            if self._acq_widget:
                self._acq_widget.set_beamline_setup(bl_setup)
                def_acq_parameters = bl_setup.get_default_acquisition_parameters()
                self._acquisition_parameters.set_from_dict(def_acq_parameters.as_dict())
                if bl_setup.diffractometer_hwobj.in_plate_mode():
                    self._acq_widget.use_kappa(False)
                    self._acq_widget.use_max_osc_range(True)
                else:
                    self._acq_widget.use_kappa(True)
                    self._acq_widget.use_max_osc_range(False)
                
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()

    def init_data_path_model(self):
        bl_setup = self._beamline_setup_hwobj

        if bl_setup is not None:
            # Initialize the path_template of the widget to default
            # values read from the beamline setup
            if self._data_path_widget:
                self._data_path_widget._base_image_dir = \
                    self._session_hwobj.get_base_image_directory()
                self._data_path_widget._base_process_dir = \
                    self._session_hwobj.get_base_process_directory()

                (data_directory, proc_directory) = self.get_default_directory()
                self._path_template = bl_setup.get_default_path_template()
                self._path_template.directory = data_directory
                self._path_template.process_directory = proc_directory
                self._path_template.base_prefix = self.get_default_prefix()
                self._path_template.run_number = bl_setup.queue_model_hwobj.\
                    get_next_run_number(self._path_template)
        else:
            self._path_template = queue_model_objects.PathTemplate()

    def tab_changed(self, tab_index, tab):
        # Update the selection if in the main tab and logged in to
        # ISPyB
        if tab_index is 0 and self._session_hwobj.proposal_code:
            self.update_selection()

    def set_beamline_setup(self, bl_setup_hwobj):
        self._beamline_setup_hwobj = bl_setup_hwobj
        self._in_plate_mode = self._beamline_setup_hwobj.diffractometer_hwobj.in_plate_mode()

        try:
            self.set_resolution_limits(bl_setup_hwobj.resolution_hwobj.getLimits())

            bl_setup_hwobj.energy_hwobj.connect('energyChanged', self.set_energy)
            bl_setup_hwobj.energy_hwobj.connect('energyLimitsChanged', self.set_energy_limits)
            bl_setup_hwobj.transmission_hwobj.connect('attFactorChanged', self.set_transmission)
            bl_setup_hwobj.transmission_hwobj.connect('attLimitsChanged', self.set_transmission_limits)
            bl_setup_hwobj.resolution_hwobj.connect('positionChanged', self.set_resolution)
            bl_setup_hwobj.resolution_hwobj.connect('limitsChanged', self.set_resolution_limits)
            bl_setup_hwobj.omega_axis_hwobj.connect('positionChanged', self.set_osc_start)
            bl_setup_hwobj.kappa_axis_hwobj.connect('positionChanged', self.set_kappa)
            bl_setup_hwobj.kappa_phi_axis_hwobj.connect('positionChanged', self.set_kappa_phi)
            bl_setup_hwobj.detector_hwobj.connect('detectorRoiModeChanged', self.set_detector_roi_mode)
            bl_setup_hwobj.detector_hwobj.connect('expTimeLimitsChanged', self.set_detector_exp_time_limits)

            bl_setup_hwobj.resolution_hwobj.update_values()
            bl_setup_hwobj.detector_hwobj.update_values()
        except AttributeError as ex:
            msg = 'Could not connect to one or more hardware objects' + str(ex)
            logging.getLogger("HWR").warning(msg)
       
        self._graphics_manager_hwobj = bl_setup_hwobj.shape_history_hwobj
        if self._graphics_manager_hwobj: 
            self._graphics_manager_hwobj.connect('shapeCreated', self.shape_created)
            self._graphics_manager_hwobj.connect('shapeChanged', self.shape_changed)
            self._graphics_manager_hwobj.connect('shapeDeleted', self.shape_deleted)

        self._session_hwobj = bl_setup_hwobj.session_hwobj
        self.init_models()

    def set_osc_start(self, new_value):
        acq_widget = self.get_acquisition_widget()

        if self._item_is_group_or_sample() and acq_widget:
            acq_widget.update_osc_start(new_value)

    def _run_processing_toggled(self, run_processing_after, run_processing_parallel):
        if len(self._current_selected_items) > 0:
            item = self._current_selected_items[0]
            model = item.get_model()
            if isinstance(model, queue_model_objects.DataCollection):
                model.run_processing_after = run_processing_after
                model.run_processing_parallel = run_processing_parallel

    def acq_parameters_changed(self, conflict):
        if self._tree_brick:
            self._tree_brick.acq_parameters_changed(conflict)
            self.acqParametersConflictSignal.emit(len(conflict) > 0)
 
    def path_template_changed(self):
        self._data_path_widget.update_file_name()
        if self._tree_brick is not None:
            self._tree_brick.dc_tree_widget.check_for_path_collisions()
            path_conflict = self._beamline_setup_hwobj.queue_model_hwobj.\
                            check_for_path_collisions(self._path_template)
            self._data_path_widget.indicate_path_conflict(path_conflict)
            self._tree_brick.data_path_changed(path_conflict)
            self.pathTempleConflictSignal.emit(path_conflict)

    def set_tree_brick(self, brick):
        self._tree_brick = brick

    @abc.abstractmethod
    def set_energies(self):
        pass
 
    def get_sample_item(self, item):
        if isinstance(item, Qt4_queue_item.SampleQueueItem):
            return item
        elif isinstance(item, Qt4_queue_item.BasketQueueItem):
            return item
        elif isinstance(item, Qt4_queue_item.TaskQueueItem):
            return item.get_sample_view_item()
        else:
            return None

    def get_group_item(self, item):
        if isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
            return item
        elif isinstance(item, Qt4_queue_item.TaskQueueItem):
            return self.item.parent()
        else:
            return None

    def get_acquisition_widget(self):
        return self._acq_widget

    def get_data_path_widget(self):
        return self._data_path_widget

    def _item_is_group_or_sample(self):
        result = False
        
        if self._current_selected_items:
            item = self._current_selected_items[0]
        
            if isinstance(item, Qt4_queue_item.SampleQueueItem) or \
                isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                    result = True
        return result

    def _item_is_dc(self):
        result = False

        if self._current_selected_items:
            item = self._current_selected_items[0]

            if isinstance(item, Qt4_queue_item.TaskQueueItem) and \
            not isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):   
                result = True
        return result

    def set_energy(self, energy, wavelength):         
        if not self._item_is_dc() and energy:
            acq_widget = self.get_acquisition_widget()
            
            if acq_widget:
                acq_widget.previous_energy = energy
                acq_widget.update_energy(energy, wavelength)

    def set_transmission(self, trans):
        acq_widget = self.get_acquisition_widget()
        
        if not self._item_is_dc() and acq_widget:
            acq_widget.update_transmission(trans)

    def set_resolution(self, res):
        acq_widget = self.get_acquisition_widget()
        
        if not self._item_is_dc() and acq_widget:
            acq_widget.update_resolution(res)

    def set_detector_roi_mode(self, detector_roi_mode):
        acq_widget = self.get_acquisition_widget()

        if not self._item_is_dc() and acq_widget:
            acq_widget.update_detector_roi_mode(detector_roi_mode)

    def set_kappa(self, kappa):
        acq_widget = self.get_acquisition_widget()

        if not self._item_is_dc() and acq_widget:
            acq_widget.update_kappa(kappa)

    def set_kappa_phi(self, kappa_phi):
        acq_widget = self.get_acquisition_widget()

        if not self._item_is_dc() and acq_widget:
            acq_widget.update_kappa_phi(kappa_phi)
                                                      
    def set_run_number(self, run_number):
        data_path_widget = self.get_data_path_widget()

        if data_path_widget:
            data_path_widget.set_run_number(run_number)

    def set_energy_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()
            if acq_widget:
                acq_widget.update_energy_limits(limits)

    def set_transmission_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_transmission_limits(limits)

    def set_resolution_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_resolution_limits(limits)

    def set_detector_exp_time_limits(self, limits):
        if limits:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.update_exp_time_limits()

    def get_default_prefix(self, sample_data_node = None, generic_name = False):
        prefix = self._session_hwobj.get_default_prefix(sample_data_node, generic_name)
        return prefix
        
    def get_default_directory(self, tree_item = None, sub_dir = ''):
        group_name = self._session_hwobj.get_group_name()

        if group_name:
            sub_dir = group_name + '/' + sub_dir

        if tree_item:
            item = self.get_sample_item(tree_item)
            if isinstance(tree_item, Qt4_queue_item.BasketQueueItem):
                sub_dir += str(tree_item.get_model().get_location())
            else:
                if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
                    if item.get_model().lims_id == -1:
                        sub_dir += ''
            
        data_directory = self._session_hwobj.\
                         get_image_directory(sub_dir)

        proc_directory = self._session_hwobj.\
                         get_process_directory(sub_dir)

        return (data_directory, proc_directory)

    def ispyb_logged_in(self, logged_in):
        self.init_models()
        self.update_selection()

    def select_shape_with_cpos(self, cpos):
        self._graphics_manager_hwobj.select_shape_with_cpos(cpos)
            
    def selection_changed(self, items):
        if items:
            if len(items) == 1:
                self._current_selected_items = items
                self.single_item_selection(items[0])
            elif len(items) > 1:                
                sample_items = []

                # Allow mutiple selections on sample items, only.
                for item in items:
                    if isinstance(item, Qt4_queue_item.SampleQueueItem):
                        sample_items.append(item)

                if sample_items:
                    self._current_selected_items = sample_items
                    self.single_item_selection(items[0])
                    #self.multiple_item_selection(sample_items)
        else:
            self.setDisabled(True)

    def update_selection(self):
        self.selection_changed(self._current_selected_items)

    def single_item_selection(self, tree_item):
        sample_item = self.get_sample_item(tree_item)
        if self._data_path_widget:
            self._data_path_widget.enable_macros = False
        

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            sample_data_model = sample_item.get_model()
            self._path_template = copy.deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)

            # Sample with lims information, use values from lims
            # to set the data path. Or has a specific user group set.
            if sample_data_model.lims_id != -1:
                prefix = self.get_default_prefix(sample_data_model)
                (data_directory, proc_directory) = self.get_default_directory(\
                  tree_item, sub_dir = "%s%s" % (prefix.split("-")[0], os.path.sep))

                #TODO create templates to customize this
                #self._path_template.directory = data_directory
                #self._path_template.process_directory = proc_directory
                self._path_template.base_prefix = prefix
            elif self._session_hwobj.get_group_name() != '':
                base_dir = self._session_hwobj.get_base_image_directory()
                # Update with group name as long as user didn't specify
                # differnt path.

                if base_dir == self._path_template.directory:
                    (data_directory, proc_directory) = self.get_default_directory()
                    self._path_template.directory = data_directory
                    self._path_template.process_directory = proc_directory
                    self._path_template.base_prefix = self.get_default_prefix()

            # If no information from lims then add basket/sample info
            # This works if each sample is clicked, but do not work
            # when a task is assigned to the whole puck.
            # Then all samples get the same dir
            
            #if sample_data_model.lims_id == -1 and \
            #   not None in (sample_data_model.location):
            #    (data_directory, proc_directory) = self.get_default_directory(tree_item)
            #    self._path_template.directory = data_directory
            #    self._path_template.process_directory = proc_directory

            # Get the next available run number at this level of the model.
            self._path_template.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                get_next_run_number(self._path_template)

            #Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                self._acq_widget.use_kappa(True)
                sample_data_model = sample_item.get_model()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
                #self.get_acquisition_widget().use_osc_start(False)

            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)
                self._data_path_widget.enable_macros = True
            self.setDisabled(False)

        elif isinstance(tree_item, Qt4_queue_item.BasketQueueItem):
            self._path_template = copy.deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)
            #(data_directory, proc_directory) = self.get_default_directory(tree_item)
            #self._path_template.directory = data_directory
            #self._path_template.process_directory = proc_directory

            #Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                self._acq_widget.use_kappa(True)
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)
                self._data_path_widget.enable_macros = True
            self.setDisabled(False)          

        elif isinstance(tree_item, Qt4_queue_item.DataCollectionGroupQueueItem):
            self.setDisabled(True)

        #if self._acq_widget:
        #    self._acq_widget.set_enable_parameter_update(\
        #         not isinstance(tree_item, Qt4_queue_item.TaskQueueItem)) 

    def _update_etr(self):
        omega = self._beamline_setup_hwobj._get_omega_axis_position()
        kappa = self._beamline_setup_hwobj._get_kappa_axis_position()
        kappa_phi = self._beamline_setup_hwobj._get_kappa_phi_axis_position()
        energy = self._beamline_setup_hwobj._get_energy()
        transmission = self._beamline_setup_hwobj._get_transmission()
        resolution = self._beamline_setup_hwobj._get_resolution()
    
        self._acquisition_parameters.osc_start = omega            
        self._acquisition_parameters.kappa = kappa
        self._acquisition_parameters.kappa_phi = kappa_phi
        self._acquisition_parameters.energy = energy
        self._acquisition_parameters.transmission = transmission
        self._acquisition_parameters.resolution = resolution

        self._acq_widget.value_changed_list = []
        self._acq_widget._acquisition_mib.clear_edit()

    """
    def multiple_item_selection(self, tree_items):
        tree_item = tree_items[0]

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            sample_data_model = tree_item.get_model()
            self._path_template = copy.deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)

            # Sample with lims information, use values from lims
            # to set the data path.
            (data_directory, proc_directory) = self.get_default_directory(\
                 sub_dir = '<acronym>%s<sample_name>%s' % (os.path.sep, os.path.sep))    
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(generic_name = True)

            # Get the next available run number at this level of the model.
            self._path_template.run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
                get_next_run_number(self._path_template)

            #Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)
                self._acq_widget.update_data_model(self._acquisition_parameters,
                                                   self._path_template)
                #self.get_acquisition_widget().use_osc_start(False)

            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)

            self.setDisabled(False)
    """

    # Called by the owning widget (task_toolbox_widget) when
    # one or several centred positions are selected.
    def centred_position_selection(self, position):
        """
        Descript. : Called by the owning widget (task_toolbox_widget) when
                    one or several centred positions are selected. 
                    Updates kappa/phi position from the centring point
                    Enables kappa/phi edit if not collection item and no
                    centring point is selected. In all other cases kappa/phi
                    edit is disabled.
                    Also updates centring point if a data collection item is
                    selected and new centring point clicked 
        Args.     : centring points
        Return    "
        """
        if self._acq_widget:
            self._acq_widget.use_kappa(False)

            if position:
                if len(self._current_selected_items) == 1:
                    item = self._current_selected_items[0]
                    cpos = position.get_centred_position()
                    if hasattr(cpos, "kappa"):
                        self._acq_widget.update_kappa(cpos.kappa)
                    if hasattr(cpos, "kappa_phi"):
                        self._acq_widget.update_kappa_phi(cpos.kappa_phi)
                    if isinstance(item, Qt4_queue_item.TaskQueueItem):
                        snapshot = self._graphics_manager_hwobj.get_scene_snapshot(position)
                        cpos.snapshot_image = snapshot
                        self._acquisition_parameters.centred_position = cpos
            else:
                self._acq_widget.use_kappa(True)

    # Should be called by the object that calls create_task,
    # and add_task.
    def approve_creation(self):
        result = True
        
        path_conflict = self._beamline_setup_hwobj.queue_model_hwobj.\
                        check_for_path_collisions(self._path_template)

        if path_conflict:
            logging.getLogger("GUI").\
                error('The current path settings will overwrite data ' + \
                      'from another task. Correct the problem before ' + \
                      'adding to queue')
            result = False

        if self._acq_widget is not None:
            parameter_conflict =  self._acq_widget.check_parameter_conflict()
            if len(parameter_conflict) > 0:
                msg = "Entered value of " 
                for item in parameter_conflict:
                    msg = msg + "%s, " % item
                msg = msg[:-2]
                msg += " is out of range. Correct the input value(s) before " + \
                       "adding item to the queue"
                logging.getLogger("GUI").error(msg)
                result = False

        return result
            
    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a task_node is selected.
    def create_task(self, sample, shape):
        (tasks, sc) = ([], None)

        dm = self._beamline_setup_hwobj.diffractometer_hwobj      

        sample_is_mounted = False
        if self._in_plate_mode:
            try:
               sample_is_mounted = self._beamline_setup_hwobj.plate_manipulator_hwobj.\
                  getLoadedSample().getCoords() == sample.location
            except:
               sample_is_mounted = False
        else: 
            try: 
               sample_is_mounted = self._beamline_setup_hwobj.sample_changer_hwobj.\
                  getLoadedSample().getCoords() == sample.location

            except AttributeError:
               sample_is_mounted = False

        fully_automatic = (not dm.user_confirms_centring)

        free_pin_mode = sample.free_pin_mode
        temp_tasks = self._create_task(sample, shape)

        if len(temp_tasks) == 0:
            return

        if ((not free_pin_mode) and (not sample_is_mounted) or (not shape)):
            # No centred positions selected, or selected sample not
            # mounted create sample centring task.

            # Check if the tasks requires centring, assumes that all
            # the "sub tasks" has the same centring requirements.
            if temp_tasks[0].requires_centring():
                if self._tree_brick.dc_tree_widget.centring_method == \
                   queue_model_enumerables.CENTRING_METHOD.MANUAL:

                    #Manual 3 click centering
                    acq_par = None
                    kappa = None
                    kappa_phi = None
                    task_label = "Manual centring"

                    if isinstance(temp_tasks[0], queue_model_objects.DataCollection):
                        acq_par = temp_tasks[0].acquisitions[0].\
                          acquisition_parameters
                    elif isinstance(temp_tasks[0], queue_model_objects.Characterisation):
                        acq_par =  temp_tasks[0].reference_image_collection.\
                           acquisitions[0].acquisition_parameters

                    if acq_par:
                        kappa = acq_par.kappa
                        kappa_phi = acq_par.kappa_phi
                        if kappa is not None and kappa_phi is not None:
                            task_label = "Manual centring (kappa=%0.1f,phi=%0.1f)" % \
                              (kappa, kappa_phi)

                    sc = queue_model_objects.SampleCentring(task_label,
                                                            kappa,
                                                            kappa_phi)
                elif self._tree_brick.dc_tree_widget.centring_method == \
                   queue_model_enumerables.CENTRING_METHOD.LOOP:

                    #Optical automatic centering with user confirmation
                    sc = queue_model_objects.OpticalCentring(user_confirms=True)
                elif self._tree_brick.dc_tree_widget.centring_method == \
                   queue_model_enumerables.CENTRING_METHOD.FULLY_AUTOMATIC:

                    #Optical automatic centering without user confirmation
                    sc = queue_model_objects.OpticalCentring()
                elif self._tree_brick.dc_tree_widget.centring_method == \
                   queue_model_enumerables.CENTRING_METHOD.XRAY:

                    #Xray centering
                    mesh_dc = self._create_dc_from_grid(sample)
                    mesh_dc.run_processing_parallel = "XrayCentering"
                    sc = queue_model_objects.XrayCentering(mesh_dc)
                if sc:
                    tasks.append(sc)

        for task in temp_tasks:
            if sc:
                sc.add_task(task)
            tasks.append(task)

        return tasks

    @abc.abstractmethod
    def _create_task(self, task_node, shape):
        pass

    def _create_path_template(self, sample, path_template):
        """Creates path template and expands macro keywords:
           %n : container name (dewar, puck, etc)
           %c : container number
           %u : username
           %p : sample position
           %s : sample name
        """

        bl_setup = self._beamline_setup_hwobj

        acq_path_template = copy.deepcopy(path_template)

        if '<sample_name>' in acq_path_template.directory:
            name = sample.get_name().replace(':', '-')
            acq_path_template.directory = acq_path_template.directory.\
                                          replace('<sample_name>', name)
            acq_path_template.process_directory = acq_path_template.process_directory.\
                                                  replace('<sample_name>', name)

        if '<acronym>-<name>' in acq_path_template.base_prefix:
            acq_path_template.base_prefix = self.get_default_prefix(sample)
            acq_path_template.run_number = bl_setup.queue_model_hwobj.get_next_run_number(acq_path_template)

        if '<acronym>' in acq_path_template.directory:
            prefix = self.get_default_prefix(sample)
            acronym = prefix.split("-")[0]
            acq_path_template.directory = acq_path_template.directory.\
                                          replace('<acronym>', acronym)
            acq_path_template.process_directory = acq_path_template.process_directory.\
                                                  replace('<acronym>', acronym)

        #TODO create a method get_user_name in Session hwobj
        user_name = ""
        if os.getenv("SUDO_USER"):
            user_name = os.getenv("SUDO_USER")
        else:
            user_name = os.getenv("USER")
 
        # expand macro keywords in the directory path
        acq_path_template.directory = acq_path_template.directory.\
            replace('%c', str(sample.location[0]))
        acq_path_template.directory = acq_path_template.directory.\
            replace('%p', str(sample.location[1]))
        acq_path_template.directory = acq_path_template.directory.\
            replace('%s', str(sample.name))
        acq_path_template.directory = acq_path_template.directory.\
            replace('%u', user_name)
 
        # expand macro keywords in the prefix
        acq_path_template.base_prefix = acq_path_template.base_prefix.\
            replace('%c', str(sample.location[0]))
        acq_path_template.base_prefix = acq_path_template.base_prefix.\
            replace('%p', str(sample.location[1]))
        acq_path_template.base_prefix = acq_path_template.base_prefix.\
            replace('%s', str(sample.name))
        acq_path_template.base_prefix = acq_path_template.base_prefix.\
            replace('%u', user_name)
        acq_path_template.base_prefix

        #acq_path_template.suffix = bl_setup.suffix

        return acq_path_template

    def _create_acq(self, sample):
        parameters = self._acquisition_parameters
        path_template = self._path_template
        processing_parameters = self._processing_parameters
        bl_setup = self._beamline_setup_hwobj

        acq = queue_model_objects.Acquisition()
        acq.acquisition_parameters = \
            copy.deepcopy(parameters)
        acq.acquisition_parameters.collect_agent = \
            queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
        
        acq.path_template = self._create_path_template(sample, path_template)

        if self._in_plate_mode:
            acq.acquisition_parameters.take_snapshots = 1

        return acq

    def _create_dc_from_grid(self, sample, grid=None):
        if grid is None:
            grid = self._graphics_manager_hwobj.get_auto_grid()

        grid.set_snapshot(self._graphics_manager_hwobj.\
                          get_scene_snapshot(grid))

        grid_properties = grid.get_properties()

        acq = self._create_acq(sample)
        acq.acquisition_parameters.centred_position = \
            grid.get_centred_position()
        acq.acquisition_parameters.mesh_range = \
            [grid_properties["dx_mm"],
             grid_properties["dy_mm"]]
        acq.acquisition_parameters.num_lines = \
            grid_properties["num_lines"]
        acq.acquisition_parameters.num_images = \
            grid_properties["num_lines"] * \
            grid_properties["num_images_per_line"]
        grid.set_osc_range(acq.acquisition_parameters.osc_range)

        processing_parameters = deepcopy(self._processing_parameters)

        dc = queue_model_objects.DataCollection([acq],
                                                sample.crystals[0],
                                                processing_parameters)

        dc.set_name(acq.path_template.get_prefix())
        dc.set_number(acq.path_template.run_number)
        dc.set_experiment_type(queue_model_enumerables.EXPERIMENT_TYPE.MESH)
        dc.set_requires_centring(False)
        dc.grid = grid

        self._path_template.run_number += 1

        return dc

    def shape_deleted(self, shape, shape_type):
        return

    def shape_created(self, shape, shape_type):
        return

    def shape_changed(self, shape, shape_type):
        return

    def mad_energy_selected(self, name, energy, state):
        """
        Descript. :
        """
        item = self._current_selected_items[0]
        model = item.get_model()

        if state:
            self._path_template.mad_prefix = str(name)
        else:
            self._path_template.mad_prefix = ''

        run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
            get_next_run_number(self._path_template)

        data_path_widget = self.get_data_path_widget()
        data_path_widget.set_run_number(run_number)
        data_path_widget.set_prefix(self._path_template.base_prefix)

        if self.isEnabled():
            if isinstance(item, Qt4_queue_item.TaskQueueItem) and \
                   not isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                model.set_name(self._path_template.get_prefix())
                item.setText(0, model.get_name())

    def refresh_current_item(self):
        if len(self._current_selected_items) > 0:
            item = self._current_selected_items[0]
            model = item.get_model()
            if self.isEnabled():
                if isinstance(item, Qt4_queue_item.TaskQueueItem) and \
                     not isinstance(item, Qt4_queue_item.DataCollectionGroupQueueItem):
                    name = self._path_template.get_prefix()
                    model.set_name(name)
                    item.setText(0, model.get_display_name())
