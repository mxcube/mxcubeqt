from SOLEILMultiCollect import *
import shutil
import logging
from PyTango import DeviceProxy
import numpy
import re

class PX2MultiCollect(SOLEILMultiCollect):
    def __init__(self, name):

        SOLEILMultiCollect.__init__(self, name, LimaAdscDetector(), TunableEnergy())
        #SOLEILMultiCollect.__init__(self, name, DummyDetector(), TunableEnergy())

    def init(self):

        logging.info("headername is %s" % self.headername )

        self.headerdev     = DeviceProxy( self.headername )
        self.mono1dev      = DeviceProxy( self.mono1name )
        self.det_mt_ts_dev = DeviceProxy( self.detmttsname )
        self.det_mt_tx_dev = DeviceProxy( self.detmttxname )
        self.det_mt_tz_dev = DeviceProxy( self.detmttzname )

        self._detector.prepareHeader = self.prepareHeader
        SOLEILMultiCollect.init(self)
       
    def prepareHeader(self):
        '''Will set up header given the actual values of beamline energy, mono and detector distance'''
        X, Y = self.beamCenter()

        BeamCenterX = str(round(X, 3))
        BeamCenterY = str(round(Y, 3))
        head = self.headerdev.read_attribute('header').value
        head = re.sub('BEAM_CENTER_X=\d\d\d\.\d', 'BEAM_CENTER_X=' + BeamCenterX, head)
        head = re.sub('BEAM_CENTER_Y=\d\d\d\.\d', 'BEAM_CENTER_Y=' + BeamCenterY, head)
        return head

    def beamCenter(self):
        '''Will calculate beam center coordinates'''

        # Useful values
        tz_ref = -6.5     # reference tz position for linear regression
        tx_ref = -17.0    # reference tx position for linear regression
        q = 0.102592  # pixel size in milimeters

        wavelength = self.mono1dev.read_attribute('lambda').value
        distance   = self.det_mt_ts_dev.read_attribute('position').value
        tx         = self.det_mt_tx_dev.read_attribute('position').value
        tz         = self.det_mt_tz_dev.read_attribute('position').value

        zcor = tz - tz_ref
        xcor = tx - tx_ref

        Theta = numpy.matrix([[1.55557116e+03,  1.43720063e+03],
                              [-8.51067454e-02, -1.84118001e-03],
                              [-1.99919592e-01,  3.57937064e+00]])  # values from 16.05.2013

        X = numpy.matrix([1., distance, wavelength])

        Origin = Theta.T * X.T
        Origin = Origin * q

        return Origin[1] + zcor, Origin[0] + xcor


