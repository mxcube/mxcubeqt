import itertools
import weakref
import qt

from Qub.Tools.QubThread import QubLock
from Qub.Tools.QubThread import QubThreadProcess
from Qub.CTools import datafuncs
from Qub.CTools import pixmaptools

##@brief This class manage the transform RawData to QImage
#
#This is an effecient way to transforme a RawData like shared memory to a image.
#
class QubRawData2Image(qt.QObject) :
    def __init__(self) :
        qt.QObject.__init__(self)
        self.__plugs = []
        self.__mutex = qt.QMutex()
        self.__PrevData = None
        self.__dataZoomProcess = _DataZoomProcess(self)
        self.__sendPending = []

    ##@brief the link between QubRawData2Image and other object which manage QImage
    #@see Qub::Objects::QubImage2Pixmap::QubImage2Pixmap
    #@param aPlug must be inherited from QubRawData2ImagePlug
    def plug(self,aPlug) :
        if isinstance(aPlug,QubRawData2ImagePlug) :
            aLock = QubLock(self.__mutex)
            aPlug.setManager(self)
            self.__plugs.append(aPlug)
        else:
            raise StandardError('Must be a QubRawData2ImagePlug')

    def getPlugs(self) :
        aLock = QubLock(self.__mutex)
        return list(self.__plugs)
    ##@brief add a raw data in the pending queue
    #
    #For all data zoom and colormap is done in a thread
    def putRawData(self,data) :
        aLock = QubLock(self.__mutex)
        self.__PrevData = data
        if self.__plugs :
            aLock.unLock()
            self.__dataZoomProcess.putRawData(data)

       
    ##@brief need a refresh for some reason
    def refresh(self) :
        aLock = QubLock(self.__mutex)
        data = self.__PrevData
        aLock.unLock()
        self.__dataZoomProcess.putRawData(data)

    def extendSendList(self,fullimageNPlugs) :
        aLock = QubLock(self.__mutex)
        self.__sendPending.extend(fullimageNPlugs)
        aLock.unLock()
        event = qt.QCustomEvent(qt.QEvent.User)
        event.event_name = "_postSetImage"
        qt.qApp.postEvent(self,event)
                
    ##@brief it use for the communication between the main thread and other
    #@todo the methode is needed by QT3 because it's not MT-Safe,
    #it's could be remove when QT4 will be used
    def customEvent(self,event) :
        try:
            if event.event_name == "_postSetImage" :
                aLock = QubLock(self.__mutex)
                pendingSend = list(self.__sendPending)
                self.__sendPending = []
                aLock.unLock()
                for fullimage,plugNImage in pendingSend :
                    for plug,image in plugNImage:
                        if not plug.isEnd() :
                            if plug.setImage(image,fullimage) :
                                aLock.lock()
                                try:
                                    self.__plugs.remove(plug)
                                except: pass
                                aLock.unLock()
                        else:
                            aLock.lock()
                            try:
                                self.__plugs.remove(plug)
                            except: pass
                            aLock.unLock()
        except:
            import traceback
            traceback.print_exc()
##@brief this class is the link between QubRawData2Image and
#other diplay pixmap object
#
#You Have to derivate this class for specific needs.
#@see setPixmap
#
class QubRawData2ImagePlug:
    ##@brief the Zoom class
    #
    class Zoom :
        def __init__(self,cnt) :
            self.__cnt = weakref.ref(cnt)
            self.__zoom = (1,1)
            self.__ox,self.__oy = (0,0)
            self.__width,self.__height = (0,0)
            self.__allimage = True
            self.__mutex = qt.QMutex()
        ##@return the horizontal and vertical zoom as a tuple
        def zoom(self) :
            aLock = QubLock(self.__mutex)
            return self.__zoom
        ##@brief set the horizontal and vertical zoom
        #@param zoomx horizontal zoom
        #@param zoomy vertical zoom
        #@param keepROI :
        # - if <b>False</b> the pixmap will be zoomed on the full image
        # - else <b>True</b> the pixmap will be zoomed with the ROI previously set
        #
        #@see setRoiNZoom
        def setZoom(self,zoomx,zoomy,keepROI = False) :
            aLock = QubLock(self.__mutex)
            if self.__zoom != (zoomx,zoomy) :
                self.__zoom = (zoomx,zoomy)
                self.__allimage = not keepROI
                aLock.unLock()
                cnt = self.__cnt()
                if cnt:  cnt.refresh()
        ##@brief set the ROI and the zoom
        #
        #the pixmap will be zoomed using the ROI and horizontal and vertical zoom
        #@param ox left point of the ROI
        #@param oy top point of the ROI
        #@param width the width of the ROI
        #@param height the height of the ROI
        #@param zoomx horizontal zoom
        #@param zoomy vertical zoom
        def setRoiNZoom(self,ox,oy,width,height,zoomx,zoomy) :
            aLock = QubLock(self.__mutex)
            self.__allimage = False
            self.__ox,self.__oy,self.__width,self.__height = (ox,oy,width,height)
            self.__zoom = (zoomx,zoomy)
            aLock.unLock()
            cnt = self.__cnt()
            if cnt:
                cnt.refresh()
        ##@return if zoom is with ROI or not
        def isRoiZoom(self) :
            return not self.__allimage
        ##@return the ROI as a tuple (left,top,with,height)
        def roi(self) :
            aLock = QubLock(self.__mutex)
            return (self.__ox,self.__oy,self.__width,self.__height)
                ##@name Internal called

        #@warning don't called those methode directly
        #@{
        #
        
        #@return if the pixmap need to be zoomed
        def needZoom(self) :
            aLock = QubLock(self.__mutex)
            return not self.__allimage or self.__zoom != (1,1)

        ##@}
        #
        #
    ##@brief the Colormap class
    class Colormap:
        def __init__(self,cnt) :
            self.__lutType = pixmaptools.LUT.LINEAR
            self.__palette = pixmaptools.LUT.Palette(pixmaptools.LUT.Palette.GREYSCALE)
            self.__colorMapType = pixmaptools.LUT.Palette.GREYSCALE
            self.__autoscale = True
            self.__min = 0
            self.__max = 255
            self.__minMappingMethode = 0
            self.__maxMappingMethode = 255
            self.__mutex = qt.QMutex()

        ##@return min max as a tuple
        def minMax(self) :
            aLock = QubLock(self.__mutex)
            return (self.__min,self.__max)
        ##@return min max calculeted by the lut
        def minMaxMappingMethode(self) :
            aLock = QubLock(self.__mutex)
            return (self.__minMappingMethode,self.__maxMappingMethode)
        ##@brief set the min max value of data for the lookup table
        def setMinMax(self,minValue,maxVlaue) :
            aLock = QubLock(self.__mutex)
            self.__min = minValue
            self.__max = maxVlaue
        ##@brief set the min max value of the mapping lut methode
        def setMinMaxMappingMethode(self,minVal,maxVal) :
            aLock = QubLock(self.__mutex)
            self.__minMappingMethode = minVal
            self.__maxMappingMethode = maxVal
        ##return True if autoscale is On
        def autoscale(self) :
            aLock = QubLock(self.__mutex)
            return self.__autoscale
        ##@brief set autoscale on/off
        def setAutoscale(self,aFlag) :
            aLock = QubLock(self.__mutex)
            self.__autoscale = aFlag

        ##@return enum spslut colormap  type
        #
        #@see setColorMapType
        def colorMapType(self) :
            aLock = QubLock(self.__mutex)
            return self.__colorMapType
        ##@brief set the colormap type
        #
        #@param aColormapType is a enum from pixmaptools.LUT.Palette, value can be:
        # - pixmaptools.LUT.Palette.GREYSCALE
        # - pixmaptools.LUT.Palette.REVERSEGREY
        # - pixmaptools.LUT.Palette.TEMP
        # - pixmaptools.LUT.Palette.RED
        # - pixmaptools.LUT.Palette.GREEN
        # - pixmaptools.LUT.Palette.BLUE
        # - pixmaptools.LUT.Palette.MANY
        def setColorMapType(self,aColormapType) :
            aLock = QubLock(self.__mutex)
            self.__colorMapType = aColormapType
            self.__palette.fillPalette(aColormapType)

        ##@return lut type
        #@see setLutType
        def lutType(self) :
            aLock = QubLock(self.__mutex)
            return self.__lutType
        ##@brief set the lut type mapping
        #
        #@param lutType is an enum from pixmaptools.LUT, value can be:
        # - pixmaptools.LUT.LINEAR
        # - pixmaptools.LUT.SHIFT_LOG
        # - pixmaptools.LUT.LOG
        def setLutType(self,lutType) :
            aLock = QubLock(self.__mutex)
            self.__lutType = lutType

        ##@brief get the palette object
        #
        def palette(self) :
            return self.__palette
            
    ##@brief constuctor
    def __init__(self) :
        self.__endFlag = False
        self._zoom = QubRawData2ImagePlug.Zoom(self)
        self._colormap = QubRawData2ImagePlug.Colormap(self)
        self._mgr = None
        self.__fullData,self.__resizedData = None,None
        self.__mutex = qt.QMutex()
    ##@brief get the zoom class
    #@return QubRawData2ImagePlug::Zoom
    #
    def zoom(self) :
        return self._zoom
    ##@brief get the colormap class
    #@return QubRawData2ImagePlug::Colormap
    #
    def colormap(self) :
        return self._colormap
    ##@return full and resized data as a tuple
    def data(self) :
        aLock = QubLock(self.__mutex)
        return self.__fullData,self.__resizedData
    ##@brief This methode is call when an lookup and zoom is done on data
    #
    #You have to redefined it in inherited class
    #@return stop flag:
    # - if <b>True</b>: the plug will be removed from every polling,
    #the object won't be called again util you replug
    # - else <b>False</b>: this wont be unplug
    #
    #@param pixmap the zoomed pixmap
    #@param image the full image
    def setImage(self,imagezoomed,fullimage) :
        return True
    ##@brief need a pixmap refresh
    def refresh(self) :
        if self._mgr:
            mgr = self._mgr()
            mgr.refresh()

    ##@brief this is the end ... of the plug. after this call, the plug will be removed from every polling.
    def setEnd(self) :
        self.__endFlag = True

    ##@return if the plug have to be remove from the polling
    def isEnd(self) :
        return self.__endFlag

    ##@brief set the container of this plug
    #@param aMgr actually is a QubRawData2Image
    def setManager(self,aMgr) :
        self._mgr = weakref.ref(aMgr)
    ##@brief set data
    #
    def setData(self,fData,rData) :
        aLock = QubLock(self.__mutex)
        self.__fullData = fData
        self.__resizedData = rData
#PRIVATE
class _DataZoomProcess(QubThreadProcess) :
    class _process_struct :
        def __init__(self,data) :
            self.data = data
            self.inProgress = False
            self.end = False
            self.fullImageNplugNImage = None
            
    def __init__(self,cnt) :
        QubThreadProcess.__init__(self)
        self.__cnt = weakref.ref(cnt)
        self.__mutex = qt.QMutex()
        self.__cond = qt.QWaitCondition()
        self.__actif = False
        self.__dataProcessPending = None
        self.__InProgress = []

    def getFunc2Process(self) :
        aLock = QubLock(self.__mutex)
        self.__InProgress.append(_DataZoomProcess._process_struct(self.__dataProcessPending))
        self.__dataProcessPending = None
        self.__cond.wakeOne()
        self.__actif = False
        aLock.unLock()
        self._threadMgr.pop(self,False)
        return self.dataProcess

    def putRawData(self,aData) :
        aLock = QubLock(self.__mutex)
        self.__dataProcessPending = aData
        if not self.__actif :
            self.__actif = True
            aLock.unLock()
            self._threadMgr.push(self)
            
    def dataProcess(self) :
        try:
            cnt = self.__cnt()
            if cnt:
                plugs = cnt.getPlugs()
                aLock = QubLock(self.__mutex)
                struct = None
                for s in self.__InProgress :
                    if not s.inProgress :
                        s.inProgress = True
                        struct = s
                        break
                aLock.unLock()
                fullImage = None
                plugNImage = []
                for plug in plugs:
                    if not plugs: continue
                    zoom = plug.zoom()
                    dataArray = s.data
                    if dataArray is not None:
                        if zoom.needZoom() :
                            xzoom,yzoom = zoom.zoom()
                            if xzoom < 1. or yzoom < 1.:
                                if xzoom > 1. : xzoom = 1.
                                if yzoom > 1. : yzoom = 1.
                                if zoom.isRoiZoom():
                                    ox,oy,width,height = zoom.roi()
                                    dataArray = datafuncs.down_size(s.data,ox,oy,width,height,xzoom,yzoom)
                                else:
                                    height,width = s.data.shape
                                    dataArray = datafuncs.down_size(s.data,0,0,width,height,xzoom,yzoom)
                            elif zoom.isRoiZoom() :
                                x,y,width,height = zoom.roi()
                                if x < 0:
                                    width += x
                                    x = 0
                                if y < 0 :
                                    height += y
                                    y = 0
                                dataArray = dataArray[y:y+height,x:x+width]

                        colormap = plug.colormap()
                        try:
                            if colormap.autoscale() :
                                image ,(minVal,maxVal) = pixmaptools.LUT.map_on_min_max_val(dataArray,colormap.palette(),
                                                                                            colormap.lutType())
                                colormap.setMinMaxMappingMethode(minVal,maxVal)
                            else:
                               image,(minVal,maxVal) = pixmaptools.LUT.map(dataArray,colormap.palette(),
                                                                           colormap.lutType(),*colormap.minMax())
                        except pixmaptools.LutError,err :
                            print err.msg()
                            return
                        if zoom.needZoom() :
                            xzoom,yzoom = zoom.zoom()
                            if xzoom > 1. or yzoom > 1. :
                                if xzoom < 1. : xzoom = 1.
                                if yzoom < 1. : yzoom = 1.
                                width,height = image.width(),image.height()
                                width *= xzoom
                                height *= yzoom
                                if fullImage is None and not zoom.isRoiZoom(): fullImage = image
                                # limit (we enter in this case usually we a fit to screen is ask and
                                #when you switch to a bigger image
                                if((xzoom > 5 or yzoom > 5) and
                                   (width > 4096 or height > 4096)) :
                                    image = image
                                else:
                                    image = image.scale(width,height)
                        if fullImage is None and not zoom.needZoom() :
                            fullImage = image
                    else:
                        image,fullImage = qt.QImage(),qt.QImage()
                    plug.setData(s.data,dataArray)
                    plugNImage.append((plug,image))

                if fullImage is None and plugs :
                    plug = plugs[0]
                    colormap = plug.colormap()
                    fullImage,(minVal,maxVal) = pixmaptools.LUT.map(s.data,colormap.palette(),
                                                                    colormap.lutType(),*colormap.minMax())
                aLock.lock()
                struct.end = True
                tmplist = []
                s.fullImageNplugNImage = (fullImage,plugNImage)
                lastid = 0
                if struct == self.__InProgress[0] :
                    for i,s in enumerate(self.__InProgress) :
                        if s.end :
                            tmplist.append(s.fullImageNplugNImage)
                            lastid = i
                        else: break
                    self.__InProgress[0:lastid + 1] = []
                aLock.unLock()

                if tmplist:
                    cnt.extendSendList(tmplist)
        except:
            import traceback
            traceback.print_exc()
