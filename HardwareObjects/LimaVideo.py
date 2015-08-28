"""
Lima video HO to capture images from camera
"""
from HardwareRepository import HardwareRepository

import time
import logging
import gevent
from Lima import Core
from Qub.CTools import pixmaptools
from HardwareRepository import BaseHardwareObjects
from HardwareRepository.HardwareObjects.Camera import JpegType, BayerType, MmapType, RawType

class LimaVideo(BaseHardwareObjects.Device):

    def __init__(self, name):
	BaseHardwareObjects.Device.__init__(self, name)

        self.scaling = pixmaptools.LUT.Scaling()

    def _init(self):
        print 'I am in init'
	self.scalingType = None	
	self.forceUpdate = False
 	self.camMirror = None

	self.__brightnessExists = False
	self.__contrastExists = False
	self.__gainExists = False
	self.__gammaExists = False 

	#self.camType = 'prosilica' self.getProperty("type").lower()
	#self.camAddress = '172.19.10.152' #self.getProperty("address")

	self.camType = self.getProperty("type").lower()
	self.camAddress = self.getProperty("address")
	self.camMirror = eval(self.getProperty("mirror_hor_ver"))
	print 'self.camAddress', self.camAddress

	if self.camType == 'prosilica':
	    from Lima import Prosilica
	    self.camera = Prosilica.Camera(self.camAddress)
            self.interface = Prosilica.Interface(self.camera)	
        if self.camType == 'simulation':
            from Lima import Simulator
            self.camera = Simulator.Camera()
            self.interface = Simulator.Interface(self.camera)
        try:
	    self.control = Core.CtControl(self.interface)
	    self.video = self.control.video()
	    #self.video.setExposure(40./1000.0) #(self.getProperty("interval")/1000.0)	
	    self.video.setExposure(self.getProperty("interval")/1000.0)	
	    self.__imageDimensions = self.camera.getMaxWidthHeight()
        except KeyError:
            logging.getLogger().warning('%s: not initialized. Check camera settings', self.name())

	self.setImageTypeFromXml('imagetype')
 	self.setIsReady(True)

    def setImageTypeFromXml(self, property_name):
        #image_type = self.getProperty(property_name) or 'Jpeg'
        image_type = self.getProperty(property_name) or 'Jpeg'
        #image_type = 'Jpeg'
        if image_type.lower() == 'jpeg':
            self.imgtype = JpegType()
        elif image_type.lower().startswith("bayer:"):
            self.imgtype = BayerType(image_type.split(":")[1])
	    if image_type.lower() == "bayer:8":
		self.scalingType = pixmaptools.LUT.Scaling.BAYER_RG8
	    elif image_type.lower() == "bayer:16":  	
		self.scalingType = pixmaptools.LUT.Scaling.BAYER_RG16
        elif image_type.lower().startswith("raw") :
            self.imgtype = RawType()
        elif image_type.lower().startswith("mmap:"):
            self.imgtype = MmapType(image_type.split(":")[1])

    def imageType(self):
        """Returns a 'jpeg' or 'bayer' type object depending on the image type"""
        return self.imgtype

    #############   CONTRAST   #################
    def contrastExists(self):
        return self.__contrastExists

    def setContrast(self, contrast):
        pass

    def getContrast(self):
	return 

    def getContrastMinMax(self):
	return 

    #############   BRIGHTNESS   #################
    def brightnessExists(self):
        return self.__brightnessExists

    def setBrightness(self, brightness):
	pass

    def getBrightness(self):
	return 

    def getBrightnessMinMax(self):
	return 

    #############   GAIN   #################
    def gainExists(self):
        return self.__gainExists

    def setGain(self, gain):
	self.video.setGain(gain)

    def getGain(self):
	return self.video.getGain()

    def getGainMinMax(self):
	return 

    #############   GAMMA   #################
    def gammaExists(self):
        return self.__gammaExists

    def setGamma(self, gamma):
 	pass

    def getGamma(self):
	return 

    def getGammaMinMax(self):
	return (0, 1)

    def setLive(self, mode):
	if mode:
	    self.video.startLive()
        else:
	    self.video.stopLive()
    
    def getWidth(self):
	return self.__imageDimensions[0]
	
    def getHeight(self):
	return self.__imageDimensions[1]

    def _do_imagePolling(self, sleep_time):
        while True:
              self.newImage()
              time.sleep(sleep_time)
	     	
    def connectNotify(self, signal):
	if signal=="imageReceived":
            #self.__imagePolling = gevent.spawn(self._do_imagePolling, 40./1000.0)
            self.__imagePolling = gevent.spawn(self._do_imagePolling, self.getProperty("interval")/1000.0)
    def newImage(self):
	if self.video.getLive():
 	    image = self.video.getLastImage()
            qimage = None
	    if image.frameNumber() > -1:
      		raw_buffer = image.buffer()	
			
	        self.scaling.autoscale_min_max(raw_buffer,
                                          image.width(), image.height(),
                                          self.scalingType)
                validFlag, qimage = pixmaptools.LUT.raw_video_2_image(raw_buffer,
                                                                      image.width(), image.height(),
                                                                      self.scalingType,
                                                                      self.scaling)
		if validFlag:
                    #if self.camMirror is not None:
                        #qimage = qimage.mirror(self.camMirror[0], self.camMirror[1])     
   	            self.emit("imageReceived", qimage, qimage.width(), qimage.height(), self.forceUpdate)
   	            
def test2():
    #import os
    #from HardwareRepository import HardwareRepository, BaseHardwareObjects
    #hwr_directory = os.environ["XML_FILES_PATH"] 

    #print hwr_directory
    #hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
    #print 'hwr'
    #print hwr
    #hwr.connect()

    #lima = hwr.getHardwareObject("/limavideo")
    
    #lima.video.getLive()
    #image = self.video.getLastImage()
    #import scipy
    #print 'image'
    #print image
    
    #scipy.misc.imsave('/tmp/limaimage.png')
    lima = LimaVideo('prosilica')
    lima._init()
    lima.video.getLive()
    print 'lima.getWidth()', lima.getWidth()
    print 'lima.getHeight()', lima.getHeight()
    print 'lima.newImage()', lima.newImage()
    print 'lima.video.getLive()', lima.video.getLive()
    import scipy
    print 'image'
    image = lima.video.getLastImage()
    
    im = image.buffer()
    print im
    scipy.misc.imsave('/tmp/limaimage.png', im)
    
def test():
    import gevent
    from HardwareRepository.HardwareRepository import HardwareRepository as hdwrep
    import os
    hwr_directory = os.environ["XML_FILES_PATH"]

    print hwr_directory

    def imageReceived(image,width,height, force_update=False):
                print " got one image " ,width, height

    hwr = hdwrep(os.path.abspath(hwr_directory))
    hwr.connect()

    camera = hwr.getHardwareObject("/prosilica")
    camera.setLive(True)
    camera.connect("imageReceived", imageReceived)

    while True:
                gevent.wait(timeout=0.1)

if __name__ == '__main__':
    test()
