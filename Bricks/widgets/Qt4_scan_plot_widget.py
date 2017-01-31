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

from PyMca.QtBlissGraph import QtBlissGraph


class ScanPlotWidget(QtGui.QWidget):

    def __init__(self, parent = None, name = "scan_plot_widget"):
        QtGui.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        self.xdata = []
        self.ylabel = ""

        self.isRealTimePlot = None
        self.isConnected = None
        self.isScanning = None

        self.lblTitle = QtGui.QLabel(self)
        #self.graphPanel = qt.QFrame(self)
        #buttonBox = qt.QHBox(self)
        self.lblPosition = QtGui.QLabel(self)
        self.graph = QtBlissGraph(self)

        QtCore.QObject.connect(self.graph, QtCore.SIGNAL('QtBlissGraphSignal'), self.handleBlissGraphSignal)
        QtCore.QObject.disconnect(self.graph, QtCore.SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
        QtCore.QObject.disconnect(self.graph, QtCore.SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)

        self.graph.canvas().setMouseTracking(True)
        self.graph.enableLegend(False)
        self.graph.enableZoom(False)
        #self.graph.setAutoLegend(False)
        """self.lblPosition.setAlignment(qt.Qt.AlignRight)
        self.lblTitle.setAlignment(qt.Qt.AlignHCenter)
        self.lblTitle.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self.lblPosition.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        buttonBox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        
        qt.QVBoxLayout(self.graphPanel)
        self.graphPanel.layout().addWidget(self.graph)

        qt.QVBoxLayout(self)
        self.layout().addWidget(self.lblTitle)
        self.layout().addWidget(buttonBox)
        self.layout().addWidget(self.graphPanel)
        self.setPaletteBackgroundColor(qt.Qt.white)"""
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.lblTitle)
        _main_vlayout.addWidget(self.lblPosition)
        _main_vlayout.addWidget(self.graph)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def setRealTimePlot(self, isRealTime):
        self.isRealTimePlot = isRealTime 

    def start_new_scan(self, scanParameters):
        self.graph.clearcurves()
        self.isScanning = True
        self.lblTitle.setText('<nobr><b>%s</b></nobr>' % scanParameters['title'])
        self.xdata = []
        self.graph.xlabel(scanParameters['xlabel'])
        self.ylabel = scanParameters['ylabel']
        ylabels = self.ylabel.split()
        self.ydatas = [[] for x in range(len(ylabels))]
        for labels,ydata in zip(ylabels,self.ydatas):
            self.graph.newcurve(labels,self.xdata,ydata)
        self.graph.ylabel(self.ylabel)
        self.graph.setx1timescale(False)
        self.graph.replot()
        self.graph.setTitle("Energy scan started. Waiting values...")
        
    def add_new_plot_value(self, x, y):
        self.xdata.append(x)
        for label,ydata,yvalue in zip(self.ylabel.split(),self.ydatas,str(y).split()) :
            ydata.append(float(yvalue))
            self.graph.newcurve(label,self.xdata,ydata)
            self.graph.setTitle("Energy scan in progress. Please wait...")
        self.graph.replot()
        
    def handleBlissGraphSignal(self, signalDict):
        if signalDict['event'] == 'MouseAt' and self.isScanning:
            self.lblPosition.setText("(X: %0.2f, Y: %0.2f)" % (signalDict['x'], signalDict['y']))

    def plot_results(self, pk, fppPeak, fpPeak, ip, fppInfl, fpInfl,
                        rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title):
	self.graph.clearcurves()	
        self.graph.setTitle(title)
        self.graph.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.graph.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.graph.replot()
	self.isScanning = False

    def plot_scan_curve(self, scan_data):
        self.graph.clearcurves()
        self.graph.setTitle("Energy scan finished")
        self.lblTitle.setText("")
        xdata = [scan_data[el][0] for el in range(len(scan_data))]
        ydata = [scan_data[el][1] for el in range(len(scan_data))]
        self.graph.newcurve("energy", xdata, ydata)
        self.graph.replot()

    def clear(self):
        self.graph.clearcurves()
        #self.graph.setTitle("")
        self.lblTitle.setText("")
        self.lblPosition.setText("")

    def scan_finished(self):
        self.graph.setTitle("Energy scan finished") 
