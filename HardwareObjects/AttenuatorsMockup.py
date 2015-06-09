from HardwareRepository.BaseHardwareObjects import Device

class AttenuatorsMockup(Device):
    def __init__(self, *args):
        Device.__init__(self, *args)
        self.transmission_value = 100 
        self.labels = []
        self.bits = [] 

        self.setTransmission = self.set_value

    def update_values(self):
        self.emit("valueChanged", self.transmission_value)

    def getAttState(self):
        return 0

    def getAttFactor(self):
        return self.transmission_value

    def get_value(self):
        return self.getAttFactor()

    def set_value(self, value):
        self.transmission_value = value
        self.update_values()

    def getAtteConfig(self):
        """
        Descript. :
        """
        self.attno = len( self['atte'] )
        for att_i in range( self.attno ):
           obj = self['atte'][att_i]
           self.labels.append( obj.label )
           self.bits.append( obj.bits )
