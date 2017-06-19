import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
import os,sys
import glob
from BlissFramework import Icons
import qttable
import DataCollectStatusBrick
import numpy

from Qub.Data.Source.QubADSC import QubADSC
from Qub.Data.Source.QubMarCCD import QubMarCCD
from Qub.CTools import pixmaptools
from Qub.Widget import QubDataDisplay
from Qub.Widget.QubActionSet import QubLineDataSelectionAction
from Qub.Widget.QubView import QubView

__category__ = 'mxCuBE'

class DetectorImage(DataCollectStatusBrick.DetectorImage):
    def __init__(self,*args):
        DataCollectStatusBrick.DetectorImage.__init__(self,*args)
        self.setFixedSize(0,0)
    def clearImage(self):
        self.emit(PYSIGNAL("clearImage"),())
    def readFailed(self,filename):
        self.emit(PYSIGNAL("imageUpdated"),(filename,False))
    def readSuccessful(self,filename,data_array,image_headers):
        self.emit(PYSIGNAL("imageUpdated"),(filename,True,data_array,image_headers))

class ImageAnalysisBrick(BlissWidget):
    ZOOM_LEVELS = ( (0.25,"25%"), (0.5,"50%"), (1.0,"100%"),\
                    (1.5,"150%"), (2.0,"200%"), (-1,"Fit to window") )

    TABLE_WIDTH = 1.1
    KEY_WIDTH   = 1.5
    VALUE_WIDTH = 1.1

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.collectObj = None

        self.imageHeaders={}
        self.image90Contrast=None
        self.imageStdDevContrast=None
        self.currentImage=None

        self.detectorImage=DetectorImage(None)
        QObject.connect(self.detectorImage, PYSIGNAL("clearImage"), self.clearImage)
        QObject.connect(self.detectorImage, PYSIGNAL("imageUpdated"), self.detectorImageUpdated)

        filename_box=QHBox(self)
        box1=QVBox(filename_box)
        box1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.radioBox=QHButtonGroup(box1)
        self.radioBox.setFrameShape(self.radioBox.NoFrame)
        self.radioBox.setInsideMargin(0)
        self.radioBox.setInsideSpacing(0)            
        self.followView=QRadioButton("Follow images",self.radioBox)
        self.imageView=QRadioButton("Specify filename:",self.radioBox)
        self.filenameBox=QHBox(filename_box)
        self.imageFilename=QComboBox(self.filenameBox)
        self.imageFilename.setEditable(True)
        self.imageFilename.setEnabled(False)
        self.imageFilename.setDuplicatesEnabled(False)
        self.imageFilename.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        QObject.connect(self.imageFilename, SIGNAL("activated(const QString &)"), self.readCurrentImage)

        self.browseButton=QToolButton(self.filenameBox)
        self.browseButton.setUsesTextLabel(True)
        self.browseButton.setTextPosition(QToolButton.BesideIcon)
        self.browseButton.setTextLabel("Browse")
        self.browseButton.setEnabled(False)
        QObject.connect(self.browseButton,SIGNAL("clicked()"), self.browseForImages)

        HorizontalSpacer3(self.filenameBox)

        self.reloadButton=QToolButton(self.filenameBox)
        self.reloadButton.setUsesTextLabel(True)
        self.reloadButton.setTextPosition(QToolButton.BesideIcon)
        self.reloadButton.setTextLabel("Load")
        QObject.connect(self.reloadButton, SIGNAL("clicked()"), self.readCurrentImage)

        QObject.connect(self.radioBox, SIGNAL("clicked(int)"), self.imageModeChanged)
        self.radioBox.setButton(0)

        box2=QHBox(self)
        box4=QVBox(box2)

        self.imageDisplay=QubDataDisplay.QubDataDisplay(box4,noToolbarAction = True)

        box5=QHBox(box4)
        box5.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        self.lineSelection=QubLineDataSelectionAction(parent=box5,show=False,group="selection",graphLegend="")
        self.imageDisplay.addDataAction(self.lineSelection,self.lineSelection)
        self.lineSelection._graph.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.lineSelection._graph.show=lambda:QubView.show(self.lineSelection._graph)
        try:
            self.lineSelection._QubLineDataSelectionAction__printAction._widget.parent().parent().hide()
        except:
            logging.getLogger().exception("ImageAnalysisBrick: problem hiding line selection graph toolbar")

        box3=QVBox(box2)

        self.zoomBox=QVButtonGroup("Image scale",box3)
        for zoom_level in ImageAnalysisBrick.ZOOM_LEVELS:
            QRadioButton(zoom_level[1],self.zoomBox)
        self.zoomBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.zoomBox.setButton(len(ImageAnalysisBrick.ZOOM_LEVELS)-1)
        QObject.connect(self.zoomBox, SIGNAL("clicked(int)"), self.zoomLevelChanged)

        self.contrastBox=QVButtonGroup("Contrast level",box3)
        self.contrastAutoscale=QRadioButton("Spread contrast across data",self.contrastBox)
        QRadioButton("Focus on 90% of data",self.contrastBox)
        QRadioButton("Spots inverse std.deviation",self.contrastBox)
        self.contrastBox.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.contrastBox.setButton(1)
        QObject.connect(self.contrastBox, SIGNAL("clicked(int)"), self.contrastChanged)

        self.headersBox=QVGroupBox("File headers",box3)
        self.headersTable=myTable(0, 2, self.headersBox)
        self.headersTable.setLeftMargin(0)
        self.headersTable.horizontalHeader().setLabel(0,"Name")
        self.headersTable.horizontalHeader().setLabel(1,"Value")
        self.headersTable.horizontalHeader().setClickEnabled(False)
        self.headersTable.horizontalHeader().setResizeEnabled(False)
        self.headersTable.horizontalHeader().setMovingEnabled(False)
        self.headersTable.setSelectionMode(qttable.QTable.NoSelection)
        self.headersTable.setColumnReadOnly(0,True)
        self.headersTable.setColumnReadOnly(1,True)
        self.headersTable.setColumnWidth(0,self.headersTable.columnWidth(0)*ImageAnalysisBrick.KEY_WIDTH)
        self.headersTable.setColumnWidth(1,self.headersTable.columnWidth(1)*ImageAnalysisBrick.VALUE_WIDTH)
        self.headersTable.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Ignored)

        self.addProperty('icons','string')
        self.addProperty('dataCollect','string')
        self.addProperty('fileHistorySize','integer',10)
        self.addProperty('showLegends','boolean',False)
        self.addProperty('graphFixedHeight','integer',200)

        self.defineSlot('setSession',())

        QVBoxLayout(self)
        self.layout().addWidget(filename_box)
        self.layout().addWidget(box2)

    def run(self):
        self.imageFilename.clear()
        self.imageFilename.setPaletteBackgroundColor(Qt.white)
        self.imageFilename.lineEdit().setPaletteBackgroundColor(Qt.white)
        self.clearImage()
        #filename="/tmp/gabadinho/external/mx415/20070924/mx415_1_002.img"

    def updateHeaders(self,img_headers):
        self.imageHeaders=img_headers
        self.headersTable.setNumRows(0)
        for header_key in img_headers:
            header_value=img_headers[header_key]
            row=self.headersTable.numRows()
            self.headersTable.insertRows(row)
            self.headersTable.setText(row,0,str(header_key).lower())
            self.headersTable.setText(row,1,str(header_value))

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName == "icons":
            icons_list=newValue.split()
            try:
                self.browseButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
            try:
                self.reloadButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass

        elif propertyName == 'dataCollect':
            if self.collectObj is not None:
                self.disconnect(self.collectObj, PYSIGNAL('progressUpdate'), self.imageCollected)
            self.collectObj=self.getHardwareObject(newValue)
            if self.collectObj is not None:
                self.connect(self.collectObj, PYSIGNAL('progressUpdate'), self.imageCollected)

        elif propertyName == 'fileHistorySize':
            self.imageFilename.setMaxCount(newValue)

        elif propertyName == 'showLegends':
            if not newValue:
                self.lineSelection._graph.setTitle=lambda t:mySetTitle(self.lineSelection._graph,t)
                self.lineSelection._graph.enableAxis(self.lineSelection._graph.xTop,False)
                self.lineSelection._graph.enableAxis(self.lineSelection._graph.xBottom,False)            

        elif propertyName == 'graphFixedHeight':
            if newValue!=-1:
                self.lineSelection._graph.setFixedHeight(newValue)

        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None,expiration_time=0):
        self.imageFilename.clear()
        self.imageFilename.setPaletteBackgroundColor(Qt.white)
        self.imageFilename.lineEdit().setPaletteBackgroundColor(Qt.white)
        self.clearImage()

    def setImage(self,filename,delay):
        #print "setImage",filename,self.currentImage
        if filename==self.currentImage:
            return
        self.filenameBox.setEnabled(False)

        found=False
        for i in range(self.imageFilename.count()):
            f=str(self.imageFilename.text(i))
            if f==filename:
                found=True
                break
        if not found:
            self.imageFilename.insertItem(filename)
            i=self.imageFilename.count()-1
        self.imageFilename.setCurrentItem(i)
        self.imageFilename.setPaletteBackgroundColor(Qt.yellow)
        self.imageFilename.lineEdit().setPaletteBackgroundColor(Qt.yellow)
        self.detectorImage.setImage("","",0,filename,delay=delay)

    def imageCollected(self,osc_id,image_number):
        #print "ImageAnalysisBrick.imageCollected",osc_id,image_number
        if self.radioBox.selectedId()==0:
            osc_info=self.collectObj.getOscillation(osc_id)
            image=int(osc_info[3]['oscillation_sequence'][0]['start_image_number'])+image_number-1
            template=osc_info[3]['fileinfo']['template']
            directory=osc_info[3]['fileinfo']['directory']
            template_file,template_ext=os.path.splitext(template)
            template_prefix_list=template_file.split("_")
            cardinals=template_prefix_list.pop(-1)
            digits=cardinals.count("#")
            format="%%0%dd" % digits
            img_number_str=format % image
            template_prefix_list.append(img_number_str)
            final_filename="_".join(template_prefix_list)
            full_filename=os.path.join(directory,"%s%s" % (final_filename,template_ext))
            self.setImage(full_filename,True)

    def browseForImages(self):
        get_dir=QFileDialog(self)
        s=self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()
        current_filename=str(self.imageFilename.currentText())
        try:
            current_directory=os.path.split(current_filename)[0]
        except:
            current_directory="/"
        d=get_dir.getOpenFileName(current_directory,"",self,"",\
            "Select an image file","",False)
        if d is not None and len(d)>0:
            self.readCurrentImage(str(d))

    def readCurrentImage(self,filename=None):
        if filename is None:
            filename=str(self.imageFilename.currentText())
        else:
            filename=str(filename)
        self.setImage(filename,False)

    def imageModeChanged(self,button):
        if button==0:
            self.imageFilename.setEnabled(False)
            self.browseButton.setEnabled(False)
        else:
            self.imageFilename.setEnabled(True)
            self.browseButton.setEnabled(True)

    def zoomLevelChanged(self,button):
        if self.currentImage is None:
            return

        level=ImageAnalysisBrick.ZOOM_LEVELS[button][0]
        try:
            if level==-1:
                self.imageDisplay.getDrawing().setScrollbarMode("Fit2Screen")
            else:
                self.imageDisplay.getDrawing().setScrollbarMode("Auto")
                self.imageDisplay.getDrawing().setZoom(level,level)
        except:
            pass

    def contrastChanged(self,button):
        if self.currentImage is None:
            return

        try:
            colormap=self.imageDisplay.getColormapPlug()
            colormap.setLutType(pixmaptools.LUT.LOG)

            if button==0:
                colormap.setColorMapType(pixmaptools.LUT.Palette.REVERSEGREY)
                colormap.setAutoscale(True)

            elif button==1:
                colormap.setColorMapType(pixmaptools.LUT.Palette.REVERSEGREY)
                colormap.setAutoscale(False)
                try:
                    min_val=float(self.image90Contrast[0])
                    max_val=float(self.image90Contrast[1])
                except:
                    datatmp = self.imageDisplay.getData().copy()
                    datatmp = datatmp.ravel()
                    datatmp.sort()
                    cumsum = datatmp.cumsum()
                    limit = cumsum[-1] * 0.97
                    maskResult = cumsum > limit
                    max_val = datatmp[maskResult][0]
                    min_val = self.imageDisplay.getData().min()
                    self.image90Contrast=(min_val,max_val)
                colormap.setMinMax(min_val,max_val)

            elif button==2:
                colormap.setColorMapType(pixmaptools.LUT.Palette.GREYSCALE)
                colormap.setAutoscale(False)
                try:
                    min_val=float(self.imageStdDevContrast[0])
                    max_val=float(self.imageStdDevContrast[1])
                except:
                    datatmp = self.imageDisplay.getData()
                    nbValue = 1
                    for val in datatmp.shape:
                        nbValue *= val
                    integralVal = datatmp.sum() 
                    average = integralVal / nbValue
                    stdDeviation = datatmp.std()
                    min_val=average - stdDeviation
                    max_val=average + stdDeviation
                    self.imageStdDevContrast=(min_val,max_val)
                colormap.setMinMax(min_val,max_val)

            self.imageDisplay.refresh()

        except:
            pass

    def detectorImageUpdated(self,filename,status,data_array=None,image_headers=None):
        #print "ImageAnalysisBrick.detectorImageUpdated",filename,status
        self.filenameBox.setEnabled(True)

        self.image90Contrast=None
        self.imageStdDevContrast=None
        if status:
            self.imageFilename.setPaletteBackgroundColor(Qt.white)
            self.imageFilename.lineEdit().setPaletteBackgroundColor(Qt.white)
            
            try:
                self.imageDisplay.setData(data_array)
            except:
                pass

            self.lineSelection.changeLineWidth(2)
            self.lineSelection.setColor(Qt.yellow)
            self.lineSelection.setState(True)

            self.currentImage=filename
            self.contrastChanged(self.contrastBox.selectedId())
            self.zoomLevelChanged(self.zoomBox.selectedId())

            self.updateHeaders(image_headers)
        else:
            #self.clearImage() # is this really necessary?
            self.imageFilename.setPaletteBackgroundColor(Qt.red)
            self.imageFilename.lineEdit().setPaletteBackgroundColor(Qt.red)
            self.lineSelection.setState(False)

    def clearImage(self):
        #print "ImageAnalysisBrick.clearImage"
        self.currentImage=None
        self.updateHeaders(())

        try:
            self.lineSelection._curve.setData(numpy.array(()),numpy.array(()))
            self.lineSelection._graph.replot()
        except:
            pass

        try:
            self.imageDisplay.setData(None)
            self.imageDisplay.refresh()
        except:
            pass

class HorizontalSpacer3(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
    def sizeHint(self):
        return QSize(4,0)

class myTable(qttable.QTable):
    def sizeHint(self):
        size_hint=qttable.QTable.sizeHint(self)
        size_hint.setWidth(size_hint.width()*ImageAnalysisBrick.TABLE_WIDTH)
        return size_hint

def mySetTitle(obj,title):
    pass
