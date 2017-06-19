import os
import qtui
import qt
import queue_model_objects_v1 as queue_model_objects
import queue_model_enumerables_v1 as queue_model_enumerables

from widgets.widget_utils import DataModelInputBinder

class ProcessingWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0, data_model = None):

        qt.QWidget.__init__(self, parent, name, fl)

        if data_model is None:
            self._model = queue_model_objects.ProcessingParameters()
        else:
            self._model = data_model

        self._model_mib = DataModelInputBinder(self._model)

        h_layout = qt.QHBoxLayout(self)
        widget = self.acq_widget_layout = qtui.QWidgetFactory.\
                 create(os.path.join(os.path.dirname(__file__),
                                     'ui_files/processing_widget_vertical_layout.ui'))
        
        widget.reparent(self, qt.QPoint(0,0))
        self.layout_widget = widget
        
        h_layout.addWidget(self.layout_widget)
       
        self.layout_widget.child('space_group_ledit').\
            insertStrList(queue_model_enumerables.XTAL_SPACEGROUPS)
        
        self._model_mib.bind_value_update('cell_a',
                                          self.layout_widget.child('a_ledit'),
                                          float,
                                          None)
        
        self._model_mib.bind_value_update('cell_alpha',
                                          self.layout_widget.child('alpha_ledit'),
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_b',
                                          self.layout_widget.child('b_ledit'),
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_beta',
                                          self.layout_widget.child('beta_ledit'),
                                          float,
                                          None)  

        self._model_mib.bind_value_update('cell_c',
                                          self.layout_widget.child('c_ledit'),
                                          float,
                                          None)

        self._model_mib.bind_value_update('cell_gamma',
                                          self.layout_widget.child('gamma_ledit'),
                                          float,
                                          None)  
        
        self._model_mib.bind_value_update('num_residues',
                                          self.layout_widget.child('num_residues_ledit'),
                                          float,
                                          None)

        self.connect(self.layout_widget.child('space_group_ledit'),
                     qt.SIGNAL("activated(int)"),
                     self._space_group_change)    

    def _space_group_change(self, index):
        self._model.space_group = queue_model_enumerables.\
            XTAL_SPACEGROUPS[index]

    def _set_space_group(self, space_group):
        index = 0

        if space_group in queue_model_enumerables.XTAL_SPACEGROUPS:
            index = queue_model_enumerables.XTAL_SPACEGROUPS.index(space_group)
        
        self._space_group_change(index)
        self.layout_widget.child('space_group_ledit').setCurrentItem(index)

    def update_data_model(self, model):
        self._model = model
        self._model_mib.set_model(model)
        self._set_space_group(model.space_group)
