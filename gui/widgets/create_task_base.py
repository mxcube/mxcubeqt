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

import os
import abc
import logging
from copy import deepcopy

from gui.utils import queue_item, QtImport
from HardwareRepository.HardwareObjects import (
    queue_model_objects,
    queue_model_enumerables,
)

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateTaskBase(QtImport.QWidget):
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

    acqParametersConflictSignal = QtImport.pyqtSignal(bool)
    pathTempleConflictSignal = QtImport.pyqtSignal(bool)

    def __init__(self, parent, name, fl, task_node_name="Unamed task-node"):
        QtImport.QWidget.__init__(self, parent, QtImport.Qt.WindowFlags(fl))
        self.setObjectName(name)

        self._tree_brick = None
        self._task_node_name = task_node_name
        self._acquisition_parameters = None
        self._processing_parameters = None

        # Centred positons that currently are selected in the parent
        # widget, position_history_brick.
        self._selected_positions = []

        # Abstract attributes
        self._acq_widget = None
        self._data_path_widget = None
        self._current_selected_items = []
        self._path_template = None
        self._enable_compression = None

        self._in_plate_mode = HWR.beamline.diffractometer.in_plate_mode()
        try:
            HWR.beamline.energy.connect("energyChanged", self.set_energy)
            HWR.beamline.energy.connect(
                "energyLimitsChanged", self.set_energy_limits
            )
            HWR.beamline.transmission.connect(
                "transmissionChanged", self.set_transmission
            )
            HWR.beamline.transmission.connect(
                "limitsChanged", self.set_transmission_limits
            )
            HWR.beamline.resolution.connect(
                "valueChanged", self.set_resolution
            )
            HWR.beamline.resolution.connect(
                "limitsChanged", self.set_resolution_limits
            )
            HWR.beamline.diffractometer.omega.connect(
                "valueChanged", self.set_osc_start
            )
            HWR.beamline.diffractometer.kappa.connect(
                "valueChanged", self.set_kappa
            )
            HWR.beamline.diffractometer.kappa_phi.connect(
                "valueChanged", self.set_kappa_phi
            )
            HWR.beamline.detector.connect(
                "detectorRoiModeChanged", self.set_detector_roi_mode
            )
            HWR.beamline.detector.connect(
                "expTimeLimitsChanged", self.set_detector_exp_time_limits
            )
            HWR.beamline.beam.connect(
                "beamInfoChanged", self.set_beam_info
            )

            HWR.beamline.resolution.update_values()
            HWR.beamline.detector.update_values()
            self.set_resolution_limits(HWR.beamline.resolution.get_limits())
        except AttributeError as ex:
            msg = "Could not connect to one or more hardware objects " + str(ex)
            logging.getLogger("HWR").warning(msg)

    def set_expert_mode(self, state):
        if self._acq_widget:
            self._acq_widget.acq_widget_layout.energy_label.setEnabled(state)
            self._acq_widget.acq_widget_layout.energy_ledit.setEnabled(state)
            if self._acq_widget.acq_widget_layout.findChild(
                QtImport.QCheckBox, "mad_cbox"
            ):
                self._acq_widget.acq_widget_layout.mad_cbox.setEnabled(state)
                self._acq_widget.acq_widget_layout.energies_combo.setEnabled(state)
            if self._acq_widget.acq_widget_layout.findChild(
                QtImport.QLabel, "first_image_label"
            ):
                self._acq_widget.acq_widget_layout.first_image_label.setEnabled(state)
                self._acq_widget.acq_widget_layout.first_image_ledit.setEnabled(state)

    def set_run_processing_parallel(self, state):
        pass

    def enable_compression(self, state):
        if self._data_path_widget:
            self._enable_compression = state
            self._data_path_widget.data_path_layout.compression_cbox.setChecked(state)
            self._data_path_widget.data_path_layout.compression_cbox.setVisible(state)
            self._data_path_widget.update_file_name()

    def init_models(self):
        self.init_acq_model()
        self.init_data_path_model()

    def init_acq_model(self):
        if self._acq_widget:
            def_acq_parameters = HWR.beamline.get_default_acquisition_parameters()
            self._acquisition_parameters.set_from_dict(def_acq_parameters.as_dict())
            if HWR.beamline.diffractometer.in_plate_mode():
                self._acq_widget.use_kappa(False)
                self._acq_widget.use_max_osc_range(True)
            else:
                self._acq_widget.use_kappa(True)
                self._acq_widget.use_max_osc_range(False)
            self._acq_widget.update_osc_total_range()
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()

    def init_data_path_model(self):
        # Initialize the path_template of the widget to default
        # values read from the beamline setup
        if self._data_path_widget:
            self._data_path_widget.set_base_image_directory(
                HWR.beamline.session.get_base_image_directory()
            )
            self._data_path_widget.set_base_process_directory(
                HWR.beamline.session.get_base_process_directory()
            )

            (data_directory, proc_directory) = self.get_default_directory()
            self._path_template = HWR.beamline.get_default_path_template()
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix()
            self._path_template.run_number = HWR.beamline.queue_model.get_next_run_number(
                  self._path_template
            )
            self._path_template.compression = self._enable_compression
        else:
            self._path_template = queue_model_objects.PathTemplate()

    def tab_changed(self, tab_index, tab):
        # Update the selection if in the main tab and logged in to
        # ISPyB
        if tab_index is 0 and HWR.beamline.session.proposal_code:
            self.update_selection()

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
            path_conflict = HWR.beamline.queue_model.check_for_path_collisions(
                self._path_template
            )
            self._data_path_widget.indicate_path_conflict(path_conflict)
            self._tree_brick.data_path_changed(path_conflict)
            self.pathTempleConflictSignal.emit(path_conflict)

    def set_tree_brick(self, brick):
        self._tree_brick = brick

    def get_sample_item(self, item):
        if isinstance(item, queue_item.SampleQueueItem):
            return item
        elif isinstance(item, queue_item.BasketQueueItem):
            return item
        elif isinstance(item, queue_item.TaskQueueItem):
            return item.get_sample_view_item()
        else:
            return None

    def get_group_item(self, item):
        if isinstance(item, queue_item.DataCollectionGroupQueueItem):
            return item
        elif isinstance(item, queue_item.TaskQueueItem):
            return self.item.parent()
        else:
            return None

    def get_task_node_name(self):
        return self._task_node_name

    def get_acquisition_widget(self):
        return self._acq_widget

    def get_data_path_widget(self):
        return self._data_path_widget

    def _item_is_group_or_sample(self):
        result = False

        if self._current_selected_items:
            item = self._current_selected_items[0]

            if isinstance(item, queue_item.SampleQueueItem) or isinstance(
                item, queue_item.DataCollectionGroupQueueItem
            ):
                result = True
        return result

    def _item_is_dc(self):
        result = False

        if self._current_selected_items:
            item = self._current_selected_items[0]

            if isinstance(item, queue_item.TaskQueueItem) and not isinstance(
                item, queue_item.DataCollectionGroupQueueItem
            ):
                result = True
        return result

    def set_energy(self, energy, wavelength):
        if not self._item_is_dc() and energy is not None:
            acq_widget = self.get_acquisition_widget()

            if acq_widget:
                acq_widget.previous_energy = energy
                acq_widget.update_energy(energy, wavelength)

    def set_transmission(self, trans):
        if trans is not None:
            acq_widget = self.get_acquisition_widget()

            if not self._item_is_dc() and acq_widget:
                acq_widget.update_transmission(trans)

    def set_resolution(self, res):
        if res is not None:
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

    def set_beam_info(self, beam_info):
        pass

    def get_default_prefix(self, sample_data_node=None, generic_name=False):
        prefix = HWR.beamline.session.get_default_prefix(
            sample_data_node, generic_name
        )
        return prefix

    def get_default_directory(self, tree_item=None, sub_dir=""):
        group_name = HWR.beamline.session.get_group_name()

        if group_name:
            sub_dir = group_name + "/" + sub_dir

        if tree_item:
            item = self.get_sample_item(tree_item)
            if isinstance(tree_item, queue_item.BasketQueueItem):
                sub_dir += str(tree_item.get_model().get_location())
            else:
                if isinstance(tree_item, queue_item.SampleQueueItem):
                    if item.get_model().lims_id == -1:
                        sub_dir += ""

        data_directory = HWR.beamline.session.get_image_directory(sub_dir)

        proc_directory = HWR.beamline.session.get_process_directory(sub_dir)

        return (data_directory, proc_directory)

    def ispyb_logged_in(self, logged_in):
        self.init_models()
        self.update_selection()

    def select_shape_with_cpos(self, cpos):
        HWR.beamline.sample_view.select_shape_with_cpos(cpos)

    def selection_changed(self, items):
        if items:
            if len(items) == 1:
                self._current_selected_items = items
                self.single_item_selection(items[0])
            elif len(items) > 1:
                sample_items = []

                # Allow mutiple selections on sample items, only.
                for item in items:
                    if isinstance(item, queue_item.SampleQueueItem):
                        sample_items.append(item)

                if sample_items:
                    self._current_selected_items = sample_items
                    self.single_item_selection(items[0])
                    # self.multiple_item_selection(sample_items)
        else:
            self.setDisabled(True)

    def update_selection(self):
        self.selection_changed(self._current_selected_items)

    def single_item_selection(self, tree_item):
        sample_item = self.get_sample_item(tree_item)
        if self._data_path_widget:
            self._data_path_widget.enable_macros = False

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_data_model = sample_item.get_model()
            self._path_template = deepcopy(self._path_template)

            self._acquisition_parameters.centred_position.snapshot_image = None
            self._acquisition_parameters = deepcopy(self._acquisition_parameters)
            self._acquisition_parameters.centred_position.snapshot_image = (
                HWR.beamline.sample_view.get_scene_snapshot()
            )

            # Sample with lims information, use values from lims
            # to set the data path. Or has a specific user group set.
            if sample_data_model.lims_id != -1:
                prefix = self.get_default_prefix(sample_data_model)
                (data_directory, proc_directory) = self.get_default_directory(
                    tree_item, sub_dir="%s%s" % (prefix.split("-")[0], os.path.sep)
                )

                # TODO create templates to customize this
                # self._path_template.directory = data_directory
                # self._path_template.process_directory = proc_directory
                self._path_template.base_prefix = prefix
            elif HWR.beamline.session.get_group_name() != "":
                base_dir = HWR.beamline.session.get_base_image_directory()
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

            # if sample_data_model.lims_id == -1 and \
            #   not None in (sample_data_model.location):
            #    (data_directory, proc_directory) = self.get_default_directory(tree_item)
            #    self._path_template.directory = data_directory
            #    self._path_template.process_directory = proc_directory

            # Get the next available run number at this level of the model.
            self._path_template.run_number = (
                HWR.beamline.queue_model.get_next_run_number(self._path_template)
            )

            # Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                self._acq_widget.use_kappa(True)
                sample_data_model = sample_item.get_model()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)
                self._acq_widget.update_data_model(
                    self._acquisition_parameters, self._path_template
                )
                # self.get_acquisition_widget().use_osc_start(False)

            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)
                self._data_path_widget.enable_macros = True
            self.setDisabled(False)

        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self._path_template = deepcopy(self._path_template)
            self._acquisition_parameters = deepcopy(self._acquisition_parameters)
            # (data_directory, proc_directory) = self.get_default_directory(tree_item)
            # self._path_template.directory = data_directory
            # self._path_template.process_directory = proc_directory

            # Update energy transmission and resolution
            if self._acq_widget:
                self._update_etr()
                self._acq_widget.use_kappa(True)
                self._acq_widget.update_data_model(
                    self._acquisition_parameters, self._path_template
                )
            if self._data_path_widget:
                self._data_path_widget.update_data_model(self._path_template)
                self._data_path_widget.enable_macros = True
            self.setDisabled(False)

        elif isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            self.setDisabled(True)

        # if self._acq_widget:
        #    self._acq_widget.set_enable_parameter_update(\
        #         not isinstance(tree_item, queue_item.TaskQueueItem))

    def _update_etr(self):
        default_acq_params = HWR.beamline.get_default_acquisition_parameters()
        for tag in ("kappa", "kappa_phi", "energy", "transmission", "resolution", ):
            setattr(self._acquisition_parameters, tag, getattr(default_acq_params, tag))

        set_omega = True
        if self._acq_widget:
            if self._acq_widget.acq_widget_layout.findChild(
                QtImport.QCheckBox, "max_osc_range_cbx"
            ):
                if self._acq_widget.acq_widget_layout.max_osc_range_cbx.isChecked():
                    set_omega = False
        if set_omega:
            self._acquisition_parameters.osc_start = default_acq_params.osc_start

        self._acq_widget.value_changed_list = []
        self._acq_widget._acquisition_mib.clear_edit()

    """
    def multiple_item_selection(self, tree_items):
        tree_item = tree_items[0]

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_data_model = tree_item.get_model()
            self._path_template = deepcopy(self._path_template)
            self._acquisition_parameters = copy.deepcopy(self._acquisition_parameters)

            # Sample with lims information, use values from lims
            # to set the data path.
            (data_directory, proc_directory) = self.get_default_directory(\
                 sub_dir = '<acronym>%s<sample_name>%s' % (os.path.sep, os.path.sep))
            self._path_template.directory = data_directory
            self._path_template.process_directory = proc_directory
            self._path_template.base_prefix = self.get_default_prefix(generic_name = True)

            # Get the next available run number at this level of the model.
            self._path_template.run_number = HWR.beamline.queue_model.\
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
            kappa = None
            kappa_phi = None
            self._acq_widget.use_kappa(False)
            if position:
                if len(self._current_selected_items) == 1:
                    item = self._current_selected_items[0]
                    cpos = position.get_centred_position()
                    if hasattr(cpos, "kappa"):
                        kappa = cpos.kappa
                    if hasattr(cpos, "kappa_phi"):
                        kappa_phi = cpos.kappa_phi
                    if isinstance(item, queue_item.TaskQueueItem):
                        snapshot = HWR.beamline.sample_view.get_scene_snapshot(
                            position
                        )
                        cpos.snapshot_image = snapshot
                        self._acquisition_parameters.centred_position = cpos
            else:
                self._acq_widget.use_kappa(True)
                kappa = HWR.beamline.diffractometer.kappa.get_value()
                kappa_phi =  HWR.beamline.diffractometer.kappa_phi.get_value()

            if kappa:
                self.set_kappa(kappa)
            if kappa_phi:
                self.set_kappa_phi(kappa_phi)

    # Should be called by the object that calls create_task,
    # and add_task.
    def approve_creation(self):
        result = True

        path_conflict = HWR.beamline.queue_model.check_for_path_collisions(
            self._path_template
        )

        if path_conflict:
            logging.getLogger("GUI").error(
                "The current path settings will overwrite data "
                + "from another task. Correct the problem before "
                + "adding to queue"
            )
            result = False

        if self._acq_widget is not None:
            parameter_conflict = self._acq_widget.check_parameter_conflict()
            if len(parameter_conflict) > 0:
                msg = "Entered value of "
                for item in parameter_conflict:
                    msg = msg + "%s, " % item
                msg = msg[:-2]
                msg += (
                    " is out of range. Correct the input value(s) before "
                    + "adding item to the queue"
                )
                logging.getLogger("GUI").error(msg)
                result = False

        return result

    # Called by the owning widget (task_toolbox_widget) to create
    # a task. When a task_node is selected.
    def create_task(self, sample, shape):
        (tasks, sc) = ([], None)

        dm = HWR.beamline.diffractometer
        sample_is_mounted = False
        if self._in_plate_mode:
            try:
                sample_is_mounted = (
                    HWR.beamline.plate_manipulator.getLoadedSample().getCoords()
                    == sample.location
                )
            except BaseException:
                sample_is_mounted = False
        else:
            try:
                sample_is_mounted = (
                    HWR.beamline.sample_changer.getLoadedSample().getCoords()
                    == sample.location
                )

            except AttributeError:
                sample_is_mounted = False

        fully_automatic = not dm.user_confirms_centring

        free_pin_mode = sample.free_pin_mode
        temp_tasks = self._create_task(sample, shape)

        if len(temp_tasks) == 0:
            return

        if (not free_pin_mode) and (not sample_is_mounted) or (not shape):
            # No centred positions selected, or selected sample not
            # mounted create sample centring task.

            # Check if the tasks requires centring, assumes that all
            # the "sub tasks" has the same centring requirements.
            if temp_tasks[0].requires_centring():
                if (
                    self._tree_brick.dc_tree_widget.centring_method
                    == queue_model_enumerables.CENTRING_METHOD.MANUAL
                ):

                    # Manual 3 click centering
                    acq_par = None
                    kappa = None
                    kappa_phi = None
                    task_label = "Manual centring"

                    if isinstance(temp_tasks[0], queue_model_objects.DataCollection):
                        acq_par = temp_tasks[0].acquisitions[0].acquisition_parameters
                    elif isinstance(
                        temp_tasks[0], queue_model_objects.Characterisation
                    ):
                        acq_par = (
                            temp_tasks[0]
                            .reference_image_collection.acquisitions[0]
                            .acquisition_parameters
                        )

                    if acq_par:
                        kappa = acq_par.kappa
                        kappa_phi = acq_par.kappa_phi
                        if kappa is not None and kappa_phi is not None:
                            task_label = "Manual centring (kappa=%0.1f,phi=%0.1f)" % (
                                kappa,
                                kappa_phi,
                            )

                    sc = queue_model_objects.SampleCentring(
                        task_label, kappa, kappa_phi
                    )
                elif (
                    self._tree_brick.dc_tree_widget.centring_method
                    == queue_model_enumerables.CENTRING_METHOD.LOOP
                ):

                    # Optical automatic centering with user confirmation
                    sc = queue_model_objects.OpticalCentring(user_confirms=True)
                elif (
                    self._tree_brick.dc_tree_widget.centring_method
                    == queue_model_enumerables.CENTRING_METHOD.FULLY_AUTOMATIC
                ):

                    # Optical automatic centering without user confirmation
                    sc = queue_model_objects.OpticalCentring()
                elif (
                    self._tree_brick.dc_tree_widget.centring_method
                    == queue_model_enumerables.CENTRING_METHOD.XRAY
                ):

                    # Xray centering
                    # TODO add dg_group for XrayCentering
                    # dc_group = self._tree_brick.dc_tree_widget.create_task_group(sample)
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
    def _create_task(self, sample, shape):
        pass

    def _create_path_template(self, sample, path_template):
        """Creates path template and expands macro keywords:
           %n : container name (dewar, puck, etc)
           %c : container number
           %u : username
           %p : sample position
           %s : sample name
        """

        acq_path_template = deepcopy(path_template)

        if "<sample_name>" in acq_path_template.directory:
            name = sample.get_name().replace(":", "-")
            acq_path_template.directory = acq_path_template.directory.replace(
                "<sample_name>", name
            )
            acq_path_template.process_directory = acq_path_template.process_directory.replace(
                "<sample_name>", name
            )

        if "<acronym>-<name>" in acq_path_template.base_prefix:
            acq_path_template.base_prefix = self.get_default_prefix(sample)
            acq_path_template.run_number = HWR.beamline.queue_model.get_next_run_number(
                acq_path_template
            )

        if "<acronym>" in acq_path_template.directory:
            prefix = self.get_default_prefix(sample)
            acronym = prefix.split("-")[0]
            acq_path_template.directory = acq_path_template.directory.replace(
                "<acronym>", acronym
            )
            acq_path_template.process_directory = acq_path_template.process_directory.replace(
                "<acronym>", acronym
            )

        # TODO create a method get_user_name in Session
        user_name = ""
        if os.getenv("SUDO_USER"):
            user_name = os.getenv("SUDO_USER")
        else:
            user_name = os.getenv("USER")

        # expand macro keywords in the directory path
        acq_path_template.directory = acq_path_template.directory.replace(
            "%c", str(sample.location[0])
        )
        acq_path_template.directory = acq_path_template.directory.replace(
            "%p", str(sample.location[1])
        )
        acq_path_template.directory = acq_path_template.directory.replace(
            "%s", str(sample.name)
        )
        acq_path_template.directory = acq_path_template.directory.replace(
            "%u", user_name
        )

        # expand macro keywords in the prefix
        acq_path_template.base_prefix = acq_path_template.base_prefix.replace(
            "%c", str(sample.location[0])
        )
        acq_path_template.base_prefix = acq_path_template.base_prefix.replace(
            "%p", str(sample.location[1])
        )
        acq_path_template.base_prefix = acq_path_template.base_prefix.replace(
            "%s", str(sample.name)
        )
        acq_path_template.base_prefix = acq_path_template.base_prefix.replace(
            "%u", user_name
        )
        acq_path_template.base_prefix

        return acq_path_template

    def _create_acq(self, sample):
        parameters = self._acquisition_parameters
        path_template = self._path_template
        processing_parameters = self._processing_parameters

        acq = queue_model_objects.Acquisition()

        parameters.centred_position.snapshot_image = None
        acq.acquisition_parameters = deepcopy(parameters)
        self._acquisition_parameters.centred_position.snapshot_image = (
            HWR.beamline.sample_view.get_scene_snapshot()
        )
        acq.acquisition_parameters.collect_agent = (
            queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
        )

        acq.path_template = self._create_path_template(sample, path_template)

        if self._in_plate_mode:
            acq.acquisition_parameters.take_snapshots = 1

        return acq

    def _create_dc_from_grid(self, sample, grid=None):
        if grid is None:
            grid = HWR.beamline.sample_view.create_auto_grid()

        grid.set_snapshot(HWR.beamline.sample_view.get_snapshot(grid))

        grid_properties = grid.get_properties()

        acq = self._create_acq(sample)
        acq.acquisition_parameters.centred_position = grid.get_centred_position()
        acq.acquisition_parameters.mesh_range = [
            grid_properties["dx_mm"],
            grid_properties["dy_mm"],
        ]
        acq.acquisition_parameters.num_lines = grid_properties["num_lines"]
        acq.acquisition_parameters.num_images = (
            grid_properties["num_lines"] * grid_properties["num_images_per_line"]
        )
        grid.set_osc_range(acq.acquisition_parameters.osc_range)

        processing_parameters = deepcopy(self._processing_parameters)

        dc = queue_model_objects.DataCollection(
            [acq], sample.crystals[0], processing_parameters
        )

        dc.set_name(acq.path_template.get_prefix())
        dc.set_number(acq.path_template.run_number)
        dc.set_experiment_type(queue_model_enumerables.EXPERIMENT_TYPE.MESH)
        dc.set_requires_centring(False)
        dc.grid = grid

        self._path_template.run_number += 1

        return dc

    def shape_deleted(self, shape, shape_type):
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
            self._path_template.mad_prefix = ""

        run_number = HWR.beamline.queue_model.get_next_run_number(
            self._path_template
        )

        data_path_widget = self.get_data_path_widget()
        data_path_widget.set_run_number(run_number)
        data_path_widget.set_prefix(self._path_template.base_prefix)

        if self.isEnabled():
            if isinstance(item, queue_item.TaskQueueItem) and not isinstance(
                item, queue_item.DataCollectionGroupQueueItem
            ):
                model.set_name(self._path_template.get_prefix())
                item.setText(0, model.get_name())

    def refresh_current_item(self):
        if len(self._current_selected_items) > 0:
            item = self._current_selected_items[0]
            model = item.get_model()
            if self.isEnabled():
                if isinstance(item, queue_item.TaskQueueItem) and not isinstance(
                    item, queue_item.DataCollectionGroupQueueItem
                ):
                    name = self._path_template.get_prefix()
                    model.set_name(name)
                    item.setText(0, model.get_display_name())

    def set_osc_total_range(self, num_images=None, mesh=False):
        """Updates osc totol range. Limits are changed if a plate is used.
           - For simple oscillation osc_range is defined by osc_start and
             osc_start top limit.
           - For mesh osc_range is defined by number of images per line
             and osc in the middle of mesh
        """
        if HWR.beamline.diffractometer.in_plate_mode() and self._acq_widget:
            set_max_range = False

            if num_images is None:
                try:
                    num_images = int(
                        self._acq_widget.acq_widget_layout.num_images_ledit.text()
                    )
                except BaseException:
                    num_images = 0

            if self._acq_widget.acq_widget_layout.findChild(
                QtImport.QCheckBox, "max_osc_range_cbx"
            ):
                if self._acq_widget.acq_widget_layout.max_osc_range_cbx.isChecked():
                    set_max_range = True
                else:
                    num_images = 0

            exp_time = None
            exp_time = float(self._acq_widget.acq_widget_layout.exp_time_ledit.text())

            scan_limits = HWR.beamline.diffractometer.get_scan_limits(
                num_images, exp_time
            )

            self._acq_widget.osc_total_range_validator.setTop(
                abs(scan_limits[1] - scan_limits[0])
            )
            self._acq_widget.acq_widget_layout.osc_total_range_ledit.setToolTip(
                "Oscillation range limits 0 : %0.5f\n4 digits precision."
                % abs(scan_limits[1] - scan_limits[0])
            )

            self._acq_widget.osc_start_validator.setRange(
                scan_limits[0], scan_limits[1], 4
            )
            self._acq_widget.acq_widget_layout.osc_start_ledit.setToolTip(
                "Oscillation start limits %0.2f : %0.2f\n"
                % (scan_limits[0], scan_limits[1])
                + "4 digits precision."
            )

            if set_max_range:
                if mesh:
                    self._acq_widget.acq_widget_layout.osc_start_ledit.setText(
                        "%.4f" % ((scan_limits[0] + scan_limits[1]) / 2)
                    )
                else:
                    self._acq_widget.acq_widget_layout.osc_start_ledit.setText(
                        "%.4f" % (scan_limits[0] + 0.01)
                    )
                self._acq_widget.acq_widget_layout.osc_total_range_ledit.setText(
                    "%.4f" % abs(scan_limits[1] - scan_limits[0] - 0.01)
                )
                if num_images:
                    osc_range_per_frame = (
                        int(
                            abs(scan_limits[1] - scan_limits[0] - 0.01)
                            / num_images
                            * 1000
                        )
                        / 1000.0
                    )
                    self._acq_widget.acq_widget_layout.osc_range_ledit.setText(
                        "%.3f" % osc_range_per_frame
                    )
