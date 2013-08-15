import qt
import sys

from Qub.Widget.QubView import QubView

from Qub.Objects.QubPixmapDisplay import QubPixmapDisplay

##@brief The QubPixmapDisplayView allows to display QPixmap
#
#and put behavior
#(zoom,selection,print ....) on it using QubAction.
#It creates a instance of QubPixmapDisplay as QubView view.
#@ingroup ImageDisplayTools
#@see Qub::Widget::QubView::QubView
class QubPixmapDisplayView(QubView):
    def __init__(self,
                parent=None, name=None, actions=None):
        QubView.__init__(self, parent, name, 0)
        
        widget = QubPixmapDisplay(self, name)
        self.setView(widget)
        if actions is not None:
            self.addAction(actions)

    ##@brief Set the Qpixmap to be displayed and tells the
    #Qub::Objects::QubPixmapDisplay::QubPixmapDisplay widget to
    #display it
    #@param pixmap a qt.QPixmap at the request size
    #@param image the full qt.QImage 
    def setPixmap(self, pixmap,image):
        self.view().setPixmap(pixmap,image)
    
    ##@brief Change the scroll bar policy of the view (QubImage)
    #@param mode accepted values:
    # - <b>"Auto"</b> Scrollbars are shown if needed
    # - <b>"AlwaysOff"</b> Scrollbars are never displayed
    # - <b>"Fit2Screen"</b> Displayed pixmap size follow CanvasView size
    #keeping data pixmap ratio
    # - <b>"FullScreen"</b> Displayed pixmap size is CanvasView size without
    #keeping data pixmap ratio
    def setScrollbarMode(self, mode):
        self.view().setScrollbarMode(mode)
            
    def closeWidget(self):
        print "CloseWidget ImageView"
        self.view().closeWidget()

    ##@brief set the interface plug
    #
    #@param plug is a Qub::Objects::QubImage2Pixmap::QubImage2PixmapPlug
    def setPixmapPlug(self,plug) :
        self.view().setPixmapPlug(plug)
                      
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
from Qub.Data.Plug.QubPlug import QubPlug

class QubShm2Pixmap(QubPlug) :
    def __init__(self,aQubPixmapDisplayView,timeout = 1000) :
        QubPlug.__init__(self,timeout)
        self.__imageView = aQubPixmapDisplayView
        
    def update(self,specversion,specshm,data) :
##        (image_str,size,minmax) = spslut.transform(data,
##                                                   (1,0), (spslut.LINEAR, 3.0),
##                                                   "BGRX", spslut.GREYSCALE,1,(0,255))
        image = qt.QImage(image_str,size[0],size[1],32,None,0,
                          qt.QImage.IgnoreEndian)
        
        self.__imageView.setPixmap(qt.QPixmap(image))

class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        pixmap = qt.QPixmap(file)
        
        actions = []
        action = QubRectangleSelection(place="toolbar", show=1, group="selection")
        actions.append(action)
        action = QubLineSelection(place="statusbar",show=1,group="selection")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
        
        self.qubImageView=QubPixmapDisplayView(container, "Test QubPixmapDisplayView",
                                       pixmap, actions)
                    
        hlayout.addWidget(self.qubImageView)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubActionSet import QubRectangleSelection,QubLineSelection
    from Qub.Widget.QubAction import QubImageAction
    from Qub.Widget.QubProfiler import QubProfiler
    from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug
    from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap

    class _changeZoom :
        def __init__(self,action,display,plug) :
            self.__plug = plug
            self.__display = display
            self.__action = action
            qt.QObject.connect(action,qt.PYSIGNAL('RectangleSelected'),self.__cbk)

        def __cbk(self,x,y,width,height) :
            if width < 0 or height < 0 :
                x += width
                y += height
                width = -width
                height = -height
            
            viewport = self.__display.view().viewport()
            (view_w, view_h) = (viewport.width(), viewport.height())
            z = min(view_h / float(width),view_h / float(height))
            self.__plug.zoom().setRoiNZoom(x,y,width,height,z,z)
    class _followMullot(qt.QTimer,QubImageAction) :
        def __init__(self,label) :
            qt.QTimer.__init__(self)
            QubImageAction.__init__(self,autoConnect = True,place = None)
            self.__label = label
            self.__x,self.__y = (0,0)
            self.connect(self,qt.SIGNAL('timeout()'),self.__displayPos)

        def mouseMove(self,event) :
            self.__x,self.__y = self._qubImage.matrix().invert()[0].map(event.x(),event.y())
            if not self.isActive() :
                self.start(0)
        def __displayPos(self) :
            self.__label.setText('pos (%d,%d)' % (self.__x,self.__y))
            self.stop()
            
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    if len(sys.argv) < 2:
##        print "Give an image file name as argument"
##        sys.exit(1)
        from Qub.CTools import sps
        from Qub.Data.Source.QubSpecSource import getSpecVersions
        SpecVers = getSpecVersions()
        sebSpec = SpecVers.getObjects('seb')
        if(sebSpec) :
            imgArray = sebSpec.getObjects('image')
            if(imgArray) :
                window = qt.QMainWindow()
                layout = qt.QVBoxLayout(window)
                imgView = QubPixmapDisplayView(window,"Test")
                layout.addWidget(imgView)
                plug = QubShm2Pixmap(imgView)
                imgArray.plug(plug)
            else :
                print "Array not found"
        else :
            print "Spec version not found"
    else:
        action1 = QubRectangleSelection(place="toolbar",square=True, show=1, group="selection")
        window = qt.QDialog()
        posFullrezo = qt.QLabel(window)
        action2 = _followMullot(posFullrezo)
        fullrezo = QubPixmapDisplayView(window,None,[action1,action2])
        action1.setColor(qt.QColor('red'))
        plug = QubPixmapZoomPlug(fullrezo)

        posZoom = qt.QLabel(window)
        zoomedImage = QubPixmapDisplayView(window,None,[_followMullot(posZoom)])
        zoomPlug = QubPixmapZoomPlug(zoomedImage)
        
        im2Pixmap = QubImage2Pixmap()
        im2Pixmap.plug(plug)
        im2Pixmap.plug(zoomPlug)
        
        im = qt.QImage(sys.argv[1])
        im2Pixmap.putImage(im)

        cbk = _changeZoom(action1,zoomedImage,zoomPlug)
        
        layout = qt.QHBoxLayout(window,11,6,"layout")
        l1 = qt.QVBoxLayout()
        l1.addWidget(posFullrezo)
        l1.addWidget(fullrezo)

        l2 = qt.QVBoxLayout()
        l2.addWidget(posZoom)
        l2.addWidget(zoomedImage)
        
        layout.addItem(l1)
        layout.addItem(l2)
        
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
