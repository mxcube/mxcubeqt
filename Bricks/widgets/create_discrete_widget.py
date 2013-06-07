import logging
import ShapeHistory as shape_history
import queue_item
import copy
import widget_utils
import math
import queue_model_objects_v1 as queue_model_objects

from qt import *
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from widgets.acquisition_widget import AcquisitionWidget
from widgets.acquisition_widget_vertical_layout \
    import AcquisitionWidgetVerticalLayout
from widgets.widget_utils import DataModelInputBinder
from create_task_base import CreateTaskBase

from widgets.processing_widget import ProcessingWidget


class CreateDiscreteWidget(CreateTaskBase):
    def __init__(self,parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Discrete')

        if not name:
            self.setName("create_discrete_widget")

        #
        # Data attributes
        #
        self._path_template = queue_model_objects.PathTemplate()
        self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
        self._energy_scan_result = queue_model_objects.EnergyScanResult()
        self._processing_parameters = queue_model_objects.ProcessingParameters()
        self.previous_energy = None
        

        #
        # Layout
        #
        v_layout = QVBoxLayout(self, 2, 5, "v_layout")
        self._acq_gbox = QVGroupBox('Acquisition', self, 'acq_gbox')
        self._acq_widget = AcquisitionWidget(self._acq_gbox, 
                                            "acquisition_widget",
                                            layout = AcquisitionWidgetVerticalLayout,
                                            acq_params =  self._acquisition_parameters,
                                            path_template = self._path_template)


        self._data_path_gbox = QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox,
                                                'create_dc_path_widget',
                                                data_model = self._path_template,
                                                layout = DataPathWidgetVerticalLayout)

        self._processing_gbox = QVGroupBox('Processing', self, 
                                           'processing_gbox')

        self._processing_widget = ProcessingWidget(self._processing_gbox,
                                                   data_model = self._processing_parameters)
        
        v_layout.addWidget(self._acq_gbox)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addWidget(self._processing_gbox)
        v_layout.addStretch()


        self.connect(self._acq_widget, PYSIGNAL('mad_energy_selected'),
                     self.mad_energy_selected)


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


    def _selection_changed(self, tree_item):
        sample_view_item = self.get_sample_item()
        
        if isinstance(tree_item, queue_item.TaskQueueItem):
            data_collection = tree_item.get_model()
            self._path_template = data_collection.acquisitions[0].path_template
            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters
            self._energy_scan_result = queue_model_objects.EnergyScanResult()
            self._processing_parameters = data_collection.processing_parameters
            self._energy_scan_result = data_collection.crystal.energy_scan_result
        else:
            self._path_template = queue_model_objects.PathTemplate()
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._energy_scan_result = queue_model_objects.EnergyScanResult()
            self._processing_parameters = queue_model_objects.ProcessingParameters()
             
            if sample_view_item:
                sample_data_model = sample_view_item.get_model()
                self.update_processing_parameters(sample_data_model.crystals[0])
       
        self._data_path_widget.update_data_model(self._path_template)
        self._acq_widget.update_data_model(self._acquisition_parameters,
                                           self._path_template)
        self._processing_widget.update_data_model(self._processing_parameters)
        self._acq_widget.set_energies(self._energy_scan_result)

        

    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, parent_task_node, sample):       
        selected_positions = []
        tasks = []

        if not self._selected_positions:
            cpos = None

            if self._tree_brick.diffractometer_hwobj:
                pos_dict = self._tree_brick.diffractometer_hwobj.getPositions()
                cpos = queue_model_objects.CentredPosition(pos_dict)

            logging.getLogger("user_level_log").\
                info("No centred position(s) was selected " + str(cpos) + \
                     " (current position) will be used.")

            selected_shapes = [shape_history.Point(None, cpos, None)]
        else:
            selected_shapes = self._shape_history.selected_shapes

        invalid = False
                
        if invalid:
            msg = "There are one or more invalid values among the" +\
                " collection parameters."

            logging.getLogger("user_level_log").\
                warning(msg)
            
        for shape in selected_shapes:
            snapshot = None
            
            if isinstance(shape, shape_history.Point):
                sc = None
                
                if not shape.get_drawing():
                    sc = queue_model_objects.SampleCentring()
                    sc.set_name('sample-centring')
                    tasks.append(sc)

                if shape.qub_point is not None:
                    snapshot = self._shape_history.get_snapshot([shape.qub_point])
                else:
                    snapshot = self._shape_history.get_snapshot([])

                # Acquisition for start position
                acq = queue_model_objects.Acquisition()
                acq.acquisition_parameters = \
                    copy.deepcopy(self._acquisition_parameters)
                acq.acquisition_parameters.collect_agent = \
                    queue_model_objects.COLLECTION_ORIGIN.MXCUBE
                acq.acquisition_parameters.\
                    centred_position = copy.deepcopy(shape.get_centred_positions()[0])                
                acq.path_template = copy.deepcopy(self._path_template)
                acq.acquisition_parameters.centred_position.\
                    snapshot_image = snapshot

                processing_parameters = copy.deepcopy(self._processing_parameters)


                acq.path_template.suffix = self._session_hwobj.suffix
                
                dc = queue_model_objects.DataCollection([acq],
                                                        sample.crystals[0],
                                                        processing_parameters)

                dc.set_name(acq.path_template.get_prefix())
                dc.set_number(acq.path_template.run_number)

                dc.experiment_type = queue_model_objects.EXPERIMENT_TYPE.NATIVE

                if sc:
                    sc.set_task(dc)

                # Increase run number for next collection
                self.set_run_number(self._path_template.run_number + 1)
                tasks.append(dc)

        return tasks
    
        
