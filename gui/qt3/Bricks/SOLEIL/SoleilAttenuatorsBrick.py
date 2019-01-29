"""
[Name] SoleilAttenuatorsBrick

[Description]

The Attenuators brick allows user to read and set the transmission,
thus moving attenuators through the Ps_attenuator hardware object
(attenuation by slits)

[Properties]

-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| mnemonic     | string | name of the Attenuators Hardware Object
| formatString | string | format string for transmission display (defaults to ###.##)
-----------------------------------------------------------------------

[Signals]

[Slots]

-------------------------------------------------------------------
| name                | arguments                  | description
-------------------------------------------------------------------
| setEnabled          |                            | enables the brick
| transmissionRequest | transmission (dict) | used to set the transmission from another brick
-------------------------------------------------------------------
[Comments]

[HardwareObjects]

Known compatible hardware objects are:
- :hw:Ps_attenuatorPX1

Compatible Hardware Objects should implements the following
methods :

- isReady()
- getAttFactor()
- getAttState()
- toggle(filter_index)
- setTransmission(transmission_percent)

Compatible Hardware Objects should also emit these signals :
- deviceReady
- deviceNotReady
- attStateChanged
- attFactorChanged

Example Hardware Object XML file :
==================================

<device class = "Ps_attenuatorPX1">
  <username>Attenuators by Primary slits</username>
  <tangoname>i10-c-c00/ex/fp_parser</tangoname>
  <channel type="tango" polling="1000" name="TrueTrans_FP">TrueTrans_FP</channel>
  <channel type="tango" polling="1000" name="State">State</channel>
  <interval>1000</interval>
</device>

"""
import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
from BlissFramework.Utils import widget_colors

__category__ = "SOLEIL"


class SoleilAttenuatorsBrick(BlissWidget):
    CONNECTED_COLOR = widget_colors.LIGHT_GREEN
    CHANGED_COLOR = QColor(255, 165, 0)
    OUTLIMITS_COLOR = widget_colors.LIGHT_RED

    MAX_HISTORY = 20

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.addProperty("icons", "string", "")
        self.addProperty("formatString", "formatString", "###.##")

        self.defineSlot("setEnabled", ())
        self.defineSlot("transmissionRequest", ())

        self.attenuators = None
        self.transmissionLimits = None

        self.currentTransmissionValue = None

        self.topBox = QHGroupBox("Transmission", self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.paramsBox = QWidget(self.topBox)
        QGridLayout(self.paramsBox, 2, 3, 0, 2)

        label1 = QLabel("Current:", self.paramsBox)
        self.paramsBox.layout().addWidget(label1, 0, 0)

        self.currentTransmission = QLineEdit(self.paramsBox)
        self.currentTransmission.setReadOnly(True)
        self.currentTransmission.setFixedWidth(75)

        self.paramsBox.layout().addWidget(self.currentTransmission, 0, 1)

        label2 = QLabel("Set to:", self.paramsBox)
        self.paramsBox.layout().addWidget(label2, 1, 0)

        self.newTransmission = QLineEdit(self.paramsBox)
        self.newTransmission.setAlignment(QWidget.AlignRight)
        self.paramsBox.layout().addWidget(self.newTransmission, 1, 1)
        self.newTransmission.setFixedWidth(75)
        self.newTransmission.setValidator(QDoubleValidator(self))
        self.newTransmission.setPaletteBackgroundColor(self.CONNECTED_COLOR)
        QObject.connect(
            self.newTransmission,
            SIGNAL("returnPressed()"),
            self.changeCurrentTransmission,
        )
        QObject.connect(
            self.newTransmission,
            SIGNAL("textChanged(const QString &)"),
            self.inputFieldChanged,
        )
        self.newTransmission.createPopupMenu = self.openHistoryMenu

        self.instanceSynchronize("newTransmission")

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    def propertyChanged(self, property, oldValue, newValue):
        if property == "mnemonic":
            if self.attenuators is not None:
                self.disconnect(
                    self.attenuators, PYSIGNAL("deviceReady"), self.connected
                )
                self.disconnect(
                    self.attenuators, PYSIGNAL("deviceNotReady"), self.disconnected
                )
                self.disconnect(
                    self.attenuators, PYSIGNAL("attStateChanged"), self.attStateChanged
                )
                self.disconnect(
                    self.attenuators,
                    PYSIGNAL("attFactorChanged"),
                    self.attFactorChanged,
                )

            self.transHistory = []

            self.attenuators = self.getHardwareObject(newValue)
            if self.attenuators is not None:

                self.connect(self.attenuators, PYSIGNAL("deviceReady"), self.connected)
                self.connect(
                    self.attenuators, PYSIGNAL("deviceNotReady"), self.disconnected
                )
                self.connect(
                    self.attenuators, PYSIGNAL("attStateChanged"), self.attStateChanged
                )
                self.connect(
                    self.attenuators,
                    PYSIGNAL("attFactorChanged"),
                    self.attFactorChanged,
                )

                if self.attenuators.isReady():
                    self.connected()
                    self.attFactorChanged(self.attenuators.getAttFactor())
                    self.attStateChanged(self.attenuators.getAttState())
                else:
                    self.disconnected()
            else:
                self.disconnected()

        elif property == "icons":
            icons_list = newValue.split()
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)

    def inputFieldChanged(self, text):
        text = str(text)
        if text == "":
            self.newTransmission.setPaletteBackgroundColor(self.CONNECTED_COLOR)
        else:
            try:
                val = float(text)
            except (TypeError, ValueError):
                widget_color = self.OUTLIMITS_COLOR
            else:
                widget_color = self.CHANGED_COLOR
                if self.transmissionLimits is not None:
                    if (
                        val < self.transmissionLimits[0]
                        or val > self.transmissionLimits[1]
                    ):
                        widget_color = self.OUTLIMITS_COLOR

            self.newTransmission.setPaletteBackgroundColor(widget_color)

    def transmissionRequest(self, param_dict):
        try:
            val = float(str(self.newTransmission.text()))
        except (ValueError, TypeError):
            pass
        else:
            if self.transmissionLimits is not None:
                if (
                    val >= self.transmissionLimits[0]
                    and val <= self.transmissionLimits[1]
                ):
                    param_dict["transmission"] = val
            else:
                param_dict["transmission"] = val

        try:
            curr_transmission = float(self.currentTransmissionValue)
        except (ValueError, TypeError, IndexError):
            pass
        else:
            param_dict["current_transmission"] = curr_transmission

    def changeCurrentTransmission(self):
        try:
            val = float(str(self.newTransmission.text()))
        except (ValueError, TypeError):
            return

        if self.transmissionLimits is not None:
            if val < self.transmissionLimits[0] or val > self.transmissionLimits[1]:
                return

        self.attenuators.setTransmission(val)
        self.newTransmission.setText("")

    def connected(self):
        self.transmissionLimits = (0, 100)
        self.topBox.setEnabled(True)

    def disconnected(self):
        self.transmissionLimits = None
        self.topBox.setEnabled(False)

    def attStateChanged(self, value):
        if value is None:
            return

    def attFactorChanged(self, value):
        logging.getLogger("user_level_info").info(
            "Attenuator factor changed to %s" % value
        )
        self.currentTransmissionValue = value
        if value is None:
            return
        if value < 0:
            self.currentTransmissionValue = None
            self.currentTransmission.setText("")
        else:
            att_str = self["formatString"] % value
            self.currentTransmissionValue = att_str
            self.currentTransmission.setText("%s%%" % att_str)
            self.updateTransHistory(att_str)

    def updateTransHistory(self, trans):
        if trans not in self.transHistory:
            if len(self.transHistory) == self.MAX_HISTORY:
                del self.transHistory[-1]
            self.transHistory.insert(0, trans)

    def openHistoryMenu(self):
        menu = QPopupMenu(self)
        menu.insertItem(QLabel("<nobr><b>Transmission history</b></nobr>", menu))
        menu.insertSeparator()
        for i in range(len(self.transHistory)):
            menu.insertItem("%s%%" % self.transHistory[i], i)
        QObject.connect(menu, SIGNAL("activated(int)"), self.goToTransHistory)
        return menu

    def goToTransHistory(self, idx):
        trans = float(self.transHistory[idx])
        self.attenuators.setTransmission(trans)
