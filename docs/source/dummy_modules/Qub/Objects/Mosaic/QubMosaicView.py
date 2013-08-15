import weakref
import logging
import qt

from Qub.Widget.QubView import QubView

from Qub.Objects.QubCanvasViewBase import QubCanvasViewBase

class _MosaicCanvas(QubCanvasViewBase) :
    def __init__(self,parent,*args,**keys) :
        QubCanvasViewBase.__init__(self,parent,*args,**keys)
        self.__cnt = parent
        
    def setZoom(self,zoomX,zoomY,*args) :
        oldZoomx,oldZoomy = self._matrix.m11(),self._matrix.m22()
        oldDx,oldDy = self._matrix.dx() / float(oldZoomx),self._matrix.dy() / float(oldZoomy)
        self._matrix.setMatrix(zoomX,0,0,zoomY,
                               oldDx * zoomX,oldDy * zoomY)

        cWidth,cHeight = self._cvs.width() / float(oldZoomx),self._cvs.height() / float(oldZoomy)
        self._cvs.resize(cWidth * zoomX,cHeight * zoomY)
        self._update()

    ##@brief Change the scroll bar policy
    #@param mode accepted string values:
    # -# <b>"Auto"</b>: Scrollbars are shown if needed
    # -# <b>"AlwaysOff"</b>: Scrollbars are never displayed
    # -# <b>"Fit2Screen"</b>: Displayed mosaic size follow CanvasView size 
    #                       keeping data mosaic ratio
    # -# <b>"FillScreen"</b>: Displayed mosaic size is CanvasView size without 
    #                       keeping data mosaic ratio
    def setScrollbarMode(self,mode) :
        if mode in ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]:
            self._scrollMode = mode
            if mode == "Auto":
                self.setHScrollBarMode(self.Auto)
                self.setVScrollBarMode(self.Auto)

            elif mode == "AlwaysOff" or mode == "Fit2Screen" or mode == "FillScreen":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                self.__cnt.refresh()
                
class QubMosaicView(QubView) :
    def __init__(self,parent=None, name=None, actions=None):
        QubView.__init__(self, parent, name, 0)

        self.setView(_MosaicCanvas(self,name))


        self.__highestCalibration = None
        self.__mosaicImage = set()
        #Refresh
        self.__idle = qt.QTimer(self)
        qt.QObject.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)
        
        if actions is not None:
            self.addAction(actions)

    def addImage(self,image) :
        imageRef = weakref.ref(image,self.__imageRemoved)
        if imageRef in self.__mosaicImage : return

        self.__mosaicImage.add(imageRef)
        image.setMosaicView(self)

        self.checkHighestCalibration(image.calibration())
        
        if image.isShown(): self.refresh()

    def removeImage(self,image) :
        try:
            ref = weakref.ref(image)
            self.__mosaicImage.remove(ref)
        except KeyError: pass
    
    def __imageRemoved(self,imageRef) :
        try:
            self.__mosaicImage.remove(imageRef)
        except KeyError: pass

    def checkHighestCalibration(self,calib) :
        sizeX,_ = calib
        if self.__highestCalibration is None or abs(self.__highestCalibration[0]) > abs(sizeX):
            self.__highestCalibration = calib
            
    def refresh(self) :
        if not self.__idle.isActive() :
            self.__idle.start(0)

    def __refresh(self) :
        self.__idle.stop()
        self.__xOffset,self.__yOffSet = None,None
        imagesDisplay = []
        for imageRef in self.__mosaicImage :
            image = imageRef()
            if image and image.image() and image.isShown():
                #Calc top left corner position
                try:
                    xSize,ySize = image.calibration()
                    beamX,beamY = image.refPoint()
                except TypeError:
                    logging.getLogger().error("can't get image calibration and beam position")
                    continue

                motorX,motorY = image.position()
                qImage = image.image()

                leftPos = -beamX * xSize
                leftPos += motorX

                topPos = -beamY * ySize
                topPos += motorY

                highXSize,highYSize = self.__highestCalibration

                xPos = leftPos / highXSize
                yPos = topPos / highYSize

                if self.__xOffset is None or self.__xOffset > xPos:
                    self.__xOffset = xPos
                if self.__yOffSet is None or self.__yOffSet > yPos:
                    self.__yOffSet = yPos

                width = qImage.width() * (xSize / highXSize)
                height = qImage.height() * (ySize / highYSize)

                drawingManager = image.drawingManager()

                imagesDisplay.append((image.layer(),xPos,yPos,width,height,drawingManager))

        boundingRect = qt.QRect()
        allRect = qt.QRect()
        for layer,x,y,width,height,drawingManager in imagesDisplay :
            drawingManager.setRect(x - self.__xOffset,y - self.__yOffSet,
                                   width,height)
            boundingRect = boundingRect.unite(drawingManager.boundingRect())
            drawingManager.setZ(layer)
            allRect = allRect.unite(drawingManager.rect())

        view = self.view()
        view.canvas().resize(boundingRect.width(),boundingRect.height())
        scrollMode = view.scrollbarMode()
        if scrollMode == "Fit2Screen" or scrollMode == "FillScreen" :
            vp = view.viewport()
            viewWidth,viewHeight = vp.width(),vp.height()
            try:
                zoomX = float(viewWidth) / allRect.width()
                zoomY = float(viewHeight) / allRect.height()
            except ZeroDivisionError:
                return
            matrix = view.matrix()
            oldZoomX = matrix.m11()
            oldZoomY = matrix.m22()

            if scrollMode == "Fit2Screen" :
                zoom = min(zoomX,zoomY)
                if abs(oldZoomX - zoom) > 1e-3 or abs(oldZoomY - zoom) > 1e-3 :
                    view.setZoom(zoom,zoom)
            elif scrollMode == "FillScreen" :
                if abs(oldZoomX - zoomX) > 1e-3 or abs(oldZoomY - zoomY) > 1e-3:
                    view.setZoom(zoomX,zoomY)
        view.canvas().update()
