import qt
import logging
from PyMca.QtBlissGraph import QtBlissGraph


class ScanPlotWidget(qt.QWidget):
    def __init__(self, parent=None, name="scan_plot_widget"):
        qt.QWidget.__init__(self, parent, name)

        self.xdata = []
        self.ylabel = ""

        self.isRealTimePlot = None
        self.isConnected = None
        self.isScanning = None

        self.lblTitle = qt.QLabel(self)
        self.graphPanel = qt.QFrame(self)
        buttonBox = qt.QHBox(self)
        self.lblPosition = qt.QLabel(buttonBox)
        self.graph = QtBlissGraph(self.graphPanel)

        qt.QObject.connect(
            self.graph, qt.PYSIGNAL("QtBlissGraphSignal"), self.handleBlissGraphSignal
        )
        qt.QObject.disconnect(
            self.graph,
            qt.SIGNAL("plotMousePressed(const QMouseEvent&)"),
            self.graph.onMousePressed,
        )
        qt.QObject.disconnect(
            self.graph,
            qt.SIGNAL("plotMouseReleased(const QMouseEvent&)"),
            self.graph.onMouseReleased,
        )

        self.graph.canvas().setMouseTracking(True)
        self.graph.enableLegend(False)
        self.graph.enableZoom(False)
        # self.graph.setAutoLegend(False)
        self.lblPosition.setAlignment(qt.Qt.AlignRight)
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
        self.setPaletteBackgroundColor(qt.Qt.white)

    def setRealTimePlot(self, isRealTime):
        self.isRealTimePlot = isRealTime

    def newScanStarted(self, scanParameters):
        self.graph.clearcurves()
        self.isScanning = True
        self.lblTitle.setText("<nobr><b>%s</b></nobr>" % scanParameters["title"])
        self.xdata = []
        self.graph.xlabel(scanParameters["xlabel"])
        self.ylabel = scanParameters["ylabel"]
        ylabels = self.ylabel.split()
        self.ydatas = [[] for x in range(len(ylabels))]
        for labels, ydata in zip(ylabels, self.ydatas):
            self.graph.newcurve(labels, self.xdata, ydata)
        self.graph.ylabel(self.ylabel)
        self.graph.setx1timescale(False)
        self.graph.replot()
        self.graph.setTitle("Energy scan started. Waiting values...")

    def newScanPoint(self, x, y):
        self.xdata.append(x)
        for label, ydata, yvalue in zip(
            self.ylabel.split(), self.ydatas, str(y).split()
        ):
            ydata.append(float(yvalue))
            self.graph.newcurve(label, self.xdata, ydata)
            self.graph.setTitle("Energy scan in progress. Please wait...")
        self.graph.replot()

    def handleBlissGraphSignal(self, signalDict):
        if signalDict["event"] == "MouseAt" and self.isScanning:
            self.lblPosition.setText(
                "(X: %0.2f, Y: %0.2f)" % (signalDict["x"], signalDict["y"])
            )

    def plotResults(
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
        self.graph.clearcurves()
        self.graph.setTitle(title)
        self.graph.newcurve("spline", chooch_graph_x, chooch_graph_y1)
        self.graph.newcurve("fp", chooch_graph_x, chooch_graph_y2)
        self.graph.replot()
        self.isScanning = False

    def plotScanCurve(self, scan_data):
        self.graph.clearcurves()
        self.graph.setTitle("Energy scan finished")
        self.lblTitle.setText("")
        xdata = [scan_data[el][0] for el in range(len(scan_data))]
        ydata = [scan_data[el][1] for el in range(len(scan_data))]
        self.graph.newcurve("energy", xdata, ydata)
        self.graph.replot()

    def clear(self):
        self.graph.clearcurves()
        # self.graph.setTitle("")
        self.lblTitle.setText("")
        self.lblPosition.setText("")

    def scanFinished(self):
        self.graph.setTitle("Energy scan finished")
