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
import pyqtgraph as pg

class TwoDimenisonalPlotWidget(QWidget):
    """
    Descript. :
    """
    mouseMovedSignal = pyqtSignal(float, float)
    mouseClickedSignal = pyqtSignal(float, float)
    mouseDoubleClickedSignal = pyqtSignal(float, float)
    mouseLeftSignal = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.plot_widget = pg.PlotWidget()
        self.image_view = pg.ImageView()
 
        self.plot_widget.showGrid(x=True, y=True)
        self.curves_dict = {}

        self.vlayout = QVBoxLayout(self)
        #self.vlayout.addWidget(self.plot_widget)
        self.vlayout.addWidget(self.image_view)

        #self.curve.setPen((200,200,100))
        self.setFixedSize(600, 300)

        colors = [(0, 0, 0),
                  (255, 0, 0),
                  (255, 255, 0),
                  (255, 255, 255)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 4), color=colors)
        self.image_view.setColorMap(cmap)
        #self.image_view.setAutoVisible(y=True)

        #self.image_view.sigMouseMoveEvent.connect(self.mouse_moved)
        #self.image_view.mouseDoubleClickEvent.connect(self.mouse_double_clicked)
        #self.image_view.mousePressEvent

        self.image_view.scene.sigMouseMoved.connect(self.mouse_moved)
 
    def add_curve(self, key, x_array, y_array, linestyle, label, color, marker):
        curve = self.plot_widget.plot(symbolPen='w', symbolSize=5)
        curve.setPen((200,200,100))
        self.curves_dict[key] = curve

    def plot_result(self, result, aspect=None):
        self.image_view.setImage(result)

    def update_curves(self, result):
        for key in result.keys():
            if key in self.curves_dict:
               self.curves_dict[key].setData(y=result['spots_num'], x=result['x_array'])
 
    def adjust_axes(self, result_key):
        pass 

    def clear(self): 
        pass

    def mouse_moved(self, mouse_event):
        self.mouseMovedSignal.emit(mouse_event.x(), mouse_event.y())

    def mouse_double_clicked(self, press_event, double):
        print press_event, double
