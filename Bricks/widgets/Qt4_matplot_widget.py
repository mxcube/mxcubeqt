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
from matplotlib.figure import Figure

#from matplotlib.backends import qt4_compat
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

try:
   from matplotlib.backends.backend_qt4agg \
   import NavigationToolbar2QTAgg as NavigationToolbar
except:
   from matplotlib.backends.backend_qt4agg \
   import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt


from BlissFramework.Utils import Qt4_widget_colors


class TwoAxisPlotWidget(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, realtime_plot = False):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, parent)

        self._realtime_plot = realtime_plot
        self._two_axis_figure_canvas = MplCanvas(self)
        self._two_axis_figure_canvas.set_real_time(realtime_plot)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._two_axis_figure_canvas)  
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    def clear(self):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.clear()

    def plot_energy_scan_curve(self, energy_scan_result):
        """
        Descript. : result is a list of lists containing energy and counts
                    Results are converted to two list describing
                    x and y axes
        """
        self._two_axis_figure_canvas.clear()
        #check the order of axis
        x_result = [item[1] for item in energy_scan_result]
        y_result = [item[0] for item in energy_scan_result] 
        self._two_axis_figure_canvas.add_curve(x_result, y_result, 'energy')

    def start_new_scan(self):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.clear()
        self._two_axis_figure_canvas.set_axes_labels("energy", "counts")
        self._two_axis_figure_canvas.set_title("Scan started")

    def plot_energy_scan_results(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, \
                     chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        self._two_axis_figure_canvas.add_curve(\
             chooch_graph_y1, chooch_graph_x, 'spline', 'blue')
        self._two_axis_figure_canvas.add_curve(\
             chooch_graph_y2, chooch_graph_x, 'fp', 'red') 
        self._two_axis_figure_canvas.set_title(title)
     
    def plot_finished(self):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.set_title("Scan finished")

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
        self.mouse_position = [0, 0]

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.curves = []
        self._axis_x_array = np.empty(0)
        self._axis_y_array = np.empty(0)

    def set_real_time(self, real_time):
        self.real_time = real_time
        #clear all axes after plot is called
        self.axes.hold(not real_time)

    def clear(self):
        self.curves = []
        self.axes.cla()
        self.axes.grid(True)

    def add_curve(self, y_axis_array, x_axis_array=None, curve_name=None, color='blue'):
        if x_axis_array is None:
            self.curves.append(self.axes.plot(y_axis_array, 
                 label = curve_name, linewidth = 2, color = color))
        else:
            self.curves.append(self.axes.plot(x_axis_array, y_axis_array, 
                 label = curve_name, linewidth = 2, color = color))
        self.draw()

    def append_new_point(self, x, y):
        self._axis_x_array = np.append(self._axis_x_array, x)
        self._axis_y_array = np.append(self._axis_y_array, y)
        self.axes.plot(self._axis_x_array, self._axis_y_array, linewidth=2)
        self.set_title("Scan in progress. Please wait...")

    def set_axes_labels(self, x_label, y_label):
        self.axes.set_xlabel(x_label)
        self.axes.xaxis.set_label_coords(1.05, -0.025)
        self.axes.set_ylabel(y_label)

    def set_title(self, title):
        self.axes.set_title(title, fontsize = 14)
        self.axes.grid(True)
        self.draw()

    def get_mouse_coord(self):
        return self.mouse_position


class PolarScaterWidget(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent = None):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, parent)

        self._polar_scater = PolarScater(self)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self._polar_scater)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    def draw_multiwedge_scater(self, sw_list):
        self._polar_scater.draw_scater(sw_list)

class PolarScater(FigureCanvas):
    """
    Descript. : Class to draw plots on canvas
    """

    def __init__(self, parent = None, width = 5, height=4, dpi = 60):
        """
        Descript. :
        """

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
        #self.axes.hold(False)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def draw_scater(self, sw_list):
        """
        Descript. : draws data collection item on the scatter
                    subwedge is represented as list:
                    collection_id, sw_id, first_image, num_images, 
                    osc_start, osc_full_range
        """
        self.axes.clear()
        col_count = 0
        for sw_index, sw in enumerate(sw_list):
            bars = self.axes.bar(np.radians(sw[4]), 1, 
                width = np.radians(sw[5]), bottom = sw[0],
                color = Qt4_widget_colors.TASK_GROUP[sw[0]])
            x_mid = bars[0].get_bbox().xmin + (bars[0].get_bbox().xmax - \
                    bars[0].get_bbox().xmin) / 2.0 
            y_mid = bars[0].get_bbox().ymin + (bars[0].get_bbox().ymax - \
                    bars[0].get_bbox().ymin) / 2.0
            self.axes.text(x_mid, y_mid, "%d (%d:%d)" % \
                           (sw_index + 1, sw[0] + 1, sw[1] + 1),
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold')
            if sw[0] > col_count:
                col_count = sw[0] 
        self.axes.set_yticks(np.arange(1, col_count + 2))
        self.fig.canvas.draw_idle()

class TwoDimenisonalPlotWidget(QtGui.QWidget):
    """
    Descript. :
    """
    mouseClickedSignal = QtCore.pyqtSignal(float, float)
    mouseDoubleClickedSignal = QtCore.pyqtSignal(float, float)

    def __init__(self, parent=None):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, parent)

        self.mpl_canvas = MplCanvas(self)
        self.ntb = NavigationToolbar(self.mpl_canvas, self)

        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.mpl_canvas)
        _main_vlayout.addWidget(self.ntb)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        self.mpl_canvas.axes.grid(True)
        self.mpl_canvas.fig.canvas.mpl_connect(\
             "button_press_event", self.mouse_clicked)

        self.setFixedSize(1000, 700)

    def mouse_clicked(self, mouse_event):
        dbl_click = False
        if hasattr(mouse_event, "dblclick"):
            dbl_click = mouse_event.dblclick
        if dbl_click:
            self.mouseDoubleClickedSignal.emit(mouse_event.xdata,
                                               mouse_event.ydata)
        else:
            self.mouseClickedSignal.emit(mouse_event.xdata,
                                         mouse_event.ydata)

    def plot_result(self, result, last_result=None):
        im = self.mpl_canvas.axes.imshow(result, 
                    interpolation='none',  aspect='auto',
                    extent=[0, result.shape[1], 0, result.shape[0]])
        im.set_cmap('hot')
        if result.max() > 0:
            self.add_divider()
            plt.colorbar(im, cax = self.cax)
            #self.mpl_canvas.draw()
            self.mpl_canvas.fig.canvas.draw_idle()

            mgr = plt.get_current_fig_manager()
            #mgr.full_screen_toggle()
            mgr.window.move(10, 10)

    def get_current_coord(self):
        return self.mpl_canvas.get_mouse_coord()

    def set_x_axis_limits(self, limits):
        self.mpl_canvas.axes.set_xlim(limits)

    def set_y_axis_limits(self, limits):
        self.mpl_canvas.axes.set_ylim(limits)

    def add_divider(self):
        self.divider = make_axes_locatable(self.mpl_canvas.axes)
        self.cax = self.divider.append_axes("right", size=0.3, pad=0.05)
        self.cax.tick_params(axis='x', labelsize=8)
        self.cax.tick_params(axis='y', labelsize=8)
