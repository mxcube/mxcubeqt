import qt
import weakref
import itertools

##@brief This class is use as a event manager and dispatcher.
#
#it's centralise all events needed by drawing objects.
#As we want a standard way of drawing object, it's acting
#as an event filter:
# - Modification can only be done by <b>SHIFT and LEFT CLICK</b>
# - Drawing on <b>LEFT CLICK</b>
#
#Moreover exclusive event are managed.
#And finally you can link an event managed with other
class QubEventMgr:
    def __init__(self) :
        ##the active event loop
	self.__pendingEvents = []
        ##the event list which are exclude
        self.__excludedEvent = []
        ##the drawing manager list
	self.__drawingMgr = []
        ##the event link list 
        self.__eventLinkMgrs = []
        #@{
        ##the last mouse position
        self.__mouseX,self.__mouseY = 0,0
        ##@}

        ##the current object in modification state
        self.__curentModifierMgr = None
        ##the scrollview associate
        self.__scrollView = None
        ##the idle use for the action's info 
        self.__actionInfoIdle = qt.QTimer(self)
        qt.QObject.connect(self.__actionInfoIdle,qt.SIGNAL('timeout()'),self.__emitActionInfo)
        self.__directInfo = ''
        
    ##@brief add a drawing manager
    #
    #@param aDrawingMgr a Qub::Objects::QubDrawingMgr::QubDrawingMgr
    def addDrawingMgr(self,aDrawingMgr) :
        try:
            self.__drawingMgr.append(weakref.ref(aDrawingMgr,self.__weakRefDrawingMgrRemove))
            aDrawingMgr.setEventMgr(self)
            for link in self.__eventLinkMgrs :
                aDrawingMgr.addLinkEventMgr(link)
        except:
            import traceback
            traceback.print_exc()
    ##@brief insert an event in the pool
    #
    #After this call, the drawing event will be called on each mouse event
    #@param aDrawingMgr a Qub::Objects::QubDrawingEvent::QubDrawingEvent
    def addDrawingEvent(self,aDrawingEvent) :
        try:
            exclusive = aDrawingEvent.exclusive()
            if exclusive is not False :
                excludeEvents = []
                for pendingEventRef in self.__pendingEvents[:] :
                    pendingEvent = pendingEventRef()
                    if pendingEvent is None : continue
                    excludePendingEvent = pendingEvent.exclusive()
                    if excludePendingEvent is not False and pendingEvent.name() not in exclusive :
                        pendingEvent.setDubMode(True)
                        self.__pendingEvents.remove(pendingEventRef)
                        excludeEvents.append(pendingEventRef)
                if len(excludeEvents) :
                    self.__excludedEvent.append((weakref.ref(aDrawingEvent,self.__weakRefEventRemove),excludeEvents))
            self.__pendingEvents.append(weakref.ref(aDrawingEvent,self.__weakRefEventRemove))
            if not self.__actionInfoIdle.isActive() :
                self.__actionInfoIdle.start(0)
        except:
            import traceback
            traceback.print_exc()
    ##@brief this methode link several event manager together,
    #thanks to that, each draw may be seen on every view
    #
    #After this call, each event on one event manager will be dispatcher on other via _linkEventMgr class
    #
    #@param anEventMgr the other event manager to be link with
    #@param srcCanvas the canvas that this object manage
    #@param desCanvas the other canvas
    #@param srcMatrix the Matrix related of this object
    #@param destMatrix the other Matrix
    def addEventMgrLink(self,anEventMgr,
                        srcCanvas,desCanvas,
                        srcMatrix,destMatrix) :
        linkEventMgr = _linkEventMgr(self,anEventMgr,
                                     srcCanvas,desCanvas,
                                     srcMatrix,destMatrix)
        self.addLinkEventMgr(linkEventMgr)
        anEventMgr.addLinkEventMgr(linkEventMgr)
        for drawingMgrRef in self.__drawingMgr :
            drawingMgr = drawingMgrRef()
            if drawingMgr:
                drawingMgr.addLinkEventMgr(linkEventMgr)
    ##@brief unlink between an event manager
    def rmEventMgrLink(self,anEventMgr) :
        linkfind = None
        for link in self.__eventLinkMgrs :
            mgr1,mgr2 = link.getMgrs()
            if mgr1 == self or mgr2 == self :
                mgr1.rmLinkEventMgr(link)
                mgr2.rmLinkEventMgr(link)
                break

    ##@brief get the scrollview
    #
    #@return the scrollview of the object or None
    #
    def scrollView(self) :
        return self.__scrollView and self.__scrollView() or None

    ##@name methode called by the inheritance
    #@{
    #all this methode should be called by the inheritance
    #in order to dispatche event to the drawing
      
    ##@brief set the scroll view if one
    #
    #this methode should be called by the inheritance if it's got a scrollView
    def _setScrollView(self,aScrollView) :
        self.__scrollView = weakref.ref(aScrollView)
    ##@brief mouse has been pressed
    #
    #dispatch event via the drawing event
    #@see Qub::Objects::QubDrawingEvent::QubDrawingEvent
    #@param event qt event
    #@param evtMgr if not None external event ie: generated from a linked event manager
    def _mousePressed(self,event,evtMgr = None) :
        try:
            if event.button() == qt.Qt.LeftButton and event.type() == qt.QEvent.MouseButtonDblClick:
                for drawingEventRef in self.__pendingEvents[:] :
                    if(drawingEventRef().mouseDblClick(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)
            elif event.button() == qt.Qt.LeftButton and event.state() == qt.Qt.ShiftButton :
                if self.__curentModifierMgr is not None :
                    self.__curentModifierMgr.mousePressed(event.x(),event.y())
            elif event.button() == qt.Qt.LeftButton :
                for drawingEventRef in self.__pendingEvents[:] :
                    drawingEvent = drawingEventRef()
                    if(drawingEvent and drawingEvent.mousePressed(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)

                for drawingMgr in self.__drawingMgr:
                    modifyClass = drawingMgr().getModifyClass(event.x(),event.y())
                    if modifyClass:
                        drawingMgr().wasClicked()
                            
            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mousePressed(event,self)

        except:
            import traceback
            traceback.print_exc()
    
    ##@brief mouse has moved
    #
    #@see _mousePressed
    def _mouseMove(self,event,evtMgr = None) :
        try:
            self.__mouseX,self.__mouseY = event.x(),event.y()
            for drawingEventRef in self.__pendingEvents[:] :
                drawingEvent = drawingEventRef()
                if(drawingEvent and drawingEvent.mouseMove(event.x(),event.y())) :
                    self._rmDrawingEventRef(drawingEventRef)

            if(self.__curentModifierMgr is not None and
               event.state() == (qt.Qt.LeftButton + qt.Qt.ShiftButton)) :
                self.__curentModifierMgr.mouseMovePressed(event.x(),event.y())
            elif event.state() == qt.Qt.ShiftButton : # FIND MOVE CLASS
                self.__checkObjectModify(event.x(),event.y(),evtMgr)
            else :
                if self.__curentModifierMgr is not None :
                    if evtMgr is not None :
                        evtMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                    else:
                        self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                    self.__curentModifierMgr = None

            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mouseMove(event,self)
        except:
            import traceback
            traceback.print_exc()

    ##@brief mouse has been released
    #
    #@see _mousePressed
    def _mouseRelease(self,event,evtMgr = None) :
        try:
            if event.state() & qt.Qt.LeftButton :
                if self.__curentModifierMgr is not None :
                    self.__curentModifierMgr.mouseReleased(event.x(),event.y())
                else :
                    for drawingEventRef in self.__pendingEvents[:] :
                        d = drawingEventRef()
                        if(d and d.mouseReleased(event.x(),event.y())) :
                            self._rmDrawingEventRef(drawingEventRef)
            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mouseReleased(event,self)
        except:
            import traceback
            traceback.print_exc()

    ##@brief need a redraw of some drawing
    #
    #this methode is called when the canvas was resized or when the view is scrolled
    def _update(self,evtMgr = None) :
        for drawingMgr in self.__drawingMgr :
            d = drawingMgr()
            try:
                if d :
                    d.update()
            except:
                import traceback
                traceback.print_exc()
        if evtMgr is None :             # event propagate
            for link in self.__eventLinkMgrs :
                link.update(self)
    ##@brief a key was pressed
    #
    #this methode filter SHIFT key which it's used for object modification
    #add dispatch key event via the drawing event
    #@see _mousePressed
    def _keyPressed(self,keyevent,evtMgr = None) :
        if keyevent.key() == qt.Qt.Key_Shift :
            self.__checkObjectModify(self.__mouseX,self.__mouseY,evtMgr)

        for drawingEventRef in self.__pendingEvents[:] :
            d = drawingEventRef()
            if d and d.rawKeyPressed(keyevent) :
                self._rmDrawingEventRef(drawingEventRef)
                
        if evtMgr is None:          # event propagate
            for link in self.__eventLinkMgrs :
                link.keyPressed(keyevent,self)

        modifyClass = self.__getCurrentModify(self.__mouseX,self.__mouseY,evtMgr)
        if modifyClass:
            modifyClass.rawKeyPressed(keyevent)
            
    ##@brief a key was released
    #
    #@see _keyPressed
    def _keyReleased(self,keyevent,evtMgr = None) :
        if keyevent.key() == qt.Qt.Key_Shift :
            if self.__curentModifierMgr is not None :
                if evtMgr is not None :
                    evtMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                else:
                    self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None

        for drawingEventRef in self.__pendingEvents[:] :
            d = drawingEventRef()
            if d and d.rawKeyReleased(keyevent) :
                self._rmDrawingEventRef(drawingEventRef)

        if evtMgr is None:          # event propagate
            for link in self.__eventLinkMgrs :
                link.keyReleased(keyevent,self)
                

    ##@brief the mouse leave the window
    #
    #leave the modification state if active
    def _leaveEvent(self,event,evtMgr = None) :
         if self.__curentModifierMgr is not None :
                self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
    ##@}
    #
    
    ##@brief remove a drawing event object of the pending event loop
    def _rmDrawingEventRef(self,aDrawingEventRef) :
        try:
            self.__pendingEvents.remove(aDrawingEventRef)
        except:
            for eRef,excludList in self.__excludedEvent :
                if aDrawingEventRef in excludList :
                    excludList.remove(aDrawingEventRef)
        try:
            self.__checkExcludedEventsBeforeRemove(aDrawingEventRef)
            aDrawingEventRef().endPolling()
        except:
            pass
        if not self.__actionInfoIdle.isActive() :
            self.__actionInfoIdle.start(0)
            
    ##@brief weakref callback on the drawing event object
    #
    #Event object is no longer reference -> clean the pending event loop
    #@see Qub::Objects::QubDrawingEvent::QubDrawingEvent
    def __weakRefEventRemove(self,eventRef) :
        try :
            self.__pendingEvents.remove(eventRef)
            self.__checkExcludedEventsBeforeRemove(eventRef)
            if not self.__actionInfoIdle.isActive() :
                self.__actionInfoIdle.start(0)
        except:
            pass

    ##@brief weakref callback on DrawingManager
    #
    #Drawing is no longer reference, hide it on canvas and
    #removed from the managed list 
    #@see Qub::Objects::QubDrawingMgr::QubDrawingMgr
    def __weakRefDrawingMgrRemove(self,mgrRef) :
        try:
            self.__drawingMgr.remove(mgrRef)
        except:
           pass

    ##@brief check if this event hased exclude some other
    #
    #this methode it's be called just before the event in arg is removed
    #@param eventRef the weakref of a drawing event
    #@see Qub::Objects::QubDrawingEvent::setExclusive
    #@see Qub::Objects::QubDrawingEvent::setExceptExclusiveListName
    def __checkExcludedEventsBeforeRemove(self,eventRef) :
        for eRef,excludedList in self.__excludedEvent[:] :
            if eRef() == eventRef() :
                tmpPendingList = self.__pendingEvents[:]
                self.__pendingEvents = excludedList
                for e in tmpPendingList :
                    self.addDrawingEvent(e())
                self.__pendingEvents = [x for x in itertools.ifilter(lambda x : x() is not None,self.__pendingEvents)]
                for i in range(len(tmpPendingList),len(self.__pendingEvents)) :
                    self.__pendingEvents[i]().setDubMode(False)
                self.__excludedEvent.remove((eRef,excludedList))
                break
                
    def __getCurrentModify(self,x,y,anEventMgr) :
        BBoxNmodifyClass = []
        for drawingMgr in self.__drawingMgr :
            modifyClass = drawingMgr().getModifyClass(x,y)
            if modifyClass is not None :
                boundingRect = drawingMgr().boundingRect()
                BBoxNmodifyClass.append((boundingRect,modifyClass))

        BBoxNmodifyClass.sort(lambda v1,v2 : v1[0].width() * v1[0].height() - v2[0].width() * v2[0].height())
        return BBoxNmodifyClass and BBoxNmodifyClass[0][1] or None
    
    ##@brief check if a drawing manager can be modify at this pixel
    def __checkObjectModify(self,x,y,anEventMgr) :
        modifierMgr = self.__getCurrentModify(x,y,anEventMgr)
        if not modifierMgr :
            if anEventMgr is None : anEventMgr = self
            if self.__curentModifierMgr is not None :
                anEventMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
        else:
            self.__curentModifierMgr = modifierMgr
            if anEventMgr is None : anEventMgr = self
            self.__curentModifierMgr.setCursor(anEventMgr)
            
    ##@brief manage the action's information
    #
    #@see Qub::Objects::QubDrawingManager::setActionInfo
    def __emitActionInfo(self) :
        if self.__directInfo : textList = [self.__directInfo]
        else : textList = []
        try:
            for pendingRef in self.__pendingEvents :
                text = pendingRef().getActionInfo()
                if text :
                    textList.append(text)
            textInfo = ' - '.join(textList)
            self._realEmitActionInfo(textInfo)
        except:
            import traceback
            traceback.print_exc()
        self.__actionInfoIdle.stop()

    def setInfo(self,text) :
        self.__directInfo = text
        if not self.__actionInfoIdle.isActive() :
            self.__actionInfoIdle.start(0)

    #@brief This methode should be redefine
    #@param text the action's text information 
    def _realEmitActionInfo(self,text) :
        print text
        
    #@brief Do not call this methode directly
    def addLinkEventMgr(self,linkEventMgr) :
        self.__eventLinkMgrs.append(linkEventMgr)

    def getEventMethodes(self) :
        return [self._mousePressed,self._mouseMove,self._mouseRelease,
                self._update,self._keyPressed,self._keyReleased,self._leaveEvent]
                   ####### Link event class #######

    def mousePosition(self):
        return (self.__mouseX,self.__mouseY)
        
class _linkEventMgr :
    MOUSE_PRESSED,MOUSE_MOVE,MOUSE_RELEASE,UPDATE,KEY_PRESSED,KEY_RELEASED,LEAVE_EVENT = range(7)

    def __init__(self,evMgr1,evMgr2,
                 canvas1,canvas2,
                 matrix1,matrix2) :
        self.__evtMgrs = [(evMgr1,evMgr1.getEventMethodes()),
                          (evMgr2,evMgr2.getEventMethodes())]
        self.__canvas = [canvas1,canvas2]
        self.__matrix = [matrix1,matrix2]
        
    def mousePressed(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_PRESSED)
        
    def mouseMove(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_MOVE)
        
    def mouseReleased(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_RELEASE)

    def update(self,evtMgr) :
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            mgrNMeth = self.__evtMgrs[1]
        mgrNMeth[1][_linkEventMgr.UPDATE](evtMgr)
        
    def keyPressed(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.KEY_PRESSED)
        
    def keyReleased(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.KEY_RELEASED)
        
    def leaveEvent(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.LEAVE_EVENT)
    
    def _simpleEvent(self,event,evtMgr,aType) :
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            mgrNMeth = self.__evtMgrs[1]
        mgrNMeth[1][aType](event,evtMgr)
        
    def _mouseEvent(self,event,evtMgr,aType) :
        matrix2,matrix1 = self.__matrix
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            matrix1,matrix2 = matrix2,matrix1
            mgrNMeth = self.__evtMgrs[1]

        x,y = event.pos().x(),event.pos().y()
        if matrix1 is not None :
            x,y = matrix1.invert()[0].map(x,y)
        if matrix2 is not None :
            x,y = matrix2.map(x,y)
        newEvent = qt.QMouseEvent(event.type(),qt.QPoint(x,y),event.button(),event.state())
        mgrNMeth[1][aType](newEvent,evtMgr)

    def getMgrs(self) :
        return self.__evtMgrs[0][0],self.__evtMgrs[1][0]

    def getOtherMgr(self,eventMgr) :
        if eventMgr == self.__evtMgrs[0][0] :
            return self.__evtMgrs[1][0]
        else :
            return self.__evtMgrs[0][0]
        
    def getCanvasNMatrix(self,evtMgr) :
        matrix1,matrix2 = self.__matrix
        canvas1,canvas2 = self.__canvas
        if evtMgr == self.__evtMgrs[0][0] :
            matrix1,matrix2 = matrix2,matrix1
            canvas1,canvas2 = canvas2,canvas1
        return (canvas1,matrix1)
