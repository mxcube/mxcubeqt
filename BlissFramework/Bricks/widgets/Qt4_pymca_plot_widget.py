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
PYMCA_EXISTS = False


if not qt_variant == 'PyQt5':
    try:
        from PyMca.QtBlissGraph import QtBlissGraph as Graph
        PYMCA_EXISTS = True
    except:
        pass

if not PYMCA_EXISTS:
    from Qt4_matplot_widget import TwoAxisPlotWidget as Graph

from BlissFramework.Utils import Qt4_widget_colors


class PymcaPlotWidget(QWidget):
    """
    Descript. :
    """

    def __init__(self, parent, realtime_plot = False):
        """
        Descript. :
        """
        QWidget.__init__(self, parent)

        self.axis_x_array = []
        self.axis_y_array = []

        self.realtime_plot = realtime_plot
   
        self.pymca_graph = Graph(self)
        self.pymca_graph.showGrid()
        self.info_label = QLabel("", self)  
        self.info_label.setAlignment(Qt.AlignRight)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.pymca_graph)  
        _main_vlayout.addWidget(self.info_label)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)

        if qt_variant == 'PyQt5':
             pass
        else:
             QObject.connect(self.pymca_graph,
                             SIGNAL("QtBlissGraphSignal"),
                             self.handle_graph_signal)

        Qt4_widget_colors.set_widget_color(self, Qt4_widget_colors.WHITE)         

    def clear(self):
        """
        Descript. :
        """
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
        """
        Descript. :
        """
        self.axis_x_array = []
        self.axis_y_array = []
        self.pymca_graph.clearcurves()
        self.pymca_graph.xlabel(scan_info['xlabel'])
        self.ylabel = scan_info['ylabel']
        self.pymca_graph.ylabel(self.ylabel)
        self.pymca_graph.setx1timescale(False)
        self.pymca_graph.replot()
        self.pymca_graph.setTitle(scan_info['title'])

    def plot_energy_scan_results(self, pk, fppPeak, fpPeak, ip, fppInfl, 
            fpInfl, rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
        """
        """
        self.pymca_graph.clearcurves()
        self.pymca_graph.setTitle(title)
        self.pymca_graph.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.pymca_graph.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.pymca_graph.replot()
        self.pymca_graph.setx1axislimits(min(chooch_graph_x),
                                         max(chooch_graph_x))
 
    def plot_finished(self):
        """
        Descript. :
        """
        if self.axis_x_array:
            self.pymca_graph.setx1axislimits(min(self.axis_x_array),
                                             max(self.axis_x_array))
            self.pymca_graph.replot()

    def add_new_plot_value(self, x, y):
        """
        Descript. :
        """
        if self.realtime_plot:
            self.axis_x_array.append(x / 1000.0)
            self.axis_y_array.append(y / 1000.0)
            self.pymca_graph.newcurve("Energy", self.axis_x_array, self.axis_y_array)
            self.pymca_graph.setx1axislimits(min(self.axis_x_array),
                                             max(self.axis_x_array))
            #self.pymca_graph.replot()
            

    def handle_graph_signal(self, signal_info):
        """
        """
        if signal_info['event'] == 'MouseAt':
            self.info_label.setText("(X: %0.2f, Y: %0.2f)" % \
                 (signal_info['x'], signal_info['y']))
