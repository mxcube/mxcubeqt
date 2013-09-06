import ShapeHistory as shape_history
import queue_item
import copy
import qt

import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables

from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from widgets.acquisition_widget import AcquisitionWidget
from create_task_base import CreateTaskBase

from widgets.processing_widget import ProcessingWidget


class CreateDiscreteWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, fl=0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Discrete')

        if not name:
            self.setName("create_discrete_widget")

        #
        # Data attributes
        #
        self.previous_energy = None
        self.init_models()

        #
        # Layout
        #
        v_layout = qt.QVBoxLayout(self, 2, 5, "v_layout")
        self._acq_gbox = qt.QVGroupBox('Acquisition', self, 'acq_gbox')
        self._acq_widget = \
            AcquisitionWidget(self._acq_gbox,
                              "acquisition_widget",
                              layout='vertical',
                              acq_params=self._acquisition_parameters,
                              path_template=self._path_template)

        self._data_path_gbox = qt.QVGroupBox('Data location',
                                             self, 'data_path_gbox')
        self._data_path_widget = \
            DataPathWidget(self._data_path_gbox,
                           'create_dc_path_widget',
                           data_model=self._path_template,
                           layout=DataPathWidgetVerticalLayout)

        self._processing_gbox = qt.QVGroupBox('Processing', self,
                                              'processing_gbox')

        self._processing_widget = \
            ProcessingWidget(self._processing_gbox,
                             data_model=self._processing_parameters)

        v_layout.addWidget(self._acq_gbox)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addWidget(self._processing_gbox)
        v_layout.addStretch()

        self.connect(self._acq_widget, qt.PYSIGNAL('mad_energy_selected'),
                     self.mad_energy_selected)

        self.connect(self._data_path_widget.data_path_widget_layout.prefix_ledit,
                     qt.SIGNAL("textChanged(const QString &)"),
                     self._prefix_ledit_change)

        self.connect(self._data_path_widget.data_path_widget_layout.run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"),
                     self._run_number_ledit_change)

        self.connect(self._acq_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

    def init_models(self):
        CreateTaskBase.init_models(self)

        self._energy_scan_result = queue_model_objects.EnergyScanResult()
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.\
                               detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less
            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters()

            try:
                transmission = self._beamline_setup_hwobj.transmission_hwobj.getAttFactor()
                transmission = round(float(transmission), 2)
            except AttributeError:
                transmission = 0

            try:
                resolution = self._beamline_setup_hwobj.resolution_hwobj.getPosition()
                resolution = round(float(resolution), 2)
            except AttributeError:
                resolution = 0

            try:
                energy = self._beamline_setup_hwobj.\
                         energy_hwobj.getCurrentEnergy()
                if energy:
                    energy = round(float(energy), 4)
                else:
                    energy = round(float(-1), 4)
            except AttributeError:
                energy = 0

            self._acquisition_parameters.resolution = resolution
            self._acquisition_parameters.energy = energy
            self._acquisition_parameters.transmission = transmission
        else:
            self._acquisition_parameters = queue_model_objects.\
                                           AcquisitionParameters()

    def set_tunable_energy(self, state):
        self._acq_widget.set_tunable_energy(state)

    def update_processing_parameters(self, crystal):
        self._processing_parameters.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma
        self._processing_widget.update_data_model(self._processing_parameters)

    def select_shape_with_cpos(self, cpos):
        self._shape_history._drawing_event.de_select_all()

        for shape in self._shape_history.get_shapes():
            if len(shape.get_centred_positions()) == 1:
                if shape.get_centred_positions()[0] is cpos:
                    self._shape_history._drawing_event.set_selected(shape)

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):

            sample_data_model = self.get_sample_item(tree_item).get_model()
            self.update_processing_parameters(sample_data_model.crystals[0])
            self._acq_widget.\
                 set_energies(sample_data_model.\
                              crystals[0].energy_scan_result)

        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
            self.setDisabled(False)
            data_collection = tree_item.get_model()

            if data_collection.get_path_template():
                self._path_template = data_collection.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
            
            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters

            if len(data_collection.acquisitions) == 1:
                self.select_shape_with_cpos(self._acquisition_parameters.\
                                            centred_position)

            self._energy_scan_result = queue_model_objects.EnergyScanResult()
            self._processing_parameters = data_collection.processing_parameters
            self._energy_scan_result = data_collection.crystal.\
                                       energy_scan_result
            self._acq_widget.set_energies(self._energy_scan_result)
        else:
            # Disable control
            self.setDisabled(True)

        if isinstance(tree_item, queue_item.SampleQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionGroupQueueItem) or \
           isinstance(tree_item, queue_item.DataCollectionQueueItem):

            self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
        
    def approve_creation(self):
        return CreateTaskBase.approve_creation(self)

    def subwedges_for_inverse_beam(self, total_num_images, subwedge_size):
        number_of_subwedges = total_num_images / subwedge_size
        subwedges = []

        for subwedge_num in range(0, number_of_subwedges):
            subwedges.append((subwedge_num * subwedge_size + 1, subwedge_size))

        return subwedges

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample):
        tasks = []
        sample_is_mounted = self._beamline_setup_hwobj.sample_changer_hwobj.\
                            is_mounted_sample(sample)

        if (not self._selected_positions) or (not sample_is_mounted):
            # No centred positions selected, or selected sample not
            # mounted create sample centring task.
            sc = self.create_sample_centring(sample)
            tasks.append(sc)
            cpos_list = [None]
        else:
            # Shapes selected and sample is mounted, get the
            # centred positions for the shapes
            selected_shapes = self._shape_history.selected_shapes
            cpos_list = self.get_centred_positions(selected_shapes)

        if self._acq_widget.use_inverse_beam():

            total_num_images = self._acquisition_parameters.num_images
            subwedge_size = self._acq_widget.get_num_subwedges()

            sub_wedges = self.subwedges_for_inverse_beam(total_num_images,
                                                         subwedge_size)

            for cpos in cpos_list:
                for sw in sub_wedges:
                    tasks.extend(self.create_dc(sample, 1, sw[0], sw[1],
                                                sc=sc, cpos=cpos))
                    tasks.extend(self.create_dc(sample, 2, sw[0], sw[1],
                                                180, sc=sc, cpos=cpos))

        else:
            for cpos in cpos_list:
                tasks.extend(self.create_dc(sample, sc=sc, cpos=cpos))

        return tasks

    def create_sample_centring(self, sample):
        sc = queue_model_objects.SampleCentring()
        sc.set_name('sample-centring')
        return sc

    def get_centred_positions(self, shapes):
        centred_positions = []

        for shape in shapes:
            snapshot = None

            if isinstance(shape, shape_history.Point):
                if shape.qub_point is not None:
                    snapshot = self._shape_history.\
                               get_snapshot([shape.qub_point])
                else:
                    snapshot = self._shape_history.get_snapshot([])

                centred_position = shape.get_centred_positions()[0]
                centred_position.snapshot_image = snapshot
                centred_positions.append(centred_position)

        return centred_positions

    def create_dc(self, sample, run_number=None, start_image=None,
                  num_images=None, osc_start=None, sc=None,
                  cpos=None):
        tasks = []

        # Acquisition for start position
        acq = queue_model_objects.Acquisition()
        acq.acquisition_parameters = \
            copy.deepcopy(self._acquisition_parameters)
        acq.acquisition_parameters.collect_agent = \
            queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
        acq.path_template = copy.deepcopy(self._path_template)

        if cpos:
            acq.acquisition_parameters.centred_position = cpos

        if run_number:
            acq.path_template.run_number = run_number

        if start_image:
            acq.acquisition_parameters.first_image = start_image
            acq.path_template.start_num = start_image

        if num_images:
            acq.acquisition_parameters.num_images = num_images
            acq.path_template.num_files = num_images

        if osc_start:
            acq.acquisition_parameters.osc_start = osc_start

        processing_parameters = copy.deepcopy(self._processing_parameters)
        dc = queue_model_objects.DataCollection([acq],
                                                sample.crystals[0],
                                                processing_parameters)

        dc.set_name(acq.path_template.get_prefix())
        dc.set_number(acq.path_template.run_number)
        dc.experiment_type = queue_model_enumerables.EXPERIMENT_TYPE.NATIVE

        if sc:
            sc.add_task(dc)

        tasks.append(dc)

        self._path_template.run_number = self._beamline_setup_hwobj.\
            queue_model_hwobj.get_next_run_number(self._path_template)
        self._data_path_widget.update_data_model(self._path_template)
        self._acq_widget.update_data_model(self._acquisition_parameters,
                                                       self._path_template)

        return tasks
