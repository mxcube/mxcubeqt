import weakref
import qt
import qtcanvas

from Qub.Objects.QubImage2Pixmap import QubImage2PixmapPlug

from Qub.Objects.QubCanvasViewBase import QubCanvasViewBase

##@defgroup ImageDisplayTools Tools to display Pixmap
#
#this is simple tools that can be link with DataProvidingTools

##@brief This tool display a Pixmap
#
#Display a Pixmap on a QCanvas background pixmap
#@ingroup ImageDisplayTools
class QubPixmapDisplay(QubCanvasViewBase) :
    ##@param parent the parent widget
    #@param name widget name
    def __init__(self, parent=None, name=None):
        QubCanvasViewBase.__init__(self,parent,name)
        
        self.__plug = None
              
        self.__lastImage = None
        
    ##@brief link this object with the pixmap object provider
    #
    #For now the pixmap object provider could be:
    # - QubImage2Pixmap
    #
    #@param plug the mother class of this object is QubImage2PixmapPlug
    #@see Qub::Objects::QubImage2Pixmap::QubImage2Pixmap
    #@see Qub::Objects::QubImage2Pixmap::QubImage2PixmapPlug
    def setPixmapPlug(self, plug):
        if self.__plug is not None :
            plug = self.__plug()
            if plug:
                plug.setEnd()
        self.__plug = weakref.ref(plug)
           
    ##@brief get the current pixmap of this object
    #@return the current display pixmap
    #
    #This methode is called before printing
    def getPPP(self):
        if self.__lastImage is not None:
            zoom = self.zoom()
            if zoom.isRoiZoom() :
                image = self.__lastImage.copy(*zoom.roi())
            else:
                image = self.__lastImage
            return qt.QPixmap(image)
        else:
            return qt.QPixmap()
        
    ##@brief get the in used zoom class
    #@see Qub::Objects::QubImage2Pixmap::QubImage2PixmapPlug::Zoom
    def zoom(self):
        if self.__plug :
            plug = self.__plug()
            if plug:
                return plug.zoom()
        
        raise StandardError("QubPixmapDisplay object not plugged")

    def zoomValue(self) :
        return self.zoom().zoom()
    ##@brief set the horizontal and vertical zoom
    #
    #@param zoomx the values of the horizontal zoom ie: zoomx == 1 == 100%
    #@param zoomy the values of the vertical zoom
    #@param keepROI if keepROI == False -> zoom on full image
    #               else the ROI is keept
    def setZoom(self, zoomx, zoomy,keepROI = False):
        try:
            if self.__plug :
                plug = self.__plug()
                if plug is None:
                    raise StandardError("QubPixmapDisplay object not plugged")

                if self._scrollMode in ["Auto", "AlwaysOff"]:
                    plug.zoom().setZoom(zoomx, zoomy,keepROI)
        except:
            import traceback
            traceback.print_exc()
    ##@brief Change the visible part of the pixmap.
    #
    #@param center:
    # - if True: the (x,y) point of the pixmap is moved to the center of
    #   the visible part of the QubPixmapDisplay Widget
    # - if False: the (x,y) point of the pixmap is moved to the upper
    #   left corner of the visible part of the QubPixmapDisplay object
    def setImagePos(x=0, y=0, center=False):
        (px, py) = self._matrix.map(x, y)
        
        if center:
            self.center(px, py)
        else:
            self.setContentsPos(px, py)
                        
    ##@brief set the the pixmap on the QubPixmapDisplay
    #
    #This is the only way to set a pixmap on QubPixmapDisplay
    #@warning this mathode should't be directly called, but via the plug
    #@see setPixmapPlug
    #@param pixmap the pixmap at the zoom asked
    #@param image the full size image
    def setPixmap(self, pixmap, image):
        self.__lastImage = image
        (cvs_w, cvs_h) = (self._cvs.width(), self._cvs.height())
        (pix_w, pix_h) = (pixmap.width(), pixmap.height())
        plug = self.__plug()
        if plug:
            zoomClass = plug.zoom()
            if self._scrollMode in ["Auto", "AlwaysOff"] or (not pix_w and not pix_h):
                if (cvs_w, cvs_h) != (pix_w, pix_h):
                    self._cvs.resize(pix_w, pix_h)
                    self._startIdle()
                self._cvs.setBackgroundPixmap(pixmap,image)
            else:
                zoom = zoomClass.zoom()
                (view_w, view_h) = (self.viewport().width(), self.viewport().height())
                if zoomClass.isRoiZoom() :
                    offx,offy,width,height = zoomClass.roi()
                    (im_w, im_h) = width,height
                else:
                    (im_w, im_h) = (image.width(), image.height())
                (w, h) = (int(im_w * zoom[0]), int(im_h * zoom[1]))

                if(abs(w - view_w) <= 1 and abs(h - view_h) <= 1 and self._scrollMode == "FillScreen" or
                   self._scrollMode == "Fit2Screen" and zoom[0] == zoom[1] and
                   (abs(w - view_w) <= 1 and h <= view_h or w <= view_w and abs(h - view_h) <= 1)) :
                    if (cvs_w, cvs_h) != (pix_w, pix_h):
                        self._cvs.resize(pix_w, pix_h)
                        self._startIdle()
                    self._cvs.setBackgroundPixmap(pixmap,image)
                else:
                    zoom_w = float(view_w) / im_w
                    zoom_h = float(view_h) / im_h
                    if self._scrollMode == "Fit2Screen":
                        zoom_val = min(zoom_w, zoom_h)
                        plug.zoom().setZoom(zoom_val, zoom_val,zoomClass.isRoiZoom())
                    else:
                        plug.zoom().setZoom(zoom_w, zoom_h,zoomClass.isRoiZoom())
                    self._startIdle()

            zoomx,zoomy = zoomClass.zoom()
            lastoffx,lastoffy = self._matrix.dx(),self._matrix.dy()
            self._matrix.setMatrix(zoomx, 0, 0, zoomy,0,0)
            if zoomClass.isRoiZoom() :
                offx,offy,width,height = zoomClass.roi()
                self._matrix = self._matrix.translate(-offx,-offy)
                lastoffx /= zoomx
                lastoffy /= zoomy
                if (offx,offy) != (-lastoffx,-lastoffy) :
                    self._startIdle()


    ##@brief Change the scroll bar policy
    #@param mode accepted string values:
    # -# <b>"Auto"</b>: Scrollbars are shown if needed
    # -# <b>"AlwaysOff"</b>: Scrollbars are never displayed
    # -# <b>"Fit2Screen"</b>: Displayed pixmap size follow CanvasView size 
    #                       keeping data pixmap ratio
    # -# <b>"FillScreen"</b>: Displayed pixmap size is CanvasView size without 
    #                       keeping data pixmap ratio
    def setScrollbarMode(self, mode):
        if mode in ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]:
            self._scrollMode = mode
            if self.__plug :
                plug = self.__plug()
                if mode == "Auto":
                    self.setHScrollBarMode(self.Auto)
                    self.setVScrollBarMode(self.Auto)

                elif mode == "AlwaysOff":
                    self.setHScrollBarMode(self.AlwaysOff)
                    self.setVScrollBarMode(self.AlwaysOff)

                elif mode == "Fit2Screen" or mode == "FillScreen":
                    self.setHScrollBarMode(self.AlwaysOff)
                    self.setVScrollBarMode(self.AlwaysOff)
                    if plug is not None :
                        plug.refresh()
##@brief this is the link plug for QubPixmapDisplay
#
#this the link of an object and QubPixmapDisplay
class QubPixmapZoomPlug(QubImage2PixmapPlug):
    def __init__(self, receiver) :
        QubImage2PixmapPlug.__init__(self)
        
        self._receiver = receiver
        receiver.setPixmapPlug(self)
        
    def setPixmap(self, pixmap, image) :
        self._receiver.setPixmap(pixmap, image)
        return False
            

class QubImageTest(qt.QMainWindow):
    class _timer(qt.QTimer) :
        def __init__(self,pixmapMgr) :
            qt.QTimer.__init__(self)
            import os
            import os.path
            self.connect(self,qt.SIGNAL('timeout()'),self.__putImage)
            self.images = []
            imagenames = []
            for root,dirs,files in os.walk('/bliss/users/petitdem/TestGui/Image') :
                for file_name in files :
                  basename,ext = os.path.splitext(file_name)
                  if ext == '.jpeg' :
                      imagenames.append(file_name)
                break
            for name in sorted(imagenames) :
                self.images.append(qt.QImage(os.path.join(root,name)))
            self.__pixmapManager = pixmapMgr
            self.id = 0
            self.start(0)

        def __putImage(self) :
            self.__pixmapManager.putImage(self.images[self.id % len(self.images)])
            self.id += 1

    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        self._scrollMode = ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.__qubpixmapdisplay = QubPixmapDisplay(container, "QubImage")
        self.__qubpixmapdisplay.setScrollbarMode("Auto")
        hlayout.addWidget(self.__qubpixmapdisplay)
    
        vlayout = qt.QHBoxLayout(hlayout)
    
        self.scrollBarWidget = qt.QButtonGroup(len(self._scrollMode), 
                                               qt.Qt.Vertical, container, 
                                               "Scrollbar mode")
        self.connect(self.scrollBarWidget, qt.SIGNAL("clicked(int)"),
                     self.setScrollbarMode)
        for name in self._scrollMode:
            scrollbarModeWidget = qt.QRadioButton(name, self.scrollBarWidget)
        
        vlayout.addWidget(self.scrollBarWidget)
        
        self.setCentralWidget(container)

        from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap
        self.__image2Pixmap = QubImage2Pixmap(True)
        plug = QubPixmapZoomPlug(self.__qubpixmapdisplay)
        self.__image2Pixmap.plug(plug)
        self.__timer = QubImageTest._timer(self.__image2Pixmap)

    def setScrollbarMode(self, item):
        self.__qubpixmapdisplay.setScrollbarMode(self._scrollMode[item])            



if  __name__ == '__main__':
    import sys
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubImageTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
