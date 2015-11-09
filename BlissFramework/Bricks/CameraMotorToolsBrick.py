"""
Camera Motor Tools Brick

[Description]

This brick allows to add a "Move to " mode as action (toolbar or popup menu)
of a camera brick. A soon as the calibration has been done and beam position
has been set, user can click on the display of the associated camera brick and
the point selected will move in the beam.

This brick also allows to graphically display on the camera brick the limits
and positions of the horizontal and vertical motors associated with the
camera brick.
    
[Properties]
Hor. Motor - string - horizontal motor associated with the camera

Vert. Motor - string - vertical motor associated with the camera

Move To - ("None", "Toolbar", "Popup") - define "Move to" mode as action and 
                                         place "Move To " action in toolbar or
                                         popup menu of the camera brick
                                      
Limits - ("None", "Toolbar", "Popup") - display limits and position of camera
                                        motors and place "Limits" action in
                                        toolbar or popup menu of the camera brick


[Signals]

getView - {"drawing"} - emitted to get a reference on the image viewer object.
                        At returned of the emit function, the key "drawing"
                        exists and its value is the reference of the image
                        viewer or the key "drawing" does not exists which mean
                        that the image viewer object does not exist.

getMosaicView - same as getView but on CameraMosaic

"getCalibration" - {"ycalib", "zcalib"} - emitted to get the calibration
                                          values.
                                          At returned of the emit function,
                                          the keys "ycalib" and "zcalib" exist
                                          and their values are set or the
                                          keys do not exist which mean the
                                          calibration do not exist.
                        
"getBeamPosition" - {"ybeam", "zbeam"} - emitted to get the beam position values.
                                         At returned of the emit function,
                                         the keys "ybeam" and "zbeam" exist
                                         and their values are set or the
                                         keys do not exist which mean the
                                         beam positions do not exist.

"moveDone" - (ybeam, zbeam) - emitted when move to beam has been done 
 
[Slots]

beamPositionChanged - {"ybeam", "zbeam"} - Get new beam position when changed
                                           by another object
pixelCalibrationChanged - {"ycalib", "zcalib"} - Get new pixel calibration when
                                                 changed by another object
                                                 
setMoveToMode - boolean - activates or desactivates the "Move To" mode

setLimitsDisplay - boolean - activates or desactivates the "limits" mode

[Comments]


"""
import qt
import sys
import qttable
import qtcanvas
import logging

from BlissFramework.BaseComponents import BlissWidget

from Qub.Widget.QubActionSet import QubRulerAction
from Qub.Widget.QubActionSet import QubSelectPointAction
from Qub.Widget.QubActionSet import QubOpenDialogAction

from Qub.Widget.QubAction import QubToggleAction

from Qub.Widget.QubDialog import QubMeasureListDialog

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr,QubAddDrawing

from Qub.Objects.QubDrawingCanvasTools import QubCanvasHomotheticRectangle

from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point

#from CameraMotorToolsFocusStateMachine import FocusState

__category__ = "Camera"

_enumTranslate = {None : None,"none" : None,"toolbar" : "toolbar","popup" : "contextmenu"}

#############################################################################
##########                                                         ##########
##########                         BRICK                           ##########
##########                                                         ##########       
#############################################################################       
class CameraMotorToolsBrick(BlissWidget):
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)
        
        """
        variables
        """
        self.YBeam = None
        self.ZBeam = None
        self.YSize = None
        self.ZSize = None
        
        self.view = None
        self.firstCall = True
        self.motorArrived = 0

        self.__mosaicView,self.__mosaicDraw = None,None

        """
        property
        """
        self.addProperty("Hor. Motor", "string", "")
        self.horMotHwo = None
        
        self.addProperty("Vert. Motor", "string", "")
        self.verMotHwo = None

        #self.addProperty("Focus Motor","string","")
        #self.focusMotHwo = None

        #self.addProperty("Focus min step","float",0.05)
        #self.focusMinStep = None
        
        self.addProperty("Move To", "combo",
                         ("none", "toolbar", "popup"), "none")
        self.movetoMode = None
        self.movetoAction = None

        self.addProperty("Move to color when activate","combo",
                         ("none","blue","green","yellow","red","orange"),"none")
        self.movetoColorWhenActivate = None
        
        self.addProperty("Limits", "combo",
                         ("none", "toolbar", "popup"), "none")
        self.limitsMode = None
        self.limitsAction = None

        self.addProperty("Measure", "combo", ("none", "toolbar", "popup"), "none")
        self.measureMode = None
        self.measureAction = None

        self.addProperty("Focus","combo",
                         ("none", "toolbar", "popup"), "none")
        self.focusMode = None
        self.focusAction = None
        self.focusState = None
        self.focusDrawingRectangle = None
        self.focusPointSelected = None
        
        self.__movetoActionMosaic = None
        
        """
        Signal
        """
        self.defineSignal('getView',())
        self.defineSignal('getMosaicView',())
        self.defineSignal('getCalibration',())
        self.defineSignal('getBeamPosition',())
        self.defineSignal('getImage',())
        self.defineSignal('moveDone', ())
        self.defineSignal('mosaicImageSelected', ())
        """
        Slot
        """
        self.defineSlot('beamPositionChanged',())
        self.defineSlot('pixelCalibrationChanged',())
        self.defineSlot('setMoveToMode',())
        self.defineSlot('setLimitsDisplay',())
        self.defineSlot('setMoveToState',())

        """
        widgets - NO APPEARANCE
        """
        self.setFixedSize(0, 0)
                        
               
    def propertyChanged(self, prop, oldValue, newValue):
        if prop == "Hor. Motor":
            if self.horMotHwo is not None:
                self.disconnect(self.horMotHwo, qt.PYSIGNAL('positionChanged'),
                                self.setHorizontalPosition)
                self.disconnect(self.horMotHwo, qt.PYSIGNAL("limitsChanged"),
                                self.setHorizontalLimits)

            self.horMotHwo = self.getHardwareObject(newValue)
            
            if self.horMotHwo is not None:
                self.connect(self.horMotHwo, qt.PYSIGNAL('positionChanged'),
                             self.setHorizontalPosition)
                self.connect(self.horMotHwo, qt.PYSIGNAL("limitsChanged"),
                             self.setHorizontalLimits)

        elif prop == "Vert. Motor":
            if self.verMotHwo is not None:
                self.disconnect(self.verMotHwo, qt.PYSIGNAL('positionChanged'),
                                self.setVerticalPosition)
                self.disconnect(self.verMotHwo, qt.PYSIGNAL("limitsChanged"),
                                self.setVerticalLimits)

            self.verMotHwo = self.getHardwareObject(newValue)
            
            if self.verMotHwo is not None:
                self.connect(self.verMotHwo, qt.PYSIGNAL('positionChanged'),
                             self.setVerticalPosition)
                self.connect(self.verMotHwo, qt.PYSIGNAL("limitsChanged"),
                             self.setVerticalLimits)
        #elif prop == "Focus Motor":
        #    if self.focusMotHwo is not None:
        #        self.disconnect(self.focusMotHwo,qt.PYSIGNAL('positionChanged'),
        #                        self.setFocusPosition)
        #        self.disconnect(self.focusMotHwo,qt.PYSIGNAL('limitsChanged'),
        #                        self.setFocusLimits)

        #    self.focusMotHwo = self.getHardwareObject(newValue)
        #    self.focusState = FocusState(self,self.focusMotHwo)
            
        #    if self.focusMotHwo is not None:
        #        self.connect(self.focusMotHwo,qt.PYSIGNAL('positionChanged'),
        #                     self.setFocusPosition)
        #        self.connect(self.focusMotHwo,qt.PYSIGNAL('limitsChanged'),
        #                     self.setFocusLimits)
        #        self.connect(self.focusMotHwo, qt.PYSIGNAL("moveDone"),
        #                     self.focusMoveFinished)
        elif prop == "Move To": self.movetoMode = _enumTranslate[newValue]
        elif prop == "Limits": self.limitsMode = _enumTranslate[newValue]
        elif prop == "Focus": self.focusMode = _enumTranslate[newValue]
        elif prop == "Measure": self.measureMode = _enumTranslate[newValue]
        elif prop == "Focus min step": self.focusMinStep = newValue
        elif prop == "Move to color when activate" :
            if newValue == "none" :
                self.movetoColorWhenActivate = None
            else:
                self.movetoColorWhenActivate = newValue
        if not self.firstCall:
            self.configureAction()
            
    def run(self):
        """
        get view
        """
        view = {}
        self.emit(qt.PYSIGNAL("getView"), (view,))
        try:
            self.drawing = view["drawing"]
            self.view = view["view"]        
        except:
            print "No View"
        
        """
        get calibration
        """
        calib = {}
        self.emit(qt.PYSIGNAL("getCalibration"), (calib,))
        try:
            # in all this brick we work with pixel calibration in mm
            self.YSize = calib["ycalib"]
            self.ZSize = calib["zcalib"]
            if calib["ycalib"] is not None and calib["zcalib"] is not None:
                self.YSize = self.YSize * 1000
                self.ZSize = self.ZSize * 1000
        except:
            print "No Calibration"
            
        """
        get beam position
        """
        position = {}
        self.emit(qt.PYSIGNAL("getBeamPosition"), (position,))
        try:
            self.YBeam = position["ybeam"]
            self.ZBeam = position["zbeam"]
        except:
            print "No Beam Position"

        """
        get mosaic view
        """
        mosaicView = {}
        self.emit(qt.PYSIGNAL('getMosaicView'),(mosaicView,))
        try:
            self.__mosaicView = mosaicView['view']
            self.__mosaicDraw = mosaicView['drawing']
        except KeyError:
            self.__mosaicView,self.__mosaicDraw = None,None
            
        self.configureAction()
        
        self.firstCall = False
    
    def configureAction(self):
        """
        Move To action
        """
        if self.movetoMode is not None:
            if self.movetoAction is None:
                """
                create action
                """
                self.movetoAction = QubSelectPointAction(name='Move to Beam',
                                                         place=self.movetoMode,
                                                         actionInfo = 'Move to Beam',
                                                         group='Tools')
                self.connect(self.movetoAction,qt.PYSIGNAL("StateChanged"),self.movetoStateChanged)
                self.connect(self.movetoAction, qt.PYSIGNAL("PointSelected"),
                             self.pointSelected)
                
                if self.view is not None:
                    self.view.addAction(self.movetoAction)
                    self.oldMoveToActionColor = self.movetoAction.paletteBackgroundColor()

        else:
            if self.movetoAction is not None:
                """
                remove action
                """
                if self.view is not None:
                    self.view.delAction(self.movetoAction)
                    
                """
                del action from view
                """
                self.disconnect(self.movetoAction, qt.PYSIGNAL("PointSelected"),
                                self.pointSelected)
                self.movetoAction = None
        """
        Limits action
        """
        if self.limitsMode is not None:
            if self.limitsAction is None:
                """
                create action
                """
                self.limitsAction = QubRulerAction(name='Motor Limits',
                                                   place=self.limitsMode,
                                                   group='Tools')
                    
                if self.view is not None:
                    self.view.addAction(self.limitsAction)
                
            """
            configure action
            """
            if self.horMotHwo is not None:
                mne = self.horMotHwo.getMotorMnemonic()
                self.limitsAction.setLabel(QubRulerAction.HORIZONTAL,0,mne)

            if self.verMotHwo is not None:
                mne = self.verMotHwo.getMotorMnemonic()
                self.limitsAction.setLabel(QubRulerAction.VERTICAL,0, mne)
                
        else:
            if self.limitsAction is not None:
                """
                remove action
                """
                if self.view is not None:
                    self.view.delAction(self.limitsAction)
                    
                """
                del action from view
                """
                self.limitsAction = None

        if self.measureMode is not None:
		if self.measureAction is None:
			self.measureAction = QubOpenDialogAction(parent=self, name='measure', iconName='measure', label='Measure', group='Tools', place=self.measureMode)
			self.measureAction.setConnectCallBack(self._measure_dialog_new)
                        logging.getLogger().info("setting measure mode")
			if self.view is not None:
				logging.getLogger().info("adding action")
				self.view.addAction(self.measureAction)
	else:
		if self.measureAction is not None:
			if self.view is not None:
				self.view.delAction(self.measureAction)
			self.measureAction = None

        if self.movetoMode is not None:
            if self.__movetoActionMosaic is not None:
                self.__mosaicView.delAction(self.__movetoActionMosaic)
                self.disconnect(self.__movetoActionMosaic, qt.PYSIGNAL("PointSelected"),
                                self.__mosaicPointSelected)
                self.diconnect(self.__movetoActionMosaic,qt.PYSIGNAL("StateChanged"),
                               self.__movetoMosaicStateChanged)
                self.__movetoActionMosaic = None
                
            if self.__mosaicView is not None :
                self.__movetoActionMosaic = QubSelectPointAction(name='Move to Beam',
                                                                 place=self.movetoMode,
                                                                 actionInfo = 'Move to Beam',
                                                                 mosaicMode = True,
                                                                 residualMode = True,
                                                                 group='Tools')
                self.connect(self.__movetoActionMosaic, qt.PYSIGNAL("PointSelected"),
                             self.__mosaicPointSelected)
                self.connect(self.__movetoActionMosaic,qt.PYSIGNAL("StateChanged"),
                             self.__movetoMosaicStateChanged)

                self.__mosaicView.addAction(self.__movetoActionMosaic)
                self.__oldMoveToMosaicActionColor = self.__movetoActionMosaic.paletteBackgroundColor()

        if self.focusMode is not None:
            if self.focusAction is None:
                self.focusAction = QubToggleAction(label='Autofocus',name='autofocus',place=self.focusMode,
                                                   group='Tools',autoConnect = True)
                qt.QObject.connect(self.focusAction,qt.PYSIGNAL('StateChanged'),self.showFocusGrab)

            if self.view and self.drawing :
                self.focusDrawingRectangle,_ = QubAddDrawing(self.drawing,QubPointDrawingMgr,QubCanvasHomotheticRectangle)
                self.focusDrawingRectangle.setDrawingEvent(QubMoveNPressed1Point)
                self.focusDrawingRectangle.setKeyPressedCallBack(self.focusRawKeyPressed)

                qt.QObject.connect(self.drawing,qt.PYSIGNAL("ForegroundColorChanged"),self.focusDrawingRectangle.setColor)
                self.focusDrawingRectangle.setEndDrawCallBack(self.setFocusPointSelected)
                self.focusRectangleSize = 12
                self.focusDrawingRectangle.setWidthNHeight(self.focusRectangleSize,self.focusRectangleSize)
                self.view.addAction(self.focusAction)
                
        elif self.view is not None:
            self.view.delAction(self.focusAction)
            self.focusDrawingRectangle = None
    
    def _measure_dialog_new(self,openDialogAction,aQubImage) :
        if  self.YSize is not None and self.ZSize is not None:
    	  self.__measureDialog = QubMeasureListDialog(self,
                                                      canvas=aQubImage.canvas(),
                                                      matrix=aQubImage.matrix(),
                                                      eventMgr=aQubImage)
          self.__measureDialog.setXPixelSize(self.YSize/1000.0)
          self.__measureDialog.setYPixelSize(self.ZSize/1000.0)
          self.__measureDialog.connect(aQubImage, qt.PYSIGNAL("ForegroundColorChanged"),
                                       self.__measureDialog.setDefaultColor)
          openDialogAction.setDialog(self.__measureDialog)
        
    def setHorizontalPosition(self, newPosition):
        if self.limitsAction is not None:        
            self.limitsAction.setCursorPosition(QubRulerAction.HORIZONTAL, 0,
                                                newPosition)
          
    def setHorizontalLimits(self, limit):
        if self.limitsAction is not None:        
            self.limitsAction.setLimits(QubRulerAction.HORIZONTAL, 0,
                                        limit[0], limit[1])
             
    def setVerticalPosition(self, newPosition):
        if self.limitsAction is not None:        
            self.limitsAction.setCursorPosition(QubRulerAction.VERTICAL, 0,
                                                newPosition)

    def setVerticalLimits(self, limit):
        if self.limitsAction is not None:        
            self.limitsAction.setLimits(QubRulerAction.VERTICAL, 0,
                                        limit[0], limit[1])
         
    #def setFocusLimits(self,limit) :
    #    self.focusState.setLimit(limit)

    #def setFocusPosition(self,newPosition) :
    #    self.focusState.newPosition(newPosition)

    #def focusMoveFinished(self, ver, mne):
    #    self.focusState.endMovement(ver)

    #def focusRawKeyPressed(self,keyevent) :
    #    key = keyevent.key()
    #    if key == qt.Qt.Key_Plus:
    #        self.focusRectangleSize += 3
    #        if self.focusRectangleSize > 99:
    #            self.focusRectangleSize = 99
    #    elif key == qt.Qt.Key_Minus:
    #        self.focusRectangleSize -= 3
    #        if self.focusRectangleSize < 12:
    #            self.focusRectangleSize = 12
    #    else: return
    #    
    #    self.focusDrawingRectangle.setWidthNHeight(self.focusRectangleSize,self.focusRectangleSize)
    
    #def showFocusGrab(self,state) :
    #    self.focusPointSelected = None
    #    if state:
    #        self.focusDrawingRectangle.startDrawing()
    #    else:
    #        self.focusDrawingRectangle.stopDrawing()
    #        self.focusDrawingRectangle.hide()
    #        self.focusPointSelected = None
            
    #def setFocusPointSelected(self,drawingMgr) :
    #    self.focusPointSelected = drawingMgr.point()
    #    if self.focusMotHwo is not None:
    #        self.focusState.start()
            
    def beamPositionChanged(self, beamy, beamz):
        self.YBeam = beamy
        self.ZBeam = beamz
    
    def pixelCalibrationChanged(self, sizey, sizez):
        if sizey is not None:
            self.YSize = sizey * 1000
            try:
		self.__measureDialog.setXPixelSize(sizey)
            except:
                pass
        else:
            self.YSize = None
        
        if sizez is not None:
            self.ZSize = sizez * 1000
            try:
                self.__measureDialog.setYPixelSize(sizez)
            except:
                pass
        else:
            self.ZSize = None

    def setMoveToState(self,state):
        if self.movetoAction is not None:
            self.movetoAction.setState(state)

    def movetoStateChanged(self,state) :
        if self.movetoColorWhenActivate:
            if state:
                self.movetoAction.setPaletteBackgroundColor(qt.QColor(self.movetoColorWhenActivate))
            else:
                self.movetoAction.setPaletteBackgroundColor(self.oldMoveToActionColor)
        
    def pointSelected(self, drawingMgr):
        if self.horMotHwo is not None and self.verMotHwo is not None:
            if  self.YSize is not None and \
                self.ZSize is not None and \
                self.YBeam is not None and \
                self.ZBeam is not None :
                
                self.drawingMgr =  drawingMgr 
                   
                (y, z) = drawingMgr.point()
                
                self.drawingMgr.stopDrawing()

                sign = 1
                if self.horMotHwo.unit < 0:
                    sign = -1
                movetoy = - sign*(self.YBeam - y) * self.YSize

                sign = 1
                if self.verMotHwo.unit < 0:
                    sign = -1
                movetoz = - sign*(self.ZBeam - z) * self.ZSize
                
                self.motorArrived = 0
            
                self.connect(self.horMotHwo, qt.PYSIGNAL("moveDone"),
                             self.moveFinished)
                self.connect(self.verMotHwo, qt.PYSIGNAL("moveDone"),
                             self.moveFinished)

                self.horMotHwo.moveRelative(movetoy)
                self.verMotHwo.moveRelative(movetoz)
    def __movetoMosaicStateChanged(self,state):
        if self.movetoColorWhenActivate:
            if state:
                self.__movetoActionMosaic.setPaletteBackgroundColor(qt.QColor(self.movetoColorWhenActivate))
            else:
                self.__movetoActionMosaic.setPaletteBackgroundColor(self.__oldMoveToMosaicActionColor)

    def __mosaicPointSelected(self,drawingMgr) :
        point = drawingMgr.mosaicPoints()
        try:
            point = point[0]
            beamY,beamZ = point.refPoint
            YSize,ZSize = point.calibration
            horMotorPos,verMotorPos = point.absPoint
            y,z = point.point
            imageId = point.imageId
        except TypeError: return        # The click wasn't on image

        self.drawingMgr = drawingMgr
        
        drawingMgr.stopDrawing()

        sign = 1
        if self.horMotHwo.unit < 0:
            sign = -1
        movetoy = horMotorPos - sign*(beamY - y) * YSize

        sign = 1
        if self.verMotHwo.unit < 0:
            sign = -1
        movetoz = verMotorPos - sign*(beamZ - z) * ZSize

        self.motorArrived = 0
        
        self.connect(self.horMotHwo, qt.PYSIGNAL("moveDone"),
                     self.moveFinished)
        self.connect(self.verMotHwo, qt.PYSIGNAL("moveDone"),
                     self.moveFinished)

        self.horMotHwo.move(movetoy)
        self.verMotHwo.move(movetoz)

        self.emit(qt.PYSIGNAL("mosaicImageSelected"), (imageId,))


    def moveFinished(self, ver, mne):
        if mne == self.horMotHwo.getMotorMnemonic():
            self.disconnect(self.horMotHwo, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.motorArrived = self.motorArrived + 1
            
        if mne == self.verMotHwo.getMotorMnemonic():
            self.disconnect(self.verMotHwo, qt.PYSIGNAL("moveDone"),
                            self.moveFinished)
            self.motorArrived = self.motorArrived + 1
                        
        if self.motorArrived == 2:
            self.drawingMgr.startDrawing()
            self.motorArrived = 0
            self.emit(qt.PYSIGNAL("moveDone"), (self.YBeam, self.ZBeam))
