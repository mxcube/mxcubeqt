from qt import *
import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import SampleChangerBrick3

__category__ = "mxCuBE"

SC_STATE_COLOR = { 
                   "READY": "green",
                   "MOVING": "yellow",
                   "ALARM": "purple",
                   "ERROR": "red",
                   "UNKNOWN": "darkGrey",
                   "DISABLE": "darkGrey" }

class GrobSampleChangerBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.addProperty("defaultHolderLength", "integer", 22)
        self.addProperty("icons", "string", "")

        self.defineSignal("scanBasketUpdate", ())
        self.defineSignal("sampleGotLoaded", ())
        self.defineSlot('setSession',())
        self.defineSlot('setCollecting',())

        self.sampleChanger = None
        self.vialStateMap = {}
        self.inExpert=None

        self.contentsBox=QVGroupBox("Sample changer",self)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(2)

        self.status = QLabel(self.contentsBox)
        self.io = {}

        self.baskets = []
        for i in range(3):
          self.baskets.append(SampleChangerBrick3.BasketView(self.contentsBox, i+1))
          QObject.connect(self.baskets[i],PYSIGNAL("loadThisSample"),self.loadThisSample)
          self.baskets[i].contentsBox.setCheckable(True) 
          QObject.connect(self.baskets[i].contentsBox, SIGNAL("toggled(bool)"), self.toggleBasketPresence)
          self.baskets[i].setEnabled(True)

        self.unmount_button = QPushButton("Unmount sample", self.contentsBox)
        self.unmount_button.setEnabled(False)
        QObject.connect(self.unmount_button, SIGNAL("clicked()"), self.unloadSample)

        self.sampleChangerStateChanged("UNKNOWN")

        lidctrlbox = QHBox(self)
        self.lidStatusLabel = QLabel("Lid ?", lidctrlbox)
        self.lidButton = QPushButton("Open", lidctrlbox)
        QObject.connect(self.lidButton, SIGNAL("clicked()"), self.openCloseDewar)
        ln2box = QHBox(self)
        self.ln2level = QLabel("LN2 level", ln2box)

        QVBoxLayout(self)
        self.layout().addWidget(ln2box)
        self.layout().addWidget(self.contentsBox)
        self.layout().addWidget(lidctrlbox)

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
        self.contentsBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'icons':
            icons_list=newValue.split()
        elif propertyName == 'mnemonic':
            if self.sampleChanger is not None:
                self.disconnect(self.sampleChanger, PYSIGNAL("stateChanged"), self.sampleChangerStateChanged)

            self.sampleChanger=self.getHardwareObject(newValue)

            if self.sampleChanger is not None:
                self.connect(self.sampleChanger, PYSIGNAL("stateChanged"),self.sampleChangerStateChanged)
                self.connect(self.sampleChanger, PYSIGNAL("loadedSampleChanged"), self.loadedSampleChanged)
                self.connect(self.sampleChanger, PYSIGNAL("samplesMapChanged"), self.updateVials)
                self.connect(self.sampleChanger, PYSIGNAL("matrixCodesUpdate"), self.dataMatricesUpdated)
                self.connect(self.sampleChanger, PYSIGNAL("ioStatusChanged"), self.ioStatusChanged)
            else:
                self.sampleChangerStateChanged("UNKNOWN")
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def ioStatusChanged(self, io):
        self.io = io
        #logging.info("IO from SC: %r", io)
        if io["lid"]:
          self.lidStatusLabel.setText("Lid opened")
          self.lidStatusLabel.setPaletteBackgroundColor(Qt.green)
          self.lidButton.setText("Close")
        else:
          self.lidStatusLabel.setText("Lid closed")
          self.lidStatusLabel.setPaletteBackgroundColor(Qt.magenta)
          self.lidButton.setText("Open")
        if io["ln2_alarm_low"]:
          self.ln2level.setText("Alarm: LN2 level is too low")
          self.ln2level.setPaletteBackgroundColor(Qt.red)
        else:
          self.ln2level.setText("LN2 level is ok")
          self.ln2level.setPaletteBackgroundColor(Qt.green)        
        for basket, puck_name in zip(self.baskets, ("puck1", "puck2", "puck3")):
          if io[puck_name]:
            # basket is present
            basket.blockSignals(True)
            basket.setChecked(True)
            basket.blockSignals(False)
            basket.setEnabled(True)
          else:
            basket.blockSignals(True)
            basket.setChecked(False)
            basket.blockSignals(False)
            basket.setEnabled(True)

    def toggleBasketPresence(self, _):
        self.ioStatusChanged(self.io)

    def openCloseDewar(self):
        self.setEnabled(False)
        if self.io.get("lid"):
          self.sampleChanger.close_dewar(callback=lambda _: self.setEnabled(True))
        else:
          self.sampleChanger.open_dewar(callback=lambda _: self.setEnabled(True)) 

    def updateVials(self, samples_map):
        self.unmount_button.setEnabled(False)

        logging.info("%r", samples_map)

        for i in range(30):
          basket = int(i/10)
          vial = i%10

          if samples_map[i] == "on_axis":
            self.baskets[basket].samplesView.vials[vial].setVial((SampleChangerBrick3.VialView.VIAL_AXIS,''))
            self.unmount_button.setEnabled(True)
          elif samples_map[i] == "unknown":
            self.baskets[basket].samplesView.vials[vial].setVial((SampleChangerBrick3.VialView.VIAL_UNKNOWN,''))
          elif samples_map[i] == "already_mounted":
            self.baskets[basket].samplesView.vials[vial].setVial((SampleChangerBrick3.VialView.VIAL_NOBARCODE_LOADED, ''))

    def loadedSampleChanged(self, loaded_dict):
        if "on_axis" in self.sampleChanger.getSamplesMap().values():
          self.emit(PYSIGNAL("sampleGotLoaded"),())

        logging.info("loaded sample changed: %r", loaded_dict)

    def dataMatricesUpdated(self, matrix_codes):
        self.emit(PYSIGNAL("scanBasketUpdate"), (matrix_codes,))

    def sampleChangerStateChanged(self, state):
        if state == "MOVING":
          self.setEnabled(False)
        else:
          self.setEnabled(True)
    
        if state  == "WAIT_PUT" or state.startswith("WAIT_GET_SAMPLE"):
           state = "READY"
   
        try:
          self.status.setPaletteBackgroundColor(QColor(SC_STATE_COLOR[state]))
        except KeyError:
          self.status.setPaletteBackgroundColor(QColor(SC_STATE_COLOR["UNKNOWN"]))

        self.status.setText("<center>"+state+"</center>")

    def setCollecting(self,enabled_state):
        self.setEnabled(enabled_state)

    def setSession(self,session_id):
        pass

    def setExpertMode(self,state):
        self.inExpert=state

    def run(self):
        if self.inExpert is not None:
            self.setExpertMode(self.inExpert)

    def loadThisSample(self,basket,vial):
        self.sampleChanger.loadSample(22, None, (basket, vial))

    def unloadSample(self,*args,**kwargs): #holder_len,matrix_code,location):
        self.sampleChanger.unloadMountedSample()
