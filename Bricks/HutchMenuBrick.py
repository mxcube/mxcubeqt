from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import logging
import MiniDiff
import CommandMenuBrick
import os
import tempfile

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr, Qub2PointSurfaceDrawingMgr, QubAddDrawing
from Qub.Objects.QubDrawingManager import QubContainerDrawingMgr
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget
from Qub.Objects.QubDrawingCanvasTools import QubCanvasVLine
from Qub.Objects.QubDrawingCanvasTools import QubCanvasHLine
from Qub.Objects.QubDrawingCanvasTools import QubCanvasBeam
from Qub.Objects.QubDrawingCanvasTools import QubCanvasSlitbox
from Qub.Objects.QubDrawingCanvasTools import QubCanvasRectangle
from Qub.Objects.QubDrawingCanvasTools import QubCanvasScale
from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point
from Qub.Tools import QubImageSave
from BlissFramework.Utils import widget_colors


__category__ = 'mxCuBE'

class CentringMethod:
  def __init__(self, method):
    self.method = method
  def text(self):
    return self.method

###
### Sample centring brick
###
class HutchMenuBrick(BlissWidget):
    SNAPSHOT_FORMATS = ('png', 'jpeg')

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.minidiff = None
        self.slitbox  = None
        self.sampleChanger=None
        self.collectObj = None
        self.queue_hwobj = None
        self._bx, self._by = (None, None)
        #self.allowMoveToBeamCentring = False

        # Define properties
        self.addProperty('minidiff','string','')
        self.addProperty('dataCollect','string','')
        self.addProperty('slitbox','string','')
        self.addProperty('samplechanger','string','')
        self.addProperty('extraCommands','string','')
        self.addProperty('extraCommandsIcons','string','')
        self.addProperty('icons','string','')
        self.addProperty('label','string','Sample centring')
        #self.addProperty('displaySlitbox', 'boolean', True)
        self.addProperty('displayBeam', 'boolean', True)
        self.addProperty('queue', 'string', '/queue')

        # Define signals and slots
        self.defineSignal('enableMinidiff',())
        self.defineSignal('centringStarted',())
        self.defineSignal('centringAccepted',())
        self.defineSignal('getView',())
        self.defineSignal('beamPositionChanged', ())
        self.defineSignal('calibrationChanged', ())
        self.defineSignal('newCentredPos', ())
        #self.defineSignal('setMoveToBeamState', ())
        self.defineSlot('setDirectory',())
        self.defineSlot('setPrefix',())
        #self.defineSlot('movedToBeam', ())
        self.defineSlot('startCentring', ())
        self.defineSlot('rejectCentring', ())
        self.defineSlot('setSample',())
        #self.defineSlot('enableAutoStartLoopCentring', ())
        self.defineSlot('getSnapshot',())
        
        self.sampleCentreBox=QVBox(self)
        #self.sampleCentreBox.setInsideMargin(11)
        #self.sampleCentreBox.setInsideSpacing(0)

        #self.modeBox=QVButtonGroup(self.sampleCentreBox)
        #self.modeBox.setFrameShape(self.modeBox.NoFrame)
        #self.modeBox.setInsideMargin(0)
        #self.modeBox.setInsideSpacing(0)            
        #QObject.connect(self.modeBox,SIGNAL('clicked(int)'),self.centringModeChanged)
        #self.userConfirmsButton=QCheckBox("User confirms", self.sampleCentreBox)
        #self.userConfirmsButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        #self.userConfirmsButton.setChecked(True)

        self.buttonsBox=QVBox(self.sampleCentreBox)
        self.buttonsBox.setSpacing(0)

        self.buttonCentre=MenuButton(self.buttonsBox,"Centre")
        self.buttonCentre.setMinimumSize(QSize(75,50))
        self.connect(self.buttonCentre,PYSIGNAL('executeCommand'),self.centreSampleClicked)
        self.connect(self.buttonCentre,PYSIGNAL('cancelCommand'),self.cancelCentringClicked)

        self.buttonAccept = QToolButton(self.buttonsBox)
        self.buttonAccept.setUsesTextLabel(True)
        self.buttonAccept.setTextLabel("Save")
        self.buttonAccept.setMinimumSize(QSize(75,50))
        self.buttonAccept.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonAccept.setEnabled(False)
        QObject.connect(self.buttonAccept,SIGNAL('clicked()'),self.acceptClicked)
        self.standardColor=None

        self.buttonReject = QToolButton(self.buttonsBox)
        self.buttonReject.setUsesTextLabel(True)
        self.buttonReject.setTextLabel("Reject")
        self.buttonReject.setMinimumSize(QSize(75,50))
        self.buttonReject.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonReject.setEnabled(False)
        self.buttonReject.hide()
        QObject.connect(self.buttonReject,SIGNAL('clicked()'),self.rejectClicked)

        #HorizontalSpacer4(self.sampleCentreBox)

        self.extraCommands=CommandMenuBrick.CommandMenuBrick(self.sampleCentreBox)
        self.extraCommands['showBorder']=False

        self.buttonSnapshot = QToolButton(self.sampleCentreBox)
        self.buttonSnapshot.setUsesTextLabel(True)
        self.buttonSnapshot.setTextLabel("Snapshot")
        self.buttonSnapshot.setMinimumSize(QSize(75,50))
        self.buttonSnapshot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.buttonSnapshot,SIGNAL('clicked()'),self.saveSnapshot)

        #HorizontalSpacer3(self.sampleCentreBox)

        self.centringButtons=[]
        self.defaultBackgroundColor=None
        self.insideDataCollection=False        
        self.currentCentring = None
        self.isMoving=False
        self.isShooting=False
        self.directory="/tmp"
        self.prefix="snapshot"
        self.fileIndex=1
        self.formatType="png"

        self.clickedPoints=[]
        self.selectedSamples=None

        # Layout
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        QHBoxLayout(self)        
        self.layout().addWidget(self.sampleCentreBox)

        self.instanceSynchronize("")

        self.resetMethods={MiniDiff.MiniDiff.MANUAL3CLICK_MODE:self.manualCentreReset,
            MiniDiff.MiniDiff.C3D_MODE:self.automaticCentreReset}
            #MiniDiff.MiniDiff.MOVE_TO_BEAM_MODE:self.moveToBeamReset}
        self.successfulMethods={MiniDiff.MiniDiff.MANUAL3CLICK_MODE:None,
            MiniDiff.MiniDiff.C3D_MODE:self.automaticCentreSuccessful}
            #MiniDiff.MiniDiff.MOVE_TO_BEAM_MODE:self.moveToBeamSuccessful}

    def enableAutoStartLoopCentring(self, enable):
        if self.minidiff is not None:
           self.minidiff.enableAutoStartLoopCentring(enable)

    def propertyChanged(self,propertyName,oldValue,newValue):
        #print "HutchMenuBrick.propertyChanged",property,newValue
        if propertyName=='minidiff':
            if self.minidiff is not None:
                self.disconnect(self.minidiff,PYSIGNAL('zoomMotorPredefinedPositionChanged'), self.zoomPositionChanged)
                self.disconnect(self.minidiff,PYSIGNAL('minidiffReady'),self.miniDiffReady)
                self.disconnect(self.minidiff,PYSIGNAL('minidiffNotReady'),self.miniDiffNotReady)
                self.disconnect(self.minidiff,PYSIGNAL('minidiffStateChanged'),self.miniDiffStateChanged)
                self.disconnect(self.minidiff,PYSIGNAL('centringStarted'),self.centringStarted)
                self.disconnect(self.minidiff,PYSIGNAL('centringSuccessful'),self.centringSuccessful)
                self.disconnect(self.minidiff,PYSIGNAL('centringFailed'),self.centringFailed)
                self.disconnect(self.minidiff,PYSIGNAL('centringMoving'),self.centringMoving)
                self.disconnect(self.minidiff,PYSIGNAL('centringInvalid'),self.centringInvalid)
                self.disconnect(self.minidiff,PYSIGNAL('centringSnapshots'),self.centringSnapshots)
                self.disconnect(self.minidiff,PYSIGNAL('progressMessage'),self.miniDiffMessage)
                self.disconnect(self.minidiff,PYSIGNAL('centringAccepted'),self.centringAccepted)
            self.minidiff=self.getHardwareObject(newValue)
          
            if self.minidiff is not None:
                self.connect(self.minidiff,PYSIGNAL('zoomMotorPredefinedPositionChanged'),self.zoomPositionChanged)
                self.connect(self.minidiff,PYSIGNAL('minidiffReady'),self.miniDiffReady)
                self.connect(self.minidiff,PYSIGNAL('minidiffNotReady'),self.miniDiffNotReady)
                self.connect(self.minidiff,PYSIGNAL('minidiffStateChanged'),self.miniDiffStateChanged)
                self.connect(self.minidiff,PYSIGNAL('centringStarted'),self.centringStarted)
                self.connect(self.minidiff,PYSIGNAL('centringSuccessful'),self.centringSuccessful)
                self.connect(self.minidiff,PYSIGNAL('centringFailed'),self.centringFailed)
                self.connect(self.minidiff,PYSIGNAL('centringMoving'),self.centringMoving)
                self.connect(self.minidiff,PYSIGNAL('centringInvalid'),self.centringInvalid)
                self.connect(self.minidiff,PYSIGNAL('centringSnapshots'),self.centringSnapshots)
                self.connect(self.minidiff,PYSIGNAL('progressMessage'),self.miniDiffMessage)
                self.connect(self.minidiff,PYSIGNAL('centringAccepted'),self.centringAccepted)
                self.connect(self.minidiff, "newAutomaticCentringPoint", self.drawAutoCentringPoint)

                if self.minidiff.isReady():
                    self.miniDiffReady()
                else:
                    self.miniDiffNotReady()
            else:
                self.miniDiffNotReady()
        elif propertyName=='slitbox':
            if self.slitbox is not None:
                for role in ('s1v', 's2v', 's1h', 's2h'):
                  m = self.slitbox.getDeviceByRole(role)
                  m.disconnect('stateChanged', self.slitsPositionChanged)
            self.slitbox=self.getHardwareObject(newValue)
            if self.slitbox is not None:
                for role in ('s1v', 's2v', 's1h', 's2h'):
                  m = self.slitbox.getDeviceByRole(role)
                  m.connect("stateChanged", self.slitsPositionChanged)
            #self.slitsPositionChanged()
        elif propertyName=="samplechanger":
            self.sampleChanger=self.getHardwareObject(newValue)
        elif propertyName=="dataCollect":
            self.collectObj=self.getHardwareObject(newValue)
        elif propertyName == 'icons':
            self.setIcons(newValue)
        elif propertyName=='label':
          pass #self.sampleCentreBox.setTitle(newValue)
        elif propertyName=='extraCommands':
            self.extraCommands['mnemonic']=newValue
        elif propertyName=='extraCommandsIcons':
            self.extraCommands['icons']=newValue
        elif propertyName=='queue':
            self.queue_hwobj = self.getHardwareObject(newValue)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def setIcons(self,icons):
        icons_list=icons.split()
        try:
            self.buttonCentre.setIcons(icons_list[0],icons_list[1])
        except IndexError:
            pass
        try:
            self.buttonAccept.setPixmap(Icons.load(icons_list[2]))
        except IndexError:
            pass
        try:
            self.buttonSnapshot.setPixmap(Icons.load(icons_list[3]))
        except IndexError:
            pass
        try:
            self.buttonReject.setPixmap(Icons.load(icons_list[4]))
        except IndexError:
            pass

    def setDirectory(self,directory):
        self.directory=str(directory)
        self.fileIndex=1

    def setPrefix(self,prefix):
        self.prefix=str(prefix)
        self.fileIndex=1

    def setSample(self,samples_list):
        self.selectedSamples = samples_list
        try:
          blsampleid=int(self.selectedSamples[0][0])
        except:
          blsampleid=None
        try:
          self.minidiff.setSampleInfo({"blsampleid":blsampleid})
        except:
          pass

    def emitWidgetSynchronize(self):
        #mode=self.modeBox.selectedId()
        points=self.clickedPoints
        #self.emit(PYSIGNAL("widgetSynchronize"),( (mode,points), ))
        self.emit(PYSIGNAL("widgetSynchronize"),( (points), ))

    def widgetSynchronize(self,state):
        #centring_method=state[0]
        #clicked_points=state[1]
        clicked_points=state[0]
        #self.modeBox.setButton(centring_method)
        if len(clicked_points):
            point=clicked_points[-1]
            self.__point.startDrawing()
            self.__point.show()
            self.__point.setPoint(point[0],point[1])
            self.__point.stopDrawing()
        else:
            self.__point.hide()

    def startCentring(self):
        # this is called from another brick, not by user
        self.insideDataCollection=True
        self.centreSampleClicked()

    def rejectCentring(self):
        self.cancelCentringClicked(reject=True)

    def acceptCentring(self):
        self.acceptClicked()

    def centreSampleClicked(self):
        self.minidiff.startCentringMethod(self.minidiff.MANUAL3CLICK_MODE)

    def saveSnapshot(self):
        formats=""
        for format in HutchMenuBrick.SNAPSHOT_FORMATS:
            formats+="*.%s " % format
        formats=formats.strip()

        current_filename=os.path.join(self.directory, self.prefix)
        current_filename=current_filename + '_%d%s%s' % (self.fileIndex, os.path.extsep, self.formatType)
        filename=str(QFileDialog.getSaveFileName(current_filename,"Images (%s)" % formats,\
            self,None,"Choose a filename to save under",None,False))
        if len(filename):
            image_type=os.path.splitext(filename)[1].strip('.').upper()
            try:
                matrix = self.__drawing.matrix()
                zoom = 1
                if matrix is not None:
                    zoom = matrix.m11()
                img = self.__drawing.getPPP()
                logging.getLogger().info("Saving snapshot : %s", filename)
                QubImageSave.save(filename, img, self.__drawing.canvas(), zoom, image_type)
            except:
                logging.getLogger().exception("HutchMenuBrick: error saving snapshot!")
                logging.getLogger().error("HutchMenuBrick: error saving snapshot!")
            else:
                self.formatType=image_type.lower()
                self.fileIndex+=1


    def centredPositionSnapshot(self):
        matrix = self.__drawing.matrix()

        zoom = 1
        if matrix is not None:
            zoom = matrix.m11()

        img = self.__drawing.getPPP()
        fd, name = tempfile.mkstemp()
        os.close(fd)

        QubImageSave.save(name, img, self.__drawing.canvas(), zoom, "JPEG")

        f = open(name, "r")
        imgcopy = f.read()
        f.close()
        os.unlink(name)

        return imgcopy


    def getSnapshot(self, img):
        logging.getLogger().debug("Taking snapshot for centred position")
        img['data'] = self.centredPositionSnapshot()
    

    def cancelCentringClicked(self,reject=False):
        #print "CANCELCENTRINGCLICKED",reject
        self.minidiff.cancelCentringMethod(reject=reject)

    def acceptClicked(self):
        if self.standardColor is not None:
            self.buttonAccept.setPaletteBackgroundColor(self.standardColor)
        logging.info("disabling accept because accept was clicked")  
        self.buttonAccept.setEnabled(False)
        self.buttonReject.setEnabled(False)
        self.minidiff.acceptCentring()

    def rejectClicked(self):
        if self.standardColor is not None:
            self.buttonReject.setPaletteBackgroundColor(self.standardColor)
        logging.info("disabling accept because reject was clicked")  
        self.buttonReject.setEnabled(False)
        self.buttonAccept.setEnabled(False)
        self.minidiff.rejectCentring()
        self.insideDataCollection=False

    def centringMoving(self):
        self.isMoving=True
        logging.info("disabling accept because centring is moving ")  
        self.buttonAccept.setEnabled(False)
        self.buttonReject.setEnabled(False)

    def centringInvalid(self):
        if self.collectObj is not None:
            self.collectObj.setCentringStatus(None)
        logging.info("disabling accept because centring is invalid ")  
        self.buttonAccept.setEnabled(False)
        self.buttonReject.setEnabled(False)

    def centringAccepted(self,state,centring_status):
        logging.info("Centring has been accepted")
        if self.collectObj is not None:
            self.collectObj.setCentringStatus(centring_status)
        logging.info("disabling accept because centring has been accepted ")  
        self.buttonAccept.setEnabled(False)
        self.buttonReject.setEnabled(False)
        if self.insideDataCollection:
          self.insideDataCollection = False
          self.emit(PYSIGNAL("centringAccepted"), (state,centring_status))

        self.emit(PYSIGNAL("newCentredPos"), (state, centring_status))

        if self.queue_hwobj.is_executing():
            self.setEnabled(False)

    def centringSnapshots(self,state):
        if state is None:
            self.isShooting=True
            self.sampleCentreBox.setEnabled(False)
        else:
            self.isShooting=False
            self.sampleCentreBox.setEnabled(True)

    def centringStarted(self,method,flexible):
        self.setEnabled(True)
        self.emit(PYSIGNAL("enableMinidiff"), (False,))
        if self.insideDataCollection:
          self.emit(PYSIGNAL("centringStarted"), ())

        self.isCentring=True
        self.isMoving=False
        self.isShooting=False
        """
        for but in self.centringButtons:
            if str(but.text())==method:
                if self.defaultBackgroundColor is None:
                    self.defaultBackgroundColor=but.paletteBackgroundColor()
                but.setPaletteBackgroundColor(QWidget.yellow)
                self.currentCentring=but
                break
        """
        self.currentCentring = CentringMethod(method)
        self.buttonCentre.commandStarted()
        logging.info("disabling accept because centring has been started ")  
        self.buttonAccept.setEnabled(False)
        self.buttonReject.setEnabled(False)

        if method==MiniDiff.MiniDiff.MANUAL3CLICK_MODE:
            self.__point.startDrawing()
            self.__helpLine.startDrawing()
            self.__pointer.startDrawing()

    def drawAutoCentringPoint(self, x,y):
      if -1 in (x,y):
        self.__autoCentringPoint.hide()
        return
      self.__autoCentringPoint.startDrawing()
      self.__autoCentringPoint.setPoint(x,y)
      self.__autoCentringPoint.stopDrawing()
      self.__autoCentringPoint.show()
      
    def centringSuccessful(self,method,centring_status):
        self.__point.stopDrawing()
        self.__point.hide()
        self.__helpLine.hide()
        self.__helpLine.stopDrawing()
        self.__pointer.stopDrawing()
        self.__pointer.hide()

        logging.info("HutchMenuBrick:  centringSuccesful received")

        self.clickedPoints=[]
        self.emitWidgetSynchronize()

        self.buttonCentre.commandDone()
        if self.currentCentring is not None:
            #    self.currentCentring.setPaletteBackgroundColor(self.defaultBackgroundColor)
            self.currentCentring=None

        logging.info("HutchMenuBrick:  enabling buttons")
        self.buttonAccept.setEnabled(True)
        self.buttonReject.setEnabled(True)
        if self.insideDataCollection:
            if self.standardColor is None:
                self.standardColor=self.buttonAccept.paletteBackgroundColor()
            self.buttonAccept.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
            self.buttonReject.setPaletteBackgroundColor(widget_colors.LIGHT_RED)

        if self.collectObj is not None:
            self.collectObj.setCentringStatus(centring_status)

        self.isMoving=False
        self.sampleCentreBox.setEnabled(True)
        self.emit(PYSIGNAL("enableMinidiff"), (True,))

        try:
            successful_method=self.successfulMethods[method]
        except KeyError,diag:
            pass
        else:
            try:
                successful_method()
            except:
                pass

    def centringFailed(self,method,centring_status):
        self.__point.stopDrawing()
        self.__point.hide()
        self.__helpLine.hide()
        self.__helpLine.stopDrawing()
        self.__pointer.stopDrawing()
        self.__pointer.hide()
       
        self.clickedPoints=[]
        self.emitWidgetSynchronize()


        self.buttonCentre.commandFailed()
        if self.currentCentring is not None:
            #    self.currentCentring.setPaletteBackgroundColor(self.defaultBackgroundColor)
            self.currentCentring=None

        logging.info("disabling accept because centing failed")  
        self.buttonAccept.setEnabled(False)
        if self.insideDataCollection:
            if self.standardColor is None:
                self.standardColor=self.buttonAccept.paletteBackgroundColor()
            self.buttonReject.setEnabled(True)
            self.buttonReject.setPaletteBackgroundColor(QWidget.red)
        else:
            self.buttonReject.setEnabled(False)

        if self.collectObj is not None:
            self.collectObj.setCentringStatus(centring_status)

        self.emit(PYSIGNAL("enableMinidiff"), (True,))

        try:
            reset_method=self.resetMethods[method]
        except KeyError,diag:
            pass
        else:
            try:
                reset_method()
            except:
                pass

    #def movedToBeam(self,x,y):
    #    pass

    def manualCentreReset(self):
        self.resetPoints()

    def automaticCentreReset(self):
        if not self.userConfirmsButton.isChecked():
           self.rejectCentring()

    def automaticCentreSuccessful(self):
        if not self.userConfirmsButton.isChecked():
           self.acceptCentring()

    #def moveToBeamSuccessful(self):
        #self.emit(PYSIGNAL("setMoveToBeamState"), (False,))
    #    pass

    #def moveToBeamReset(self):
        #self.emit(PYSIGNAL("setMoveToBeamState"), (False,))
    #    pass

    def __endDrawingPoint(self,drawingManager) :
        x,y = drawingManager.point()
        self.imageClicked(x,y,x,y)

    # Handler for clicking the video when doing the 3-click centring
    def imageClicked(self,x,y,xi,yi):
        #print "HutchMenuBrick.imageClicked",self.minidiff,self.manualCentering
        if self.currentCentring is not None and str(self.currentCentring.text())==MiniDiff.MiniDiff.MANUAL3CLICK_MODE and self.minidiff.isReady():
            try:
                points=self.minidiff.imageClicked(x,y,xi,yi)
            except StopIteration:
                pass
            else:
                self.addPoint(x,y,xi,yi)
 
    # Signals a new point in the 3-click centering
    def addPoint(self,x,y,xi,yi):
        self.clickedPoints.append((x,y,xi,yi))
        self.emitWidgetSynchronize()

    # Resets the points in the 3-click centering
    def resetPoints(self):
        self.clickedPoints=[]
        self.emitWidgetSynchronize()

    # Displays a message
    def showMessageToUser(self,message=None):
        #print "showMessage",message
        try:
            self.__drawing.setInfo(message)
        except:
            pass

    def connectNotify(self, signalName):
        if signalName=='beamPositionChanged':
            if self.minidiff and self.minidiff.isReady():
    	        self.emit(PYSIGNAL("beamPositionChanged"), (self.minidiff.imgWidth/2, self.minidiff.imgHeight/2))
        elif signalName=='calibrationChanged':
            if self.minidiff and self.minidiff.isReady():
                try:
                    self.emit(PYSIGNAL("calibrationChanged"), (1e3/self.minidiff.pixelsPerMmY, 1e3/self.minidiff.pixelsPerMmZ))      			
                except:
                    pass

    # Event when the minidiff is in ready state
    def miniDiffReady(self):
        #import pdb;pdb.set_trace()
        try:
            pxmmy=self.minidiff.pixelsPerMmY
            pxmmz=self.minidiff.pixelsPerMmZ
            self.emit(PYSIGNAL("beamPositionChanged"), (self.minidiff.imgWidth/2, self.minidiff.imgHeight/2))
        except:
            pxmmy=None
            pxmmz=None 
        if pxmmy is not None and pxmmz is not None:
            self.sampleCentreBox.setEnabled(True)
            self.updateBeam()
        else:
            self.miniDiffNotReady()

    # Event when the minidiff is in notready state
    def miniDiffNotReady(self):
        #import pdb; pdb.set_trace()
        try:
          self.__beam.hide()
        except AttributeError:
          pass
        if not self.buttonCentre.executing:
           self.sampleCentreBox.setEnabled(False)

    def miniDiffStateChanged(self,state):
        if self.buttonCentre.executing or self.isMoving or self.isShooting:
            return
        try:
            self.sampleCentreBox.setEnabled(state==self.minidiff.phiMotor.READY)
        except:
            pass

    # Displays a message (signaled from the minidiff hardware object)
    def miniDiffMessage(self,msg=None):
        #print "MINIDIFF MESSAGE!!!",msg
        self.showMessageToUser(msg)

    # Update both zoom and slits when started
    def run(self):
        if self.minidiff is not None:
            zoom=self.minidiff.zoomMotor
            if zoom is not None:
                if zoom.isReady():
                    self.zoomPositionChanged(zoom.getCurrentPositionName(),0)

        keys = {}
        self.emit(PYSIGNAL('getView'),(keys,))
        self.__drawing = keys.get('drawing',None)
        self.__view = keys.get('view',None)
        if self.minidiff is not None:
          self.minidiff._drawing = self.__drawing

        try:
            self.__point, _ = QubAddDrawing(self.__drawing, QubPointDrawingMgr, QubCanvasTarget)
            self.__point.setEndDrawCallBack(self.__endDrawingPoint)
            self.__point.setColor(Qt.yellow)
            
            self.__autoCentringPoint, _ = QubAddDrawing(self.__drawing, QubPointDrawingMgr, QubCanvasTarget)
            self.__autoCentringPoint.setColor(Qt.green)

            self.__helpLine, _ = QubAddDrawing(self.__drawing, QubPointDrawingMgr, QubCanvasVLine)
            self.__helpLine.setAutoDisconnectEvent(True)
            self.__helpLine.setExclusive(False)
            self.__helpLine.setColor(Qt.yellow)

            self.__rectangularBeam, _ = QubAddDrawing(self.__drawing, QubContainerDrawingMgr, QubCanvasSlitbox)
            self.__rectangularBeam.show()
            self.__rectangularBeam.setSlitboxSize(0,0)
            self.__rectangularBeam.setColor(Qt.red)
            self.__rectangularBeam.setSlitboxPen(QPen(Qt.blue))

            self.__beam, _ = QubAddDrawing(self.__drawing, QubContainerDrawingMgr, QubCanvasBeam) 
            self.__beam.setPen(QPen(Qt.blue))
            self.__beam.hide()

            self.__pointer, _, _ = QubAddDrawing(self.__drawing, QubPointDrawingMgr, QubCanvasHLine, QubCanvasVLine)
            self.__pointer.setDrawingEvent(QubMoveNPressed1Point)
            self.__pointer.setExclusive(False)
            self.__pointer.setColor(Qt.yellow)

            self.__scale, scale = QubAddDrawing(self.__drawing, QubContainerDrawingMgr, QubCanvasScale)
            self.sx = self.__scale.setXPixelSize
            self.sy = self.__scale.setYPixelSize
            self.__scale.show()

            try:
                self.__scale.setXPixelSize(self.__scaleX)
                self.__scale.setYPixelSize(self.__scaleY)
            except AttributeError:
                pass
            else:
		self.emit(PYSIGNAL("calibrationChanged"), (self.__scaleX, self.__scaleY))
                self.slitsPositionChanged()
                self.updateBeam(force=True)
        except:
            logging.getLogger().exception("HutchMenuBrick: problem starting up display")

    def _drawBeam(self):
        try:
          self.__rectangularBeam.show()
          if None in (self._by, self._bx):
            return
          bx = self._bx
          by = self._by
          pxmmy=self.minidiff.pixelsPerMmY
          pxmmz=self.minidiff.pixelsPerMmZ
          if self._bshape == "rectangular":
            self.__rectangularBeam.setSlitboxSize(bx*pxmmy, by*pxmmz)
          else:
            self.__rectangularBeam.setSlitboxSize(0,0)
            self.__beam.setSize(bx*pxmmy, by*pxmmz)
            self.__beam.show()
        except:
          pass
    
    def _updateBeam(self, ret):
        #logging.info("UPDATE BEAM %s", ret)
        self._bx = float(ret["size_x"])
        self._bshape = ret["shape"]
        self._by = float(ret["size_y"])
        self._drawBeam()

    def updateBeam(self,force=False):
        if self["displayBeam"]:
              beam_x, beam_y = (self.minidiff.imgWidth/2, self.minidiff.imgHeight/2)
              try:
                self.__beam.move(beam_x, beam_y)
                try:
                  #get_beam_info = self.minidiff.getCommandObject("getBeamInfo")
                  if force or get_beam_info.isSpecReady():
                    self.minidiff.getBeamInfo( callback= self._updateBeam, error_callback=None)
                    #get_beam_info(callback=self._updateBeam, error_callback=None)
                except:
                  logging.getLogger().exception("Could not get beam size: cannot display beam")
                  self.__beam.hide()
              except AttributeError:
                pass


    # Zoom changed: update pixels per mm
    def zoomPositionChanged(self,position,offset):
        pxmmy, pxmmz, pxsize_y, pxsize_z = None,None,None,None

        if offset is None:
          # unknown zoom pos.
          try:
            self.__scale.hide()
            self.__rectangularBeam.hide()
            self.__beam.hide()
          except AttributeError:
            self.__scaleX = None
            self.__scaleY = None
        else:
            if self.minidiff is not None:
                pxmmy=self.minidiff.pixelsPerMmY
                pxmmz=self.minidiff.pixelsPerMmZ
                if pxmmy is not None and pxmmz is not None:
                    pxsize_y = 1e-3 / pxmmy
                    pxsize_z = 1e-3 / pxmmz

                try:
                    self.sx(pxsize_y)
                    self.sy(pxsize_z)
                except AttributeError:
                    self.__scaleX = pxsize_y
                    self.__scaleY = pxsize_z
                else:
                    self.emit(PYSIGNAL("calibrationChanged"), (pxsize_y, pxsize_z))
                    self._drawBeam()
                    self.__scale.show()
               

    # Slits changed: update beam size
    def slitsPositionChanged(self, *args):
        if self.minidiff is None or self.slitbox is None or self.minidiff.pixelsPerMmY is None or self.minidiff.pixelsPerMmZ is None:
            pass
        else:
            self.updateBeam(force=True)

class MenuButton(QToolButton):
    def __init__(self, parent, caption):
        QToolButton.__init__(self,parent)
        self.executing=None
        self.runIcon=None
        self.stopIcon=None
        self.standardColor=None
        self.setUsesTextLabel(True)
        self.setTextLabel(caption)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self, SIGNAL('clicked()'), self.buttonClicked)
    def setIcons(self,icon_run,icon_stop):
        self.runIcon=Icons.load(icon_run)
        self.stopIcon=Icons.load(icon_stop)
        if self.executing:
            self.setPixmap(self.stopIcon)
        else:
            self.setPixmap(self.runIcon)
    def buttonClicked(self):
        if self.executing:
            self.emit(PYSIGNAL('cancelCommand'), ())
        else:
            self.setEnabled(False)
            self.emit(PYSIGNAL('executeCommand'), ())
    def commandStarted(self):
        if self.standardColor is None:
            self.standardColor=self.paletteBackgroundColor()
        self.setPaletteBackgroundColor(QWidget.yellow)
        if self.stopIcon is not None:
            self.setPixmap(self.stopIcon)
        self.executing=True
        self.setEnabled(True)
    def isExecuting(self):
        return self.executing
    def commandDone(self):
        self.executing=False
        if self.standardColor is not None:
            self.setPaletteBackgroundColor(self.standardColor)
        if self.runIcon is not None:
            self.setPixmap(self.runIcon)
        self.setEnabled(True)
    def commandFailed(self):
        self.commandDone()


class HorizontalSpacer3(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    def sizeHint(self):
        return QSize(5,0)


class HorizontalSpacer4(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    def sizeHint(self):
        return QSize(5,0)
