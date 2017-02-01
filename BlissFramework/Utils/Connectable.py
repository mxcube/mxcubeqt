from QtImport import *

class Connectable:
    def __init__(self):
        self.__signal = {}
        self.__slot = {}


    def defineSignal(self, signalName, signalArgs):
        try:
            args = tuple(signalArgs)
        except:
            print("'", signalArgs, "' is not a valid arguments tuple.")
            raise ValueError
        
        self.__signal[str(signalName)] = args

    def defineSlot(self, slotName, slotArgs):
        try:
            args = tuple(slotArgs)
        except:
            print("'", slotArgs, "' is not a valid arguments tuple.")
            raise ValueError
        
        self.__slot[str(slotName)] = args


    def resetSignals(self):
        self.__signal = {}


    def resetSlots(self):
        self.__slot = {}


    def removeSignal(self, signalName):
        try:
            del self.__signal[str(signalName)]
        except KeyError:
            pass
        

    def removeSlot(self, slotName):
        try:
            del self.__slot[str(slotName)]
        except KeyError:
            pass


    def hasSignal(self, signalName):
        return signalName in self.__signal


    def hasSlot(self, slotName):
        return slotName in self.__slot
    

    def getSignals(self):
        return self.__signal


    def getSlots(self):
        return self.__slot
