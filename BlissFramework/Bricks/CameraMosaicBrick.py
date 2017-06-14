"""
CameraMosaicBrick

[Description]

This brick can display several images in mosaic

[Slots]

----------------------------------------------------------------------
| name                | arguments                         | description
----------------------------------------------------------------------
| getView             | a Dictionary                      |  return a dictionnary whith 2 key : 'view' (QubPixmapDisplayView Object) to add external action and 'drawing' (QubPixmapDisplay Object) to add external drawing
----------------------------------------------------------------------

"""
import weakref
import logging
import qt

from BlissFramework.BaseComponents import BlissWidget

from Qub.Widget.QubActionSet import QubZoomListAction
from Qub.Widget.QubActionSet import QubZoomRectangle
from Qub.Widget.QubActionSet import QubZoomAction
from Qub.Widget.QubActionSet import QubForegroundColorAction
from Qub.Widget.QubActionSet import QubOpenDialogAction

from Qub.Widget.QubDialog import QubMeasureListDialog

from Qub.Objects.Mosaic.QubMosaicView import QubMosaicView

__category__ = "Camera"

class CameraMosaicBrick(BlissWidget) :
    def __init__(self,*args) :
        BlissWidget.__init__(self,*args)

        actions = []

        self.__zoomList = QubZoomListAction(place = "toolbar",
                                   zoomValList = [0.1,.25,.5,1,1.5,2,2.5,3,3.5,4],
                                   show = 1,group = "zoom")
        actions.append(self.__zoomList)

        self.__zoomFitOrFill = QubZoomAction(place = "toolbar",keepROI = True,group = "zoom")
        self.__zoomFitOrFill.setList(self.__zoomList)
        self.__zoomList.setActionZoomMode(self.__zoomFitOrFill)
        actions.append(self.__zoomFitOrFill)
        
        zoomAction = QubZoomRectangle(label='Zoom Crop',place="toolbar", show=1, group="zoom",
                                      activate_click_drag = True,drawingObjectLayer = 2 ** 31,
                                      unactiveActionWhenDub = True)
        qt.QObject.connect(zoomAction,qt.PYSIGNAL('RectangleSelected'),self.__rectangleZoomChanged)
        actions.append(zoomAction)

               ####### CHANGE FOREGROUND COLOR #######
        fcoloraction = QubForegroundColorAction(name="color", group="image")
        actions.append(fcoloraction)

                        ####### MEASURE #######
        measureAction = QubOpenDialogAction(parent=self,name='measure',iconName='measure',label='Measure',group="Tools")
        measureAction.setConnectCallBack(self._measure_dialog_new)
        actions.append(measureAction)
        
        self.__mainView = QubMosaicView(self,actions = actions)

        layout = qt.QHBoxLayout(self)
        layout.addWidget(self.__mainView)

                         ####### SLOT #######
        self.defineSlot('getView',())
                    
    def getView(self,key) :
        try:
            key['drawing'] = self.__mainView.view()
            key['view'] = self.__mainView
        except:
            pass

    def __rectangleZoomChanged(self,drawingMgr) :
        self.__zoomFitOrFill.setState(False)
        rect = drawingMgr.rect()
        canvas = self.__mainView.view()

        matrix = canvas.matrix()

        vp = canvas.viewport()
        viewWidth,viewHeight = vp.width(),vp.height()
        zoomX = float(viewWidth) / rect.width()
        zoomY = float(viewHeight) / rect.height()
        zoom = max(zoomX,zoomY)

        newMatrix = qt.QWMatrix(zoom,0,0,zoom,matrix.dx(),matrix.dy())
        rect = newMatrix.map(rect)
        zoom = min(zoom,20)
        canvas.setZoom(zoom,zoom)
        canvas.setContentsPos(rect.x(),rect.y())
        self.__zoomList.writeStrValue("%d%%" % (zoom * 100))

    def _measure_dialog_new(self,openDialogAction,aQubImage) :
        try :
            self.__measureDialog = QubMeasureListDialog(self,
                                                        canvas=aQubImage.canvas(),
                                                        matrix=aQubImage.matrix(),
                                                        eventMgr=aQubImage,
                                                        drawingObjectLayer = 2 ** 31)
            self.__measureDialog.connect(aQubImage, qt.PYSIGNAL("ForegroundColorChanged"),
                                         self.__measureDialog.setDefaultColor)
            openDialogAction.setDialog(self.__measureDialog)
        except:
            import traceback
            traceback.print_exc()
 
