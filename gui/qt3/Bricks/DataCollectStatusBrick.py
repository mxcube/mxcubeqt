from qt import *
from DataCollectBrick2 import readonlyLineEdit
from DataCollectBrick2 import LineEditInput
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
import logging
import os,sys
from Qub.Data.Source.QubADSC import QubADSC
from Qub.Data.Source.QubMarCCD import QubMarCCD
from Qub.CTools import pixmaptools

try:
    from Bruker import Bruker
except:
    pass


__category__ = 'mxCuBE'

DATACOLLECTSTATUS_GUI_EVENT = QEvent.User
class DataCollectStatusGUIEvent(QCustomEvent):
    def __init__(self, method, arguments):
        QCustomEvent.__init__(self, DATACOLLECTSTATUS_GUI_EVENT)
        self.method = method
        self.arguments = arguments

class DetectorImage(QLabel):
    NO_IMAGE_FILE = "blank_thumbnail.jpeg"
    IMAGE_DELAY = 2500
    IMAGE_TIMEOUT = 1000
    TIMEOUT_RETRIES = 5
    THUMBNAIL_SIZE = 250

    def __init__(self,*args):
        QLabel.__init__(self,*args)
        self.setFixedSize(DetectorImage.THUMBNAIL_SIZE,DetectorImage.THUMBNAIL_SIZE)
        self.noImagePixmap=Icons.load(DetectorImage.NO_IMAGE_FILE)
        self.wantedImage=None
        self.waitingImage=None
        self.delayTimer=QTimer(self)
        QObject.connect(self.delayTimer,SIGNAL('timeout()'),self.readImage)
        self.timeoutTimer=QTimer(self)
        QObject.connect(self.timeoutTimer,SIGNAL('timeout()'),self.rereadImage)
        self.retries=None
        self.dataArray = []

    def clearImage(self):
        self.setPixmap(self.noImagePixmap)

    def setImage(self,directory,template,image_number,filename=None,delay=True):
        self.wantedImage=[directory,template,image_number,filename]
        self.setImageUpdated(delay)

    def readImage(self):
        if self.waitingImage[3] is not None:
            full_filename=self.waitingImage[3]
            filename_sans_ext,template_ext=os.path.splitext(full_filename)
        else:
            template_file,template_ext=os.path.splitext(self.waitingImage[1])
            template_prefix_list=template_file.split("_")
            cardinals=template_prefix_list.pop(-1)
            digits=cardinals.count("#")
            format="%%0%dd" % digits
            img_number_str=format % self.waitingImage[2]
            template_prefix_list.append(img_number_str)
            final_filename="_".join(template_prefix_list)
            full_filename=os.path.join(self.waitingImage[0],"%s%s" % (final_filename,template_ext))

        format_reader=None
        if template_ext==".img":
            format_reader=QubADSC()
        elif template_ext==".mccd":
            format_reader=QubMarCCD()            
        elif template_ext==".gfrm":
            format_reader=Bruker()
        
        
        if format_reader is not None:
            try:
                fd = file(full_filename)
                read_handler = format_reader.readHandler(fd)
                data_array = read_handler.get()
                self.dataArray = data_array
            except:
                self.retries-=1
                if self.retries>0:
                    self.readRetry()
                else:
                    self.retries=None
                    if self.wantedImage is None:
                        self.clearImage()

                    self.readFailed(full_filename)

                    self.waitingImage=None
                    if self.wantedImage is not None:
                        self.setImageUpdated(False)
            else:
                try:
                    img_headers=read_handler.info()
                except:
                    img_headers={}
                self.readSuccessful(full_filename,data_array,img_headers)
                self.waitingImage=None
                if self.wantedImage is not None:
                    self.setImageUpdated(False)
            try:
                fd.close()
            except:
                pass
        else:
            self.readFailed(full_filename)

    def readRetry(self):
        self.delayTimer.start(DetectorImage.IMAGE_TIMEOUT,True)

    def readFailed(self,filename):
        self.emit(PYSIGNAL("imageUpdated"),(filename,self.waitingImage[2],False))

    def readSuccessful(self,filename,data_array,image_headers):
        palette = pixmaptools.LUT.Palette(pixmaptools.LUT.Palette.REVERSEGREY)
        qimage,(minVal,maxVal) = pixmaptools.LUT.map_on_min_max_val(data_array,palette,pixmaptools.LUT.LOG)
        qimage = qimage.scale(250,250,qimage.ScaleMin)
        #qimage = qimage.smoothScale(250,250,qimage.ScaleMin)
        self.setPixmap(QPixmap(qimage))
        self.emit(PYSIGNAL("imageUpdated"),(filename,self.waitingImage[2],True))

    def rereadImage(self):
        self.readImage()

    def setImageUpdated(self,delay=True):
        if self.waitingImage is None and self.wantedImage is not None:
            self.waitingImage=self.wantedImage
            self.wantedImage=None
            wait=0
            if delay:
                wait=DetectorImage.IMAGE_DELAY
            self.retries=DetectorImage.TIMEOUT_RETRIES
            self.delayTimer.start(wait,True)
    
            
    def getDataArray(self):
        return self.dataArray
    
    

class DataCollectStatusBrick(BlissWidget):
    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        self.oscillationId=None
        self.oscillationInfo=None

        self.dbServer=None
        self.collectObj=None

        self.dataCollectionThreads=[]

        self.addProperty('dataCollect','string','')
        self.addProperty('icons','string','')

        self.defineSlot('setOscillation',())

        results_box=QVBox(self)
        self.resultsBox = QWidget(results_box)
        QGridLayout(self.resultsBox, 7, 3, 1, 2)

        label1=QLabel("Collection status:",self.resultsBox)
        self.resultsBox.layout().addWidget(label1, 0, 0)

        status_box=QHBox(self.resultsBox)
        self.resultStatus=readonlyLineEdit(status_box)
        HorizontalSpacer3(status_box)
        self.resultMessage=readonlyLineEdit(status_box)
        self.resultsBox.layout().addMultiCellWidget(status_box,0,0,1,2)

        label2=QLabel("Date and time:",self.resultsBox)
        self.resultsBox.layout().addWidget(label2, 1, 0)
        self.resultTime=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addMultiCellWidget(self.resultTime,1,1,1,2)

        label3=QLabel("Directory:",self.resultsBox)
        self.resultsBox.layout().addWidget(label3, 2, 0)
        self.resultDirectory=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addMultiCellWidget(self.resultDirectory,2,2,1,2)

        label4=QLabel("File template:",self.resultsBox)
        self.resultsBox.layout().addWidget(label4, 3, 0)
        self.resultTemplate=readonlyLineEdit(self.resultsBox)
        self.resultsBox.layout().addMultiCellWidget(self.resultTemplate,3,3,1,2)

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
        self.resultsBox.layout().addMultiCellWidget(images_box,4,4,1,2)
        self.currentImageNumber=None

        #label7=QLabel("Image comments",self.resultsBox)
        #self.resultsBox.layout().addWidget(label7, 5, 0)
        #self.resultImageComments=LineEditInput(self.resultsBox)
        #self.resultsBox.layout().addWidget(self.resultImageComments,5,1)

        label6=QLabel("Collection comments:",self.resultsBox)
        #self.resultsBox.layout().addWidget(label6, 6, 0)
        self.resultsBox.layout().addWidget(label6, 5, 0)
        self.commentsBox=QHBox(self.resultsBox)
        self.resultComments=LineEditInput(self.commentsBox)
        self.resultsBox.layout().addWidget(self.commentsBox, 5, 1)
        self.connect(self.resultComments, PYSIGNAL("returnPressed"), self.updateComments)

        self.commentsButton=QToolButton(self.resultsBox)
        self.commentsButton.setUsesTextLabel(True)
        self.commentsButton.setTextLabel("Update ISPyB")
        self.commentsButton.setTextPosition(QToolButton.BesideIcon)
        #self.resultsBox.layout().addMultiCellWidget(self.commentsButton,5,6,2,2)
        self.resultsBox.layout().addWidget(self.commentsButton,5,2)
        QObject.connect(self.commentsButton, SIGNAL("clicked()"), self.updateComments)

        VerticalSpacer(results_box)

        self.imageDisplay=DetectorImage(self)
        self.connect(self.imageDisplay,PYSIGNAL('imageUpdated'), self.detectorImageUpdated)

        QHBoxLayout(self)
        self.layout().addWidget(results_box)
        self.layout().addWidget(self.imageDisplay)

        self.setEnabled(False)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'dataCollect':
            if self.collectObj is not None:
                self.disconnect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.updateOscillation)
                self.disconnect(self.collectObj, PYSIGNAL('collectImageTaken'), self.imageCollected)
            self.collectObj=self.getHardwareObject(newValue)
            if self.collectObj is not None:
                self.connect(self.collectObj, PYSIGNAL('collectOscillationFinished'), self.updateOscillation)
                self.connect(self.collectObj, PYSIGNAL('collectImageTaken'), self.imageCollected)
                self.dbServer=self.collectObj.dbServerHO()

        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.commentsButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def customEvent(self,event):
        if self.isRunning():
            if event.type() == DATACOLLECTSTATUS_GUI_EVENT:
                try:
                    method=event.method
                    arguments=event.arguments
                except Exception,diag:
                    logging.getLogger().exception("DataCollectStatusBrick: problem in event! (%s)" % str(diag))
                except:
                    logging.getLogger().exception("DataCollectStatusBrick: problem in event!")
                else:
                    #logging.getLogger().debug("DataCollectStatusBrick: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method(*arguments)
                        except Exception,diag:
                            logging.getLogger().exception("DataCollectStatusBrick: uncaught exception! (%s)" % str(diag))
                        except:
                            logging.getLogger().exception("DataCollectStatusBrick: uncaught exception!")
                        else:
                            #logging.getLogger().debug("DataCollectStatusBrick: custom event finished")
                            pass
                    else:
                        logging.getLogger().warning('DataCollectStatusBrick: uncallable custom event!')

    def run(self):
        self.clearImage()

    def clearImage(self):
        self.imageDisplay.clearImage()

    def setCollectionComments(self,datacollection_dict):
        try:
            col_id=int(datacollection_dict['dataCollectionId'])
            collect_dict=self.oscillationInfo[3]
        except:
            pass
        else:
            try:
                datacollectionid=int(collect_dict['collection_datacollectionid'])
            except:
                pass
            else:
                if col_id==datacollectionid:
                    try:
                        comments=datacollection_dict['comments']
                    except:
                        pass
                    else:
                        if comments is None:
                            comments=""
                        self.resultComments.setText(comments)

    def fontChange(self,oldFont):
        self.resultStatus.setFixedWidth(self.fontMetrics().width("#FINISHED.#"))

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

    def imageCollected(self,image_number):
        #print "DataCollectStatusBrick.imageCollected",osc_id,image_number,self.oscillationId,self.oscillationInfo
        if self.oscillationInfo is None:
            return
        if self.radioBox.selectedId()==0:
            image=int(self.oscillationInfo[3]['oscillation_sequence'][0]['start_image_number'])+image_number-1
            template=self.oscillationInfo[3]['fileinfo']['template']
            directory=self.oscillationInfo[3]['fileinfo']['directory']
            self.imageDisplay.setImage(directory,template,image)

    def imageTextChanged(self,img_number):
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
                self.imageDisplay.setImage(self.oscillationInfo[3]['fileinfo']['directory'],template,img_number,delay=False)

    def detectorImageUpdated(self,filename,image_number,state):
        self.currentImageNumber=image_number
        if image_number is not None:
            self.imageNumber.blockSignals(True)
            self.imageNumber.setValue(image_number)
            self.imageNumber.blockSignals(False)
        if self.radioBox.selectedId()==1:
            self.imageNumber.editor().setPaletteBackgroundColor(QWidget.white)

    def setOscillation(self,osc_id):
        #print "DataCollectResultsWidget.setOscillation",osc_id

        if osc_id is None or self.collectObj is None:
            self.clearImage()
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

        osc_info=self.collectObj.getOscillation(osc_id)
        #print "DataCollectResultsWidget.setOscillation",osc_id,osc_info

        if osc_info is not None:
            if self.oscillationId!=osc_id:
                self.clearImage()
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

        if osc_info is not None and self.oscillationId!=osc_id:
            if self.imageNumber.value()==first_image:
                self.imageNumber.valueChange()
            else:
                self.imageNumber.setValue(first_image)

        self.oscillationId=osc_id

        ### AVOID THIS AS MUCH AS POSSIBLE! WATCHOUT FOR REFRESH/UPDATE
        if self.dbServer is not None and datacollectionid is not None:
            get_collection_thread=GetDataCollectionThread(self,datacollectionid,self.dbServer)
            get_collection_thread.start()
            self.dataCollectionThreads.append(get_collection_thread)

        self.setEnabled(True)

    def updateOscillation(self,owner,state,message,col_id,oscillation_id,*args):
        if self.oscillationInfo is None:
            return
        if self.oscillationId == oscillation_id:
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

class GetDataCollectionThread(QThread):
    def postDataCollectionEvent(self,datacollection):
        method=DataCollectStatusBrick.setCollectionComments
        arguments=(self.Brick,datacollection)
        custom_event=DataCollectStatusGUIEvent(method,arguments)
        self.postEvent(self.Brick,custom_event)

    def __init__(self,brick,datacollection_id,db_connection):
        QThread.__init__(self)
        self.Brick=brick
        self.dataCollectionId=datacollection_id
        self.dbConnection=db_connection

    def run(self):
        datacollection=self.dbConnection.getDataCollection(self.dataCollectionId)
        try:
            int(datacollection['dataCollectionId'])
        except:
            pass
        else:
            self.postDataCollectionEvent(datacollection)
