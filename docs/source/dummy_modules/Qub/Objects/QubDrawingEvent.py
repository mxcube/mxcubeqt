import weakref
import qt
##@defgroup DrawingEvent
#@brief Manager of the event behaviour
#
#They are the link between Qub::Objects::QubEventMgr::QubEventMgr and
#QubDrawingManager.

##@brief base class of drawing event
#@ingroup DrawingEvent
class QubDrawingEvent :
    def __init__(self,exclusive = True,exceptList = []) :
        self.__name = ''
        # exclusive with the name of other event
        self.__exceptList = exceptList
        # if False self.__exceptList is not considered
        self.__exclusive = exclusive
        
    def rawKeyPressed(self,keyevent) :
        pass
    def rawKeyReleased(self,keyevent) :
        pass
    
    def mousePressed(self,x,y) :
        pass
    def mouseReleased(self,x,y) :
        pass
    def mouseMove(self,x,y) :
        pass
    def mouseDblClick(self,x,y) :
        pass
    #@brief called when the event is removed from the polling loop
    def endPolling(self) :
        pass
    
    def setName(self,name) :
        self.__name = name
    def name(self) :
        return self.__name

    def setExclusive(self,aFlag) :
        self.__exclusive = bool(aFlag)
        
    def setExceptExclusiveListName(self,names) :
        self.__exceptList = names
        
    def exclusive(self) :
        if self.__exclusive :
            return self.__exceptList
        else :
            return False
    #@brief methode called when the event is just exclude or active again
    #@param aFlag :
    # - if <b>True</b> event is dub (exclude)
    # - else <b>False</b> event is active
    def setDubMode(self,aFlag) :
        pass                            # TODO

    #@return text information about the current action
    def getActionInfo(self) :
        return ''                       # MUST BE REDEFINE
    
class _DrawingEventNDrawingMgr(QubDrawingEvent):
    def __init__(self,aDrawingMgr,oneShot) :
        QubDrawingEvent.__init__(self)
        self._drawingMgr = weakref.ref(aDrawingMgr)
        self._oneShot = oneShot
    def getActionInfo(self) :
        d = self._drawingMgr()
        return d and d.getActionInfo() or None

    def rawKeyPressed(self,keyevent) :
        drawingMgr = self._drawingMgr()
        if drawingMgr:
            drawingMgr.rawKeyPressed(keyevent)
            
    def rawKeyReleased(self,keyevent) :
        drawingMgr = self._drawingMgr()
        if drawingMgr:
            drawingMgr.rawKeyReleased(keyevent)
    def setDubMode(self,aFlag) :
        d = self._drawingMgr()
        if d: d.setDubMode(aFlag)
            
##@brief A point event behaviour manager.
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on init
# -# move the drawing object on mouse move
# -# call the endDraw callback on mouse released
class QubMoveNPressed1Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        aDrawingMgr.show()

    def mouseReleased(self,x,y) :
        d = self._drawingMgr()
        if d :
            d.move(x,y)
            d.endDraw()
        return self._oneShot
    
    def mouseMove(self,x,y) :
        d = self._drawingMgr()
        if d :
           d.move(x,y)
        return False                    # NOT END
##@brief A point event behaviour manager.
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing after first click
# -# move the drawing object on mouse move and call the endDraw callback
class QubFollowMouseOnClick(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__mousePressed = False
        
    def mousePressed(self,x,y) :
        self.__mousePressed = True
        d = self._drawingMgr()
        if d :
            d.show()

    def mouseReleased(self,x,y) :
        self.mouseMove(x,y)
        self.__mousePressed = False
        return self._oneShot
    
    def mouseMove(self,x,y) :
        d = self._drawingMgr()
        if self.__mousePressed and d :
           d.move(x,y)
           d.endDraw()
        return False                    # NOT END
    
##@brief The default point event behaviour manager
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on mouse pressed
# -# call drawing object move until mouse released
# -# on mouse released call endDraw callback
class QubPressedNDrag1Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__buttonPressed = False
        
    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        d = self._drawingMgr()
        if d:
            d.show()
            d.move(x,y)
        return False                    # not END
        
    def mouseReleased(self,x,y) :
        if self.__buttonPressed:
            self.__buttonPressed = False
            d = self._drawingMgr()
            if d:
                d.move(x,y)
                d.endDraw()
            return self._oneShot
    
    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            d = self._drawingMgr()
            if d:
                d.move(x,y)
        return False                    # NOT END
##@brief Set 2 points with a pressed and drag
#@ingroup DrawingEvent
#
#The default line and rectangle behaviour manager
#Behaviour description:
# -# show drawing object on mouse pressed and set the
#absolute position on the first point
# -# move the second point until mouse button is released
# -# on mouse released call endDraw callback
class QubPressedNDrag2Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__buttonPressed = False

    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        d = self._drawingMgr()
        if d :
            d.moveFirstPoint(x,y)
            d.moveSecondPoint(x,y)
            d.show()
        return False                    # not END

    def mouseReleased(self,x,y) :
        if self.__buttonPressed:
            self.__buttonPressed = False
            d = self._drawingMgr()
            if d :
                d.moveSecondPoint(x,y)
                d.endDraw()
            return self._oneShot

    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            d = self._drawingMgr()
            if d :
                d.moveSecondPoint(x,y)
        return False                    # not END

##@brief Set 2 points with 2 click
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on first mouse pressed
# -# set the first point on first mouse released
# -# start moving the second point since mouse pressed
# -# set the second point on second mouse released and call endDraw callback
class Qub2PointClick(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__active = False
        self.__pointNb = 0

    def mousePressed(self,x,y) :
        self.__active = True
        d = self._drawingMgr()
        if d :
            if not self.__pointNb :         # first press
                d.moveFirstPoint(x,y)
                d.moveSecondPoint(x,y)
                d.show()
            else :                          # second press
                d.moveSecondPoint(x,y)
        return False
    
    def mouseReleased(self,x,y) :
        returnFlag = False
        d = self._drawingMgr()
        if d :
            if not self.__pointNb :
                d.moveFirstPoint(x,y)
                d.moveSecondPoint(x,y)
                self.__pointNb += 1
            else :
                d.moveSecondPoint(x,y)
                d.endDraw()
                self.__active = False
                self.__pointNb = 0
                returnFlag = self._oneShot
        return returnFlag
    
    def mouseMove(self,x,y) :
        if self.__active :
            d = self._drawingMgr()
            if d :
                if not self.__pointNb :
                    d.moveFirstPoint(x,y)
                    d.moveSecondPoint(x,y)
                else :
                    d.moveSecondPoint(x,y)
        return False

##@brief Set N point with N click
#@ingroup DrawingEvent
#
#This event behaviour manager is used with polygone.
#Behaviour description:
# -# the drawing object is shown on first mouse pressed
# -# on first mouse released set the first point absolute position
# -# check if it's the end of the draw by testing the return of
#the drawing manager's moving methode:
#    - if it's return <b>True</b> end of draw and call endDraw callback
#    - else go to next point
class QubNPointClick(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__pointNb = 0
        self.__active = False
        aDrawingMgr.reset()
        
    def mousePressed(self,x,y) :
        d = self._drawingMgr()
        if d :
            if self.__pointNb == 0 :
                d.initDraw()
                d.show()

            d.move(x,y,self.__pointNb)
            self.__active = True
            
    def mouseReleased(self,x,y) :
        d = self._drawingMgr()
        if d :
            aEndFlag = d.move(x,y,self.__pointNb)
            if aEndFlag :
                self.__pointNb = 0; self.__active = False
                d.endDraw()
            else: self.__pointNb += 1
            return aEndFlag and self._oneShot

    def mouseDblClick(self,x,y) :
        d = self._drawingMgr()
        if d : d.endDraw()
        return self._oneShot
    
    def mouseMove(self,x,y) :
        if self.__active :
            d = self._drawingMgr()
            if d : d.move(x,y,self.__pointNb)
            
##@brief Modify a point
#@ingroup DrawingEvent
#
#This is the default event behaviour manger to modify point
class QubModifyAbsoluteAction(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,modifyCBK,
                 cursor = qt.QCursor(qt.Qt.SizeAllCursor)) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
        self._cursor = cursor
        self._modify = modifyCBK
        self._dirtyFlag = False
        
    def __del__(self) :
        if self._dirtyFlag :
            d = self._drawingMgr()
            if d : d.endDraw()
        
    def setCursor(self,eventMgr) :
        eventMgr.setCursor(self._cursor)
        
    def mousePressed(self, x, y):
        self._dirtyFlag = True
        self._modify(x,y)
                
    def mouseMove(self, x, y):
        pass
                
    def mouseMovePressed(self, x, y):
        self._modify(x, y)
        
    def mouseReleased(self, x, y):
        self._modify(x, y)
        self._dirtyFlag = False
        d = self._drawingMgr()
        if d : d.endDraw()

##@brief Modify a point by relative moving
#@ingroup DrawingEvent
class QubModifyRelativeAction(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,modifyCBK,
                 cursor = qt.QCursor(qt.Qt.SizeAllCursor)) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
        self._cursor = cursor
        self._modify = modifyCBK
        self._dirtyFlag = False

    def __del__(self) :
        if self._dirtyFlag :
            d = self._drawingMgr()
            if d : d.endDraw()
        
    def setCursor(self,eventMgr) :
        eventMgr.setCursor(self._cursor)

    def mousePressed(self, x, y):
        self._dirtyFlag = True
        self.__oldX = x
        self.__oldY = y
                
    def mouseMove(self, x, y):
        pass

    def mouseMovePressed(self, x, y):
        self._modify(x - self.__oldX, y - self.__oldY)
        self.__oldX = x
        self.__oldY = y        
        
    def mouseReleased(self, x, y):
        self._modify(x - self.__oldX, y - self.__oldY)
        self._dirtyFlag = False
        d = self._drawingMgr()
        if d : d.endDraw()
