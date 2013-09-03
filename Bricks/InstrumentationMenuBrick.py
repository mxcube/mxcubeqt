from BlissFramework.BaseComponents import BlissWidget
from qt import *
import logging

__category__ = 'mxCuBE'

###
### 
###
class InstrumentationMenuBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.mainMenu=None
        self.instrumentationMenu=None
        self.instrumentationMenuId=None

        self.defineSignal("enableAutoStartLoopCentring", ())
        self.defineSignal("toggle_kappa", ())

        # Initialize HO
        self.cryostreamHO=None
        self.fluodetectorHO=None
        self.hutchtriggerHO=None
        self.lightHO=None
        self.scintillatorHO=None
        self.apertureHO=None

        self.addProperty('cryostream','string','')
        self.addProperty('fluodetector','string','')
        self.addProperty('hutchtrigger','string','')
        self.addProperty('light','string','')
        self.addProperty('scintillator','string','')
        self.addProperty('Kappa on/off','string', '')
        self.addProperty('aperture','string','')
        self.addProperty('menuTitle','string','Instrumentation')
        self.addProperty('menuPosition','integer',1)
        self.addProperty('hutchtriggerDefaultMode', 'combo', ('automatic', 'manual'), 'automatic')
        self.addProperty('scintillatorWarning', 'string', '')
        self.addProperty('apertureWarning', 'string', '')

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

    def lightClicked(self):
        if self.instrumentationMenu.isItemChecked(self.lightId):
            self.lightHO.wagoOut()
        else:
            self.lightHO.wagoIn()

    def cryostreamClicked(self):
        if self.instrumentationMenu.isItemChecked(self.cryostreamId):
            self.cryostreamHO.wagoOut()
        else:
            self.cryostreamHO.wagoIn()

    def fluodetectorClicked(self):
        if self.instrumentationMenu.isItemChecked(self.fluodetectorId):
            self.fluodetectorHO.wagoOut()
        else:
            self.fluodetectorHO.wagoIn()

    def scintillatorClicked(self):
        if self.instrumentationMenu.isItemChecked(self.scintillatorId):
            self.scintillatorHO.wagoOut()
        else:
            msg = self["scintillatorWarning"]
            ret=True
            if len(msg) > 0:
              ret=QMessageBox.warning(self, 'Scintillator in', msg, QMessageBox.Ok, QMessageBox.Cancel)==QMessageBox.Ok
            if ret:
              self.scintillatorHO.wagoIn()

    def apertureClicked(self):
        if self.instrumentationMenu.isItemChecked(self.apertureId):
            self.apertureHO.wagoOut()
        else:
            self.apertureHO.wagoIn()

    def hutchtriggerClicked(self):
        if self.instrumentationMenu.isItemChecked(self.hutchtriggerId):
            self.instrumentationMenu.setItemChecked(self.hutchtriggerId,False)
        else:
            self.instrumentationMenu.setItemChecked(self.hutchtriggerId,True)

    def lightChanged(self,state):
        if self.instrumentationMenu is None:
            return
        if state=="in":
            state=True
        else:
            state=False
        self.instrumentationMenu.setItemChecked(self.lightId,state)

    def cryostreamChanged(self,state):
        if self.instrumentationMenu is None:
            return
        if state=="in":
            state=True
        else:
            state=False
        self.instrumentationMenu.setItemChecked(self.cryostreamId,state)

    def fluodetectorChanged(self,state):
        if self.instrumentationMenu is None:
            return
        if state=="in":
            state=True
        else:
            state=False
        self.instrumentationMenu.setItemChecked(self.fluodetectorId,state)

    def scintillatorChanged(self,state):
        if self.instrumentationMenu is None:
            return
        if state=="in":
            state=True
        else:
            state=False
        self.instrumentationMenu.setItemChecked(self.scintillatorId,state)

    def apertureChanged(self,state):
        if self.instrumentationMenu is None:
            return
        if state=="in":
            state=True
        else:
            state=False
        self.instrumentationMenu.setItemChecked(self.apertureId,state)

    def hutchtriggerChanged(self,state):
        if not BlissWidget.isInstanceRoleServer():
            # do not allow hutch trigger to be started when not in server mode
            return

        if self.instrumentationMenu.isItemChecked(self.hutchtriggerId):
            if state:
                self.hutchtriggerHO.macro(1)
            else:
                self.hutchtriggerHO.macro(0)

    def toggle_kappa(self):
        self.emit(PYSIGNAL("toggle_kappa"), (None,))

    def run(self):
        self.mainMenu=BlissWidget._menuBar

        if self.mainMenu is not None:
            f=self.mainMenu.font()
            f.setPointSize(self.font().pointSize())
            self.mainMenu.setFont(f)

            self.instrumentationMenu = QPopupMenu(self.mainMenu)

            for menu in self.mainMenu.children():
                if isinstance(menu,QPopupMenu):
                    f=menu.font()
                    f.setPointSize(self.font().pointSize())
                    menu.setFont(f)

            self.lightId=self.instrumentationMenu.insertItem("Sample light",self.lightClicked)
            if self.lightHO is not None:
                self.lightChanged(self.lightHO.getWagoState())
            else:
                self.instrumentationMenu.setItemEnabled(self.lightId,False)

            self.cryostreamId=self.instrumentationMenu.insertItem("Cryostream",self.cryostreamClicked)
            if self.cryostreamHO is not None:
                self.cryostreamChanged(self.cryostreamHO.getWagoState())
            else:
                self.instrumentationMenu.setItemEnabled(self.cryostreamId,False)

            self.fluodetectorId=self.instrumentationMenu.insertItem("Fluorescence detector",self.fluodetectorClicked)
            if self.fluodetectorHO is not None:
                self.fluodetectorChanged(self.fluodetectorHO.getWagoState())
            else:
                self.instrumentationMenu.setItemEnabled(self.fluodetectorId,False)

            if self.scintillatorHO is not None:
                self.scintillatorId=self.instrumentationMenu.insertItem("Scintillator",self.scintillatorClicked)
                self.scintillatorChanged(self.scintillatorHO.getWagoState())

            if self.apertureHO is not None:
                self.apertureId=self.instrumentationMenu.insertItem("Aperture",self.apertureClicked)
                self.apertureChanged(self.apertureHO.getWagoState())

            self.instrumentationMenu.insertItem("Kappa on/off", self.toggle_kappa)

            self.instrumentationMenu.insertSeparator()

            self.hutchtriggerId=self.instrumentationMenu.insertItem("Automatic hutch trigger",self.hutchtriggerClicked)
            if self.hutchtriggerHO is not None:
                if self['hutchtriggerDefaultMode']=="automatic":
                    self.instrumentationMenu.setItemChecked(self.hutchtriggerId,True)
            else:
                self.instrumentationMenu.setItemEnabled(self.hutchtriggerId,False)

            self.instrumentationMenuId=self.mainMenu.insertItem(self['menuTitle'],self.instrumentationMenu,-1,self['menuPosition'])
        else:
            logging.getLogger().debug("InstrumentationMenuBrick: could not find the windows's main menu")

    def hutchtriggerConnected(self):
        if self.instrumentationMenu is None:
            return
        self.instrumentationMenu.setItemEnabled(self.hutchtriggerId,True)

    def hutchtriggerDisconnected(self):
        if self.instrumentationMenu is None:
            return
        self.instrumentationMenu.setItemEnabled(self.hutchtriggerId,False)

    def hutchtriggerMsgChanged(self,msg):
        logging.getLogger().info(msg)

    def instanceModeChanged(self,mode):
        self.mainMenu.setItemEnabled(self.instrumentationMenuId,BlissWidget.isInstanceModeMaster())

    # Callback fot the brick's properties
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='light':
            if self.lightHO is not None:
                self.disconnect(self.lightHO,'wagoStateChanged',self.lightChanged)
            self.lightHO=self.getHardwareObject(newValue)
            if self.lightHO is not None:
                self.connect(self.lightHO,'wagoStateChanged',self.lightChanged)

        elif propertyName=='cryostream':
            if self.cryostreamHO is not None:
                self.disconnect(self.cryostreamHO,'wagoStateChanged',self.cryostreamChanged)
            self.cryostreamHO=self.getHardwareObject(newValue)
            if self.cryostreamHO is not None:
                self.connect(self.cryostreamHO,'wagoStateChanged',self.cryostreamChanged)

        elif propertyName=='fluodetector':
            if self.fluodetectorHO is not None:
                self.disconnect(self.fluodetectorHO,'wagoStateChanged',self.fluodetectorChanged)
            self.fluodetectorHO=self.getHardwareObject(newValue)
            if self.fluodetectorHO is not None:
                self.connect(self.fluodetectorHO,'wagoStateChanged',self.fluodetectorChanged)

        elif propertyName=='scintillator':
            if self.scintillatorHO is not None:
                self.disconnect(self.scintillatorHO,'wagoStateChanged',self.scintillatorChanged)
            self.scintillatorHO=self.getHardwareObject(newValue)
            if self.scintillatorHO is not None:
                self.connect(self.scintillatorHO,'wagoStateChanged',self.scintillatorChanged)

        elif propertyName=='aperture':
            if self.apertureHO is not None:
                self.disconnect(self.apertureHO,'wagoStateChanged',self.apertureChanged)
            self.apertureHO=self.getHardwareObject(newValue)
            if self.apertureHO is not None:
                self.connect(self.apertureHO,'wagoStateChanged',self.apertureChanged)

        elif propertyName=='hutchtrigger':
            if self.hutchtriggerHO is not None:
                self.disconnect(self.hutchtriggerHO,'hutchTrigger',self.hutchtriggerChanged)
                self.disconnect(self.hutchtriggerHO,'connected',self.hutchtriggerConnected)
                self.disconnect(self.hutchtriggerHO,'disconnected',self.hutchtriggerDisconnected)
                self.disconnect(self.hutchtriggerHO,'msgChanged',self.hutchtriggerMsgChanged)
            self.hutchtriggerHO=self.getHardwareObject(newValue)
            if self.hutchtriggerHO is not None:
                self.connect(self.hutchtriggerHO,'hutchTrigger',self.hutchtriggerChanged)
                self.connect(self.hutchtriggerHO,'connected',self.hutchtriggerConnected)
                self.connect(self.hutchtriggerHO,'disconnected',self.hutchtriggerDisconnected)
                self.connect(self.hutchtriggerHO,'msgChanged',self.hutchtriggerMsgChanged)

        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
