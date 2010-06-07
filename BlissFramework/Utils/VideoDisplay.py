#$Id: VideoDisplay.py,v 1.5 2005/01/11 12:44:16 guijarro Exp $
"""Helper module containing classes for video display""" 

__author__ = 'Matias Guijarro'
__version__ = '1.0'

from qt import *
from qtgl import *
from new import classobj
import logging
import cStringIO

import Image #Python Imaging Library

RGB_NUMCOLORS = 256*256*256

grayColorMap = []
for i in range(256):
    grayColorMap.append(qRgb(i, i, i))

def hasOpenGL():
    import BlissFramework
    return BlissFramework.isOpenGLEnabled() and QGLFormat.hasOpenGL()

class _VideoView(QFrame):
    """QWidget-derived class for video display"""
    def __init__(self, parent, width = 1, height = 1):
        """Constructor

        Parameters :
          parent -- the parent QObject
          width -- the desired width of the viewport
          height -- the desired height of the viewport"""
        QFrame.__init__(self, parent, None, Qt.WNoAutoErase)

        self.pixmap = None
        self.imgWidth = width
        self.imgHeight = height
        self._8bit = False

        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setMidLineWidth(0)
        self.setLineWidth(1)
        
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setFixedSize(width + 2*self.frameWidth(), height + 2*self.frameWidth())
               

    def width(self):
        return self.contentsRect().width()


    def height(self):
        return self.contentsRect().height()
    

    def imageWidth(self):
        return self.imgWidth


    def imageHeight(self):
        return self.imgHeight


    def imageZoomX(self):
        if self.imgWidth != 0:
            return self.contentsRect().width() / float(self.imgWidth)
       

    def imageZoomY(self):
        if self.imgHeight != 0:
            return self.contentsRect().height() / float(self.imgHeight)
           
           
    def mouseReleaseEvent(self, event):
        """Emit a signal when the image viewport is clicked

        Emitted signals :
          imageClicked (<x pos. in viewport>, <y pos. in viewport>) --"""
        x = event.x()
        y = event.y()

        try:
            zx = self.contentsRect().width() / float(self.imgWidth)
            zy = self.contentsRect().height() / float(self.imgHeight)

            self.emit(PYSIGNAL('imageClicked'), (x/zx, y/zy, x, y, ))
        except Exception,diag:
            logging.getLogger().warning('VideoDisplay: exception in mouseReleaseEvent (%s)' % str(diag))


    def setImageSize(self, width, height):
        """Set the viewport size

        Displayed images will be resized accordingly"""    
        self.setFixedSize(width + 2*self.frameWidth(), height + 2*self.frameWidth())
       

    def setImageData(self, data):
        """Set the image to display

        Parameters :
          data -- a valid image data string"""
        img = Image.open(cStringIO.StringIO(data))

        self.imgWidth, self.imgHeight = img.size

        try:
            self.pixmap = img.tostring('raw', 'RGBX')
        except:
            self.pixmap = img.tostring() #supposed 8 bit-depth
            self._8bit = True
        else:
            self._8bit = False

        self.update()
                   
        
    def drawContents(self, painter):
        """Paint the image previously set"""
        if self.pixmap is not None:
            if self._8bit:
                image = QImage(self.pixmap, self.imgWidth, self.imgHeight, 8, grayColorMap, 256, QImage.IgnoreEndian)
            else:
                image = QImage(self.pixmap, self.imgWidth, self.imgHeight, 32, None, RGB_NUMCOLORS, QImage.IgnoreEndian)
                
            if not image.isNull():
                if self.imgWidth != self.contentsRect().width() or self.imgHeight != self.contentsRect().height():
                    image = image.smoothScale(self.contentsRect().width(), self.contentsRect().height())
    
                painter.drawImage(self.contentsRect().x(), self.contentsRect().y(), image)

        self.customPaint(painter)


    def customPaint(self, painter):
        pass
        
    

if hasOpenGL():
    import OpenGL.GL as opengl
    
    class _GLVideoView(QGLWidget):
        """QGLWidget-derived class for OpenGL video display"""
        def __init__(self, parent, width = 1, height = 1):
            """Constructor

            Parameters :
              parent -- the parent QObject
              width -- the desired width of the OpenGL viewport
              height -- the desired height of the OpenGL viewport"""
            QGLWidget.__init__(self, parent, None, None, Qt.WNoAutoErase)
                    
            self.imgWidth = width
            self.imgHeight = height
            self.pixmap = None
            self._8bit = False
                     
            self.setCursor(QCursor(Qt.CrossCursor))
            self.setFixedSize(width, height)
            
            
        def initializeGL(self):
            """Initialize OpenGL. Set optimized settings for blitting"""
            self.qglClearColor(QColor(0, 0, 0))

            opengl.glDisable(opengl.GL_ALPHA_TEST)
            opengl.glDisable(opengl.GL_BLEND)
            opengl.glDisable(opengl.GL_DEPTH_TEST)
            opengl.glDisable(opengl.GL_DITHER)
            opengl.glDisable(opengl.GL_FOG)
            opengl.glDisable(opengl.GL_LIGHTING)
            opengl.glDisable(opengl.GL_LOGIC_OP)
            opengl.glDisable(opengl.GL_STENCIL_TEST)
            opengl.glDisable(opengl.GL_TEXTURE_1D)
            opengl.glDisable(opengl.GL_TEXTURE_2D)
            opengl.glPixelTransferi(opengl.GL_MAP_COLOR, opengl.GL_FALSE)
            opengl.glPixelTransferi(opengl.GL_RED_SCALE, 1)
            opengl.glPixelTransferi(opengl.GL_RED_BIAS, 0)
            opengl.glPixelTransferi(opengl.GL_GREEN_SCALE, 1)
            opengl.glPixelTransferi(opengl.GL_GREEN_BIAS, 0)
            opengl.glPixelTransferi(opengl.GL_BLUE_SCALE, 1)
            opengl.glPixelTransferi(opengl.GL_BLUE_BIAS, 0)
            opengl.glPixelTransferi(opengl.GL_ALPHA_SCALE, 1)
            opengl.glPixelTransferi(opengl.GL_ALPHA_BIAS, 0)


        def imageWidth(self):
            return self.imgWidth


        def imageHeight(self):
            return self.imgHeight


        def imageZoomX(self):
            self.makeCurrent()
            return opengl.glGetFloatv(opengl.GL_ZOOM_X)
           

        def imageZoomY(self):
            self.makeCurrent()
            return -opengl.glGetFloatv(opengl.GL_ZOOM_Y)
            
    
        def mouseReleaseEvent(self, event):
            """Emit a signal when the image viewport is clicked

            Emitted signals :
              imageClicked (<x pos. in image>, <y pos. in image>, <x pos. in viewport>, <y pos. in viewport>) --"""
            self.makeCurrent()
            
            x = event.x()
            y = event.y()
            zx = opengl.glGetFloatv(opengl.GL_ZOOM_X)
            zy = opengl.glGetFloatv(opengl.GL_ZOOM_Y)

            try:
                self.emit(PYSIGNAL('imageClicked'), (x/zx, -y/zy, x, y, ))
            except Exception,diag:
                logging.getLogger().warning('VideoDisplay: exception in mouseReleaseEvent (%s)' % str(diag))


        def setImageSize(self, width, height):
            """Set the OpenGL viewport size

            Displayed images will be resized accordingly"""
            self.setFixedSize(width, height)
       

        def setImageData(self, data):
            """Set the image to display

            Parameters :
              data -- a valid JPEG data string"""
            img = Image.open(cStringIO.StringIO(data))
                        
            width, height = img.size
            if width != self.imgWidth or height != self.imgHeight:
                self.imgWidth = width
                self.imgHeight = height
                QApplication.postEvent(self, QResizeEvent(QSize(self.width(), self.height()), QSize(self.width(), self.height())))

            try:
                self.pixmap = img.tostring('raw', 'BGRX')
            except:
                self.pixmap = img.tostring() #supposed 8 bit depth
                self._8bit = True
            else:
                self._8bit = False
                
            self.update()
        
      
        def resizeGL(self, width, height):
            """Resize the OpenGL viewport and set pixel zoom"""
            opengl.glViewport(0, 0, width, height)
            opengl.glRasterPos4f(-1.0, 1.0, 0.0, 1.0)
            x, y, width, height = opengl.glGetDoublev(opengl.GL_VIEWPORT)
            opengl.glPixelZoom(width/self.imgWidth,-height/self.imgHeight)
        
        
        def paintGL(self):
            """Paint the OpenGL viewport with the image previously set"""
            if self.pixmap is not None:
                if self._8bit:
                    opengl.glDrawPixels(self.imgWidth, self.imgHeight, opengl.GL_LUMINANCE, opengl.GL_UNSIGNED_BYTE, self.pixmap)
                else:
                    opengl.glDrawPixels(self.imgWidth, self.imgHeight, opengl.GL_RGBA, opengl.GL_UNSIGNED_BYTE, self.pixmap)
            

        def paintEvent(self, event):
            QGLWidget.paintEvent(self, event)

            self.customPaint(QPainter(self))


        def customPaint(self, painter):
            pass


if hasOpenGL():
    VideoDisplayWidget = classobj('VideoDisplayWidget', (_GLVideoView, ), {})
else:
    logging.getLogger().warning('No OpenGL support! Use standard video display instead.')
    VideoDisplayWidget = classobj('VideoDisplayWidget', (_VideoView, ), {})












