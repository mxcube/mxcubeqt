import math
import qt,qtcanvas,qttable
import logging

from Qub.Objects.QubDrawingManager import Qub2PointSurfaceDrawingMgr

from BlissFramework.Utils.GraphicScan import BaseGraphicScan

__category__ = 'Scans'

class MeshScanBrick(BaseGraphicScan) :
    def __init__(self,parent,name,**kwargs) :
        BaseGraphicScan.__init__(self,parent,name,uifile = 'Mesh.ui',cmd_name = 'mesh',**kwargs)

        self.__rect = None

        meshTable = self._widgetTree.child('__table')
        qt.QObject.connect(meshTable,qt.SIGNAL('valueChanged(int,int)'),self._valueChangedScanParam)
        gButton = self._widgetTree.child('__grabButton')
        meshTable.setColumnReadOnly(5,True)
        
        filloutButton = self._widgetTree.child('__fillout')
        qt.QObject.connect(filloutButton,qt.SIGNAL('clicked()'),self.__fillout)
        
        # TABLE SIZE HACKED
        height = meshTable.rowHeight(0) * (meshTable.numRows() + 1) + 5
        vheaders = meshTable.verticalHeader()
        hheaders = meshTable.horizontalHeader()
        width = vheaders.headerWidth() + hheaders.headerWidth() + 5
        meshTable.setMaximumSize(width,height)
        meshTable.setMinimumSize(width,height)
        
    def _viewConnect(self,view) :
        self._graphicSelection = Qub2PointSurfaceDrawingMgr(view.canvas(),
                                                                view.matrix())
        self._graphicSelection.setActionInfo('Mesh grab, select the area')
        drawingobject = qtcanvas.QCanvasRectangle(view.canvas())
        self._graphicSelection.addDrawingObject(drawingobject)
        self._graphicSelection.setEndDrawCallBack(self.__endGrab)
        view.addDrawingMgr(self._graphicSelection)
            
    def __endGrab(self,aDrawingObject) :
        self.__rect = aDrawingObject.rect()
        self._updateGUI()
        self.__fillout()
        
                       ####### CALLBACK #######

    def _startScan(self) :
        mot1 = self._getHorizontalMotor()
        mot2 = self._getVerticalMotor()

        table = self._widgetTree.child('__table')
        argList = []
        for row in range(2) :
            for col in range(1,4) :
                 stringVal = table.text(row,col)
                 value,valid = stringVal.toFloat()
                 if not valid :
                     dialog = qt.QErrorMessage(self)
                     dialog.message('value in mesh must be float')
                     return
                 argList.append(value)
        argList.insert(0,mot1.getMotorMnemonic())
        argList.insert(4,mot2.getMotorMnemonic())

        timeWidget = self._widgetTree.child('__time')
        stringVal = timeWidget.text()
        value,valid = stringVal.toFloat()
        if not valid :
            dialog = qt.QErrorMessage(self)
            dialog.message('Time must be float')
            return
        argList.append(value)
        self._logArgs = dict(list(zip(('mot1','mot1_start','mot1_final','mot1_intervals',
                                   'mot2','mot2_start','mot2_final','mot2_intervals',
                                   'scan_time'),argList)))
        self._logArgs['scan_type'] = 'mesh'
        try:
            self._logArgs['scanId'] = self.SCAN_N.getValue()
        except:
            pass

        startButton = self._widgetTree.child('__startScan')
        startButton.setEnabled(False)

        stopButton = self._widgetTree.child('__stopScan')
        stopButton.setEnabled(True)

        self._SpecCmd(*argList)

    def _moveGraphicInBeam(self,beamx,beamy) :
        self.__rect.moveTopLeft(qt.QPoint(beamx,beamy))
        self._graphicSelection.setRect(self.__rect.x(),self.__rect.y(),
                                       self.__rect.width(),self.__rect.height())
        
    def _valueChangedScanParam(self,row,column) :
        if column == 0 :
            self._updateGUI()
        elif column == 1 or column == 2 : # resize rectangle
            if self.__rect is not None :
                meshTable = self._widgetTree.child('__table')
                stringVal = meshTable.text(row,column)
                pos,valid = stringVal.toFloat()
                if valid :
                    # distance
                    stringVal = meshTable.text(row,(column % 2) + 1)
                    otherpos,valid = stringVal.toFloat()
                    if valid :
                        meshTable.setText(row,5,self._formatString % abs(otherpos - pos))

                    if row == 0 :
                        hmotor = self._getHorizontalMotor()
                        pos -= hmotor.getPosition()
                        pix = (pos / self._XSize * hmotor.getProperty('unit')) + self._beamx
                        if column == 1 : self.__rect.setLeft(pix)
                        else : self.__rect.setRight(pix)
                    else :
                        vmotor = self._getVerticalMotor()
                        pos -= vmotor.getPosition()
                        pix = (pos / self._YSize * vmotor.getProperty('unit')) + self._beamy
                        if column == 1 : self.__rect.setTop(pix)
                        else : self.__rect.setBottom(pix)
                    self._graphicSelection.setRect(self.__rect.x(),self.__rect.y(),self.__rect.width(),self.__rect.height())

                else :
                    dialog = qt.QErrorMessage(self)
                    dialog.message('Motors position must be float')
        elif column == 3 :              # interval
            self.__fillOneRow(row)
        elif column == 4 :
            self.__fillOneRow(row,True)
            
    def __fillout(self) :
        for row in range(2) :
            self.__fillOneRow(row)
            
    def __fillOneRow(self,row,useStep = False) :
        meshTable = self._widgetTree.child('__table')
        stringVal = meshTable.text(row,1)
        start,validStart = stringVal.toFloat()

        stringVal = meshTable.text(row,2)
        stop,validStop = stringVal.toFloat()
        try:
            if validStop and validStart :
                stringVal = meshTable.text(row,3)
                val,okFlag = stringVal.toFloat()
                if not useStep and okFlag :                     # using interval to set steps
                    steps = (stop - start) / val
                    meshTable.setText(row,4,self._formatString % steps)
                else:                   # try use steps to fill stop end intervals
                    stringVal = meshTable.text(row,4)
                    val,okFlag = stringVal.toFloat()
                    if okFlag :
                        intervals = math.ceil((stop - start) / val)
                        meshTable.setText(row,3,'%d' % int(abs(intervals)))
                        stop = start +  intervals * val
                        meshTable.setText(row,2,self._formatString % stop)
                        self._valueChangedScanParam(row,2) # update
        except:
            import traceback
            traceback.print_exc()

    def _getHStartStopPix(self) :
        if self.__rect is not None :
            return self.__rect.left(),self.__rect.right()
        else: raise
            

    def _getVStartStopPix(self) :
        if self.__rect is not None :
            return self.__rect.top(),self.__rect.bottom()
        else: raise
