import math
import logging
import qt
import qtcanvas

from BlissFramework.BaseComponents import BlissWidget

from Qub.Objects.QubDrawingManager import QubLineDrawingMgr

from BlissFramework.Utils.GraphicScan import BaseGraphicScan


__category__ = 'Scans'

class A2ScanBrick(BaseGraphicScan) :
    def __init__(self,parent,name,**kwargs) :
        BaseGraphicScan.__init__(self,parent,name,uifile = 'A2Scan.ui',cmd_name='a2scan',**kwargs)
        self.__points = []
                       ####### INIT GUI #######
        aTable = self._widgetTree.child('__table')
        qt.QObject.connect(aTable,qt.SIGNAL('valueChanged(int,int)'),self._valueChangedScanParam)
        aTable.setColumnReadOnly(4,True)
                
        intervals = self._widgetTree.child('__intervals')
        intervals.setValidator(qt.QIntValidator(intervals))
        qt.QObject.connect(intervals,qt.SIGNAL('returnPressed ()'),self.__intervalsChanged)
        qt.QObject.connect(intervals,qt.SIGNAL('lostFocus()'),self.__intervalsChanged)
        
        timeWidget = self._widgetTree.child('__time')
        timeWidget.setValidator(qt.QDoubleValidator(timeWidget))
        
    def _viewConnect(self,view) :
        self._graphicSelection = QubLineDrawingMgr(view.canvas(),
                                                   view.matrix())
        self._graphicSelection.setActionInfo('A2Scan grab, select the line')
        drawingobject = qtcanvas.QCanvasLine(view.canvas())
        self._graphicSelection.addDrawingObject(drawingobject)
        self._graphicSelection.setEndDrawCallBack(self.__endGrab)
        view.addDrawingMgr(self._graphicSelection)

    def __endGrab(self,aDrawingObject) :
        self.__points = list(aDrawingObject.points())
        self._updateGUI()

    def _getHStartStopPix(self) :
        if self.__points:
            return self.__points[0],self.__points[2]
        else: raise Exception

    def _getVStartStopPix(self) :
        if self.__points:
            return self.__points[1],self.__points[3]
        else: raise Exception
    
    def _moveGraphicInBeam(self,beamx,beamy) :
        x1,y1,x2,y2 = self.__points
        dx,dy = beamx - x1,beamy - y1
        self.__points = [x1 + dx,y1 + dy,x2 + dx,y2 + dy]
        self._graphicSelection.setPoints(*self.__points)

    def _valueChangedScanParam(self,row,column) :
        if row != 2 :
            if column == 0:
                self._updateGUI()
            elif column == 1 or column == 2: # point has moved
                aTable = self._widgetTree.child('__table')
                stringVal = aTable.text(row,column)
                pos,valid = stringVal.toFloat()
                if valid :
                    #distance
                    stringVal = aTable.text(row,(column % 2) + 1)
                    otherpos,valid = stringVal.toFloat()
                    if valid :
                        aTable.setText(row,4,self._formatString % abs(otherpos - pos))

                    if row == 0 :
                        hmotor = self._getHorizontalMotor()
                        pos -= hmotor.getPosition()
                        pix = (pos / self._XSize * hmotor.getProperty('unit')) + self._beamx
                        if column == 1 : self.__points[0] = pix
                        else: self.__points[2] = pix
                    else:
                        vmotor = self._getVerticalMotor()
                        pos -= vmotor.getPosition()
                        pix = (pos / self._YSize * vmotor.getProperty('unit')) + self._beamy
                        if column == 1: self.__points[1] = pix
                        else: self.__points[3] = pix
                    self._graphicSelection.setPoints(*self.__points)
                else:
                    dialog = qt.QErrorMessage(self)
                    dialog.message('Motors position must be float')
            elif column == 3 :
                aTable = self._widgetTree.child('__table')
                (start,v1),(stop,v2) = [aTable.text(row,column).toFloat() for column in range(1,3)]
                if v1 and v2 :
                    stringVal = aTable.text(row,3)
                    val,okFlag = stringVal.toFloat()
                    if okFlag:
                        intervals = math.ceil((stop - start) / val)
                        intervals_widget = self._widgetTree.child('__intervals')
                        intervals_widget.setText('%d' % int(abs(intervals)))
                        stop = start + intervals * val
                        aTable.setText(row,2,self._formatString % stop)
                        self._valueChangedScanParam(row,2) # update
                        self.__intervalsChanged()  # update
        else:
            if column == 3 :
                aTable = self._widgetTree.child('__table')
                angle,v1 = aTable.text(2,0).toFloat()
                step,v2 = aTable.text(2,column).toFloat()
                if v1 and v2:
                    angle = angle * math.pi / 180
                    
                    hstep = step * math.cos(angle)
                    aTable.setText(0,column,self._formatString % hstep)
                    
                    vstep = step * math.sin(angle)
                    aTable.setText(1,column,self._formatString % vstep)

                    (startMot1,v1),(stopMot1,v2) = [aTable.text(0,column).toFloat() for column in range(1,3)]
                    (startMot2,v1),(stopMot2,v2) = [aTable.text(1,column).toFloat() for column in range(1,3)]

                    distance = math.sqrt((stopMot1 - startMot1) ** 2 + (stopMot2 - startMot2) ** 2)
                    interval = int(math.ceil(distance / step))

                    corr = (interval * step) / distance

                    stopMot1 = startMot1 + corr * (stopMot1 - startMot1)
                    stopMot2 = startMot2 + corr * (stopMot2 - startMot2)
                    
                    aTable.setText(0,2,self._formatString % stopMot1)
                    aTable.setText(1,2,self._formatString % stopMot2)

                    intervals_widget = self._widgetTree.child('__intervals')
                    intervals_widget.setText('%d' % int(abs(interval )))

                    for row in range(2):
                        for column in range(1,3) :
                            self._valueChangedScanParam(row,column)

    def _updateGUI(self) :
        BaseGraphicScan._updateGUI(self)
        aTable = self._widgetTree.child('__table')
        (startMot1,v1),(stopMot1,v2) = [aTable.text(0,column).toFloat() for column in range(1,3)]
        if not v1 or not v2 : return
        
        (startMot2,v1),(stopMot2,v2) = [aTable.text(1,column).toFloat() for column in range(1,3)]
        if not v1 or not v2 : return

        try:
            angle = math.atan((stopMot2 - startMot2) / (stopMot1 - startMot1))
        except ZeroDivisionError:
            angle = math.pi / 2
        aTable.setText(2,0,'%.2f' % (angle * 180 / math.pi))

        self._valueChangedScanParam(2,3)
        
    def __intervalsChanged(self) :
        intervals_widget = self._widgetTree.child('__intervals')
        intervals,valid = intervals_widget.text().toInt()
        try:
            aTable = self._widgetTree.child('__table')
                      ####### step calc #######
            for row in range(2) :
                (start,v1),(stop,v2) = [aTable.text(row,column).toFloat() for column in range(1,3)]
                if v1 and v2 :
                    aTable.setText(row,3,self._formatString % ((stop - start) / float(intervals)))
                else:
                    dialog = qt.QErrorMessage(self)
                    dialog.message('Start and stop must be float')
                    return
        except:
            import traceback
            traceback.print_exc()
    
    def _startScan(self) :
        mot1 = self._getHorizontalMotor()
        mot2 = self._getVerticalMotor()

        table = self._widgetTree.child('__table')
        argList = []
        for row in range(2) :
            for col in range(1,3) :
                 stringVal = table.text(row,col)
                 value,valid = stringVal.toFloat()
                 if not valid :
                     dialog = qt.QErrorMessage(self)
                     dialog.message('value must be float')
                     return
                 argList.append(value)
        argList.insert(0,mot1.getMotorMnemonic())
        argList.insert(3,mot2.getMotorMnemonic())

        intervals_widget = self._widgetTree.child('__intervals')
        stringVal = intervals_widget.text()
        intervals,valid = stringVal.toInt()
        argList.append(intervals)

        timeWidget = self._widgetTree.child('__time')
        stringVal = timeWidget.text()
        timeVal,valid = stringVal.toFloat()
        argList.append(timeVal)

        self._logArgs = dict(list(zip(('mot1','mot1_start','mot1_final',
                                  'mot2','mot2_start','mot2_final',
                                  'intervals','scan_time'),argList)))
        self._logArgs['scan_type'] = 'a2scan'
        try:
            self._logArgs['scanId'] = self.SCAN_N.getValue()
        except:
            pass

        self._SpecCmd(*argList)

        startButton = self._widgetTree.child('__startScan')
        startButton.setEnabled(False)

        stopButton = self._widgetTree.child('__stopScan')
        stopButton.setEnabled(True)
