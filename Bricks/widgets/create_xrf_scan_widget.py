import qt
import logging
import copy
import queue_item
import queue_model_objects_v1 as queue_model_objects
import sys

from create_task_base import CreateTaskBase
from widgets.data_path_widget import DataPathWidget


class CreateXRFScanWidget(CreateTaskBase):
    def __init__(self, parent = None, name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, fl, 'XRF-scan')

	self.count_time = None

        # Data attributes
        self.init_models()

        #Layout
        v_layout = qt.QVBoxLayout(self, 2, 6, "main_v_layout")
        
        self._data_path_gbox = qt.QVGroupBox('Data location', self, 'data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox, 
                                               data_model = self._path_template,
                                               layout = 'vertical')

	parameters_hor_gbox = qt.QHGroupBox('Parameters', self)
	#self._parameters_hor_box = qt.QHBoxLayout(v_layout, 0, "parameters_hor_box")

	self.count_time_label = qt.QLabel("Count time (in seconds):", parameters_hor_gbox)
        #self._parameters_hor_box.addWidget(self.count_time_label)

	self.count_time_ledit = qt.QLineEdit("1", parameters_hor_gbox,"count_time_ledit")
	#self.count_time_ledit.setMinimumSize(qt.QSize(50,0))
        #self.count_time_ledit.setMaximumSize(qt.QSize(50,32767))


	v_layout.addWidget(self._data_path_gbox)
	v_layout.addWidget(parameters_hor_gbox)
        v_layout.addStretch()

        self.connect(self._data_path_widget.data_path_widget_layout.child('run_number_ledit'),
                     qt.SIGNAL("textChanged(const QString &)"), 
                     self._run_number_ledit_change)
        
        self.connect(self._data_path_widget,
                     qt.PYSIGNAL("path_template_changed"),
                     self.handle_path_conflict)

    def init_models(self):
        CreateTaskBase.init_models(self)
        self.enery_scan = queue_model_objects.XRFScan()
        self._path_template.start_num = 1
        self._path_template.num_files = 1
        self._path_template.suffix = 'raw'

    def single_item_selection(self, tree_item):
        CreateTaskBase.single_item_selection(self, tree_item)
        escan_model = tree_item.get_model()

        if isinstance(tree_item, queue_item.XRFScanQueueItem):
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)    

            if escan_model.get_path_template():
                self._path_template = escan_model.get_path_template()

            self._data_path_widget.update_data_model(self._path_template)
        elif not(isinstance(tree_item, queue_item.SampleQueueItem) or \
                     isinstance(tree_item, queue_item.DataCollectionGroupQueueItem)):
            self.setDisabled(True)


    def approve_creation(self):
        base_result = CreateTaskBase.approve_creation(self)

	self.count_time = None

	try:
	   self.count_time = float(str(self.count_time_ledit.text()))
	except:
	   logging.getLogger("user_level_log").\
                info("Incorrect count time value.")

        return base_result and self.count_time


    # Called by the owning widget (task_toolbox_widget) to create
    # a collection. When a data collection group is selected.
    def _create_task(self, sample, shape):
        data_collections = []

	if self.count_time is not None:
            path_template = copy.deepcopy(self._path_template)
            if '<sample_name>' in path_template.directory:
                name = sample.get_name().replace(':', '-')
                path_template.directory = path_template.directory.\
                                          replace('<sample_name>', name)

                path_template.process_directory = path_template.process_directory.\
                                                  replace('<sample_name>', name)
                
            if '<acronym>-<name>' in path_template.base_prefix:
                path_template.base_prefix = self.get_default_prefix(sample)
                path_template.run_numer = self._beamline_setup_hwobj.queue_model_hwobj.\
                                          get_next_run_number(path_template)

        xrf_scan = queue_model_objects.XRFScan(sample, path_template)
        xrf_scan.set_name(path_template.get_prefix())
        xrf_scan.set_number(path_template.run_number)
	xrf_scan.count_time = self.count_time

        data_collections.append(xrf_scan)

        return data_collections


if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    widget = CreateXRFScanWidget()
    app.setMainWidget(widget)
    widget.show()
    app.exec_loop()
