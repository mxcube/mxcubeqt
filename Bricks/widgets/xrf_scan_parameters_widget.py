import qt
import queue_model_objects_v1 as queue_model_objects

from widgets.data_path_widget import DataPathWidget


class XRFScanParametersWidget(qt.QWidget):
    def __init__(self, parent = None, name = "xrf_scan_tab_widget"):
        qt.QWidget.__init__(self, parent, name)

        # Data Attributes
        self.xrf_scan = queue_model_objects.XRFScan()
        self._tree_view_item = None

        # Layout
        h_layout = qt.QHBoxLayout(self, 0, 0, "main_v_layout")
        col_one_vlayout = qt.QVBoxLayout(h_layout, 0, "row_one")

        self.data_path_widget = DataPathWidget(self)
        self.data_path_widget.data_path_widget_layout.child('file_name_label').setText('')
        self.data_path_widget.data_path_widget_layout.child('file_name_value_label').hide()

	parameters_hor_gbox = qt.QHGroupBox("Parameters", self)
	#parameters_hor_box = qt.QHBoxLayout(self, 0, "parameters_box")

	self.count_time_label = qt.QLabel("Count", parameters_hor_gbox)
        #arameters_hor_box.addWidget(self.count_time_label)

	self.count_time_ledit = qt.QLineEdit(parameters_hor_gbox,"count_time_ledit")
	self.count_time_ledit.setFixedWidth(100)
	#arameters_hor_box.addWidget(self.count_time_ledit)

	#parameters_hor_box.add(parameters_hor_gbox)
	#parameters_hor_box.addStretch()

        col_one_vlayout.add(self.data_path_widget)
	col_one_vlayout.add(parameters_hor_gbox)
        col_one_vlayout.addStretch()

        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.child('prefix_ledit'), 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._prefix_ledit_change)

        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.child('run_number_ledit'), 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._run_number_ledit_change)
        
        qt.QObject.connect(qt.qApp, qt.PYSIGNAL('tab_changed'),
                           self.tab_changed)

    def _prefix_ledit_change(self, new_value):
        self.xrf_scan.set_name(str(new_value))
        self._tree_view_item.setText(0, self.xrf_scan.get_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.xrf_scan.set_number(int(new_value))
            self._tree_view_item.setText(0, self.xrf_scan.get_name())
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        self.xrf_scan = item.get_model()

        if self.xrf_scan.is_executed():
            self.data_path_widget.setEnabled(False)
	    self.count_time_ledit.setEnabled(False)
        else:
            self.data_path_widget.setEnabled(True)
            self.count_time_ledit.setEnabled(True)	
            self.data_path_widget.update_data_model(self.xrf_scan.path_template)
