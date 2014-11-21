"""
[Name] BeamInfo

[Description]
BeamInfo hardware object is used to define final beam size and shape.
It can include aperture, slits and/or other beam definer (lenses or other eq.)

[Emited signals]
beamInfoChanged

[Included Hardware Objects]
-----------------------------------------------------------------------
| name            | signals          | functions
-----------------------------------------------------------------------
 aperture_HO	    apertureChanged
 slits_HO	    	
 beam_definer_HO
-----------------------------------------------------------------------
"""

import logging
from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import Equipment

class BeamInfo(Equipment):

    def __init__(self, *args):
        Equipment.__init__(self, *args)

        self.beam_size_slits = [9999, 9999]
        self.beam_size_aperture = [9999, 9999]
        self.beam_size_definer = [9999, 9999]
	self.beam_position = [0, 0]

        self.aperture_HO = None
        self.slits_HO = None
        self.beam_definer_HO = None
        self.beam_info_dict = {}

    def init(self):
	try:
           self.aperture_HO = HardwareRepository.HardwareRepository().getHardwareObject(self.getProperty("aperture"))
	   self.connect(self.aperture_HO, "apertureChanged", self.aperture_pos_changed)
	except:
	   logging.getLogger("HWR").debug('BeamInfo: aperture not defined correctly') 
        try:
           self.slits_HO = HardwareRepository.HardwareRepository().getHardwareObject(self.getProperty("slits"))
           self.connect(self.slits_HO, "gapSizeChanged", self.slits_gap_changed)
        except:
           logging.getLogger("HWR").debug('BeamInfo: slits not defined correctly')
        try:
           self.beam_definer_HO = HardwareRepository.HardwareRepository().getHardwareObject(self.getProperty("definer"))
           self.connect(self.beam_definer_HO, "definerPosChanged", self.definer_pos_changed)
        except:
           logging.getLogger("HWR").debug('BeamInfo: beam definer not defined correctly')

        #self.beam_position_hor = self.getChannelObject("beam_position_hor")
        #self.beam_position_hor.connectSignal("update", self.beam_pos_hor_changed)
        #self.beam_position_ver = self.getChannelObject("beam_position_ver")
        #self.beam_position_ver.connectSignal("update", self.beam_pos_ver_changed)
	#self.chan_beam_size_microns = self.getChannelObject("beam_size_microns")
        #self.chan_beam_shape_ellipse  = self.getChannelObject("beam_shape_ellipse")
  
    def beam_pos_hor_changed(self, value):
	self.beam_position[0] = value
	self.emit("beamPosChanged", (self.beam_position, ))

    def beam_pos_ver_changed(self, value):
        self.beam_position[1] = value 
	self.emit("beamPosChanged", (self.beam_position, ))

    def get_beam_position(self):
	return self.beam_position	

    def set_beam_position(self, beam_x, beam_y):
	self.beam_position = [beam_x, beam_y]
	self.beam_position_hor.setValue(int(beam_x))
	self.beam_position_ver.setValue(int(beam_y))

    def aperture_pos_changed(self, size): # size must be a tuple like (xsize,ysize)
        self.beam_size_aperture = size
        self.evaluate_beam_info() 
	self.emit_beam_info_change()

    def slits_gap_changed(self, size):
        self.beam_size_slits = size
        self.evaluate_beam_info()
	self.emit_beam_info_change()

    def definer_pos_changed(self, name, size):
        self.beam_size_definer = size
        self.evaluate_beam_info()
	self.emit_beam_info_change()

    def get_beam_info(self):
        return self.evaluate_beam_info()
        
    def get_beam_size(self):
	"""
	Description: returns beam size in microns
	Resturns: list with two integers
	"""
	self.evaluate_beam_info()
        return float(self.beam_info_dict["size_x"]), \
	       float(self.beam_info_dict["size_y"])

    def get_beam_shape(self):
	self.evaluate_beam_info()
        return self.beam_info_dict["shape"]

    def get_slits_gap(self):
	self.evaluate_beam_info()
	return self.beam_size_slits	

    def evaluate_beam_info(self):
        """
        Description: called if aperture, slits or focusing has been changed
        Returns: dictionary, {size_x: 0.1, size_y: 0.1, shape: "rectangular"}
        """
        size_x = min(self.beam_size_aperture[0],
	   	     self.beam_size_slits[0],
		     self.beam_size_definer[0]) 
        size_y = min(self.beam_size_aperture[1],
  		     self.beam_size_slits[1], 
		     self.beam_size_definer[1]) 
	
        self.beam_info_dict["size_x"] = size_x
        self.beam_info_dict["size_y"] = size_y

        # be careful with comparisons!!! both have to be the same type (=tuple)
        if tuple(self.beam_size_aperture) < tuple(self.beam_size_slits):
	    self.beam_info_dict["shape"] = "ellipse"
	else:
	    self.beam_info_dict["shape"] = "rectangular"
	
	return self.beam_info_dict	

    def emit_beam_info_change(self): 
	if self.beam_info_dict["size_x"] <> 9999 and \
	   self.beam_info_dict["size_y"] <> 9999:		
	    self.emit("beamSizeChanged", ((self.beam_info_dict["size_x"],\
					   self.beam_info_dict["size_y"]), ))
            self.emit("beamInfoChanged", (self.beam_info_dict, ))
	    """if self.chan_beam_size_microns is not None:
		self.chan_beam_size_microns.setValue((self.beam_info_dict["size_x"] * 1000, \
					 	     self.beam_info_dict["size_y"] * 1000))	
            if self.chan_beam_shape_ellipse is not None:
                self.chan_beam_shape_ellipse.setValue(self.beam_info_dict["shape"] == "ellipse") 
            """
