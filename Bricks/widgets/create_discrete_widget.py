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

    def mad_energy_selected(self, name, energy, state):
        item = self._current_selected_items[0]
        model = item.get_model()

        if state:
            self._path_template.mad_prefix = name
        else:
            self._path_template.mad_prefix = ''

        run_number = self._beamline_setup_hwobj.queue_model_hwobj.\
            get_next_run_number(self._path_template)

        data_path_widget = self.get_data_path_widget()
        data_path_widget.set_run_number(run_number)
        data_path_widget.set_prefix(self._path_template.base_prefix)

        if self.isEnabled():
            if isinstance(item, queue_item.TaskQueueItem) and \
                   not isinstance(item, queue_item.DataCollectionGroupQueueItem):
                model.set_name(self._path_template.get_prefix())
                item.setText(0, model.get_name())

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            self._processing_parameters = copy.deepcopy(self._processing_parameters)
            self._processing_widget.update_data_model(self._processing_parameters)
            self._acq_widget.disable_inverse_beam(False)

        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
            dc = tree_item.get_model()

            if dc.experiment_type != queue_model_enumerables.EXPERIMENT_TYPE.HELICAL:
                self.setDisabled(False)
                self._acq_widget.disable_inverse_beam(True)

                if dc.get_path_template():
                    self._path_template = dc.get_path_template()

                self._data_path_widget.update_data_model(self._path_template)
                self._acquisition_parameters = dc.acquisitions[0].acquisition_parameters

                if len(dc.acquisitions) == 1:
                    self.select_shape_with_cpos(self._acquisition_parameters.\
                                                centred_position)

                self._processing_parameters = dc.processing_parameters
                self._processing_widget.update_data_model(self._processing_parameters)
            else:
                self.setDisabled(True)
        else:
            self.setDisabled(True)

    def approve_creation(self):
        result = CreateTaskBase.approve_creation(self)
        selected_shapes = self._shape_history.selected_shapes

        for shape in selected_shapes:
            if isinstance(shape, shape_history.Line):
                result = False

        return result

    def get_subwedges(self, total_num_images, subwedge_size,
                      osc_range, osc_offset):
        number_of_subwedges = total_num_images / subwedge_size
        subwedges = []

        for subwedge_num in range(0, number_of_subwedges):
            osc_start = osc_offset + (osc_range * subwedge_size * subwedge_num)
            subwedges.append((subwedge_num * subwedge_size + 1,
                              subwedge_size, osc_start))

        return subwedges

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        tasks = []

        if not shape:
            cpos = queue_model_objects.CentredPosition()
            cpos.snapshot_image = self._shape_history.get_snapshot([])
        else:
            # Shapes selected and sample is mounted, get the
            # centred positions for the shapes
            if isinstance(shape, shape_history.Point):
                snapshot = self._shape_history.\
                           get_snapshot([shape.qub_point])

                cpos = shape.get_centred_positions()[0]
                cpos.snapshot_image = snapshot

        if self._acq_widget.use_inverse_beam():
            total_num_images = self._acquisition_parameters.num_images
            subwedge_size = self._acq_widget.get_num_subwedges()
            osc_range = self._acquisition_parameters.osc_range
            osc_start = self._acquisition_parameters.osc_start
            run_number = self._path_template.run_number

            wedge_one = self.get_subwedges(total_num_images, subwedge_size,
                                           osc_range, osc_start)

            wedge_one = [pair + (run_number,) for pair in wedge_one]

            wedge_two = self.get_subwedges(total_num_images,
                                           subwedge_size, osc_range,
                                           180 + osc_start)
            
            wedge_two = [pair + (run_number + 1,) for pair in wedge_two]

            subwedges = [sw_pair for pair in zip(wedge_one, wedge_two) for sw_pair in pair]

            self._acq_widget.set_use_inverse_beam(False)

            for sw in subwedges:
                tasks.extend(self.create_dc(sample, sw[3], sw[0], sw[1],
                    sw[2], cpos=cpos, inverse_beam = True))
                self._path_template.run_number += 1

        else:
            tasks.extend(self.create_dc(sample, cpos=cpos))
            self._path_template.run_number += 1

        return tasks

    def create_sample_centring(self, sample):
        sc = queue_model_objects.SampleCentring()
        sc.set_name('sample-centring')
        return sc
    
    def create_dc(self, sample, run_number=None, start_image=None,
                  num_images=None, osc_start=None, sc=None,
                  cpos=None, inverse_beam = False):
        tasks = []

        # Acquisition for start position
        acq = queue_model_objects.Acquisition()
        acq.acquisition_parameters = \
            copy.deepcopy(self._acquisition_parameters)
        acq.acquisition_parameters.collect_agent = \
            queue_model_enumerables.COLLECTION_ORIGIN.MXCUBE
        acq.path_template = copy.deepcopy(self._path_template)
        acq.acquisition_parameters.centred_position = cpos

        if '<sample_name>' in acq.path_template.directory:
            name = sample.get_name().replace(':', '-')
            acq.path_template.directory = acq.path_template.directory.\
                                          replace('<sample_name>', name)
            acq.path_template.process_directory = acq.path_template.process_directory.\
                                                  replace('<sample_name>', name)

        if '<acronym>-<name>' in acq.path_template.base_prefix:
            acq.path_template.base_prefix = self.get_default_prefix(sample)
            acq.path_template.run_numer = self._beamline_setup_hwobj.queue_model_hwobj.\
                                          get_next_run_number(acq.path_template)

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

        if inverse_beam:
            acq.acquisition_parameters.inverse_beam = False

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

        self._data_path_widget.update_data_model(self._path_template)
        self._acq_widget.update_data_model(self._acquisition_parameters,
                                                       self._path_template)

        return tasks
