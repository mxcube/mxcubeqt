#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.utils import qt_import
from mxcubeqt.widgets.data_path_widget import DataPathWidget
from mxcubeqt.widgets.periodic_table_widget import PeriodicTableWidget
from mxcubeqt.widgets.pyqtgraph_widget import PlotWidget
from mxcubeqt.widgets.snapshot_widget import SnapshotWidget

from mxcubecore.model import queue_model_objects
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class EnergyScanParametersWidget(qt_import.QWidget):
    def __init__(self, parent=None, name="energy_scan_tab_widget"):
        qt_import.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Internal variables --------------------------------------------------
        self.energy_scan_model = queue_model_objects.EnergyScan()
        self._tree_view_item = None

        # Graphic elements ----------------------------------------------------
        self.periodic_table_widget = PeriodicTableWidget(self)
        self.data_path_widget = DataPathWidget(self)
        self.data_path_widget.data_path_layout.file_name_label.setText("")
        self.data_path_widget.data_path_layout.file_name_value_label.hide()
        self.snapshot_widget = SnapshotWidget(self)

        self.scan_online_plot_widget = PlotWidget(self)
        self.scan_online_plot_widget.set_plot_type("1D")
        self.scan_result_plot_widget = PlotWidget(self)
        self.scan_result_plot_widget.set_plot_type("1D")

        # Layout -------------------------------------------------------------
        _main_gridlayout = qt_import.QGridLayout(self)
        _main_gridlayout.addWidget(self.periodic_table_widget, 0, 0)
        _main_gridlayout.addWidget(self.snapshot_widget, 0, 1)
        _main_gridlayout.addWidget(self.data_path_widget, 1, 0, 1, 2)
        _main_gridlayout.addWidget(self.scan_online_plot_widget, 2, 0, 1, 2)
        _main_gridlayout.addWidget(self.scan_result_plot_widget, 3, 0, 1, 2)
        _main_gridlayout.setSpacing(5)
        _main_gridlayout.setContentsMargins(2, 2, 2, 2)
        _main_gridlayout.setColumnStretch(2, 1)

        # SizePolicies --------------------------------------------------------
        self.periodic_table_widget.setFixedSize(600, 400)
        #self.scan_online_plot_widget.setSizePolicy(
        #    qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Fixed
        #)
        #self.scan_result_plot_widget.setSizePolicy(
        #    qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Fixed
        #)
        #self.scan_online_plot_widget.setFixedHeight(300)
        #self.scan_result_plot_widget.setFixedHeight(300)

        # Qt signal/slot connections ------------------------------------------
        # qt.QObject.connect(self.periodic_table_widget, qt.PYSIGNAL('edgeSelected'),
        #                   self.element_clicked)

        self.data_path_widget.data_path_layout.prefix_ledit.textChanged.connect(
            self._prefix_ledit_change
        )

        self.data_path_widget.data_path_layout.run_number_ledit.textChanged.connect(
            self._run_number_ledit_change
        )

        # Other ---------------------------------------------------------------
        self.data_path_widget.data_path_layout.compression_cbox.setVisible(False)

        if HWR.beamline.energy_scan is not None:
            HWR.beamline.energy_scan.connect(
                "energyScanStarted", self.energy_scan_started
            )
            HWR.beamline.energy_scan.connect("scanNewPoint", self.energy_scan_new_point)
            HWR.beamline.energy_scan.connect("choochFinished", self.chooch_finished)

        self.scan_online_plot_widget.one_dim_plot.setLabel('left', "Counts")
        self.scan_online_plot_widget.one_dim_plot.setLabel('bottom', "Energy", "keV")
        self.scan_result_plot_widget.one_dim_plot.setLabel('bottom', "Energy", "keV")

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
        is_running = self.energy_scan_model.is_running()

        self.data_path_widget.setDisabled(executed or is_running)
        self.periodic_table_widget.setDisabled(executed or is_running)
        # self.scan_online_plot_widget.setEnabled()
        # self.scan_online_plot_widget.setEnabled(not executed)
        # self.chooch_plot_widget.setEnabled(not executed)

        #width = self.data_path_widget.width() + self.snapshot_widget.width()
        #self.scan_online_plot_widget.setFixedWidth(width)
        #self.scan_result_plot_widget.setFixedWidth(width)
        #self.chooch_plot_widget.setFixedWidth(width)
        title = "Element: %s, Edge: %s" % (
            self.energy_scan_model.element_symbol,
            self.energy_scan_model.edge,
        )

        if executed:
            self.scan_online_plot_widget.clear()
            self.scan_online_plot_widget.clear()
            result = self.energy_scan_model.get_scan_result()
            self.scan_online_plot_widget.plot_energy_scan_results(result.data, title)
            self.scan_result_plot_widget.plot_chooch_results(
                result.pk,
                result.fppPeak,
                result.fpPeak,
                result.ip,
                result.fppInfl,
                result.fpInfl,
                result.rm,
                result.chooch_graph_x,
                result.chooch_graph_y1,
                result.chooch_graph_y2,
                result.title,
            )
        
        self.data_path_widget.update_data_model(
            self.energy_scan_model.path_template
        )
        self.periodic_table_widget.set_current_element_edge(
            self.energy_scan_model.element_symbol,
            self.energy_scan_model.edge
        )

        image = self.energy_scan_model.centred_position.snapshot_image
        self.snapshot_widget.display_snapshot(image, width=500)

    def element_clicked(self, symbol, energy):
        self.energy_scan_model.element_symbol = symbol
        self.energy_scan_model.edge = energy

    def energy_scan_started(self, scan_info):
        self.scan_online_plot_widget.clear()
        self.scan_result_plot_widget.clear()
        #self.scan_online_plot_widget.start_new_scan(scan_info)
        self.scan_online_plot_widget.add_energy_scan_plot(scan_info)
        #self.scan_online_plot_widget.one_dim_plot.setTitle(scan_info["title"])
        #self.scan_online_plot_widget.add_curve("energyscan")
        self.data_path_widget.setEnabled(False)
        self.periodic_table_widget.setEnabled(False)

    def energy_scan_new_point(self, x, y):
        self.scan_online_plot_widget.add_energy_scan_plot_point(x, y)

    def chooch_finished(
        self,
        pk,
        fppPeak,
        fpPeak,
        ip,
        fppInfl,
        fpInfl,
        rm,
        chooch_graph_x,
        chooch_graph_y1,
        chooch_graph_y2,
        title,
    ):
        self.scan_result_plot_widget.plot_chooch_results(
            pk,
            fppPeak,
            fpPeak,
            ip,
            fppInfl,
            fpInfl,
            rm,
            chooch_graph_x,
            chooch_graph_y1,
            chooch_graph_y2,
            title,
        )
