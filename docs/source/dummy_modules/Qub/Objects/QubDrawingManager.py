import math
import new
import weakref
import qt
from Qub.Objects.QubDrawingEvent import QubPressedNDrag1Point,QubPressedNDrag2Point,QubNPointClick
from Qub.Objects.QubDrawingEvent import QubModifyAbsoluteAction
from Qub.Objects.QubDrawingEvent import QubModifyRelativeAction
from Qub.Tools import QubWeakref
from Qub.CTools import polygone
##@defgroup DrawingManager Drawing object manager
#
#those class are used with the Qub::Objects::QubEventMgr::QubEventMgr to
#manage drawing on canvas

def QubAddDrawing(drawing, mngr_class, *args):
    """Return drawing manager"""
    objs = []
    mngr = mngr_class(drawing.canvas(), drawing.matrix())
    for obj_class in args:
        objs.append(obj_class(drawing.canvas()))
        mngr.addDrawingObject(objs[-1])
    drawing.addDrawingMgr(mngr)
    return (mngr,) + tuple(objs)

##@brief Base class of Drawing manager
#
#@ingroup DrawingManager
class QubDrawingMgr :
    def __init__(self,aCanvas,aMatrix) :
        self._matrix = aMatrix
        self._canvas = aCanvas
        self._drawingObjects = []
        self._foreignObjects = []       # Object from other Views
        self._eventMgr = None
        self._lastEvent = None
        self._oneShot = False
        self._drawingEvent = None
        self.__exclusive = True
        self.__exceptList = []          # event Name with is not exclusive
        self.__eventName = ''
        self.__cantBeModify = True
        self._endDrawCbk = None
        self._initDrawCbk = None
        self._dubModeCbk = None
        self._keyPressedCbk = None
        self._keyReleasedCbk = None
        self._clickedCbk = None
        self._actionInfo = ''
        
    def __del__(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.update()
            drawingObject.setCanvas(None)
        if self._canvas: self._canvas.update()
        
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.update()
                drawingObject.setCanvas(None)
            if canvas: canvas.update()
        
    def __nonzero__(self):
        return True

    def __getattr__(self, attr):
        if attr.startswith("__"):
            raise AttributeError, attr
   
        objects_to_call = self._drawingObjects
        for link,canvas,matrix,objectlist in self._foreignObjects:
            objects_to_call += objectlist
        objects_to_call = [x for x in objects_to_call if hasattr(x, attr)]

        if not objects_to_call:
            raise AttributeError, attr

        class calleach:
            def __init__(self, method, drawingObject,foreignObjects):
                self.method = method
                self.__drawingObjects = drawingObject
                self.__foreignObjects = foreignObjects
                
            def __call__(self, *args, **kwargs):
                objects_to_call = []
                objects_to_call.extend(self.__drawingObjects)
                for link,canvas,matrix,objectlist in self.__foreignObjects:
                    objects_to_call += objectlist
                objects_to_call = [x for x in objects_to_call if hasattr(x, self.method)]
                returnValues = []
                for obj in objects_to_call:
                    m = getattr(obj, self.method)
                    try:
                        returnValues.append(m(*args,**kwargs))
                    except Exception, err:
                        # error description is in 'err'
                        pass
                return returnValues
            
        m = calleach(attr,self._drawingObjects,self._foreignObjects)
        self.__dict__[attr]=m
        return m               
            
 
    ##@brief add a drawing canvas object in this manager
    #
    #all canvas object must have the same management
    #ie : if you add one point object, all other must be point too
    #@param aDrawingObject cant be directly a qtcanvas.QCanvasItem
    #@see DrawingCanvasTools
    def addDrawingObject(self,aDrawingObject) :
        try :
            self._drawingObjects.append(aDrawingObject)
            eventMgr = self._eventMgr and self._eventMgr() or None
            if hasattr(aDrawingObject,'setScrollView') and eventMgr is not None :
                aDrawingObject.setScrollView(eventMgr.scrollView())
            if hasattr(aDrawingObject,'setMatrix') :
                aDrawingObject.setMatrix(self._matrix)
                
            for link,canvas,matrix,objectlist in self._foreignObjects :
                newObject = aDrawingObject.__class__(None)
                newObject.setCanvas(canvas)
                if hasattr(newObject,'setScrollView') :
                    otherMgr = link().getOtherMgr(eventMgr)
                    newObject.setScrollView(otherMgr.scrollView())
                if hasattr(newObject,'setMatrix') :
                    otherMgr = link().getOtherMgr(eventMgr)
                    newObject.setMatrix(matrix)
                objectlist.append(newObject)
        except:
            import traceback
            traceback.print_exc()
    ##@brief remove a drawing object
    def removeDrawingObject(self,aDrawingObject) :
        aFindFlag = False
        for i,drawingObject in enumerate(self._drawingObjects):
            if aDrawingObject == drawingObject :
                aFindFlag = True
                break
        if aFindFlag :
            self._drawingObjects.pop(i)
            for link,canvas,matrix,objectlist in self._foreignObjects :
                objectlist.pop(i)

    ##@brief hide all canvas item
    def hide(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.hide()
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.hide()
    ##@brief show all canvas item
    def show(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.show()
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.show()

    def setZ(self,layer) :
        for drawingObject in self._drawingObjects :
            drawingObject.setZ(layer)
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.setZ(layer)

    ##@brief authorize the user to modify the drawing manager ie :
    # - resized,moved....
    #
    #@param aFlag default True
    # - if <b>True</b> this object can be modify with SHIFT + LEFT CLICK
    # - else <b>False</b> can't be modify
    def setCanBeModify(self,aFlag) :
        self.__cantBeModify = aFlag
        
    ##@brief disconnect the event at the end of procedure
    #
    #otherwise the event is keep in the event loop as soon as the startDrawing is called
    #@param aFlag default = False
    # - if <b>True</b> disconnect the event at the end of procedure
    # - else <b> False</b> keep in the loop
    def setAutoDisconnectEvent(self,aFlag) :
        self._oneShot = aFlag

    ##@brief set the exclusivity of the event
    #
    #@param aFlag :
    # - if <b>True</b> (default) the event loop will exclude every other
    #event which is not in the ExceptExclusiveList when
    #startDrawing is called
    # - else <b>False</b> not exclusive
    #
    #@see setExceptExclusiveListName
    #@see setEventName
    def setExclusive(self,aFlag) :
        self.__exclusive = bool(aFlag)
        
    ##@brief set the list of event names that is not exclusive with this drawing
    #@param names name list of event.. ['helpLines','control',...]
    #@see setEventName
    #@see setExclusive
    def setExceptExclusiveListName(self,names) :
        self.__exceptList = names

    ##@brief the name of the event, its use to make the exclusion
    #@param name the name of the event
    #@see setExclusive
    #@see setExceptExclusiveListName
    def setEventName(self,name) :
        self.__eventName = name
    ##@brief set the color of all the drawing objects
    #@param color is a qt.QColor
    def setColor(self,color) :
        try:
            for drawingObject in self._drawingObjects :
                pen = drawingObject.pen()
                pen.setColor(color)
                drawingObject.setPen(pen)
                drawingObject.update()
            if self._canvas: self._canvas.update()
            
            for link,canvas,matrix,objectlist in self._foreignObjects :
                for drawingObject in objectlist :
                    pen = drawingObject.pen()
                    pen.setColor(color)
                    drawingObject.setPen(pen)
                if canvas: canvas.update()
        except:
            import traceback
            traceback.print_exc()
    ##@brief set the pen of all the drawing object
    #@param pen is a qt.QPen
    def setPen(self,pen) :
        for drawingObject in self._drawingObjects :
            drawingObject.setPen(pen)
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.setPen(pen)
    ##@brief start the drawing procedure
    #
    #, now this object will listen events -> mouse move,click
    def startDrawing(self) :
        eventMgr = self._eventMgr and self._eventMgr() or None
        if eventMgr is not None :
            self._lastEvent = self._getDrawingEvent()
            if self._lastEvent is not None :
                self._lastEvent.setExceptExclusiveListName(self.__exceptList)
                self._lastEvent.setExclusive(self.__exclusive)
                self._lastEvent.setName(self.__eventName)
                eventMgr.addDrawingEvent(self._lastEvent)

    ##@brief ends the events listening
    #@see startDrawing
    def stopDrawing(self) :
        self._lastEvent = None
                    
    ##@brief set the end callback drawing procedure
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,Qub::Objects::QubDrawingMgr::QubDrawingMgr)</b>
    def setEndDrawCallBack(self,cbk) :
        self._endDrawCbk = QubWeakref.createWeakrefMethod(cbk)

    ##@brief set a callback for the init draw
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,Qub::Objects::QubDrawingMgr::QubDrawingMgr)</b>
    def setInitDrawCallBack(self,cbk) :
        self._initDrawCbk = QubWeakref.createWeakrefMethod(cbk)

    ##@brief set a callback for the dub mode
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,drawingManager,aFlag)</b> if the flag is True the DrawingManager is Dub
    #It doesn't receved event anymore
    def setDubModeCallBack(self,cbk) :
        self._dubModeCbk = QubWeakref.createWeakrefMethod(cbk)
    ##@brief set the keyPressed callback
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,keyEvent)</b>
    def setKeyPressedCallBack(self,cbk) :
        self._keyPressedCbk = QubWeakref.createWeakrefMethod(cbk)

    ##@brief set the keyPressed callback
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,keyEvent)</b>
    def setKeyReleasedCallBack(self,cbk) :
        self._keyReleasedCbk = QubWeakref.createWeakrefMethod(cbk)

    ##@brief set the clicked callback
    #
    #@param cbk is the addresse of a function or a methode with this signature
    #<b>cbk(self,drawingManager)</b>
    def setClickedCallBack(self,cbk) :
        self._clickedCbk = QubWeakref.createWeakrefMethod(cbk)
        
    ##@brief change the drawing procedure beavior
    ##@see Qub::Objects::QubDrawingEvent::QubDrawingEvent
    def setDrawingEvent(self,event) :
        self._drawingEvent = event
        
    

    ##@brief get action information
    #@return human text readable action's information
    def getActionInfo(self) :
        return self._actionInfo

    ##@brief Set the information about the action
    #@param text human readable action information
    def setActionInfo(self,text) :
        self._actionInfo = text
        
    ##@return the bounding rect of all drawing
    def boundingRect(self) :
        returnRect = None
        for drawingObject in self._drawingObjects :
            objectRect = drawingObject.boundingRect()
            if returnRect is not None :
                returnRect = objectRect.unite(returnRect)
            else :
                returnRect = objectRect
        return returnRect
        
    ##@brief the end callback procedure (intern use)
    def endDraw(self) :
        if self._endDrawCbk is not None :
            self._endDrawCbk(self)
    ##@brief the init callback procedure (intern use)
    def initDraw(self) :
        if self._initDrawCbk is not None :
            self._initDrawCbk(self)
    ##@brief the dub callback procedure (intern use)
    def setDubMode(self,aFlag) :
        if self._dubModeCbk is not None:
            self._dubModeCbk(self,aFlag)
    ##@brief key pressed callback
    def rawKeyPressed(self,keyevent) :
        if self._keyPressedCbk:
            self._keyPressedCbk(self, keyevent)
    ##@brief key pressed callback
    def rawKeyReleased(self,keyevent) :
        if self._keyReleasedCbk:
            self._keyReleasedCbk(self, keyevent)
    ##@brief object was clicked
    def wasClicked(self) :
        if self._clickedCbk:
            self._clickedCbk(self)
    ##@name Has to or may be redefine in subclass
    #@{
    #
    ##@brief all drawingObject should be update
    def update(self) :
        raise StandardError('update has to be redifined')
    ##@brief reset all the points in the container
    #
    def reset(self) :
        pass
    ##@return the drawing procedure beavior
    ##@see setDrawingEvent
    def _getDrawingEvent(self) :
        return self._drawingEvent(self,self._oneShot)

    ##@return a class to modify graphicaly this object
    #@see Qub::Objects::QubModifyAbsoluteAction::QubModifyAbsoluteAction
    #@see Qub::Objects::QubModifyRelativeAction::QubModifyRelativeAction
    def _getModifyClass(self,x,y) :
        return None
    ##@}
    
    #@name Call by the event loop
    #@{
    #
    
    def getModifyClass(self,x,y) :
        if self.__cantBeModify :
            aVisibleFlag = False
            for drawingObject in self._drawingObjects :
                if drawingObject.isVisible() :
                    aVisibleFlag = True
                    break
            if aVisibleFlag :
                return self._getModifyClass(x,y)

    def setEventMgr(self,anEventMgr) :
        self._eventMgr = weakref.ref(anEventMgr)
        for drawingObject in self._drawingObjects :
            if hasattr(drawingObject,'setScrollView') :
                drawingObject.setScrollView(anEventMgr.scrollView())
    ##@brief add a link between two event manager
    #@see __linkRm
    def addLinkEventMgr(self,aLinkEventMgr) :
        try:
            eventMgr = self._eventMgr and self._eventMgr() or None
            if eventMgr is None : return
            canvas,matrix = aLinkEventMgr.getCanvasNMatrix(eventMgr)
            newObjects = []
            for drawing in self._drawingObjects :
                nObject = drawing.__class__(None)
                nObject.setCanvas(canvas)
                if hasattr(nObject,'setScrollView') :
                    otherMgr = aLinkEventMgr.getOtherMgr(eventMgr)
                    nObject.setScrollView(otherMgr.scrollView())
                if hasattr(nObject,'setMatrix') :
                    otherMgr = aLinkEventMgr.getOtherMgr(eventMgr)
                    nObject.setMatrix(matrix)
                newObjects.append(nObject)
            self._foreignObjects.append((weakref.ref(aLinkEventMgr,QubWeakref.createWeakrefMethod(self.__linkRm)),
                                         canvas,matrix,newObjects))
        except:
            import traceback
            traceback.print_exc()
    ##@}

    ##@brief remove link between two event manager
    #@see addLinkEventMgr
    def __linkRm(self,linkref) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            if link == linkref :
                for drawingObject in objectlist :
                    drawingObject.setCanvas(None)
                self._foreignObjects.remove((link,canvas,matrix,objectlist))
                break

##@brief this class is a container of stand alone drawing object
#
#This class should be used with stand alone DrawingObject
#@ingroup DrawingManager
class QubContainerDrawingMgr(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)

    def update(self) :
        try :
            for drawingObject in self._drawingObjects :
                drawingObject.update()
            if self._canvas: self._canvas.update()
            
            for link,canvas,matrix,objectlist in self._foreignObjects :
                for drawingObject in objectlist :
                    drawingObject.update()
                if canvas: canvas.update()
        except:
            import traceback
            traceback.print_exc()
            
    def _getDrawingEvent(self) :
        return None                     # just in case that someone call startDrawing

##@brief This class manage all the drawing object
#that can be define with one point
#@ingroup DrawingManager
class QubPointDrawingMgr(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x,self._y = 0,0
        self._drawingEvent = QubPressedNDrag1Point
        self.__width,self.__height = -1,-1
        self.__authorizedWidthResize = False
        self.__authorizedHeightResize = False
        self.__homotheticFlag = False
        
    ##@brief set the absolute position (x,y)
    #@param x horizontal position
    #@param y vertical position
    def setPoint(self,x,y) :
        self._x,self._y = x,y
        self.update()
    ##@return the horizontal and vertical position in tuple
    def point(self) :
        return (self._x,self._y)
    ##@brief set the size of drawing objects
    #
    #@param width the width of objects
    #@param height the height of objects
    def setSize(self,width,height) :
        self.__width,self.__height = width,height
        self.update()
    ##@brief return the objects size
    #
    #@return width and height as a tuple
    def size(self) :
        return self.__width,self.__height

    ##@brief set if objects are homothetic
    def setHomothetic(self,flag) :
        self.__homotheticFlag = flag
        self.update()

    ##@brief change the height resize capability
    #
    def setAuthorizedHeightResize(self,flag) :
        self.__homotheticFlag = self.__homotheticFlag or flag
        self.__authorizedHeightResize = flag
        if flag : self.setCanBeModify(True)

    ##@brief change the width resize capability
    #
    def setAuthorizedWidthResize(self,flag) :
        self.__homotheticFlag = self.__homotheticFlag or flag
        self.__authorizedWidthResize = flag
        if flag : self.setCanBeModify(True)
        
    ##@name Internal loop event call
    #@{
    #
    #@brief move to x,y position
    def move(self,x,y) :
        if self._matrix is not None :
            self._x,self._y = self._matrix.invert()[0].map(x,y)
        else:
            self._x,self._y = (x,y)

        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject()

    def xLeft(self,x,y) :
        rect = self.boundingRect()
        rect.setX(x)
        if self._matrix is not None:
            rect = self._matrix.invert()[0].mapRect(rect)
        self.setSize(rect.width(),rect.height())
        self.update()

    def xRight(self,x,y) :
        rect = self.boundingRect()
        rect.setRight(x)
        if self._matrix is not None:
            rect = self._matrix.invert()[0].mapRect(rect)
        self.setSize(rect.width(),rect.height())
        self.update()
        
    def yTop(self,x,y) :
        rect = self.boundingRect()
        rect.setY(y)
        if self._matrix is not None:
            rect = self._matrix.invert()[0].mapRect(rect)
        self.setSize(rect.width(),rect.height())
        self.update()

    def yBottom(self,x,y) :
        rect = self.boundingRect()
        rect.setBottom(y)
        if self._matrix is not None:
            rect = self._matrix.invert()[0].mapRect(rect)
        self.setSize(rect.width(),rect.height())
        self.update()
        
    def update(self) :
        if self._matrix is not None :
            x,y = self._matrix.map(self._x,self._y)
        else :
            x,y = self._x,self._y

        if(self.__homotheticFlag and self._matrix and
           self.__width > -1 and self.__height > -1):
            width,height = self._matrix.invert()[0].map(self.__width,self.__height)
        else:
            width,height = self.__width,self.__height

            
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
            if width > -1 and height > -1 and hasattr(drawingObject,'setSize') :
                drawingObject.setSize(width,height)
                
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject(width,height)
        
    def _getModifyClass(self,x,y) :
        modifyClass = None
        rect = self.boundingRect()

        if self.__authorizedWidthResize :
            if rect.contains(x,y) :
                xFirst,xLast = rect.x(),rect.x() + rect.width()
                if (xFirst - 2) <= x <= (xFirst + 2):
                    modifyClass = QubModifyAbsoluteAction(self,self.xLeft,qt.QCursor(qt.Qt.SizeHorCursor))
                elif (xLast - 2) <= x <= (xLast + 2):
                    modifyClass = QubModifyAbsoluteAction(self,self.xRight,qt.QCursor(qt.Qt.SizeHorCursor))

        if not modifyClass and self.__authorizedHeightResize:
            if rect.contains(x,y) :
                yFirst,yLast = rect.y(),rect.y() + rect.height()
                if (yFirst - 2) <= y <= (yFirst + 2):
                    modifyClass = QubModifyAbsoluteAction(self,self.yTop,qt.QCursor(qt.Qt.SizeVerCursor))
                elif (yLast - 2) <= y <= (yLast + 2):
                    modifyClass = QubModifyAbsoluteAction(self,self.yBottom,qt.QCursor(qt.Qt.SizeVerCursor))

        if not modifyClass:
            if rect.contains(x,y) : 
                modifyClass = QubModifyAbsoluteAction(self,self.move)
        return modifyClass

    def _drawForeignObject(self,width = -1,height = -1) :
        try:
            for link,canvas,matrix,objectlist in self._foreignObjects :
                x,y = self._x,self._y
                if matrix is not None :
                    x,y = matrix.map(x,y)
                for drawingObject in objectlist :
                    drawingObject.move(x,y)
                    if width > -1 and height > -1 and hasattr(drawingObject,'setSize'):
                        drawingObject.setSize(width,height)
                if canvas: canvas.update()
        except:
            import traceback
            traceback.print_exc()
    ##@}
            
##@brief this class manage all drawing object
#that can be define with a line
#@ingroup DrawingManager
class QubLineDrawingMgr(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x1,self._y1 = 0,0
        self._x2,self._y2 = 0,0
        self._drawingEvent = QubPressedNDrag2Point
        #contraint object (default) None ==  no constraint
        self.__contraintObject = None

    ##@brief set absolute position of first and second point
    #@param x1 horizontal first point
    #@param y1 vertical first point
    #@param x2 horizontal second point
    #@param y2 vertical second point
    def setPoints(self,x1,y1,x2,y2) :
        self._x1,self._y1 = x1,y1
        self._x2,self._y2 = x2,y2
        self.update()
    ##@return absolute position of first and second point like (x1,y1,x2,y2)
    def points(self) :
        return (self._x1,self._y1,self._x2,self._y2)

    ##@brief set constraint object
    #@see 
    def setConstraint(self,constraintObject) :
        self.__contraintObject = constraintObject
        
    ##@name internal LOOP EVENT CALL
    #@{
    #
    ##@brief callback to move first point
    def moveFirstPoint(self,x,y) :
        if self._matrix is not None :
            self._x1,self._y1 = self._matrix.invert()[0].map(x,y)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else:
            self._x1,self._y1 = x,y
            x2,y2 = self._x2,self._y2


        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x,y,x2,y2)
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject()
        
    ##@brief callback to move second point
    def moveSecondPoint(self,x,y) :
        if self._matrix is not None :
            self._x2,self._y2 = self._matrix.invert()[0].map(x,y)
            x1,y1 = self._matrix.map(self._x1,self._y1)
        else:
            self._x2,self._y2 = x,y
            x1,y1 = self._x1,self._y1

        if self.__contraintObject is not None :
            dummy,dummy,self._x2,self._y2 = self.__contraintObject.calc(self._x1,self._y1,self._x2,self._y2)
            if self._matrix is not None :
                x,y = self._matrix.map(self._x2,self._y2)
            else:
                x,y = self._x2,self._y2

        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x,y)
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject()

    def update(self) :
        if self._matrix is not None :
            x1,y1 = self._matrix.map(self._x1,self._y1)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
            
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x2,y2)

        if self._canvas: self._canvas.update()

        self._drawForeignObject()
    ##@brief get a modify class to move or resize the line
    def _getModifyClass(self,x,y) :
        (x1,y1,x2,y2) = self._x1,self._y1,self._x2,self._y2
        if self._matrix is not None :
            x1,y1 = self._matrix.map(x1,y1)
            x2,y2 = self._matrix.map(x2,y2)
            
        if(abs(x - x1) < 5 and abs(y - y1) < 5) :
            return QubModifyAbsoluteAction(self,self.moveFirstPoint)
        elif(abs(x - x2) < 5 and abs(y - y2) < 5) :
            return QubModifyAbsoluteAction(self,self.moveSecondPoint)

    ##@brief methode to draw object from other canvas
    def _drawForeignObject(self) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
            if matrix is not None :
                x1,y1 = matrix.map(x1,y1)
                x2,y2 = matrix.map(x2,y2)
                
            for drawingObject in objectlist :
                drawingObject.setPoints(x1,y1,x2,y2)
            if canvas: canvas.update()
    ##@}

##@brief manage all object that can be define with a 2 points rectangle
#@ingroup DrawingManager
class Qub2PointSurfaceDrawingMgr(QubDrawingMgr) :
    class _Rect(qt.QRect) :
        def __init__(self,*args) :
            qt.QRect.__init__(self,*args)
            self.__subXPix = 0
            self.__subYPix = 0
            
        def setCoords(self,*args) :
            self.__subXPix = 0
            self.__subYPix = 0
            qt.QRect.setCoords(self,*args)
        def setRect(self,*args) :
            self.__subXPix = 0
            self.__subYPix = 0
            qt.QRect.setRect(self,*args)

        def normalize(self):
            rect = qt.QRect.normalize(self)
            return Qub2PointSurfaceDrawingMgr._Rect(rect)
        
        def moveBy(self,dx,dy) :
            self.__subXPix += dx
            self.__subYPix += dy
            rDx = int(self.__subXPix)
            rDy = int(self.__subYPix)
            qt.QRect.moveBy(self,rDx,rDy)
            self.__subXPix -= rDx
            self.__subYPix -= rDy

    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._rect = Qub2PointSurfaceDrawingMgr._Rect(0,0,1,1)
        self._drawingEvent = QubPressedNDrag2Point
        
    ##@brief set absolute position of top left and bottom right point
    #@param x1 horizontal position of first point
    #@param y1 vertical position of first point
    #@param x2 horizontal position of second point
    #@param y2 vertical position of second point
    #@see setRect
    def setPoints(self,x1,y1,x2,y2) :
        self._rect.setCoords(x1,y1,x2,y2);
        self.update()
    ##@brief set a corner absolute position and with and height
    #@param x horizontal top left position
    #@param y vertical top left position
    #@param w width of the rectangle
    #@param h height of the rectangle
    #@see setPoints
    def setRect(self,x,y,w,h) :
        self._rect.setRect(x,y,w,h);
        self.update()
    ##@return the rectangle (qt.QRec)
    def rect(self) :
        rect = self._rect.normalize()
        return rect
    
    ##@name INTERNAL LOOP EVENT CALL
    #@{
    #private methode to move and resize the surface
    def moveFirstPoint(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(xNew,yNew,x2,y2)
        self.update()

    def moveSecondPoint(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(x1,y1,xNew,yNew)
        self.update()

    def moveTopRight(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(x1,yNew,xNew,y2)
        self.update()

    def moveBottomLeft(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(xNew,y1,x2,yNew)
        self.update()

    def moveRelativeRectangle(self, dx, dy):
        if self._matrix is not None :
            dxNew,dyNew = self._matrix.invert()[0].map(float(dx),float(dy))
        else:
            dxNew,dyNew = dx, dy
        self._rect.moveBy(dxNew, dyNew)
        self.update()
    ##@}

    ##@return width of the rectangle    
    def width(self) :
        width = 0
        try:
            for drawingObject in self._drawingObjects :
                tmpWidth = drawingObject.width()
                if tmpWidth > width :
                    width = tmpWidth
        except:
            import traceback
            traceback.print_exc()
        return width

    ##@return height of the rectangle
    def height(self) :
        height = 0
        try:
            for drawingObject in self._drawingObjects :
                tmpHeight = drawingObject.height()
                if tmpHeight > height :
                    height = tmpHeight
        except:
            import traceback
            traceback.print_exc()
        return height
    
    def update(self) :
        rect = self._rect.normalize()
        if self._matrix is not None :
            rect = self._matrix.map(rect)
        x,y,width,height = rect.rect()
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
            drawingObject.setSize(width,height)
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject()
        
    ##@brief get a modify class to move or resize the rectangle
    def _getModifyClass(self,x,y) :
        rect = self._rect.normalize()
        self._rect = rect
        if self._matrix is not None :
            rect = self._matrix.map(rect)
        (x1,y1,x2,y2) = rect.coords()
        if(abs(x - x1) < 5) :           # TOP LEFT OR BOTTOM LEFT
            if(abs(y - y1) < 5) :       # TOP LEFT
                return QubModifyAbsoluteAction(self,
                                       self.moveFirstPoint,
                                       qt.QCursor(qt.Qt.SizeFDiagCursor))
            elif(abs(y - y2) < 5) :     # BOTTOM LEFT
                return QubModifyAbsoluteAction(self,
                                       self.moveBottomLeft,
                                       qt.QCursor(qt.Qt.SizeBDiagCursor))
        elif(abs(x - x2) < 5) :         # TOP RIGHT OR BOTTOM RIGHT
            if(abs(y - y1) < 5) :       # TOP RIGHT
                return QubModifyAbsoluteAction(self,
                                       self.moveTopRight,
                                       qt.QCursor(qt.Qt.SizeBDiagCursor))
            elif(abs(y - y2) < 5) :
                return QubModifyAbsoluteAction(self,
                                       self.moveSecondPoint,
                                       qt.QCursor(qt.Qt.SizeFDiagCursor))
        elif (rect.contains(x, y)):
                return QubModifyRelativeAction(self,
                                       self.moveRelativeRectangle)
            
    ##@brief methode to draw object from other canvas
    def _drawForeignObject(self) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            rect = self._rect.normalize()
            if matrix is not None :
                rect = matrix.map(rect)
            x,y,width,height = rect.rect()
            for drawingObject in objectlist :
                drawingObject.move(x,y)
                drawingObject.setSize(width,height)
            if canvas: canvas.update()

##@brief manage all object which can be define with 3 points or more
#@ingroup DrawingManager
class QubPolygoneDrawingMgr(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._points = []
        self._drawingEvent = QubNPointClick
        self.__constraintPoint = {}
        self.__modifierConstraint = {}
        
    ##@brief set the brush for all drawingObject
    #@param brush a qt.QBrush
    def setBrush(self,brush) :
        for drawingObject in self._drawingObjects :
            drawingObject.setBrush(brush)
        if self._canvas: self._canvas.update()
        
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.setBrush(brush)
            if canvas: canvas.update()
            
    ##@brief set the list of points
    #@param pointList this is a list a tuple (x,y)
    def setPoints(self,pointList) :
        self._points = pointList
        self.update()
    ##@return list of tuple (x,y)
    def points(self) :
        return self._points

    def reset(self) :
        self._points = []
    ##@name Internal loop event call
    #@{
    def move(self,x,y,point_id) :
        (fromPointId,constraintObject) = self.__constraintPoint.get(point_id,(None,None))
        if fromPointId is not None and len(self._points) > fromPointId :
            x0,y0 = self._points[fromPointId]
            if self._matrix is not None :
                x0,y0 = self._matrix.map(float(x0),float(y0))
            x0,y0,x,y = constraintObject.calc(x0,y0,x,y)
            
        if self._matrix is not None :
            xWarp,yWarp = self._matrix.invert()[0].map(float(x),float(y))
        else:
            xWarp,yWarp = x,y

        if len(self._points) <= point_id :
            self._points.append((xWarp,yWarp))
        else:
            self._points[point_id] = (xWarp,yWarp)

        aEndFlag = False
        for drawingObject in self._drawingObjects :
            aEndFlag = drawingObject.move(x,y,point_id) or aEndFlag
        if self._canvas: self._canvas.update()
        
        self._drawForeignObject(point_id)

        return aEndFlag

    def update(self) :
        for point_id,(x,y) in enumerate(self._points) :
            if self._matrix is not None :
                x,y = self._matrix.map(float(x),float(y))

            for drawingObject in self._drawingObjects :
                drawingObject.move(x,y,point_id)

            self._drawForeignObject(point_id)

        for drawingObject in self._drawingObjects:
            if hasattr(drawingObject,"update") :
                drawingObject.update()
        if self._canvas: self._canvas.update()
        
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                if hasattr(drawingObject,"update") :
                    drawingObject.update()
            if canvas: canvas.update()
    ##@}
    def addDrawingObject(self,aDrawingObject) :
        QubDrawingMgr.addDrawingObject(self,aDrawingObject)
        if hasattr(aDrawingObject,'getConstraint') :
            for contraintId,fromPointId,constaintObject in aDrawingObject.getConstraint() :
                self.__constraintPoint[contraintId] = (fromPointId,constaintObject)
        if hasattr(aDrawingObject,'getModifierConstraint') :
            for fromPointId,contraintIdList,constaintObject in aDrawingObject.getModifierConstraint() :
                self.__modifierConstraint[fromPointId] = (contraintIdList,constaintObject)

    ##@brief get a modify class to move or resize the polygone
    def _getModifyClass(self,x,y) :
        point_screen = []
        for i,(xpoint,ypoint) in enumerate(self._points) :
            if self._matrix is not None :
                xpoint,ypoint = self._matrix.map(float(xpoint),float(ypoint))
            point_screen.append([xpoint,ypoint])
            if(abs(x - xpoint) < 5 and abs(y - ypoint) < 5) :
                (constraintIdList,constraintObject) = self.__modifierConstraint.get(i,(None,None))
                if constraintIdList is None:
                    func = self.move.im_func
                    tmpfunc = new.function(func.func_code,func.func_globals,'tmpmove',(self,0,0,i))
                else:
                    func = self.__moveWithContraint.im_func
                    tmpfunc = new.function(func.func_code,func.func_globals,'tmpmove',(self,0,0,i,constraintIdList,constraintObject))
                callBack = new.instancemethod(tmpfunc,self,QubPolygoneDrawingMgr)
                return QubModifyAbsoluteAction(self,callBack)
        
        match_points = polygone.points_inclusion([[x,y]],point_screen,False)
        if match_points[0]:
            return QubModifyRelativeAction(self, self.move_rel)
        
    def move_rel(self, dx, dy):
        for i,(xpoint,ypoint) in enumerate(self._points):
            if self._matrix is not None :
                xpoint,ypoint = self._matrix.map(float(xpoint),float(ypoint))
            self.move(xpoint+dx, ypoint+dy, i)
                     

    ##@brief this methode is use when a drawing object has contraint on point modification
    #
    def __moveWithContraint(self,x,y,pointId,pointIdList,constraintobject) :
        pointList = []
        for Id in pointIdList :
            xp,yp = self._points[Id]
            if self._matrix is not None:
                xp,yp = self._matrix.map(float(xp),float(yp))
            pointList.append((xp,yp))
        newPointList = constraintobject.calc(x,y,pointList)
        self.move(x,y,pointId)
        for pointId,(x,y) in zip(pointIdList,newPointList) :
            self.move(x,y,pointId)
        
    ##@brief methode to draw object from other canvas
    def _drawForeignObject(self,point_id) :
        try:
            for link,canvas,matrix,objectlist in self._foreignObjects :
                x,y = self._points[point_id]
                if matrix is not None :
                    x,y = matrix.map(float(x),float(y))
                for drawingObject in objectlist :
                    drawingObject.move(x,y,point_id)
                if canvas: canvas.update()
        except:
            import traceback
            traceback.print_exc()
            
