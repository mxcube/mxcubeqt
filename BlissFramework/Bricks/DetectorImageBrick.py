from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils import VideoDisplay
from qt import *
import types
import logging

'''
Brick to handle CCD detector images (Mar or ADSC)
'''

__category__ = 'Instrument'

class VerticalSpacer(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        
class DetectorImageBrick(BlissWidget):
    def __init__(self, *args, **kwargs):
        BlissWidget.__init__(self, *args, **kwargs)

        self.imgClient = None
        self.zoom = 1
        self.contrast = 400
        self.cx = 0.5
        self.cy = 0.5
        self.filename = ""
        
        self.addProperty("mnemonic", "string")
        self.defineSignal("imageTransferStarted", ("filename", ))
        self.defineSignal("imageTransferCompleted", ("filename", ))

        imageBox = QVBox(self)
        self.lblStatus = QLabel(imageBox)
        self.imageWidget = VideoDisplay.VideoDisplayWidget(imageBox, 600, 600)
        self.imageWidget.setCursor(QCursor(QCursor.PointingHandCursor))
        self.imageWidget.installEventFilter(self)

        controlBox = QVBox(self)
        controlBox.setMargin(5)
        controlBox.setSpacing(10)
        controlBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        zoomBox = QVBox(controlBox)
        QLabel("zoom", zoomBox)
        self.zoomLevel = QSlider(1, 100, 25, 1, Qt.Horizontal, zoomBox)
        self.zoomLevel.setTickmarks(QSlider.Both)
        self.zoomLevel.setTracking(False)
        contrastBox = QVBox(controlBox)
        QLabel("contrast", contrastBox)
        self.contrastLevel = QSlider(1, 800, 100, 400, Qt.Horizontal, contrastBox)
        self.contrastLevel.setTickmarks(QSlider.Both)
        self.contrastLevel.setTracking(False)
        self.lblInfo = QLabel(controlBox)
        self.lblInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmdResetZoom = QPushButton("reset zoom", controlBox)
        VerticalSpacer(controlBox)

        QObject.connect(self.cmdResetZoom, SIGNAL("clicked()"), self.resetZoom)
        QObject.connect(self.zoomLevel, SIGNAL("valueChanged(int)"), self.zoomLevelChanged)
        QObject.connect(self.contrastLevel, SIGNAL("valueChanged(int)"), self.contrastLevelChanged)

        QHBoxLayout(self, 5, 5)
        self.layout().addWidget(imageBox)
        self.layout().addWidget(controlBox)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        

    def getImage(self):
        if self.imgClient is not None and len(self.filename):
            self.imgClient.setContrast(self.contrast)
            self.imgClient.getImage(self.filename, self.zoom, self.cx, self.cy)


    def zoomLevelChanged(self, newval):
        self.zoom=newval
        self.getImage()


    def resetZoom(self):
        self.zoom=1
        self.cx=0.5
        self.cy=0.5
        self.zoomLevel.setValue(1)
        self.getImage()


    def contrastLevelChanged(self, newval):
        self.contrast=newval
        self.getImage()


    def imageTransferStarted(self, filename):
        self.emit(PYSIGNAL("imageTransferStarted"), (filename, ))

        self.lblStatus.setText("loading %s..." % filename)
        self.setCursor(QCursor(QCursor.BusyCursor))
        self.imageWidget.setCursor(QCursor(QCursor.BusyCursor))
        

    def imageTransferCompleted(self, img_info):
        self.filename = img_info["filename"]
        del img_info["filename"]
        self.emit(PYSIGNAL("imageTransferCompleted"), (self.filename, ))

        self.lblStatus.setText(self.filename)
        self.setCursor(QCursor(QCursor.ArrowCursor))
        self.imageWidget.setCursor(QCursor(QCursor.PointingHandCursor))

        s = "<table>"
        for info_item, item_val in img_info.iteritems():
            if type(item_val) == types.FloatType:
                item_val_s = "%.3f" % item_val
            else:
                item_val_s = str(item_val)
            s = s + "<tr><td>%s</td><td><b>%s</b></td></tr>" % (info_item, item_val_s)
        s=s+"</table>"
        self.lblInfo.setText(s)
        

    def imageReceived(self, jpeg_data):
        self.imageWidget.setImageData(jpeg_data)
        

    def propertyChanged(self, property, oldval, newval):
        if property == 'mnemonic':
            self.imgClient = self.getHardwareObject(newval)

            if self.imgClient is not None:
                self.imgClient.setSize(600, 600)
                self.imgClient.setContrast(self.contrast)
                
                self.imgClient.connect("transferStarted", self.imageTransferStarted)
                self.imgClient.connect("transferCompleted", self.imageTransferCompleted)
                self.imgClient.connect("imageReceived", self.imageReceived)
                
                self.getImage()

                self.setEnabled(True)
            else:
                self.setEnabled(False)


    def eventFilter(self, o, event):
        if event.type() == QEvent.Wheel:
            # 1 'wheel delta' = 120, we say 1wd=5 zoom units
            try:
                wd=120; zd=5
                deltas=event.delta()
                self.zoom+= (deltas*zd)/wd
                self.zoomLevel.setValue(self.zoom)
            except:
                logging.getLogger().exception("bla")
            self.getImage()
        elif event.type() == QEvent.MouseButtonPress:
            self.pos1 = (event.x(), event.y())
        elif event.type() == QEvent.MouseButtonRelease:
            dx = self.pos1[0]-event.x()
            dy = self.pos1[1]-event.y()
            self.cx += dx*0.5/300
            self.cy += dy*0.5/300
            
            self.getImage()
         
        return False
    

    
