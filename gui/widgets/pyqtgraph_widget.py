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

from gui.utils import QtImport

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


#pg.setConfigOption('background', 'w')


class PlotWidget(QtImport.QWidget):

    mouseMovedSignal = QtImport.pyqtSignal(float, float)
    mouseClickedSignal = QtImport.pyqtSignal(float, float)
    mouseDoubleClickedSignal = QtImport.pyqtSignal(float, float)
    mouseLeftSignal = QtImport.pyqtSignal()

    def __init__(self, parent=None):
        QtImport.QWidget.__init__(self, parent)

        self.view_box = CustomViewBox()
        self.plot_widget = pg.PlotWidget(viewBox=self.view_box)
        self.image_view = pg.ImageView()

        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        self.plot_widget.showGrid(x=True, y=True)
        self.curves_dict = {}

        self.vlayout = QtImport.QVBoxLayout(self)
        self.vlayout.addWidget(self.plot_widget)
        self.vlayout.addWidget(self.image_view)

        # self.curve.setPen((200,200,100))
        self.setFixedSize(600, 300)

        colors = [(0, 0, 0),
                  (255, 0, 0),
                  (255, 255, 0),
                  (255, 255, 255)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 4), color=colors)
        self.image_view.setColorMap(cmap)

        self.plot_widget.scene().sigMouseMoved.connect(self.plot_widget_mouse_moved)
        self.image_view.scene.sigMouseMoved.connect(self.image_view_mouse_moved)
        #self.setMouseMode(self.RectMode)

    def set_plot_type(self, plot_type):
        self.plot_widget.setVisible(plot_type == "1D")
        self.image_view.setVisible(plot_type == "2D")

    def add_curve(self, key, y_array, x_array, linestyle, label, color, marker):
        curve = self.plot_widget.plot(y=y_array, x=x_array, pen=None, symbolPen='w', symbolBrush=color, symbolSize=5)
        #curve.setPen((200, 200, 100))
        self.curves_dict[key] = curve

    def update_curves(self, result):
        for key in result.keys():
            if key in self.curves_dict:
                self.curves_dict[key].setData(y=result[key]) #, x=result['x_array'])

    def plot_result(self, result, aspect=None):
        self.image_view.setImage(result)

    def update_plot(self, result, aspect=None):
        self.image_view.setImage(result)

    def autoscale_axes(self):
        #self.plot_widget.enableAutoRange(self.view_box.XYAxes, True)
        self.view_box.autoRange()

    def clear(self):
        self.plot_widget.clear()
        self.image_view.clear()
        self.curves_dict = {}

    def hide_all_curves(self):
        for key in self.curves_dict.keys():
            self.curves_dict[key].hide()

    def show_curve(self, curve_key):
        for key in self.curves_dict.keys():
            if key == curve_key:
                self.curves_dict[key].show()

    def plot_widget_mouse_moved(self, mouse_event):
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(mouse_event)
        self.mouseMovedSignal.emit(mouse_point.x(), mouse_point.y())

    def image_view_mouse_moved(self, mouse_event):
        mouse_point = self.image_view.imageItem.getViewBox().mapSceneToView(mouse_event)
        self.mouseMovedSignal.emit(mouse_point.x(), mouse_point.y())

    def mouse_double_clicked(self, press_event, double):
        pass

    def set_yticks(self, ticks):
        pass

    def set_ytick_labels(self, labels):
        pass

    def set_x_axis_limits(self, limits):
        self.plot_widget.setRange(xRange=limits)

    def set_y_axis_limits(self, limits):
        self.plot_widget.setRange(yRange=limits)

class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    #def mouseClickEvent(self, ev):
    #    if ev.button() == QtImport.Qt.RightButton:
    #        self.autoRange()

    def mouseDragEvent(self, ev):
        if ev.button() == QtImport.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)
