import qt,qtcanvas

from Qub.Objects.QubEventMgr import QubEventMgr


##@brief This tool display canvas object as mosaic
#
#@ingroup ImageDisplayTools

class QubCanvasViewBase(qtcanvas.QCanvasView,QubEventMgr) :
    ##@param parent the parent widget
    #@param name widget name
    def __init__(self, parent=None, name=None):
        qtcanvas.QCanvasView.__init__(self, parent, name,qt.Qt.WNoAutoErase|qt.Qt.WStaticContents) 
                                           
        QubEventMgr.__init__(self)
        self.setFocusPolicy(qt.QWidget.WheelFocus)
        self._setScrollView(self)

        self._contextMenu = None
        
        self._matrix = qt.QWMatrix(1,0,0,1,0,0)
        self._matrix.setTransformationMode(qt.QWMatrix.Areas)

        self._cvs = _canvas(1,1)
        self.setCanvas(self._cvs)

        ##@brief By default set the scrollbar mode to automatic
        self._scrollMode = "Auto"
        self.setHScrollBarMode(self.Auto)
        self.setVScrollBarMode(self.Auto)

        self.viewport().setPaletteBackgroundColor(qt.QColor(qt.Qt.gray))
        self.viewport().setMouseTracking(True)

        self.setSizePolicy(qt.QSizePolicy.Ignored,
                           qt.QSizePolicy.Ignored)

        self.connect(self,qt.SIGNAL('contentsMoving (int, int)'),self._startIdle)

        self._idle = qt.QTimer(self)
        self.connect(self._idle,qt.SIGNAL('timeout()'),self.__emitViewPortUpdate)

        self._foregroundColor = qtcanvas.QCanvasView.foregroundColor(self)

    ##@name Mouse Events
    #@{

    ##@brief Mouse has moved
    #
    def contentsMouseMoveEvent(self, event):
        self._mouseMove(event)

    ##@brief Mouse has been pressed
    #    
    def contentsMousePressEvent(self,event) :
        if not self.hasFocus() :
            self.setFocus()

        self._mousePressed(event)

    ##@brief Mouse has been release
    #
    def contentsMouseReleaseEvent(self,event) :
        self._mouseRelease(event)
    ##@}
    #

    ##@brief right mouse button has been hit. make the context menu appears
    def contentsContextMenuEvent(self,event) :
        if self._contextMenu is not None :
            if event.reason() == qt.QContextMenuEvent.Mouse :
                self._contextMenu.exec_loop(qt.QCursor.pos())

    ##@name Key Event
    #@{

    ##@brief key pressed, dispatch
    def keyPressEvent(self,keyevent) :
        self._keyPressed(keyevent)

    ##@brief key release, dispatch
    def keyReleaseEvent(self,keyevent) :
        self._keyReleased(keyevent)
    ##@}

    ##@name Leave Events and resize event
    #@{

    ##@brief leave event dispatch
    def leaveEvent(self,event) :
        self._leaveEvent(event)

    def viewportResizeEvent(self,resize) :
        self._startIdle()

    ##@}
        
    def _startIdle(self,x = 0,y = 0) :
        if not self._idle.isActive() :
            self._idle.start(0)

    def __emitViewPortUpdate(self) :
        self._idle.stop()
        vp = self.viewport()
        self.emit(qt.PYSIGNAL("ContentViewChanged"), (self.contentsX(),self.contentsY(),vp.width(),vp.height()))
        self._update()

    def _realEmitActionInfo(self,text) :
        self.emit(qt.PYSIGNAL("ActionInfo"),(text,))

    ##@brief set a context menu on the QubPixmapDisplay
    #
    #It'll be called on the right click
    #@param menu is a QPopupMenu
    def setContextMenu(self, menu):
        self._contextMenu = menu

    ##@return scrollbarMode
    #
    def scrollbarMode(self) :
        return self._scrollMode

    ##@brief get the transformation matrix
    #
    #the matrix include the image zoom and the translation
    def matrix(self) :
        return self._matrix

    def zoomValue(self) :
        return self._matrix.m11(),self._matrix.m22()

    ##@brief get the default foreground color of the drawing vector
    def foregroundColor(self) :
        return self._foregroundColor
    ##@brief change the default foreground color of the drawing vector 
    def setForegroundColor(self,color) :
        self._foregroundColor = color
        self.emit(qt.PYSIGNAL("ForegroundColorChanged"), 
                  (self._foregroundColor,))


class _canvas(qtcanvas.QCanvas) :
    def __init__(self,*args) :
        qtcanvas.QCanvas.__init__(self,*args)
        self.__updateIdle = qt.QTimer(self)
        qt.QObject.connect(self.__updateIdle,qt.SIGNAL('timeout()'),self.__update)
        self.__lastImage = None
        
    def update(self) :
        if not self.__updateIdle.isActive():
            self.__updateIdle.start(0)

    def __update(self) :
        self.__updateIdle.stop()
        qtcanvas.QCanvas.update(self)

    def setBackgroundPixmap(self,pixmap,image = None) :
        qtcanvas.QCanvas.setBackgroundPixmap(self,pixmap)
        self.__lastImage = image

    def lastImage(self) :
        return self.__lastImage
