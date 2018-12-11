import logging
import types
import time

from  SpecClient import *

import qt

from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils.McceWidget import McceWidget

__category__ = "Instrument"

# There is one brick for 1 electrometer now.

# def decdebug(func):
#     print "--McceBrick--DEBUG--", func.__name__, "   > ",
#     return func

class McceBrick(BlissWidget):
    """
    this brick allows to display Mcce infos
    """
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.firstTime = True

        self.addProperty('mnemonic', 'string', '')

        # Hadrware Object.
        self.hwo = None

        # electrometer
        self.elec    = None
        self._name   = None
        self._number = None

        # Electrometer Widget.
        self.elecWidget = None

        qt.QHBoxLayout(self, 0, 0)

        self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)

        """
        GRAPHICAL INTERFACE
        """
        self.buildInterface()
        self.__idle = qt.QTimer()
        self.connect(self.__idle, qt.SIGNAL("timeout()"), self.__lastInit)

    def buildInterface(self):
        '''
        Creates the widget unconfigured.
        '''

        # (enumber = 0, etype = 0,
        #  erange = None, efreq = None,  egain = None, epolarity = None,
        #  parent = None, name = None)
        self.elecWidget = McceWidget( 0, 0, None, None, None, None,
                                     self, "NoName")


        # Puts widget in layout
        self.layout().addWidget(self.elecWidget)
        self.elecWidget.show()



    def configureInterface(self):
        '''
        ?
        '''
        print "--McceBrick--configureInterface--", self._name

        # ?? before any connection ??
        self.elecWidget.setType(self.hwo.mcce_type)

        # Connects signals : HWO -----> GUI
        self.hwo.connect(qt.PYSIGNAL("updateRange"), self.rangeToChange)
        self.hwo.connect(qt.PYSIGNAL("updateFreq"),  self.freqToChange)
        self.hwo.connect(qt.PYSIGNAL("updateGain"),  self.gainToChange)
        self.hwo.connect(qt.PYSIGNAL("updatePol"),   self.polToChange)
        self.hwo.connect(qt.PYSIGNAL("updateType"),  self.typeToChange)
        self.hwo.connect(qt.PYSIGNAL("updateDev"),   self.devToChange)
        self.hwo.connect(qt.PYSIGNAL("updateName"),  self.nameToChange)



        # Fills the combo lists.
        self.elecWidget.initRangeList()
        self.elecWidget.initPolList()
        self.elecWidget.initGainList()
        self.elecWidget.initFreqList()

        # _name = "toto"
        # self.elecWidget.setName(_name)


        # Connection of signals :   GUI ------> HARDWARE OBJECT
        self.connect(self.elecWidget, qt.PYSIGNAL("rangeChanged"),     self.setRange)
        self.connect(self.elecWidget, qt.PYSIGNAL("gainChanged"),      self.setGain)
        self.connect(self.elecWidget, qt.PYSIGNAL("frequencyChanged"), self.setFrequency)
        self.connect(self.elecWidget, qt.PYSIGNAL("polarityChanged"),  self.setPolarity)

        # First Initialization.
        print "--McceBrick.py--first initialization--"
        self.numberToChange(self.hwo.mcce_number)
        self.rangeToChange(self.hwo.mcce_range)
        self.freqToChange(self.hwo.mcce_freq)
        self.gainToChange(self.hwo.mcce_gain)
        self.polToChange(self.hwo.mcce_pol)
        self.devToChange(self.hwo.mcce_dev)   # taco DS name.
        self.nameToChange(self.hwo.mcce_name) # name of the electrometer channel.


    def __lastInit(self) :
        self.__idle.stop()
        print "--McceBrick--__lastInit-- fin du timer, maintenant on peut bosser tranquille ...--", self._name
        self.configureInterface()


    def run(self):
        '''
        '''
        if self.firstTime:
            # self.configureInterface()
            # print "run first time McceBrick "
            pass
        else:
            # print "run (not first time) McceBrick"
            pass

        self.firstTime = False
        self.__idle.start(2230)


    def isGainType(self, device):
        ''' Return True if the device is a gain electrometer'''
        _type = device.getType()
        return (_type == 4 or _type == 5)

    def isFreqType(self, device):
        ''' Return True if the device is a frequency electrometer'''
        _type = device.getType()
        return (_type == 1 or _type == 2 or _type == 3 or _type == 6)


    def propertyChanged(self, property, oldValue, newValue):
        ''' Called each time a brick propertie is changed.
        Here we connect the brick to the hardware object defined in mnemonic
        field (usualy mcce.xml)
        '''
        if property == 'mnemonic':
            print "--mcceBrick--propertyChanged--mnemonic"
            if self.hwo is not None:
                # + close all objects previously created ???
                self.hwo = None

            self.hwoName = newValue

            self.hwo = self.getHardwareObject(self.hwoName)

            if self.hwo is None:
                print "--mcceBrick--propertyChanged--ERROR-- hwo is None"
                return
            else:
                print "--mcceBrick--propertyChanged-- hwo OK, now connecting :", self.hwo
                self.hwo.connect(qt.PYSIGNAL("hwoConnected"), self.hwoConnected)


    '''
    Functions to change the GUI widgets.
    '''
    def rangeToChange(self, val):
        print "--val=%s(string)"%val
        self.elecWidget.setRange(val)

    def freqToChange(self, val):
        print "--mcceBrick--freqToChange--val=%s(string)"%val
        if self.elecWidget.isFreqType():
            self.elecWidget.setFreq(val)

    def gainToChange(self, val):
        print "--mcceBrick--gainToChange--val=%s(string)"%val
        if self.elecWidget.isGainType():
            self.elecWidget.setGain(val)

    def polToChange(self, val):
        print "--mcceBrick--polToChange--val=%s(string)"%val
        self.elecWidget.setPol(val)

    def typeToChange(self, val):
        print "--mcceBrick--typeToChange--val=%s(string)"%val
        self.elecWidget.setType(val)

    def devToChange(self, val):
        print "--mcceBrick--devToChange--val=%s(string)"%val
        self.elecWidget.setDSName(val)

    def nameToChange(self, name):
        print "--mcceBrick--nameToChange--val=%s(string)"%name
        self.elecWidget.setName(name)

    def numberToChange(self, number):
        print "--mcceBrick--numberToChange--val=%d(int)"%number
        self._number = number
        self.elecWidget.setNumber(number)



    '''
    Functions  to call SPEC mcce macros via HWO.
    '''
    def setRange(self, v):
        (val, widgetNb) = v
        # print "--mcceBrick--setRange-- rangeVal=%s, widgetnb=%d"%(val, widgetNb)
        self.hwo.mcceRangeCmd(widgetNb+1, str(val))


    def setGain(self, v):
        (val, widgetNb) = v
        #print "--mcceBrick--setGain-- gainVal=%s, widgetnb=%d"%(val, widgetNb)
        self.hwo.mcceGainCmd(widgetNb+1, str(val))

    def setFrequency(self, v):
        (val, widgetNb) = v
        #print "--mcceBrick--setFrequency-- freqVal=%s, widgetnb=%d"%(val, widgetNb)
        self.hwo.mcceFreqCmd(widgetNb+1, str(val))

    def setPolarity(self, v):
        (val, widgetNb) = v
        #print "--mcceBrick--setPolarity-- polVal=%s, widgetnb=%d"%(val, widgetNb)

        if (str(val))=="positive":
            self.hwo.mccePolCmd(widgetNb+1, "+")
        elif str(val)=="negative":
            self.hwo.mccePolCmd(widgetNb+1, "-")
        else:
            print "--mcceBrick--setPolarity-- ERROR not a valid polarity", val

    def hwoConnected(self, val ):
        '''
        - called dwhen HWO is starting connections...
          => not all connections are finnished...
        '''
        #print "--mcceBrick--hwoConnected-- OK, hardware object is connected.", val
        pass

