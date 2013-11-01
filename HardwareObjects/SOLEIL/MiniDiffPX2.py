
import logging, time
from MiniDiff import MiniDiff
import PyTango

class MiniDiffPX2(MiniDiff):

   def _init(self,*args):
       MiniDiff._init(self, *args)

       self.md2_ready = False

       try:
          self.md2 = PyTango.DeviceProxy( self.tangoname )
       except:
          logging.error("MiniDiffPX2 / Cannot connect to tango device: %s ", self.tangoname )
       else:
          self.md2_ready = True

       # some defaults
       self.anticipation  = 1
       self.collect_phaseposition = 4

   def getState(self):
       return str( self.md2.state() )

   def setScanStartAngle(self, sangle):
       logging.info("MiniDiffPX2 / setting start angle to %s ", sangle )
       if self.md2_ready:
           self.md2.write_attribute("ScanStartAngle", sangle )

   def startScan(self,wait=True):
       logging.info("MiniDiffPX2 / starting scan " )

       if self.md2_ready:
           diffstate = self.getState()
           logging.info("SOLEILCollect - diffractometer scan started  (state: %s)" % diffstate)
           self.md2.StartScan()

       # self.getCommandObject("start_scan")() - if we define start_scan command in *xml

   def goniometerReady(self, oscrange, npass, exptime):
       logging.info("MiniDiffPX2 / programming gonio oscrange=%s npass=%s exptime=%s" % (oscrange,npass, exptime) )

       if self.md2_ready:

          diffstate = self.getState()
          logging.info("SOLEILCollect - setting gonio ready (state: %s)" % diffstate)

          self.md2.write_attribute('ScanAnticipation', self.anticipation)
          self.md2.write_attribute('ScanNumberOfPasses', npass)
          self.md2.write_attribute('ScanRange', oscrange)
          self.md2.write_attribute('ScanExposureTime', exptime)
          self.md2.write_attribute('PhasePosition', self.collect_phaseposition)

   def getBeamInfo(self, callback=None, error_callback=None):
      logging.info(" I am getBeamInfo in MiniDiff2.py ")
      
      d = {}
      d["size_x"] = 100
      d["size_y"] = 50
      d["shape"] = "elliptical"

      return d
      #callback( d )
