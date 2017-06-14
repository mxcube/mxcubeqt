"""
[Name] Camera Off Line Image Manager

[Description]

The brick managed camera snap image for off line scan or motor movement

[Properties]
----------------------------------------------------------------------
| name                | type     | description
----------------------------------------------------------------------
| horizontal          | string   | horizontal motor
| vertical            | string   | vertical motor
| save_motors         | string   | an equipment containing a motor list in order to save snap motors position
| live_camera         | string   | the live camera
----------------------------------------------------------------------

[Signals]

----------------------------------------------------------------------
| name                | arguments                         | description
----------------------------------------------------------------------
| getImage            | a dictionnary                     | emitted when an image snap is required (usualy connected on getImage CameraBrick Slot)
| getView             | a dictionnary                     | emitted to get a reference on the image viewer object. At returned of the emit function, the key "drawing" exists and its value is the reference of the image viewer or the key "drawing" does not exists which mean that the image viewer object does not exist.
----------------------------------------------------------------------

"""

__category__ = "Camera"

import os
import logging
import pickle
import qt
from BlissFramework.BaseComponents import BlissWidget

from Qub.Icons.QubIcons import loadIcon

from Qub.Objects.Mosaic.QubMosaicImage import QubMosaicImage
from Qub.Objects.Mosaic.QubMosaicDrawingManager import QubMosaicPointDrawingMgr
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget
from Qub.Objects.QubDrawingEvent import _DrawingEventNDrawingMgr
from Qub.Objects.QubDrawingManager import QubAddDrawing

from Qub.Objects.QubStdData2Image import QubStdData2Image,QubStdData2ImagePlug

from Qub.Widget.QubActionSet import QubToolButtonAction

from Qub.Widget.QubActionSet import QubOpenDialogAction
from Qub.Widget.QubActionSet import QubRulerAction

from Qub.Tools import QubImageSave

import weakref

def _foreachSelectedItems(func) :
    def _eachRecurs(classname,item,*args,**keys) :
        while item :
            if item.isSelected() :
                NextItem = item.nextSibling()
                if(not func(classname,item,*args,**keys)) :
                    _eachRecurs(classname,item.firstChild(),*args,**keys)
                item = NextItem
            else:
                _eachRecurs(classname,item.firstChild(),*args,**keys)
                item = item.nextSibling()

    def _eachSelected(classname,*args,**keys) :
        _eachRecurs(classname,classname._CameraOffLineImageManagerBrick__imageList.firstChild(),
                    *args,**keys)
    return _eachSelected

###
### Brick to managed already stored camera's images
###
class CameraOffLineImageManagerBrick(BlissWidget):
    def __init__(self,parent,name,**keys) :
        BlissWidget.__init__(self,parent,name)
        self.__hMotor = None
        self.__vMotor = None
        self.__motor_pos_save = []
        self.__master_motor = None
        self.__masterPosition2Item = weakref.WeakValueDictionary()
        self.__currentCalib = None
        self.__currentBeamPos = None
        self.__camDecompNPlug = None
        self.mosaicView = None
        self.drawing = None
        self.__saveImageTreeDirName = '.'
        self.__imageMosaicPosition = None
                       ####### Property #######
        self.addProperty('horizontal','string','')
        self.addProperty('vertical','string','')
        self.addProperty('save_motors','string','')
        self.addProperty('master_motor','string','')
        self.addProperty('focus_motor','string','')
        self.addProperty('live_camera','string','')
        self.addProperty("formatString", "formatString", "###.##")
                        ####### SIGNAL #######
        self.defineSignal("getImage",())
        self.defineSignal('getView',())
        self.defineSignal('getMosaicView',())
                         ####### SLOT #######
        self.defineSlot("ChangePixelCalibration", ())
        self.defineSlot("ChangeBeamPosition", ())
        self.defineSlot('setMosaicImageSelected',())
        
        self.__widgetTree = self.loadUIFile('CameraOffLineImageManager.ui')
        self.__frame = self.__widgetTree.child('__frame')
        self.__frame.reparent(self,qt.QPoint(0,0))
        layout = qt.QHBoxLayout(self)
        layout.addWidget(self.__frame)
        
        snapButton = self.child('__snapShoot')
        iconSet = qt.QIconSet(loadIcon("snapshot.png"))
        snapButton.setIconSet(iconSet)
        qt.QObject.connect(snapButton,qt.SIGNAL('clicked()'),self.__snapCBK)

        liveCheckBox = self.child('__liveCheckBox')
        liveCheckBox.hide()
        qt.QObject.connect(liveCheckBox,qt.SIGNAL('toggled(bool)'),self.__liveOnOff)
        

        self.__imageList = self.child('__imageList')
        self.__imageList.setSelectionMode(qt.QListView.Extended)
        self.__imageList.setSortColumn(-1)
        self.__popUpMenu = qt.QPopupMenu(self)
        self.__popUpMenu.insertItem('layer up',self.__layerUp)
        self.__popUpMenu.insertItem('layer down',self.__layerDown)
        self.__popUpMenu.insertItem('remove',self.__removeImage)

        self.__popUpMenu.insertSeparator()
        self.__popUpMenu.insertItem('load',self.__loadImageTree)
        self.__popUpMenu.insertItem('save',self.__saveImageTree)

        qt.QObject.connect(self.__imageList,qt.SIGNAL('rightButtonPressed(QListViewItem*,const QPoint &,int)'),
                           self.__popUpDisplay)

    def propertyChanged(self,propertyName,oldValue,newValue) :
        if propertyName == 'horizontal' :
            if self.__hMotor:
                self.disconnect(self.__hMotor, qt.PYSIGNAL("positionChanged"), self.__hMotorPositionChanged)
            self.__hMotor = self.getHardwareObject(newValue)
            self.connect(self.__hMotor, qt.PYSIGNAL("positionChanged"), self.__hMotorPositionChanged)
            self.connect(self.__hMotor,qt.PYSIGNAL("limitsChanged"),self.__hMotorLimitsChanged)
        elif propertyName == 'vertical' :
            if self.__vMotor:
                self.disconnect(self.__vMotor, qt.PYSIGNAL("positionChanged"), self.__vMotorPositionChanged)
            self.__vMotor = self.getHardwareObject(newValue)
            self.connect(self.__vMotor, qt.PYSIGNAL("positionChanged"), self.__vMotorPositionChanged)
            self.connect(self.__vMotor,qt.PYSIGNAL("limitsChanged"),self.__vMotorLimitsChanged)

        elif propertyName == 'save_motors' :
            equipment = self.getHardwareObject(newValue)
            self.__motor_pos_save = []
            if equipment :
                try:
                    ho = equipment['motors']
                except KeyError:
                    print equipment.userName(), 'is not an Equipment : no <motors> section.'
                    return
                for motor in ho.getDevices() :
                    self.__motor_pos_save.append(motor)

                #Refresh Tree column
                nbColumn = self.__imageList.columns()
                for columnId in range(1,self.__imageList.columns()) :
                    self.__imageList.removeColumn(columnId)
                for motor in self.__motor_pos_save:
                    self.__imageList.addColumn(motor.userName())
        elif propertyName == 'master_motor':
            if self.__master_motor is not None:
                self.__imageList.takeItem(self.__masterControler)
            self.__master_motor = self.getHardwareObject(newValue)
            if self.__master_motor is not None:
                self.__masterControler = qt.QCheckListItem(self.__imageList,self.__master_motor.userName())
                self.__masterControler.setSelectable(False)
                self.__masterControler.setOpen(True)
        elif propertyName == 'focus_motor':
            self.__focus_motor = self.getHardwareObject(newValue)
            moveFocusCheckBox = self.child('__moveFocusCheckBox')
            if self.__focus_motor is not None:
                moveFocusCheckBox.show()
            else:
                moveFocusCheckBox.hide()
        elif propertyName == 'live_camera' :
            if self.__camDecompNPlug :
                camera,decomp,_ = self.__camDecompNPlug
                self.disconnect(camera,qt.PYSIGNAL('imageReceived'),decomp.putData)
                self.__camDecompNPlug = None
                
            camera = self.getHardwareObject(newValue)
            liveCheckBox = self.child('__liveCheckBox')
            if camera is not None:
                decomp = QubStdData2Image()
                plug = _LiveImagePlug(self)
                decomp.plug(plug)

                imageInfo = camera.imageType()
                if imageInfo and imageInfo.type() == 'bayer': imType = decomp.BAYER_RG
                elif imageInfo and imageInfo.type() == 'raw': imType = decomp.RAW
                else: imType = decomp.STANDARD # JPEG
                decomp.setImageType(imType)

                self.__camDecompNPlug = camera,decomp,plug

                liveCheckBox.show()
            else:
                liveCheckBox.hide()
        elif propertyName == 'formatString':
            self._formatString = self['formatString']
            
    def ChangePixelCalibration(self,sizeX,sizeY) :
        if sizeX is not None and sizeY is not None:
            motorXUnit = self.__hMotor.getProperty('unit')
            if motorXUnit is None : motorXUnit = 1e-3

            motorYUnit = self.__vMotor.getProperty('unit')
            if motorYUnit is None : motorYUnit = 1e-3

            self.__currentCalib = sizeX / motorXUnit,sizeY / motorYUnit

            if self.__camDecompNPlug :
                camera,decomp,plug = self.__camDecompNPlug
                plug.setPixelCalibration(*self.__currentCalib)
        else:
            self.__currentCalib = None
            
    def ChangeBeamPosition(self,x,y) :
        self.__currentBeamPos = x,y
        if self.__camDecompNPlug :
            camera,decomp,plug = self.__camDecompNPlug
            plug.setBeamPosition(*self.__currentBeamPos)

    def setMosaicImageSelected(self,imageSelectedID) :
        moveFocusCheckBox = self.child('__moveFocusCheckBox')
        if moveFocusCheckBox.isChecked() :
            position = self.__focus_motor.getPosition()
            def _recursfind(item,lookinId) :
                while item:
                    if id(item) == lookinId:
                        return item
                    else:
                        returnItem = _recursfind(item.firstChild(),lookinId)
                        if returnItem: return returnItem
                        item = item.nextSibling()
            item = _recursfind(self.__imageList.firstChild(),imageSelectedID)
            try:
                if item and item.focusMotorPosition != position:
                    self.__focus_motor.move(item.focusMotorPosition)
            except AttributeError:
                pass
    def __displayMotorsPositionUnderMouse(self,drawingManager) :
        point = drawingManager.mosaicPoints()
        try:
            point = point[0]
            beamY,beamZ = point.refPoint
            YSize,ZSize = point.calibration
            horMotorPos,verMotorPos = point.absPoint
            y,z = point.point
            imageId = point.imageId
        except TypeError: return
        movetoy = horMotorPos - (beamY - y) * YSize
        movetoz = verMotorPos - (beamZ - z) * ZSize

        if self.__imageMosaicPosition:
            self.__imageMosaicPosition.setCursorPosition(QubRulerAction.HORIZONTAL,1,
                                                         movetoy)
            self.__imageMosaicPosition.setCursorPosition(QubRulerAction.VERTICAL,1,
                                                         movetoz)
            self.__mouseMotorPosition.setXValue(movetoy)
            self.__mouseMotorPosition.setYValue(movetoz)
            
    def __hMotorPositionChanged(self,position) :
        if self.__imageMosaicPosition:
            self.__imageMosaicPosition.setCursorPosition(QubRulerAction.HORIZONTAL, 0,
                                                         position)
            self.__currentMotorPosition.setXValue(position)
            
        if self.__camDecompNPlug :
            camera,decomp,plug = self.__camDecompNPlug
            plug.setHMotorPosition(position)
            
    def __hMotorLimitsChanged(self,limit) :
        if self.__imageMosaicPosition:
            self.__imageMosaicPosition.setLimits(QubRulerAction.HORIZONTAL,0,
                                                 *limit)
            self.__imageMosaicPosition.setLimits(QubRulerAction.HORIZONTAL,1,
                                                 *limit)
        
    def __vMotorPositionChanged(self,position) :
        if self.__imageMosaicPosition:
            self.__imageMosaicPosition.setCursorPosition(QubRulerAction.VERTICAL, 0,
                                                         position)
            self.__currentMotorPosition.setYValue(position)
        if self.__camDecompNPlug :
            camera,decomp,plug = self.__camDecompNPlug
            plug.setVMotorPosition(position)

    def __vMotorLimitsChanged(self,limit) :
        if self.__imageMosaicPosition:
            self.__imageMosaicPosition.setLimits(QubRulerAction.VERTICAL,0,
                                                 *limit)
            self.__imageMosaicPosition.setLimits(QubRulerAction.VERTICAL,1,
                                                 *limit)
        
    def __getMasterItem(self,position = None) :
        if self.__master_motor is not None:
            if position is None:
                position = self.__master_motor.getPosition()
            try:
                master_item = self.__masterPosition2Item[position]
            except KeyError:
                positionString = self._formatString % position
                master_item = _MasterCheckItem(self.__masterControler,'p_%d (%s)' % (len(self.__masterPosition2Item),positionString))
                self.__masterPosition2Item[position] = master_item
        else:
            master_item = self.__imageList
            position = None
        return master_item,position
        
    def __snapCBK(self) :
        key = {}
        self.emit(qt.PYSIGNAL('getImage'),(key,))
        image = key.get('image',None)
        if image:
            master_item,position = self.__getMasterItem()
            if self.__focus_motor is not None:
                focusPosition = self.__focus_motor.getPosition()
            else:
                focusPosition = None
            try:
                item = _CheckItem(master_item,'image',self,image,
                                  self.__currentBeamPos,self.__currentCalib,
                                  self.__hMotor,self.__vMotor,self.__motor_pos_save,position,focusPosition)
            except:
                logging.getLogger().error('CameraOffLineImageManager : Spec not connected')

        else:
            logging.getLogger().error('CameraOffLineImageManager : getImage is not connected to CameraOffLineImageManager!!!')

    def __liveOnOff(self,state) :
        camera,decomp,plug = self.__camDecompNPlug
        if state:
            self.connect(camera,qt.PYSIGNAL('imageReceived'),decomp.putData)
            plug.show()
        else:
            self.disconnect(camera,qt.PYSIGNAL('imageReceived'),decomp.putData)
            plug.hide()

    def __saveImageTree(self,i) :
        pickleObjects = []
        self.__saveImageRecurse(self.__imageList.firstChild(),pickleObjects)
        if pickleObjects:
            fullpathname = qt.QFileDialog.getSaveFileName(self.__saveImageTreeDirName,'Camera mosaic (*.mosaic)',self,
                                                          'Save mosaic images',
                                                          "Choose a filename to save under")
            if fullpathname:
                fullpathname = fullpathname.latin1()
                self.__saveImageTreeDirName,fname = os.path.split(fullpathname)
                filename,ext = os.path.splitext(fname)
                fullpathname = os.path.join(self.__saveImageTreeDirName,'%s.mosaic' % filename)
                pickle.dump(pickleObjects,file(fullpathname,'w'))
        else:
            errorMess = qt.QErrorMessage(self)
            errorMess.message('Nothing to Save!!!')

    def __loadImageTree(self,i) :
        fullpathname = qt.QFileDialog.getOpenFileName(self.__saveImageTreeDirName,'Camera mosaic (*.mosaic)',self,
                                                      'Load mosaic images',
                                                      "Load a image tree")
        if fullpathname:
            fullpathname = fullpathname.latin1()
            self.__imageList.selectAll(True)
            self.__removeImage(0)
            for saveItem in pickle.load(file(fullpathname)):
              master_item,position = self.__getMasterItem(saveItem.masterPosition)
              _CheckItem(master_item,saveItem,self)
            
    def __saveImageRecurse(self,item,pickleObjects) :
        while item:
            NextItem = item.nextSibling()
            try: pickleObjects.append(item.getSavePickleObject())
            except AttributeError: pass
            self.__saveImageRecurse(item.firstChild(),pickleObjects)
            item = NextItem

    @_foreachSelectedItems
    def __removeImage(self,item,i)  :
        try:
            item.parent().takeItem(item)
        except AttributeError:
            self.__imageList.takeItem(item)
        return True
    @_foreachSelectedItems
    def __layerUp(self,item,i) :
        item.layerUp()

    @_foreachSelectedItems
    def __layerDown(self,item,i) :
        item.layerDown()

    def __popUpDisplay(self,item,point,columnid) :
        self.__popUpMenu.exec_loop(point)

    def run(self) :
        key = {}
        self.emit(qt.PYSIGNAL('getView'),(key,))
        try:
            view = key['view']
            drawing = key['drawing']

            self.__snapAction = QubToolButtonAction(name='MosaicSnap',iconName='snapshot',toolButtonStyle = True,
                                                    place='toolbar',
                                                    group='image',autoConnect = True)
            qt.QObject.connect(self.__snapAction,qt.PYSIGNAL('ButtonPressed'),self.__snapCBK)
            view.addAction([self.__snapAction])
        except KeyError:
            logging.getLogger().error('getView is not connected to CameraOffLineImageManager!!!')
            


        mosaicKey = {}
        self.emit(qt.PYSIGNAL('getMosaicView'),(mosaicKey,))
        try:
            self.mosaicView = mosaicKey['view']
            self.drawing = mosaicKey['drawing']
            class _openDialog(QubOpenDialogAction) :
                def __init__(self,*args,**keys) :
                    QubOpenDialogAction.__init__(self,*args,**keys)
                def setCanvas(self,canvas) :
                    self.__canvas = canvas
                    
                def _showDialog(self) :
                    if self._dialog.exec_loop() == qt.QDialog.Accepted :
                        file_path = self._dialog.selectedFile().ascii()
                        dirName,file_name = os.path.split(file_path)
                        base,ext = os.path.splitext(file_name)
                        QubImageSave.save(os.path.join(dirName,'%s.svg' % base),None,self.__canvas,1,'svg',True)
                        
            self.__saveMosaicAction = _openDialog(parent=self,label='Save image',name="save", iconName='save',group="admin")
            saveMosaicDialogue = qt.QFileDialog('.','Mosaic Images (*.svg)',self,'Save mosaic Images',True)
            saveMosaicDialogue.setMode(saveMosaicDialogue.AnyFile)
            self.__saveMosaicAction.setDialog(saveMosaicDialogue)
            self.__saveMosaicAction.setCanvas(self.drawing.canvas())

            self.__imageMosaicPosition = QubRulerAction(name='Motor Position',
                                                        place='toolbar',
                                                        group='Tools')

            self.__mouseMotorPosition = _MouseOrMotorPosition(name='mouse motor position',
                                                              place='statusbar',
                                                              group='info',
                                                              mouseFlag = True)
            
            self.__currentMotorPosition = _MouseOrMotorPosition(name='current motor position',
                                                                place='statusbar',
                                                                group='info')
            
            self.mosaicView.addAction([self.__imageMosaicPosition,self.__saveMosaicAction,
                                       self.__currentMotorPosition,self.__mouseMotorPosition])
            
            if self.__vMotor is not None:
                self.__imageMosaicPosition.setLabel(QubRulerAction.VERTICAL,0,self.__vMotor.getMotorMnemonic())
                self.__imageMosaicPosition.setCursorPosition(QubRulerAction.VERTICAL, 0,
                                                             self.__vMotor.getPosition())
                limits = self.__vMotor.getLimits()
                self.__imageMosaicPosition.setLimits(QubRulerAction.VERTICAL,0,
                                                     *limits)
                self.__imageMosaicPosition.setLimits(QubRulerAction.VERTICAL,1,
                                                     *limits)

                self.__imageMosaicPosition.setLabel(QubRulerAction.VERTICAL,1, '')
                for label in [self.__mouseMotorPosition,self.__currentMotorPosition] :
                    label.setMotyName(self.__vMotor.getMotorMnemonic())
                    label.setYValue(self.__vMotor.getPosition())
                                        
            if self.__hMotor is not None:
                self.__imageMosaicPosition.setLabel(QubRulerAction.HORIZONTAL,0,self.__hMotor.getMotorMnemonic())
                limits = self.__hMotor.getLimits()
                self.__imageMosaicPosition.setLimits(QubRulerAction.HORIZONTAL,0,
                                                     *limits)
                self.__imageMosaicPosition.setLimits(QubRulerAction.HORIZONTAL,1,
                                                     *limits)
                
                self.__imageMosaicPosition.setCursorPosition(QubRulerAction.HORIZONTAL, 0,
                                                             self.__hMotor.getPosition())
                self.__imageMosaicPosition.setLabel(QubRulerAction.HORIZONTAL,1,'')

                for label in [self.__mouseMotorPosition,self.__currentMotorPosition] :
                    label.setMotxName(self.__hMotor.getMotorMnemonic())
                    label.setXValue(self.__hMotor.getPosition())
                    
            for ruler in self.__imageMosaicPosition._QubRulerAction__ruler:
                ruler.setZ(99)          # upper layer

            #Add a follow mulot
            class _MouseFollow(_DrawingEventNDrawingMgr) :
                def __init__(self,aDrawingMgr,oneShot,**keys) :
                    _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
                    
                def mouseMove(self,x,y) :
                    d = self._drawingMgr()
                    if d:
                        d.move(x,y)
                        d.endDraw()
            self.__followPointMouse,_ = QubAddDrawing(self.drawing,QubMosaicPointDrawingMgr,QubCanvasTarget)
            self.__followPointMouse.setDrawingEvent(_MouseFollow)
            self.__followPointMouse.setExclusive(False)
            self.__followPointMouse.startDrawing()
            self.__followPointMouse.setEndDrawCallBack(self.__displayMotorsPositionUnderMouse)
        except KeyError: pass

        if self.__camDecompNPlug:
            camera,decomp,plug = self.__camDecompNPlug
            try:
                plug.addImage()
                try:
                    plug.move(self.__hMotor.getPosition(),self.__vMotor.getPosition())
                except: pass
                else:
                    try:
                        plug.setCalibration(*self.__currentCalib)
                        plug.setBeamPosition(*self.__currentBeamPos)
                    except (AttributeError,TypeError) :
                        pass
            except AttributeError:
                liveCheckBox = self.child('__liveCheckBox')
                liveCheckBox.hide()
                
class _SavePickleItem:
    def __init__(self,checkitem,image,layer,state,cnt,masterPosition,focusPosition) :
        self.image = image
        self.textcolumn = []
        for i in xrange(cnt._CameraOffLineImageManagerBrick__imageList.columns()) :
            self.textcolumn.append(checkitem.text(i).latin1())
        self.layer = layer
        self.state = state == qt.QCheckListItem.On
        self.masterPosition = masterPosition
        self.focusMotorPosition = focusPosition
        
class _CheckItem(qt.QCheckListItem):
    def __init__(self,parent,name,cnt,image = None,
                 beamPos = None,calib = None,
                 hMotor = None,vMotor = None,motorList = None,masterPosition = None,
                 focusMotorPosition = None) :
        try:
            lastItem = parent.lastItem()
        except AttributeError:
            firstChild = parent.firstChild()
            if firstChild:
                childCount = parent.childCount()
                lastItem = firstChild
                try:
                    for i in range(1,childCount) :
                        lastItem = lastItem.itemBelow()
                except AttributeError:
                    lastItem = None
            else:
                lastItem = None
        if isinstance(name,_SavePickleItem) :
            if lastItem:
                qt.QCheckListItem.__init__(self,parent,lastItem,name.textcolumn[0],qt.QCheckListItem.CheckBox)
            else:
                qt.QCheckListItem.__init__(self,parent,name.textcolumn[0],qt.QCheckListItem.CheckBox)
            saveItem = name
            self.__image = saveItem.image

            for i,text in enumerate(saveItem.textcolumn):
                self.setText(i,text)
            self.__masterPosition = masterPosition
            try:
                self.focusMotorPosition = saveItem.focusMotorPosition
            except AttributeError:      # compatibility with old save mosaic
                self.focusMotorPosition = None
            self.__layer = saveItem.layer
            self.__cnt = cnt
            cnt.mosaicView.addImage(self.__image) # adding image to MosaicDisplay
            self.setState(saveItem.masterPosition and qt.QCheckListItem.On or qt.QCheckListItem.Off)
            self.setRenameEnabled(0,True)
        else:
            self.__image = QubMosaicImage(image,hMotor.getPosition(),vMotor.getPosition(),0)
            if lastItem:
                qt.QCheckListItem.__init__(self,parent,lastItem,name,qt.QCheckListItem.CheckBox)
            else:
                qt.QCheckListItem.__init__(self,parent,name,qt.QCheckListItem.CheckBox)
            icon = image.smoothScale(16,16,qt.QImage.ScaleMin)
            self.setPixmap(0,qt.QPixmap(icon))
            try:
                self.__image.setRefPos(*beamPos)
                self.__image.setCalibration(*calib)
            except TypeError:
                logging.getLogger().error('You have to connect ChangeBeamPosition and ChangePixelCalibration slot')
                return
            for i,motor in enumerate(motorList) :
                self.setText(i + 1,'%f' % motor.getPosition())
            self.__masterPosition = masterPosition
            self.focusMotorPosition = focusMotorPosition

            self.setRenameEnabled(0,True)

            self.__layer = 0
            self.__cnt = cnt
            cnt.mosaicView.addImage(self.__image) # adding image to MosaicDisplay
            try:
                self.__state = parent.isSelected() and qt.QCheckListItem.On or qt.QCheckListItem.Off
                self.setState(self.__state)
            except TypeError:
                self.__state = qt.QCheckListItem.On
                self.setState(qt.QCheckListItem.On)
        self.__image.setImageId(id(self))
        
    def getSavePickleObject(self) :
        return _SavePickleItem(self,self.__image,self.__layer,
                               self.__state,self.__cnt,self.__masterPosition,
                               self.focusMotorPosition)
    
    def layerUp(self) :
        self.__layer += 1
        self.__image.setLayer(self.__layer)
    def layerDown(self) :
        self.__layer -= 1
        self.__image.setLayer(self.__layer)
        
    def stateChange(self,flag) :
        self.__state = flag
        if flag:
            self.__image.show()
        else:
            self.__image.hide()

    def image(self) :
        return self.__image

class _MasterCheckItem(qt.QCheckListItem) :
    def __init__(self,parent,name) :
        qt.QCheckListItem.__init__(self,parent,name,qt.QCheckListItem.RadioButton)
        self.setRenameEnabled(0,True)
        self.setOpen(True)

    def layerUp(self,item) :
        pass

    def layerDown(self,item):
        pass

    def stateChange(self,flag) :
        item = self.firstChild()
        while item:
            item.setState(flag and qt.QCheckListItem.On or qt.QCheckListItem.Off)
            item = item.nextSibling()

class _LiveImagePlug(QubStdData2ImagePlug) :
    def __init__(self,cnt) :
        QubStdData2ImagePlug.__init__(self)
        self.__image = QubMosaicImage(motX = 0,motY = 0)
        self.__image.setLayer(4096)
        self.__cnt = cnt
        self.__imageAlreadySend = False

    def setImage(self,imagezoomed,fullimage) :
        self.__image.setImage(fullimage)
        return False

    def show(self) :
        self.__image.show()
        
    def hide(self) :
        self.__image.hide()
        
    def addImage(self) :
        if not self.__imageAlreadySend:
            self.__cnt.mosaicView.addImage(self.__image)
            self.__imageAlreadySend = True
    
    def setPixelCalibration(self,xSize,ySize) :
        self.__image.setCalibration(xSize,ySize)

    def setBeamPosition(self,x,y) :
        if x and y :
            self.__image.setRefPos(x,y)

    def move(self,x,y) :
        self.__image.move(x,y)

    def setHMotorPosition(self,position) :
        _,vPos = self.__image.position()
        self.__image.move(position,vPos)

    def setVMotorPosition(self,position) :
        hPos,_ = self.__image.position()
        self.__image.move(hPos,position)

from Qub.Widget.QubAction import QubImageAction
class _MouseOrMotorPosition(QubImageAction):
    def __init__(self,autoConnect = True,mouseFlag = False,**keys) :
        QubImageAction.__init__(self,autoConnect = autoConnect,**keys)
        self.__mouseFlag = mouseFlag
        
    def addStatusWidget(self,parent) :
        if self._widget is None:
            self._widget = qt.QWidget(parent)
            
            hlayout = qt.QHBoxLayout(self._widget)

            self._xLabel = qt.QLabel("X:", self._widget)
            self._xLabel.setSizePolicy(qt.QSizePolicy.Fixed,qt.QSizePolicy.Fixed)
            hlayout.addWidget(self._xLabel)
            
            self._xValue = qt.QLabel("x", self._widget)
            self._xValue.setSizePolicy(qt.QSizePolicy.Fixed,qt.QSizePolicy.Fixed)
            font = self._xValue.font()
            font.setBold(True)
            self._xValue.setFont(font)
            hlayout.addWidget(self._xValue)
            
            hlayout.addSpacing(5)
                   
            self._yLabel = qt.QLabel("Y:", self._widget)
            self._yLabel.setSizePolicy(qt.QSizePolicy.Fixed,qt.QSizePolicy.Fixed)
            hlayout.addWidget(self._yLabel)
            
            self._yValue = qt.QLabel("x", self._widget)
            self._yValue.setSizePolicy(qt.QSizePolicy.Fixed,qt.QSizePolicy.Fixed)
            self._yValue.setFont(font)
                        
            hlayout.addWidget(self._yValue)
            hlayout.addStretch()
        return self._widget

    def setMotxName(self,name) :
        if self.__mouseFlag:
            self._xLabel.setText('Mouse %s :' % str(name))
        else:
            self._xLabel.setText(name)

    def setXValue(self,pos) :
        self._xValue.setText('%.2f' % pos)


    def setMotyName(self,name) :
        if self.__mouseFlag:
            self._yLabel.setText('Mouse %s :' % str(name))
        else:
            self._yLabel.setText(name)

    def setYValue(self,pos) :
        self._yValue.setText('%.2f' % pos)
