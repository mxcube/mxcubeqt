from qt import *
from DataCollectParametersWidget import readonlyLineEdit
from DataCollectParametersWidget import LineEditInput
import logging
from BlissFramework import Icons
from HardwareRepository import HardwareRepository
from BlissFramework.Utils import VideoDisplay
import os

class DetectorImage(VideoDisplay.VideoDisplayWidget):
    NO_IMAGE_FILE = "no_image4.jpeg"
    CONTRAST_LEVELS = (50,125,200,275,350)
    IMAGE_DELAY = 2000
    IMAGE_TIMEOUT = 5000
    IMAGE_SIZE = 250

    def __init__(self, parent):
        VideoDisplay.VideoDisplayWidget.__init__(self,parent,DetectorImage.IMAGE_SIZE,DetectorImage.IMAGE_SIZE)

        self.setCursor(QCursor(QCursor.ArrowCursor))

        no_image=None
        self.noImageJpeg=None
        self.waitingFor=[None,None,None,None,None]
        self.currentContrast=2
        self.wantedImage=[None,None,None]
        self.currentImage=[None,None,None]
        try:
            no_image=open(Icons.getIconPath(DetectorImage.NO_IMAGE_FILE))
        except:
            pass
        else:
            try:
                self.noImageJpeg=no_image.read()
            except:
                self.noImageJpeg=None
        try:
            no_image.close()
        except:
            pass
        self.imageServer=None
        self.clearImage()

        self.delayTimer=QTimer(self)
        QObject.connect(self.delayTimer,SIGNAL('timeout()'),self.serverGetImage)
        self.timeoutTimer=QTimer(self)
        QObject.connect(self.timeoutTimer,SIGNAL('timeout()'),self.serverTimeout)

    def changeContrast(self,i):
        self.currentContrast=i
        if self.currentImage[0] is not None:
            self.setWantedImage(self.currentImage[0],self.currentImage[1],self.currentImage[2],False)

    def mouseReleaseEvent(self,event):
        pass

    def mousePressEvent(self,event):
        if self.imageServer is None:
            return
        if event.button()!= Qt.RightButton:
            return

        menu=QPopupMenu(self)
        menu.setCheckable(True)
        label=QLabel('<nobr><b>Contrast</b></nobr>',menu)
        label.setAlignment(Qt.AlignCenter)
        menu.insertItem(label)
        menu.insertSeparator()
        menu.insertItem("Darkest",0)
        menu.insertItem("Darker",1)
        menu.insertItem("Normal",2)
        menu.insertItem("Lighter",3)
        menu.insertItem("Lightest",4)
        menu.setItemChecked(self.currentContrast,True)
        QObject.connect(menu,SIGNAL('activated(int)'),self.changeContrast)
        menu.popup(QCursor.pos())

    def serverGetImage(self):
        #print "serverGetImage",self.waitingFor,"X",self.wantedImage
        self.delayTimer.stop()
        full_filename=self.waitingFor[0]
        if full_filename is None:
            return
        self.currentImage=[self.waitingFor[2],self.waitingFor[3],self.waitingFor[4]]
        self.imageServer.getImage(full_filename,\
            DetectorImage.IMAGE_SIZE,\
            DetectorImage.IMAGE_SIZE,\
            1,\
            DetectorImage.CONTRAST_LEVELS[self.currentContrast])
        self.timeoutTimer.start(DetectorImage.IMAGE_TIMEOUT)

    def serverTimeout(self):
        #print "serverTimeout",self.waitingFor
        self.timeoutTimer.stop()
        filename=self.waitingFor[0]
        image_number=self.waitingFor[4]
        self.clearImage()
        self.emit(PYSIGNAL("imageUpdated"),(filename,image_number,False))
        self.wantedImageUpdated()

    def wantedImageUpdated(self,delay=True):
        #print "wantedImageUpdated",self.waitingFor,"X",self.wantedImage
        if self.waitingFor[0] is not None:
            return
        if self.wantedImage[0] is None:
            return

        template_file,template_ext=os.path.splitext(self.wantedImage[1])
        template_prefix_list=template_file.split("_")
        cardinals=template_prefix_list.pop(-1)
        digits=cardinals.count("#")
        format="%%0%dd" % digits
        img_number_str=format % self.wantedImage[2]
        template_prefix_list.append(img_number_str)
        final_filename="_".join(template_prefix_list)
        full_filename=os.path.join(self.wantedImage[0],"%s%s" % (final_filename,template_ext))
        self.waitingFor=[full_filename,None,self.wantedImage[0],self.wantedImage[1],self.wantedImage[2]]
        self.wantedImage=[None,None,None]
        if delay:
            self.delayTimer.start(DetectorImage.IMAGE_DELAY)
        else:
            self.delayTimer.start(0)

    def setWantedImage(self,directory,template,image_number,delay=True):
        #print "setWantedImage",directory,template,image_number
        if self.imageServer is not None:
            self.wantedImage=[directory,template,image_number]
	    self.wantedImageUpdated(delay)

    def clearImage(self,current_also=False):
        #print "clearImage"
        if self.noImageJpeg is not None:
            self.setImageData(self.noImageJpeg)
        self.waitingFor=[None,None,None,None,None]
        if current_also:
            self.currentImage=[None,None,None]

    def setImageServer(self,image_server):
        #print "setImageServer",image_server
        if self.imageServer is not None:
            self.imageServer.disconnect("imageReceived", self.imageReceived)
            self.imageServer.disconnect("imageTransferCompleted", self.imageTransferCompleteqqqqd)
        self.imageServer=image_server
        if self.imageServer is not None:
            self.imageServer.connect("imageReceived", self.imageReceived)
            self.imageServer.connect("transferCompleted", self.imageTransferCompleted)

    def imageReceived(self,jpeg_data):
        #print "imageReceived",self.waitingFor
        try:
            display=self.waitingFor[1]
        except IndexError:
            display=False
        if display:
            self.timeoutTimer.stop()
            self.setImageData(jpeg_data)
            self.emit(PYSIGNAL("imageUpdated"),(self.waitingFor[0],self.waitingFor[4],True))
            self.waitingFor=[None,None,None,None,None]
            self.wantedImageUpdated()

    def imageTransferCompleted(self,img_info):
        #print "imageTransferCompleted",img_info,"X",self.waitingFor
        if img_info['filename']==self.waitingFor[0]:
            self.waitingFor[1]=True

class DataCollectResultsWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.oscillationId=None
        self.oscillationInfo=None

        self.dbServer=None

        results_box=QVBox(self)
        self.resultsBox = QWidget(results_box)
        QGridLayout(self.resultsBox, 6, 2, 1, 2)

        label1=QLabel("Status:",self.resultsBox)
        self.resultsBox.layout().addWidget(label1, 0, 0)

        status_box=QHBox(self.resultsBox)
        self.resultStatus=readonlyLineEdit(status_box)
        HorizontalSpacer3(status_box)
        self.resultMessage=readonlyLineEdit(status_box)
        self.resultsBox.layout().addWidget(status_box, 0, 1)

        label2=QLabel("Time:",self.resultsBox)
        self.resultsBox.layout().addWidget(label2, 1, 0)
        self.resultTime=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addWidget(self.resultTime, 1, 1)

        label3=QLabel("Directory:",self.resultsBox)
        self.resultsBox.layout().addWidget(label3, 2, 0)
        self.resultDirectory=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addWidget(self.resultDirectory, 2, 1)

        label4=QLabel("Template:",self.resultsBox)
        self.resultsBox.layout().addWidget(label4, 3, 0)
        self.resultTemplate=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addWidget(self.resultTemplate, 3, 1)

        label5=QLabel("Images:",self.resultsBox)
        self.resultsBox.layout().addWidget(label5, 4, 0)
        images_box=QHBox(self.resultsBox)
        self.resultImages=readonlyLineEdit(images_box)
        HorizontalSpacer3(images_box)

        self.radioBox=QHButtonGroup(images_box)
        self.radioBox.setFrameShape(self.radioBox.NoFrame)
        self.radioBox.setInsideMargin(0)
        self.radioBox.setInsideSpacing(0)            
        self.followView=QRadioButton("Follow images",self.radioBox)
        self.imageView=QRadioButton("View image:",self.radioBox)
        self.imageNumber=QSpinBox(images_box)
        self.imageNumber.setMinValue(1)
        self.imageNumber.setMaxValue(1)
        self.imageNumber.setEnabled(False)
        self.radioBox.setButton(0)
        QObject.connect(self.radioBox, SIGNAL("clicked(int)"), self.imageModeChanged)
        QObject.connect(self.imageNumber, SIGNAL("valueChanged(int)"), self.imageNumberChanged)
        QObject.connect(self.imageNumber.editor(), SIGNAL("textChanged(const QString &)"), self.imageTextChanged)
        self.resultsBox.layout().addWidget(images_box, 4, 1)
        self.currentImageNumber=None

        label6=QLabel("Comments:",self.resultsBox)
        self.resultsBox.layout().addWidget(label6, 5, 0)
        self.commentsBox=QHBox(self.resultsBox)
        self.resultComments=LineEditInput(self.commentsBox)
        self.connect(self.resultComments, PYSIGNAL("returnPressed"), self.updateComments)
        HorizontalSpacer3(self.commentsBox)
        self.commentsButton=QToolButton(self.commentsBox)
        self.commentsButton.setUsesTextLabel(True)
        self.commentsButton.setTextPosition(QToolButton.BesideIcon)
        self.commentsButton.setTextLabel("Update ISPyB")
        QObject.connect(self.commentsButton, SIGNAL("clicked()"), self.updateComments)
        self.resultsBox.layout().addWidget(self.commentsBox, 5, 1)

        VerticalSpacer(results_box)

        self.imageDisplay=DetectorImage(self)
        QObject.connect(self.imageDisplay, PYSIGNAL('imageUpdated'), self.detectorImageUpdated)

        QHBoxLayout(self)
        self.layout().addWidget(results_box)
        self.layout().addWidget(self.imageDisplay)

        self.setEnabled(False)

    def fontChange(self,oldFont):
        self.resultStatus.setFixedWidth(self.fontMetrics().width("#FINISHED.#"))

    def setDbServer(self,dbserver):
        self.dbServer=dbserver

    def setImageServer(self,image_server):
        self.imageDisplay.setImageServer(image_server)

    def updateComments(self):
        col_dict={}
        col_dict['dataCollectionId']=self.oscillationInfo[3]['collection_datacollectionid']
        col_dict['comments']=self.resultComments.text()
        self.dbServer.updateDataCollection(col_dict)

    def imageModeChanged(self,button):
        if button==0:
            self.imageNumber.setEnabled(False)
        else:
            self.imageNumber.setEnabled(True)

    def imageCollected(self,osc_id,image_number):
        if self.oscillationInfo is None:
            return
        if osc_id!=self.oscillationId:
            return
        if str(self.resultTime.text())=="" or str(self.resultTemplate.text())=="":
            self.updateOscillation(osc_id)
        if self.radioBox.selectedId()==0:
            image=int(self.oscillationInfo[3]['oscillation_sequence'][0]['start_image_number'])+image_number-1

            template=self.oscillationInfo[3]['fileinfo']['template']
            directory=self.oscillationInfo[3]['fileinfo']['directory']
            self.imageDisplay.setWantedImage(directory,template,image)

    def imageTextChanged(self,img_number):
        # set yellow color
        if self.radioBox.selectedId()==1:
            try:
                img_number=int(str(img_number))
            except (TypeError,ValueError):
                self.imageNumber.editor().setPaletteBackgroundColor(QWidget.yellow)
            else:
                if self.currentImageNumber==img_number:
                    self.imageNumber.editor().setPaletteBackgroundColor(QWidget.white)
                else:
                    self.imageNumber.editor().setPaletteBackgroundColor(QWidget.yellow)

    def imageNumberChanged(self,img_number):
        if self.oscillationInfo is None:
            return

        if self.radioBox.selectedId()==1:
            try:
                template=self.oscillationInfo[3]['fileinfo']['template']
            except KeyError:
                pass
            else:
                self.imageDisplay.setWantedImage(self.oscillationInfo[3]['fileinfo']['directory'],template,img_number,False)

    def detectorImageUpdated(self,filename,image_number,state):
        #print "DETECTOR IMAGE UPDATED",filename,image_number,state
        self.currentImageNumber=image_number
        if image_number is not None:
            self.imageNumber.blockSignals(True)
            self.imageNumber.setValue(image_number)
            self.imageNumber.blockSignals(False)
        if self.radioBox.selectedId()==1:
            self.imageNumber.editor().setPaletteBackgroundColor(QWidget.white)

    def setOscillation(self,osc_id,osc_info=None):
        #print "DataCollectResultsWidget.setOscillation",osc_id,osc_info

        if osc_id is None:
            self.imageDisplay.clearImage(True)
            self.resultStatus.setText("")
            self.resultMessage.setText("")
            self.resultTime.setText("")
            self.resultDirectory.setText("")
            self.resultTemplate.setText("")
            self.resultImages.setText("")
            self.imageNumber.blockSignals(True)
            self.imageNumber.setMinValue(1)
            self.imageNumber.setMaxValue(1)
            self.imageNumber.blockSignals(False)
            self.resultComments.setText("")
            self.setEnabled(False)
            self.oscillationId=None
            self.oscillationInfo=None
            return
        
        self.oscillationId=osc_id
        if osc_info is not None:
            self.imageDisplay.clearImage()
            self.oscillationInfo=osc_info
        collect_dict=self.oscillationInfo[3]

        try:
            datacollectionid=collect_dict['collection_datacollectionid']
        except KeyError:
            datacollectionid=None

        try:
            status=collect_dict['collection_code']
        except KeyError:
            status_msg="Ongoing..."
            status_detailed_msg=""
            self.followView.setEnabled(True)
            if osc_info is not None:
                self.radioBox.setButton(0)
                self.imageNumber.setEnabled(False)
        else:
            try:
                msg=collect_dict['collection_message']
            except KeyError:
                msg=""
            else:
                try:
                    msg=msg.replace('DataCollect: ','')
                    msg=msg[0].upper()+msg[1:]+'.'
                except IndexError:
                    msg=""
            status_detailed_msg=msg

            self.radioBox.setButton(1)
            self.imageNumber.setEnabled(True)
            self.followView.setEnabled(False)
            if status is None:
                status_msg="Stopped!"
            elif status:
                status_msg="Finished."
                status_detailed_msg=""
            else:
                status_msg="Failed!"

        try:
            start_time=collect_dict['collection_start_time']
        except KeyError:
            time_msg=""
        else:
            try:
                end_time=collect_dict['collection_end_time']
            except KeyError:
                time_msg="Started at %s" % start_time
            else:
                time_msg="From %s to %s" % (start_time,end_time)

        directory=collect_dict['fileinfo']['directory']
        try:
            template=collect_dict['fileinfo']['template']
        except KeyError:
            template=''
        first_image=int(collect_dict['oscillation_sequence'][0]['start_image_number'])
        last_image=first_image+int(collect_dict['oscillation_sequence'][0]['number_of_images'])-1
        self.imageNumber.blockSignals(True)
        self.imageNumber.setMinValue(first_image)
        self.imageNumber.setMaxValue(last_image)
        self.imageNumber.blockSignals(False)

        try:
            comments=collect_dict['comment']
        except KeyError:
            comments=""

        self.resultStatus.setText(status_msg)
        self.resultMessage.setText(status_detailed_msg)
        self.resultTime.setText(time_msg)
        self.resultDirectory.setText(directory)
        self.resultTemplate.setText(template)
        self.resultImages.setText("%d to %d" % (first_image, last_image))

        if datacollectionid is not None and self.dbServer is not None:
            self.resultComments.setReadOnly(False)
            self.commentsButton.setEnabled(True)
            # get current comments from ispyb (new thread? :P)!
            self.resultComments.setText("")
        else:
            self.resultComments.setText(comments)
            self.resultComments.setReadOnly(True)
            self.commentsButton.setEnabled(False)

        if osc_info is not None:
            if self.imageNumber.value()==first_image:
                self.imageNumber.valueChange()
            else:
                self.imageNumber.setValue(first_image)

        self.setEnabled(True)

    def updateOscillation(self,osc_id):
        if self.oscillationInfo is None:
            return
        if self.oscillationId == osc_id:
            self.setOscillation(self.oscillationId)

    def setUpdateIcon(self,icon_name):
        self.commentsButton.setPixmap(Icons.load(icon_name))

class VerticalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)

class HorizontalSpacer3(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
    def sizeHint(self):
        return QSize(4,0)
