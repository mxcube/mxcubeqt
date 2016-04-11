#!/usr/bin/env python
# McceWidget.py

__author__  = "cyril.guilloud@esrf.fr"
__date__    = "Fri 28 Sep 2007 10:12:07"
__version__ = 0.2

# imports python
import sys
#import logging

# imports qt
import qt

# imports mccewidget
#from BlissFramework.BaseComponents import BlissWidget
#from BlissFramework.Utils.mcceVals import *
from mcceVals import *

class McceWidget(qt.QWidget):
    def __init__(self, enumber = 0, etype = 0, erange = None, efreq = None,
                 egain = None, epolarity = None, parent = None, name = "tutu"):

        qt.QWidget.__init__(self, parent, "McceWidget")

        self._number    = enumber
        self._type      = etype
        self._range     = erange
        self._frequency = efreq
        self._gain      = egain
        self._polarity  = epolarity

        self.gainTypes  = [4, 5]
        self.freqTypes  = [1, 2, 3, 6]

        layout = qt.QVBoxLayout(self, 0 ,-1 , "McceWidgetMainLayout")

        # TITLE (default name)
        self.titleLabel = qt.QLabel("<b>Electrometer %d</b>"%self._number, self)
        self.titleLabel.setAlignment(qt.Qt.AlignHCenter)
        #self.titleLabel.setMinimumWidth(110)

        # Number  +   TACO DEVICE NAME (for information)
        self.ds_layout = qt.QHBoxLayout(None, 0 ,-1 , "McceWidget-TacoLayout")
        self.devNumber = qt.QLabel(name, self)
        self.tacoDevName = qt.QLabel(name, self)
        self.tacoDevName.setAlignment(qt.Qt.AlignHCenter)
        self.ds_layout.addStretch(1)
        self.ds_layout.addWidget(self.devNumber)
        self.ds_layout.addStretch(2)
        self.ds_layout.addWidget(self.tacoDevName)
        self.ds_layout.addStretch(1)

        # FRAME
        self.frame = qt.QFrame(self)
        self.frame.setFrameShape(qt.QFrame.Box)
        self.frame.setFrameShadow(qt.QFrame.Sunken)
        framelayout = qt.QVBoxLayout(self.frame, 5, 5, "FrameLayout")

        # MAIN LAYOUT MANAGEMENT
        layout.addStretch(1)
        layout.addWidget(self.titleLabel)
        # layout.addWidget(self.tacoDevName)
        layout.addLayout(self.ds_layout)
        layout.addStretch(1)
        layout.addWidget(self.frame)
        layout.addStretch(1)

        # TYPE field
        self.typeLabel = qt.QLabel("<b>Type %d</b>"%self._type, self.frame)
        self.typeLabel.setSizePolicy(qt.QSizePolicy.Fixed,
                                     qt.QSizePolicy.Fixed)
        self.typeLabel.setMinimumWidth(80)

        self.typeLayout = qt.QHBoxLayout(None)
        self.typeLayout.addStretch(1)
        self.typeLayout.addWidget(self.typeLabel)
        self.typeLayout.addStretch(1)

        # RANGE field
        # for all types
        self.rangeLabel  = qt.QLabel("range", self.frame)
        self.rangeCombo  = qt.QComboBox(self.frame, "range combo")

        self.rangeLayout = qt.QHBoxLayout(None)
        self.rangeLayout.addWidget(self.rangeLabel)
        self.rangeLayout.addWidget(self.rangeCombo)

        self.connect(self.rangeCombo, qt.SIGNAL("activated( const QString & )"),
                     self.rangeChanged )

        # GAIN field
        # types 4 and 5
        self.gainLabel  = qt.QLabel("gain",self.frame)
        self.gainCombo  = qt.QComboBox(self.frame, "gain combo")

        self.gainLayout = qt.QHBoxLayout(None)
        self.gainLayout.addWidget(self.gainLabel)
        self.gainLayout.addWidget(self.gainCombo)

        self.connect(self.gainCombo, qt.SIGNAL("activated( const QString & )"),
                     self.gainChanged )

        # FREQUENCY field
        # types 1 2 3 6
        self.frequencyLabel  = qt.QLabel("frequency",self.frame)
        self.frequencyCombo  = qt.QComboBox(self.frame, "freq combo")

        self.frequencyLayout = qt.QHBoxLayout(None)
        self.frequencyLayout.addWidget(self.frequencyLabel)
        self.frequencyLayout.addWidget(self.frequencyCombo)

        self.connect(self.frequencyCombo, qt.SIGNAL("activated( const QString & )"),
                     self.frequencyChanged )

        # POLARITY field
        # for all types
        self._polarityList = ["positive", "negative"]

        self.polarityLabel  = qt.QLabel("polarity",self.frame)
        self.polarityCombo  = qt.QComboBox(self.frame , "pol combo")

        self.polarityLayout = qt.QHBoxLayout(None)
        self.polarityLayout.addWidget(self.polarityLabel)
        self.polarityLayout.addWidget(self.polarityCombo)

        self.connect(self.polarityCombo, qt.SIGNAL("activated( const QString & )"),
                     self.polarityChanged )


        # LAYOUT PLACEMENT
        framelayout.addLayout(self.typeLayout)
        framelayout.addStretch(2)
        framelayout.addLayout(self.rangeLayout)
        framelayout.addLayout(self.gainLayout)
        framelayout.addLayout(self.frequencyLayout)
        framelayout.addLayout(self.polarityLayout)
#        framelayout.addStretch(1)
#        framelayout.addLayout(self.channelLayout)
        framelayout.addStretch(1)

        # WIDGET SIZE
        self.setMaximumSize(qt.QSize(210,260))

    def setNumber(self, number):
        ''' Sets the electrometer number '''
        self._number = number
        self.devNumber.setText(str(number))

    def setName(self, name):
        ''' Sets the name of the electrometer'''
        self.titleLabel.setText("<b>%s</b>"%name)

    def setDSName(self, dsname):
        ''' Sets the DS name of the electrometer'''
        self.tacoDevName.setText(str(dsname))

    def setType(self, value):
        ''' Sets the type of the electrometer: gain or frequency
        Hide the unused combobox.
        '''
        try:
            _val = int(value)

            if _val in self.gainTypes:
                self._type = _val
            elif _val in self.freqTypes:
                self._type = _val
            else:
                print "--mcceWidget--setType-- ERROR : bad type : ", _val

            if self.isGainType():
                self.frequencyCombo.hide()
                self.frequencyLabel.hide()
            else:
                self.gainLabel.hide()
                self.gainCombo.hide()

            self.typeLabel.setText("<b>Type %d</b>"%self._type)

        except:
            print "unknown type"



    def isGainType(self):
        return (self._type in self.gainTypes)

    def isFreqType(self):
        return (self._type in self.freqTypes)


    '''
    Lists initializations
    '''
    def initFreqList(self):
        ''' Set the frequency combo list values.
        '''
        #print "--mcceWidget--initFreqList-- "
        self.frequencyCombo.insertStrList(
            [ str(x) for x in MCCE_FREQ_LIST[self._type]])

    def initPolList(self):
        ''' Set the polarity combo list values.
        '''
        #print "--mcceWidget--initPolList-- "
        self.polarityCombo.insertStrList(self._polarityList)

    def initRangeList(self):
        ''' Set the range combo list values.
        '''
        #print "--mcceWidget--initRangeList-- "
        self.rangeCombo.insertStrList(
            [ str(x) for x in MCCE_RANGE_LIST[self._type]])

    def initGainList(self):
        ''' Set the gain combo list values.
        '''
        #print "--mcceWidget--initGainList-- "
        self.gainCombo.insertStrList(
            [ str(x) for x in MCCE_GAIN_LIST[self._type]])

    '''
    GUI changes signals.
    GUI -> outer world.
    Adds a widget identifier _number to the signal.
    '''
    def rangeChanged(self, newValue):
        print "--mcceWidget--user change  range ;  new value=", newValue, " number=", self._number
        self.emit(qt.PYSIGNAL("rangeChanged"), ((newValue, self._number),))

    def gainChanged(self, newValue):
        print "--mcceWidget--user change  gain ;  new value=", newValue, " number=", self._number
        self.emit(qt.PYSIGNAL("gainChanged"), ((newValue, self._number),))

    def frequencyChanged(self, newValue):
        print "--mcceWidget--user change frequency ;  new value=", newValue, " number=", self._number
        self.emit(qt.PYSIGNAL("frequencyChanged"), ((newValue, self._number),))

    def polarityChanged(self, newValue):
        print "--mcceWidget--user change  polarity ;  new value=", newValue, " number=", self._number
        self.emit(qt.PYSIGNAL("polarityChanged"), ((newValue, self._number),))


    '''
    Functions to change parameters of an electrometer in the GUI.
    '''
    def setRange(self, val):
        print "--McceWidget--setRange--val=%s(string)--"%val

        try:
            idx = MCCE_RANGE_LIST[self._type].index(val)
        except:
            print "--McceWidget--setRange-- set range to", type(val), val
            print "--McceWidget--setRange-- MCCE_RANGE_LIST", MCCE_RANGE_LIST
            print "--McceWidget--setRange-- self._type=%d , val=%s"%(self._type, val)

        try:
            self.rangeCombo.setCurrentItem(idx)
        except:
            print "--McceWidget--setRange-- ERROR: pas une val de la liste des range"

    def setGain(self, val):
        #print "--McceWidget--setGain-- set gain to %s (type=%d)"%(val, self._type)
        #print "MCCE_GAIN_LIST=", MCCE_GAIN_LIST
        #print "MCCE_GAIN_LIST[self._type]=", MCCE_GAIN_LIST[self._type]

        try:
            idx = MCCE_GAIN_LIST[self._type].index(int(val))
            self.gainCombo.setCurrentItem(idx)
        except:
            print "--McceWidget--setGain-- ERROR: pas une val de la liste des gains"

    def setFreq(self, val):
        #print "--McceWidget--setFreq-- set freq to %s (type=%d)"%(val, self._type)
        #print "MCCE_FREQ_LIST=", MCCE_FREQ_LIST
        #print "MCCE_FREQ_LIST[self._type]=", MCCE_FREQ_LIST[self._type]
        try:
            idx = MCCE_FREQ_LIST[self._type].index(int(val))
            self.frequencyCombo.setCurrentItem(idx)
        except:
            print "--McceWidget--setFreq-- ERROR: pas une val de la liste des freqs"

    def setPol(self, val):
        #print "--McceWidget--setPol-- set pol to", val
        try:
            idx = self._polarityList.index(val)
            self.polarityCombo.setCurrentItem(idx)
        except:
            print "--McceWidget--setPol-- ERROR: not a good value of pol list"


class testMcceWidget (qt.QWidget):
    ''' Test class to test McceWidget without a Brick '''
    def __init__(self, nb = 1, parent = None, name = None):
        qt.QWidget.__init__(self, parent, name)

        self.layout = qt.QHBoxLayout(self, 8 ,5 , "mainTestLayout")

        self.freqTypes  = [1, 2, 3, 6]
        self.gainTypes  = [4, 5]

        for i in range(nb):
            elec_nb   = i
            elec_type = i+1
            erange    = MCCE_RANGE_LIST[elec_type][1]
            pol       = "negative"

            if (elec_type in self.freqTypes):
                freq = MCCE_FREQ_LIST[elec_type][0]
                gain = 0
            elif (elec_type in self.gainTypes):
                gain = MCCE_GAIN_LIST[elec_type][0]
                freq = 0
            else:
                print "elec_type is not in good interval"

            mw = McceWidget(elec_nb, elec_type, erange, freq, gain, pol, self, "tt%d"%i)

            self.layout.addWidget(mw)

            mw.initRangeList()
            mw.initPolList()
            mw.initGainList()
            mw.initFreqList()

            self.connect(mw, qt.PYSIGNAL("rangeChanged"),     self.sigSetRange)
            self.connect(mw, qt.PYSIGNAL("frequencyChanged"), self.sigSetFreq)
            self.connect(mw, qt.PYSIGNAL("gainChanged"),      self.sigSetGain)
            self.connect(mw, qt.PYSIGNAL("polarityChanged"),  self.sigSetPol)

    def sigSetRange(self):
        print "sigSetRange"

    def sigSetGain(self):
        print "sigSetGain"

    def sigSetFreq(self):
        print "sigSetFreq"

    def sigSetPol(self):
        print "sigSetPol"



def main(args):
    app = qt.QApplication(sys.argv)
    win = testMcceWidget(6)
    app.setMainWidget(win)
    win.show()
    app.connect(app, qt.SIGNAL("lastWindowClosed()"),app, qt.SLOT("quit()"))
    app.exec_loop()

if __name__=="__main__":
    main(sys.argv)



