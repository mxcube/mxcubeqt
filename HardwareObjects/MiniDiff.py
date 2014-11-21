import gevent
from gevent.event import AsyncResult
from Qub.Tools import QubImageSave
from HardwareRepository.BaseHardwareObjects import Equipment
from HardwareRepository.TaskUtils import *
import tempfile
import logging
import math
import os
import time
from HardwareRepository import HardwareRepository
import copy
import sample_centring
import numpy
import queue_model_objects_v1 as qmo

class myimage:
    def __init__(self, drawing):
        self.drawing = drawing
        matrix = self.drawing.matrix()
        self.zoom = 1
        if matrix is not None:
            self.zoom = matrix.m11()

    def save(self, filename=None):
        self.img = self.drawing.getPPP()

        if filename is None:
          fd, name = tempfile.mkstemp()
          os.close(fd)
        else:
          name = filename

        QubImageSave.save(name, self.img, self.drawing.canvas(), self.zoom, "JPEG")

        if filename is None:
          f = open(name, "r")
          self.imgcopy = f.read()
          f.close()
          os.unlink(name)

    def __str__(self):
        self.save()
        return self.imgcopy


def take_snapshots(number_of_snapshots, light, light_motor, phi, zoom, drawing):
  if number_of_snapshots <= 0:
    return

  centredImages = []

  if light is not None:
    light.wagoIn()

    # No light level, choose default
    if light_motor.getPosition() == 0:
      zoom_level = int(zoom.getPosition())
      light_level = None

      try:
        light_level = zoom['positions'][0][zoom_level].getProperty('lightLevel')
      except IndexError:
        logging.getLogger("HWR").info("Could not get default light level")
        light_level = 1

      if light_level:
        light_motor.move(light_level)

    while light.getWagoState()!="in":
      time.sleep(0.5)

  for i, angle in enumerate([-90]*number_of_snapshots):
     logging.getLogger("HWR").info("MiniDiff: taking snapshot #%d", i+1)
     centredImages.append((phi.getPosition(),str(myimage(drawing))))
     phi.syncMoveRelative(angle)

  centredImages.reverse() # snapshot order must be according to positive rotation direction

  return centredImages


class MiniDiff(Equipment):
    MANUAL3CLICK_MODE = "Manual 3-click"
    C3D_MODE = "Computer automatic"
    #MOVE_TO_BEAM_MODE = "Move to Beam"

    def __init__(self, *args):
        Equipment.__init__(self, *args)

        qmo.CentredPosition.set_diffractometer_motor_names("phi",
                                                           "focus",
                                                           "phiz",
                                                           "phiy",
                                                           "zoom",
                                                           "sampx",
                                                           "sampy",
                                                           "kappa",
                                                           "kappa_phi")

        self.phiMotor = None
        self.phizMotor = None
        self.phiyMotor = None
        self.lightMotor = None
        self.zoomMotor = None
        self.sampleXMotor = None
        self.sampleYMotor = None
        self.camera = None
        self.sampleChanger = None
        self.lightWago = None
        self.currentSampleInfo = None
        self.aperture = None
        self.beam_info = None
      
        self.pixelsPerMmY=None
        self.pixelsPerMmZ=None
        self.imgWidth = None
        self.imgHeight = None
        self.centredTime = 0
        self.user_confirms_centring = True

        self.connect(self, 'equipmentReady', self.equipmentReady)
        self.connect(self, 'equipmentNotReady', self.equipmentNotReady)     


    def init(self):
        self.centringMethods={MiniDiff.MANUAL3CLICK_MODE: self.start3ClickCentring,\
            MiniDiff.C3D_MODE: self.startAutoCentring }
        self.cancelCentringMethods={}

        self.currentCentringProcedure = None
        self.currentCentringMethod = None

        self.centringStatus={"valid":False}

        try:
          phiz_ref = self["centringReferencePosition"].getProperty("phiz")
        except:
          phiz_ref = None
        
        self.phiMotor = self.getDeviceByRole('phi')
        self.phizMotor = self.getDeviceByRole('phiz')
        self.phiyMotor = self.getObjectByRole("phiy")
        self.zoomMotor = self.getDeviceByRole('zoom')
        self.lightMotor = self.getDeviceByRole('light')
        self.focusMotor = self.getDeviceByRole('focus')
        self.sampleXMotor = self.getDeviceByRole("sampx")
        self.sampleYMotor = self.getDeviceByRole("sampy")
        self.camera = self.getDeviceByRole('camera')
        self.kappaMotor = self.getDeviceByRole('kappa')
        self.kappaPhiMotor = self.getDeviceByRole('kappa_phi')
        self.beam_info = self.getObjectByRole('beam_info')

        # mh 2013-11-05:why is the channel read directly? disabled for the moment
        # self.camera.addChannel({ 'type': 'tango', 'name': 'jpegImage' }, "JpegImage")

        self.centringPhi=sample_centring.CentringMotor(self.phiMotor, direction=-1)
        self.centringPhiz=sample_centring.CentringMotor(self.phizMotor, reference_position=phiz_ref)
        self.centringPhiy=sample_centring.CentringMotor(self.phiyMotor)
        self.centringSamplex=sample_centring.CentringMotor(self.sampleXMotor)
        self.centringSampley=sample_centring.CentringMotor(self.sampleYMotor)

        hwr = HardwareRepository.HardwareRepository()
        sc_prop=self.getProperty("samplechanger")
        if sc_prop is not None:
            try:
                self.sampleChanger=hwr.getHardwareObject(sc_prop)
            except:
                pass
        wl_prop=self.getProperty("wagolight")
        if wl_prop is not None:
            try:
                self.lightWago=hwr.getHardwareObject(wl_prop)
            except:
                pass
        aperture_prop = self.getProperty("aperture")
        if aperture_prop is not None:
            try:
                self.aperture = hwr.getHardwareObject(aperture_prop)
            except:
                pass
            
        if self.phiMotor is not None:
            self.connect(self.phiMotor, 'stateChanged', self.phiMotorStateChanged)
            self.connect(self.phiMotor, "positionChanged", self.emitDiffractometerMoved)
        else:
            logging.getLogger("HWR").error('MiniDiff: phi motor is not defined in minidiff equipment %s', str(self.name()))
        if self.phizMotor is not None:
            self.connect(self.phizMotor, 'stateChanged', self.phizMotorStateChanged)
            self.connect(self.phizMotor, 'positionChanged', self.phizMotorMoved)
            self.connect(self.phizMotor, "positionChanged", self.emitDiffractometerMoved)
        else:
            logging.getLogger("HWR").error('MiniDiff: phiz motor is not defined in minidiff equipment %s', str(self.name()))
        if self.phiyMotor is not None:
            self.connect(self.phiyMotor, 'stateChanged', self.phiyMotorStateChanged)
            self.connect(self.phiyMotor, 'positionChanged', self.phiyMotorMoved)
            self.connect(self.phiyMotor, "positionChanged", self.emitDiffractometerMoved)
        else:
            logging.getLogger("HWR").error('MiniDiff: phiy motor is not defined in minidiff equipment %s', str(self.name()))
        if self.zoomMotor is not None:
            self.connect(self.zoomMotor, 'predefinedPositionChanged', self.zoomMotorPredefinedPositionChanged)
            self.connect(self.zoomMotor, 'stateChanged', self.zoomMotorStateChanged)
        else:
            logging.getLogger("HWR").error('MiniDiff: zoom motor is not defined in minidiff equipment %s', str(self.name()))
        if self.sampleXMotor is not None:
            self.connect(self.sampleXMotor, 'stateChanged', self.sampleXMotorStateChanged)
            self.connect(self.sampleXMotor, 'positionChanged', self.sampleXMotorMoved)
            self.connect(self.sampleXMotor, "positionChanged", self.emitDiffractometerMoved)
        else:
            logging.getLogger("HWR").error('MiniDiff: sampx motor is not defined in minidiff equipment %s', str(self.name()))
        if self.sampleYMotor is not None:
            self.connect(self.sampleYMotor, 'stateChanged', self.sampleYMotorStateChanged)
            self.connect(self.sampleYMotor, 'positionChanged', self.sampleYMotorMoved)
            self.connect(self.sampleYMotor, "positionChanged", self.emitDiffractometerMoved)
        else:
            logging.getLogger("HWR").error('MiniDiff: sampx motor is not defined in minidiff equipment %s', str(self.name()))
        if self.camera is None:
            logging.getLogger("HWR").error('MiniDiff: camera is not defined in minidiff equipment %s', str(self.name()))
        else:
            self.imgWidth, self.imgHeight = self.camera.getWidth(), self.camera.getHeight()
        if self.sampleChanger is None:
            logging.getLogger("HWR").warning('MiniDiff: sample changer is not defined in minidiff equipment %s', str(self.name()))
        else:
            try:
                self.connect(self.sampleChanger, 'sampleIsLoaded', self.sampleChangerSampleIsLoaded)
            except:
                logging.getLogger("HWR").exception('MiniDiff: could not connect to sample changer smart magnet')
        if self.lightWago is not None:
            self.connect(self.lightWago, 'wagoStateChanged', self.wagoLightStateChanged)
        else:
            logging.getLogger("HWR").warning('MiniDiff: wago light is not defined in minidiff equipment %s', str(self.name()))
        if self.aperture is not None:
            self.connect(self.aperture, 'predefinedPositionChanged', self.apertureChanged)
            self.connect(self.aperture, 'positionReached', self.apertureChanged)


    def save_snapshot(self, filename):
        img = myimage(self._drawing)
        img.save(filename)

    def setSampleInfo(self, sample_info):
        self.currentSampleInfo = sample_info

    def emitDiffractometerMoved(self, *args):
      self.emit("diffractometerMoved", ())
        
    def isReady(self):
        return self.isValid() and not any([m.motorIsMoving() for m in (self.sampleXMotor, self.sampleYMotor, self.zoomMotor, self.phiMotor, self.phizMotor, self.phiyMotor)])
    

    def isValid(self):
        return self.sampleXMotor is not None and \
            self.sampleYMotor is not None and \
            self.zoomMotor is not None and \
            self.phiMotor is not None and \
            self.phizMotor is not None and \
            self.phiyMotor is not None and \
            self.camera is not None


    def apertureChanged(self, *args):
        # will trigger minidiffReady signal for update of beam size in video
        self.equipmentReady()
         

    def equipmentReady(self):
        self.emit('minidiffReady', ())


    def equipmentNotReady(self):
        self.emit('minidiffNotReady', ())


    def wagoLightStateChanged(self,state):
        pass


    def phiMotorStateChanged(self,state):
        self.emit('phiMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def phizMotorStateChanged(self, state):
        self.emit('phizMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def phiyMotorStateChanged(self, state):
        self.emit('phiyMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def getCalibrationData(self, offset):
        if self.zoomMotor is not None:
            if self.zoomMotor.hasObject('positions'):
                for position in self.zoomMotor['positions']:
                    if abs(position.offset - offset)<=self.zoomMotor.delta:
                        calibrationData = position['calibrationData']
                        return (float(calibrationData.pixelsPerMmY) or 0, float(calibrationData.pixelsPerMmZ) or 0)
        return (None, None)

    def get_pixels_per_mm(self):
	return (self.pixelsPerMmY, self.pixelsPerMmZ)

    def getBeamInfo(self, callback=None):
	beam_info = self.beam_info.get_beam_info() 
	if callable(callback):
          callback(beam_info)
        return beam_info

    def zoomMotorPredefinedPositionChanged(self, positionName, offset):
        self.pixelsPerMmY, self.pixelsPerMmZ = self.getCalibrationData(offset)
        self.emit('zoomMotorPredefinedPositionChanged', (positionName, offset, ))


    def zoomMotorStateChanged(self, state):
        self.emit('zoomMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def sampleXMotorStateChanged(self, state):
        self.emit('sampxMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def sampleYMotorStateChanged(self, state):
        self.emit('sampyMotorStateChanged', (state, ))
        self.emit('minidiffStateChanged', (state,))


    def invalidateCentring(self):
        if self.currentCentringProcedure is None and self.centringStatus["valid"]:
            self.centringStatus={"valid":False}
            self.emitProgressMessage("")
            self.emit('centringInvalid', ())


    def phizMotorMoved(self, pos):
        if time.time() - self.centredTime > 1.0:
          self.invalidateCentring()

    def phiyMotorMoved(self, pos):
        if time.time() - self.centredTime > 1.0:
           self.invalidateCentring()


    def sampleXMotorMoved(self, pos):
        if time.time() - self.centredTime > 1.0:
           self.invalidateCentring()


    def sampleYMotorMoved(self, pos):
        if time.time() - self.centredTime > 1.0:
           self.invalidateCentring()


    def sampleChangerSampleIsLoaded(self, state):
        if time.time() - self.centredTime > 1.0:
           self.invalidateCentring()

    def getBeamPosX(self):
        return self.imgWidth / 2

    def getBeamPosY(self):
        return self.imgHeight / 2

    def moveToBeam(self, x, y):
        try:
            beam_xc = self.getBeamPosX()
            beam_yc = self.getBeamPosY()
            self.centringPhiz.moveRelative((y-beam_yc)/float(self.pixelsPerMmZ))
            self.centringPhiy.moveRelative((x-beam_xc)/float(self.pixelsPerMmY))
        except:
            logging.getLogger("HWR").exception("MiniDiff: could not center to beam, aborting")


    def getAvailableCentringMethods(self):
        return self.centringMethods.keys()


    def startCentringMethod(self,method,sample_info=None):
        if self.currentCentringMethod is not None:
            logging.getLogger("HWR").error("MiniDiff: already in centring method %s" % self.currentCentringMethod)
            return
        
        curr_time=time.strftime("%Y-%m-%d %H:%M:%S")
        self.centringStatus={"valid":False, "startTime":curr_time}

        self.emitCentringStarted(method)

        try:
            fun=self.centringMethods[method]
        except KeyError,diag:
            logging.getLogger("HWR").error("MiniDiff: unknown centring method (%s)" % str(diag))
            self.emitCentringFailed()
        else:
            try:
                fun(sample_info)
            except:
                logging.getLogger("HWR").exception("MiniDiff: problem while centring")
                self.emitCentringFailed()


    def cancelCentringMethod(self,reject=False):
        if self.currentCentringProcedure is not None:
            try:
                self.currentCentringProcedure.kill()
            except:
                logging.getLogger("HWR").exception("MiniDiff: problem aborting the centring method")
            try:
                fun=self.cancelCentringMethods[self.currentCentringMethod]
            except KeyError,diag:
                self.emitCentringFailed()
            else:
                try:
                    fun()
                except:
                    self.emitCentringFailed()
        else:
            self.emitCentringFailed()

        self.emitProgressMessage("")

        if reject:
            self.rejectCentring()


    def currentCentringMethod(self):
        return self.currentCentringMethod

    
    def saveCurrentPos(self):
        self.centringStatus["motors"] = self.getPositions()
        self.acceptCentring()


    def start3ClickCentring(self, sample_info=None):
        self.currentCentringProcedure = sample_centring.start({"phi":self.centringPhi,
                                                               "phiy":self.centringPhiy,
                                                               "sampx": self.centringSamplex,
                                                               "sampy": self.centringSampley,
                                                               "phiz": self.centringPhiz }, 
                                                              self.pixelsPerMmY, self.pixelsPerMmZ, 
                                                              self.getBeamPosX(), self.getBeamPosY())
                                                                         
        self.currentCentringProcedure.link(self.manualCentringDone)

  
    def motor_positions_to_screen(self, centred_positions_dict):
        self.pixelsPerMmY, self.pixelsPerMmZ = self.getCalibrationData(self.zoomMotor.getPosition())
        phi_angle = math.radians(self.centringPhi.direction*self.centringPhi.getPosition()) 
        sampx = self.centringSamplex.direction * (centred_positions_dict["sampx"]-self.centringSamplex.getPosition())
        sampy = self.centringSampley.direction * (centred_positions_dict["sampy"]-self.centringSampley.getPosition())
        phiy = self.centringPhiy.direction * (centred_positions_dict["phiy"]-self.centringPhiy.getPosition())
        phiz = self.centringPhiz.direction * (centred_positions_dict["phiz"]-self.centringPhiz.getPosition())
        rotMatrix = numpy.matrix([math.cos(phi_angle), -math.sin(phi_angle), math.sin(phi_angle), math.cos(phi_angle)])
        rotMatrix.shape = (2, 2)
        invRotMatrix = numpy.array(rotMatrix.I)
        dx, dy = numpy.dot(numpy.array([sampx, sampy]), invRotMatrix)*self.pixelsPerMmY
        beam_pos_x = self.getBeamPosX()
        beam_pos_y = self.getBeamPosY()

        x = (phiy * self.pixelsPerMmY) + beam_pos_x
        y = dy + (phiz * self.pixelsPerMmZ) + beam_pos_y

        return x, y
 
    def manualCentringDone(self, manual_centring_procedure):
        try:
          motor_pos = manual_centring_procedure.get()
          if isinstance(motor_pos, gevent.GreenletExit):
            raise motor_pos
        except:
          logging.exception("Could not complete manual centring")
          self.emitCentringFailed()
        else:
          self.emitProgressMessage("Moving sample to centred position...")
          self.emitCentringMoving()
          try:
            sample_centring.end()
          except:
            logging.exception("Could not move to centred position")
            self.emitCentringFailed()
          
          #logging.info("EMITTING CENTRING SUCCESSFUL")
          self.centredTime = time.time()
          self.emitCentringSuccessful()
          self.emitProgressMessage("")

    def autoCentringDone(self, auto_centring_procedure): 
        self.emitProgressMessage("")
        self.emit("newAutomaticCentringPoint", (-1,-1))

        res = auto_centring_procedure.get()
        
        if isinstance(res, gevent.GreenletExit):
          logging.error("Could not complete automatic centring")
          self.emitCentringFailed()
        else: 
          positions = self.zoomMotor.getPredefinedPositionsList()
          i = len(positions) / 2
          self.zoomMotor.moveToPosition(positions[i-1])

          #be sure zoom stop moving
          while self.zoomMotor.motorIsMoving():
              time.sleep(0.1)

          self.pixelsPerMmY, self.pixelsPerMmZ = self.getCalibrationData(self.zoomMotor.getPosition())

          if self.user_confirms_centring:
            self.emitCentringSuccessful()
          else:
            self.emitCentringSuccessful()
            self.acceptCentring()
              
    def startAutoCentring(self, sample_info=None, loop_only=False):
        self.currentCentringProcedure = sample_centring.start_auto(self.camera, 
                                                                   {"phi":self.centringPhi,
                                                                    "phiy":self.centringPhiy,
                                                                    "sampx": self.centringSamplex,
                                                                    "sampy": self.centringSampley,
                                                                    "phiz": self.centringPhiz },
                                                                   self.pixelsPerMmY, self.pixelsPerMmZ, 
                                                                   self.getBeamPosX(), self.getBeamPosY(), 
                                                                   msg_cb=self.emitProgressMessage,
                                                                   new_point_cb=lambda point: self.emit("newAutomaticCentringPoint", point))
       
        self.currentCentringProcedure.link(self.autoCentringDone)

	self.emitProgressMessage("Starting automatic centring procedure...")
       
    @task 
    def moveToCentredPosition(self, centred_position):
      return self.moveMotors(centred_position.as_dict())

    def imageClicked(self, x, y, xi, yi):
        sample_centring.user_click(x,y)

    def emitCentringStarted(self,method):
        self.currentCentringMethod=method
        self.emit('centringStarted', (method,False))

    def acceptCentring(self):
        self.centringStatus["valid"]=True
        self.centringStatus["accepted"]=True
        self.emit('centringAccepted', (True,self.getCentringStatus()))

    def rejectCentring(self):
        if self.currentCentringProcedure:
          self.currentCentringProcedure.kill()
        self.centringStatus={"valid":False}
        self.emitProgressMessage("")
        self.emit('centringAccepted', (False,self.getCentringStatus()))

    def emitCentringMoving(self):
        self.emit('centringMoving', ())

    def emitCentringFailed(self):
        self.centringStatus={"valid":False}
        method=self.currentCentringMethod
        self.currentCentringMethod = None
        self.currentCentringProcedure=None
        self.emit('centringFailed', (method,self.getCentringStatus()))

    def emitCentringSuccessful(self):
        if self.currentCentringProcedure is not None:
            curr_time=time.strftime("%Y-%m-%d %H:%M:%S")
            self.centringStatus["endTime"]=curr_time
            self.centringStatus["motors"]=self.getPositions()
            centred_pos = self.currentCentringProcedure.get()
            for role in self.centringStatus["motors"].iterkeys():
              motor = self.getDeviceByRole(role)
              try:
                self.centringStatus["motors"][role] = centred_pos[motor]
              except KeyError:
		continue

            self.centringStatus["method"]=self.currentCentringMethod
            self.centringStatus["valid"]=True
            
            method=self.currentCentringMethod
            self.emit('centringSuccessful', (method,self.getCentringStatus()))
            self.currentCentringMethod = None
            self.currentCentringProcedure = None
        else:
            logging.getLogger("HWR").debug("MiniDiff: trying to emit centringSuccessful outside of a centring")


    def emitProgressMessage(self,msg=None):
        #logging.getLogger("HWR").debug("%s: %s", self.name(), msg)
        self.emit('progressMessage', (msg,))


    def getCentringStatus(self):
        return copy.deepcopy(self.centringStatus)


    def getPositions(self):
      return { "phi": self.phiMotor.getPosition(),
               "focus": self.focusMotor.getPosition(),
               "phiy": self.phiyMotor.getPosition(),
               "phiz": self.phizMotor.getPosition(),
               "sampx": self.sampleXMotor.getPosition(),
               "sampy": self.sampleYMotor.getPosition(),
               "kappa": self.kappaMotor.getPosition() if self.kappaMotor else None,
               "kappa_phi": self.kappaPhiMotor.getPosition() if self.kappaPhiMotor else None,    
               "zoom": self.zoomMotor.getPosition()}
    

    def moveMotors(self, roles_positions_dict):
        motor = { "phi": self.phiMotor,
                  "focus": self.focusMotor,
                  "phiy": self.phiyMotor,
                  "phiz": self.phizMotor,
                  "sampx": self.sampleXMotor,
                  "sampy": self.sampleYMotor,
                  "kappa": self.kappaMotor,
                  "kappa_phi": self.kappaPhiMotor,
                  "zoom": self.zoomMotor }
   
        for role, pos in roles_positions_dict.iteritems():
           m = motor.get(role)
           if m is not None:
             m.move(pos)
 
        # TODO: remove this sleep, the motors states should
        # be MOVING since the beginning (or READY if move is
        # already finished) 
        time.sleep(1)
 
        while not all([m.getState() == m.READY for m in motor.itervalues() if m is not None]):
           time.sleep(0.1)


    def takeSnapshots(self, image_count, wait=False):
        self.camera.forceUpdate = True
        
        snapshotsProcedure = gevent.spawn(take_snapshots, image_count, self.lightWago, self.lightMotor ,self.phiMotor,self.zoomMotor,self._drawing)
        self.emit('centringSnapshots', (None,))
        self.emitProgressMessage("Taking snapshots")
        self.centringStatus["images"]=[]
        snapshotsProcedure.link(self.snapshotsDone)

        if wait:
          self.centringStatus["images"] = snapshotsProcedure.get()

 
    def snapshotsDone(self, snapshotsProcedure):
        self.camera.forceUpdate = False
        
        try:
           self.centringStatus["images"] = snapshotsProcedure.get()
        except:
           logging.getLogger("HWR").exception("MiniDiff: could not take crystal snapshots")
           self.emit('centringSnapshots', (False,))
           self.emitProgressMessage("")
        else:
           self.emit('centringSnapshots', (True,))
           self.emitProgressMessage("")
        self.emitProgressMessage("Sample is centred!")
        #self.emit('centringAccepted', (True,self.getCentringStatus()))



    def simulateAutoCentring(self,sample_info=None):
        pass
