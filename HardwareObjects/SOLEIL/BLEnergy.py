from qt import *
from HardwareRepository.BaseHardwareObjects import Device
from PyTango import DeviceProxy

import logging
import os
import time
import types

class BLEnergy (Device) :
    
    stateEnergy = {'ALARM': 'error',
                   'FAULT': 'error',
                   'RUNNING': 'moving',
                   'MOVING' : 'moving',
                   'STANDBY' : 'ready',
                   'UNKNOWN': 'unknown',
                   'EXTRACT': 'outlimits'}

    def init(self):
        
        self.moving = None
        self.deviceOk = True
        self.prev_state = None
        self.doBacklashCompensation = True
        
        # Connect to device BLEnergy defined "tangoname" in the xml file 
        try :
            self.BLEnergydevice = DeviceProxy(self.getProperty("tangoname"))
        except :
            self.errorDeviceInstance(self.getProperty("tangoname"))
            
        # Connect to device mono defined "tangoname2" in the xml file 
        # used for conversion in wavelength
        try :    
            self.monodevice = DeviceProxy(self.getProperty("tangoname2"))
        except :    
            self.errorDeviceInstance(self.getProperty("tangoname2"))

        # Nom du device bivu (Energy to gap) : necessaire pour amelioration du positionnement de l'onduleur (Backlash)
        try :    
#            self.U20Energydevice = DeviceProxy(self.getProperty("tangoname3"), movingState="RUNNING")
# Modif suite a changement par ICA de l etat du device U20 RUNNING devient MOVING
            self.U20Energydevice = DeviceProxy(self.getProperty("tangoname3"))
        except :    
            self.errorDeviceInstance(self.getProperty("tangoname3"))
            
        self.doBacklashCompensation = self.getProperty("backlash")
#        print self.doBacklashCompensation
            
        # parameters for polling     
        if self.deviceOk :
            self.sConnected()
            self.prev_state = str( self.BLEnergydevice.State() )
            energyChan = self.getChannelObject("energy") 
            energyChan.connectSignal("update", self.energyChanged)
            stateChan = self.getChannelObject("state") # utile seulement si statechan n'est pas defini dans le code
            stateChan.connectSignal("update", self.stateChanged)

    def stateChanged(self,value):
        if (str(value) == 'MOVING') :
            self.moveEnergyCmdStarted()
        if self.prev_state == 'MOVING' or self.moving == True:
            if str(value) != 'MOVING' :
                self.moveEnergyCmdFinished() 
                     
        self.prev_state = str(value)
        
        self.emit('stateChanged', BLEnergy.stateEnergy[str(value)])
        
    # function called during polling
    def energyChanged(self,value):
        #logging.getLogger("HWR").debug("%s: BLEnergy.energyChanged: %.3f", self.name(), value)
        wav = self.monodevice.read_attribute("lambda").value
        if wav is not None:
            self.emit('energyChanged', (value,wav))
            
            
    def connectNotify(self, signal):
        #logging.getLogger("HWR").info("%s: BLEnergy.connectNotify, : %s", self.name(), signal)           
        if signal == 'energyChanged':
            self.energyChanged(self.BLEnergydevice.energy)
        if signal == 'stateChanged' :    
            self.stateChanged( str(self.BLEnergydevice.State()) )            
        self.setIsReady(True)
         
    # called by brick : not useful      
    def isSpecConnected(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.isSpecConnected", self.name())
        return True


    def sConnected(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.sConnected", self.name())
        self.deviceOk = True
        self.emit('connected', ())
      
    def sDisconnected(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.sDisconnected", self.name())
        self.deviceOk = False
        self.emit('disconnected', ())

    # Definit si la beamline est a energie fixe ou variable      
    def canMoveEnergy(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.canMoveEnergy", self.name())
        return  True
        
    def getCurrentEnergy(self):
        if self.deviceOk :           
            return self.BLEnergydevice.energy
        else : 
            return None
    
    def getEnergyComputedFromCurrentGap(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.getCurrentEnergy", self.name())
        if self.deviceOk:
            # PL. Rq: if the device is not redy, it send a NaN...
            return self.U20Energydevice.energy
        else : 
            return None
    
    def getCurrentUndulatorGap(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.getCurrentEnergy", self.name())
        if self.deviceOk :           
            return self.U20Energydevice.gap
        else : 
            return None
            
    def getCurrentWavelength(self):
        #logging.getLogger("HWR").debug("%s: BLEnergy.getCurrentWavelength", self.name())
        # Pb with the attribute name "lamdda" which is a keyword for python
        if self.deviceOk :           
            # using calculation of the device mono
            return self.monodevice.read_attribute("lambda").value
        else :
            return None
    
        
    def getEnergyLimits(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.getEnergyLimits", self.name())
        if self.deviceOk :          
            # limits defined in tango 
            enconfig = self.BLEnergydevice.get_attribute_config("energy")
            max = float(enconfig.max_value)
            min = float(enconfig.min_value)
            lims = [min,max]

            logging.getLogger("HWR").info("HOS : energy Limits: %.4f %.4f" % lims)       
            return lims
        else :
            return None
    
    def getWavelengthLimits(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.getWavelengthLimits", self.name())
        if self.deviceOk :
            lims=[]
            # Recuperation des limites en energie
            energylims = self.getEnergyLimits()
            # Conversion de la limite inferieure en wavelength superieure (Utilisation des fonctions de conversion du device mono)
            self.monodevice.simEnergy = energylims[1]
            lims.append(self.monodevice.simLambda)
            # Conversion de la limite superieure en wavelength inferieure (Utilisation des fonctions de conversion du device mono)       
            self.monodevice.simEnergy = energylims[0]
            lims.append(self.monodevice.simLambda)      
    #        logging.getLogger("HWR").info("HOS : wavelength Limits: %.4f %.4f" % lims)       
            logging.getLogger("HWR").info("HOS : wavelength Limits: %s" % lims)       
            return lims   
        else :
            return None    
            
    def startMoveEnergy(self,value):   
        logging.getLogger("HWR").debug("%s: BLEnergy.startMoveEnergy: %.3f", self.name(), value)
    
        # MODIFICATION DE CETTE FONCTION POUR COMPENSER LE PROBLEME D'HYSTERESIS DE L"ONDULEUR
        # PAR CETTE METHODE ON APPLIQUE TOUJOURS UN GAP CROISSANT
        backlash = 0.1 # en mm
        gaplimite = 5.5  # en mm

        if (  str( self.BLEnergydevice.State() ) != "MOVING" and self.deviceOk) :
            if self.doBacklashCompensation :
                try : 
                    # Recuperation de la valeur de gap correspondant a l'energie souhaitee
                    self.U20Energydevice.autoApplyComputedParameters = False
                    self.U20Energydevice.energy = value
                    newgap = self.U20Energydevice.computedGap
                    actualgap = self.U20Energydevice.gap

                    self.U20Energydevice.autoApplyComputedParameters = True
                
                    # On applique le backlash que si on doit descendre en gap	    
                    if newgap < actualgap + backlash:
                        # Envoi a un gap juste en dessous (backlash)    
                        if newgap-backlash > gaplimite :
                            self.U20Energydevice.gap = newgap - backlash
                        else :
                            self.U20Energydevice.gap = gaplimite
                            self.U20Energydevice.gap = newgap + backlash
                        time.sleep(1)
                except :           
                    logging.getLogger("HWR").error("%s: Cannot move undulator U20 : State device = %s", self.name(), str(self.U20Energydevice.State()))

            try :
                # Envoi a l'energie desiree    
                self.BLEnergydevice.energy = value
            except :           
                logging.getLogger("HWR").error("%s: Cannot move BLEnergy : State device = %s", self.name(), str( self.BLEnergydevice.State() ))
        
        else : 
            statusBLEnergydevice = self.BLEnergydevice.Status()
            logging.getLogger("HWR").error("%s: Cannot move : State device = %s", self.name(), str( self.BLEnergydevice.State()))

            for i in statusBLEnergydevice.split("\n") :
                logging.getLogger().error("\t%s\n" % i)
            logging.getLogger().error("\tCheck devices")
    

    def startMoveWavelength(self,value):
        logging.getLogger("HWR").debug("%s: BLEnergy.startMoveWavelength: %.3f", self.name(), value)
        self.monodevice.simLambda = value
        self.startMoveEnergy(self.monodevice.simEnergy)
#        return self.startMoveEnergy(energy_val)
    
    def cancelMoveEnergy(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.cancelMoveEnergy", self.name())
        self.BLEnergydevice.Stop()
        self.moving = False
            
    def energyLimitsChanged(self,limits):
        logging.getLogger("HWR").debug("%s: BLEnergy.energyLimitsChanged: %.3f", self.name(), value)
        self.monodevice.simEnergy = limits[0]
        wav_limits.append[self.monodevice.simLambda]
        self.monodevice.simEnergy = limits[1]
        wav_limits.append[self.monodevice.simLambda]
        self.emit('energyLimitsChanged', (limits,))
        if wav_limits[0]!=None and wav_limits[1]!=None:
            self.emit('wavelengthLimitsChanged', (wav_limits,))
        else:
            self.emit('wavelengthLimitsChanged', (None,))
            
    def moveEnergyCmdReady(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdReady", self.name())
        if not self.moving :
            self.emit('moveEnergyReady', (True,))
            
    def moveEnergyCmdNotReady(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdNotReady", self.name())
        if not self.moving :
            self.emit('moveEnergyReady', (False,))
            
    def moveEnergyCmdStarted(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdStarted", self.name())
        self.moving = True
        self.emit('moveEnergyStarted',(BLEnergy.stateEnergy[str(self.BLEnergydevice.State())]))
        
    def moveEnergyCmdFailed(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdFailed", self.name())
        self.moving = False
        self.emit('moveEnergyFailed', ())
        
    def moveEnergyCmdAborted(self):
        self.moving = False
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdAborted", self.name())
    
    def moveEnergyCmdFinished(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.moveEnergyCmdFinished", self.name())
        self.moving = False
        print 'moveEnergyFinished'
        self.emit('moveEnergyFinished',(BLEnergy.stateEnergy[str(self.BLEnergydevice.State())]))

    def getPreviousResolution(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.getPreviousResolution", self.name())
        return (None, None)
        
    def restoreResolution(self):
        logging.getLogger("HWR").debug("%s: BLEnergy.restoreResolution", self.name())
        return (False,"Resolution motor not defined")
    
    def errorDeviceInstance(self,device) :
        logging.getLogger("HWR").debug("%s: BLEnergy.errorDeviceInstance: %s", self.name(), device)
        db = DeviceProxy("sys/database/dbds1")
        logging.getLogger().error("Check Instance of Device server %s" % db.DbGetDeviceInfo(device)[1][3])
        self.sDisconnected()

#     def energy2wavelength(self,val):
#         try:
#             other_val = 12.39854 / val
#         except ZeroDivisionError:
#             other_val=None
#         return other_val
#     
#     def wavelength2energy(self,val):
#         try:
#             other_val = 12.39854 / val
#         except ZeroDivisionError:
#             other_val=None
#         return other_val
# 
                


#     # Energy scan commands
#     def canScanEnergy(self):
#         logging.getLogger().debug("HOS : passe dans canScanEnergy")
#         return True
#     
#     def cancelEnergyScan(self):
#         logging.getLogger().debug("HOS : passe dans cancelEnergyScan")
#         return True
#     
#     def scanCommandReady(self):
#         logging.getLogger().debug("HOS : passe dans scanCommandReady")
#         if not self.scanning:
#             self.emit('energyScanReady', (True,))
#     
#     def scanCommandNotReady(self):
#         logging.getLogger().debug("HOS : passe dans scanCommandNotReady")      
#         if not self.scanning:
#             self.emit('energyScanReady', (False,))
#     
#     def scanCommandStarted(self):
#         logging.getLogger().debug("HOS : passe dans scanCommandStarted")      
#         self.scanInfo['startTime']=time.strftime("%Y-%m-%d %H:%M:%S")
#         self.scanning = True
#         self.emit('energyScanStarted', ())
#         
#     def scanCommandFailed(self):
#         logging.getLogger().debug("HOS : passe dans scanCommandFailed")      
#         self.scanInfo['endTime']=time.strftime("%Y-%m-%d %H:%M:%S")
#         self.scanning = False
#         self.storeEnergyScan()
#         self.emit('energyScanFailed', ())
#         
#     def scanCommandAborted(self):
#         pass
#     
#     def scanCommandFinished(self,result):
#         logging.getLogger().debug("HOS : passe dans scanCommandFinished")      
#         return
# 
#     def scanStatusChanged(self,status):
#         logging.getLogger().debug("HOS : passe dans scanStatusChanged")      
#         self.emit('scanStatusChanged', (status,))
#     
#     def storeEnergyScan(self):
#         logging.getLogger().debug("HOS : passe dans storeEnergyScan")      
# 
#     def updateEnergyScan(self,scan_id,jpeg_scan_filename):
#         pass
# 
    # Elements commands
#    def getElements(self):
#        elements=[]
#        logging.getLogger().debug("HOS : passe dans getElements")      
#        return elements

    # Mad energies commands
#    def getDefaultMadEnergies(self):
#        energies=[]
#        logging.getLogger().debug("HOS : passe dans getDefaultMadEnergies")      
#        return energies
