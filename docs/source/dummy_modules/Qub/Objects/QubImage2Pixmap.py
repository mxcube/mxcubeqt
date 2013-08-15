import weakref
import new
import qt
if __name__ == "__main__":              # TEST
    a = qt.QApplication([])

from Qub.CTools import pixmaptools

from Qub.Tools.QubThread import QubLock
from Qub.Tools.QubThread import QubThreadProcess

#try:
#    from opencv import cv
#    from Qub.CTools.opencv import qtTools
#except ImportError:
#    cv = None

# No more try to import opencv module : API has changed ?
# Let qt do the job.
cv = None


##@brief This class manage the copy between QImage and QPixmap
#
#This is an effecient way to transforme a QImage to a QPixmap
#@see QImage
#@see QPixmap
class QubImage2Pixmap(qt.QObject) :
    ##@brief idle transformation of image to pixmap
    #
    #every tranformation is done with this idle to be on the rythm of
    #the computer
    class _Idle(qt.QTimer) :
        ##@param cnt is in fact QubImage2Pixmap
        ##@param skipSmooth:
        # - if <b>True</b>: the image skip try to be smooth
        # - else <b>False</b>: skip all image and take the last
        def __init__(self,cnt,skipSmooth) :
            qt.QTimer.__init__(self)
            self.connect(self,qt.SIGNAL('timeout()'),self.__idleCopy)
            self.__plugsNimagesPending = []
            self.__plugs = []
            self.__skipSmooth = skipSmooth
            self.__mutex = qt.QMutex()
            self.__PrevImageNeedZoom = None
            self.__imageZoomProcess = _ImageZoomProcess(self)
            self.__cnt = weakref.ref(cnt)

        ##@brief the link between QubImage2Pixmap and an other object which display Pixmap
        #@see Qub::Objects::QubPixmapDisplay::QubPixmapDisplay
        #@param aPlug must be inherited from QubImage2PixmapPlug
        def plug(self,aPlug) :
            if isinstance(aPlug,QubImage2PixmapPlug) :
                aLock = QubLock(self.__mutex)
                aPlug.setManager(self)
                self.__plugs.append(aPlug)
            else :
                raise StandardError('Must be a QubImage2PixmapPlug')
        ##@return the plug object inherited from QubImage2PixmapPlug
        def getPlugs(self) :
            aLock = QubLock(self.__mutex)
            return list(self.__plugs)
        ##@return get the Last images zoomedImage and fullImage
        #
        def getLastImages(self) :
            return self.__PrevImageNeedZoom
        ##@brief add an image in the pending stack
        #
        #All image are transformed to Pixmap asynchronously, there is two way:
        # -# if a client asked a zoom, the image is pushed in a zoom task list.
        #    those image are zoomed in a thread
        # -# if a client just want to display full image, the task is pushed in the display
        #    stack
        def putImage(self,images,aLockFlag = True) :
            zoomedImage,fullimage = images
            aLock = QubLock(self.__mutex,aLockFlag)
            if len(self.__plugs) :
                needZoomFlag = False
                for plug in self.__plugs :
                    zoom = plug.zoom()
                    if zoom.needZoom():
                        needZoomFlag = True
                        break
                self.__PrevImageNeedZoom = (zoomedImage,fullimage)
                if needZoomFlag :
                    self.__imageZoomProcess.putImage((zoomedImage,fullimage))
                else :
                    self.__plugsNimagesPending.append([(plug,zoomedImage,fullimage) for plug in self.__plugs])
                    aLock.unLock()
                    self.__startIdle()

        ##@brief add an image in the pending display stack
        def appendPendingList(self,aList) :
            aLock = QubLock(self.__mutex)
            self.__plugsNimagesPending.append(aList)
            aLock.unLock()
            self.__startIdle()
            

        ##@brief need a refresh for somme reason
        def refresh(self) :
            try:
                aLock = QubLock(self.__mutex)
                needzoom = False
                for plug in self.__plugs :
                    zoom = plug.zoom()
                    if zoom.needZoom():
                        needzoom = True
                        break
                previmage = self.__PrevImageNeedZoom
                if previmage is not None :
                    if needzoom and previmage != self.__imageZoomProcess.lastImagePending() :
                        self.__imageZoomProcess.putImage(previmage)
                    elif not needzoom :
                        if not len(self.__plugsNimagesPending) :
                            self.putImage(previmage,False)
            except:
                import traceback
                traceback.print_exc()
                
        ##@brief this methode is the idle callback
        def __idleCopy(self) :
            self.copy()
            aLock = QubLock(self.__mutex)
            if not len(self.__plugsNimagesPending) :
                aLock.unLock()
                self.stop()
        
        ##@brief copy image on a pixmap
        def copy(self) :
            aLock = QubLock(self.__mutex)
            self.__plugsNimagesPending = self.decim(self.__plugsNimagesPending)
            if len(self.__plugsNimagesPending) :
                plugsNimages = self.__plugsNimagesPending.pop(0)
                aLock.unLock()
                for plug,image,fullSizeImage in plugsNimages :
                    if not plug.isEnd() :
                        pixmap = plug.zoom().getPixmapFrom(image)
                        if plug.setPixmap(pixmap,fullSizeImage) :
                            aLock.lock()
                            try:
                                for pni in self.__plugsNimagesPending :
                                    for tmpplug,ti,fi in pni :
                                        if tmpplug == plug :
                                            pni.remove((tmpplug,ti,fi))
                                self.__plugs.remove(plug)
                            except:
                                pass
                            aLock.unLock()
                    else :
                        aLock.lock()
                        try:
                            for pni in self.__plugsNimagesPending :
                                for tmpplug,ti,fi in pni :
                                    if tmpplug == plug :
                                        pni.remove((tmpplug,ti,fi))
                            self.__plugs.remove(plug)
                        except:
                            pass
                        aLock.unLock()
                            
        ##@brief send a custom event to start the timer
        #@todo in Qt4 remove the event and replace this fct by the curent customEvent
        def __startIdle(self) :
            if not self.isActive() :
                #send event
                event = qt.QCustomEvent(qt.QEvent.User)
                event.event_name = "_startTimer"
                cnt = self.__cnt()
                if cnt :
                    qt.qApp.postEvent(cnt,event)
                    
        ##@brief decimation algorithm
        #
        #this methode has two way of decimation :
        # -# a smooth one decim 1/5 image in a task list
        # -# skip all except the last
        def decim(self,l) :
            lenght = len(l)
            if self.__skipSmooth  and lenght < 25 : # (<25 -> stream is up to 4x)
                nbSkip = lenght / 5
                for x in xrange(nbSkip) :
                    l.pop(0)
            elif lenght > 1 :                      # last
                l = l[-1:]
            return l

    ##@brief constructor
    def __init__(self,skipSmooth = True) :
        qt.QObject.__init__(self)
        self.__idle = QubImage2Pixmap._Idle(self,skipSmooth)

    ##@brief Asynchronous Image Put, the copy to pixmap will be made on idle
    def putImage(self,imageZoomed,fullimage) :
        self.__idle.putImage((imageZoomed,fullimage))

    ##@brief link the object to an other one which can display pixmap
    def plug(self,aQubImage2PixmapPlug) :
        self.__idle.plug(aQubImage2PixmapPlug)
    ##@brief it use for the communication between the main thread and other
    #@todo the methode is needed by QT3 because it's not MT-Safe,
    #it's could be remove when QT4 will be used
    def customEvent(self,event) :
        if event.event_name == "_startTimer" and not self.__idle.isActive():
            self.__idle.copy()

##@brief this class is the link between QubImage2Pixmap and
#other object which can display Pixmap
#
#You have to derivate this class for specific needs.
#@see setPixmap
#
class QubImage2PixmapPlug :
    ##@brief the Zoom class containt two Pixmap for a soft double buffer
    #
    #on inherited class, you can set the interpolation. default is CV_INTER_LINEAR (bilinear interpolation)
    class Zoom :
        def __init__(self,cnt) :
            self.__cnt = weakref.ref(cnt)
            self.__zoom = (1,1)
            self.__ox,self.__oy = (0,0)
            self.__width,self.__height = (0,0)
            self.__allimage = True
            self.__mutex = qt.QMutex()
            if cv is not None :
                self._interpolation = cv.CV_INTER_LINEAR #CV_INTER_CUBIC
                self.__interpolationInUse = self._interpolation
            
            self.__pixmapIO = [pixmaptools.IO(),pixmaptools.IO()]
            self.__pixmapbuffer = [qt.QPixmap(),qt.QPixmap()]
            self.__bufferId = 0
            for buffer in self.__pixmapIO :
                buffer.setShmPolicy(pixmaptools.IO.ShmKeepAndGrow)
        ##@retun the horizontal and vertical zoom as a tuple
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
            try:
                aLock = QubLock(self.__mutex)
                if self.__zoom != (zoomx,zoomy) :
                    self.__zoom = (zoomx,zoomy)
                    self.__allimage = not keepROI
                    aLock.unLock()
                    cnt = self.__cnt()
                    if cnt:
                        cnt.refresh()
            except:
                import traceback
                traceback.print_exc()
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
            if cv is not None:
                if self.__zoom < (1,1) :
                    self.__interpolationInUse = cv.CV_INTER_NN
                else :
                    self.__interpolationInUse = self._interpolation
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
            return self.__zoom != (1,1)
        ##@brief this methode zoom image
        #
        #by using opencv library.
        #@param imageOpencv is an opencv image
        #@return a QImage zoomed 
        def getZoomedImage(self,imageOpencv) :
            aLock = QubLock(self.__mutex) # LOCK
            width = imageOpencv.width
            height = imageOpencv.height
            if not self.__allimage :
                width = self.__width
                height = self.__height

            width *= self.__zoom[0]
            height *= self.__zoom[1]
            width = int(width)
            height = int(height)
            #oldroi = imageOpencv.roi
	    oldroi = None
            roiX,roiY,roiWidth,roiHeight = (0,0,0,0)
            if oldroi is not None :
                roiX,roiY,roiWidth,roiHeight = (oldroi.xOffset,oldroi.yOffset,oldroi.width,oldroi.height)

            if self.__allimage :
                if oldroi is not None :
                    cv.cvResetImageROI(imageOpencv)
            else:
                cv.cvSetImageROI(imageOpencv,cv.cvRect(self.__ox,self.__oy,self.__width,self.__height))
            aLock.unLock()              # UNLOCK

            destImage = cv.cvCreateImage(cv.cvSize(width,max(1,height)),imageOpencv.depth,imageOpencv.nChannels)

            cv.cvResize(imageOpencv,destImage,self.__interpolationInUse)

            zoomedImage = qtTools.getQImageFromImageOpencv(destImage)

            if oldroi is not None :
                cv.cvSetImageROI(imageOpencv,cv.cvRect(roiX,roiY,roiWidth,roiHeight))
            elif not self.__allimage :
                cv.cvResetImageROI(imageOpencv)
            return zoomedImage
        ##@brief this methode zoom image (link the above fct)
        #
        #by using only qt library (slower than the above one)
        #@param qtimage a full image (Qt)
        #@return a QImage zoomed
        def getZoomedQtImage(self,qimage) :
            aLock = QubLock(self.__mutex) # LOCK
            if not self.__allimage:
                width = self.__width
                height = self.__height
            else:
                width = qimage.width()
                height = qimage.height()

            width *= self.__zoom[0]
            height *= self.__zoom[1]
            width = int(width)
            height = int(height)

            if not self.__allimage:
                returnImage = qimage.copy(self.__ox,self.__oy,self.__width,self.__height)
            else:
                returnImage = qimage
            
            return returnImage.smoothScale(width,height)
            

        ##@return the zoomed pixmap
        def getPixmapFrom(self,zoomedImage) :
            pixmapbuffer = self.__pixmapbuffer[self.__bufferId % len(self.__pixmapbuffer)]
            pixmapIO = self.__pixmapIO[self.__bufferId % len(self.__pixmapIO)]
            self.__bufferId += 1

            if(pixmapbuffer.width() != zoomedImage.width() or
               pixmapbuffer.height() != zoomedImage.height()) :
                pixmapbuffer.resize(zoomedImage.width(),zoomedImage.height())
            cnt = self.__cnt()
            if cnt and cnt.viewportPosNSize:
                x,y,vpWidth,vpHeight = cnt.viewportPosNSize
                imWidth,imHeight = zoomedImage.width(),zoomedImage.height()
                imWidth -= x
                imHeight -= y
                imageCopy = zoomedImage.copy(x,y,min(vpWidth,imWidth),min(vpHeight,imHeight))
            else:
                x,y = 0,0
                imageCopy = zoomedImage
                
            pixmapIO.putImage(pixmapbuffer,x,y,imageCopy)
            
            return pixmapbuffer
        ##@}
        #
        #

    ##@brief constuctor
    def __init__(self) :
        self.__endFlag = False
        self._zoom = QubImage2PixmapPlug.Zoom(self)
        self._mgr = None
        self.viewportPosNSize = None
        
    ##@brief get the zoom class
    #@return QubImage2PixmapPlug::Zoom
    #
    def zoom(self) :
        return self._zoom
    
    ##@brief This methode is call when an image is copied on pixmap
    #
    #You have to redefined it in inherited class
    #@return stop flag:
    # - if <b>True</b>: the plug will be removed from every polling,
    #the object won't be called again util you replug
    # - else <b>False</b>: this wont be unplug
    #
    #@param pixmap the zoomed pixmap
    #@param image the full image
    def setPixmap(self,pixmap,image) :
        return True
    ##@brief need a pixmap refresh
    def refresh(self) :
        if self._mgr:
            mgr = self._mgr()
            if mgr:
                mgr.refresh()
    ##@brief this is the end ... of the plug. after this call, the plug will be removed from every polling.
    def setEnd(self) :
        self.__endFlag = True

    ##@return if the plug have to be remove from the polling
    def isEnd(self) :
        return self.__endFlag
    ##@brief set the container of this plug
    #@param aMgr actually is a QubPixmapDisplay
    def setManager(self,aMgr) :
        self._mgr = weakref.ref(aMgr)

    ##@brief viewport callback
    #
    #optimisation for the pixmap copy
    def setViewPortPoseNSize(self,x,y,width,height) :
        self.viewportPosNSize = (x,y,width,height)
        if self._mgr :
            mgr = self._mgr()
            if mgr:
                try:
                    zoomedImage,fullimage = mgr.getLastImages()
                    pixmap = self.zoom().getPixmapFrom(zoomedImage)
                    self.setPixmap(pixmap,fullimage)
                except TypeError: pass
#Private


class _ImageZoomProcess(QubThreadProcess):
    class _process_struct :
        def __init__(self,image) :
            self.image,self.fullimage = image
            self.plugNimage = []
            self.inProgress = False
            self.end = False
            
    def __init__(self,cnt) :
        QubThreadProcess.__init__(self)
        self.__end = False
        self.__cnt = weakref.ref(cnt)
        self.__mutex = qt.QMutex()
        self.__actif = False
        self.__imageZoomPending = []
        self.__InProgress = []
        if cv is None :
            self.zoomProcess = new.instancemethod(_ImageZoomProcess.__zoomProcess_qt.im_func, self, _ImageZoomProcess)
        else:
            self.zoomProcess = new.instancemethod(_ImageZoomProcess.__zoomProcess_opencv.im_func, self, _ImageZoomProcess)
        
       
    def getFunc2Process(self) :
        try:
            aLock = QubLock(self.__mutex)
            cnt = self.__cnt()
            if cnt:
                self.__imageZoomPending = cnt.decim(self.__imageZoomPending)
                self.__InProgress.append(_ImageZoomProcess._process_struct(self.__imageZoomPending.pop(0)))
                if not len(self.__imageZoomPending) :
                    self.__actif = False
                    aLock.unLock()
                    self._threadMgr.pop(self,False)
            else:
                self._threadMgr.pop(self,False)
            return self.zoomProcess
        except:
            import traceback
            traceback.print_exc()

    def lastImagePending(self) :
        aLock = QubLock(self.__mutex)
        lastImagePending = None
        if len(self.__imageZoomPending) :
            lastImagePending = self.__imageZoomPending[-1]
        return lastImagePending
    
    def putImage(self,image) :
        try:
            aLock = QubLock(self.__mutex)
            self.__imageZoomPending.append(image)
            if not self.__actif :
                self.__actif = True
                aLock.unLock()
                self._threadMgr.push(self)
        except:
            import traceback
            traceback.print_exc()

    def __zoomProcess_opencv(self) :
        cnt = self.__cnt()
        if not cnt: return
        
        plugs = cnt.getPlugs()
        aLock = QubLock(self.__mutex)
        struct = None
        for s in self.__InProgress :
            if not s.inProgress :
                s.inProgress = True
                struct = s
                break
        aLock.unLock()

        imageOpencv = qtTools.getImageOpencvFromQImage(struct.image)
                
        for plug in plugs :
            zoom = plug.zoom()
            if zoom.needZoom() :
                try:
                    imageZoomed = zoom.getZoomedImage(imageOpencv)
                    struct.plugNimage.append((plug,imageZoomed,struct.fullimage))
                except:
                    import traceback
                    traceback.print_exc()

            else :
                struct.plugNimage.append((plug,struct.image,struct.fullimage))

        aLock.lock()
        struct.end = True
        tmplist = []
        if struct == self.__InProgress[0] :
            lastid = 0
            for i,s in enumerate(self.__InProgress) :
                if s.end :
                    tmplist.append(s.plugNimage)
                    lastid = i
                else:
                    break
            self.__InProgress[0:lastid + 1] = []
        aLock.unLock()
        for plugnimage in tmplist:
            cnt.appendPendingList(plugnimage)

    def __zoomProcess_qt(self) :
        try:
            cnt = self.__cnt()
            if not cnt: return

            plugs = cnt.getPlugs()
            aLock = QubLock(self.__mutex)
            struct = None
            for s in self.__InProgress :
                if not s.inProgress :
                    s.inProgress = True
                    struct = s
                    break
            aLock.unLock()

            for plug in plugs :
                zoom = plug.zoom()
                if zoom.needZoom() :
                    try:
                        imageZoomed = zoom.getZoomedQtImage(struct.image)
                        struct.plugNimage.append((plug,imageZoomed,struct.fullimage))
                    except:
                        import traceback
                        traceback.print_exc()

                else :
                    struct.plugNimage.append((plug,struct.image,struct.fullimage))

            aLock.lock()
            struct.end = True
            tmplist = []
            if struct == self.__InProgress[0] :
                lastid = 0
                for i,s in enumerate(self.__InProgress) :
                    if s.end :
                        tmplist.append(s.plugNimage)
                        lastid = i
                    else:
                        break
                self.__InProgress[0:lastid + 1] = []
            aLock.unLock()
            for plugnimage in tmplist:
                cnt.appendPendingList(plugnimage)
        except:
            import traceback
            traceback.print_exc()

            
                         ####### TEST #######
if __name__ == "__main__":
    class Image2Pixmap(QubImage2PixmapPlug) :
        def __init__(self,label) :
            QubImage2PixmapPlug.__init__(self)
            self.__label = label
                        
        def setPixmap(self,pixmap,image) :
            self.__label.setPixmap(pixmap)
            return False
        
    import os
    import os.path
    class PutImageTimer(qt.QTimer) :
        def __init__(self,pixmapMgr) :
            qt.QTimer.__init__(self)
            self.connect(self,qt.SIGNAL('timeout()'),self.__putImage)
            self.images = []
            for root,dirs,files in os.walk('/bliss/users/petitdem/TestGui/Image/resize') :
                for file_name in files :
                  basename,ext = os.path.splitext(file_name)
                  if ext == '.jpeg' :
                      self.images.append(qt.QImage(os.path.join(root,file_name)))
                break
            self.__pixmapManager = pixmapMgr
            self.id = 0
            self.start(10)

        def __putImage(self) :
            image = self.images[self.id % len(self.images)]
            self.__pixmapManager.putImage(image,image)
            self.id += 1
                                      
    qt.QObject.connect(a,qt.SIGNAL("lastWindowClosed()"),a,qt.SLOT("quit()"))

    dialog = qt.QDialog()
    layout = qt.QHBoxLayout(dialog,11,6,"layout")
    label1 = qt.QLabel(dialog,"label1")
    layout.addWidget(label1)

    label2 = qt.QLabel(dialog,"label2")
    layout.addWidget(label2)

    pixmapMgr = QubImage2Pixmap()

    i2p = Image2Pixmap(label1)
    z = i2p.zoom()
    z.setZoom(1/2.,1/2.)
    i2pzoom = Image2Pixmap(label2)
    zoom = i2pzoom.zoom()
    zoom.setRoiNZoom(100,0,300,200,1,2.5)

    pixmapMgr.plug(i2p)
    pixmapMgr.plug(i2pzoom)

    timer = PutImageTimer(pixmapMgr)
    
    a.setMainWidget(dialog)
    dialog.show()
    a.exec_loop()
