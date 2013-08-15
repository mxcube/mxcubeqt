import qt
import traceback
from Qub.Tools.QubThread import QubLock
from Qub.Tools.QubThread import QubThreadProcess
from Qub.CTools import pixmaptools

try:
    from Qub.CTools import qttools
except ImportError:
    qttools = None

try:
    from opencv import cv
    from Qub.CTools import opencv
except ImportError :
    cv = None
    opencv = None

import numpy
##@brief This class is use to decompress standard data -> image.
#data cant be (jpeg,tiff 8 bits...)
class QubStdData2Image(QubThreadProcess,qt.QObject) :
    STANDARD,BAYER_RG,RAW = (0,1,2)
    
    class _data_struct :
        PATH_TYPE,DATA_TYPE = range(2)
        def __init__(self) :
            self.type = QubStdData2Image._data_struct.DATA_TYPE
            self.path = None
            self.data = None
            self.inProcess = False
            self.end = False
            self.image = qt.QImage()
            
        def setPath(self,path) :
            self.type = QubStdData2Image._data_struct.PATH_TYPE
            self.path = path
            return self
        def setData(self,data) :
            self.type = QubStdData2Image._data_struct.DATA_TYPE
            self.data = data
            return self

        def loadFromData(self,data) :
            self.image.loadFromData(data)
            
    def __init__(self) :
        QubThreadProcess.__init__(self)
        qt.QObject.__init__(self)
        self.__plug = None
        self.__mutex = qt.QMutex()
        self.__dataPending = []
        self.__actif = False
        self.__postSetImage = []
        self.__swap = False
        self.__imageType = QubStdData2Image.STANDARD
        self.palette = pixmaptools.LUT.Palette(pixmaptools.LUT.Palette.GREYSCALE)
        
    def plug(self,plug):
        if isinstance(plug,QubStdData2ImagePlug) :
            aLock = QubLock(self.__mutex)
            self.__plug = plug
        else :
            raise StandardError('Must be a QubStdData2ImagePlug')

    ##@brief insert a data array in the decompress queues
    #@param data must be an array of a known type (jpeg,png...)
    def putData(self,data,width = -1,height = -1) :
        self.__append(data,None,width,height)
    ##@brief Insert a image path file in the decompress queues
    #@param path the full path of the image
    def putImagePath(self,path) :
        self.__append(None,path,-1,-1)
        
    
    def __append(self,arrayData,path,width,height) :
        aLock = QubLock(self.__mutex)
        if self.__plug is not None and not self.__plug.isEnd() :
            if self.__imageType == QubStdData2Image.STANDARD :
                dataStruct = QubStdData2Image._data_struct()
            elif self.__imageType == QubStdData2Image.BAYER_RG:
                dataStruct = _bayer_struct(width,height)
            else:
                try:
                    TangoString,HeaderVersion,videoType,width,height = struct.unpack('<16sq8sqq',arrayData[:48])
                    if videoType.upper().startswith('I420') :
                        dataStruct = _i420_struct(width,height)
                        arrayData = arrayData[64:]
                    elif videoType.upper().startswith('RGB24') :
                        arrayData = arrayData[64:]
                        dataStruct = _rgb_8_struct(width,height)
                        dataStruct.swapBand()
                    elif videoType.upper().startswith('BGR24') :
                        arrayData = arrayData[64:]
                        dataStruct = _rgb_8_struct(width,height)
                    elif videoType.upper().startswith('Y8'):
                        arrayData = arrayData[64:]
                        dataStruct = _mono8_struct(self,width,height)
                    elif videoType.upper().startswith('Y16') :
                        arrayData = arrayData[64:]
                        dataStruct = _mono16_struct(self,width,height)
                    elif videoType.upper().startswith('RGB565') :
                        arrayData = arrayData[64:]
                        dataStruct = _rgb565_struct(width,height)
                    elif videoType.upper().startswith('RGB555') :
                        arrayData = arrayData[64:]
                        dataStruct = _rgb555_struct(width,height)
                    else:
                        print 'VideoType: %s not managed' % videoType
                        return
                except struct.error:
                    import traceback
                    traceback.print_exc()
                    return
                
            if path is not None :
                dataStruct.setPath(path)
            else :
                dataStruct.setData(arrayData)
            if len(self.__dataPending) > 16 : # SIZE QUEUE LIMIT FLUSH PENDING
                self.__dataPending = [dataStruct] # TODO SEE IF WE CAN DO BETTER
            else:
                self.__dataPending.append(dataStruct)
            if not self.__actif :
                self.__actif = True
                aLock.unLock()
                self._threadMgr.push(self)

    def getFunc2Process(self) :
        aLock = QubLock(self.__mutex)
        aPendingDataNb = 0
        for dataStruct in self.__dataPending :
            if not dataStruct.inProcess :
                aPendingDataNb += 1
        if aPendingDataNb <= 1 :
            self.__actif = False
            aLock.unLock()
            self._threadMgr.pop(self,False)
        return self.__decompress
    
    def __decompress(self) :
        aLock = QubLock(self.__mutex)
        aWorkingStruct = None
        for dataStruct in self.__dataPending :
            if not dataStruct.inProcess :
                aWorkingStruct = dataStruct
                dataStruct.inProcess = True
                break
        swapFlag = self.__swap
        aLock.unLock()
        if aWorkingStruct is not None :
            try :
                if aWorkingStruct.type is QubStdData2Image._data_struct.DATA_TYPE :
                    aWorkingStruct.loadFromData(aWorkingStruct.data)
                else :
                    aWorkingStruct.image.load(aWorkingStruct.path)
                if swapFlag :
                    aWorkingStruct.image = aWorkingStruct.image.swapRGB()
                aLock.lock()
                aWorkingStruct.end = True
                if self.__plug is not None and not self.__plug.isEnd() :
                    removeDataStructs = []
                    for dataStruct in self.__dataPending :
                        if dataStruct.end :
                            self.__postSetImage.append(dataStruct.image)
                            removeDataStructs.append(dataStruct)
                        else :
                            break
                    for dataStruct in removeDataStructs :
                        self.__dataPending.remove(dataStruct)
                else :
                    self.__dataPending = []
            except :
                traceback.print_exc()
                self.__dataPending.remove(aWorkingStruct)
            aLock.unLock()
            #send event
            event = qt.QCustomEvent(qt.QEvent.User)
            event.event_name = "_postSetImage"
            qt.qApp.postEvent(self,event)
            
    def customEvent(self,event) :
        if event.event_name == "_postSetImage" :
            aLock = QubLock(self.__mutex)
            if self.__plug is not None and not self.__plug.isEnd() :
                plug = self.__plug
                images = self.__postSetImage[:]
                self.__postSetImage = []
                aLock.unLock()
                for image in images :
                    if plug.setImage(image,image) :
                        aLock.lock()
                        self.__plug = None
                        break
            else :
                self.__plug = None
                self.__postSetImage = []

    def setSwapRGB(self,aFlag) :
        aLock = QubLock(self.__mutex)
        self.__swap = aFlag
    ##@brief set the image type
    #
    #@param imageType can be STANDARD (qt Standard or BAYER_RG)
    def setImageType(self,imageType) :
        self.__imageType = imageType
        
##@brief this class link a Data image provider and
#a image manager
class QubStdData2ImagePlug :
    def __init__(self) :
        self.__endFlag = False
    def setEnd(self) :
        self.__endFlag = True
    def isEnd(self) :
        return self.__endFlag

    ##@brief This methode is call when an image is decompressed
    #@return boolean:
    # - if <b>True</b> end of the polling for the object link with
    # - else <b>False</b> keep in the polling loop
    #
    #@param image a qt.QImage
    def setImage(self,imagezoomed,fullimage) :
        return True                     # (END)

class _cvtColor_struct(QubStdData2Image._data_struct) :
    def __init__(self,w,h,conversionType,srcSize) :
        QubStdData2Image._data_struct.__init__(self)
        _type = {1:cv.CV_8UC1,2:cv.CV_8UC2,3:cv.CV_8UC3}
        self._srcImage = cv.cvCreateMat(h,w,_type[srcSize])
        self._destimage = cv.cvCreateMat(h,w,cv.CV_8UC3);
        self._widthStep = w
        self._conversion = conversionType
        
    def loadFromData(self,data) :
        self._srcImage.imageData = data
        cv.cvCvtColor(self._srcImage,self._destimage,self._conversion)
        self.image = opencv.qtTools.getQImageFromImageOpencv(self._destimage)

##@brief a decompress bayer class
#
class _bayer_struct(_cvtColor_struct) :
    def __init__(self,w,h) :
        _cvtColor_struct.__init__(self,w,h,cv.CV_BayerRG2RGB,1)

import struct

##@brief a decompress i420 class
#
class _i420_struct(QubStdData2Image._data_struct) :
    def __init__(self,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h
        
    def loadFromData(self,data) :
        self.image = opencv.qtTools.convertI420Data2YUV(data,self.__width,self.__height)
    

##@brief a decompress rgb 8 bits
#
class _rgb_8_struct(QubStdData2Image._data_struct) :
    def __init__(self,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h
        self.__swap = False
        
    def swapBand(self) :
        self.__swap = True
        
    def loadFromData(self,data) :
        destimage = cv.cvCreateImage(cv.cvSize(self.__width,self.__height),cv.IPL_DEPTH_8U,3)
        destimage.imageData = data
        self.image = opencv.qtTools.getQImageFromImageOpencv(destimage)
        if self.__swap:
            self.image = self.image.swapRGB()
        

##@brief a decompress mono 8 bits
#
class _mono8_struct(QubStdData2Image._data_struct) :
    def __init__(self,cnt,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h
        self.__palette = cnt.palette
        
    def loadFromData(self,data) :
        array = numpy.fromstring(data,dtype=numpy.uint8)
        array.shape = self.__height,self.__width
        try:
            self.image,(minVal,maxVal) = pixmaptools.LUT.map_on_min_max_val(array,self.__palette,pixmaptools.LUT.LINEAR)
        except pixmaptools.LutError,err:
            print err.msg()
            return
        
##@brief a decompress mono 16 bits
#
class _mono16_struct(QubStdData2Image._data_struct) :
    def __init__(self,cnt,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h
        self.__palette = cnt.palette
        
    def loadFromData(self,data) :
        array = numpy.fromstring(data,dtype=numpy.uint16)
        array = array.byteswap()
        array.shape = self.__height,self.__width
        try:
            self.image,(minVal,maxVal) = pixmaptools.LUT.map_on_min_max_val(array,self.__palette,pixmaptools.LUT.LINEAR)
        except pixmaptools.LutError,err :
            print err.msg()
            return
        
##@brief a decompress RGB565
#
class _rgb565_struct(QubStdData2Image._data_struct) :
    def __init__(self,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h

    def loadFromData(self,data) :
        self.image = qttools.QubImage(qttools.QubImage.RGB565,
                                      self.__width,self.__height,
                                      data)
    
##@brief a decompress RGB555
#
class _rgb555_struct(QubStdData2Image._data_struct) :
    def __init__(self,w,h) :
        QubStdData2Image._data_struct.__init__(self)
        self.__width = w
        self.__height = h

    def loadFromData(self,data) :
        self.image = qttools.QubImage(qttools.QubImage.RGB555,
                                      self.__width,self.__height,
                                      data)
    
