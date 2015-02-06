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

from PyQt4 import QtGui
from PyQt4 import QtCore

from numpy import arange, sin, pi

from matplotlib.backends import qt4_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from BlissFramework.Qt4_BaseComponents import BlissWidget


class TwoAxisPlotWidget(BlissWidget):
    def __init__(self, realtime_plot):
        BlissWidget.__init__(self)

        self.realtime_plot = False
        self.two_axis_figure_canvas = StaticMplCanvas(self)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.two_axis_figure_canvas)  
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    def set_real_time_plot(self, realtime_plot):
        self.realtime_plot = realtime_plot

    def clear(self):
        self.two_axis_figure_canvas.axes.cla()

    def plot_scan_curve(self, result):
        self.axes.plot(t, result)

        print "plot_scan_curve", result

    def start_new_scan(self, scan_parameters):
        print "start_new_scan", scan_parameters

    def plot_results(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
                     chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        print "plot_results: ", self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
                    chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title
     

    def plot_finished(self):
        print "plot_finished"   


class MplCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 5, height=4, dpi = 60):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class StaticMplCanvas(MplCanvas):
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)
        self.axes.set_xlabel("x label")
        self.axes.set_ylabel("y_label")
        #legend = self.axes.legend(loc='upper center', shadow=True, fontsize='x-large')



