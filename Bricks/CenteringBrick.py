import numpy
from scipy import optimize

import logging

import qt
import qtcanvas

from BlissFramework.BaseComponents import BlissWidget

from Qub.Objects.QubDrawingManager import QubLineDrawingMgr,QubPointDrawingMgr
from Qub.Objects.QubDrawingEvent import Qub2PointClick
from Qub.Objects.QubDrawingCanvasTools import QubCanvasVLine,QubCanvasHLine,QubCanvasTarget


class CenteringBrick(BlissWidget) :
    def __init__(self,*args) :
        BlissWidget.__init__(self,*args)
        self.__widgetTree = self.loadUIFile('Centering.ui')
        self.__widgetTree.reparent(self,qt.QPoint(0,0))
        layout = qt.QHBoxLayout(self,11,6,'layout')
        layout.addWidget(self.__widgetTree)
        self.__centeringPlug = None

        self.__currentXSize,self.__currentYSize = 0,0 # current pixel size
        self.__verticalPhi = True
        self.pxclient = None
       
        self.beam_pos = (None, None)
 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('clockwise','boolean',False)
        self.addProperty('table_y_inverted', 'boolean', False)
        self.addProperty('table_z_inverted', 'boolean', False)
 
                        ####### SIGNAL #######
        self.defineSignal('getView',())
        self.defineSignal('getBeamPosition',())
 
                        ####### SLOTS #######
        self.defineSlot("changePixelScale",())

    def changePixelScale(self,sizex,sizey) :
        self.__currentXSize,self.__currentYSize = sizex,sizey

    def getPixelSize(self) :
        return self.__currentXSize,self.__currentYSize

    def propertyChanged(self,property,oldValue,newValue):
        if property == 'mnemonic':
            equipment = self.getHardwareObject(newValue)
            if equipment is not None :
                    xoryMotor = equipment.getDeviceByRole('horizontal')
                    if xoryMotor is not None:
                        self.__verticalPhi = True
                    else:
                        xoryMotor = equipment.getDeviceByRole('vertical')
                        if xoryMotor is None:
                            logging.getLogger().error('%s: could not find motors horizontal nor vertical motor in Hardware Objects %s',
                                                      str(self.name()),equipment.name())
                            return
                        self.__verticalPhi = False

                    zMotor = equipment.getDeviceByRole('inBeam')
                    rMotor = equipment.getDeviceByRole('rotation')
                    if zMotor is None or rMotor is None :
                        logging.getLogger().error('%s: could not find motors inBeam or rotation motor in Hardware Objects %s',
                                                  str(self.name()),equipment.name())
                        return
                    table_y = equipment.getDeviceByRole('table_y')
                    table_z = equipment.getDeviceByRole('table_z')
                    self.__centeringPlug = _centeringPlug(self,self.__widgetTree,xoryMotor,zMotor,rMotor,table_y,table_z,self.getProperty('table_y_inverted'), self.getProperty('table_z_inverted'))
                    self.__centeringPlug.setVerticalPhi(self.__verticalPhi)
 

    def run(self) :
        try :
            key = {}
            self.emit(qt.PYSIGNAL("getView"), (key,))
            try:
                drawing = key['drawing']
            except:
                drawing = None

            if drawing is not None :
                if self.__centeringPlug is not None :
                    self.__centeringPlug.setView(drawing)
            else :
                logging.getLogger().error('view is not connected from CenteringBrick')

            """
            get beam position
            """
            position = {}
            self.emit(qt.PYSIGNAL("getBeamPosition"), (position,))
            try:
              self.beam_pos = (position["ybeam"], position["zbeam"])
            except:
              logging.getLogger().debug("%s: No Beam Position", self.name())
            else:
              self.__centeringPlug.bx = position["ybeam"]
              self.__centeringPlug.by = position["zbeam"]
        except:
            logging.getLogger().exception("%s: exception in run()", self.name())

    def multiPointCentre(self,z,phis) :
        fitfunc = lambda p,x: p[0] * numpy.sin(x+p[1]) + p[2]
        errfunc = lambda p,x,y: fitfunc(p,x) - y
        p1,sucess = optimize.leastsq(errfunc,[1.,0.,0.],args = (phis,z))
        return p1
    
                 ####### CENTERING INTERFACE #######
class _centeringPlug :
    def __init__(self,brick,widgetTree,xoryMotor,zMotor,rMotor,tableyMotor, tablezMotor, table_y_inverted, table_z_inverted) :
        self.__brick = brick
        self.__zMotor,self.__xoryMotor,self.__rotationMotor = zMotor,xoryMotor,rMotor
        self.__widgetTree = widgetTree
        self.endAlignementFlag = False
        self.alignementProcedureOff = True
        self.hLines = []
        self.motorReadyFlag = False
        self.bx=None
        self.by=None
        self.__tableYMotor=tableyMotor
        self.__tableZMotor=tablezMotor
        self.table_y_inverted=table_y_inverted
        self.table_z_inverted=table_z_inverted
 
        alignementTable = self.__widgetTree.child('alignementTable')
        header = alignementTable.horizontalHeader()
        header.setLabel(0,rMotor.userName())

        phiStepLineEditor= self.__widgetTree.child('__deltaPhiCalib')
        phiStepLineEditor.setValidator(qt.QDoubleValidator(self.__widgetTree))
        
                    ####### ALIGNMENT TYPE #######
        self.nbPoint4Alignement = 3
        self.alignementProcessState = _cancelAlignementProcess(self,self.__widgetTree)

        self.__centerRotation = None
        self.__helpLines = []

                      ####### QT SIGNAL #######
        startAlignementButton = self.__widgetTree.child('__startAlignement')
        qt.QObject.connect(startAlignementButton,qt.SIGNAL('clicked()'),self.__startAlignement)

        cancelAlignementButton = self.__widgetTree.child('__cancelAlignement')
        qt.QObject.connect(cancelAlignementButton,qt.SIGNAL('clicked()'),self.__cancelAlignementButton)

        showCenter = self.__widgetTree.child('__showCenter')
        qt.QObject.connect(showCenter,qt.SIGNAL('toggled(bool)'),self.__showCenter)
        
        showHelpLines = self.__widgetTree.child('__helpLines')
        qt.QObject.connect(showHelpLines,qt.SIGNAL('toggled(bool)'),self.__showHelpLines)
        
                   ####### BRICK CONNECTION #######
        self.__brick.connect(self.__rotationMotor, qt.PYSIGNAL("stateChanged"), self.__updateMotorState)
        
    def __del__(self) :
        self.__brick.disconnect(self.__rotationMotor, qt.PYSIGNAL("stateChanged"), self.__updateMotorState)

    def __updateMotorState(self,state) :
        self.motorReadyFlag = state == self.__rotationMotor.READY

    def __startAlignement(self) :
        try:
            self.alignementProcessState.begin()
        except:
            logging.getLogger().exception("_centeringPlug: could not start alignment")
            
    def __cancelAlignementButton(self) :
        try:
           self.alignementProcessState.cancel()
        except:
           logging.getLogger().exception("_centeringPlug: exception in cancel alignment")

    def endAlignementDraw(self,aDrawingMgr) :
        self.alignementProcessState.endDraw(aDrawingMgr)

    def endHline(self,aDrawingMgr) :
        self.alignementProcessState.endHline(aDrawingMgr)

        
    def setView(self,view) :
        self.alignementProcessState.setView(view)
                    ####### CENTER DRAWING #######
        self.__centerRotation = QubPointDrawingMgr(view.canvas(),view.matrix())
        self.__centerRotation.setCanBeModify(False)
        target = QubCanvasTarget(view.canvas())
        self.__centerRotation.addDrawingObject(target)
        view.addDrawingMgr(self.__centerRotation)
        self.__centerRotation.setColor(qt.QColor('red'))

                      ####### Help lines #######
        self.__helpLines = []
        for i in range(3) :
            dMgr = QubPointDrawingMgr(view.canvas(),view.matrix())
            view.addDrawingMgr(dMgr)
            if self.alignementProcessState.verticalPhi() :
                line = QubCanvasVLine(view.canvas())
            else:
                line = QubCanvasHLine(view.canvas())
            dMgr.addDrawingObject(line)
            if not i :
                dMgr.setCanBeModify(False)
                dMgr.setPen(qt.QPen(qt.Qt.red,1,qt.Qt.DashLine))
            else:
                dMgr.setPen(qt.QPen(qt.Qt.red,2))
                dMgr.setEndDrawCallBack(self.__helpLineMoved)
            self.__helpLines.append(dMgr)
            
    def getPhi(self) :
        return self.__rotationMotor.getPosition()

    def mvPhi(self,step) :
        self.__rotationMotor.moveRelative(step)

    def setVerticalPhi(self,aFlag) :
        self.alignementProcessState.setVerticalPhi(aFlag)

    def __showCenter(self,actifFlag) :
        if actifFlag :
            if self.endAlignementFlag :
                self.__centerRotation.show()
        else:
            self.hideCenter()
            
    def showCenterIfNeed(self) :
        try:
            showCenterFlag = self.__widgetTree.child('__showCenter')
            if self.endAlignementFlag :
                at = self.__widgetTree.child('alignementTable')
                phis = []
                z = []
                averagePos = 0
                invertSigned = 1
                if self.__brick['clockwise']:
                    invertSigned = -1

                for rowid in range(self.nbPoint4Alignement) :
                    phiPos = str(at.text(rowid,0))
                    phis.append(float(phiPos) * numpy.pi / 180. * invertSigned)

                    x = str(at.text(rowid,1))
                    y = str(at.text(rowid,2))
                    if self.alignementProcessState.verticalPhi() :                    
                        z.append(float(x))
                        averagePos += float(y) / self.nbPoint4Alignement
                    else:
                        z.append(float(y))
                        averagePos += float(x) / self.nbPoint4Alignement

                rayon,alpha,offset = self.__brick.multiPointCentre(z, phis)
                xSize,ySize = self.__brick.getPixelSize()
                try:
                    stepUnit = self.__xoryMotor.getProperty('unit')
                except:
                    logging.getLogger().error('motors must have a unit field')
                    return

                xSize /= stepUnit
                ySize /= stepUnit

                if self.alignementProcessState.verticalPhi() : # VERTICAL
                    motx = rayon * numpy.sin(alpha)
                    motz = rayon * numpy.cos(alpha)
                    self.__xoryMotor.moveRelative(float(motx * xSize))
                    self.__zMotor.moveRelative(float(motz * xSize))
                    self.__centerRotation.setPoint(offset,averagePos)
                else:
                    moty = rayon * numpy.sin(alpha)
                    motz = rayon * numpy.cos(alpha)
                    self.__xoryMotor.moveRelative(float(moty * ySize))
                    self.__zMotor.moveRelative(float(motz * ySize))
                    self.__centerRotation.setPoint(averagePos,offset)
                    
                if showCenterFlag.isOn() :
                    self.__centerRotation.show()

                if self.bx is not None and self.by is not None:
                    if self.__tableYMotor is not None and self.__tableZMotor is not None:
                      # move center of rotation to beam
                      x,y = self.__centerRotation.point()
                      #logging.getLogger().info("CENTER OF ROTATION IS %f,%f", x, y)
                      self.__tableYMotor.moveRelative(float((self.table_y_inverted and xSize or -xSize)*(x-self.bx)))
                      self.__tableZMotor.moveRelative(float((self.table_z_inverted and ySize or -ySize)*(y-self.by)))
        except:
            logging.getLogger().exception("_centeringPlug: could not center")
            
    def hideCenter(self) :
        self.__centerRotation.hide()

    def __helpLineMoved(self,aDrawingMgr) :
        if aDrawingMgr == self.__helpLines[1] :
            fx,fy = aDrawingMgr.point()
            sx,sy = self.__helpLines[2].point()
        else:
            fx,fy = aDrawingMgr.point()
            sx,sy = self.__helpLines[1].point()
        self.__helpLines[0].setPoint((fx + sx) / 2,(fy + sy) / 2)

    def __showHelpLines(self,aFlag) :
        for i,line in enumerate(self.__helpLines) :
            if aFlag :
                line.show()
                if not i :
                    line.setPen(qt.QPen(qt.Qt.red,1,qt.Qt.DashLine))
                else:
                    line.setPen(qt.QPen(qt.Qt.red,2))
            else:
                line.hide()

                   ####### Alignment State #######
class _alignementProcess :
    def __init__(self,centeringPlug,widgetTree,view,verticalPhi) :
        self._centeringPlug = centeringPlug
        self._widgetTree = widgetTree
        self._view = view
        self._vertPhiFlag = verticalPhi
        self._lastDrawing = None
        centeringPlug.alignementProcessState = self
        
    def __del__(self) :
        if self._lastDrawing is not None:
            self._lastDrawing.stopDrawing()

    def begin(self) :
        pass
    
    def endDraw(self,aDrawingMgr) :
        pass
    def cancel(self) :
        _cancelAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)

    def setView(self,view) :
        self._view = view

    def setVerticalPhi(self,aFlag) :
        self._vertPhiFlag = aFlag
    def verticalPhi(self) :
        return self._vertPhiFlag
    
    def _clearTable(self) :
        at = self._widgetTree.child('alignementTable')
        self._centeringPlug.nbPoint4Alignement = self._widgetTree.child('__nbPoint').value()
        at.setNumRows(self._centeringPlug.nbPoint4Alignement)
        
        for rowid in range(at.numRows()) :
            for colid in range(at.numCols()) :
                at.setText(rowid,colid,'')
                
    def _insertPos(self,aDrawingMgr,rowid) :
        phiPos = str(self._centeringPlug.getPhi())
        x,y = aDrawingMgr.point()

        aDrawingMgr.hide()

        at = self._widgetTree.child('alignementTable')
        at.setText(rowid,0,phiPos)
        at.setText(rowid,1,str(x))
        at.setText(rowid,2,str(y))
        
    def _startDraw(self) :
        self._lastDrawing = QubPointDrawingMgr(self._view.canvas(),self._view.matrix())
        drawingobject = QubCanvasTarget(self._view.canvas())
        
        self._lastDrawing.setAutoDisconnectEvent(True)
        self._lastDrawing.setEventName('StickAlignement')
        self._lastDrawing.setExceptExclusiveListName(['HelpLine'])
        self._lastDrawing.addDrawingObject(drawingobject)
        self._view.addDrawingMgr(self._lastDrawing)
        self._lastDrawing.startDrawing()
        self._lastDrawing.setEndDrawCallBack(self._centeringPlug.endAlignementDraw)

    def _helpLineDraw(self) :
        hline = QubPointDrawingMgr(self._view.canvas(),self._view.matrix())
        hline.setAutoDisconnectEvent(True)
        hline.setEventName('HelpLine')
        hline.setExceptExclusiveListName(['StickAlignement'])
        if self._vertPhiFlag :
            drawingobject = QubCanvasHLine(self._view.canvas())
        else :
            drawingobject = QubCanvasVLine(self._view.canvas())
        hline.addDrawingObject(drawingobject)
        hline.setEndDrawCallBack(self._centeringPlug.endHline)
        self._view.addDrawingMgr(hline)
        hline.setPen(qt.QPen(qt.Qt.red,2,qt.Qt.DashLine))

        hline.startDrawing()
        self._centeringPlug.hLines.append(hline)
        
    def _phiStep(self) :
        phiStepLineEditor = self._widgetTree.child('__deltaPhiCalib')
        step,valid = phiStepLineEditor.text().toFloat()
        self._centeringPlug.mvPhi(step)

    def endHline(self,drawingMgr) :
        pass
        
    
class _cancelAlignementProcess(_alignementProcess) :
    def __init__(self,centeringPlug,widgetTree,view = None,verticalPhi = True) :
        _alignementProcess.__init__(self,centeringPlug,widgetTree,view,verticalPhi)

        self._clearTable()

        centeringPlug.alignementProcedureOff = True
        
        cancelButton = self._widgetTree.child('__cancelAlignement')
        cancelButton.setEnabled(False)

        startAlignementButton = self._widgetTree.child('__startAlignement')
        startAlignementButton.setEnabled(True)

        phiStepLineEditor = self._widgetTree.child('__deltaPhiCalib')
        phiStepLineEditor.setEnabled(True)


        self._centeringPlug.hLines = []
        
    def __del__(self) :
        self._clearTable()
        self._centeringPlug.alignementProcedureOff = True

        cancelButton = self._widgetTree.child('__cancelAlignement')
        cancelButton.setEnabled(True)

        startAlignementButton = self._widgetTree.child('__startAlignement')
        startAlignementButton.setEnabled(False)

        phiStepLineEditor = self._widgetTree.child('__deltaPhiCalib')
        phiStepLineEditor.setEnabled(False)

    def cancel(self) :
        pass

    def begin(self) :
        _beginAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)

              
class _beginAlignementProcess(_alignementProcess) :
    def __init__(self,centeringPlug,widgetTree,view,verticalPhi) :
        _alignementProcess.__init__(self,centeringPlug,widgetTree,view,verticalPhi)
        self._startDraw()
        self._lastDrawing.setActionInfo('Start alignement, select the first point')
        self._helpLineDraw()
        
    def endDraw(self,aDrawingMgr) :
        self._insertPos(aDrawingMgr,0)
        _secondStepAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)

class _secondStepAlignementProcess(_alignementProcess) :
    def __init__(self,centeringPlug,widgetTree,view,verticalPhi) :
        _alignementProcess.__init__(self,centeringPlug,widgetTree,view,verticalPhi)
        self.__nbPoint = 1
        self.__init()
        
    def __init(self) :
        self._startDraw()
        self._lastDrawing.setActionInfo('In alignement procedure, select %d point' % (self.__nbPoint + 1))
        self._phiStep()
        
    def endDraw(self,aDrawingMgr) :
        self._insertPos(aDrawingMgr,self.__nbPoint)
        self.__nbPoint += 1
        if self.__nbPoint < self._centeringPlug.nbPoint4Alignement - 1 :
            self.__init()
        else:
            _lastStepAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)

class _lastStepAlignementProcess(_alignementProcess) :
    def __init__(self,centeringPlug,widgetTree,view,verticalPhi) :
        _alignementProcess.__init__(self,centeringPlug,widgetTree,view,verticalPhi)
        self._startDraw()
        self._lastDrawing.setActionInfo('End alignement procedure, select last point')
        self._phiStep()

    def endDraw(self,aDrawingMgr) :
        self._insertPos(aDrawingMgr,self._centeringPlug.nbPoint4Alignement - 1)
        _endAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)

class _endAlignementProcess(_alignementProcess) :
    def __init__(self,centeringPlug,widgetTree,view,verticalPhi) :
        _alignementProcess.__init__(self,centeringPlug,widgetTree,view,verticalPhi)

        centeringPlug.endAlignementFlag = True
        centeringPlug.alignementProcedureOff = True

        startAlignementButton = self._widgetTree.child('__startAlignement')
        startAlignementButton.setEnabled(True)
            
        cancelButton = self._widgetTree.child('__cancelAlignement')
        cancelButton.setEnabled(False)

        phiStepLineEditor = self._widgetTree.child('__deltaPhiCalib')
        phiStepLineEditor.setEnabled(True)
     
        self._centeringPlug.hLines = []
        
        self._centeringPlug.showCenterIfNeed()
        
    def __del__(self) :
        self._centeringPlug.endAlignementFlag = False
        self._centeringPlug.alignementProcedureOff = False

        self._clearTable()
        self._centeringPlug.hideCenter()
        
    def begin(self) :
        cancelButton = self._widgetTree.child('__cancelAlignement')
        cancelButton.setEnabled(True)
 
        startAlignementButton = self._widgetTree.child('__startAlignement')
        startAlignementButton.setEnabled(False)

        phiStepLineEditor = self._widgetTree.child('__deltaPhiCalib')
        phiStepLineEditor.setEnabled(False)

        _beginAlignementProcess(self._centeringPlug,self._widgetTree,self._view,self._vertPhiFlag)
