"""
Lakeshore brick
Tested on Lakeshore 218
"""
import logging
import weakref
import time
import os
import ValueDisplayBrick
from PyMca.QtBlissGraph import QtBlissGraph
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from qt import *

__category__ = 'instrument'

class HorizontalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

class LakeshoreBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.addProperty("unit", "combo", ("C", "K"), "C")
        self.addProperty("baseTime", "combo", ("current time", "0"), "0")

        self.lstChannelValueDisplay = []
        self.lstChannelWidgets = []
        self.data = {}
        self.lakeshore = None

        graphBox = QVBox(self)
        graphButtonsBox = QHBox(graphBox)
        graphButtonsBox.setSpacing(5)
        self.graph = QtBlissGraph(graphBox)
        self.graph.setx1timescale(True)
        self.graph.xlabel("time")
        self.graph.ylabel("temperature (%s)" % self["unit"])
        self.graph.setPaletteBackgroundColor(Qt.white)
        self.graph.canvas().setMouseTracking(True)
        self.cmdResetZoom = QPushButton("Reset zoom", graphButtonsBox)
        self.lblXY = QLabel("X = ? ; Y = ?", graphButtonsBox)
        HorizontalSpacer(graphButtonsBox)
        self.cmdSaveData = QToolButton(graphButtonsBox)
        self.cmdSaveData.setUsesTextLabel(True)
        self.cmdSaveData.setTextLabel("Save data to file")
        self.cmdSaveData.setIconSet(QIconSet(Icons.load("save")))
        self.cmdSaveData.setTextPosition(QToolButton.BesideIcon)

        self.topFrame = QVGroupBox("Lakeshore - ", self)
        updateFreqBox = QHBox(self.topFrame)
        updateFreqBox.setSpacing(5)
        QLabel("Update frequency : every", updateFreqBox)
        self.spnUpdateFrequency = QSpinBox(64, 30000, 500, updateFreqBox)
        QLabel("millisecond", updateFreqBox)
        self.lblUpdateFrequency = QLabel("<nobr><b>current = ?</b></nobr>", updateFreqBox) 
        self.cmdUpdateFrequency = QPushButton("Change", updateFreqBox)
        HorizontalSpacer(updateFreqBox)
        self.lblStatus = QLabel("<h1>status</h1>", self.topFrame)
        self.lblStatus.setAlignment(Qt.AlignCenter)
        innerBox = QVBox(self.topFrame)
        self.channelsBox = QGrid(8, innerBox)
        self.channelsBox.setSpacing(5)
        self.channelsBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        commandsBox = QVBox(innerBox)
        VerticalSpacer(self.topFrame)
        resetBox = QHBox(self.topFrame)
        HorizontalSpacer(resetBox)
        #self.cmdReset = QToolButton(resetBox)
        #self.cmdReset.setUsesTextLabel(True)
        #self.cmdReset.setTextLabel("Reset instrument")
        #self.cmdReset.setIconSet(QIconSet(Icons.load("reload")))
        #self.cmdReset.setTextPosition(QToolButton.BesideIcon)

        #QObject.connect(self.cmdReset, SIGNAL("clicked()"), self.lsReset)
        QObject.connect(self.cmdResetZoom, SIGNAL('clicked()'), self.graph.ResetZoom)
        QObject.connect(self.cmdSaveData, SIGNAL('clicked()'), self.saveGraph)
        QObject.connect(self.graph, PYSIGNAL('QtBlissGraphSignal'), self.graphSignal)
        QObject.connect(self.cmdUpdateFrequency, SIGNAL("clicked()"), self.lsUpdateFrequency) 
 
        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(graphBox)
        self.layout().addWidget(self.topFrame)
        

    def graphSignal(self, dict):
        if dict['event'] == 'MouseAt':            
            self.lblXY.setText("X = %.3f ; Y = %.3f" % (dict['x'], dict['y']))


    def setStatus(self, status):
        self.lblStatus.setText("<nobr><h1>status: %s</h1></nobr>" % status)


    def updateFrequency(self, freq):
        self.lblUpdateFrequency.setText("<nobr><b>current = %d</b></nobr>" % freq)
        self.spnUpdateFrequency.setValue(freq)


    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            self.lakeshore = self.getHardwareObject(newValue)

            if self.lakeshore is not None:
                self.lakeshore.setUnit(self["unit"])
                self.topFrame.setTitle("Lakeshore - %s" % self.lakeshore.getIdent())
                self.updateFrequency(self.lakeshore.interval)
 
                for w in self.lstChannelWidgets:
                    w.close(True)

                self.lstChannelValueDisplay = []
                self.lstChannelWidgets = []
                self.channelCheckboxCb = weakref.WeakKeyDictionary()
                
                for i in range(self.lakeshore.getChannelsNumber()):
                    newCheckbox = QCheckBox("Channel %d" % (i+1), self.channelsBox)
                    self.lstChannelWidgets.append(newCheckbox)

                    self.data[i]=None

                    def checkbox_cb(state, channel=i):
                        if state == QButton.On:
                            self.data[channel]={ "x":[], "y":[], "t0": None }
                        else:
                            self.data[channel]=None

                    self.channelCheckboxCb[newCheckbox] = checkbox_cb

                    QObject.connect(newCheckbox, SIGNAL("stateChanged(int)"), checkbox_cb)
                    
                    newValueDisplayBrick = ValueDisplayBrick.ValueDisplayBrick(self.channelsBox, "channel%d" % i)
                    self.lstChannelValueDisplay.append(newValueDisplayBrick)
                    self.lstChannelWidgets.append(self.lstChannelValueDisplay[-1])
                    newValueDisplayBrick["unit"] = self["unit"]
                    newValueDisplayBrick["valueLabel"]=""
                    newValueDisplayBrick["showSynoptic"] = False
                    newValueDisplayBrick["showTitle"] = False
                    newValueDisplayBrick["formatString"]="+####.##"
                    newValueDisplayBrick.show()
                    
                self.connect(self.lakeshore, "statusChanged", self.setStatus)
                self.connect(self.lakeshore, "channelsUpdate", self.lsChannelsUpdated)
                self.connect(self.lakeshore, "intervalChanged", self.updateFrequency)
        elif property == "unit":
            if self.lakeshore is not None:
                self.lakeshore.setUnit(newValue)
        elif property == "baseTime":
            for channel, curve_data in self.data.items():
                if curve_data is None:
                   continue
 
                self.graph.delcurve("channel %d" % (channel+1))
                
                curve_data["x"]=[]
                curve_data["y"]=[]
                curve_data["t0"]=None


    def saveGraph(self):
        filename = str(QFileDialog.getSaveFileName(os.environ["HOME"],
                                               "Data file (*.dat *.txt)",
                                               self,
                                               "Save file",
                                               "Choose a filename to save under"))

        if len(filename) == 0:
            return
        
        try:
            f = open(filename, "w")
        except:
            logging.getLogger().exception("An error occured while trying to open file %s", filename)
            QMessageBox.warning(self, "Error", "Could not open file %s for writing !" % filename, QMessageBox.Ok)
        else:
            contents = ["#F Lakeshore temperatures", "#D %s" % time.ctime(time.time())]

            for channel, curve_data in self.data.items():
                if curve_data is None:
                    continue

                contents.append("\n#S %d %s" % (channel+1, "channel %d" % (channel+1)))
                contents.append("#N 2")
                contents.append("#L  %s  %s" % ("time (s)", "temperature"))

                for x, y in zip(curve_data["x"], curve_data["y"]):
                    contents.append("%s %s" % (str(x), str(y)))

                contents.append("\n")

            try:
                try:
                    f.write("\n".join(contents))
                except:
                    QMessageBox.warning(self, "Error", "Could not save file to\n%s" % filename, QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Success", "Data have been saved successfully to\n%s" % filename, QMessageBox.Ok)
            finally:
                f.close()

        

    def lsChannelsUpdated(self, values):
        i = 0
        t = None
        
        if self["baseTime"] == "0":
            t = time.time()
            
            try:
                t0 = min([_f for _f in [d["t0"] for d in [_f for _f in iter(self.data.values()) if _f]] if _f])
            except ValueError:
                t0 = t
 
        for v in values:
            curve_name = "channel %d" % (i+1)
            
            self.lstChannelValueDisplay[i].setValue(v)
            self.lstChannelValueDisplay[i]["unit"] = self["unit"]

            if self.data[i] is not None:
                if self.data[i]["t0"] is None:
                    self.data[i]["t0"] = t

                if self["baseTime"] == "0":
                    self.data[i]["x"].append(t-t0)
                else:
                    # convert computer local time to seconds
                    t = time.localtime()
                    self.data[i]["x"].append(sum([t[n+3]*(60**(2-n)) for n in range(3)]))
                
                self.data[i]["y"].append(v)

                self.graph.newcurve(curve_name, self.data[i]["x"], self.data[i]["y"])
            else:
                self.graph.delcurve(curve_name) 
                    
            i += 1 

        self.graph.replot()


    def lsReset(self):
        if self.lakeshore is not None:
            self.lakeshore.reset()


    def lsUpdateFrequency(self):
        new_freq = self.spnUpdateFrequency.value()
  
        if self.lakeshore is not None:
            self.lakeshore.setInterval(new_freq)
