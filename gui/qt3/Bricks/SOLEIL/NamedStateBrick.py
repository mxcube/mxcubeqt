from BlissFramework import BaseComponents
from qt import *
from BlissFramework.Utils import widget_colors
import logging

__category__ = "SOLEIL"
__author__ = "Bixente Rey Bakaikoa"
__version__ = "1.0"


class NamedStateBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.hwo = None
        self.hdwstate = "Ready"

        #
        # add properties and brick signals
        #
        self.addProperty("mnemonic", "string", "")

        #
        # create GUI components
        #
        self.lblUsername = QLabel("", self)
        self.lstStates = QComboBox(self)

        #
        # configure GUI components
        #
        self.lstStates.setEditable(False)
        QToolTip.add(self.lstStates, "Select where to go to")

        #
        # connect signals / slots
        #
        QObject.connect(
            self.lstStates, SIGNAL("activated( int )"), self.lstStatesClicked
        )

        #
        # layout
        #
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        QVBoxLayout(self, 5, 5)
        self.lblUsername.setText("PHASE")
        self.layout().addWidget(self.lblUsername, 0)
        self.layout().addWidget(self.lstStates, 0)

        self.palet = QPalette()
        self.states = None

        box1 = QHBox(self)
        self.layout().addWidget(box1, 0)
        self.lstStates.reparent(box1, 0, QPoint(0, 0), True)
        box1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        QToolTip.add(self.lstStates, "Trigger a change to new state")

        self.defineSlot("setEnabled", ())

    def propertyChanged(self, property, oldValue, newValue):

        logging.debug(
            "Changing property for NamedStateBrick %s = %s" % (property, newValue)
        )

        if property == "mnemonic":

            self.setMnemonic(newValue)

            if self.hwo is not None:
                lbl = self.hwo.getUserName()
                if lbl.strip() != "":
                    lbl += " :"
                self.lblUsername.setText("<i>" + lbl + "</i>")

            if self.hwo is None:
                self.palet.setColor(QColorGroup.Base, QColor("#eeeeee"))
                self.lstStates.setPalette(self.palet)
            else:
                self.palet.setColor(QColorGroup.Base, QColor("#ddffdd"))
                self.lstStates.setPalette(self.palet)

    def setMnemonic(self, mne):

        if self.hwo is not None:
            self.disconnect(self.hwo, PYSIGNAL("stateChanged"), self.stateChanged)
            self.disconnect(
                self.hwo, PYSIGNAL("hardwareStateChanged"), self.hdwStateChanged
            )
            self.disconnect(self.hwo, PYSIGNAL("newStateList"), self.stateList)

        self.hwo = self.getHardwareObject(mne)

        if self.hwo is not None:

            username = self.hwo.getUserName()
            if username.strip() != "":
                logging.debug(username)
                username += " :"
            self.lblUsername.setText(username + " :")

            self.fillStates()

            self.connect(self.hwo, PYSIGNAL("newStateList"), self.fillStates)
            self.connect(self.hwo, PYSIGNAL("stateChanged"), self.stateChanged)
            self.connect(
                self.hwo, PYSIGNAL("hardwareStateChanged"), self.hdwStateChanged
            )

            if self.hwo.isReady():
                self.stateChanged(self.hwo.getCurrentState())
        else:
            self.lblUsername.setText("State Object:")
            self.cleanStates()

        self.lblUsername.setText("")
        # self.setToolTip(name=mne)

    def fillStates(self, states=None):
        self.cleanStates()

        if self.hwo is not None:
            if states is None:
                states = self.hwo.getStateList()

        if states is None:
            states = []

        for state_name in states:
            self.lstStates.insertItem(str(state_name))

        self.states = states

        if self.hwo is not None:
            if self.hwo.isReady():
                self.stateChanged(self.hwo.getCurrentState())

        self.lstStates.show()

    def lstStatesClicked(self, index):
        logging.debug(" changed required on brick %d" % index)

        if index > 0:
            if self.hwo.isReady():
                logging.debug("       trying to go to %s" % self.states[index - 1])
                self.hwo.setState(self.states[index - 1])
            else:
                logging.debug("       but not ready")
                self.lstStates.setCurrentItem(0)

    def hdwStateChanged(self, hdwstate):
        self.hdwstate = str(hdwstate)
        logging.debug(" hdw state changed it is %s" % hdwstate)
        if self.hdwstate == "RUNNING":
            self.palet.setColor(QColorGroup.Base, QColor("#ffff99"))
            self.lstStates.setPalette(self.palet)
        elif self.hdwstate == "STANDBY":
            self.palet.setColor(QColorGroup.Base, QColor("#ddffdd"))
            self.lstStates.setPalette(self.palet)
        else:
            self.palet.setColor(QColorGroup.Base, QColor("#ffdddd"))
            self.lstStates.setPalette(self.palet)

    def stateChanged(self, state):
        if not self.lstStates:
            logging.debug("   - but no state list is ready")
            self.palet.setColor(QColorGroup.Base, QColor("#cccccc"))
            self.lstStates.setPalette(self.palet)
        else:
            self.lstStates.setCurrentItem(0)

            for i in range(len(self.states)):
                if self.states[i] == state:
                    logging.debug("   - found it")
                    self.lstStates.setCurrentItem(i + 1)
                    break
            else:
                logging.debug(
                    "   - could not find %s in list of valid states (%s)"
                    % (state, str(self.states))
                )

    def cleanStates(self):
        self.lstStates.clear()
        self.lstStates.insertItem("")
