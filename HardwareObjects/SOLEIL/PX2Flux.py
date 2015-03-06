
from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import Device
import logging
import PyTango

class PX2Flux(Device):

    def __init__(self, name):
        Device.__init__(self, name)

    def init(self):
        logging.info('PX2Flux, initializing')
        self.flux_channel = self.getChannelObject("flux")
    
    def getCurrentFlux(self):
        
        try:
            flx = self.flux_channel.getValue()/1e12
            logging.info('PX2Flux, getCurrentFlux %s' % flx)
            return flx
            
        except PyTango.DevFailed:
            import traceback
                
            logging.info('PX2Flux, getCurrentFlux failed' % traceback.format_exc())
            return -1


def test():
    import os
    import time
    hwr_directory = os.environ["XML_FILES_PATH"]

    hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
    hwr.connect()

    flux = hwr.getHardwareObject("/flux")

    print "PX2 Flux is ",flux.getCurrentFlux()


if __name__ == '__main__':
   test()

