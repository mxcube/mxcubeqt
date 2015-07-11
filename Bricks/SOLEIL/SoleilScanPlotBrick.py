"""Spec scan plot brick"""

__author__ = 'Matias Guijarro'
__version__ = '1.0'
__category__ = 'Scans'

import logging

from qt import *
from PyMca.QtBlissGraph import QtBlissGraph
from BlissFramework.BaseComponents import BlissWidget

__category__ = 'Scans'

class SoleilScanPlotBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSlot('newScan', ())
	
        self.defineSlot('newScanPoint',())

        self.scanObject = None
        self.xdata = []
        self.ydata = []

        self.isConnected = None
        self.canAddPoint = True

        self.addProperty('specVersion', 'string', '')
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
        if property == 'specVersion':
            if self.scanObject is not None:
                self.safeDisconnect()
                
            self.scanObject = None
            if self.scanObject is not None:
                self.safeConnect()

        elif property == 'backgroundColor':
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
               

    def newScan(self, scanParameters):
        logging.info('newScan scanParameters %s' % str(scanParameters) )
        self.lblTitle.setText('<nobr><b>%s</b></nobr>' % scanParameters['title'])
        self.graph.xlabel(scanParameters['xlabel'])
        self.graph.ylabel(scanParameters['ylabel'])
        self.graph.setx1timescale(False)
        self.xdata = []
        self.ydata = []
        self.graph.newcurve('scan', self.xdata, self.ydata)
        self.graph.replot() 

    def newScanPoint(self, x, y):
        logging.info('newScanPoint x %s, y %s' % (x,y))
        self.xdata.append(x)
        self.ydata.append(y)
        self.graph.newcurve('scan', self.xdata, self.ydata, curveinfo='bo-')
        self.graph.replot() 
        
    def handleBlissGraphSignal(self, signalDict):
        if signalDict['event'] == 'MouseAt':
            self.lblPosition.setText("(X: %f, Y: %f)" % (signalDict['x'], signalDict['y']))


    def safeConnect(self):
        if not self.isConnected:
            self.connect(self.scanObject, PYSIGNAL('newScanPoint'), self.newScan)
            self.connect(self.scanObject, PYSIGNAL('newPoint'), self.newScanPoint)
            self.isConnected=True

    def safeDisconnect(self):
        if self.isConnected:
            self.disconnect(self.scanObject, PYSIGNAL('newScan'), self.newScan)
            self.disconnect(self.scanObject, PYSIGNAL('newScanPoint'), self.newScanPoint)
            self.isConnected = False


