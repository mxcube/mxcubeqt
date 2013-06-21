import queue_model_objects_v1 as queue_model_objects
import qt

from widgets.widget_utils import DataModelInputBinder
from widgets.processing_widget_vertical_layout \
    import ProcessingWidgetVerticalLayout


class ProcessingWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, data_model = None):

        qt.QWidget.__init__(self, parent, name, fl)

        if data_model is None:
            self._model = queue_model_objects.ProcessingParameters()
        else:
            self._model = data_model

        self._model_mib = DataModelInputBinder(self._model)

        h_layout = qt.QHBoxLayout(self)
        self.layout_widget = ProcessingWidgetVerticalLayout(self)
        h_layout.addWidget(self.layout_widget)
        self.layout_widget.upload_radio.setDisabled(True)
        self.layout_widget.use_code_radio.setDisabled(True)
        self.layout_widget.path_ledit.setDisabled(True)
        self.layout_widget.browse_button.setDisabled(True)

        self.layout_widget.space_group_ledit.\
            insertStrList(queue_model_objects.XTAL_SPACEGROUPS)
        
        #self._model_mib.bind_value_update('space_group',
        #                                  self.layout_widget.space_group_ledit,
        #                                  int,
        #                                  None)

        self._model_mib.bind_value_update('cell_a',
                                          self.layout_widget.a_ledit,
                                          float,
                                          None)
        
        self._model_mib.bind_value_update('cell_alpha',
                                          self.layout_widget.alpha_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_b',
                                          self.layout_widget.b_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_beta',
                                          self.layout_widget.beta_ledit,
                                          float,
                                          None)  

        self._model_mib.bind_value_update('cell_c',
                                          self.layout_widget.c_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_gamma',
                                          self.layout_widget.gamma_ledit,
                                          float,
                                          None)  
        
        self._model_mib.bind_value_update('num_residues',
                                          self.layout_widget.num_residues_ledit,
                                          float,
                                          None)

        self._model_mib.bind_value_update('process_data',
                                          self.layout_widget.use_processing,
                                          bool,
                                          None)

        self._model_mib.bind_value_update('anomalous',
                                          self.layout_widget.use_anomalous,
                                          bool,
                                          None)

        self.connect(self.layout_widget.space_group_ledit,
                     qt.SIGNAL("activated(int)"),
                     self._space_group_change)    


    def _space_group_change(self, index):
        self._model.space_group = queue_model_objects.\
                                 XTAL_SPACEGROUPS[index]


    def _set_space_group(self, space_group):
        index = 0

        if space_group in queue_model_objects.XTAL_SPACEGROUPS:
            index = queue_model_objects.XTAL_SPACEGROUPS.index(space_group)
        
        self._space_group_change(index)
        self.layout_widget.space_group_ledit.setCurrentItem(index)
        

    def update_data_model(self, model):
        self._model = model
        self._model_mib.set_model(model)
        self._set_space_group(model.space_group)
