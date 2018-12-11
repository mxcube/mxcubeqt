import logging
import numpy
import qt
import qtcanvas

from Qub.Widget.QubAction import QubToggleAction

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr,QubAddDrawing
from Qub.Objects.QubDrawingCanvasTools import QubCanvasHLine,QubCanvasVLine

from BlissFramework.BaseComponents import BlissWidget

__category__ = "Camera"

class _graphPoint(qtcanvas.QCanvasPolygon) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasPolygon.__init__(self,canvas)
        
    def drawShape(self,painter) :
        points = self.points()
        if self.isVisible():
            painter.setPen(self.pen())
            painter.drawLineSegments(points,0)


class CameraProfileBrick(BlissWidget) :
    def __init__(self,*args) :
        BlissWidget.__init__(self,*args)
        self.__view = None
        self.__drawing = None
        self.__line = None
        self.__pointSelected = None
        self.__graphs = None
        self.__refreshTimer = qt.QTimer(self)
        qt.QObject.connect(self.__refreshTimer,qt.SIGNAL('timeout()'),self.__refreshGraph)
        # Properties
                        ####### SIGNAL #######
        self.defineSignal('getView',())
        self.defineSignal('getImage',())
        self.setFixedSize(0,0)
        
               
    def run(self) :
        key = {}
        self.emit(qt.PYSIGNAL("getView"), (key,))
        try:
            self.__view = key['view']
            self.__drawing = key['drawing']
        except KeyError:
            logging.getLogger().error('%s : You have to connect this brick to the CameraBrick',self.name())
            return
        
        self.__toggleButton = QubToggleAction(label='Show profile',name='histogram',place='toolbar',
                                              group='Camera',autoConnect = True)
        qt.QObject.connect(self.__toggleButton,qt.PYSIGNAL('StateChanged'),self.__showCBK)
        self.__view.addAction([self.__toggleButton])

        self.__line,_,_ = QubAddDrawing(self.__drawing,QubPointDrawingMgr,QubCanvasHLine,QubCanvasVLine)
        self.__line.setEndDrawCallBack(self.__clickedPoint)

        graphV = _graphPoint(self.__drawing.canvas())
        graphV.setPen(qt.QPen(qt.Qt.red,2))

        graphH = _graphPoint(self.__drawing.canvas())
        graphH.setPen(qt.QPen(qt.Qt.green,2))
        graphH.setZ(5)
        
        self.__graphs = (graphH,graphV)
        
    def __showCBK(self,state) :
        if state:
            self.__line.startDrawing()
            self.__refreshTimer.start(1000)
        else:
            self.__refreshTimer.stop()
            self.__line.hide()
            self.__line.stopDrawing()

    def __clickedPoint(self,drawingMgr) :
        self.__pointSelected = drawingMgr.point()

        for graph in self.__graphs:
            graph.show()

        self.__refreshGraph()

    def __refreshGraph(self) :
        key = {}
        try:
            self.emit(qt.PYSIGNAL("getImage"), (key,))
            qimage = key['image']
        except KeyError: return

        matrix = self.__drawing.matrix()
        try:
            x,y = self.__pointSelected
        except TypeError: return
        
        (graphH,graphV) = self.__graphs
        
        array = numpy.fromstring(qimage.bits().asstring(qimage.width() * qimage.height() * 4),
                                 dtype = numpy.uint8)
        array.shape = qimage.height(),qimage.width(),-1
        
        yColor = array[y]
        yData = yColor[:,0] * 0.114 + yColor[:,1] * 0.587 + yColor[:,2] * 0.299
        maxData = yData.max()
        maxHeight = qimage.height() / 3
        z = float(maxHeight) / maxData
        yData = yData * z
        yData = (qimage.height()) - yData
        #yData[len(yData)/2]= 220
        xData = numpy.arange(qimage.width())
        allPoint = numpy.array(zip(xData,yData))
        allPoint.shape = -1        
        aP = qt.QPointArray(len(xData))
        aP.putPoints(0,allPoint.tolist())
        aP = matrix.map(aP)
        graphH._myXProfile = aP
        graphH.setPoints(aP)

        xColor = array[:,x]
        xData = xColor[:,0] * 0.114 + xColor[:,1] * 0.587 + xColor[:,2] * 0.299
        maxData = xData.max()
        maxHeight = qimage.width() / 3
        z = float(maxHeight) / maxData
        xData = xData * z
        xData = qimage.width() - xData
        yData = numpy.arange(qimage.height())
        allPoint = numpy.array(zip(xData,yData))
        allPoint.shape = -1
        aP = qt.QPointArray(len(xData))
        aP.putPoints(0,allPoint.tolist())
        aP = matrix.map(aP)
        graphV._myYProfile = aP
        graphV.setPoints(aP)
