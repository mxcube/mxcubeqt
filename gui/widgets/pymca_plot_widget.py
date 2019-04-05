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

PYMCA_EXISTS = False

try: 
   from PyMca.QtBlissGraph import QtBlissGraph as Plot
   PYMCA_EXISTS = True
except BaseException:
   from gui.widgets.matplot_widget import TwoAxisPlotWidget as Plot

from gui.utils import Colors, QtImport


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class PymcaPlotWidget(QtImport.QWidget):

    def __init__(self, parent, realtime_plot=False):

        QtImport.QWidget.__init__(self, parent)

        self.axis_x_array = []
        self.axis_y_array = []

        self.realtime_plot = realtime_plot

        self.pymca_graph = Plot(self)
        self.pymca_graph.showGrid()
        self.info_label = QtImport.QLabel("", self)
        self.info_label.setAlignment(QtImport.Qt.AlignRight)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.pymca_graph)
        _main_vlayout.addWidget(self.info_label)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        self.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding
        )

        if PYMCA_EXISTS:
            QtImport.QObject.connect(
                self.pymca_graph,
                QtImport.SIGNAL("QtBlissGraphSignal"),
                self.handle_graph_signal,
            )

        Colors.set_widget_color(self, Colors.WHITE)

    def clear(self):
        self.pymca_graph.clearcurves()
        self.pymca_graph.setTitle("")
        self.info_label.setText("")

    def plot_energy_scan_curve(self, scan_result, scan_title):
        """Results are converted to two list describing
           x and y axes
        """
        x_data = [item[0] for item in scan_result]
        y_data = [item[1] for item in scan_result]
        self.pymca_graph.newcurve("Energy", x_data, y_data)
        self.pymca_graph.replot()
        self.pymca_graph.setTitle(scan_title)
        self.pymca_graph.setx1axislimits(min(x_data), max(x_data))

    def start_new_scan(self, scan_info):
        self.axis_x_array = []
        self.axis_y_array = []
        self.pymca_graph.clearcurves()
        self.pymca_graph.xlabel(scan_info["xlabel"])
        self.ylabel = scan_info["ylabel"]
        self.pymca_graph.ylabel(self.ylabel)
        self.pymca_graph.setx1timescale(False)
        self.pymca_graph.replot()
        self.pymca_graph.setTitle(scan_info["title"])

    def plot_energy_scan_results(
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
        self.pymca_graph.clearcurves()
        self.pymca_graph.setTitle(title)
        self.pymca_graph.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.pymca_graph.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.pymca_graph.replot()
        self.pymca_graph.setx1axislimits(min(chooch_graph_x), max(chooch_graph_x))

    def plot_finished(self):
        if self.axis_x_array:
            self.pymca_graph.setx1axislimits(
                min(self.axis_x_array), max(self.axis_x_array)
            )
            self.pymca_graph.replot()

    def add_new_plot_value(self, x, y):
        if self.realtime_plot:
            self.axis_x_array.append(x / 1000.0)
            self.axis_y_array.append(y / 1000.0)
            self.pymca_graph.newcurve("Energy", self.axis_x_array, self.axis_y_array)
            self.pymca_graph.setx1axislimits(
                min(self.axis_x_array), max(self.axis_x_array)
            )
            # self.pymca_graph.replot()

    def handle_graph_signal(self, signal_info):
        if signal_info["event"] == "MouseAt":
            self.info_label.setText(
                "(X: %0.2f, Y: %0.2f)" % (signal_info["x"], signal_info["y"])
            )
