import qt
import queue_model

#from PyMca import QPeriodicTable
from PeriodicTableBrick import PeriodicTableBrick
from widgets.data_path_widget import DataPathWidget
from SpecScanPlotBrick import SpecScanPlotBrick


class EnergyScanParametersWidget(qt.QWidget):

    def __init__(self, parent = None, name = "energy_scan_tab_widget"):
        qt.QWidget.__init__(self, parent, name)

        # Data Attributes
        self.energy_scan = queue_model.EnergyScan()

        # Layout
        h_layout = qt.QHBoxLayout(self, 0, 0, "main_v_layout")
        col_one_vlayout = qt.QVBoxLayout(h_layout, 0, "row_one")
        col_two_vlayout = qt.QVBoxLayout(h_layout, 0, "row_two")

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
        

    def populate_widget(self, energy_scan):
        self.energy_scan = energy_scan
        self.data_path_widget.update_data_model(energy_scan.path_template)
        
        new_path = queue_model.QueueModelFactory().\
            get_context().build_image_path(energy_scan.path_template)

        self.periodic_table.periodicTable.\
            tableElementChanged(energy_scan.symbol)
                
        self.data_path_widget.set_data_path(new_path)


    def element_clicked(self, symbol, energy):
        self.energy_scan.symbol = symbol
        self.energy_scan.edge = energy
