import qt
import struct
from Qub.Objects.QubDrawingManager import QubAddDrawing,Qub2PointSurfaceDrawingMgr
from Qub.Objects.QubDrawingCanvasTools import QubCanvasPixmap


def _mosaicViewRefresh(func) :
    def c(className,*args,**keys) :
        retVal = func(className,*args,**keys)
        if className.mosaicView is not None:
            className.mosaicView.refresh()
        return retVal
    return c

class QubMosaicImage :
    def __init__(self,image = None,motX = None,motY = None,layer = 0,imageId = None) :
        self.__image = image
        self.__imageId = imageId
        self.__motX = motX
        self.__motY = motY
        self.__pixelSize = (1,1)
        self.__refPoint = (0,0)
        self.mosaicView = None
        self.__drawingManager = None
        self.__layer = layer
        self.__isShown = False
        self.__lastImageSize = None
        
    def __del__(self) :
        self.__isShown = False
        if self.mosaicView is not None:
            self.mosaicView.refresh()

    def __getstate__(self):
        try:
            odict = self.__dict__.copy()
            odict['mosaicView'] = None
            odict['_QubMosaicImage__drawingManager'] = None
            odict['_QubMosaicImage__lastImageSize'] = None
            odict['_QubMosaicImage__isShown'] = False
            odict['imageString'] = self.__image.bits().asstring(self.__image.numBytes())
            odict['imageWidth'] = self.__image.width()
            odict['imageHeight'] = self.__image.height()
            odict['imageDepth'] = self.__image.depth()
            del odict['_QubMosaicImage__image']

            colorTable = self.__image.colorTable()
            if colorTable:
               odict['imageColortableNbColor'] = self.__image.numColors()
               odict['imageColortable'] = colorTable.asstring(self.__image.numColors() * 4)
        except AttributeError:
            import traceback
            traceback.print_exc()
            pass
        return odict

    def __setstate__(self,dict):
        try:
            imageString = dict['imageString']
            del dict['imageString']
            imageWidth = dict['imageWidth']
            del dict['imageWidth']
            imageHeight = dict['imageHeight']
            del dict['imageHeight']
            imageDepth = dict['imageDepth']
            del dict['imageDepth']
            im = qt.QImage(imageString,imageWidth,imageHeight,imageDepth,None,0,qt.QImage.IgnoreEndian)
            im.imageString = imageString
            try:
                numColor = dict['imageColortableNbColor']
                del dict['imageColortableNbColor']
                colorTable = dict['imageColortable']
                del dict['imageColortable']
                unpackstr = '%dL' % numColor
                im.setNumColors(numColor)
                for i,color in enumerate(struct.unpack(unpackstr,colorTable)) :
                    im.setColor(i,color)
            except KeyError: pass
            self.__image = im
        finally:
            self.__dict__.update(dict)
            
    ##@brief set a QImage
    #
    #@param image a QImage
    def setImage(self,image) :
        self.__image = image
        if self.__drawingManager is not None:
            self.__drawingManager.setImage(image)

        if self.__lastImageSize is None or \
           self.__lastImageSize[0] != image.width() or self.__lastImageSize[1] != image.height() :
            self.__lastImageSize = image.width(),image.height()
            if self.mosaicView is not None and self.isShown() :
                self.mosaicView.refresh()

    def image(self) :
        return self.__image

    ##@brief set an private id to the image
    #
    #@param imageId could be what you want as it's private
    def setImageId(self,imageId) :
        self.__imageId = imageId

    def imageId(self) :
        return self.__imageId

    ##@brief set image position
    #
    #@param motX can be a X pixel position if you don't use ChangePixelCalibration and ChangeBeamPosition
    #or motor X position
    #@param motY same as motX but for Y
    #
    @_mosaicViewRefresh
    def move(self,motX,motY) :
        self.__motX = motX
        self.__motY = motY

    def position(self) :
        return self.__motX,self.__motY
    
    @_mosaicViewRefresh
    def show(self) :
        self.__isShown = True
        if self.__drawingManager is not None:
            self.__drawingManager.show()

    @_mosaicViewRefresh
    def hide(self) :
        self.__isShown = False
        if self.__drawingManager is not None:
            self.__drawingManager.hide()
            
    def isShown(self) :
        return self.__isShown

    ##@brief get the display layer of the image
    #
    def layer(self) :
        return self.__layer

    ##@brief set the display layer of the image
    #
    @_mosaicViewRefresh
    def setLayer(self,layer) :
        self.__layer = layer

    
    @_mosaicViewRefresh
    def setCalibration(self,sizeX,sizeY) :
        self.__pixelSize = (sizeX,sizeY)
        if self.mosaicView is not None:
            self.mosaicView.checkHighestCalibration(self.__pixelSize)

    def calibration(self) :
        return self.__pixelSize

    @_mosaicViewRefresh
    def setRefPos(self,x,y) :
        self.__refPoint = x,y

    def refPoint(self) :
        return self.__refPoint
    
    ##@name Internal call DON'T USE IT AS A PUBLIC METHODE!!!
    #@{
    #

    #@brief set the mosaicView container
    #
    def setMosaicView(self,mosaicView) :
        try:
            self.mosaicView = mosaicView
            self.__drawingManager,_ = QubAddDrawing(mosaicView.view(),
                                                    Qub2PointSurfaceDrawingMgr,QubCanvasPixmap)
            self.__drawingManager.setCanBeModify(False)

            if self.__image is not None:
                self.__drawingManager.setImage(self.__image)

            if self.__isShown:
                self.__drawingManager.show()

            self.__drawingManager.setMosaicImage(self)
        except:
            import traceback
            traceback.print_exc()
            
    def drawingManager(self) :
        return self.__drawingManager

    ##@}
