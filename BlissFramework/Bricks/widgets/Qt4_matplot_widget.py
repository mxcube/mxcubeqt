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

from QtImport import *

import numpy as np
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

if qt_variant == 'PyQt5':
    from matplotlib.backends.backend_qt5agg \
    import FigureCanvasQTAgg as FigureCanvas
    try:
        from matplotlib.backends.backend_qt5agg \
        import NavigationToolbar2QTAgg as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt5agg \
        import NavigationToolbar2QT as NavigationToolbar 
else:
    from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
    try:
        from matplotlib.backends.backend_qt4agg \
        import NavigationToolbar2QTAgg as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt4agg \
        import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt

from BlissFramework.Utils import Qt4_widget_colors


class TwoAxisPlotWidget(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, realtime_plot=False):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self._realtime_plot = realtime_plot
        self._two_axis_figure_canvas = MplCanvas(self)
        self._two_axis_figure_canvas.set_real_time(realtime_plot)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self._two_axis_figure_canvas)  
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)

        self.clearcurves = self.clear 

    def setTitle(self, title):
        self._two_axis_figure_canvas.set_title(title)

    def clear(self):
        """
        Descript. :
        """
        self._two_axis_figure_canvas.clear()
        self._two_axis_figure_canvas.set_title("")

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

    def add_new_plot_value(self, y, x=None):
        """
        Descript. :
        """
        if self._realtime_plot:
            self._two_axis_figure_canvas.append_new_point(y, x)

    def set_tight_layout(self):
        self._two_axis_figure_canvas.axes.xaxis.set_visible(False)
        #self._two_axis_figure_canvas.fig.tight_layout()

    def set_max_plot_point(self, max_points):
        self._two_axis_figure_canvas.set_max_plot_points(max_points)

    def showGrid(self):
        pass

    def newcurve(self, label, x_array, y_array):
        self._two_axis_figure_canvas.add_curve(y_array, x_array, label=label)

    def setx1axislimits(self, x_min, x_max):
        self._two_axis_figure_canvas.axes.set_xlim((x_min, x_max))

    def xlabel(self, label):
        self._two_axis_figure_canvas.axes.axes.set_xlabel(label)

    def ylabel(self, label):
        self._two_axis_figure_canvas.axes.axes.set_ylabel(label)

    def setx1timescale(self, state):
        pass

    def replot(self):
        self._two_axis_figure_canvas.axes.relim()
        self._two_axis_figure_canvas.axes.autoscale_view()
        self._two_axis_figure_canvas.fig.canvas.draw()
        self._two_axis_figure_canvas.fig.canvas.flush_events()

    def setdata(self, x, y):
        self.newcurve("XRF spectrum", x, y)

class MplCanvas(FigureCanvas):
    """
    Descript. : Class to draw plots on canvas
    """

    def __init__(self, parent = None, width=5, height=4, dpi=60):
        """
        Descript. :
        """
        self.mouse_position = [0, 0]
        self.max_plot_points = None

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.single_curve = None

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.curves = []
        self._axis_x_array = np.empty(0)
        self._axis_y_array = np.empty(0)
        self._axis_x_limits = [None, None]
        self._axis_y_limits = [None, None]

    def set_real_time(self, real_time):
        self.real_time = real_time
        #clear all axes after plot is called
        #self.axes.hold(not real_time)
        self.axes.clear()

    def set_max_plot_points(self, max_points):
        self.max_plot_points = max_points

    def clear(self):
        self.curves = []
        self.single_curve = None
        self.axes.cla()
        self.axes.grid(True)

    def add_curve(self, y_axis_array, x_axis_array=None, label=None,
           linestyle="-", color='blue', marker='None'):
        if x_axis_array is None:
            self.curves.append(self.axes.plot(y_axis_array, 
                 label=label, linewidth=2, linestyle=linestyle,
                 color=color, marker=marker))
        else:
            self.curves.append(self.axes.plot(x_axis_array, y_axis_array, 
                 label=label, linewidth=2, linestyle=linestyle,
                 color=color, marker=marker))
        self.draw()

    def append_new_point(self, y, x=None):
        self._axis_y_array = np.append(self._axis_y_array, y)
        if x:
             self._axis_x_array = np.append(self._axis_x_array, x)
        else:
             self._axis_x_array = np.arange(len(self._axis_y_array)) 

        if self.max_plot_points:
            if self._axis_y_array.size > self.max_plot_points:
                self._axis_y_array = np.delete(self._axis_y_array, 0)
                self._axis_x_array = np.delete(self._axis_x_array, 0)

        if self.single_curve is None:
            self.single_curve, = self.axes.plot(self._axis_y_array,
                                                linewidth=2,
                                                marker='s')
        else:  
            self.axes.fill(self._axis_y_array, 'r', linewidth=2)

        self._axis_y_limits[1]= self._axis_y_array.max() + self._axis_y_array.max() * 0.05
        self.axes.set_ylim(self._axis_y_limits) 
        self.single_curve.set_xdata(self._axis_x_array)
        self.single_curve.set_ydata(self._axis_y_array)
        self.axes.relim()
        self.axes.autoscale_view()
        #We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.axes.grid(True)
       
        #TODO move y lims as propery 
        self.axes.set_ylim((0, self._axis_y_array.max() + \
                               self._axis_y_array.max() * 0.05))
        #self.draw()
        #self.set_title("Scan in progress. Please wait...")

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


class PolarScaterWidget(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent = None):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self._polar_scater = PolarScater(self)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self._polar_scater)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)

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
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
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
                width=np.radians(sw[5]), bottom = sw[0],
                color=sw[-1],
                alpha=0.3)
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

class TwoDimenisonalPlotWidget(QWidget):
    """
    Descript. :
    """
    mouseMovedSignal = pyqtSignal(float, float)
    mouseClickedSignal = pyqtSignal(float, float)
    mouseDoubleClickedSignal = pyqtSignal(float, float)
    mouseLeftSignal = pyqtSignal()

    def __init__(self, parent=None):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self.im = None
        self.mpl_canvas = MplCanvas(self)
        self.ntb = NavigationToolbar(self.mpl_canvas, self)
        self.selection_xrange = None
        self.selection_span = None
        self.mouse_clicked = None

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.mpl_canvas)
        _main_vlayout.addWidget(self.ntb)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)

        #self.mpl_canvas.axes.grid(True)
        self.mpl_canvas.axes.grid(color='r')
        self.mpl_canvas.fig.canvas.mpl_connect(\
             "button_press_event", self.button_pressed)
        self.mpl_canvas.fig.canvas.mpl_connect(\
             "button_release_event", self.mouse_released)
        self.mpl_canvas.fig.canvas.mpl_connect(\
             "motion_notify_event", self.motion_notify_event)
        #self.setFixedSize(1000, 700)

    def button_pressed(self, mouse_event):
        dbl_click = False
        if hasattr(mouse_event, "dblclick"):
            dbl_click = mouse_event.dblclick
        if mouse_event.xdata and mouse_event.ydata:
            if dbl_click:
                self.mouseDoubleClickedSignal.emit(mouse_event.xdata,
                                                   mouse_event.ydata)
            else:
                self.mouse_clicked = True
                self.mouseClickedSignal.emit(mouse_event.xdata,
                                             mouse_event.ydata)

    def mouse_released(self, mouse_event):
        self.mouse_clicked = False

    def motion_notify_event(self, mouse_event):
        QApplication.restoreOverrideCursor()

        if mouse_event.xdata and mouse_event.ydata:
            self.mouseMovedSignal.emit(mouse_event.xdata,
                                       mouse_event.ydata)
        else:
            self.mouseLeftSignal.emit()

        if self.selection_xrange and mouse_event.xdata:
            do_update = False
            (x_start, x_end) = self.mpl_canvas.axes.get_xlim()
            delta = abs((x_end - x_start) / 50.0)
            if abs(self.selection_xrange[0] - mouse_event.xdata) < delta:
                QApplication.setOverrideCursor(\
                    QCursor(Qt.SizeHorCursor))
                if self.mouse_clicked: 
                    self.selection_xrange[0] = mouse_event.xdata
                    do_update = True
            elif abs(self.selection_xrange[1] - mouse_event.xdata) < delta:
                QApplication.setOverrideCursor(\
                    QCursor(Qt.SizeHorCursor))
                if self.mouse_clicked:
                    self.selection_xrange[1] = mouse_event.xdata 
                    do_update = True

            if do_update:
                self.selection_span.set_xy([[self.selection_xrange[0], 0],
                                            [self.selection_xrange[0], 1],
                                            [self.selection_xrange[1], 1],
                                            [self.selection_xrange[1], 0],
                                            [self.selection_xrange[0], 0]])
                self.mpl_canvas.fig.canvas.draw()
                self.mpl_canvas.fig.canvas.flush_events()

    def plot_result(self, result, aspect=None):
        if not aspect:
            aspect = 'auto'

        if self.im is None:
            self.im = self.mpl_canvas.axes.imshow(result, 
                      interpolation='none',  aspect='auto',
                      extent=[0, result.shape[1], 0, result.shape[0]])
            self.im.set_cmap('hot')
        else:
            self.im.set_data(result)

        self.im.autoscale()
        self.mpl_canvas.fig.canvas.draw()
        self.mpl_canvas.fig.canvas.flush_events()

        #if result.max() > 0:
        #    self.add_divider()
        #    plt.colorbar(im, cax = self.cax)

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

    def clear(self): 
        self.im = None
        self.selection_xrange = None
        self.selection_span = None
        self.mpl_canvas.clear()

    def add_curve(self, y_axis_array, x_axis_array=None, label=None,
            linestyle='-', color='blue', marker=None):
        self.mpl_canvas.add_curve(y_axis_array,
                                  x_axis_array=None,
                                  label=None,
                                  linestyle=linestyle,
                                  color=color,
                                  marker=marker)
        self.set_x_axis_limits((x_axis_array.min() - 1,
                                x_axis_array.max() + 1))

    def enable_selection_range(self):
        (x_start, x_end) = self.mpl_canvas.axes.get_xlim()
        offset = abs((x_end - x_start) / 10.0)
        self.selection_xrange = [x_start + offset, x_end - offset]

        self.selection_span = self.mpl_canvas.axes.axvspan(\
             self.selection_xrange[0], self.selection_xrange[1],
             facecolor='g', alpha=0.3)
        self.mpl_canvas.fig.canvas.draw()
        self.mpl_canvas.fig.canvas.flush_events()

    def enable_legend(self):
        self.mpl_canvas.axes.legend()
        self.mpl_canvas.fig.canvas.draw()
        self.mpl_canvas.fig.canvas.flush_events()
