import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *

__category__ = "mxCuBE"
__author__ = "Matias Guijarro"
__version__ = 1.0


SC_STATE_COLOR = { "FAULT": "red",
                   "STANDBY": "green",
                   "MOVING": "yellow",
                   "ALARM": "purple",
                   "DISABLE": "grey",
                   "RUNNING": "yellow",
                   "UNKNOWN": "grey",
                   "CLOSE": "white",
                   "OFF": "white",
                   "INIT": "yellow" }


class HorizontalSpacer(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)


class MicrodiffBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.defineSignal("centringSuccessful", ())

        self.microdiff = None
         
        # GUI
        self.statusBox = QVGroupBox("Status", self)
        self.lblStatus = QLabel("", self.statusBox)
      
        self.statusBox.setInsideMargin(5)
        self.statusBox.setInsideSpacing(10)
        self.statusBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lblStatus.setAlignment(Qt.AlignHCenter)
       
        self.chkBackground = QCheckBox("Auto-check automatic centring background", self)
        QObject.connect(self.chkBackground, SIGNAL("clicked()"), self.setAutocheckBackground)
 
        # final layout
        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(self.statusBox)
        self.layout().addWidget(self.chkBackground)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)        
 
       
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.microdiff is not None:
                self.disconnect(self.microdiff, PYSIGNAL("stateChanged"), self.microdiffStateChanged)
                self.disconnect(self.microdiff, PYSIGNAL("statusChanged"), self.microdiffStatusChanged)
                self.disconnect(self.microdiff, PYSIGNAL("centeringSuccessful"), self.microdiffCenteringSuccessful)
                self.disconnect(self.microdiff, PYSIGNAL("autocheckBackground"), self.autocheckBackgroundChanged)
           
            self.microdiff = self.getHardwareObject(newValue)

            if self.microdiff is not None:
                self.connect(self.microdiff, PYSIGNAL("stateChanged"), self.microdiffStateChanged)
                self.connect(self.microdiff, PYSIGNAL("statusChanged"), self.microdiffStatusChanged)
                self.connect(self.microdiff, PYSIGNAL("autocheckBackground"), self.autocheckBackgroundChanged)
            else:
                self.microdiffStateChanged("UNKNOWN")
                self.microdiffStatusChanged("?")   
    

    def microdiffStatusChanged(self, status):
        status = status.replace("#", "")
        self.lblStatus.setText("<b><h1>%s</h1></b>" % status)
        if status.startswith("centring") and status.endswith("successfull"):
          logging.getLogger().info("emitting centring successfull 1")
          self.emit(PYSIGNAL("centringSuccessful"), (1, self.microdiff.getCentringStatus()))
        #else:
        #  logging.getLogger().info("emitting centring successfull 0")
        #  self.emit(PYSIGNAL("centringSuccessful"), (0, self.microdiff.getCentringStatus()))
        
   
    def microdiffStateChanged(self, state):
        self.emit(PYSIGNAL("stateChanged"), (state, ))
        self.lblStatus.setPaletteBackgroundColor(QColor(SC_STATE_COLOR[state]))
        self.statusBox.setTitle("Status - %s" % state)


    def autocheckBackgroundChanged(self, autocheck):
        if autocheck < 0:
          self.chkBackground.setEnabled(False)
        else: 
          self.chkBackground.setEnabled(True)
          if autocheck:
            self.chkBackground.setChecked(True)
          else:
            self.chkBackground.setChecked(False)


    def setAutocheckBackground(self):
       if self.microdiff is not None:
          self.microdiff.setAutocheckBackground(self.chkBackground.isChecked()) 
