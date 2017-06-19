"""Bliss step-by-step scan plot brick"""

__author__ = 'Matias Guijarro'
__version__ = '1.0'
__category__ = 'Scans'

import logging

from qt import *
from PyMca.QtBlissGraph import QtBlissGraph
from BlissFramework.BaseComponents import BlissWidget
from bliss.common.data_manager import DataManager
from bliss.common import event

__category__ = 'Scans'

class BlissScanPlotBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSignal('newScan', ())

        self.scanObject = None
        self.xdata = []
        self.ylable = ""
        self.mylog = 0
        self.canAddPoint = True
        self.dm = DataManager()
        event.connect(self.dm, "scan_new", self.newScan)
        event.connect(self.dm, "scan_data", self.newScanPoint)

        self.addProperty('backgroundColor', 'combo', ('white', 'default'), 'white')
        self.addProperty('graphColor', 'combo', ('white', 'default'), 'white')
        self.lblTitle = QLabel(self)
        self.graphPanel = QFrame(self)
        buttonBox = QHBox(self)
        self.lblPosition = QLabel(buttonBox)
        self.graph = QtBlissGraph(self.graphPanel)
                         
        QObject.connect(self.graph, PYSIGNAL('QtBlissGraphSignal'), self.handleBlissGraphSignal)
        QObject.disconnect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
        QObject.disconnect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)
 
        self.graph.canvas().setMouseTracking(True)
        self.graph.enableLegend(False)
        self.graph.enableZoom(False)
        self.graph.setAutoLegend(False)
        self.lblPosition.setAlignment(Qt.AlignRight)
        self.lblTitle.setAlignment(Qt.AlignHCenter)
        self.lblTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lblPosition.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        QVBoxLayout(self.graphPanel)
        self.graphPanel.layout().addWidget(self.graph)

        QVBoxLayout(self)
        self.layout().addWidget(self.lblTitle)
        self.layout().addWidget(buttonBox)
        self.layout().addWidget(self.graphPanel)


    def propertyChanged(self, property, oldValue, newValue):
        if property == 'backgroundColor':
            if newValue == 'white':
                self.setPaletteBackgroundColor(Qt.white)
            elif newValue == 'default':
                self.setPaletteBackgroundColor(QWidget.paletteBackgroundColor(self))
        
        elif property == 'graphColor':
            if newValue == 'white':
                self.graph.canvas().setPaletteBackgroundColor(Qt.white)
            elif newValue == 'default':
                self.graph.canvas().setPaletteBackgroundColor(QWidget.paletteBackgroundColor(self))
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)
               
    #def newScan(self, dm, scan_id, filename, motors, npoints, counters, save_flag=True):
    def newScan(self, scan_id, filename, motors, npoints, counters, save_flag=True):
        self.emit(PYSIGNAL('newScan'), ())
        self.lblTitle.setText('<nobr><b>%s</b></nobr>' % filename)
        self.xdata = []

        self.graph.clearcurves()
        #self.graph.xlabel(scanParameters['xlabel'])
        self.graph.xlabel("Energy")
        self.ylabel = "Counts"

        ylabels = self.ylabel.split()
        self.ydatas = [[] for x in range(len(ylabels))]
        for labels,ydata in zip(ylabels,self.ydatas):
            self.graph.newcurve(labels,self.xdata,ydata)
            
        self.graph.ylabel(self.ylabel)
        if motors == 'Time':
            self.graph.setx1timescale(True)
        else:
            self.graph.setx1timescale(False)

        self.graph.replot()
        
    def newScanPoint(self, scan_id, values):
        x = values[0]
        self.xdata.append(x)
        for label,ydata,yvalue in zip(self.ylabel.split(),self.ydatas,values[1:]):
            ydata.append(float(yvalue))
            self.graph.newcurve(label,self.xdata,ydata)
        self.graph.replot()
        
    def handleBlissGraphSignal(self, signalDict):
        if signalDict['event'] == 'MouseAt':
            self.lblPosition.setText("(X: %f, Y: %f)" % (signalDict['x'], signalDict['y']))

