import qt
import queue_model_objects_v1 as queue_model_objects

#from PyMca import QPeriodicTable
from PeriodicTableBrick import PeriodicTableBrick
from widgets.data_path_widget import DataPathWidget
#from SpecScanPlotBrick import SpecScanPlotBrick


class EnergyScanParametersWidget(qt.QWidget):
    def __init__(self, parent = None, name = "energy_scan_tab_widget"):
        qt.QWidget.__init__(self, parent, name)

        # Data Attributes
        self.energy_scan = queue_model_objects.EnergyScan()
        self._tree_view_item = None

        # Layout
        h_layout = qt.QHBoxLayout(self, 0, 0, "main_v_layout")
        col_one_vlayout = qt.QVBoxLayout(h_layout, 0, "row_one")

        periodic_table_gbox = qt.QHGroupBox("Available Elements", self)
        self.periodic_table =  PeriodicTableBrick(periodic_table_gbox)
            #QPeriodicTable.QPeriodicTable(periodic_table_gbox)
        self.periodic_table.setFixedHeight(341)
        self.periodic_table.setFixedWidth(650)
        #font = periodic_table.font()
        #font.setPointSize(8)
        #periodic_table.setFont(font)
        #scan_plot_gbox = qt.QHGroupBox("Scan plot", self)
        #spec_scan_plot_brick = SpecScanPlotBrick(scan_plot_gbox)
        self.data_path_widget = DataPathWidget(self)
        self.data_path_widget.data_path_widget_layout.file_name_label.setText('')
        self.data_path_widget.data_path_widget_layout.file_name_value_label.hide()

        col_one_vlayout.add(periodic_table_gbox)
        col_one_vlayout.add(self.data_path_widget)
        col_one_vlayout.addStretch(10)

        qt.QObject.connect(self.periodic_table, qt.PYSIGNAL('edgeSelected'), 
                           self.element_clicked)


        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.prefix_ledit, 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._prefix_ledit_change)


        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.run_number_ledit, 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._run_number_ledit_change)
        
        qt.QObject.connect(qt.qApp, qt.PYSIGNAL('tab_changed'),
                           self.tab_changed)

    def _prefix_ledit_change(self, new_value):
        self.energy_scan.set_name(str(new_value))
        self._tree_view_item.setText(0, self.energy_scan.get_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.energy_scan.set_number(int(new_value))
            self._tree_view_item.setText(0, self.energy_scan.get_name())
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        
        self.energy_scan = item.get_model()
        self.data_path_widget.update_data_model(self.energy_scan.path_template)
        
        self.periodic_table.periodicTable.\
            tableElementChanged(self.energy_scan.symbol)

    def element_clicked(self, symbol, energy):
        self.energy_scan.symbol = symbol
        self.energy_scan.edge = energy
