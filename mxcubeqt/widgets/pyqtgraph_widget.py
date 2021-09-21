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

import numpy as np
import pyqtgraph as pg

from mxcubeqt.utils import qt_import

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class PlotWidget(qt_import.QWidget):

    mouseMovedSignal = qt_import.pyqtSignal(float, float)
    mouseClickedSignal = qt_import.pyqtSignal(float, float)
    mouseDoubleClickedSignal = qt_import.pyqtSignal(float, float)
    mouseLeftSignal = qt_import.pyqtSignal()

    def __init__(self, parent=None):
        qt_import.QWidget.__init__(self, parent)

        self.curves_dict = {}
        self.visible_curve = None

        self.view_box = CustomViewBox()
        self.one_dim_plot = pg.PlotWidget(viewBox=self.view_box)
        self.two_dim_plot = pg.ImageView()

        self.one_dim_plot.showGrid(x=True, y=True)
        self.two_dim_plot.ui.histogram.hide()
        self.two_dim_plot.ui.roiBtn.hide()
        self.two_dim_plot.ui.menuBtn.hide()
        self.two_dim_plot.setFixedWidth(400)

        hlayout = qt_import.QHBoxLayout(self)
        hlayout.addWidget(self.one_dim_plot)
        hlayout.addWidget(self.two_dim_plot)

        colors = [(0, 0, 0),
                  (255, 0, 0),
                  (255, 255, 0),
                  (255, 255, 255)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 4), color=colors)
        self.two_dim_plot.setColorMap(cmap)

        self.one_dim_plot.scene().sigMouseMoved.connect(self.one_dim_plot_mouse_moved)
        self.two_dim_plot.scene.sigMouseMoved.connect(self.two_dim_plot_mouse_moved)

    def set_plot_type(self, plot_type):
        self.one_dim_plot.setVisible(plot_type == "1D")
        self.two_dim_plot.setVisible(plot_type == "2D")

    def add_curve(self, key, y_array, x_array, color):
        self.curves_dict[key] = self.one_dim_plot.plot(
            y=y_array,
            x=x_array,
            symbolPen='w',
            symbolBrush=color,
            symbolSize=3
        )
        self.visible_curve = key

    def add_energy_scan_plot(self, scan_info):
        self.one_dim_plot.setTitle(scan_info["title"])
        pen = pg.mkPen('w', width=2)
        plot = self.one_dim_plot.plot(pen=pen)
        plot.setDownsampling(method="peak")
        plot.setClipToView(True)
        self.curves_dict["energyscan"] = plot
    
    def add_energy_scan_plot_point(self, x, y):
        if self.curves_dict["energyscan"].xData is None:
            x_data = [x]
            y_data = [y]
        else:
            x_data = np.append(self.curves_dict["energyscan"].xData, x)
            y_data = np.append(self.curves_dict["energyscan"].yData, y)
        self.curves_dict["energyscan"].setData(y=y_data, x=x_data)

    def plot_energy_scan_results(self, data, title):
        pen = pg.mkPen('w', width=2)
        #x_data = [item[0] for item in data]
        #y_data = [item[1] for item in data]
        self.one_dim_plot.plot(data, pen=pen)

    def plot_chooch_results(
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
        pen = pg.mkPen('r', width=3)
        self.one_dim_plot.plot(y=chooch_graph_y1, x=chooch_graph_x, pen=pen)
        pen = pg.mkPen('b', width=3)
        self.one_dim_plot.plot(y=chooch_graph_y2, x=chooch_graph_x, pen=pen)

    def update_curves(self, result):
        for key in result.keys():
            if key in self.curves_dict:
                self.curves_dict[key].setData(y=result[key]) #, x=result['x_array'])

    def plot_result(self, result, aspect=None):
        self.two_dim_plot.setImage(result)

    def autoscale_axes(self):
        #self.one_dim_plot.enableAutoRange(self.view_box.XYAxes, True)
        self.view_box.autoRange(padding=0.02)
        
        self.view_box.setYRange(min=0, max=max(self.curves_dict[self.visible_curve].yData))

    def clear(self):
        self.one_dim_plot.clear()
        self.two_dim_plot.clear()
        self.curves_dict = {}

    def hide_all_curves(self):
        for key in self.curves_dict.keys():
            self.curves_dict[key].hide()
        self.visible_curve = None

    def show_curve(self, curve_key):
        for key in self.curves_dict.keys():
            if key == curve_key:
                self.curves_dict[key].show()
                self.visible_curve = key
                return

    def one_dim_plot_mouse_moved(self, mouse_event):
        mouse_point = self.one_dim_plot.plotItem.vb.mapSceneToView(mouse_event)
        self.mouseMovedSignal.emit(mouse_point.x(), mouse_point.y())

    def two_dim_plot_mouse_moved(self, mouse_event):
        mouse_point = self.two_dim_plot.imageItem.getViewBox().mapSceneToView(mouse_event)
        self.mouseMovedSignal.emit(mouse_point.x(), mouse_point.y())

    def mouse_double_clicked(self, press_event, double):
        pass

    def set_yticks(self, ticks):
        y_axis = self.one_dim_plot.getAxis("left")
        y_axis.setTicks([ticks])

    def set_x_axis_limits(self, limits):
        self.one_dim_plot.setRange(xRange=limits)

    def set_y_axis_limits(self, limits):
        self.one_dim_plot.setRange(yRange=limits)

class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    #def mouseClickEvent(self, ev):
    #    if ev.button() == qt_import.Qt.RightButton:
    #        self.autoRange()

    def mouseDragEvent(self, ev):
        if ev.button() == qt_import.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)
