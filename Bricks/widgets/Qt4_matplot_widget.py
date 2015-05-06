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

import numpy as np

from matplotlib.backends import qt4_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from BlissFramework.Qt4_BaseComponents import BlissWidget


class TwoAxisPlotWidget(BlissWidget):
    """
    Descript. :
    """

    def __init__(self, realtime_plot = False):
        """
        Descript. :
        """
        BlissWidget.__init__(self)

        self._two_axis_figure_canvas = MplCanvas(self)
        self._two_axis_figure_canvas.set_real_time(realtime_plot)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._two_axis_figure_canvas)  
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    def set_real_time_plot(self, realtime_plot):
        """
        Descript. :
        """
        self._realtime_plot = realtime_plot

    def clear(self):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.clear()

    def plot_scan_curve(self, result):
        self._two_axis_figure_canvas.clear()
        self._two_axis_figure_canvas.add_curve(result, 'energy')

    def start_new_scan(self, scan_parameters):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.clear()
        self._two_axis_figure_canvas.set_axes_labels(scan_parameters.get('xlabel', ''),
                                                     scan_parameters.get('ylabel', ''))

    def plot_results(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
                     chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        self._two_axis_figure_canvas.add_curve(chooch_graph_y1, chooch_graph_x, 'spline')
        self._two_axis_figure_canvas.add_curve(chooch_graph_y2, chooch_graph_x, 'fp') 
     
    def plot_finished(self):
        """
        Descript. :
        """
        print "plot_finished"   

    def add_new_plot_value(self, x, y):
        """
        Descript. :
        """
        if self._realtime_plot:
            self._two_axis_figure_canvas.append_new_point(x, y)

class MplCanvas(FigureCanvas):
    """
    Descript. : Class to draw plots on canvas
    """

    def __init__(self, parent = None, width = 5, height=4, dpi = 60):
        """
        Descript. :
        """

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._axis_x_array = np.empty(0)
        self._axis_y_array = np.empty(0)

    def set_real_time(self, real_time):
        self.real_time = real_time

    def clear(self):
        self.axes.cla()

    def add_curve(self, y_axis_array, x_axis_array=None, curve_name=None):
        if x_axis_array is None:
            self.axes.plot(y_axis_array, label=curve_name)
        else:
            self.axes.plot(x_axis_array, y_axis_array, label=curve_name)

    def append_new_point(self, x, y):
        self._axis_x_array = np.append(self._axis_x_array, x)
        self._axis_y_array = np.append(self._axis_y_array, y)
        self.axes.plot(self._axis_x_array, self._axis_y_array)
        self.draw()

    def set_axes_labels(self, x_label, y_label):
        self.axes.set_xlabel(x_label)
        self.axes.xaxis.set_label_coords(1.05, -0.025)
        self.axes.set_ylabel(y_label)

    def set_title(self, title):
        self.title(title)
