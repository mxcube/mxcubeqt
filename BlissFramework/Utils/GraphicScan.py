"""
This file group base classes for framework graphic
"""

import qt
import qttable
import logging

from BlissFramework.BaseComponents import BlissWidget

class SpecCmd(qt.QObject):
  def __init__(self, ho, spec_cmd_name):
    qt.QObject.__init__(self)
    self.spec_cmd_name = spec_cmd_name
    self.ho = ho
    self._initialized = False

  def __getattr__(self, attr):
    if not attr.startswith("__"):
      spec_cmd = self.ho.getCommandObject(self.spec_cmd_name)
      return getattr(spec_cmd, attr)
    raise AttributeError  

  def _emitReplyArrived(self, *args):
    self.emit(qt.PYSIGNAL("commandReplyArrived"), args)

  def _emitAborted(self, *args):
    self.emit(qt.PYSIGNAL("commandAborted"), args)

  def _emitFailed(self, *args):
    self.emit(qt.PYSIGNAL("commandFailed"), args)

  def __call__(self, *args):
    spec_cmd = self.ho.getCommandObject(self.spec_cmd_name)
    if not self._initialized:
      spec_cmd.connectSignal('commandReplyArrived', self._emitReplyArrived)
      spec_cmd.connectSignal("commandAborted", self._emitAborted)
      spec_cmd.connectSignal("commandFailed", self._emitFailed)
    self._initialized = True
    spec_cmd(*args)


class BaseGraphicScan(BlissWidget) :
    def __init__(self,parent,name, uifile='',cmd_name=None) :
        BlissWidget.__init__(self,parent,name)

        self._widgetTree = self.loadUIFile(uifile)
        self._widgetTree.reparent(self,qt.QPoint(0,0))
        layout = qt.QHBoxLayout(self)
        layout.addWidget(self._widgetTree)
        
        self.addProperty('horizontal','string','')
        self.addProperty('vertical','string','')
        self.addProperty('command','string','')
        self.addProperty("formatString", "formatString", "###.##")
                        ####### SIGNAL #######
        self.defineSignal('getView',())
        self.defineSignal('scanFinished',())
                         ####### SLOT #######
        self.defineSlot("ChangePixelCalibration", ())
        self.defineSlot("ChangeBeamPosition", ())

        self._view = None
        self._beamx,self._beamy = 0,0
        self._XSize,self._YSize = 1,1
        self._horizontalMotors = []
        self._verticalMotors = []
        self._graphicSelection = None
        self._SpecCmd = None
        self.__commandName = cmd_name
        self._logArgs = {}
        self._formatString = '%f'

                       ####### GUI INIT #######
        gButton = self._widgetTree.child('__grabButton')
        gButton.hide()

        showgButton = self._widgetTree.child('__showGrab')
        showgButton.hide()
        
        mvButton = self._widgetTree.child('__movetoStart')
        qt.QObject.connect(mvButton,qt.SIGNAL('clicked()'),self._movetoStart)
        mvButton.hide()

        startButton = self._widgetTree.child('__startScan')
        qt.QObject.connect(startButton,qt.SIGNAL('clicked()'),self._startScan)
        startButton.setEnabled(False)

        stopButton = self._widgetTree.child('__stopScan')
        qt.QObject.connect(stopButton,qt.SIGNAL('clicked()'),self._stopScan)
        stopButton.setEnabled(False)
        
    def propertyChanged(self,property,oldValue,newValue):
        if property == 'horizontal' or property == 'vertical' :
            try:
                hardwareObject = self.getHardwareObject(self[property])
                if hardwareObject is None:
                    return
            except:
                return
            motors = []
            l = qt.QStringList()
            if not hardwareObject.hasObject('motors') :
                try:
                    l.append(hardwareObject.getMotorMnemonic())
                    motors.append(hardwareObject)
                except:
                    logging.getLogger().error('is not a motor device nor an Equipment : no <motors> section')
            else:
                ho = hardwareObject['motors']
                for motor in ho :
                    motors.append(motor)
                    l.append(motor.getMotorMnemonic())

            if property == 'horizontal':
                self._horizontalMotors = motors
            else:
                self._verticalMotors = motors

            self._setMotor(property,l)
            
        elif property == 'command' :
            ho = self.getHardwareObject(newValue)
            if ho is not None:
                try:
                    spec_cmd = ho.getCommandObject(self.__commandName)
                except:
                    self._SpecCmd = None
                else:
                    self._SpecCmd = SpecCmd(ho, self.__commandName)
  
                if self._SpecCmd is not None:
                    startButton = self._widgetTree.child('__startScan')
                    startButton.setEnabled(True)
                    qt.QObject.connect(self._SpecCmd, qt.PYSIGNAL("commandReplyArrived"), self._scanFinished)
                    qt.QObject.connect(self._SpecCmd, qt.PYSIGNAL("commandAborted"), self._scanAborted)
                    qt.QObject.connect(self._SpecCmd, qt.PYSIGNAL("commandFailed"), self._scanAborted)
                try:
                    self.SCAN_N = ho.getChannelObject('SCAN_N')
                except:
                    self.SCAN_N = None

        elif property == 'formatString' :
            self._formatString = self['formatString']

    def run(self):
        """
        get view
        """
        view = {}
        self.emit(qt.PYSIGNAL("getView"), (view,))
        try:
            self._view = view["drawing"]
        except:
            logging.getLogger().error('view is not connected to MeshScanBrick')
            return
        
        if self._view is not None :
            gButton = self._widgetTree.child('__grabButton')
            gButton.show()
            qt.QObject.connect(gButton,qt.SIGNAL('toggled(bool)'),self._grabScan)

            showgButton = self._widgetTree.child('__showGrab')
            showgButton.show()
            qt.QObject.connect(showgButton,qt.SIGNAL('toggled(bool)'),self._showGrabScan)

            mvButton = self._widgetTree.child('__movetoStart')
            mvButton.show()

            self.connect(self._view, qt.PYSIGNAL("ForegroundColorChanged"),
                         self._setColor)
            self._viewConnect(self._view)


            
    def ChangeBeamPosition(self,x,y) :
        #logging.getLogger().info(">>>>>>>>>>>>>>>>> in meshscanbrick, beam x = %d, beam y = %d", x, y)
        self._beamx,self._beamy = x,y
        self._updateGUI()
        
    def ChangePixelCalibration(self,sizex,sizey) :
        #logging.getLogger().info(">>>>>>>>>>>>>>>>> in meshscanbrick, size x = %f, size y = %f", sizex, sizey)
        self._XSize,self._YSize = sizex,sizey
        self._updateGUI()
        
                         ####### GRAB #######
    def _grabScan(self,aFlag) :
        if aFlag :
            showgButton = self._widgetTree.child('__showGrab')
            showgButton.setOn(True)
            self._graphicSelection.setDubModeCallBack(self._unactiveAction)
            self._graphicSelection.startDrawing()
            self._updateGUI()
        else:
            self._graphicSelection.stopDrawing()

    def _showGrabScan(self,aFlag) :
        if aFlag :
            self._graphicSelection.show()
        else:
            self._graphicSelection.hide()
            gButton = self._widgetTree.child('__grabButton')
            gButton.setOn(False)

    def _setMotor(self,property,motorList) :
        table = self._widgetTree.child('__table')
        combo = qttable.QComboTableItem(table,motorList)
        if property == 'horizontal':
            table.setItem(0,0,combo)
        else:
            table.setItem(1,0,combo)
                    ####### MOVE TO START #######
    def _updateGUI(self) :
        try:
            hpixStart,hpixStop = self._getHStartStopPix()
            vpixStart,vpixStop = self._getVStartStopPix()
            table = self._widgetTree.child('__table')
                      ####### HORIZONTAL #######
            if(self._XSize is not None and self._YSize is not None and
               self._beamx is not None and self._beamy is not None) :
                hmotor = self._getHorizontalMotor()
                try:
                    hStartPos = (hpixStart - self._beamx) / hmotor.getProperty('unit') * self._XSize
                    hStopPos = (hpixStop - self._beamx) / hmotor.getProperty('unit') * self._XSize

                    hStartPos += hmotor.getPosition()
                    hStopPos += hmotor.getPosition()

                    table.setText(0,1,self._formatString % hStartPos)
                    table.setText (0,2,self._formatString % hStopPos)

                    # update mesh rectangle
                    self._valueChangedScanParam(0,1)
                    self._valueChangedScanParam(0,2)
                    
                except AttributeError:
                    import traceback
                    traceback.print_exc()
                    logging.getLogger().error('motors must have a unit field')
                    
                       ####### VERTICAL #######
                vmotor = self._getVerticalMotor()
                try:
                    vStartPos = (vpixStart - self._beamy) / vmotor.getProperty('unit') * self._YSize
                    vStopPos = (vpixStop - self._beamy) / vmotor.getProperty('unit') * self._YSize
                    
                    vStartPos += vmotor.getPosition()
                    vStopPos += vmotor.getPosition()

                    table.setText(1,1,self._formatString % vStartPos)
                    table.setText (1,2,self._formatString % vStopPos)

                    # update mesh rectangle
                    self._valueChangedScanParam(1,1)
                    self._valueChangedScanParam(1,2)

                except AttributeError :
                    import traceback
                    traceback.print_exc()
                    logging.getLogger().error('motors must have a unit field')
        except:
            pass
        
    def _getHStartStopPix(self) :
        logging.getLogger().error('_getHStartStopPix must be redefine')
        raise

    def _getVStartStopPix(self) :
        logging.getLogger().error('_getVStartStopPix must be redefine')
        raise

    def _getHorizontalMotor(self) :
        table = self._widgetTree.child('__table')
        userNameMot = str(table.item(0,0).currentText())
        for motor in self._horizontalMotors :
            if motor.getMotorMnemonic() == userNameMot :
                return motor

    def _getVerticalMotor(self) :
        table = self._widgetTree.child('__table')
        userNameMot = str(table.item(1,0).currentText())
        for motor in self._verticalMotors :
            if motor.getMotorMnemonic() == userNameMot :
                return motor

                       ####### CALLBACK #######

    def _startScan(self) :
        logging.getLogger().error('start scan must be redefine')

    def _movetoStart(self) :
        table = self._widgetTree.child('__table')
        stringVal = table.text(0,1)
        mot1StartPos,valid = stringVal.toFloat()
        if not valid :
            dialog = qt.QErrorMessage(self)
            dialog.message('Start must be float')
            return

        stringVal = table.text(1,1)
        mot2StartPos,valid = stringVal.toFloat()
        if not valid :
            dialog = qt.QErrorMessage(self)
            dialog.message('Start must be float')
            return
        mot1 = self._getHorizontalMotor()
        mot2 = self._getVerticalMotor()

        mot1.move(mot1StartPos)
        mot2.move(mot2StartPos)
        self._moveGraphicInBeam(self._beamx,self._beamy)
        
    def _valueChangedScanParam(self,row,column) :
        pass                            # May be redefine
    
    def _stopScan(self) :
        self._SpecCmd.abort()
    
    def _scanFinished(self) :
        startButton = self._widgetTree.child('__startScan')
        startButton.setEnabled(True)

        stopButton = self._widgetTree.child('__stopScan')
        stopButton.setEnabled(False)
        self._logArgs['stat'] = 'OK'
        self.emit(qt.PYSIGNAL("scanFinished"), (self._logArgs,))
        
    def _scanAborted(self) :
        startButton = self._widgetTree.child('__startScan')
        startButton.setEnabled(True)
        
        stopButton = self._widgetTree.child('__stopScan')
        stopButton.setEnabled(False)
        if self._logArgs :
            self._logArgs['stat'] = 'ABORTED'
            self.emit(qt.PYSIGNAL("scanFinished"), (self._logArgs,))
        self._logArgs = {}
        
    def _setColor(self,color) :
        self._graphicSelection.setColor(color)

    def _unactiveAction(self,drawingManager,aFlag) :
        gButton = self._widgetTree.child('__grabButton')
        gButton.setOn(not aFlag)
