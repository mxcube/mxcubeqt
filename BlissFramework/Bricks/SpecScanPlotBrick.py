"""Spec scan plot brick"""

__author__ = 'Matias Guijarro'
__version__ = '1.0'
__category__ = 'Scans'

import logging

from qt import *
from PyMca.QtBlissGraph import QtBlissGraph
from BlissFramework.BaseComponents import BlissWidget
try:
  from SpecClient_gevent import SpecScan
except ImportError:
  from SpecClient import SpecScan

__category__ = 'Scans'

## class QSpecScan(QObject, SpecScan.SpecScanA):
##     def __init__(self, specVersion):
##         QObject.__init__(self)
##         SpecScan.SpecScanA.__init__(self, specVersion)
    

##     def newScan(self, scanParameters):
##         self.emit(PYSIGNAL('newScan'), (scanParameters, ))


##     def newScanPoint(self, i, x, y):
##         self.emit(PYSIGNAL('newPoint'), (x, y, ))


class SpecScanPlotBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSignal('newScan', ())

        self.scanObject = None
        self.xdata = []
        self.ydata = []

        self.isConnected = None
        #self.canAddPoint = None
        self.canAddPoint = True

        self.addProperty('specVersion', 'string', '')
        self.addProperty('backgroundColor', 'combo', ('white', 'default'), 'white')
        self.addProperty('graphColor', 'combo', ('white', 'default'), 'white')
        self.lblTitle = QLabel(self)
        self.graphPanel = QFrame(self)
        buttonBox = QHBox(self)
        #self.cmdZoomIn = QToolButton(buttonBox)
        #self.cmdZoomOut = QToolButton(buttonBox)
        self.lblPosition = QLabel(buttonBox)
        self.graph = QtBlissGraph(self.graphPanel)
                         
        QObject.connect(self.graph, PYSIGNAL('QtBlissGraphSignal'), self.handleBlissGraphSignal)
        QObject.disconnect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
        QObject.disconnect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)
        #QObject.connect(self.cmdZoomIn, SIGNAL('clicked()'), self.cmdZoomInClicked)
        #QObject.connect(self.cmdZoomOut, SIGNAL('clicked()'), self.cmdZoomOutClicked)

        #self.cmdZoomIn.setIconSet(QIconSet(Icons.load("zoomin")))
        #self.cmdZoomOut.setIconSet(QIconSet(Icons.load("zoomout")))
        #self.cmdZoomIn.setToggleButton(True)
        #self.cmdZoomOut.setToggleButton(True)
        #self.cmdZoomIn.setUsesTextLabel(False)
        #self.cmdZoomOut.setUsesTextLabel(False)
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

            self.scanObject = SpecScan.SpecScanA(newValue, callbacks={"newScan":self.newScan, "newPoint":self.newScanPoint})
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
        #self.canAddPoint = True
        self.emit(PYSIGNAL('newScan'), ())
        self.lblTitle.setText('<nobr><b>%s</b></nobr>' % scanParameters['title'])
        self.graph.xlabel(scanParameters['xlabel'])
        self.graph.ylabel(scanParameters['ylabel'])
        if self.scanObject.getScanType() == SpecScan.TIMESCAN:
            self.graph.setx1timescale(True)
        else:
            self.graph.setx1timescale(False)
        self.xdata = []
        self.ydata = []
        self.graph.newcurve('scan', self.xdata, self.ydata)
        self.graph.replot() 

    def newScanPoint(self, i, x, y):
        #if not self.canAddPoint:
        #    return
        self.xdata.append(x)
        self.ydata.append(y)
        self.graph.newcurve('scan', self.xdata, self.ydata)
        self.graph.replot() 
        

    def handleBlissGraphSignal(self, signalDict):
        if signalDict['event'] == 'MouseAt':
            self.lblPosition.setText("(X: %3.3f, Y: %3.3f)" % (signalDict['x'], signalDict['y']))


    #def instanceMirrorChanged(self,mirror):
    #    if BlissWidget.isInstanceMirrorAllow():
    #        self.safeConnect()
    #    else:
    #        self.safeDisconnect()


    """
    def cmdZoomInClicked(self):
        if self.cmdZoomIn.isOn():
            self.cmdZoomOut.setOn(False)

            self.graph.disablezoomback()           

        #QObject.disconnect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
        #QObject.disconnect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)
        if not self.cmdZoomOut.isOn() and not self.cmdZoomIn.isOn():
            pass
        else:
            QObject.connect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
            QObject.connect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)


    def cmdZoomOutClicked(self):
        if self.cmdZoomOut.isOn():
            self.cmdZoomIn.setOn(False)

            self.graph.enablezoomback()

        #QObject.disconnect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
        #QObject.disconnect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)
        if not self.cmdZoomOut.isOn() and not self.cmdZoomIn.isOn():
            pass
        else:
            QObject.connect(self.graph, SIGNAL('plotMousePressed(const QMouseEvent&)'), self.graph.onMousePressed)
            QObject.connect(self.graph, SIGNAL('plotMouseReleased(const QMouseEvent&)'), self.graph.onMouseReleased)
    """
