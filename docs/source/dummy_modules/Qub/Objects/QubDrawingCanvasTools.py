import weakref
import math
import itertools
import numpy
import qt
import qtcanvas

from Qub.Objects.QubDrawingConstraint import QubAngleConstraint
from Qub.Objects.QubDrawingEvent import QubModifyAbsoluteAction

from Qub.CTools import pixmaptools

try:
    from opencv import cv
    from Qub.CTools.opencv import qtTools
except ImportError:
    cv = None

##@defgroup DrawingCanvasTools Low level objects drawing
#@brief this is the group of all vector objects which can be put in a simple QCanvas.
#
#HOW TO COOK a new QubDrawingCanvasTools:
# - for all new object with several qtcanvas object base, you need to redefine :
#   - def show(self)
#   - def hide(self)
#   - def setPen(self,pen)
#   - def setCanvas(self,canvas)
#
# - for object acting as a point, you need to redefine :
#   - def move(self,x,y)
#
# - for object acting as a line, you need to redefine :
#   - def setPoints(self,x1,y1,x2,y2)
#
# - for object acting as a surface ie (a simple rectangle define by TOP LEFT and BOTTOM RIGH points),
#you need to redefine :
#   - def move(self,x,y)
#   - def setSize(self,width,height)
#
#
# - if your object need the scrollView, you have to redefine :
#   - def setScrollView(self,scrollView)
# - if your object need the matrix, you have to redefine :
#   - def setMatrix(self,matrix)


##@defgroup DrawingCanvasToolsPoint Point objects
#@brief all drawingObject in this group can be used with Qub::Objects::QubDrawingManager::QubPointDrawingMgr
#@ingroup DrawingCanvasTools
#

##@defgroup DrawingCanvasToolsRectangle Two points surface
#@brief all drawingObject in this group can be used with Qub::Objects::QubDrawingManager::Qub2PointSurfaceDrawingManager
#@ingroup DrawingCanvasTools
#

##@defgroup DrawingCanvasToolsContainer Stand alone drawing object
#@brief all drawingObject in this group can only be use with Qub::Objects::QubDrawingManager::QubContainerDrawingMgr
#@ingroup DrawingCanvasTools
#

##@defgroup DrawingCanvasToolsPolygon Polygon objects
#@brief all drawing in this group can only be use with Qub::Objects::QubDrawingManager::QubPolygoneDrawingMgr
#@ingroup DrawingCanvasTools
#

QubCanvasRectangle = qtcanvas.QCanvasRectangle

##@brief the Ellipse object
#@ingroup DrawingCanvasToolsPoint
#@ingroup DrawingCanvasToolsRectangle
class QubCanvasEllipse(qtcanvas.QCanvasEllipse):
    def __init__(self,*args) :
        qtcanvas.QCanvasEllipse.__init__(self,*args)
        self.__centerRayonDrawingMode = False
    def setCenterRayonDrawingMode(self,aFlag) :
        self.__centerRayonDrawingMode = aFlag
        self.update()
        
    def setSize(self,width,height) :
        if self.__centerRayonDrawingMode:
            width *= 2
            height *= 2
        qtcanvas.QCanvasEllipse.setSize(self,width,height)
        
    def drawShape(self, p):
        p.drawArc(int(self.x()-self.width()/2+0.5), 
                  int(self.y()-self.height()/2+0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())

                        
##@brief the Donut Object
#@ingroup DrawingCanvasToolsPoint
#@ingroup DrawingCanvasToolsRectangle
#@ingroup DrawingCanvasToolsPolygon
class QubCanvasDonut(qtcanvas.QCanvasEllipse):
    def __init__(self,canvas) :
        qtcanvas.QCanvasEllipse.__init__(self,canvas)
        if isinstance(canvas,QubCanvasDonut) :
            self.__centerRayonDrawingMode = canvas._QubCanvasDonut__centerRayonDrawingMode
            self.__discwidth = canvas._QubCanvasDonut__discwidth
            self.__circle = canvas._QubCanvasDonut__circle
            self.__matrix = canvas._QubCanvasDonut__matrix
            self.__nbDrawPoint = canvas._QubCanvasDonut__nbDrawPoint
        else:
            self.__centerRayonDrawingMode = False
            self.__discwidth = 5
            self.__oldDiscWidth = None
            self.__circle = False
            self.__matrix = None
            self.__nbDrawPoint = 3
        
    ##@brief this methode is called by the drawing manager
    #
    # - first point move the center
    # - second point define the rayon
    # - third point define the width (on absciss axis) 
    def move(self,x,y,point_id = 0) :
        if point_id == 0:               # CENTER
            qtcanvas.QCanvasEllipse.move(self,x,y)
        elif point_id == 1:             # RAYON
            width = abs(self.x() - x) * 2
            height = abs(self.y() - y) * 2
            if self.__circle:
                rayon = math.sqrt(width ** 2 + height ** 2)
                height = rayon
                width = rayon
            qtcanvas.QCanvasEllipse.setSize(self,width,height)
            if self.__nbDrawPoint > 2 : # START ANGLE SET
                x1,y1 = x - self.x(),y - self.y()
                dist = math.sqrt(x1 ** 2 + y1 ** 2)
                angle = math.acos(x1/dist)
                if y > self.y() : angle = -angle
                angle = angle * 180 / math.pi
                self.setAngles(angle * 16,self.angleLength())
        elif point_id == 2:             # DISC WIDTH
            extXRayon = (x - self.x()) * 2
            extYRayon = (y - self.y()) * 2
            rayon = math.sqrt(extXRayon ** 2 + extYRayon ** 2)
            discwidth =  abs(rayon) - self.width()
            if discwidth <= 0: discwidth = 1

            self.__oldDiscWidth = self.__discwidth
            self.__discwidth = discwidth
            self.update()
        else:
            x1 = x - self.x()
            y1 = y - self.y()
            startAngle = -((self.angleStart() / 16) * math.pi / 180)
            x2 = math.cos(startAngle)
            y2 = math.sin(startAngle)
            scalar = x1 * x2 + y1 * y2
            dist1 = math.sqrt(x1 **2 + y1 **2)
            dist2 = math.sqrt(x2 **2 + y2 ** 2)
            angle = math.acos(scalar/(dist1 * dist2))
            #prod vect
            z = x1 * y2 - x2 * y1
            if z < 0 : angle = 2 * math.pi - angle
            angle = angle * 180 / math.pi
            self.setAngles(self.angleStart(),angle * 16)
        return self.__nbDrawPoint <= point_id # END DRAW

    def areaPoints(self) :
        point = qt.QPointArray()
        if self.__oldDiscWidth > self.__discwidth :
            discwidth = self.__oldDiscWidth
        else: discwidth = self.__discwidth
        self.__oldDiscWidth = None

        width = self.width() + discwidth + 6
        height = self.height() + discwidth + 6
        point.makeEllipse(self.x() - 3,self.y() - 3,width,height)
        point.translate(-width / 2,-height / 2)
        return point
    
    ##@brief set the last point id to stop drawing
    #the circle or arc
    def setEndPointDraw(self,nbPoint) :
        self.__nbDrawPoint = nbPoint

    def setCircleMode(self,aFlag) :
        self.__circle = aFlag
        self.update()
        
    def setCenterRayonDrawingMode(self,aFlag) :
        self.__centerRayonDrawingMode = aFlag
        self.update()

    def setSize(self,width,height) :
        if self.__centerRayonDrawingMode:
            width *= 2
            height *= 2
        qtcanvas.QCanvasEllipse.setSize(self,width,height)

    def setPen(self,pen) :
        qtcanvas.QCanvasEllipse.setPen(self,pen)
        color = pen.color()
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def setMatrix(self,matrix) :
        self.__matrix = matrix

    def setDiscWidth(self, width) :
        self.__discwidth = width
             
    def drawShape(self, p):
        discwidth = self.__discwidth
        if self.__matrix is not None:
            scale = max(self.__matrix.m11(),self.__matrix.m22())
            discwidth *= scale

        if self.__discwidth > 1:
            width = self.width() + self.__discwidth
            height = self.height() + self.__discwidth
            xout = self.x() - width / 2 - 1
            yout = self.y() - height / 2 - 1

            regionout = qt.QRegion(xout,yout,
                                   width,height, 
                                   qt.QRegion.Ellipse)

            internalWidth = self.width()
            internalHeight = self.height()
            
            xin  = self.x() - internalWidth / 2 - 1
            yin  = self.y() - internalHeight / 2 - 1

            regionin  = qt.QRegion(xin,yin,
                                   internalWidth,internalHeight,
                                   qt.QRegion.Ellipse)

            region = regionout.subtract(regionin)
            
            p.setClipRegion(region, qt.QPainter.CoordPainter)
            p.setBrush(self.brush())
            if not self.angleStart() and self.angleLength() == 360*16 :
                p.drawEllipse(xout,yout,width,height)
            else:
                p.drawPie(xout,yout,width,height,self.angleStart(),self.angleLength())

            p.setClipping(0)       
            p.setPen(qt.QPen(self.brush().color(),1))
            p.drawArc(xout,yout,width,height,
                      self.angleStart(), self.angleLength())

        p.setPen(qt.QPen(self.brush().color(),1))
        p.drawArc(int(self.x()-self.width()/2-0.5), 
                  int(self.y()-self.height()/2-0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())
        p.drawLine(self.x() - 5,self.y(),self.x() + 5,self.y())
        p.drawLine(self.x(),self.y() - 5,self.x(),self.y() + 5)

##@brief the Beam Object
#@ingroup DrawingCanvasToolsPoint
class QubCanvasBeam(QubCanvasEllipse):
    def __init__(self,canvas) :
        if isinstance(canvas,QubCanvasBeam) :
            QubCanvasEllipse.__init__(self,canvas)
            self.__centerE = QubCanvasEllipse(canvas._QubCanvasBeam__centerE)
        else:
            QubCanvasEllipse.__init__(self, 29,19,0,5760, canvas)
            self.__centerE = QubCanvasEllipse(7,7,0,5760, canvas)

    def move(self,x,y) :
        QubCanvasEllipse.move(self,x,y)
        self.__centerE.move(x, y)

    def show(self) :
        QubCanvasEllipse.show(self)
        self.__centerE.show()

    def hide(self) :
        QubCanvasEllipse.hide(self)
        self.__centerE.hide()
        canvas = self.canvas()
        if canvas: canvas.update()

    def setPen(self,pen) :
        QubCanvasEllipse.setPen(self,pen)
        self.__centerE.setPen(pen)

    def setCanvas(self,aCanvas) :
        QubCanvasEllipse.setCanvas(self,aCanvas)
        self.__centerE.setCanvas(aCanvas)

##@brief this is a simple target with a circle and a cross
#@ingroup DrawingCanvasToolsPoint
class QubCanvasTarget(QubCanvasEllipse) :
    def __init__(self,canvas) :
        if isinstance(canvas,QubCanvasTarget) :
            self.__pointWidth = canvas._QubCanvasTarget__pointWidth
            QubCanvasEllipse.__init__(self,canvas)
            qtcanvas.QCanvasEllipse.__init__(self,canvas)
            self.__hLine = qtcanvas.QCanvasLine(canvas._QubCanvasTarget__hLine)
            self.__vLine = qtcanvas.QCanvasLine(canvas._QubCanvasTarget__vLine)
        else: 
            self.__pointWidth = 20
            QubCanvasEllipse.__init__(self,self.__pointWidth,self.__pointWidth,canvas)
            self.__hLine = qtcanvas.QCanvasLine(None)
            self.__hLine.setPoints(0,0,self.__pointWidth,self.__pointWidth)
            self.__vLine = qtcanvas.QCanvasLine(None)
            self.__vLine.setPoints(0,self.__pointWidth,self.__pointWidth,0)
            
    def move(self,x,y) :
        QubCanvasEllipse.move(self,x,y)
        self.__hLine.move(x - self.__pointWidth / 2,y - self.__pointWidth / 2)
        self.__vLine.move(x - self.__pointWidth / 2,y - self.__pointWidth / 2)

    def show(self) :
        QubCanvasEllipse.show(self)
        self.__hLine.show()
        self.__vLine.show()

    def hide(self) :
        QubCanvasEllipse.hide(self)
        self.__hLine.hide()
        self.__vLine.hide()
        canvas = self.canvas()
        if canvas: canvas.update()

    def drawShape(self,p) :
        QubCanvasEllipse.drawShape(self,p)
        self.__hLine.drawShape(p)
        self.__vLine.drawShape(p)

    def setCanvas(self,canvas) :
        QubCanvasEllipse.setCanvas(self,canvas)

    def setPen(self,pen) :
        QubCanvasEllipse.setPen(self,pen)
        self.__hLine.setPen(pen)
        self.__vLine.setPen(pen)
##@brief this is a simple point with a text
#@ingroup DrawingCanvasToolsPoint
class QubCanvasPointNText(qtcanvas.QCanvasRectangle) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        if isinstance(canvas,QubCanvasPointNText) :
            self.__text = QubCanvasText(canvas._QubCanvasPointNText__text)
            self.setSize(canvas.width(),canvas.height())
        else:
            self.__text = QubCanvasText(canvas)
            self.setSize(5,5)
    ##@brief set the text value
    #
    def setText(self,text) :
        self.__text.setText(text)
        point = self.rect().center()
        self.move(point.x(),point.y())
    ##@brief change the pen point and text
    #
    def setPen(self,pen) :
        qtcanvas.QCanvasRectangle.setPen(self,pen)
        self.__text.setColor(pen.color())
    ##@brief set text color
    #
    def setTextColor(self,color) :
        self.__text.setColor(color)
    ##@brief set point color
    #
    def setPointColor(self,color) :
        self.setPointPen(qt.QPen(color))
    ##@brief set pen point
    #
    def setPointPen(self,pen) :
        qtcanvas.QCanvasRectangle.setPen(self,pen)
        
    def move(self,x,y) :
        rect = self.rect()
        rect.moveCenter(qt.QPoint(x,y))
        qtcanvas.QCanvasRectangle.move(self,rect.x(),rect.y())
        rect = self.__text.boundingRect()
        Xtext,Ytext = x - 2 - rect.width(),y - 2 - rect.height()
        self.__text.move(Xtext,Ytext)
        collisionObj = [obj for obj in self.__text.collisions(True) if obj != self]
        if collisionObj:
            self.__text.move(x + self.width() + 2,y - 2 - rect.height())
            
    def setSize(self,width,height) :
        if not width % 2 : width += 1
        if not height % 2: height += 1
        qtcanvas.QCanvasRectangle.setSize(self,width,height)
        
    def show(self) :
        qtcanvas.QCanvasRectangle.show(self)
        self.__text.show()
        self.update()
        canvas = self.canvas()
        if canvas: canvas.update()
        
    def hide(self) :
        qtcanvas.QCanvasRectangle.hide(self)
        self.__text.hide()
        self.update()
        canvas = self.canvas()
        if canvas: canvas.update()
        
    def drawShape(self, p):
        rect = self.rect()
        p.drawLine(rect.left(),rect.top(),rect.right(),rect.bottom())
        p.drawLine(rect.left(),rect.bottom(),rect.right(),rect.top())

    def boundingRect(self) :
        rect = qtcanvas.QCanvasRectangle.boundingRect(self)
        rect.unite(self.__text.boundingRect())
        return rect

    def setCanvas(self,canvas) :
        qtcanvas.QCanvasRectangle.setCanvas(self,canvas)
        self.__text.setCanvas(canvas)
        
##@brief simple text with rotation
#@ingroup DrawingCanvasToolsPoint
class QubCanvasText(qtcanvas.QCanvasText) :
    def __init__(self,canvas) :
        if isinstance(canvas,qtcanvas.QCanvasText) :
            qtcanvas.QCanvasText.__init__(self,canvas.canvas())
            self.setText(canvas.text())
            self.setFont(canvas.font())
            self.setColor(canvas.color())
            self.setX(canvas.x())
            self.setY(canvas.y())
            self.setZ(canvas.z())
            self.setVisible(canvas.isVisible())
        else:
            qtcanvas.QCanvasText.__init__(self,canvas)
        if isinstance(canvas,QubCanvasText) :
            self.__rotation_angle = canvas._QubCanvasText__rotation_angle
        else:
            self.__rotation_angle = 0
    def setRotation(self,angle) :
        self.__rotation_angle = angle
    def rotation(self) :
        return self.__rotation_angle
    def boundingRect(self) :
        rect = qtcanvas.QCanvasText.boundingRect(self)
        if self.__rotation_angle :
            rotMatrix = qt.QWMatrix(1,0,0,1,0,0)
            rotMatrix.translate(rect.x(),rect.y())
            rotMatrix.rotate(self.__rotation_angle)
            rotMatrix.translate(-rect.x(),-rect.y())
            rect = rotMatrix.map(rect)
        return rect
    def draw(self,painter) :
        if self.__rotation_angle :
            painter.translate(self.x(),self.y())
            painter.rotate(self.__rotation_angle)
            painter.translate(-self.x(),-self.y())
        qtcanvas.QCanvasText.draw(self,painter)
        if self.__rotation_angle:
            painter.translate(self.x(),self.y())
            painter.rotate(-self.__rotation_angle)
            painter.translate(-self.x(),-self.y())
##@brief this is a vertical line draw on the height of the canvas
#@ingroup DrawingCanvasToolsPoint
class QubCanvasVLine(qtcanvas.QCanvasLine) :
    def move(self,x,y) :
        height = self.canvas().height()
        self.setPoints(x,0,x,height)

    def hide(self) :
        qtcanvas.QCanvasLine.hide(self)
        canvas = self.canvas()
        if canvas: canvas.update()

class QubCanvasSlitbox(qtcanvas.QCanvasRectangle) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)

        if isinstance(canvas,QubCanvasSlitbox) :
            self.__canvas = canvas._QubCanvasSlitbox__canvas
            self.__hline = qtcanvas.QCanvasLine(canvas._QubCanvasSlitbox__hline)
            self.__vline = qtcanvas.QCanvasLine(canvas._QubCanvasSlitbox__vline)
            self.__slitbox_width = canvas._QubCanvasSlitbox__slitbox_width
            self.__slitbox_height = canvas._QubCanvasSlitbox__slitbox_height
        else:
            self.__hline = qtcanvas.QCanvasLine(canvas)
            self.__vline = qtcanvas.QCanvasLine(canvas)
            self.__canvas = canvas
            self.__slitbox_width = None
            self.__slitbox_height = None
            
        
    def update(self) :
        (xMid,yMid) = (self.__canvas.width() / 2,self.__canvas.height() / 2)
        self.__hline.setPoints(xMid - 20,yMid,xMid + 20,yMid)
        self.__vline.setPoints(xMid,yMid - 20,xMid,yMid + 20)
       
        if self.__slitbox_width is None or self.__slitbox_height is None:
            self.setSize(0,0)
            self.setX(xMid)
            self.setY(yMid)
        else:
            self.setSize(self.__slitbox_width, self.__slitbox_height)
            self.setX(xMid - self.__slitbox_width/2)
            self.setY(yMid - self.__slitbox_height/2)
        
        
    def setCanvas(self,canvas) :
        self.__canvas = canvas
        self.__hline.setCanvas(canvas)
        self.__vline.setCanvas(canvas)
        
    def show(self) :
        qtcanvas.QCanvasRectangle.show(self)
        self.__hline.show()
        self.__vline.show()

    def hide(self) :
        qtcanvas.QCanvasRectangle.hide(self)
        self.__hline.hide()
        self.__vline.hide()
        canvas = self.canvas()
        if canvas: canvas.update()

    def setPen(self,pen) :
        self.__hline.setPen(pen)
        self.__vline.setPen(pen)

    def setSlitboxPen(self, pen):
        qtcanvas.QCanvasRectangle.setPen(self,pen)

    def setSlitboxSize(self, w, h):
        self.__slitbox_width, self.__slitbox_height = w, h
        self.update()
        
        
##@brief this is a horizontal line draw on the width of the canvas
#@ingroup DrawingCanvasToolsPoint
class QubCanvasHLine(qtcanvas.QCanvasLine) :
    def move(self,x,y) :
        width = self.canvas().width()
        self.setPoints(0,y,width,y)

    def hide(self) :
        qtcanvas.QCanvasLine.hide(self)
        canvas = self.canvas()
        if canvas: canvas.update()

##@brief this is a pixmap display object
#@ingroup DrawingCanvasToolsRectangle
class QubCanvasPixmap(qtcanvas.QCanvasRectangle) :
    RTTI = 2000
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        if isinstance(canvas,QubCanvasPixmap) :
            self.__image = canvas._QubCanvasPixmap__image.copy()
            class pixmapIO :
                def putImage(self,pixmap,x,y,image) :
                    pixmap.convertFromImage(image)
            self.__pixmapIO = pixmapIO()
        else:
            self.__image = qt.QImage()
            self.__pixmapIO = pixmaptools.IO()
            self.__pixmapIO.setShmPolicy(pixmaptools.IO.ShmKeepAndGrow)

        self.__pixmap = qt.QPixmap()
        self.__scrollView = None
        self.__mosaicImage = None
        self.__alphaChannel = None
        
    def setImage(self,image) :
        self.__image = image
        self.update()
        canvas = self.canvas()
        if canvas: canvas.update()

    def setAlphaChannel(self,val) :
        if 0. <= val < 1. :
            self.__alphaChannel = val
            self.update()
            canvas = self.canvas()
            if canvas: canvas.update()
        else:
            self.__alphaChannel = None
            
    def hide(self) :
        qtcanvas.QCanvasRectangle.hide(self)
        canvas = self.canvas()
        if canvas: canvas.update()
        
    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def setMosaicImage(self,mosaicImage) :
        self.__mosaicImage = weakref.ref(mosaicImage)

    def mosaicImage(self) :
        return self.__mosaicImage and self.__mosaicImage() or None
    
    def draw(self,painter) :
        if self.__image:
            if self.__scrollView :
                xOri,yOri = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
                viewSizeX,viewSizeY = (self.__scrollView.visibleWidth(),self.__scrollView.visibleHeight())
                viewRect = qt.QRect(xOri,yOri,viewSizeX,viewSizeY)
                boundingBox = viewRect.intersect(self.boundingRect())

                if boundingBox.isNull():
                    print 'Nothing to do rectangle is not in the view space'
                    return # Nothing to do rectangle is not in the view space

                boundingBox.moveBy(-self.x(),-self.y())
                imageWidth,imageHeight = self.__image.width(),self.__image.height()
                xOriPixmapCpy,yOriPixmapCpy = boundingBox.x(),boundingBox.y()
                scaleWidth,scaleHeight = boundingBox.width(),boundingBox.height()
                try:
                    matrix = qt.QWMatrix(float(imageWidth) / self.width(),0,0,
                                         float(imageHeight) / self.height(),0,0)
                except ZeroDivisionError: return
                boundingBox = matrix.map(boundingBox)
                image = self.__image.copy(boundingBox)
            else:
                xOriPixmapCpy,yOriPixmapCpy = 0,0
                scaleWidth,scaleHeight = self.width(),self.height()
                image = self.__image

            if not image.isNull() :
                image = image.scale(scaleWidth,scaleHeight)
                if self.__alphaChannel is not None:
                    canvas = self.canvas()
                    if canvas:
                        backgroundImage = canvas.lastImage()
                        if backgroundImage:
                            xzoom,yzoom = backgroundImage.width() / float(canvas.width()),backgroundImage.height() / float(canvas.height())
                            backgroundImage = backgroundImage.copy((self.x() + xOriPixmapCpy) * xzoom,
                                                                   (self.y() + yOriPixmapCpy) * yzoom,
                                                                   image.width() * xzoom,image.height() * yzoom)
                            backI = qtTools.getImageOpencvFromQImage(backgroundImage)
                            if xzoom != 1. or yzoom != 1.:
                                tmpBack = cv.cvCreateImage(cv.cvSize(image.width(),image.height()),backI.depth,backI.nChannels)
                                cv.cvResize(backI,tmpBack,cv.CV_INTER_LINEAR)
                                backI = tmpBack
                            if backI.nChannels == 1:
                                tmpBack = cv.cvCreateImage(cv.cvSize(backI.width,backI.height),backI.depth,3)
                                cv.cvCvtColor(backI,tmpBack,cv.CV_GRAY2RGB)
                                backI = tmpBack
                            im = qtTools.getImageOpencvFromQImage(image)
                            destimage = cv.cvCreateImage(cv.cvSize(im.width,im.height),im.depth,im.nChannels)
                            cv.cvAddWeighted(backI,1. - self.__alphaChannel,
                                             im,self.__alphaChannel,0.,
                                             destimage)
                            image = qtTools.getQImageFromImageOpencv(destimage)
                                             
                if self.__pixmap.size != image.size() :
                    self.__pixmap.resize(image.size())
                self.__pixmapIO.putImage(self.__pixmap,0,0,image)


                painter.drawPixmap(self.x() + xOriPixmapCpy,self.y() + yOriPixmapCpy,self.__pixmap)

    def rtti(self) :
        return QubCanvasPixmap.RTTI
    
##@brief this object display the scale on bottom left of the image
#@ingroup DrawingCanvasToolsContainer
class QubCanvasScale(qtcanvas.QCanvasRectangle) :
    HORIZONTAL,VERTICAL,BOTH = (0x1,0x2,0x3)
    def __init__(self,canvas) :
        if isinstance(canvas,QubCanvasScale) :
            self.__hLine = qtcanvas.QCanvasLine(canvas._QubCanvasScale__hLine)
            self.__hText = QubCanvasText(canvas._QubCanvasScale__hText)
            
            self.__vLine = qtcanvas.QCanvasLine(canvas._QubCanvasScale__vLine)
            self.__vText = QubCanvasText(canvas._QubCanvasScale__vText)
            
            self.__globalShow = canvas._QubCanvasScale__globalShow
            self.__xPixelSize = canvas._QubCanvasScale__xPixelSize
            self.__yPixelSize = canvas._QubCanvasScale__yPixelSize
            self.__mode = canvas._QubCanvasScale__mode
            self.__unit = list(canvas._QubCanvasScale__unit)
            self.__autorizeValues = list(canvas._QubCanvasScale__autorizeValues)

            self.__canvas = canvas._QubCanvasScale__canvas
            self.__pen = qt.QPen(canvas._QubCanvasScale__pen)
        else:
            color = qt.Qt.green
            self.__pen = qt.QPen(color,4)
            self.__hLine = qtcanvas.QCanvasLine(canvas)
            self.__hLine.setPen(self.__pen)
            self.__hText = QubCanvasText(canvas)
            self.__hText.setColor(color)

            self.__vLine = qtcanvas.QCanvasLine(canvas)
            self.__vLine.setPen(self.__pen)
            self.__vText = QubCanvasText(canvas)
            self.__vText.setColor(color)

            self.__globalShow = False   # remember if the widget is shown
            self.__xPixelSize = 0
            self.__yPixelSize = 0
            self.__mode = QubCanvasScale.BOTH
            self.__unit = [(1e-3,'mm'),(1e-6,'\xb5m'),(1e-9,'nm')]
            self.__autorizeValues = [1,2,5,10,20,50,100,200,500]

            self.__canvas = canvas
    ##@brief set the display mode
    #
    # - if mode == QubCanvasScale::HORIZONTAL the scale will only be horizontal
    # - if mode == QubCanvasScale::VERTICAL the scale will only be vertical
    # - if mode == QubCanvasScale::BOTH the scale will be horizontal and vertical
    def setMode(self,mode) :
        self.__mode = mode
        self.update()

    ##@brief define autorized values to be display
    #
    #example: if you set [1,10,100] scale display can only be 1nm,10nm,100nm...
    #@param values list of posible values, values must be ascending sort 
    def setAutorizedValues(self,values) :
        self.__autorizeValues = values
        self.update()
    ##@brief set the size of the horizontal pixel
    #@param size values in meter of a pixel
    #@see setYPixelSize
    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0
        if(self.__globalShow and self.__mode & QubCanvasScale.HORIZONTAL and self.__xPixelSize) :
            self.__hText.show()
            self.__hLine.show()
            self.update()
        else:
            self.__hText.hide()
            self.__hLine.hide()
    ##@brief set the size of the vertical pixel
    #@param size values in meter of a pixel
    #@see setXPixelSize
    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0
        if self.__vText is not None :
            if (self.__globalShow and self.__mode & QubCanvasScale.VERTICAL and self.__yPixelSize) :
                self.__vText.show()
                self.__vLine.show()
                self.update()
            else :
                self.__vText.hide()
                self.__vLine.hide()

    def show(self) :
        self.__globalShow = True
        self.setXPixelSize(self.__xPixelSize)
        self.setYPixelSize(self.__yPixelSize)
        self.update()
        
    def hide(self) :
        self.__globalShow = False
        self.__vText.hide()
        self.__vLine.hide()
        self.__hText.hide()
        self.__hLine.hide()
    
    def update(self) :
        if self.__globalShow :
            (canvasX,canvasY) = (self.__canvas.width(),self.__canvas.height())
            if self.__scrollView is None :
                (viewSizeX,viewSizeY) = canvasX,canvasY
                (xOri,yOri) = 0,0
            else :
                (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
                (viewSizeX,viewSizeY) = (self.__scrollView.visibleWidth(),self.__scrollView.visibleHeight())

            (nbXPixel,nbYPixel) =  min(canvasX,viewSizeX),min(canvasY,viewSizeY)
            (widthUse,heightUse) = (nbXPixel,nbYPixel)

            if self.__matrix is None :
                (xOriCrop,yOriCrop) = 0,0
            else :
                (xOriCrop,yOriCrop) = self.__matrix.invert()[0].map(0,0)
                
            if self.__mode & QubCanvasScale.HORIZONTAL :
                nbXPixel /= 4 # 1/4 of image display
                if self.__matrix is None :
                    y1,y2 = 0,nbXPixel
                else:
                    dummy,y1 = self.__matrix.invert()[0].map(0,0)
                    dummy,y2 = self.__matrix.invert()[0].map(0,nbXPixel)
                unit,XSize = self.__getUnitNAuthValue((y2 - y1) * self.__xPixelSize)
                try:
                    nbXPixel = int(XSize * unit[0] / self.__xPixelSize)
                    if self.__matrix is not None :
                        (nbXPixel,dummy) = self.__matrix.map(nbXPixel + xOriCrop,0)
                    y0 = heightUse - 10 + yOri
                    self.__hLine.setPoints (14 + xOri,y0,nbXPixel + 14 + xOri,y0)
                    self.__hText.setText('%d %s' % (XSize,unit[1]))
                    rect = self.__hText.boundingRect()
                    xTextPos = nbXPixel + 14 - rect.width()
                    if xTextPos < 14 :
                        self.__hText.move(nbXPixel + 16 + xOri,y0 - rect.height() / 2)
                    else:
                        self.__hText.move(xTextPos + xOri,y0 - rect.height() - 2)
                except:
                    pass
                
            if self.__mode & QubCanvasScale.VERTICAL :
                nbYPixel /= 4
                if self.__matrix is None :
                    y1,y2 = 0,nbYPixel
                else:
                    dummy,y1 = self.__matrix.invert()[0].map(0,0)
                    dummy,y2 = self.__matrix.invert()[0].map(0,nbYPixel)
                unit,YSize = self.__getUnitNAuthValue((y2 - y1) * self.__yPixelSize)
                try:
                    nbYPixel = int(YSize * unit[0] / self.__yPixelSize)
                    if self.__matrix is not None :
                        (dummy,nbYPixel) = self.__matrix.map(0,nbYPixel + yOriCrop)
                    y0 = heightUse - 14 + yOri
                    self.__vLine.setPoints(10 + xOri,y0,10 + xOri,y0 - nbYPixel)
                    self.__vText.move(15 + xOri,y0 - nbYPixel)
                    self.__vText.setText('%d %s' % (YSize,unit[1]))
                except :
                    pass

            if self.__mode & QubCanvasScale.BOTH :
                hRect = self.__hText.boundingRect()
                vRect = self.__vText.boundingRect()
                
                vPoint = vRect.bottomRight()
                hPoint = hRect.topLeft()
                if hPoint.y() - vPoint.y() < 5 :
                    hLinePoint = self.__hLine.endPoint()
                    self.__hText.move(hLinePoint.x() + 2,hLinePoint.y() - hRect.height() / 2)

                    vLinePoint = self.__vLine.endPoint()
                    vTextRect = self.__vText.boundingRect()
                    self.__vText.move(vLinePoint.x() - 4,vLinePoint.y() - vTextRect.height())
            
    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def setMatrix(self,matrix) :
        self.__matrix = matrix

    def setCanvas(self,canvas) :
        self.__canvas = canvas
        self.__vText.setCanvas(canvas)
        self.__vLine.setCanvas(canvas)
        self.__hText.setCanvas(canvas)
        self.__hLine.setCanvas(canvas)

    def isVisible(self) :
        return self.__globalShow

    def pen(self) :
        return self.__pen

    def setPen(self,pen) :
        self.__hLine.setPen(pen)
        self.__hText.setColor(pen.color())

        self.__vLine.setPen(pen)
        self.__vText.setColor(pen.color())

    def __getUnitNAuthValue(self,size) :
        for unit in self.__unit :
                tmpSize = size / unit[0]
                if 1. < tmpSize < 1000. :
                    size = int(tmpSize)
                    aFindFlag = False
                    for i,autValue in enumerate(self.__autorizeValues) :
                        if size < autValue :
                            if i > 0 :
                                size = self.__autorizeValues[i - 1]
                            else :
                                size = autValue
                            aFindFlag = True
                            break
                        elif size == autValue:
                            aFindFlag = True
                            break
                    if not aFindFlag :
                        size = autValue
                    break
        return (unit,size)

##@brief Simple ruler
#@ingroup DrawingCanvasToolsContainer
#
#this ruler can manage one or two cursors
class QubCanvasRuler(qtcanvas.QCanvasRectangle) :
    HORIZONTAL,VERTICAL = range(2)
    MARGIN = 4
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        self.__scrollView = None
        if isinstance(canvas,QubCanvasRuler) :
            self.__positionMode = canvas._QubCanvasRuler__positionMode
            self.__scrollViewPercent = canvas._QubCanvasRuler__scrollViewPercent
            
            self.__limits = list(canvas._QubCanvasRuler__limits)
            self.__positions = list(canvas._QubCanvasRuler__positions)
            self.__textlimits = list(canvas._QubCanvasRuler__textlimits)
            self.__cursor = list(canvas._QubCanvasRuler__cursor)
            self.__label = list(canvas._QubCanvasRuler__label)

            self.__format = canvas._QubCanvasRuler__format
            self.__globalShow = canvas._QubCanvasRuler__globalShow

            self.__line = qtcanvas.QCanvasLine(canvas._QubCanvasRuler__line)
        else :
            self.__positionMode = QubCanvasRuler.HORIZONTAL
            self.__scrollViewPercent = 0.8

            self.__limits = []
            self.__positions = []
            self.__textlimits = []
            self.__cursor = []
            self.__label = []

            self.__format = '%.2f'
            self.__globalShow = False
            self.__line = qtcanvas.QCanvasLine(canvas)

            
    ##@brief set where the ruler will be display on the image
    #@param mode can be:
    # - <b>HORIZONTAL</b> horizontal on the image's top
    # - <b>VERTICAL</b> vertical on the image's right
    def setPositionMode(self,mode) :
        try:
            self.__positionMode = mode
            self.update()
        except:
            import traceback
            traceback.print_exc()
            
    ##@brief set text label
    def setLabel(self,cursorID,text) :
        if 0 <= cursorID <= 1 :
            while len(self.__label) <= cursorID :
                self.__createCursor()
            self.__label[cursorID].setText(text)

    ##@brief set the cursor position
    def setCursorPosition(self,cursorID,position) :
        if 0 <= cursorID <= 1 :
            while len(self.__positions) <= cursorID :
                self.__createCursor()
            self.__positions[cursorID] = position
            self.update()
        else:
            raise StandardError('can only manage one or two cursor')
    ##@brief set the limit of a cursor
    def setLimits(self,cursorID,low,high) :
        if 0 <= cursorID <= 1 :
            while len(self.__limits) <= cursorID :
                self.__createCursor()
            self.__limits[cursorID] = (low,high)
            self.__textlimits[cursorID][0].setText(self.__format % low)
            self.__textlimits[cursorID][1].setText(self.__format % high)
            self.update()
    
    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def show(self) :
        self.__globalShow = True
        self.update()
        for t in self.__textlimits :
            for widget in t: widget.show()
            
        for l in [self.__label,self.__cursor] :
            for w in l :
                w.show()
        self.__line.show()
        
    def hide(self) :
        self.__globalShow = False
        for t in self.__textlimits :
            for widget in t: widget.hide()
            
        for l in [self.__label,self.__cursor] :
            for w in l :
                w.hide()
        self.__line.hide()
        canvas = self.canvas()
        if canvas: canvas.update()
    
    def setPen(self,pen) :
        color = pen.color()
        for label in self.__label:
            label.setColor(color)
        for limits in self.__textlimits :
            for limitWidget in limits:
                limitWidget.setColor(color)
        self.__line.setPen(pen)
        for cursor in self.__cursor :
            brush = cursor.brush()
            brush.setColor(color)
            cursor.setBrush(brush)

    def setZ(self,zValue) :
        for label in self.__label:
            label.setZ(zValue)
        for limits in self.__textlimits :
            for limitWidget in limits:
                limitWidget.setZ(zValue)
        self.__line.setZ(zValue)
        for cursor in self.__cursor :
            cursor.setZ(zValue)
        
    def update(self) :
        try:
            if self.__globalShow and self.__limits :
                if self.__scrollView is None :
                    (useSizeX,useSizeY) = self.canvas().width(),self.canvas().height()
                    (xOri,yOri) = 0,0
                else :
                    (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
                    (useSizeX,useSizeY) = (min(self.canvas().width(),self.__scrollView.visibleWidth()),
                                           min(self.__scrollView.visibleHeight(),self.canvas().height()))

                rotationAngle = 0
                if self.__positionMode == QubCanvasRuler.VERTICAL :
                    rotationAngle = 90
                for l,h in self.__textlimits :
                    l.setRotation(rotationAngle)
                    h.setRotation(rotationAngle)
                for l in self.__label :
                    l.setRotation(rotationAngle)

                if self.__positionMode == QubCanvasRuler.HORIZONTAL :
                    textBBox = [(x.boundingRect(),y.boundingRect()) for x,y in self.__textlimits]
                    maxLowWidth,maxHighWidth = 0,0
                    for lowRect,highRect in textBBox :
                        maxLowWidth += lowRect.width()
                        maxHighWidth += highRect.width()
                    spareSize = useSizeX - maxLowWidth - maxHighWidth - QubCanvasRuler.MARGIN
                    spareSize *= self.__scrollViewPercent
                    centerX = (useSizeX / 2) + xOri
                    textHeight = self.__textlimits[0][0].boundingRect().height()
                    for i,(ll,hl) in enumerate(self.__textlimits) :
                        ll.move(centerX - (spareSize + QubCanvasRuler.MARGIN) / 2 - ll.boundingRect().width(),
                                QubCanvasRuler.MARGIN + yOri + (textHeight + QubCanvasRuler.MARGIN / 2) * i)
                        hl.move(centerX + (spareSize + QubCanvasRuler.MARGIN) / 2,
                                QubCanvasRuler.MARGIN + yOri + (textHeight + QubCanvasRuler.MARGIN / 2) * i)
                    y0Line = QubCanvasRuler.MARGIN + yOri + textHeight
                    self.__line.setPoints(centerX - spareSize / 2, y0Line,centerX + spareSize / 2,y0Line)
                    hTriangle = -textHeight
                    X0position = []

                    for pos,(ll,lh),cursor in zip(self.__positions,self.__limits,self.__cursor) :
                        diff = lh -ll
                        offsetPix = (pos - ll) * spareSize / diff
                        x0 = centerX - spareSize / 2 + offsetPix
                        y1Line = y0Line + hTriangle
                        xMin = x0 - hTriangle / 2
                        xMax = x0 + hTriangle / 2
                        array = qt.QPointArray()
                        array.putPoints(0,[xMin,y1Line,xMax,y1Line,x0,y0Line])
                        cursor.setPoints(array)
                        hTriangle = - hTriangle
                        X0position.append(x0)
                    labelOffset = (abs(hTriangle) + QubCanvasRuler.MARGIN) / 2
                    for label,x0,(ll,hl) in zip(self.__label,X0position,self.__textlimits) :
                        hlRect = hl.boundingRect()
                        label.move(x0 + labelOffset,hlRect.y())
                        labelRect = label.boundingRect()
                        if labelRect.intersects(hlRect) :
                            label.move(x0 - labelOffset - labelRect.width(),hlRect.y())
                else:
                    textBBox = [(x.boundingRect(),y.boundingRect()) for x,y in self.__textlimits]
                    maxLowHeight,maxHightHeight = 0,0
                    for lowRect,hightRect in textBBox :
                        maxLowHeight += lowRect.height()
                        maxHightHeight += hightRect.height()
                    spareSize = useSizeY - maxLowHeight - maxHightHeight - QubCanvasRuler.MARGIN
                    spareSize *= self.__scrollViewPercent
                    centerY = (useSizeY / 2) + yOri
                    textHeight = self.__textlimits[0][0].boundingRect().width()
                    for i,(ll,hl) in enumerate(self.__textlimits) :
                        ll.move(xOri + useSizeX - (QubCanvasRuler.MARGIN + (textHeight + QubCanvasRuler.MARGIN / 2) * i),
                                centerY - (spareSize + QubCanvasRuler.MARGIN) / 2 - ll.boundingRect().height())
                        hl.move(ll.x(),
                                centerY + (spareSize + QubCanvasRuler.MARGIN) / 2)
                    x0Line = xOri + useSizeX - (QubCanvasRuler.MARGIN + textHeight)
                    self.__line.setPoints(x0Line,centerY - spareSize / 2,x0Line,centerY + spareSize / 2)
                    hTriangle = textHeight
                    Y0position = []

                    for pos,(ll,lh),cursor in zip(self.__positions,self.__limits,self.__cursor) :
                        diff = lh - ll
                        offsetPix = (pos - ll) * spareSize / diff
                        y0 = centerY - spareSize / 2 + offsetPix
                        x1Line = x0Line + hTriangle
                        yMin = y0 - hTriangle / 2
                        yMax = y0 + hTriangle / 2
                        array = qt.QPointArray()
                        array.putPoints(0,[x1Line,yMin,x1Line,yMax,x0Line,y0])
                        cursor.setPoints(array)
                        hTriangle = -hTriangle
                        Y0position.append(y0)
                        
                    labelOffset = (abs(hTriangle) + QubCanvasRuler.MARGIN) / 2
                    for label,y0,(ll,hl) in zip(self.__label,Y0position,self.__textlimits) :
                        hlRect = hl.boundingRect()
                        label.move(hl.x(),y0 + labelOffset)
                        labelRect = label.boundingRect()
                        if labelRect.intersects(hlRect) :
                            label.move(hl.x(),y0 - labelOffset - labelRect.height())
                self.canvas().update()
        except:
            import traceback
            traceback.print_exc()
            
    def setCanvas(self,canvas) :
        qtcanvas.QCanvasRectangle.setCanvas(self,canvas)
        self.__line.setCanvas(canvas)
        for tup in self.__textlimits :
            for x in tup :
                x.setCanvas(canvas)
        for cur in self.__cursor :
            cur.setCanvas(canvas)
        for l in self.__label :
            l.setCanvas(canvas)
        

    def __createCursor(self) :
        try:
            canvas = self.canvas()
            self.__limits.append((0,1))
            self.__positions.append(0)
            self.__textlimits.append((QubCanvasText(canvas),QubCanvasText(canvas)))
            poly = qtcanvas.QCanvasPolygon(canvas)
            brush = poly.brush()
            brush.setStyle(qt.Qt.SolidPattern)
            poly.setBrush(brush)
            self.__cursor.append(poly)
            self.__label.append(QubCanvasText(canvas))
        except:
            import traceback
            traceback.print_exc()
            
##@brief drawing object to display two line with one same corner
#
#it is use for an angle measurement
#@ingroup DrawingCanvasToolsPolygon
class QubCanvasAngle(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)
        if isinstance(canvas,QubCanvasAngle) :
            if canvas._QubCanvasAngle__secLine is not None :
                self.__secLine = qtcanvas.QCanvasLine(canvas._QubCanvasAngle__secLine)
            else:
                self.__secLine = None
            self.__showFlag = canvas._QubCanvasAngle__showFlag
        else:
            self.__secLine = None
            self.__showFlag = False
        
    def move(self,x,y,point_id) :
        if point_id == 0 :
            if self.__secLine is None : # Init
                self.setPoints(x,y,x,y)
            else:                       # Modif
                for line in [self,self.__secLine] :
                    endPoint = line.endPoint()
                    line.setPoints(x,y,endPoint.x(),endPoint.y())
        elif point_id == 1 :
            firstPoint = self.startPoint()
            self.setPoints(firstPoint.x(),firstPoint.y(),x,y)
        else:
            if self.__secLine is None :
                self.__secLine = qtcanvas.QCanvasLine(self.canvas())
                self.__secLine.setPen(self.pen())
                if self.__showFlag :
                    self.__secLine.show()
            firstPoint = self.startPoint()
            self.__secLine.setPoints(firstPoint.x(),firstPoint.y(),x,y)
            return True                 # END OF POLYGONE
                    
    def show(self) :
        qtcanvas.QCanvasLine.show(self)
        if self.__secLine is not None :
            self.__secLine.show()
        self.__showFlag = True

    def hide(self) :
        qtcanvas.QCanvasLine.hide(self)
        if self.__secLine is not None :
            self.__secLine.hide()
        self.__showFlag = False
        canvas = self.canvas()
        if canvas: canvas.update()

    def setPen(self,pen) :
        qtcanvas.QCanvasLine.setPen(self,pen)
        if self.__secLine is not None :
            self.__secLine.setPen(pen)

    def setCanvas(self,aCanvas) :
        qtcanvas.QCanvasLine.setCanvas(self,aCanvas)
        if self.__secLine is not None :
            self.__secLine.setCanvas(aCanvas)

##@brief drawing object to display a N lines polygone
#
#it is use for an angle measurement
#@ingroup DrawingCanvasToolsPolygon
class QubCanvasCloseLinePolygone(qtcanvas.QCanvasPolygon) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasPolygon.__init__(self,canvas)
        if isinstance(canvas,QubCanvasCloseLinePolygone) :
            self.__points = list(canvas._QubCanvasCloseLinePolygone__points)
            self.__pen = canvas._QubCanvasCloseLinePolygone__pen
        else:
            self.__points = []
            self.__pen = qt.QPen()
            
    def move(self,x,y,point_id = 0) :
        while len(self.__points) <= point_id:
            self.__points.append((x,y))
        self.__points[point_id] = (x,y)
        self.setPoints(self._areaPoints())
        return False                    # NEVER END
    
    def pen(self) :
        return self.__pen
    def setPen(self,pen) :
        self.__pen = pen
        
    def drawShape(self,painter):
        if self.isVisible() and self.__points :
            painter.setPen(self.__pen)
            if len(self.__points) >= 2 :
                if len(self.__points) > 2 :
                    for (x1,y1),(x2,y2) in zip(itertools.islice(self.__points,0,None),
                                               itertools.islice(self.__points,1,None)) :
                        painter.drawLine(x1,y1,x2,y2)
                (fx,fy),(ex,ey) = self.__points[0],self.__points[-1]
                painter.drawLine(fx,fy,ex,ey)
            else: painter.drawPoint(*self.__points[0])
        
    def _areaPoints(self) :
        if self.canvas() and self.__points :
            if len(self.__points) > 2 :
                aP = qt.QPointArray(len(self.__points))
                for i,(x,y) in enumerate(self.__points) :
                    aP.setPoint(i,x,y)
            elif len(self.__points) == 2:
                aP = qt.QPointArray(4)
                x0,y0 = self.__points[0]
                x1,y1 = self.__points[1]
                aP.putPoints(0,[x0,y0,x1,y0,x1,y1,x0,y1])
            else:
                aP = qt.QPointArray(4)
                x,y = self.__points[0]
                aP.putPoints(0,[x-2,y-2,x+2,y-2,x+2,y+2,x-2,y+2])
        else:
            aP = qt.QPointArray(0)
        return aP
    
##@brief drawing object to display a grid
#
#@ingroup DrawingCanvasToolsPolygon
#@ingroup DrawingCanvasToolsRectangle
class QubCanvasGrid(qtcanvas.QCanvasRectangle) :
    class _translateFromFirstPoint :
        def __init__(self,cnt) :
            self.__cnt = weakref.ref(cnt)
        def calc(self,x,y,pointlist) :
            cnt = self.__cnt()
            if cnt:
                prevX,prevY = cnt.x(),cnt.y()
                points = numpy.array([[px,py] for px,py in pointlist])
                translation = numpy.matrix([x - prevX,y - prevY])
                points += translation
                return points
            
    class _rotateOrTranslateFromSecondPoint :
        def __init__(self,cnt) :
            self.__cnt = weakref.ref(cnt)
        def calc(self,x,y,pointlist) :
            cnt = self.__cnt()
            if cnt :
                x1,y1 = cnt.x(),cnt.y()
                X,Y = (x - x1,y - y1)
                width = math.sqrt(X ** 2 + Y ** 2)
                try:
                    angle = math.acos(X / width)
                except ZeroDivisionError :
                    angle = 0
                if y - y1 < 0:
                    angle = -angle
                height = cnt.height()
                points = numpy.array([[width,height]])
                rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                         [numpy.sin(-angle),numpy.cos(-angle)]])
                translation = numpy.matrix([x1,y1])
                points = points * rotation
                points += translation
                return numpy.array(points)
                

    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        if isinstance(canvas,QubCanvasGrid) :
            self.__angle = canvas._QubCanvasGrid__angle
            self.__nbPointAxis1 = canvas._QubCanvasGrid__nbPointAxis1
            self.__nbPointAxis2 = canvas._QubCanvasGrid__nbPointAxis2
            self.__points = list(canvas._QubCanvasGrid__points)
            self.__addRegionPoints = list(canvas._QubCanvasGrid__addRegionPoints)
            self.__minusRegionPoints = list(canvas._QubCanvasGrid__minusRegionPoints)
            self.__matrix = canvas._QubCanvasGrid__matrix
            self.__whole_region = canvas._QubCanvasGrid__whole_region
            self.__dirtyFlag = canvas._QubCanvasGrid__dirtyFlag
            self.__realGridRegion = canvas._QubCanvasGrid__realGridRegion
        else:
            self.__angle = 0
            self.__nbPointAxis1 = 0
            self.__nbPointAxis2 = 0
            self.__secondPoints = (0,0)
            self.__addRegionPoints = []
            self.__minusRegionPoints = []
            self.__matrix = None
            self.__whole_region = None
            self.__dirtyFlag = False
            self.__realGridRegion = None
        self.__show = False
        self.__oldMatrixValues = None
        self.__contraintAngle = QubAngleConstraint(self.__angle + 90)
        self.__translateFromFirstPoint = QubCanvasGrid._translateFromFirstPoint(self)
        self.__rotateOrTranslateFromSecondPoint = QubCanvasGrid._rotateOrTranslateFromSecondPoint(self)
        
    def move(self,x,y,point_id = 0) :
        if self.__show:                
            self.__dirtyFlag = True
            if point_id == 0:               # FIRST
                qtcanvas.QCanvasRectangle.move(self,x,y)
            elif point_id == 1:
                self.__secondPoints = (x,y)
                x1,y1 = self.x(),self.y()
                X,Y = (x - x1,y - y1)
                dist = math.sqrt(X ** 2 + Y ** 2)
                try:
                    self.__angle = math.acos(X / dist) * 180 / math.pi
                except ZeroDivisionError :
                    self.__angle = 0
                width = dist
                if y - y1 < 0 :
                    self.__angle = -self.__angle
                self.setSize (width,self.height())
                self.__contraintAngle.setAngle(self.__angle + 90)
            else:
                if abs(self.__angle) == 90 :
                    height = self.x() - x
                    if self.__angle < 0:
                        height = -height
                    self.setSize(self.width(),height)
                elif self.__angle == 180 or self.__angle == 0 :
                    height = y - self.y()
                    if self.__angle == 180:
                        height = -height
                    self.setSize(self.width(),height)
                else :
                    x1,y1 = self.__secondPoints
                    height = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
                    u = (x1 - self.x(),y1 - self.y())
                    v = (x - x1,y - y1)
                    #prod vect
                    z = u[0] * v[1] - u[1] * v[0]
                    if z < 0. :
                        height = -height
                    self.setSize(self.width(),height)
        
                return True

    def setNbPointAxis1(self,nbPoint) :
        self.__dirtyFlag = True
        self.__nbPointAxis1 = nbPoint
        
        self.update()
        canvas = self.canvas()
        if canvas:
            canvas.setAllChanged()
            canvas.update()

    def setNbPointAxis2(self,nbPoint) :
        self.__dirtyFlag = True
        self.__nbPointAxis2 = nbPoint
        
        self.update()
        canvas = self.canvas()
        if canvas:
            canvas.setAllChanged()
            canvas.update()

    def angle(self) :
        return self.__angle
       
    def setPointRegion(self,addPointList,minusPointlist) :
        self.__addRegionPoints = addPointList
        self.__minusRegionPoints = minusPointlist
        self.__dirtyFlag = True
        
        self.update()
        canvas = self.canvas()
        if canvas:
            canvas.setAllChanged()
            canvas.update()

    def setMatrix(self,matrix) :
        self.__matrix = matrix
        self.__dirtyFlag = True
        
    def setRealGridRegion(self,region) :
        self.__realGridRegion = region
        
    def show(self):
        self.__show = True
        qtcanvas.QCanvasRectangle.show(self)
        
        self.update()
        canvas = self.canvas()
        if canvas: canvas.update()
        
    def hide(self):
        self.__show = False
        qtcanvas.QCanvasRectangle.hide(self)
        
        self.update()
        canvas = self.canvas()
        if canvas: canvas.update()
        
    def drawShape(self,painter) :
        if self.__show:                
            wm = painter.worldMatrix()
            if self.__matrix :
                matrixValues = (self.__matrix.m11(),self.__matrix.m12(),
                                self.__matrix.m21(),self.__matrix.m22(),
                                wm.dx() + self.__matrix.dx(),wm.dy() + self.__matrix.dy())
                workingMatrix = qt.QWMatrix(*matrixValues)
            else:
                matrixValues = None
                workingMatrix = None
                
            if self.__dirtyFlag or matrixValues != self.__oldMatrixValues:
                self.__dirtyFlag = False


                self.__oldMatrixValues = tuple([x for x in matrixValues])

                self.__whole_region = None
                if self.__addRegionPoints or self.__minusRegionPoints:
                    if self.__addRegionPoints :
                        for pointsList in self.__addRegionPoints :
                            region = self.__createRegionFromPoint(pointsList,workingMatrix)
                            if self.__whole_region:
                                self.__whole_region = self.__whole_region.unite(region)
                            else:
                                self.__whole_region = region
                    if self.__whole_region :
                        for pointsList in self.__minusRegionPoints :
                            region = self.__createRegionFromPoint(pointsList,workingMatrix)
                            self.__whole_region = self.__whole_region.subtract(region)
                    else:
                        for pointList in self.__minusRegionPoints :
                            region = self.__createRegionFromPoint(pointList,workingMatrix)
                            if self.__whole_region :
                                self.__whole_region = self.__whole_region.unite(region)
                            else:
                                self.__whole_region = region

                    if self.__minusRegionPoints and not self.__addRegionPoints :
                        matrix = qt.QWMatrix(1,0,0,1,0,0)
                        matrix.translate(self.x(),self.y())
                        matrix.rotate(self.__angle)
                        matrix.translate(-self.x(),-self.y())
                        rect = matrix.map(self.rect())
                        rect.moveBy(wm.dx() - self.__matrix.dx(),wm.dy() - self.__matrix.dy())
                        region = qt.QRegion(rect)
                        self.__whole_region = region.subtract(self.__whole_region)

            if self.__angle :
                painter.translate(self.x(),self.y())
                painter.rotate(self.__angle)
                painter.translate(-self.x(),-self.y())

            qtcanvas.QCanvasRectangle.drawShape(self,painter)
            xOri = self.x() + self.width()
            painter.drawLine(xOri,self.y(),xOri + 20,self.y())
            painter.drawLine(xOri + 15,self.y() - 2,xOri + 20,self.y())
            painter.drawLine(xOri + 15,self.y() + 2,xOri + 20,self.y())

            yOri = self.y() + self.height()
            painter.drawLine(self.x(),yOri,self.x(),yOri + 20)
            painter.drawLine(self.x() - 2,yOri + 15,self.x(),yOri + 20)
            painter.drawLine(self.x() + 2,yOri + 15,self.x(),yOri + 20)
            if self.__whole_region is not None:
                painter.setClipRegion(self.__whole_region)

            h = self.height()
            w = self.width()
            if self.__nbPointAxis2 :
                yStep = float(self.height()) / self.__nbPointAxis2
                y0 = self.y()
                for i in range(self.__nbPointAxis2) :
                    x0,x1 = self.x(),self.x() + self.width()
                    painter.drawLine(x0,y0,x1,y0)
                    y0 += yStep

            if self.__nbPointAxis1:
                self.__pen = qt.QPen(qt.Qt.DotLine)
                self.__pen.setColor(painter.pen().color())
                painter.setPen(self.__pen)
                
                xStep = float(self.width()) / self.__nbPointAxis1
                x0 = self.x()
                for i in range(self.__nbPointAxis1) :
                    y0,y1 = self.y(),self.y() + self.height()
                    painter.drawLine(x0,y0,x0,y1)
                    x0 += xStep


            if self.__whole_region is not None: painter.setClipping(False)

            if self.__angle :
                painter.translate(self.x(),self.y())
                painter.rotate(-self.__angle)
                painter.translate(-self.x(),-self.y())
                                
    ##@brief set the drawing constraint
    #
    #Has the grid is a rectangle, the last point (3th) must be drawn to have a square angle
    def getConstraint(self) :
        return [(2,1,self.__contraintAngle)]
    ##@brief get the point modifier
    #
    #return a translate modifier for the first point
    #return a rotation modifier for the second point
    def getModifierConstraint(self) :
        return [(0,[1,2],self.__translateFromFirstPoint),
                (1,[2],self.__rotateOrTranslateFromSecondPoint)]
    
    def update(self) :
        self.__dirtyFlag = True
    
    # add by GB to remove arrow in top/right and down/left corner    
    def boundingRect(self) :
        rect = qtcanvas.QCanvasRectangle.boundingRect(self)        
        xOri = self.x() + self.width()
        rect = rect.unite(qt.QRect(xOri, self.y() - 2, 20, 4))
        yOri = self.y() + self.height()
        rect = rect.unite(qt.QRect(self.x()-2, yOri, 4, 20))
        
        matrix = qt.QWMatrix(1,0,0,1,0,0)
        matrix.translate(self.x()-2,self.y()-2)
        matrix.rotate(self.__angle)
        matrix.translate(-self.x()+2,-self.y()+2)
        
        rect1 = matrix.map(rect)
        
        return rect1.normalize()

    def __createRegionFromPoint(self,pointList,workingMatrix) :
        array = qt.QPointArray(len(pointList))
        for i,(x,y) in enumerate(pointList) :
            x1,y1 = workingMatrix.map(x,y)
            array.setPoint(i,x1,y1)
        return qt.QRegion(array)

##@brief a simple zoom dependent rectangle
#
#the width and height of this rectangle is the width and height of the full zoom (1:1)
class QubCanvasHomotheticRectangle(qtcanvas.QCanvasRectangle) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        if isinstance(canvas,QubCanvasHomotheticRectangle) :
            self.__width = canvas._QubCanvasHomotheticRectangle__width
            self.__height = canvas._QubCanvasHomotheticRectangle__height
        else:
            self.__width,self.__height = 1,1
        self.__dirtyFlag = True
        self.__oldMatrixValues = None
        self.__matrix = None
        
    def setWidthNHeight(self,width,height) :
        self.__width,self.__height = width,height
        self.__dirtyFlag = True
        
    def setMatrix(self,matrix) :
        self.__matrix = matrix
        self.__dirtyFlag = True

    def move(self,x,y) :
        rect = self.rect()
        rect.moveCenter(qt.QPoint(x,y))
        qtcanvas.QCanvasRectangle.move(self,rect.x(),rect.y())
        
    def drawShape(self,painter) :
        if self.__matrix :
            matrixValues = (self.__matrix.m11(),self.__matrix.m22()) # USE ONLY ZOOM
        else:
            matrixValues = None
        if self.__dirtyFlag or matrixValues != self.__oldMatrixValues:
            self.__dirtyFlag = False
            self.__oldMatrixValues = matrixValues
            p = qt.QPoint(self.__width,self.__height)
            if self.__matrix:
                matrix = qt.QWMatrix(self.__matrix.m11(),0,0,self.__matrix.m22(),0,0)
                p = matrix.map(p)
            qtcanvas.QCanvasRectangle.setSize(self,p.x(),p.y())
        qtcanvas.QCanvasRectangle.drawShape(self,painter)
            
class QubCanvasStripeH(qtcanvas.QCanvasRectangle) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        
    def drawShape(self,painter) :
        height = self.size().height()
        halfHeight = height >> 1
        canvasWidth = self.canvas().width()
        y = self.y()
        painter.drawLine(0, y + halfHeight, canvasWidth, y + halfHeight)
        painter.drawLine(0, y - halfHeight, canvasWidth, y - halfHeight)
        painter.setPen(qt.Qt.NoPen)
        painter.drawRect(0, y - halfHeight, canvasWidth, height)

    def setPen(self, pen):
        qtcanvas.QCanvasRectangle.setPen(self, pen)
        brush = self.brush()
        brush.setColor(pen.color())
        self.setBrush(brush)
        
    def boundingRect(self) :
        rect = qt.QRect(0,0,self.canvas().width(),self.size().height())
        rect.moveCenter(qt.QPoint(self.canvas().width() >> 1,self.y()))
        return rect

    def hide(self) :
        qtcanvas.QCanvasRectangle.hide(self)
        canvas = self.canvas()
        if canvas: canvas.update()
    
class QubCanvasStripeV(QubCanvasStripeH) :
    def __init__(self,canvas) :
        QubCanvasStripeH.__init__(self,canvas)

    def drawShape(self,painter) :
        width = self.size().width()
        halfWidth = width >> 1
        canvasHeight = self.canvas().height()
        x = self.x()
        painter.drawLine(x + halfWidth,0,x + halfWidth,canvasHeight)
        painter.drawLine(x - halfWidth,0,x - halfWidth,canvasHeight)
        painter.setPen(qt.Qt.NoPen)
        painter.drawRect(x - halfWidth, 0, width, canvasHeight)
       
    def boundingRect(self) :
        rect = qt.QRect(0,0,self.size().width(),self.canvas().height())
        rect.moveCenter(qt.QPoint(self.x(),self.canvas().height() >> 1))
        return rect

class QubCanvasRotationPoint(qtcanvas.QCanvasRectangle) :  
    def __init__(self, canvas) :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
                
    def drawShape(self,painter) :
        x = self.x()
        y = self.y()
        
        painter.drawArc(x-15, y-15, 30, 30, 800, 4400)
        painter.drawLine(x+6, y+8, x+11, y+8)
        painter.drawLine(x+11, y+8, x+11, y+13)

        painter.drawLine(x-10, y, x+10, y)
        painter.drawLine(x, y-10, x, y+10)
        
        #painter.drawArc(x-10, y-40, 20, 20, 2160, 4320)
        #painter.drawLine(x+6, y-32, x+6, y-37)
        #painter.drawLine(x+6, y-37, x+11, y-37)

       
    def boundingRect(self) :
        x = self.x()
        y = self.y()
        rect = qt.QRect(x-15, y-15, 80, 80)
        return rect

class QubCanvasRotationAxis(qtcanvas.QCanvasRectangle) :
    def __init__(self, canvas, drawing="HV") :
        qtcanvas.QCanvasRectangle.__init__(self,canvas)
        
        if drawing in ["H", "V", "HV"]:
            self.__drawingType = drawing
        else:
            self.__drawingType = "HV"

        self.__scrollview = None
        
    def drawShape(self,painter) :
        x = self.x()
        y = self.y()
        
        if self.__scrollview is not None:
            (useSizeX,useSizeY) = (min(self.canvas().width(),self.__scrollView.visibleWidth()),
                                   min(self.__scrollView.visibleHeight(),self.canvas().height()))
            (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
        else:
            (useSizeX,useSizeY) = self.canvas().width(),self.canvas().height()
            (xOri,yOri) = 0,0
        
        if self.__drawingType.rfind("H") != -1:
            painter.drawArc(xOri+useSizeX-60, y-10, 20, 20, 720, 4320)
            painter.drawLine(xOri+useSizeX-49, y+6, xOri+useSizeX-44, y+6)
            painter.drawLine(xOri+useSizeX-44, y+6, xOri+useSizeX-44, y+11)

            painter.drawLine(xOri, y, xOri+useSizeX, y)

        if self.__drawingType.rfind("V") != -1:
            painter.drawArc(x-10, yOri+40, 20, 20, 2160, 4320)
            painter.drawLine(x+6, yOri+48, x+6, yOri+43)
            painter.drawLine(x+6, yOri+43, x+11, yOri+43)

            painter.drawLine(x, yOri, x, yOri+useSizeX)
       
    def boundingRect(self) :
        if self.__scrollview is not None:
            (useSizeX,useSizeY) = (min(self.canvas().width(),self.__scrollView.visibleWidth()),
                                   min(self.__scrollView.visibleHeight(),self.canvas().height()))
            (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
        else:
            (useSizeX,useSizeY) = self.canvas().width(),self.canvas().height()
            (xOri,yOri) = 0,0
        rect = qt.QRect(xOri, yOri, xOri+useSizeX, yOri+useSizeX)
        return rect

    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def setDrawingManager(self,drawingManager) :
        drawingManager.setCustomModifierMethod(self.__getModifier)

    def __getModifier(self,drawingManager,xmouse,ymouse):
        x = self.x()
        y = self.y()
        
        if self.__scrollview is not None:
            (useSizeX,useSizeY) = (min(self.canvas().width(),self.__scrollView.visibleWidth()),
                                   min(self.__scrollView.visibleHeight(),self.canvas().height()))
            (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
        else:
            (useSizeX,useSizeY) = self.canvas().width(),self.canvas().height()
            (xOri,yOri) = 0,0
            
        vRectUp = qt.QRect(x-10, yOri, 20, y-10-yOri)
        vRectDown = qt.QRect(x-10, y+10, 20, useSizeY-10-y)
        if vRectUp.contains(xmouse, ymouse) or vRectDown.contains(xmouse, ymouse):
            return QubModifyAbsoluteAction(drawingManager,drawingManager.moveX,qt.QCursor(qt.Qt.SizeHorCursor))

        hRectLeft = qt.QRect(xOri, y-10-yOri, x-10-xOri, 20)
        hRectRight = qt.QRect(x+10, y-10, useSizeX-10-x, 20)
        if hRectLeft.contains(xmouse, ymouse) or hRectRight.contains(xmouse, ymouse):
            return QubModifyAbsoluteAction(drawingManager,drawingManager.moveY,qt.QCursor(qt.Qt.SizeVerCursor))

        rectCenter = qt.QRect(x-10, y-10, 20, 20)
        if rectCenter.contains(xmouse, ymouse):
            return QubModifyAbsoluteAction(drawingManager,drawingManager.move,qt.QCursor(qt.Qt.SizeAllCursor))

        return None
