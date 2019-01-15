import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Utils import widget_colors

__category__ = "mxCuBE"


class EnergyBrick(BlissWidget):
    STATE_COLORS = {
        "error": widget_colors.LIGHT_RED,
        "moving": widget_colors.LIGHT_YELLOW,
        "ready": widget_colors.LIGHT_GREEN,
        "changed": QColor(255, 165, 0),
        "outlimits": widget_colors.LIGHT_RED,
    }

    MAX_HISTORY = 20

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.energy = None
        self.colorGroupDict = {}
        self.originalBackgroundColor = None

        self.energyLimits = None
        self.wavelengthLimits = None

        self.currentEnergyValue = None
        self.currentWavelengthValue = None

        self.addProperty("mnemonic", "string", "")
        self.addProperty("icons", "string", "")
        self.addProperty("defaultMode", "combo", ("keV", "Ang"), "keV")
        self.addProperty("kevFormatString", "formatString", "###.####")
        self.addProperty("angFormatString", "formatString", "##.###")
        self.addProperty("angResFormatString", "formatString", "##.###")
        self.addProperty("startupEnable", "boolean", False)
        self.addProperty("alwaysReadonly", "boolean", False)

        self.defineSignal("energyConnected", ())

        self.defineSlot("setEnabled", ())
        self.defineSlot("energyRequest", ())

        self.topBox = QVGroupBox("Energy", self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.paramsBox = QWidget(self.topBox)
        QGridLayout(self.paramsBox, 2, 5, 0, 2)
        self.paramsBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        label1 = QLabel("Current:", self.paramsBox)
        self.paramsBox.layout().addWidget(label1, 0, 0)

        box1 = QVBox(self.paramsBox)
        self.currentEnergy = QLineEdit(box1)
        self.currentEnergy.setReadOnly(True)
        # self.currentEnergy.setAlignment(QWidget.AlignRight)
        # self.currentEnergy.setFixedWidth(60)
        self.currentWavelength = QLineEdit(box1)
        self.currentWavelength.setReadOnly(True)
        # self.currentWavelength.setAlignment(QWidget.AlignRight)
        # self.currentWavelength.setFixedWidth(90)
        self.paramsBox.layout().addMultiCellWidget(box1, 0, 0, 1, 3)

        label2 = QLabel("Move to:", self.paramsBox)
        self.paramsBox.layout().addWidget(label2, 1, 0)

        self.newValue = QLineEdit(self.paramsBox)
        self.newValue.setFixedWidth(50)
        self.paramsBox.layout().addWidget(self.newValue, 1, 1)
        self.newValue.setValidator(QDoubleValidator(self))
        self.newValue.setAlignment(QWidget.AlignRight)
        pol = self.newValue.sizePolicy()
        pol.setVerData(QSizePolicy.MinimumExpanding)
        self.newValue.setSizePolicy(pol)
        QObject.connect(
            self.newValue, SIGNAL("returnPressed()"), self.changeCurrentValue
        )
        QObject.connect(
            self.newValue,
            SIGNAL("textChanged(const QString &)"),
            self.inputFieldChanged,
        )
        self.newValue.createPopupMenu = self.openHistoryMenu

        self.units = QComboBox(self.paramsBox)
        self.units.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.paramsBox.layout().addWidget(self.units, 1, 2)
        QObject.connect(
            self.units, SIGNAL("activated(const QString &)"), self.unitChanged
        )

        self.instanceSynchronize("topBox", "newValue", "units")

        box2 = QHBox(self.paramsBox)
        box2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        # self.applyButton=QPushButton("+",box2)
        # QObject.connect(self.applyButton,SIGNAL('clicked()'),self.changeCurrentValue)
        self.stopButton = QPushButton("*", box2)
        self.stopButton.setEnabled(False)
        QObject.connect(self.stopButton, SIGNAL("clicked()"), self.stopClicked)
        # HorizontalSpacer(box2)
        self.paramsBox.layout().addWidget(box2, 1, 3)

        # self.applyButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        self.stopButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

        self.staticBox = QWidget(self.topBox)
        QGridLayout(self.staticBox, 2, 2, 0, 2)
        label3 = QLabel("Energy:", self.staticBox)
        self.staticBox.layout().addWidget(label3, 0, 0)

        self.staticEnergy = QLineEdit(self.staticBox)
        f = self.staticEnergy.font()
        # f.setBold(True)
        self.staticEnergy.setFont(f)
        self.staticBox.layout().addWidget(self.staticEnergy, 0, 1)

        label4 = QLabel("Wavelength:", self.staticBox)
        self.staticBox.layout().addWidget(label4, 1, 0)

        self.staticWavelength = QLineEdit(self.staticBox)
        self.staticBox.layout().addWidget(self.staticWavelength, 1, 1)

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == "mnemonic":
            if self.energy is not None:
                self.disconnect(
                    self.energy, PYSIGNAL("energyChanged"), self.energyChanged
                )
                self.disconnect(self.energy, PYSIGNAL("connected"), self.connected)
                self.disconnect(
                    self.energy, PYSIGNAL("disconnected"), self.disconnected
                )
                self.disconnect(
                    self.energy, PYSIGNAL("moveEnergyStarted"), self.changeEnergyStarted
                )
                self.disconnect(
                    self.energy, PYSIGNAL("moveEnergyFailed"), self.changeEnergyFailed
                )
                self.disconnect(
                    self.energy, PYSIGNAL("moveEnergyFinished"), self.changeEnergyOk
                )
                self.disconnect(
                    self.energy, PYSIGNAL("moveEnergyReady"), self.changeEnergyReady
                )
                self.disconnect(
                    self.energy,
                    PYSIGNAL("energyLimitsChanged"),
                    self.energyLimitsChanged,
                )
                self.disconnect(
                    self.energy,
                    PYSIGNAL("wavelengthLimitsChanged"),
                    self.wavelengthLimitsChanged,
                )

            self.units.clear()
            self.kevHistory = []
            self.angHistory = []
            self.energy = self.getHardwareObject(newValue)
            if self.energy is not None:
                self.units.insertItem("keV")
                self.units.insertItem(chr(197))
                def_mode = self["defaultMode"]
                if def_mode == "Ang":
                    def_mode = chr(197)
                self.units.setCurrentText(def_mode)
                self.unitChanged(def_mode)

                self.connect(self.energy, PYSIGNAL("energyChanged"), self.energyChanged)
                self.connect(self.energy, PYSIGNAL("connected"), self.connected)
                self.connect(self.energy, PYSIGNAL("disconnected"), self.disconnected)
                self.connect(
                    self.energy, PYSIGNAL("moveEnergyStarted"), self.changeEnergyStarted
                )
                self.connect(
                    self.energy, PYSIGNAL("moveEnergyFailed"), self.changeEnergyFailed
                )
                self.connect(
                    self.energy, PYSIGNAL("moveEnergyFinished"), self.changeEnergyOk
                )
                self.connect(
                    self.energy, PYSIGNAL("moveEnergyReady"), self.changeEnergyReady
                )
                self.connect(
                    self.energy,
                    PYSIGNAL("energyLimitsChanged"),
                    self.energyLimitsChanged,
                )
                self.connect(
                    self.energy,
                    PYSIGNAL("wavelengthLimitsChanged"),
                    self.wavelengthLimitsChanged,
                )

                if self.energy.isConnected():
                    self.connected()
                else:
                    self.disconnected()
            else:
                self.updateGUI()

        elif propertyName == "icons":
            icons_list = newValue.split()

            # try:
            #    self.applyButton.setPixmap(Icons.load(icons_list[0]))
            # except IndexError:
            #    pass

            try:
                self.stopButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass

        elif propertyName == "alwaysReadonly":
            pass
        else:
            BlissWidget.propertyChanged(self, propertyName, oldValue, newValue)

    def inputFieldChanged(self, text):
        text = str(text)
        if text == "":
            self.setWidgetColor("ready")
        else:
            try:
                val = float(text)
            except (ValueError, TypeError):
                widget_color = "outlimits"
            else:
                unit = self.units.currentText()
                limits = None
                if unit == "keV":
                    limits = self.energyLimits
                elif unit == chr(197):
                    limits = self.wavelengthLimits

                widget_color = "changed"
                if limits is not None:
                    if val < limits[0] or val > limits[1]:
                        widget_color = "outlimits"

            self.setWidgetColor(widget_color)

    def updateGUI(self, connected=None):
        # print "EnergyBrick.updateGUI",connected
        if self.energy is None:
            connected = False
        elif connected is None:
            connected = self.energy.isConnected()

        if connected:
            curr_energy = self.energy.getCurrentEnergy()
            curr_wavelength = self.energy.getCurrentWavelength()
            if curr_energy is None or curr_wavelength is None:
                connected = False

        if connected:
            self.topBox.setEnabled(True)
            self.setWidgetColor("ready")
            if self.energy.canMoveEnergy() and not self["alwaysReadonly"]:
                self.energyLimits = self.energy.getEnergyLimits()
                self.wavelengthLimits = self.energy.getWavelengthLimits()
                self.staticBox.hide()
                self.paramsBox.show()
                # unit=str(self.units.currentText())
                unit = self.units.currentText()
                if unit == "keV":
                    self.topBox.setTitle("Energy")
                elif unit == chr(197):
                    self.topBox.setTitle("Wavelength")
                self.topBox.setCheckable(True)
                self.topBox.setChecked(self["startupEnable"])
            else:
                self.energyLimits = None
                self.wavelengthLimits = None
                self.paramsBox.hide()
                self.staticBox.show()
                self.topBox.setTitle("Energy")
                self.topBox.setCheckable(False)
                self.staticEnergy.setText(str(curr_energy))
                self.staticWavelength.setText(str(curr_wavelength))
                self.staticEnergy.setReadOnly(True)
                self.staticWavelength.setReadOnly(True)
            self.energyChanged(curr_energy, curr_wavelength)
        else:
            self.topBox.setEnabled(False)
            self.setWidgetColor("error")
            self.paramsBox.hide()
            self.staticBox.show()
            self.topBox.setTitle("Energy")
            self.topBox.setCheckable(False)
            self.staticEnergy.setReadOnly(True)
            self.staticWavelength.setReadOnly(True)

    def connected(self):
        # print "EnergyBrick.connected"
        self.updateGUI(connected=True)
        move = self.energy.canMoveEnergy() and not self["alwaysReadonly"]
        self.emit(PYSIGNAL("energyConnected"), (True, move))

    def disconnected(self):
        # print "EnergyBrick.disconnected"
        self.updateGUI(connected=False)
        self.emit(PYSIGNAL("energyConnected"), (False,))

    def energyRequest(self, param_dict):
        unit = self.units.currentText()
        try:
            val = float(str(self.newValue.text()))
        except (ValueError, TypeError):
            pass
        else:
            if unit == chr(197):
                if self.wavelengthLimits is not None:
                    if (
                        val >= self.wavelengthLimits[0]
                        and val <= self.wavelengthLimits[1]
                    ):
                        param_dict["wavelength"] = val
                else:
                    param_dict["wavelength"] = val
            elif unit == "keV":
                if self.energyLimits is not None:
                    if val >= self.energyLimits[0] and val <= self.energyLimits[1]:
                        param_dict["energy"] = val
                else:
                    param_dict["energy"] = val

        try:
            curr_energy = float(self.currentEnergyValue)
        except (ValueError, TypeError, IndexError):
            pass
        else:
            if self.staticBox.isShown():
                param_dict["fixed_energy"] = curr_energy
            else:
                param_dict["current_energy"] = curr_energy
        try:
            curr_wavelength = float(self.currentWavelengthValue)
        except (ValueError, TypeError, IndexError):
            pass
        else:
            if self.staticBox.isShown():
                param_dict["fixed_wavelength"] = curr_wavelength
            else:
                param_dict["current_wavelength"] = curr_wavelength

    def run(self):
        if self.energy is None:
            connected = False
        else:
            connected = self.energy.isConnected()
        if connected:
            curr_energy = self.energy.getCurrentEnergy()
            curr_wavelength = self.energy.getCurrentWavelength()
            if curr_energy is None or curr_wavelength is None:
                connected = False

        move = None
        if connected:
            move = self.energy.canMoveEnergy() and not self["alwaysReadonly"]
        self.emit(PYSIGNAL("energyConnected"), (connected, move))

    def setWidgetColor(self, state=None):
        color = EnergyBrick.STATE_COLORS[state]
        self.newValue.setPaletteBackgroundColor(color)

        if state == "ready":
            if self.originalBackgroundColor is None:
                self.originalBackgroundColor = self.paletteBackgroundColor()
            color = self.originalBackgroundColor

        w_palette = self.newValue.palette()
        try:
            cg = self.colorGroupDict[state]
        except KeyError:
            cg = QColorGroup(w_palette.disabled())
            cg.setColor(cg.Background, color)
            self.colorGroupDict[state] = cg
        w_palette.setDisabled(cg)

    def unitChanged(self, unit):
        f_kev = self.currentEnergy.font()
        f_ang = self.currentWavelength.font()
        if unit == chr(197):
            # f_kev.setBold(False)
            # f_ang.setBold(True)
            self.topBox.setTitle("Wavelength")
        elif unit == "keV":
            # f_kev.setBold(True)
            # f_ang.setBold(False)
            self.topBox.setTitle("Energy")
        self.currentEnergy.setFont(f_kev)
        self.currentWavelength.setFont(f_ang)
        # self.newValue.blockSignals(True)
        self.newValue.setText("")
        # self.newValue.blockSignals(False)
        self.setWidgetColor("ready")

    def setEnergy(self, kev):
        if self.energyLimits is not None:
            if kev < self.energyLimits[0] or kev > self.energyLimits[1]:
                return
        self.energy.startMoveEnergy(kev, wait=False)
        # self.applyButton.setEnabled(False)
        self.newValue.setEnabled(False)
        self.units.setEnabled(False)

    def setWavelength(self, ang):
        if self.wavelengthLimits is not None:
            if ang < self.wavelengthLimits[0] or ang > self.wavelengthLimits[1]:
                return
        self.energy.startMoveWavelength(ang, wait=False)
        # self.applyButton.setEnabled(False)
        self.newValue.setEnabled(False)
        self.units.setEnabled(False)

    def changeCurrentValue(self):
        unit = self.units.currentText()
        try:
            val = float(str(self.newValue.text()))
        except (ValueError, TypeError):
            return
        if unit == chr(197):
            self.setWavelength(val)
        elif unit == "keV":
            self.setEnergy(val)

    def changeEnergyReady(self, state):
        self.newValue.setEnabled(state)
        # self.applyButton.setEnabled(state)

    def changeEnergyStarted(self):
        self.stopButton.setEnabled(True)
        self.setWidgetColor("moving")

    def changeEnergyOk(self):
        self.stopButton.setEnabled(False)
        # self.newValue.blockSignals(True)
        self.newValue.setText("")
        # self.newValue.blockSignals(False)
        self.newValue.setEnabled(True)
        self.units.setEnabled(True)
        # self.applyButton.setEnabled(True)
        self.setWidgetColor("ready")

        """
        prev_res=self.energy.getPreviousResolution()
        logging.getLogger().info("%s", prev_res)
        if prev_res[0]!=None and prev_res[1]!=None:
            prev_res_str=self['angResFormatString'] % prev_res[0]
            curr_res_str=self['angResFormatString'] % prev_res[1]

            if prev_res_str!=curr_res_str:
                mov_resol=QMessageBox.question(self,"Energy change",\
                    "Resolution has changed (was %s %s, now is %s %s)!" % (prev_res_str,chr(197),curr_res_str,chr(197)),\
                    "Move back to %s %s" % (prev_res_str,chr(197)), "Keep it at %s %s" % (curr_res_str,chr(197)))
                if mov_resol==0:
                    mov_res=self.energy.restoreResolution()
                    if not mov_res[0]:
                        logging.getLogger().warning('EnergyBrick: problems restoring resolution (%s)' % mov_res[1].lower())
        """

    def changeEnergyFailed(self):
        self.stopButton.setEnabled(False)
        # self.newValue.blockSignals(True)
        self.newValue.setText("")
        # self.newValue.blockSignals(False)
        self.newValue.setEnabled(True)
        self.units.setEnabled(True)
        # self.applyButton.setEnabled(True)
        self.setWidgetColor("error")

    def stopClicked(self):
        self.stopButton.setEnabled(False)
        self.energy.cancelMoveEnergy()

    def energyChanged(self, energy, wavelength):
        self.currentEnergyValue = self["kevFormatString"] % energy
        self.currentWavelengthValue = self["angFormatString"] % wavelength

        energy_str = self["kevFormatString"] % energy
        wavelength_str = self["angFormatString"] % wavelength

        self.staticEnergy.setText("%s keV" % energy_str)
        self.staticWavelength.setText("%s %s" % (wavelength_str, chr(197)))
        self.currentEnergy.setText("%s keV" % energy_str)
        self.currentWavelength.setText("%s %s" % (wavelength_str, chr(197)))

        self.updateKevHistory(energy_str)
        self.updateAngHistory(wavelength_str)

    def energyLimitsChanged(self, limits):
        self.energyLimits = limits

    def wavelengthLimitsChanged(self, limits):
        self.wavelengthLimits = limits

    def openHistoryMenu(self):
        unit = self.units.currentText()
        history = None
        if unit == chr(197):
            title = "Wavelength"
            history = self.angHistory
            sig = self.goToAngHistory
        elif unit == "keV":
            title = "Energy"
            history = self.kevHistory
            sig = self.goToKevHistory

        if history is not None:
            menu = QPopupMenu(self)
            menu.insertItem(QLabel("<nobr><b>%s history</b></nobr>" % title, menu))
            menu.insertSeparator()
            for i in range(len(history)):
                menu.insertItem(history[i], i)
            QObject.connect(menu, SIGNAL("activated(int)"), sig)
            return menu

    def updateAngHistory(self, ang):
        ang = str(ang)
        if ang not in self.angHistory:
            if len(self.angHistory) == EnergyBrick.MAX_HISTORY:
                del self.angHistory[-1]
            self.angHistory.insert(0, ang)

    def updateKevHistory(self, kev):
        kev = str(kev)
        if kev not in self.kevHistory:
            if len(self.kevHistory) == EnergyBrick.MAX_HISTORY:
                del self.kevHistory[-1]
            self.kevHistory.insert(0, kev)

    def goToKevHistory(self, idx):
        kev = float(self.kevHistory[idx])
        self.setEnergy(kev)

    def goToAngHistory(self, idx):
        ang = float(self.angHistory[idx])
        self.setWavelength(ang)


###
# Auxiliary class for positioning
###


class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)


class MenuButton(QToolButton):
    def __init__(self, parent, caption):
        QToolButton.__init__(self, parent)

        self.executing = None
        self.runIcon = None
        self.stopIcon = None

        self.setUsesTextLabel(True)
        self.setTextLabel(caption)

        QObject.connect(self, SIGNAL("clicked()"), self.buttonClicked)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setIcons(self, icon_run, icon_stop=None):
        self.runIcon = Icons.load(icon_run)
        if icon_stop is not None:
            self.stopIcon = Icons.load(icon_stop)

        if self.executing and icon_stop is not None:
            self.setPixmap(self.stopIcon)
        else:
            self.setPixmap(self.runIcon)

    def buttonClicked(self):
        if self.executing:
            self.setEnabled(False)
            self.emit(PYSIGNAL("cancelCommand"), ())
        else:
            self.setEnabled(False)
            self.emit(PYSIGNAL("executeCommand"), ())

    def commandStarted(self):
        self.executing = True
        if self.stopIcon is not None:
            self.setPixmap(self.stopIcon)
        self.setEnabled(True)

    def commandDone(self):
        self.executing = False
        if self.runIcon is not None:
            self.setPixmap(self.runIcon)
        self.setEnabled(True)

    def commandFailed(self):
        self.commandDone()

    def cancelCancel(self):
        self.setEnabled(True)


class myLineEdit(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        palette = self.palette()
        # self.originalCG=QColorGroup(palette.disabled())
        # self.disabledCG=QColorGroup(palette.disabled())
        # self.disabledCG.setColor(QColorGroup.Text,QWidget.black)

        # palette.setDisabled(self.disabledCG)
        # self.originalCG.setColor(QColorGroup.Background,QWidget.red)


#    def setDisabledLook(self,state):
#        palette=self.palette()
#        if state:
#            palette.setDisabled(self.originalCG)
#        else:
#            palette.setDisabled(self.disabledCG)
