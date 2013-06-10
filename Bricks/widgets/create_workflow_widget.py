import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys


from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget
from widgets.data_path_widget_vertical_layout import\
    DataPathWidgetVerticalLayout


class CreateWorkflowWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'Workflow')

        # Data attributes
        self._path_template = queue_model_objects.PathTemplate()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 5, "main_v_layout")
        self._data_path_gbox = qt.QVGroupBox('Data location', self,
                                             'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                                data_model = self._path_template,
                                                layout = DataPathWidgetVerticalLayout)

        self._data_path_widget.data_path_widget_layout.file_name_label.setText('')
        self._data_path_widget.data_path_widget_layout.file_name_value_label.hide()


        v_layout.addWidget(self._data_path_gbox)
        v_layout.addStretch()


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, dcg, sample):
        tasks = []

        path_template = copy.deepcopy(self._path_template)
        wf = queue_model_objects.Workflow()
        wf.path_tempalte = path_template
        wf.set_name(path_template.get_prefix())
        
        tasks.append(wf)

        return tasks
