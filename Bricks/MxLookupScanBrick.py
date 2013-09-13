import math
import os
import qt,qttable,qtcanvas
import logging
import numpy
import itertools
import datetime
import types
from BlissFramework.Utils.GraphicScan import BaseGraphicScan
from BlissFramework import Icons

from Qub.Objects.QubDrawingManager import QubPolygoneDrawingMgr
from Qub.Objects.QubDrawingCanvasTools import QubCanvasGrid

__category__ = 'Scans'

class MxLookupScanBrick(BaseGraphicScan) :
    def __init__(self,parent,name,uifile = 'MxLookupScan.ui',**kwargs) :
        BaseGraphicScan.__init__(self, parent, name, uifile=uifile, **kwargs)
        self._graphicSelection = None
        self.__gridPoints = None
        self._matchPoints = None
        self.__offsetMeasure = 1e3
        self.old_mot1_pos = None
        self.old_mot2_pos = None
        self._shape_history = None
        
        self.addProperty('offsetmeasure','float',1e3)
        self.defineSignal("addToQueue", ())
        self.defineSignal('clearQueue', ())
        self.defineSignal("dataCollectParametersRequest", ())
        self.defineSignal("goToCollect", ())

        table = self._widgetTree.child('__gridTable')
        qt.QObject.connect(table,qt.SIGNAL('valueChanged(int,int)'),self._valueChangedScanParam)

        timeWidget = self._widgetTree.child('__time')
        timeWidget.setValidator(qt.QDoubleValidator(timeWidget))
        timeWidget = self._widgetTree.child('__time')

    def propertyChanged(self,property,oldValue,newValue):
        if property == 'offsetmeasure':
            self.__offsetMeasure = newValue
        elif property == 'command':
            pass
        else:
            BaseGraphicScan.propertyChanged(self,property,oldValue,newValue)
       
    def run(self):
        BaseGraphicScan.run(self)
        startButton = self._widgetTree.child('__startScan')
        startButton.hide()

        stopButton = self._widgetTree.child('__stopScan')
        stopButton.hide()
        
        if self._horizontalMotors and self._verticalMotors:
       
          startButton.setEnabled(True)
          mot1 = self._horizontalMotors[0]
          mot2 = self._verticalMotors[0]
          self.old_mot1_pos = mot1.getPosition()
          self.old_mot2_pos = mot2.getPosition()
          mot1.connect('positionChanged', self.mot1_position_changed)
          mot2.connect('positionChanged', self.mot2_position_changed)
 
        table = self._widgetTree.child('__gridTable')
        table.setText(0, 0, "2")
        table.setText(1, 0, "2")

    def mot1_position_changed(self, new_pos):
        if self.old_mot1_pos is None:
          self.old_mot1_pos = new_pos
        else:
          if not hasattr(self._graphicSelection, "_xy_in_mm"):
            return
          mot1 = self._horizontalMotors[0]
          dx = new_pos - self.old_mot1_pos
          current_x = self._graphicSelection.x()[0]
          current_y = self._graphicSelection.y()[0]
          new_x = current_x-(dx*mot1.getProperty('unit')/self._XSize)
          self._graphicSelection.move(new_x,current_y, 0)
          points = self._graphicSelection.points()
          self._graphicSelection._xy_in_mm = numpy.array([(points[0][0] - self._beamx) * self._XSize,
                                                          (points[0][1] - self._beamy) * self._YSize])
          self.old_mot1_pos = new_pos

    def mot2_position_changed(self, new_pos):
        if self.old_mot2_pos is None:
          self.old_mot2_pos = new_pos
        else:
          if not hasattr(self._graphicSelection, "_xy_in_mm"): 
            return
          mot2=self._verticalMotors[0]
          dy = new_pos - self.old_mot2_pos
          current_x = self._graphicSelection.x()[0]
          current_y = self._graphicSelection.y()[0]
          new_y = current_y-(dy*mot2.getProperty('unit')/self._YSize)
          self._graphicSelection.move(current_x, new_y, 0)
          points = self._graphicSelection.points()
          self._graphicSelection._xy_in_mm = numpy.array([(points[0][0] - self._beamx) * self._XSize,
                                                          (points[0][1] - self._beamy) * self._YSize])
          self.old_mot2_pos = new_pos

    def _setMotor(self,property,motorList):
        pass

    def _viewConnect(self,view) :
        self._graphicSelection = QubPolygoneDrawingMgr(view.canvas(),
                                                       view.matrix())
        self._graphicSelection.setActionInfo('Grid grab, select the area')
        drawingobject = QubCanvasGrid(view.canvas())
        self._graphicSelection.addDrawingObject(drawingobject)
        
        self._graphicSelection.setEndDrawCallBack(self.__endGridGrab)

        view.addDrawingMgr(self._graphicSelection)

    def __endGridGrab(self,drawingobject):
       self.__createGridPoints()
       points = self._graphicSelection.points()
       if len(points) == 3 and self._XSize and self._YSize:
             self._graphicSelection._xy_in_mm = numpy.array([(points[0][0] - self._beamx) * self._XSize,
					                     (points[0][1] - self._beamy) * self._YSize])
             table = self._widgetTree.child('__gridTable')
             dist = math.sqrt(((points[0][0] - points[1][0]) * self._XSize ) ** 2 + \
                                 ((points[0][1] - points[1][1]) * self._YSize) ** 2)
             table.setText(0,2,self._formatString % (dist * self.__offsetMeasure))

             dist = math.sqrt(((points[1][0] - points[2][0]) * self._YSize) ** 2 + \
                                 ((points[1][1] - points[2][1]) * self._XSize) ** 2)
             table.setText(1,2,self._formatString % (dist * self.__offsetMeasure))
             self.__refreshSteps()
    
    def _updateGUI(self):
       if self._graphicSelection:
         if self._XSize and self._YSize:
            #showgButton = self._widgetTree.child('__showGrab')
            #if showgButton.isOn():
            #  self._graphicSelection.show()
            self._valueChangedScanParam(0,2)
            self._valueChangedScanParam(1,2)
         else:
            pass
            #self._graphicSelection.hide() 
                
    def _valueChangedScanParam(self,row,column) :
       table = self._widgetTree.child('__gridTable')
       if column == 0:
          stringVal = table.text(row,column)
          val,okFlag = stringVal.toInt()
          if okFlag :
             self.__refreshSteps()
             if row == 0 :
                self._graphicSelection.setNbPointAxis1(val-1)
             else:
                self._graphicSelection.setNbPointAxis2(val-1)
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
             dialog.message('Step must be a positive float')
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

             xori = (self._graphicSelection._xy_in_mm[0] / self._XSize) + self._beamx
             yori = (self._graphicSelection._xy_in_mm[1] / self._YSize) + self._beamy
             #xori, yori = points[0]
	     
             #p = numpy.array([[xori,yori],[xori + width,yori],[xori + width,yori + height]])
             p = numpy.array([[0,0],[width,0],[width,height]])
             
             translation = numpy.matrix([xori,yori])
             rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                        [numpy.sin(-angle),numpy.cos(-angle)]])
             #p -= translation
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
           inter1 = inter1 - 1
           if inter1 < 1:
             qt.QMessageBox.warning(self, "Invalid value for points per line", "There should be at least 2 points per line for mesh", qt.QMessageBox.Ok)
             return
           if ok1:
              step = dist1 / inter1
              table.setText(0,1,self._formatString % step)

           stringVal = table.text(1,0)
           inter2,ok2 = stringVal.toInt()
           inter2 = inter2 - 1
           if inter2 < 1:
               qt.QMessageBox.warning(self, "Invalid value for points per line", "There should be at least 2 points per line for mesh", qt.QMessageBox.Ok)
               return
           if ok2 :
               step = dist2 / inter2
               table.setText(1,1,self._formatString % step)
        if not self._matchPoints:
          self.emit(qt.PYSIGNAL("addToQueue"), ({}, ))
          return
        try:
          firstPoint = self._matchPoints.index(True)
        except:
          self.emit(qt.PYSIGNAL("addToQueue"), ({}, ))
          return
        mot1 = self._horizontalMotors[0]
        mot2 = self._verticalMotors[0]
        x,y = self.__gridPoints[firstPoint,0],self.__gridPoints[firstPoint,1]
        angle = self._graphicSelection.angle()[0]

        self._shape_history.add_grid({"dx_mm": float(dist1),
                                      "dy_mm": float(dist2),
                                      "steps_x": int(inter1)+1,
                                      "steps_y": int(inter2)+1,
                                      "x1": float((x - self._beamx) / mot1.getProperty('unit') * self._XSize),
                                      "y1": float((y - self._beamy) / mot2.getProperty('unit') * self._YSize),
                                      "angle": angle})
        
        self.emit(qt.PYSIGNAL("addToQueue"), ({ "dx_mm": float(dist1),
                                                "dy_mm": float(dist2),
                                                "steps_x": int(inter1)+1,
                                                "steps_y": int(inter2)+1,
                                                "x1": float((x - self._beamx)/ mot1.getProperty('unit') * self._XSize),
                                                "y1": float((y - self._beamy)/ mot2.getProperty('unit') * self._YSize) }, ))

 
    def _movetoStart(self) :
        if not self._matchPoints :
            return
        mot1 = self._horizontalMotors[0]
        mot2 = self._verticalMotors[0]
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
            translationMatrix = numpy.matrix([xtranslation,ytranslation])
            self.__gridPoints += translationMatrix
            self._moveGraphicInBeam(self._beamx,self._beamy)
        except AttributeError :
            logging.getLogger().exception("motors must have a unit field")

    def _startScan(self):
        self._scanFinished()

        try :
            self._matchPoints.index(True) # if not point math -> go to exception
        except ValueError:
            dialog = qt.QErrorMessage(self)
            dialog.message('Nothing to scan')
            return

        table = self._widgetTree.child('__gridTable')
        stringVal = table.text(0,0)
        nbColumn,valid = stringVal.toInt()
        if not valid :
            dialog = qt.QErrorMessage(self)
            dialog.message('Interval must be integer')
            return

        nbColumn += 1
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
            timeWidget = self._widgetTree.child('__time')
            ctime,valid = timeWidget.text().toFloat()
            if not valid :
              dialog = qt.QErrorMessage(self)
              dialog.message('Time must be float')
              return

            mot1 = self._horizontalMotors[0]
            mot2 = self._verticalMotors[0]
            
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

            self.emit(qt.PYSIGNAL("clearQueue"), (0, )) #clear entire queue
            params = {}
            self.emit(qt.PYSIGNAL("dataCollectParametersRequest"), (params,))
            # determine points and add to queue
            collectList = []
            params["exposure_time"]=str(ctime)
            params["directory"]=os.path.join(params["directory"], "mesh")
            params["osc_range"]="0.5"
            params["number_images"]="1"
            params["osc_start"]=params["current_osc_start"]

            motor1_name = mot1.getMotorMnemonic()
            motor2_name = mot2.getMotorMnemonic()
            i = 1 
            for pos1, pos2 in zip(posMot1, posMot2): 
              oscillation_parameters = { "motors": {mot1:float(pos1), mot2:float(pos2) }}
              oscillation_parameters.update(params)
              oscillation_parameters["run_number"]=i
              i+=1
              oscillation_parameters["comments"]="%s: %f, %s: %f" % (motor1_name, pos1, motor2_name, pos2)
              self.emit(qt.PYSIGNAL("addToQueue"), ([oscillation_parameters], ))
            self.emit(qt.PYSIGNAL("goToCollect"), ())


    def _moveGraphicInBeam(self,beamx,beamy) :
        self._graphicSelection.move(beamx, beamy, 0)


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

            points = numpy.array([[x,y] for y in numpy.linspace(points[0,1],points[2,1],nbAxis2) for x in numpy.linspace(points[0,0],points[1,0],nbAxis1)])

            rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                     [numpy.sin(-angle),numpy.cos(-angle)]])

            self.__gridPoints = points * rotation
            self.__gridPoints += translation
        # grid == points
        self._matchPoints = [True for x in self.__gridPoints.tolist()]
           
    def _setColor(self,color) :
        BaseGraphicScan._setColor(self,color)

    def _showGrabScan(self,aFlag) :
        BaseGraphicScan._showGrabScan(self,aFlag)

