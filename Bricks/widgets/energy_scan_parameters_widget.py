import os
import qt
import qtui
import queue_model_objects_v1 as queue_model_objects

from PeriodicTableBrick import PeriodicTableBrick
from widgets.data_path_widget import DataPathWidget
from widgets.scan_plot_widget import ScanPlotWidget


class EnergyScanParametersWidget(qt.QWidget):
    def __init__(self, parent = None, name = "energy_scan_tab_widget"):
        qt.QWidget.__init__(self, parent, name)

        # Data Attributes
        self.energy_scan_hwobj = None
        self.energy_scan = queue_model_objects.EnergyScan()
        self._tree_view_item = None

        # Layout
        h_layout = qt.QHBoxLayout(self, 0, 0, "main_v_layout")
        col_one_vlayout = qt.QVBoxLayout(h_layout, 0, "row_one")

        hbox = qt.QHBox(self)
        periodic_table_gbox = qt.QHGroupBox("Available Elements", hbox)
        self.periodic_table =  PeriodicTableBrick(periodic_table_gbox)
        self.periodic_table.setFixedHeight(341)
        self.periodic_table.setFixedWidth(650)

        widget_ui = os.path.join(os.path.dirname(__file__),
                                 'ui_files/snapshot_widget_layout.ui')
        widget = qtui.QWidgetFactory.create(widget_ui)
        widget.reparent(hbox, qt.QPoint(0, 0))
        self.position_widget = widget

        self.data_path_widget = DataPathWidget(self)

        self.scan_plot = ScanPlotWidget(self)
        self.scan_plot.setRealTimePlot(True)
        self.results_plot = ScanPlotWidget(self)
        self.results_plot.setRealTimePlot(False)

        col_one_vlayout.add(hbox)
        col_one_vlayout.add(self.data_path_widget)
        col_one_vlayout.add(self.scan_plot)
        col_one_vlayout.add(self.results_plot)

        qt.QObject.connect(self.periodic_table, qt.PYSIGNAL('edgeSelected'), 
                           self.element_clicked)

        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.child('prefix_ledit'), 
                           qt.SIGNAL("textChanged(const QString &)"), 
                           self._prefix_ledit_change)


        qt.QObject.connect(self.data_path_widget.data_path_widget_layout.child('run_number_ledit'), 
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
 
        # If scan is alreadu executed, then results are ploted
        # If scan still in progress then display realtime data
        executed = self.energy_scan.is_executed()
        
        self.data_path_widget.setEnabled(not executed)
        self.periodic_table.setEnabled(not executed)
        self.scan_plot.setEnabled(not executed)
        self.results_plot.setEnabled(not executed)

        if executed:
            result = self.energy_scan.get_scan_result()
            self.scan_plot.plotScanCurve(result.data)
            self.results_plot.plotResults(result.pk, result.fppPeak,
              result.fpPeak, result.ip, result.fppInfl, result.fpInfl,
              result.rm, result.chooch_graph_x, result.chooch_graph_y1,
              result.chooch_graph_y2, result.title)
        else:
            self.scan_plot.clear()
            self.results_plot.clear()

        self.data_path_widget.update_data_model(self.energy_scan.path_template)
        self.periodic_table.periodicTable.\
             tableElementChanged(self.energy_scan.element_symbol, self.energy_scan.edge)

        # Displays sample screenshot
        image = self.energy_scan.centred_position.snapshot_image
        if image is not None:
            try:
               image = image.scale(427, 320)
               self.position_widget.child("svideo").setPixmap(qt.QPixmap(image))
            except:
               pass

    def element_clicked(self, symbol, energy):
        self.energy_scan.element_symbol = symbol
        self.energy_scan.edge = energy

    def set_enegy_scan_hwobj(self, energy_scan_hwobj):
        self.energy_scan_hwobj = energy_scan_hwobj
        if self.energy_scan_hwobj:
            self.energy_scan_hwobj.connect("scanStart", self.scanStarted)
            self.energy_scan_hwobj.connect("scanNewPoint", self.scanNewPoint)
            self.energy_scan_hwobj.connect("choochFinished", self.choochFinished)

    def scanStarted(self, scan_parameters):
        self.scan_plot.newScanStarted(scan_parameters)
        self.data_path_widget.setEnabled(False)
        self.periodic_table.setEnabled(False)

    def scanNewPoint(self, x, y):
        self.scan_plot.newScanPoint(x, y)

    def choochFinished(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
              chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        self.results_plot.plotResults(pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm,\
              chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title)
        self.scan_plot.scanFinished()
