#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore
from PyQt4 import QtGui

import queue_model_objects_v1 as queue_model_objects

from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_periodic_table_widget import PeriodicTableWidget
#from widgets.Qt4_matplot_widget import TwoAxisPlotWidget
from widgets.Qt4_pymca_plot_widget import PymcaPlotWidget
from widgets.Qt4_snapshot_widget import SnapshotWidget

from BlissFramework.Utils import Qt4_widget_colors


__category__ = 'Tasks'


class EnergyScanParametersWidget(QtGui.QWidget):
    def __init__(self, parent = None, name = "energy_scan_tab_widget"):
        QtGui.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.energy_scan_model = queue_model_objects.EnergyScan()
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        _top_widget = QtGui.QWidget(self) 
        _parameters_widget = QtGui.QWidget(_top_widget)  
        self.periodic_table_widget =  PeriodicTableWidget(_parameters_widget)
        self.data_path_widget = DataPathWidget(_parameters_widget)
        self.data_path_widget.data_path_layout.file_name_label.setText('')
        self.data_path_widget.data_path_layout.file_name_value_label.hide()
        self.snapshot_widget = SnapshotWidget(self)

        self.scan_plot_widget = PymcaPlotWidget(self, True)
        self.result_plot_widget = PymcaPlotWidget(self, False)
        #self.scan_plot_widget = TwoAxisPlotWidget(self, True)
        #self.result_plot_widget = TwoAxisPlotWidget(self, False)
 
        # Layout -------------------------------------------------------------
        _parameters_widget_layout = QtGui.QVBoxLayout()
        _parameters_widget_layout.addWidget(self.periodic_table_widget)
        _parameters_widget_layout.addWidget(self.data_path_widget)
        _parameters_widget_layout.addStretch(0)
        _parameters_widget_layout.setSpacing(2)
        _parameters_widget_layout.setContentsMargins(0, 0, 0, 0)
        _parameters_widget.setLayout(_parameters_widget_layout)

        _top_widget_hlayout = QtGui.QHBoxLayout(self)
        _top_widget_hlayout.addWidget(_parameters_widget)
        _top_widget_hlayout.addWidget(self.snapshot_widget)
        _top_widget_hlayout.addStretch(0)
        _top_widget_hlayout.setSpacing(2)
        _top_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        _top_widget.setLayout(_top_widget_hlayout) 

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_top_widget)
        _main_vlayout.addWidget(self.scan_plot_widget)
        _main_vlayout.addWidget(self.result_plot_widget)
        _main_vlayout.setSpacing(5)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)
        _main_vlayout.addStretch(0)

        self.setLayout(_main_vlayout)
      
        # SizePolicies --------------------------------------------------------
        self.scan_plot_widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                            QtGui.QSizePolicy.Expanding)
        self.result_plot_widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                              QtGui.QSizePolicy.Expanding)

        # Qt signal/slot connections ------------------------------------------
        #qt.QObject.connect(self.periodic_table_widget, qt.PYSIGNAL('edgeSelected'), 
        #                   self.element_clicked)

        self.data_path_widget.data_path_layout.prefix_ledit.\
             textChanged.connect(self._prefix_ledit_change)

        self.data_path_widget.data_path_layout.run_number_ledit.\
             textChanged.connect(self._run_number_ledit_change)
        
        # Other ---------------------------------------------------------------

    def _prefix_ledit_change(self, new_value):
        self.energy_scan_model.set_name(str(new_value))
        self._tree_view_item.setText(0, self.energy_scan_model.get_name())

    def _run_number_ledit_change(self, new_value):
        if str(new_value).isdigit():
            self.energy_scan_model.set_number(int(new_value))
            self._tree_view_item.setText(0, self.energy_scan_model.get_name())
        
    def tab_changed(self):
        if self._tree_view_item:
            self.populate_widget(self._tree_view_item)

    def populate_widget(self, item):
        self._tree_view_item = item
        self.energy_scan_model = item.get_model()
        executed = self.energy_scan_model.is_executed()

        self.data_path_widget.setEnabled(not executed)
        self.periodic_table_widget.setEnabled(not executed)
        self.scan_plot_widget.setEnabled(not executed)
        self.result_plot_widget.setEnabled(not executed)
 
        width = self.data_path_widget.width() + \
                self.snapshot_widget.width()
        self.scan_plot_widget.setFixedWidth(width)
        self.result_plot_widget.setFixedWidth(width)

        if executed:
            title = "Element: %s, Edge: %s" % (\
                    self.energy_scan_model.element_symbol,
                    self.energy_scan_model.edge)

            result = self.energy_scan_model.get_scan_result()
            self.scan_plot_widget.plot_energy_scan_curve(result.data,
                                                         title)

            self.result_plot_widget.plot_energy_scan_results(\
              result.pk, result.fppPeak, result.fpPeak, result.ip, 
              result.fppInfl, result.fpInfl, result.rm, 
              result.chooch_graph_x, result.chooch_graph_y1, 
              result.chooch_graph_y2, result.title)
        else:
            self.scan_plot_widget.clear()
            self.result_plot_widget.clear()

        self.data_path_widget.update_data_model(self.energy_scan_model.path_template)
        self.periodic_table_widget.set_current_element_edge(\
             self.energy_scan_model.element_symbol,
             self.energy_scan_model.edge)

        image = self.energy_scan_model.centred_position.snapshot_image
        self.snapshot_widget.display_snapshot(image, width=400)

    def element_clicked(self, symbol, energy):
        self.energy_scan_model.element_symbol = symbol
        self.energy_scan_model.edge = energy

    def set_enegy_scan_hwobj(self, energy_scan_hwobj):
        self.energy_scan_hwobj = energy_scan_hwobj
        if self.energy_scan_hwobj:
            self.energy_scan_hwobj.connect("energyScanStarted", self.energy_scan_started)
            self.energy_scan_hwobj.connect("scanNewPoint", self.energy_scan_new_point) 
            self.energy_scan_hwobj.connect("choochFinished", self.chooch_finished)

    def energy_scan_started(self, scan_info):
        self.scan_plot_widget.start_new_scan(scan_info)
        self.data_path_widget.setEnabled(False)
        self.periodic_table_widget.setEnabled(False)

    def energy_scan_new_point(self, x, y):
        self.scan_plot_widget.add_new_plot_value(x, y)

    def chooch_finished(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
              chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        self.result_plot_widget.plot_energy_scan_results(pk, fppPeak, fpPeak, 
              ip, fppInfl, fpInfl, rm, chooch_graph_x, chooch_graph_y1, 
              chooch_graph_y2, title)
        self.scan_plot_widget.plot_finished()
