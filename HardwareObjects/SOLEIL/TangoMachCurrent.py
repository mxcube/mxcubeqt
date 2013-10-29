# -*- coding: utf-8 -*-
#$Id: MachCurrent.py,v 1.3 2004/11/23 08:54:06 guijarro Exp guijarro $
from HardwareRepository.BaseHardwareObjects import Device
#from SimpleDevice import SimpleDevice
import PyTango
import logging

class TangoMachCurrent(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.opmsg = ''
        self.fillmode = ''

    def init(self):
            
        self.device = PyTango.DeviceProxy(self.getProperty("tangoname"))
        self.flux =  PyTango.DeviceProxy('i11-ma-c04/dt/xbpm_diode.1')
        #self.device.timeout = 6000 # Setting timeout to 6 sec
        self.setIsReady(True)
        stateChan = self.getChannelObject("current") # utile seulement si statechan n'est pas defini dans le code
        stateChan.connectSignal("update", self.valueChanged)

        #if self.device.imported:
        #    self.setPollCommand('DevReadSigValues')
        #    self.setIsReady(True)

    def valueChanged(self, value):
        mach = value
        opmsg = None
        fillmode = None
        refill = None
        try:
            refill = self.device.read_attribute("lifetime").value
            #opmsg = self.device.DevReadOpMesg() #self.executeCommand('DevReadOpMesg()')
            #opmsg = self.device.read_attribute("message").value
            opmsg = self.device.read_attribute("operatorMessage").value
            opmsg = opmsg.strip()
            opmsg = opmsg.replace(': Faisceau disponible', ':\nFaisceau disponible')
            #' ' #On Gavin's request ;-)
            #fillmode = self.device.DevReadFillMode()
            fillmode = self.device.read_attribute("fillingMode").value + " filling"
            fillmode = fillmode.strip()
            fillmode += ': ' + opmsg[opmsg.rindex(':') + 2:]
            
        except AttributeError:
            #self.device.command_inout("Init")
            #self.device.InitDevice()
            #self.device.Init()
            logging.getLogger("HWR").error("%s: AAA AttributeError machinestatus not responding, %s", self.name(), '')
    
        except:
            # Too much error with this Device... stoping the logging (Pierre 22/03/2010).
            #logging.getLogger("HWR").error("%s: BBB machinestatus not responding, %s", self.name(), '')
            pass
        
        if opmsg and opmsg != self.opmsg:
            self.opmsg = opmsg
            logging.getLogger('HWR').info("<b>"+self.opmsg+"</b>")
        
        opmsg = 'Flux: ' + str(round(self.flux.intensity, 3)) + ' uA' #MS. 29.01.13 ugly hack to have flux in the output instead of opmsg
        self.emit('valueChanged', (mach, opmsg, fillmode, opmsg))

