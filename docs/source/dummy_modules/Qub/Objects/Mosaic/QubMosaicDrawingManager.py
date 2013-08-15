import itertools

import qt

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr
from Qub.Objects.QubDrawingManager import QubLineDrawingMgr

from Qub.Objects.QubDrawingCanvasTools import QubCanvasPixmap

##@brief this little structure have the point pixel position with all the information needed
#to transform the pixel localisation in reel world
#
# - point => the pixel postion
# - refPoint => the pixel reference point of all mosaic image (i.e: usually the ref point is the beam position)
# - calibration => the is the calibration of the image under the position point
# - absPoint => this is the absolute point of the image, it is usally the motor position of the image under the position point
class QubMosaicPoint:
    def __init__(self) :
        self.point = None
        self.refPoint = None
        self.calibration = None
        self.absPoint = None
        self.imageId = None
        self.qimage = None
        
def _mosaicPoints(canvas,matrix,points) :
    returnPoints = []
    allPointSucced = True
    for x,y in points:
        items = [a for a in itertools.ifilter(lambda b: b.rtti() == QubCanvasPixmap.RTTI,canvas.collisions(qt.QPoint(x,y)))]
        if items :
            item = items[0]             # take the upper layer item
            mosaicImage = item.mosaicImage()
        else: mosaicImage = None

        p = QubMosaicPoint()
        if mosaicImage:
            x,y = x - item.x(),y - item.y()
            qimage = mosaicImage.image()
            matrix = qt.QWMatrix(float(item.width()) / qimage.width(),0,0,float(item.height()) / qimage.height(),0,0)
            p.point = matrix.invert()[0].map(x,y)
            p.refPoint = mosaicImage.refPoint()
            p.calibration = mosaicImage.calibration()
            p.absPoint = mosaicImage.position()
            p.imageId = mosaicImage.imageId()
            p.qimage = qimage
        else:
            if matrix: p.point = matrix.invert()[0].map(x,y)
            else: p.point = x,y
            allPointSucced = False
        returnPoints.append(p)

    return returnPoints,allPointSucced
            
def _mosaicPointsFromRect(canvas,boundingRect,points) :
    items = [x for x in itertools.ifilter(lambda y: y.rtti() == QubCanvasPixmap.RTTI,canvas.collisions(boundingRect))]
    returnPoints = []
    if items:
        for x,y in points :
            item_selected = []
            for item in items :
                bBox = item.boundingRect()
                if bBox.contains(x,y) :
                    item_selected = [(0,item)]
                    break
                else:
                    center = item.boundingRect().center()
                    xCenter,yCenter = center.x(),center.y()
                    dist = (xCenter - x) ** 2 + (yCenter - y) ** 2
                    item_selected.append((dist,item))
            item_selected.sort(lambda a,b : a[0] - b[0])
            item = item_selected[0][1]
            mosaicImage = item.mosaicImage()
            if not mosaicImage: break # Can't do better
            p = QubMosaicPoint()
            x,y = x - item.x(),y - item.y()
            qimage = mosaicImage.image()
            matrix = qt.QWMatrix(float(item.width()) / qimage.width(),0,0,float(item.height()) / qimage.height(),0,0)
            p.point = matrix.invert()[0].map(x,y)
            p.refPoint = mosaicImage.refPoint()
            p.calibration = mosaicImage.calibration()
            p.absPoint = mosaicImage.position()
            p.imageId = mosaicImage.imageId()
            p.qimage = qimage
            returnPoints.append(p)
    return returnPoints

##@brief This class manage all the drawing object that can be define with one point on a mosaic
#@ingroup DrawingManager
class QubMosaicPointDrawingMgr(QubPointDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubPointDrawingMgr.__init__(self,aCanvas,aMatrix)
        self.__defaultZ = 2**31
        
    def mosaicPoints(self) :
        if self._matrix is not None :
            x,y = self._matrix.map(self._x,self._y)
        else :
            x,y = self._x,self._y
        returnPoints,_ = _mosaicPoints(self._canvas,self._matrix,[(x,y)])
        return returnPoints

    def setDefaultZ(self,z) :
        self.__defaultZ = z
        
    def show(self) :
        QubPointDrawingMgr.show(self)
        self.setZ(self.__defaultZ)

##@brief this class manage all drawing object
#that can be define with a line on a mosaic
#@ingroup DrawingManager
class QubMosaicLineDrawingMgr(QubLineDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubLineDrawingMgr.__init__(self,aCanvas,aMatrix)
        self.__defaultZ = 2**31

    def mosaicPoints(self) :
        if self._matrix is not None :
            x1,y1 = self._matrix.map(self._x1,self._y1)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
        returnPoints,ok = _mosaicPoints(self._canvas,self._matrix,[(x1,y1),(x2,y2)])
        if not ok:                      # not all point are under an image
            tmpPoints = _mosaicPointsFromRect(self._canvas,self.boundingRect(),[(x1,y1),(x2,y2)])
            if tmpPoints: returnPoints = tmpPoints
        return returnPoints

    def setDefaultZ(self,z) :
        self.__defaultZ = z
        
    def show(self) :
        QubLineDrawingMgr.show(self)
        self.setZ(self.__defaultZ)

