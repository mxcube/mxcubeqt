"""
[Name] CameraBrick

[Description]

The Camera brick can display image from camera. You can connect
external action and some drawing vector.

[Properties]

----------------------------------------------------------------------
| name                | type     | description
----------------------------------------------------------------------
| camera                                      | string   | name of camera hardware object
| zoom list                                   | string   | a list of posible zoom separate
|                                             |          |   with comma for the sub view display
| init zoom                                   | integer  | the init zoom for the sub view display
| swap rgb                                    | boolean  | swap the bgr chanel to rgb
| fix width                                   | integer  | fix the width of the camera display
| fix height                                  | integer  | fix the height of the camera display
| action : print                              | boolean  | show print action
| action : save image                         | boolean  | show save image action
| action : update                             | boolean  | show update action
| action : startCamera                        | boolean  | Starts the camera (set live mode)
| action : brightness contrast                | boolean  | show brightness contrast action
| action : beam                               | boolean  | show beam action
| action : scale                              | boolean  | show scale action
| action : change foreground color            | boolean  | show change foreground color action
| action : measure                            | boolean  | show measure action
| action : measure (place)		      | combo    | display measure action in the toolbar or in contextmenu
| action : zoom window                        | boolean  | show zoom window action
| action : zoom fit or fill                   | boolean  | show zoom fit or fill action
| action : zoom list                          | boolean  | show zoom list action
| action : x,y coordinates                    | boolean  | show x,y coordinates
| action : save image (place)                 | combo    | display save action in the toolbar or
|                                             |          |   in contextmenu
| action : save image (default path)          | string   | change the default save path
| action : save image (show always configure) | boolean  | on save action click : if true shows
|                                             |          |   the configure save panel ELSE save an image on click.
| action : default color                      | combo    | chose the default vector color (requier
|                                             |          |   to have <b>change foreground color<\b> activated
----------------------------------------------------------------------

[Signals]

---------------------------------------------------------------
| name                | arguments                  | description
---------------------------------------------------------------
| BeamPositionChanged | x,y position on image      | emitted when beam position changed
---------------------------------------------------------------

[Slots]

----------------------------------------------------------------------
| name                | arguments                         | description
-------------------------------------------------------------------
| changeBeamPosition  | x,y position on image             | usualy emitted by the CameraBeamBrick
|                     |                                   |   when the zoom changed
| changePixelScale    | xSize,ySize in pixelsize in meter | usualy emitted by the CameraCalibrationBrick
|                     |                                   |    when the zoom changed
| getView             | a Dictionary                      | returns a dictionnary whith 2 key : 'view'
|                     |                                   |   (QubPixmapDisplayView Object) to add external
|                     |                                   |   action and 'drawing' (QubPixmapDisplay
|                     |                                   |   Object) to add external drawing
| getImage            | a Dictionary                      | return the last image in a dictionnary key 'image'
----------------------------------------------------------------------
"""

__category__ = "Camera"

from BlissFramework.BaseComponents import BlissWidget
import logging
import os
import time
import qt
from Qub.Widget.QubAction import QubToggleAction
from Qub.Widget.QubActionSet import QubZoomRectangle
from Qub.Widget.QubActionSet import QubZoomListAction
from Qub.Widget.QubActionSet import QubZoomAction
from Qub.Widget.QubActionSet import QubBeamAction
from Qub.Widget.QubActionSet import QubPositionAction
from Qub.Widget.QubActionSet import QubPrintPreviewAction
from Qub.Widget.QubActionSet import QubScaleAction
from Qub.Widget.QubActionSet import QubOpenDialogAction
from Qub.Widget.QubActionSet import QubForegroundColorAction
from Qub.Widget.QubActionSet import QubInfoAction
from Qub.Widget.QubActionSet import QubSaveImageAction
from Qub.Objects.QubPixmapDisplayView import QubPixmapDisplayView
from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug
from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap
from Qub.Objects.QubStdData2Image import QubStdData2Image,QubStdData2ImagePlug
from Qub.Print.QubPrintPreview import QubPrintPreview
from Qub.Widget.QubDialog import QubSaveImageDialog,QubMeasureListDialog,QubBrightnessContrastDialog
from widgets.grid_dialog import GridDialog


DISABLED_JPEG = file(os.path.join(os.path.dirname(__file__), "disabled.jpeg"), "r").read()
DISABLED_WIDTH = 659
DISABLED_HEIGHT = 493

###
### Brick to display a video of the sample
###
class CameraBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.camera       = None
        self.update_disabled = False
        self.__cameraName = None

        self.__zoomList = [1.5,2,2.5,3,3.5,4]
        self.__initZoom = 2

        self.__fixWidth  = -1
        self.__fixHeight = -1

        self.__swapRgb = True
                        ####### PRINT #######
        self.__printWidget = QubPrintPreview(self)
        self.__printWidget.resize(400,500)
        printer = qt.QPrinter()
        printer.setOutputToFile(1)
        printer.setOutputFileName('/tmp/print_file.ps')
        self.__printWidget.setPrinter(printer)
        self.__printWidget.update()

        self.__beamAction    = None
        self.__scaleAction   = None
        self.__chosenActions = {}
        self.__wholeActions  = []
        self.__measureDialog = None

        ####### PRINT ACTION #######
        printAction = QubPrintPreviewAction(name="print",group="admin",withVectorMenu=True)
        printAction.previewConnect(self.__printWidget)
        self.__wholeActions.append(printAction)

        ####### SAVE IMAGE #######
        self.__saveAction = QubSaveImageAction(parent=self, label='Save falcon image',
                                               name="save", group="admin")
        self.__saveAction.setConnectCallBack(self._save_dialog_new)
        self.__wholeActions.append(self.__saveAction)
        self.__defaultSavePath = '/tmp'

        ####### UPDATE #######
        update = QubToggleAction(name="update",group="image",initState=True)
        self.connect(update,qt.PYSIGNAL("StateChanged"),self.__cameraUpdate)
        self.__wholeActions.append(update)

        ####### Start Camera ######
        startCamera = QubToggleAction(name="startCamera", group="image", iconName = 'bright-cont', initState=True)
        self.connect(startCamera, qt.PYSIGNAL("StateChanged"), self.__cameraStart)
        self.__wholeActions.append(startCamera)


        ####### BRIGHTNESS/CONTRAST #######
        self.__brightcount = QubOpenDialogAction(name="bright-cont",
                                                 iconName = 'bright-cont', group="image")
        self.__brightcount.setDialog(QubBrightnessContrastDialog(self))
        self.__wholeActions.append(self.__brightcount)

        ###### Grid TOOL ######
        self.__gridToolAction = QubOpenDialogAction(parent=self, name='grid_tool',
                                                    iconName='rectangle', label='Grid tool',
                                                    group="Tools") #place="contextmenu")
        self.__gridDialog = GridDialog(self, "Grid Dialog", flags = qt.Qt.WStyle_StaysOnTop)
        self.__gridToolAction.setConnectCallBack(self._grid_dialog_connect_hdlr)
        self.__wholeActions.append(self.__gridToolAction)

        self.__previous_pos_dict = {}
        self.__beamWidth = 0
        self.__beamHeight = 0

        ####### BEAM ACTION #######
        self.__beamAction = QubBeamAction(name="beam", group="Tools")
        self.__wholeActions.append(self.__beamAction)
        self.connect(self.__beamAction,qt.PYSIGNAL("BeamSelected"),
                     self.beamSelection)

        ####### SCALE #######
        self.__scaleAction = QubScaleAction(name='scale',group='Tools')
        self.__wholeActions.append(self.__scaleAction)
        self.__wholeActions.extend(self.__creatStdActions())

        ####### ACTION INFO #######
        actionInfo = QubInfoAction(name="actionInfo", group="image",place="statusbar")
        self.__wholeActions.append(actionInfo)

        ####### CHANGE FOREGROUND COLOR #######
        self.__fcoloraction = QubForegroundColorAction(name="color", group="image")
        self.__wholeActions.append(self.__fcoloraction)

        ####### MEASURE #######
        self.__measureAction = QubOpenDialogAction(parent=self, name='measure',
                                            iconName='measure', label='Measure',
                                            group="Tools")
        self.__measureAction.setConnectCallBack(self._measure_dialog_new)
        self.__wholeActions.append(self.__measureAction)

        # ###### POSITION TOOL ######
        # self.__posToolAction = QubOpenDialogAction(parent=self, name='pos_tool',
        #                                            iconName='circle', label='Position tool',
        #                                            group="Tools")
        # self.__posToolAction.setConnectCallBack(self._line_dialog_new)
        # self.__wholeActions.append(self.__posToolAction)

        ####### ZOOM LIST #######
        zoomActionList = QubZoomListAction(place = "toolbar",
                                           initZoom = 1,zoomValList = [0.1,0.25,0.5,0.75,1,1.5,2],
                                           show = 1,group = "zoom")
        self.__wholeActions.append(zoomActionList)

        ####### ZOOM Action #######
        self.__zoomFitOrFill = QubZoomAction(place = "toolbar",group = "zoom")
        self.__wholeActions.append(self.__zoomFitOrFill)

        ####### LINK ZOOM ACTION #######
        self.__zoomFitOrFill.setList(zoomActionList)
        zoomActionList.setActionZoomMode(self.__zoomFitOrFill)

        ####### ZOOM WINDOW #######
        self.__zoomAction = QubZoomRectangle(label='Zoom Crop',place="toolbar", show=1, group="zoom")
        self.connect(self.__zoomAction,qt.PYSIGNAL("Actif"),self.__hide_show_zoom)
        self.__wholeActions.append(self.__zoomAction)

        self.__splitter = qt.QSplitter(qt.Qt.Horizontal,self)
        self.__splitter.show()

        self.__mainVideo = QubPixmapDisplayView(self.__splitter)
        self.__mainVideo.show()
        self.__mainVideo.setScrollbarMode('Auto')
        self.__mainPlug = _MainVideoPlug(self.__mainVideo,self.__zoomAction)

        actions = self.__creatStdActions()

        ####### ZOOM LIST #######
        self.__zoomActionList = QubZoomListAction(place = "toolbar",keepROI = True,
                                                  initZoom = self.__initZoom,zoomValList = self.__zoomList,
                                                  show = 1,group = "zoom")
        actions.insert(0,self.__zoomActionList)

        ####### ZOOM Action #######
        zoomFitOrFill = QubZoomAction(place = "toolbar",keepROI = True,group = "zoom")
        zoomFitOrFill.setList(self.__zoomActionList)
        self.__zoomActionList.setActionZoomMode(zoomFitOrFill)
        actions.append(zoomFitOrFill)

        self.__zoomVideo = QubPixmapDisplayView(self.__splitter,None,actions)
        self.__zoomVideo.hide()
        self.__zoomPlug = _ZoomPlug(self.__zoomVideo)
        self.__zoomPlug.zoom().setZoom(2,2)
        self.__cbk = _rectangleZoom(self.__zoomAction,self.__zoomPlug)

        layout = qt.QHBoxLayout(self,0,0,"layout")
        layout.addWidget(self.__splitter)

        self.__image2Pixmap = QubImage2Pixmap()
        self.__image2Pixmap.plug(self.__mainPlug)
        self.__zoomPlug.setPoller(self.__image2Pixmap)

        self.__jpegDecompress = QubStdData2Image()
        self.__jpegDecompress.setSwapRGB(True)
        self.__jpeg2image = None

        ####### PROPERTY #######
        self.addProperty('camera','string','')
        self.addProperty('zoom list','string',','.join([str(x) for x in self.__zoomList]))
        self.addProperty('init zoom','integer',self.__initZoom)
        self.addProperty('swap rgb','boolean',True)

        self.addProperty('fix : width','integer',-1)
        self.addProperty('fix : height','integer',-1)

        self.addProperty('action : print','boolean',True)
        self.addProperty('action : save image','boolean',True)
        self.addProperty('action : update','boolean',True)
        self.addProperty('action : startCamera','boolean',True)
        self.addProperty('action : brightness contrast','boolean',True)
        self.addProperty('action : beam','boolean',True)
        self.addProperty('action : scale','boolean',True)
        self.addProperty('action : change foreground color','boolean',True)
        self.addProperty('action : measure','boolean',True)
        self.addProperty('action : measure (place)', 'combo', ('toolbar','contextmenu'),'toolbar')
        self.addProperty('action : zoom window','boolean',True)
        self.addProperty('action : zoom fit or fill','boolean',True)
        self.addProperty('action : zoom list','boolean',True)
        self.addProperty('action : x,y coordinates','boolean',True)
        self.addProperty('action : default color','combo',('black','red','green'),'black')

        self.addProperty('action : save image (place)',"combo",('toolbar','contextmenu'),'toolbar')
        self.addProperty('action : save image (default path)',"string",'/tmp')
        self.addProperty('action : save image (show always configure)',"boolean",True)

        self.addProperty("diffractometer", "string", "")
        self.diffractometerHwobj = None


        ####### SIGNAL #######
        self.defineSignal("BeamPositionChanged", ())

        ####### SLOT #######
        self.defineSlot("changeBeamPosition", ())
        self.defineSlot("changePixelScale",())
        self.defineSlot('getView',())
        self.defineSlot('getImage',())

        ####### LINK VIEW AND SUB VIEW #######
        mainView = self.__mainVideo.view()
        zoomView = self.__zoomVideo.view()
        mainView.addEventMgrLink(zoomView,
                                 mainView.canvas(),zoomView.canvas(),
                                 mainView.matrix(),zoomView.matrix())

        self.imageReceivedConnected = None

    def safeConnect(self):
        if not self.imageReceivedConnected and self.camera is not None:
            #print "CONNECTING 0"
            self.camera.connect('imageReceived', self.__imageReceived)
            #self.connect(self.camera,qt.PYSIGNAL('imageReceived'),self.__imageReceived)
            self.imageReceivedConnected = False

    def safeDisconnect(self):
        if self.imageReceivedConnected and self.camera is not None:
            #print "DISCONNECTING 3"
            self.camera.disconnect('imageReceived', self.__imageReceived)
            #self.disconnect(self.camera,qt.PYSIGNAL('imageReceived'),self.__imageReceived)
            self.imageReceivedConnected = False

    def disable_update(self):
        self.__imageReceived(DISABLED_JPEG,DISABLED_WIDTH,DISABLED_HEIGHT)
        self.update_disabled = True

    def enable_update(self):
        self.update_disabled = False

    def __imageReceived(self,image,width,height,force_update=False):
        if self.update_disabled:
            return

        if not force_update:
            if not self.isVisible():
                return
        
        if isinstance(image,qt.QImage):
            if self.__swapRgb:
                image = image.swapRGB()
            self.__jpeg2image.setImage(image,image)
        else:
            self.__jpegDecompress.putData(image,width,height)

    def propertyChanged(self,property,oldValue,newValue):
        if property=='camera':
            #if self.camera is not None and not self.isRunning():
            #    self.safeDisconnect()
            self.safeDisconnect()
            self.camera      = self.getHardwareObject(newValue)
            self.__hwoName   = newValue

            if self.camera is not None:
		try:
                    self.__tangoName = self.camera.tangoname
		except:
		    self.__tangoName = ""

                try:
                    camera_role=self.camera.getDeviceByRole('camera')
                    if camera_role is not None:
                        self.camera=camera_role
                except AttributeError:
                    pass

                self.__brightcount.setCamera(self.camera)

        elif property == 'zoom list' :
            zoomList = [float(x) for x in newValue.split(',')]
            if zoomList != self.__zoomList :
                self.__zoomList = zoomList
                self.__zoomActionList.changeZoomList(zoomList,self.__initZoom)
        elif property == 'init zoom' :
            if newValue != self.__initZoom :
                self.__initZoom = newValue
                self.__zoomActionList.changeZoomList(self.__zoomList,newValue)
        elif property == 'swap rgb' :
            self.__jpegDecompress.setSwapRGB(newValue)
            self.__swapRgb = newValue
        elif property == 'action : print' : self.__chosenActions['print'] = newValue
        elif property == 'action : save image' : self.__chosenActions['save'] = newValue
        elif property == 'action : update' : self.__chosenActions['update'] = newValue
        elif property == 'action : startCamera' : self.__chosenActions['startCamera'] = newValue
        elif property == 'action : brightness contrast' : self.__chosenActions['bright-cont'] = newValue
        elif property == 'action : beam' : self.__chosenActions['beam'] = newValue
        elif property == 'action : scale' : self.__chosenActions['scale'] = newValue
        elif property == 'action : change foreground color' : self.__chosenActions['color'] = newValue
        elif property == 'action : measure' : self.__chosenActions['measure'] = newValue
        elif property == 'action : zoom window' : self.__chosenActions['zoomrect'] = newValue
        elif property == 'action : zoom fit or fill' : self.__chosenActions['Zoom tools'] = newValue
        elif property == 'action : zoom list' : self.__chosenActions['zoomlist'] = newValue
        elif property == 'action : x,y coordinates' : self.__chosenActions['position'] = newValue
        elif property == 'action : default color' : self.__chosenDefaultColor = newValue
        elif property == 'action : save image (place)' :
            self.__saveAction.setPlace(newValue,True)
        elif property == 'action : measure (place)':
            self.__measureAction.setPlace(newValue, True)
        elif property == 'action : save image (default path)' :
            self.__defaultSavePath = newValue
        elif property == 'action : save image (show always configure)' :
            self.__saveAction.setConfigureOnClick(newValue)

        elif property == 'fix : width' : self.__fixWidth = newValue
        elif property == 'fix : height': self.__fixHeight = newValue
        elif property == "diffractometer":
            self.diffractometerHwobj = self.getHardwareObject(newValue)
            if self.diffractometerHwobj is not None:
                self.__previous_pos_dict = self.diffractometerHwobj.getPositions()
                self.diffractometerHwobj.connect("minidiffStateChanged",
                                                 self.diffractometerChanged)
                if self.diffractometerHwobj.zoomMotor is not None:
                    zoom = self.diffractometerHwobj.zoomMotor.getPosition()
                    xSize, ySize = self.diffractometerHwobj.getCalibrationData(zoom)
                    self.diffractometerHwobj.getBeamInfo(self.__getBeamInfo)
                    beam_pos_x = self.diffractometerHwobj.getBeamPosX()
                    beam_pos_y = self.diffractometerHwobj.getBeamPosY()
 
                    self.__gridDialog.set_x_pixel_size(xSize)
                    self.__gridDialog.set_y_pixel_size(ySize)
                    self.__gridDialog.set_beam_position(beam_pos_x, beam_pos_y,
                                                        self.__beamWidth, self.__beamHeight)

    def run(self) :
        chosenActions = []

        for action in self.__wholeActions :
            if self.__chosenActions.get(action.name(), True) :
                chosenActions.append(action)

        self.__mainVideo.addAction(chosenActions)

        if not self.__chosenActions.get('update', False) :
            self.__cameraUpdate(True)

        if not self.__chosenActions.get('startCamera', False) :
            self.__cameraStart(True)

        if self.__fixWidth != -1 and self.__fixHeight != -1 :
            self.__mainVideo.view().setFixedSize(self.__fixWidth + 4,self.__fixHeight + 4)

        self.__startIdle = qt.QTimer(self)
        qt.QObject.connect(self.__startIdle,qt.SIGNAL('timeout()'),self.__idleRun)
        self.__startIdle.start(0)

    def __idleRun(self) :
        self.__startIdle.stop()
        self.__fcoloraction.setColor(self.__chosenDefaultColor)
        self.__mainVideo.view().setForegroundColor(qt.QColor(self.__chosenDefaultColor))

    def stop(self) :
        self.safeDisconnect()

    def beamSelection(self,x,y) :
        self.emit(qt.PYSIGNAL("BeamPositionChanged"), (x,y))
        self.changeBeamPosition(x,y)

    def changeBeamPosition(self, x, y, beam_width=None, beam_height=None):
        self.__beamAction.setBeamPosition(x, y)
        try:
            if not beam_width:
                beam_width = self.__beamWidth

            if not beam_height:
                beam_height = self.__beamHeight

            self.__gridDialog.set_beam_position(x, y, beam_width, beam_height)
        except:
            pass

    def changePixelScale(self,sizex,sizey) :
        self.__scaleAction.setXPixelSize(sizex)
        self.__scaleAction.setYPixelSize(sizey)
        if self.__measureDialog :
            self.__measureDialog.setXPixelSize(sizex)
            self.__measureDialog.setYPixelSize(sizey)

        self.__gridDialog.set_x_pixel_size(sizex)
        self.__gridDialog.set_y_pixel_size(sizey)

    def getView(self,key):
        try:
            key['drawing'] = self.__mainVideo.view()
            key['view']    = self.__mainVideo
            key['hwname']  = self.__hwoName
            key['dsname']  = self.__tangoName
        except:
            pass

    def getImage(self,key) :
        if self.__jpeg2image is not None :
            try:
                key['image'] = self.__jpeg2image.getLastImage()
            except:
                pass

    def __creatStdActions(self) :
        actions = []
        ####### MOUSE POSITION #######
        posaction = QubPositionAction(name="position", group="image",place="statusbar")
        actions.append(posaction)

        return actions

    def __cameraUpdate(self,onoff) :
        if onoff :
            self.__jpeg2image = _Jpeg2ImagePlug(self.__image2Pixmap)
            self.__jpegDecompress.plug(self.__jpeg2image)
            if self.camera is not None:
                imageInfo = self.camera.imageType()
            else:
                imageInfo = None
            imType    = self.__jpegDecompress.STANDARD
            if imageInfo :
                if imageInfo.type() == 'bayer': imType = self.__jpegDecompress.BAYER_RG
                elif imageInfo.type() == 'raw': imType = self.__jpegDecompress.RAW
            self.__jpegDecompress.setImageType(imType)
            self.safeConnect()
        else:
            self.safeDisconnect()
            self.__jpeg2image.setEnd()

    def __cameraStart(self, onoff) :
        if onoff :
            print "********************************************************Set the camera ON"
            if self.camera is not None:
                self.camera.setLive(True)
            else:
                print "camera is none"
        else:
            print "****************************************************Set the camera off"
            if self.camera is not None:
                print "camera :"
                print self.camera
                self.camera.setLive(False)
            else:
                print "camera is none"

    def __hide_show_zoom(self,actif) :
        if actif :
            if self.__chosenActions['Zoom tools'] :
                self.__zoomFitOrFill.setState(True)
            else:
                self.__mainVideo.setScrollbarMode('Fit2Screen')
            self.__zoomPlug.start()
            self.__zoomVideo.show()
            splitterWidth = self.__splitter.width()
            self.__splitter.setSizes([splitterWidth/3,splitterWidth - splitterWidth/3])
        else:
            if self.__chosenActions['Zoom tools'] :
                self.__zoomFitOrFill.setState(False)
            else:
                self.__mainVideo.setScrollbarMode('Auto')
            self.__zoomPlug.stop()
            self.__zoomVideo.hide()

    def _measure_dialog_new(self,openDialogAction,aQubImage) :
        try :
            self.__measureDialog = QubMeasureListDialog(self,
                                                        canvas=aQubImage.canvas(),
                                                        matrix=aQubImage.matrix(),
                                                        eventMgr=aQubImage)
            xSize,ySize = self.__scaleAction.xPixelSize(),self.__scaleAction.yPixelSize()
            self.__measureDialog.setXPixelSize(xSize)
            self.__measureDialog.setYPixelSize(ySize)
            self.__measureDialog.connect(aQubImage, qt.PYSIGNAL("ForegroundColorChanged"),
                                         self.__measureDialog.setDefaultColor)
            openDialogAction.setDialog(self.__measureDialog)
        except:
            import traceback
            traceback.print_exc()

    def _grid_dialog_connect_hdlr(self,openDialogAction, aQubImage) :
        try :
            self.__gridDialog.set_qub_event_mgr(aQubImage)
            openDialogAction.setDialog(self.__gridDialog)
        except:
            import traceback
            traceback.print_exc()

    def __getBeamInfo(self, ret):
        self.__beamWidth = float(ret["size_x"])
        self.__beamHeight = float(ret["size_y"])
        #self.__beamShape = ret["shape"]

    def _save_dialog_new(self,openDialogAction,aQubImage) :
        saveDialog = QubSaveImageDialog(self,matrix=aQubImage.matrix(),canvas=aQubImage.canvas())
        saveDialog.setImage2Pixmap(self.__image2Pixmap)
        saveDialog.setSavePath(self.__defaultSavePath)
        openDialogAction.setDialog(saveDialog)

    def instanceMirrorChanged(self,mirror):
        #print "INSTANCEMIRRORCHANGED",mirror,BlissWidget.isInstanceMirrorAllow()
        return
        if BlissWidget.isInstanceModeSlave():
            if BlissWidget.isInstanceMirrorAllow():
                self.safeConnect()
            else:
                self.safeDisconnect()

    def diffractometerChanged(self, *args):
        """
        Handles diffractometer change events, connected to the signal 
        minidiffStateChanged of the diffractometer hardware object.
        """
        
        if self.diffractometerHwobj.isReady():
            pos_dict = self.diffractometerHwobj.getPositions()
            p1 = self.diffractometerHwobj.motor_positions_to_screen(self.__previous_pos_dict)
            p2 = (self.diffractometerHwobj.getBeamPosX(), self.diffractometerHwobj.getBeamPosY())

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            if dy != 0:
                self.__gridDialog.move_grid_ver(-dy)

            if dx != 0:
                self.__gridDialog.move_grid_hor(-dx)

            #print dx, dy

            self.__previous_pos_dict = pos_dict


class _MainVideoPlug(QubPixmapZoomPlug) :
    def __init__(self,receiver,zoomAction) :
        QubPixmapZoomPlug.__init__(self,receiver)
        self.__firstPixmap = True
        self.__zoomAction = zoomAction

    def setPixmap(self,pixmap,image) :
        if self.__firstPixmap :         # INIT
            self.__firstPixmap = False
            width,height = image.width() / 2,image.height() / 2
            self.__zoomAction.initSelection(width / 2,height / 2,width,height)
        self._receiver.setPixmap(pixmap, image)
        return False

class _ZoomPlug(QubPixmapZoomPlug) :
    def __init__(self,receiver) :
        QubPixmapZoomPlug.__init__(self,receiver)
        self.__actif = True
        self.__inPoll = False

    def setPixmap(self,pixmap,image) :
        if self.__actif :
            QubPixmapZoomPlug.setPixmap(self,pixmap,image)
        else :
            self.__inPoll = False
        return not self.__actif

    def setPoller(self,poller) :
        self.__poller = poller

    def start(self) :
        self.__actif = True
        if not self.__inPoll :
            self.__poller.plug(self)
            self.__inPoll = True
    def stop(self) :
        self.__actif = False

class _Jpeg2ImagePlug(QubStdData2ImagePlug) :
    def __init__(self,receiver) :
        QubStdData2ImagePlug.__init__(self)
        self.__receiver = receiver

    def setImage(self,imagezoomed,fullimage) :
        self.__lastImage = fullimage
        self.__receiver.putImage(imagezoomed,fullimage)
        return False

    def getLastImage(self) :
        return self.__lastImage

class _rectangleZoom :
    def __init__(self,action,plug) :
        self.__plug = plug
        self.__action = action
        qt.QObject.connect(action,qt.PYSIGNAL('RectangleSelected'),self.__cbk)

    def __del__(self) :
        qt.QObject.disconnect(self.__action,qt.PYSIGNAL('RectangleSelected'),self.__cbk)

    def __cbk(self,drawingMgr) :
        rect = drawingMgr.rect()
        zoomClass = self.__plug.zoom()
        zoom = zoomClass.zoom()
        zoomClass.setRoiNZoom(rect.x(),rect.y(),
                              rect.width(),rect.height(),*zoom)


