"""
[Name] LookupScanBrick

[Description]

It's like a mesh with rotation and exclude/include scan points posibility

[Properties]

-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| command     | string | file name of the spec commands (See below Hardware Object)
| horizontal  | string  | horizontal motors list for scan
| vertical    | string  | vertical motors list for scan
| offsetmeasure| float | offset use to display measure like distance and step (default mm)
-----------------------------------------------------------------------

[Signals]

[Slots]

-------------------------------------------------------------------
| name                | arguments                  | description
-------------------------------------------------------------------
| ChangePixelCalibration | pixel_x_size,pixel_y_size | pixel size calibration 
| ChangeBeamPosition | xBeam,yBeam | beam position
-------------------------------------------------------------------

[Comments]

[HardwareObjects]

 - command, You must have in your xml file at least this 2 entries :
    <command type="spec" name="ltscan">ltscan</command>
    <command type="spec" name="ltinit">ltinit</command>
 - horizontal and vertical can be a simple motor list :
    <equipment>
     <motors>
           <device hwrid="/seb/samy"/>
           <device hwrid="/seb/sampz"/>
     </motors>
    </equipment>
    and motor must have a <b>unit field</b>:
    <device class = "SpecMotor">
      <username>samy</username>
      <specname>samy</specname>
      <unit>1e-6</unit>
      <specversion>plouf:seb</specversion>
    </device>
"""
import math
import qt,qttable,qtcanvas
import logging
import numpy
import itertools
import datetime
from BlissFramework.Utils.GraphicScan import BaseGraphicScan
from BlissFramework import Icons

from SpecClient import SpecVariable,SpecArray

from Qub.Objects.QubDrawingManager import QubPolygoneDrawingMgr
from Qub.Objects.QubDrawingCanvasTools import QubCanvasGrid
from Qub.Objects.QubDrawingCanvasTools import QubCanvasCloseLinePolygone
from Qub.CTools import polygone

__category__ = 'Scans'

class LookupScanBrick(BaseGraphicScan) :
    def __init__(self,parent,name,uifile = 'LookupScan.ui',cmd_name = 'ltscan',**kwargs) :
        BaseGraphicScan.__init__(self, parent, name, uifile=uifile, cmd_name=cmd_name, **kwargs)
        self._graphicSelection = None
        self.__polyNb = 0
        self.__gridPoints = None
        self._matchPoints = None
        self.__offsetMeasure = 1e3
        self._ltinit = None
        
        self.addProperty('offsetmeasure','float',1e3)
        
        table = self._widgetTree.child('__gridTable')
        qt.QObject.connect(table,qt.SIGNAL('valueChanged(int,int)'),self._valueChangedScanParam)

        timeWidget = self._widgetTree.child('__time')
        timeWidget.setValidator(qt.QDoubleValidator(timeWidget))
        # PopUp Menu
        self.__polygonListWidget = self._widgetTree.child('__polygonList')
        self.__polygonListWidget.setSelectionMode(qt.QListView.Extended)

        self.__polygonPopUpMenu = qt.QPopupMenu(self.__polygonListWidget)
        for itemName,cbk in [('Create new',self.__createPolygon),
                             ('Remove',self.__removeSelectedPolygon),
                             ('Revert selection',self.__revertSelectedPolygon)] :
            self.__polygonPopUpMenu.insertItem(itemName,cbk)

        self.connect(self.__polygonListWidget,qt.SIGNAL('rightButtonPressed(QListViewItem*,const QPoint &,int)'),
                     self.__polygonPopUpDisplay)

        timeWidget = self._widgetTree.child('__time')
        self.connect(timeWidget,qt.SIGNAL('returnPressed()'),self.__refreshInfoText)
        self.connect(timeWidget,qt.SIGNAL('lostFocus()'),self.__refreshInfoText)

    def propertyChanged(self,property,oldValue,newValue) :
        if property == 'offsetmeasure':
            self.__offsetMeasure = newValue
        elif property == 'command' :
            BaseGraphicScan.propertyChanged(self,property,oldValue,newValue)
            ho = self.getHardwareObject(newValue)
            if ho is not None:
                try:
                    self._ltinit = ho.getCommandObject('ltinit')
                    self._ltinit.connectSignal('commandReplyArrived',self.__ltinitFinished)
                except:
                    self._ltinit = None
                    logging.getLogger().error('ltinit not find in command file')
                    startButton = self._widgetTree.child('__startScan')
                    startButton.setEnabled(False)

        else:
            BaseGraphicScan.propertyChanged(self,property,oldValue,newValue)
            
    def _setMotor(self,property,motorList) :
        if property == 'horizontal':
           combo = self._widgetTree.child('__motor1')
        else:
            combo = self._widgetTree.child('__motor2')
        for i in range(combo.count()) :
            combo.removeItem(i)
        combo.insertStringList(motorList)
    
    def _viewConnect(self,view) :
        self._graphicSelection = QubPolygoneDrawingMgr(view.canvas(),
                                                       view.matrix())
        self._graphicSelection.setActionInfo('Grid grab, select the area')
        drawingobject = QubCanvasGrid(view.canvas())
        self._graphicSelection.addDrawingObject(drawingobject)
        
        self._graphicSelection.setEndDrawCallBack(self.__endGridGrab)

        view.addDrawingMgr(self._graphicSelection)

    def __endGridGrab(self,drawingobject) :
       self.__createGridPoints()
       self._updateGUI()
    
    def _updateGUI(self) :
       if self._graphicSelection :
          points = self._graphicSelection.points()
          if len(points) == 3 and self._XSize and self._YSize :
             table = self._widgetTree.child('__gridTable')
             try:
                dist = math.sqrt(((points[0][0] - points[1][0]) * self._XSize ) ** 2 + \
                                 ((points[0][1] - points[1][1]) * self._YSize) ** 2)
                table.setText(0,2,self._formatString % (dist * self.__offsetMeasure))

                dist = math.sqrt(((points[1][0] - points[2][0]) * self._YSize) ** 2 + \
                                 ((points[1][1] - points[2][1]) * self._XSize) ** 2)
                table.setText(1,2,self._formatString % (dist * self.__offsetMeasure))
                self.__refreshSteps()
             except:
                import traceback
                traceback.print_exc()
                
    def _valueChangedScanParam(self,row,column) :
       table = self._widgetTree.child('__gridTable')
       if column == 0:
          stringVal = table.text(row,column)
          val,okFlag = stringVal.toInt()
          if okFlag :
             if row == 0 :
                self._graphicSelection.setNbPointAxis1(val)
             else:
                self._graphicSelection.setNbPointAxis2(val)
             self.__refreshSteps()
             self.__createGridPoints()
          else:
             dialog = qt.QErrorMessage(self)
             dialog.message('Interval must be integer')
       elif column == 1:
          stringVal = table.text(row,column)
          step,ok1 = stringVal.toFloat()
          stringVal = table.text(row,0)
          interval,ok2 = stringVal.toInt()
          if ok1 and step > 0.:
             if ok2:
                distance = interval * step
                table.setText(row,2,self._formatString % distance)
                self._valueChangedScanParam(row,2)
          else:
             dialog = qt.QErrorMessage(self)
             dialog.message('Step must be a positif float')
       elif column == 2:
          self.__refreshSteps()

          # UPDATE GRAPHIC
          points = self._graphicSelection.points()
          if len(points) == 3 :
             angle = self._graphicSelection.angle()[0] * math.pi / 180
             pixelSize = math.sqrt((self._XSize * math.cos(angle)) ** 2 + \
                                   (self._YSize * math.sin(angle)) ** 2)
             if row == 0 :
                stringVal = table.text(0,2)
                dist1,ok1 = stringVal.toFloat()
                dist1 /= self.__offsetMeasure
                
                width = dist1 / pixelSize
                height = math.sqrt(((points[1][0] - points[2][0])) ** 2 + \
                                   ((points[1][1] - points[2][1])) ** 2)
             else:
                width = math.sqrt(((points[0][0] - points[1][0])) ** 2 + \
                                  ((points[0][1] - points[1][1])) ** 2)

                stringVal = table.text(1,2)
                dist2,ok2 = stringVal.toFloat()
                dist2 /= self.__offsetMeasure
                height = dist2 / pixelSize

             xori,yori = points[0]
             p = numpy.array([[xori,yori],[xori + width,yori],[xori + width,yori + height]])
             
             translation = numpy.matrix([xori,yori])
             rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                        [numpy.sin(-angle),numpy.cos(-angle)]])
             p -= translation
             p = p * rotation
             p += translation
             self._graphicSelection.setPoints(p.tolist())

    def __refreshSteps(self) :
        table = self._widgetTree.child('__gridTable')
        # DISTANCE
        stringVal = table.text(0,2)
        dist1,ok1 = stringVal.toFloat()
        stringVal = table.text(1,2)
        dist2,ok2 = stringVal.toFloat()
        # INTERVALS
        if ok1 and ok2 :
           stringVal = table.text(0,0)
           inter1,ok1 = stringVal.toInt()
           if ok1:
              step = dist1 / inter1
              table.setText(0,1,self._formatString % step)

           stringVal = table.text(1,0)
           inter2,ok2 = stringVal.toInt()
           if ok2 :
              step = dist2 / inter2
              table.setText(1,1,self._formatString % step)

 
    def _movetoStart(self) :
        if not self._matchPoints :
            return
        mot1Widget = self._widgetTree.child('__motor1')
        mot2Widget = self._widgetTree.child('__motor2')
        mot1 = self.__getMotor(mot1Widget.currentText(),self._horizontalMotors)
        mot2 = self.__getMotor(mot2Widget.currentText(),self._verticalMotors)
        try:
            firstPoint = self._matchPoints.index(True)
        except:
            return                      # No scan point
        x,y = self.__gridPoints[firstPoint,0],self.__gridPoints[firstPoint,1]
        try:
            mot1Fp = (x - self._beamx) / mot1.getProperty('unit') * self._XSize
            mot2Fp = (y - self._beamy) / mot2.getProperty('unit') * self._YSize

            mot1Fp += mot1.getPosition()
            mot2Fp += mot2.getPosition()

            mot1.move(float(mot1Fp))
            mot2.move(float(mot2Fp))

            xtranslation,ytranslation = (self._beamx - x,self._beamy - y)
            graphicItems = [x.drawingManager for x in self.__getIterator()]
            graphicItems.append(self._graphicSelection)
            for item in graphicItems :
                newPoint = []
                for x,y in item.points() :
                    x,y = (x + xtranslation,y + ytranslation)
                    newPoint.append((x,y))
                item.setPoints(newPoint)
            translationMatrix = numpy.matrix([xtranslation,ytranslation])
            self.__gridPoints += translationMatrix
            self.__setRegion(False)
            
        except AttributeError :
            import traceback
            traceback.print_exc()
            logging.getLogger().error('motors must have a unit field')

    def _startScan(self) :
        try :
            self._matchPoints.index(True) # if not point math -> go to exception
            mot1Widget = self._widgetTree.child('__motor1')
            mot2Widget = self._widgetTree.child('__motor2')

            self._ltinit(str(mot1Widget.currentText()),str(mot2Widget.currentText()))
        except ValueError:
            dialog = qt.QErrorMessage(self)
            dialog.message('Nothing to scan')
            return
        
    def __ltinitFinished(self,*args) :
        table = self._widgetTree.child('__gridTable')
        stringVal = table.text(0,0)
        nbColumn,valid = stringVal.toInt()
        if not valid :
            dialog = qt.QErrorMessage(self)
            dialog.message('Interval must be integer')
            return

        nbColumn += 1
        self._logArgs['scan_type'] = 'lookup'
        posMot1 = []
        posMot2 = []
        pointMatchNb = 0
        matchPointId = []
        for i,(match,point) in enumerate(itertools.izip(self._matchPoints,self.__gridPoints)) :
            if match :
                posMot1.append(point[0,0])
                posMot2.append(point[0,1])
                matchPointId.append((i / nbColumn,pointMatchNb))
                pointMatchNb += 1
                
        if posMot1:
            mot1Widget = self._widgetTree.child('__motor1')
            mot2Widget = self._widgetTree.child('__motor2')

            timeWidget = self._widgetTree.child('__time')
            ctime,valid = timeWidget.text().toFloat()
            
            mot1 = self.__getMotor(mot1Widget.currentText(),self._horizontalMotors)
            mot2 = self.__getMotor(mot2Widget.currentText(),self._verticalMotors)
            
            posMot1 = numpy.array(posMot1)
            posMot1 -= self._beamx
            posMot1 *= (self._XSize / mot1.getProperty('unit'))
            posMot1 += mot1.getPosition()

            
            posMot2 = numpy.array(posMot2)
            posMot2 -= self._beamy
            posMot2 *= (self._YSize / mot2.getProperty('unit'))
            posMot2 += mot2.getPosition()

            lineStartStop = []
            lastLineId = -1
            currentPointInLine = []
            for lineId,pointId in matchPointId:
                if lineId != lastLineId :
                    if currentPointInLine:
                        lineStartStop.append(currentPointInLine)
                    currentPointInLine = [pointId]
                    lastLineId = lineId
                else:
                    currentPointInLine.append(pointId)
            if currentPointInLine :
                lineStartStop.append(currentPointInLine)

            startIndex = []
            stopIndex  = []
            for line in lineStartStop:
                startIndex.append(line[0])
                stopIndex.append(line[-1])

            startIndex = numpy.array(startIndex)
            stopIndex = numpy.array(stopIndex)

            specVersion = self._ltinit.specVersion
            for motor_name,pos_motor in zip([str(mot1Widget.currentText()),str(mot2Widget.currentText())],
                                            [posMot1,posMot2]) :
                ho = self.getHardwareObject(self["command"])
                MOTOR_ARRAY = ho.addChannel({"type":"spec", "version":specVersion,
                                             "name":"MOTOR_ARRAY", "dispatchMode":None},
                                            "%s_ltscan_arr" % motor_name)
                MOTOR_ARRAY.setValue(SpecArray.SpecArray(pos_motor.ravel()))

            LT_START = SpecVariable.SpecVariable('LT_START',specVersion)
            LT_START.setValue(SpecArray.SpecArray(startIndex))
            
            LT_STOP = SpecVariable.SpecVariable('LT_STOP',specVersion)
            LT_STOP.setValue(SpecArray.SpecArray(stopIndex))        

            LT_LINE = SpecVariable.SpecVariable('LT_LINE',specVersion)
            LT_LINE.setValue(len(stopIndex))

            self._SpecCmd(str(mot1Widget.currentText()),str(mot2Widget.currentText()),ctime)
            
    def __getMotor(self,userMotName,motorList) :
        for mot in motorList:
            if mot.getMotorMnemonic() == userMotName:
                return mot
    def _moveGraphicInBeam(self,beamx,beamy) :
        pass

    def __createPolygon(self,nb) :
        try:
            showgButton = self._widgetTree.child('__showGrab')
            showgButton.setOn(True)
            grabButton = self._widgetTree.child('__grabButton')
            grabButton.setOn(False)
            
            polygon = QubPolygoneDrawingMgr(self._view.canvas(),self._view.matrix())
            polygon.setActionInfo('Drawing mask plygon %d' % self.__polyNb)
            polygon.setEndDrawCallBack(self.__polygonCBK)
            polygon.setAutoDisconnectEvent(True)
            drawingObject = QubCanvasCloseLinePolygone(self._view.canvas())
            polygon.addDrawingObject(drawingObject)
            self._view.addDrawingMgr(polygon)
            polygon.setColor(self._view.foregroundColor())
            newItem = qt.QListViewItem(self.__polygonListWidget)
            newItem.setText(0,'Polygon %d' % self.__polyNb)
            newItem.setPixmap(0,Icons.load('Plus2'))
            newItem.drawingManager = polygon
            newItem.includeMode = True
            self.__polyNb += 1
            polygon.startDrawing()
        except:
            import traceback
            traceback.print_exc()

    def __removeSelectedPolygon(self,nb):
        for item in self.__getIterator(True) :
            self.__polygonListWidget.takeItem(item)
        self.__setRegion()
        
    def __revertSelectedPolygon(self,nb) :
        for item in self.__getIterator(True) :
            item.includeMode = not item.includeMode
            if item.includeMode: pixmap = Icons.load('Plus2')
            else: pixmap = Icons.load('Minus2')
            item.setPixmap(0,pixmap)
        self.__setRegion()
        
    def __getIterator(self,selectedFilter = False) :
        Item = self.__polygonListWidget.firstChild()
        while Item:
            NextItem = Item.nextSibling()
            selectedFlag = Item.isSelected()
            if not selectedFilter or selectedFlag :
                yield Item
            Item = NextItem
            
    def __polygonPopUpDisplay(self,item,point,columnid) :
        self.__polygonPopUpMenu.exec_loop(point)

    def __polygonCBK(self,drawingManager) :
        self.__setRegion()
        
    def __createGridPoints(self) :
        # del old grid point
        self.__gridPoints = None

        table = self._widgetTree.child('__gridTable')
        stringVal = table.text(0,0)
        nbAxis1,okFlag = stringVal.toInt()
        if not okFlag: return

        stringVal = table.text(1,0)
        nbAxis2,okFlag = stringVal.toInt()
        if not okFlag: return

        if self._graphicSelection.points() :
            points = numpy.array([[x,y] for x,y in self._graphicSelection.points()])
            angle = self._graphicSelection.angle()[0] * math.pi / 180
            rotation = numpy.matrix([[numpy.cos(angle),-numpy.sin(angle)],
                                     [numpy.sin(angle),numpy.cos(angle)]])
            translation = numpy.matrix([points[0][0],points[0][1]])

            points -= translation
            points = points * rotation


            points = numpy.array([[x,y] for y in numpy.linspace(points[0,1],points[2,1],nbAxis2 + 1) for x in numpy.linspace(points[0,0],points[1,0],nbAxis1 + 1)])

            rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                     [numpy.sin(-angle),numpy.cos(-angle)]])

            self.__gridPoints = points * rotation
            self.__gridPoints += translation
            self.__checkPolygoneItersection()
            
    def __checkPolygoneItersection(self) :
        self._matchPoints = None
        if self.__gridPoints is None : return

        includePolygone,excludePolygone = [],[]
        for item in self.__getIterator() :
            points = item.drawingManager.points()
            if item.includeMode : includePolygone.append(points)
            else: excludePolygone.append(points)

        pointGrid = self.__gridPoints.tolist()
        allInPoints = []
        if includePolygone :
            for points in includePolygone:
                pInPoly = polygone.points_inclusion(pointGrid,points,False)
                if not allInPoints :
                    allInPoints = pInPoly
                else:
                    allInPoints = [x > 0 or y > 0 for x,y in itertools.izip(pInPoly,allInPoints)]

        if not allInPoints :
            allInPoints = [True for x in range(len(self.__gridPoints))]
            
        for points in excludePolygone:
            pInPoly = polygone.points_inclusion(pointGrid,points,False)
            allInPoints = [x > 0 and not y > 0 for x,y in itertools.izip(allInPoints,pInPoly)]
        self._matchPoints = allInPoints
        self.__refreshInfoText()

    def __refreshInfoText(self) :
        if self._matchPoints :
            matchPoint = self._matchPoints.count(True)
            textInfo = self._widgetTree.child('__info')
            timeString = self._widgetTree.child('__time').text()
            time,valid = timeString.toFloat()
            if valid :
                delta = datetime.timedelta(0,time) * matchPoint
                textInfo.setText('%d points in scan until %s' % (matchPoint,
                                                                 (datetime.datetime.today() + delta).strftime('%HH%M')))
            else:
                textInfo.setText('%d points in scan' % matchPoint)
                
    def __setRegion(self,aCheckPolygoneFlag = True) :
        addRegion = []
        minusRegion = []
        for item in self.__getIterator() :
            array = qt.QPointArray(len(item.drawingManager.points()))
            for i,(x,y) in enumerate(item.drawingManager.points()) :
                array.setPoint(i,x,y)
            region = qt.QRegion(array)
            if item.includeMode: addRegion.append(region)
            else: minusRegion.append(region)
        self._graphicSelection.setRegion(addRegion,minusRegion)
        if aCheckPolygoneFlag: self.__checkPolygoneItersection()
        
    def _setColor(self,color) :
        BaseGraphicScan._setColor(self,color)
        for item in self.__getIterator() :
            item.drawingManager.setColor(color)

    def _showGrabScan(self,aFlag) :
        BaseGraphicScan._showGrabScan(self,aFlag)
        for item in self.__getIterator() :
            if aFlag:
                item.drawingManager.show()
            else:
                item.drawingManager.hide()

