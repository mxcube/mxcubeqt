import queue_model_objects_v1 as queue_model_objects
import queue_item
import logging
import qt
import copy

import ShapeHistory as shape_history

from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout
from widgets.acquisition_widget import AcquisitionWidget
from widgets.processing_widget import ProcessingWidget

class CreateHelicalWidget(CreateTaskBase):
    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Helical')

        if not name:
            self.setName("create_helical_widget")

        #
        # Data attributes
        #
        self.init_models()
        
        self._prev_pos = None
        self._current_pos = None
        self._list_item_map = {}

        #
        # Layout
        #
        #lines_gbox = QGroupBox(self, "lines_group_box")
        v_layout = qt.QVBoxLayout(self, 2, 5, "v_layout")
        self._lines_gbox = qt.QGroupBox('Lines', self, "lines_gbox")
        self._lines_gbox.setColumnLayout(0, qt.Qt.Vertical)
        self._lines_gbox.layout().setSpacing(6)
        self._lines_gbox.layout().setMargin(11)
        lines_gbox_layout = qt.QHBoxLayout(self._lines_gbox.layout())
        lines_gbox_layout.setAlignment(qt.Qt.AlignTop)

        self._list_box = qt.QListBox(self._lines_gbox, "helical_page")
        self._list_box.setSelectionMode(qt.QListBox.Extended)
        self._list_box.setFixedWidth(175)

        lines_gbox_layout.addWidget(self._list_box)

        button_layout = qt.QVBoxLayout(None, 0, 6, "button_layout")
        button_layout.setSpacing(20)
        add_button = qt.QPushButton("+", self._lines_gbox, "add_button")
        add_button.setFixedWidth(25)
        remove_button = qt.QPushButton("-", self._lines_gbox, "add_button")
        remove_button.setFixedWidth(25)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        lines_gbox_layout.addLayout(button_layout)


        self._acq_gbox = qt.QVGroupBox('Acquisition', self, 'acq_gbox')
        self._acq_widget = AcquisitionWidget(self._acq_gbox, 
                                            "acquisition_widget",
                                            layout = 'vertical',
                                            acq_params =  self._acquisition_parameters,
                                            path_template = self._path_template)


        self._acq_widget.disable_inverse_beam(True)
        

        self._data_path_gbox = qt.QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = DataPathWidgetVerticalLayout)

        self._processing_gbox = qt.QVGroupBox('Processing', self, 
                                           'processing_gbox')
        
        self._processing_widget = ProcessingWidget(self._processing_gbox,
                                                   data_model = self._processing_parameters)

        v_layout.addWidget(self._lines_gbox)
        v_layout.addWidget(self._acq_gbox)
        v_layout.addWidget(self._data_path_gbox)
        v_layout.addWidget(self._processing_gbox)

        qt.QObject.connect(add_button, qt.SIGNAL("clicked()"),
                        self.add_clicked)

        qt.QObject.connect(remove_button, qt.SIGNAL("clicked()"),
                        self.remove_clicked)

        qt.QObject.connect(self._list_box, qt.SIGNAL("selectionChanged()"),
                        self.list_box_selection_changed)

        self.connect(self._data_path_widget.data_path_widget_layout.prefix_ledit, 
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._prefix_ledit_change)

        self.connect(self._data_path_widget.data_path_widget_layout.run_number_ledit,
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)


        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)


    def init_models(self):
        CreateTaskBase.init_models(self)
        self._energy_scan_result = queue_model_objects.EnergyScanResult()
        self._processing_parameters = queue_model_objects.ProcessingParameters()
  
        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less

            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters()

            try:
                transmission = self._beamline_setup_hwobj.transmission_hwobj.getAttFactor()
                transmission = round(float(transmission), 1)
            except AttributeError:
                transmission = 0

            try:
                resolution = self._beamline_setup_hwobj.resolution_hwobj.getPosition()
                resolution = round(float(resolution), 4)
            except AttributeError:
                resolution = 0

            try:
                energy = self._beamline_setup_hwobj.energy_hwobj.getCurrentEnergy()
                energy = round(float(energy), 2)
            except AttributeError:
                energy = 0

            self._acquisition_parameters.resolution = resolution
            self._acquisition_parameters.energy = energy
            self._acquisition_parameters.transmission = transmission
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._path_template = queue_model_objects.PathTemplate()


    def add_clicked(self):
        selected_shapes = self._shape_history.selected_shapes.values()

        if len(selected_shapes) == 2:
            p1 = selected_shapes[1]
            p2 = selected_shapes[0]
            
            line = shape_history.Line(self._shape_history.get_drawing(), p1.qub_point, p2.qub_point,
                                     p1.centred_position, p2.centred_position)

            line.show()
            self._shape_history.add_shape(line)
            list_box_item = qt.QListBoxText(self._list_box, 'Line')
            self._list_item_map[list_box_item] = line


    def remove_clicked(self):
        selected_items = self.selected_items()

        if selected_items:
            for item in selected_items:
                self._list_box.removeItem(self._list_box.index(item))
                line = self._list_item_map[item]
                self._shape_history.delete_shape(line)
                del self._list_item_map[item]


    # Calback from shape_history, called when a shape is deleted
    def shape_deleted(self, shape):
        if isinstance(shape, shape_history.Point):
            items_to_remove = []

            for (list_item, line) in self._list_item_map.iteritems():
                for qub_object in shape.get_qub_objects():
                    if qub_object in line.get_qub_objects():
                        items_to_remove.append((list_item, line))

            for (list_item, line) in items_to_remove:
                self._list_box.removeItem(self._list_box.index(list_item))
                del self._list_item_map[list_item]
                self._shape_history.delete_shape(line)


    def centred_position_selection(self, positions):
        if len(positions) == 1:
            self._prev_pos = positions[0]
            
        elif len(positions) == 2:

            for pos in positions:
                if pos != self._prev_pos:
                    self._current_pos = pos
        else:
            self._prev_pos = None
            self._current_pos = None


    def list_box_selection_changed(self):
        self.show_selected_lines()


    def selected_items(self):
        selected_items = []
                
        for item_index in range(0, self._list_box.numRows()):
            if self._list_box.isSelected(item_index):
                selected_items.append(self._list_box.item(item_index))

        return selected_items
        

    def show_selected_lines(self):
        selected_items = self.selected_items()

        for list_item in self._list_item_map.keys():
            line = self._list_item_map[list_item]
            if list_item in selected_items:
                line.highlight()
            else:
                line.unhighlight()


    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)
    
        selected_lines = False
        
        if self.selected_items():
            selected_lines = True
        else:
            logging.getLogger("user_level_log").\
                info("No lines selected, please select one or more lines.")

        return base_result and selected_lines 
            

    def update_processing_parameters(self, crystal):
        self._processing_parameters.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma
        self._processing_widget.update_data_model(self._processing_parameters)


    def select_shape_with_cpos(self, start_cpos, end_cpos):
        self._shape_history._drawing_event.de_select_all()

        for shape in self._shape_history.get_shapes():
            if len(shape.get_centred_positions()) == 2:
                if shape.get_centred_positions()[0] is start_cpos and\
                       shape.get_centred_positions()[1] is end_cpos:
                    self._shape_history._drawing_event.set_selected(shape)


    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
                                                             
        if isinstance(tree_item, queue_item.SampleQueueItem) or \
               isinstance(tree_item, queue_item.DataCollectionGroupQueueItem):
            sample_data_model = self.get_sample_item(tree_item).get_model()
            self.update_processing_parameters(sample_data_model.crystals[0])
            self._acq_widget.set_energies(sample_data_model.crystals[0].energy_scan_result)

        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
            self.setDisabled(False)
            data_collection = tree_item.get_model()
            self._path_template = data_collection.acquisitions[0].path_template
            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters

            if len(data_collection.acquisitions) == 2:
                start_cpos = data_collection.acquisitions[0].acquisition_parameters.\
                             centred_position
                end_cpos = data_collection.acquisitions[1].acquisition_parameters.\
                           centred_position

                self.select_shape_with_cpos(start_cpos, end_cpos)

            self._energy_scan_result = queue_model_objects.EnergyScanResult()
            self._processing_parameters = data_collection.processing_parameters
            self._energy_scan_result = data_collection.crystal.energy_scan_result
            self._acq_widget.set_energies(self._energy_scan_result)
        else:
            self.setDisabled(True)
                  
        self._processing_widget.update_data_model(self._processing_parameters)
        self._acq_widget.update_data_model(self._acquisition_parameters,
                                           self._path_template)

    def _create_task(self,  sample):
        data_collections = []
        selected_items = self.selected_items()

        for item in selected_items:
            shape = self._list_item_map[item]
            snapshot = None

            if isinstance(shape, shape_history.Line ):
                if shape.get_qub_objects() is not None:
                    snapshot = self._shape_history.get_snapshot(shape.get_qub_objects())
                else:
                    snapshot = self._shape_history.get_snapshot([])

                # Acquisition for start position
                start_acq = queue_model_objects.Acquisition()
                start_acq.acquisition_parameters = \
                    copy.deepcopy(self._acquisition_parameters)
                start_acq.acquisition_parameters.collect_agent = \
                    queue_model_objects.COLLECTION_ORIGIN.MXCUBE
                start_acq.acquisition_parameters.\
                    centred_position = shape.start_cpos
                start_acq.path_template = copy.deepcopy(self._path_template)
                start_acq.acquisition_parameters.centred_position.\
                    snapshot_image = snapshot

                start_acq.path_template.suffix = self._session_hwobj.suffix

                # Add another acquisition for the end position
                end_acq = queue_model_objects.Acquisition()
                end_acq.acquisition_parameters = \
                    copy.deepcopy(self._acquisition_parameters)
                end_acq.acquisition_parameters.collect_agent = \
                    queue_model_objects.COLLECTION_ORIGIN.MXCUBE
                end_acq.acquisition_parameters.\
                    centred_position = shape.end_cpos
                end_acq.path_template = copy.deepcopy(self._path_template)
                end_acq.acquisition_parameters.centred_position.\
                    snapshot_image = snapshot

                end_acq.path_template.suffix = self._session_hwobj.suffix

                processing_parameters = copy.deepcopy(self._processing_parameters)
              
                dc = queue_model_objects.DataCollection([start_acq, end_acq],
                                                        sample.crystals[0],
                                                        processing_parameters)

                dc.set_name(start_acq.path_template.get_prefix())
                dc.set_number(start_acq.path_template.run_number)

                
                dc.experiment_type = queue_model_objects.EXPERIMENT_TYPE.HELICAL

                data_collections.append(dc)

        return data_collections
                   
