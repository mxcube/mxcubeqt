from BlissFramework.BaseComponents import BlissWidget
from qt import *
import logging

__category__ = "mxCuBE"

###
###
###


class InstrumentationMenuBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.mainMenu = None
        self.instrumentationMenu = None
        self.instrumentationMenuId = None

        self.defineSignal("enableAutoStartLoopCentring", ())
        self.defineSignal("toggle_kappa", ())

        # Initialize HO
        self.cryostreamHO = None
        self.fluodetectorHO = None
        self.hutchtriggerHO = None
        self.lightHO = None
        self.scintillatorHO = None
        self.apertureHO = None
        self.fshutHO = None
        self.detcoverHO = None

        self.addProperty("cryostream", "string", "")
        self.addProperty("fluodetector", "string", "")
        self.addProperty("hutchtrigger", "string", "")
        self.addProperty("light", "string", "")
        self.addProperty("DetectorCover", "string", "")
        self.addProperty("FastShutter", "string", "")
        self.addProperty("scintillator", "string", "")
        self.addProperty("scintillatorWarning", "string", "")
        self.addProperty("Kappa on/off", "string", "")
        self.addProperty("aperture", "string", "")
        self.addProperty("apertureWarning", "string", "")
        self.addProperty("menuTitle", "string", "Instrumentation")
        self.addProperty("menuPosition", "integer", 1)
        self.addProperty(
            "hutchtriggerDefaultMode", "combo", ("automatic", "manual"), "automatic"
        )

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def detcoverClicked(self):
        if self.instrumentationMenu.isItemChecked(self.detcoverId):
            self.detcoverHO.actuatorOut()
        else:
            self.detcoverHO.actuatorIn()

    def lightClicked(self):
        if self.instrumentationMenu.isItemChecked(self.lightId):
            self.lightHO.actuatorOut()
        else:
            self.lightHO.actuatorIn()

    def cryostreamClicked(self):
        if self.instrumentationMenu.isItemChecked(self.cryostreamId):
            self.cryostreamHO.actuatorOut()
        else:
            self.cryostreamHO.actuatorIn()

    def fluodetectorClicked(self):
        if self.instrumentationMenu.isItemChecked(self.fluodetectorId):
            self.fluodetectorHO.actuatorOut()
        else:
            self.fluodetectorHO.actuatorIn()

    def scintillatorClicked(self):
        if self.instrumentationMenu.isItemChecked(self.scintillatorId):
            try:
                self.fshutHO.actuatorOut()
            except BaseException:
                pass
            self.scintillatorHO.actuatorOut(timeout=20)
        else:
            msg = self["scintillatorWarning"]
            ret = True
            if len(msg) > 0:
                ret = (
                    QMessageBox.warning(
                        self, "Scintillator in", msg, QMessageBox.Ok, QMessageBox.Cancel
                    )
                    == QMessageBox.Ok
                )
            if ret:
                try:
                    self.detcoverHO.actuatorIn()
                except BaseException:
                    pass
                self.scintillatorHO.actuatorIn(timeout=20)
                """
                try:
                    self.fshutHO.actuatorIn()
                except:
                    pass
                """

    def apertureClicked(self):
        if self.instrumentationMenu.isItemChecked(self.apertureId):
            self.apertureHO.actuatorOut()
        else:
            self.apertureHO.actuatorIn()

    def hutchtriggerClicked(self):
        if self.instrumentationMenu.isItemChecked(self.hutchtriggerId):
            self.instrumentationMenu.setItemChecked(self.hutchtriggerId, False)
        else:
            self.instrumentationMenu.setItemChecked(self.hutchtriggerId, True)

    def detcoverChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.detcoverId, state)

    def lightChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.lightId, state)

    def cryostreamChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.cryostreamId, state)

    def fluodetectorChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.fluodetectorId, state)

    def scintillatorChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.scintillatorId, state)

    def apertureChanged(self, state):
        if self.instrumentationMenu is None:
            return
        if state == "in":
            state = True
        else:
            state = False
        self.instrumentationMenu.setItemChecked(self.apertureId, state)

    def hutchtriggerChanged(self, state):
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
        self.mainMenu = BlissWidget._menuBar

        if self.mainMenu is not None:
            f = self.mainMenu.font()
            f.setPointSize(self.font().pointSize())
            self.mainMenu.setFont(f)

            self.instrumentationMenu = QPopupMenu(self.mainMenu)

            for menu in self.mainMenu.children():
                if isinstance(menu, QPopupMenu):
                    f = menu.font()
                    f.setPointSize(self.font().pointSize())
                    menu.setFont(f)

            self.detcoverId = self.instrumentationMenu.insertItem(
                "Detector Cover", self.detcoverClicked
            )
            if self.detcoverHO is not None:
                self.detcoverChanged(self.detcoverHO.getActuatorState())
            else:
                self.instrumentationMenu.setItemEnabled(self.detcoverId, False)

            self.lightId = self.instrumentationMenu.insertItem(
                "Sample light", self.lightClicked
            )
            if self.lightHO is not None:
                self.lightChanged(self.lightHO.getActuatorState())
            else:
                self.instrumentationMenu.setItemEnabled(self.lightId, False)

            self.cryostreamId = self.instrumentationMenu.insertItem(
                "Cryostream", self.cryostreamClicked
            )
            if self.cryostreamHO is not None:
                self.cryostreamChanged(self.cryostreamHO.getActuatorState())
            else:
                self.instrumentationMenu.setItemEnabled(self.cryostreamId, False)

            self.fluodetectorId = self.instrumentationMenu.insertItem(
                "Fluorescence detector", self.fluodetectorClicked
            )
            if self.fluodetectorHO is not None:
                self.fluodetectorChanged(self.fluodetectorHO.getActuatorState())
            else:
                self.instrumentationMenu.setItemEnabled(self.fluodetectorId, False)

            if self.scintillatorHO is not None:
                self.scintillatorId = self.instrumentationMenu.insertItem(
                    "Scintillator", self.scintillatorClicked
                )
                self.scintillatorChanged(self.scintillatorHO.getActuatorState())

            if self.apertureHO is not None:
                self.apertureId = self.instrumentationMenu.insertItem(
                    "Aperture", self.apertureClicked
                )
                self.apertureChanged(self.apertureHO.getActuatorState())

            self.instrumentationMenu.insertItem("Kappa on/off", self.toggle_kappa)

            self.instrumentationMenu.insertSeparator()

            self.hutchtriggerId = self.instrumentationMenu.insertItem(
                "Automatic hutch trigger", self.hutchtriggerClicked
            )
            if self.hutchtriggerHO is not None:
                if self["hutchtriggerDefaultMode"] == "automatic":
                    self.instrumentationMenu.setItemChecked(self.hutchtriggerId, True)
            else:
                self.instrumentationMenu.setItemEnabled(self.hutchtriggerId, False)

            self.instrumentationMenuId = self.mainMenu.insertItem(
                self["menuTitle"], self.instrumentationMenu, -1, self["menuPosition"]
            )
        else:
            logging.getLogger().debug(
                "InstrumentationMenuBrick: could not find the windows's main menu"
            )

    def hutchtriggerConnected(self):
        if self.instrumentationMenu is None:
            return
        self.instrumentationMenu.setItemEnabled(self.hutchtriggerId, True)

    def hutchtriggerDisconnected(self):
        if self.instrumentationMenu is None:
            return
        self.instrumentationMenu.setItemEnabled(self.hutchtriggerId, False)

    def hutchtriggerMsgChanged(self, msg):
        logging.getLogger().info(msg)

    def instanceModeChanged(self, mode):
        self.mainMenu.setItemEnabled(
            self.instrumentationMenuId, BlissWidget.isInstanceModeMaster()
        )

    # Callback fot the brick's properties
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == "light":
            if newValue:
                if self.lightHO is not None:
                    self.disconnect(
                        self.lightHO, "actuatorStateChanged", self.lightChanged
                    )
                self.lightHO = self.getHardwareObject(newValue)
                if self.lightHO is not None:
                    self.connect(
                        self.lightHO, "actuatorStateChanged", self.lightChanged
                    )

        elif propertyName == "DetectorCover":
            if newValue:
                if self.detcoverHO is not None:
                    self.disconnect(
                        self.detcoverHO, "actuatorStateChanged", self.detcoverChanged
                    )
                self.detcoverHO = self.getHardwareObject(newValue)
                if self.detcoverHO is not None:
                    self.connect(
                        self.detcoverHO, "actuatorStateChanged", self.detcoverChanged
                    )

        elif propertyName == "cryostream":
            if newValue:
                if self.cryostreamHO is not None:
                    self.disconnect(
                        self.cryostreamHO,
                        "actuatorStateChanged",
                        self.cryostreamChanged,
                    )
                self.cryostreamHO = self.getHardwareObject(newValue)
                if self.cryostreamHO is not None:
                    self.connect(
                        self.cryostreamHO,
                        "actuatorStateChanged",
                        self.cryostreamChanged,
                    )

        elif propertyName == "fluodetector":
            if newValue:
                if self.fluodetectorHO is not None:
                    self.disconnect(
                        self.fluodetectorHO,
                        "actuatorStateChanged",
                        self.fluodetectorChanged,
                    )
                self.fluodetectorHO = self.getHardwareObject(newValue)
                if self.fluodetectorHO is not None:
                    self.connect(
                        self.fluodetectorHO,
                        "actuatorStateChanged",
                        self.fluodetectorChanged,
                    )

        elif propertyName == "scintillator":
            if newValue:
                if self.scintillatorHO is not None:
                    self.disconnect(
                        self.scintillatorHO,
                        "actuatorStateChanged",
                        self.scintillatorChanged,
                    )
                self.scintillatorHO = self.getHardwareObject(newValue)
                if self.scintillatorHO is not None:
                    self.connect(
                        self.scintillatorHO,
                        "actuatorStateChanged",
                        self.scintillatorChanged,
                    )

        elif propertyName == "FastShutter":
            if newValue:
                self.fshutHO = self.getHardwareObject(newValue)

        elif propertyName == "aperture":
            if newValue:
                if self.apertureHO is not None:
                    self.disconnect(
                        self.apertureHO, "actuatorStateChanged", self.apertureChanged
                    )
                self.apertureHO = self.getHardwareObject(newValue)
                if self.apertureHO is not None:
                    self.connect(
                        self.apertureHO, "actuatorStateChanged", self.apertureChanged
                    )

        elif propertyName == "hutchtrigger":
            if newValue:
                if self.hutchtriggerHO is not None:
                    self.disconnect(
                        self.hutchtriggerHO, "hutchTrigger", self.hutchtriggerChanged
                    )
                    self.disconnect(
                        self.hutchtriggerHO, "connected", self.hutchtriggerConnected
                    )
                    self.disconnect(
                        self.hutchtriggerHO,
                        "disconnected",
                        self.hutchtriggerDisconnected,
                    )
                    self.disconnect(
                        self.hutchtriggerHO, "msgChanged", self.hutchtriggerMsgChanged
                    )
                self.hutchtriggerHO = self.getHardwareObject(newValue)
                if self.hutchtriggerHO is not None:
                    self.connect(
                        self.hutchtriggerHO, "hutchTrigger", self.hutchtriggerChanged
                    )
                    self.connect(
                        self.hutchtriggerHO, "connected", self.hutchtriggerConnected
                    )
                    self.connect(
                        self.hutchtriggerHO,
                        "disconnected",
                        self.hutchtriggerDisconnected,
                    )
                    self.connect(
                        self.hutchtriggerHO, "msgChanged", self.hutchtriggerMsgChanged
                    )

        else:
            BlissWidget.propertyChanged(self, propertyName, oldValue, newValue)
