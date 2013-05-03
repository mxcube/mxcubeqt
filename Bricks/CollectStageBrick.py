from BlissFramework.BaseComponents import BlissWidget
from qt import *

__category__ = "mxCuBE"

STAGE_COLORS = { "UNKNOWN": None,
                 "WORKING": "yellow",
                 "DONE": "green",
                 "ERROR": "red" }

STATE_DICT = { None: "WORKING",\
               False: "ERROR",\
               True: "DONE" }

DEFAULT_TITLE = "Collect stage"

class CollectStageBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        
        self.addProperty("mnemonic", "string", "")

        self.dataCollect = None
        self.stages={}

        self.containerBox=QVGroupBox(DEFAULT_TITLE,self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(0)
        self.containerBox.setAlignment(QLabel.AlignCenter)

        self.stageBox = QWidget(self.containerBox)
        QGridLayout(self.stageBox, 6, 2, 0, 0)

        self.pic1=QLabel("<i>1.</i>",self.stageBox)
        self.stageBox.layout().addWidget(self.pic1, 0, 0)
        self.label1=QLabel("Preparing beamline",self.stageBox)
        self.stageBox.layout().addWidget(self.label1, 0, 1)

        self.pic2=QLabel("<i>2.</i>",self.stageBox)
        self.stageBox.layout().addWidget(self.pic2, 1, 0)
        self.label2=QLabel("Mounting sample",self.stageBox)
        self.stageBox.layout().addWidget(self.label2, 1, 1)

        self.pic3=QLabel("<i>3.</i>",self.stageBox)
        self.stageBox.layout().addWidget(self.pic3, 2, 0)
        self.label3=QLabel("Centring sample",self.stageBox)
        self.stageBox.layout().addWidget(self.label3, 2, 1)

        self.pic4=QLabel("<i>4.</i>",self.stageBox)
        self.stageBox.layout().addWidget(self.pic4, 3, 0)
        self.label4=QLabel("Collecting images",self.stageBox)
        self.stageBox.layout().addWidget(self.label4, 3, 1)

        #self.pic5=QLabel("<i>5.</i>",self.stageBox)
        #self.stageBox.layout().addWidget(self.pic5, 4, 0)
        #self.label5=QLabel("Unmounting sample",self.stageBox)
        #self.stageBox.layout().addWidget(self.label5, 4, 1)

        self.containerBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.dataCollect is not None:
                #self.disconnect(self.dataCollect,'collectStarted', self.collectStarted)
                self.disconnect(self.dataCollect,'collectNumberOfFrames', self.collectSpecStarted)
                #self.disconnect(self.dataCollect,'collectEnded', self.collectEnded)
                #self.disconnect(self.dataCollect,'collectFailed', self.collectFailed)
                #self.disconnect(self.dataCollect,'collectStartCentring', self.collectStartCentring)
                #self.disconnect(self.dataCollect,'collectCentringFinished', self.collectCentringFinished)
                self.disconnect(self.dataCollect,'collectValidateCentring', self.collectValidateCentring)
                self.disconnect(self.dataCollect,'collectRejectCentring', self.collectRejectCentring)
                #self.disconnect(self.dataCollect,'collectCentringFinished', self.collectCentringFinished)
                self.disconnect(self.dataCollect,'collectMountingSample', self.collectMountingSample)
                #self.disconnect(self.dataCollect,'collectUnmountingSample', self.collectUnmountingSample)
                self.disconnect(self.dataCollect,'collectOscillationStarted', self.collectOscillationStarted)
                self.disconnect(self.dataCollect,'collectOscillationFailed', self.collectOscillationFailed)
                self.disconnect(self.dataCollect,'collectOscillationFinished', self.collectOscillationFinished)
                
            self.dataCollect = self.getHardwareObject(newValue)
            if self.dataCollect is not None:
                #self.connect(self.dataCollect,'collectStarted', self.collectStarted)
                self.connect(self.dataCollect,'collectNumberOfFrames', self.collectSpecStarted)
                #self.connect(self.dataCollect,'collectEnded', self.collectEnded)
                #self.connect(self.dataCollect,'collectFailed', self.collectFailed)
                #self.connect(self.dataCollect,'collectStartCentring', self.collectStartCentring)
                #self.connect(self.dataCollect,'collectCentringFinished', self.collectCentringFinished)
                self.connect(self.dataCollect,'collectValidateCentring', self.collectValidateCentring)
                self.connect(self.dataCollect,'collectRejectCentring', self.collectRejectCentring)
                self.connect(self.dataCollect,'collectMountingSample', self.collectMountingSample)
                #self.connect(self.dataCollect,'collectUnmountingSample', self.collectUnmountingSample)
                self.connect(self.dataCollect,'collectOscillationStarted', self.collectOscillationStarted)
                self.connect(self.dataCollect,'collectOscillationFailed', self.collectOscillationFailed)
                self.connect(self.dataCollect,'collectOscillationFinished', self.collectOscillationFinished)

        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    #def collectStarted(self,owner):
    #    self.clearStages()
    #    self.setStage(1,None)

    def collectOscillationStarted(self,owner,blsampleid,barcode,location,collect_dict,oscillation_id,*args):
        self.clearStages()
        self.setStage(1,None)

        try:
            title=collect_dict['fileinfo']['prefix']
        except KeyError:
            title=DEFAULT_TITLE
        self.containerBox.setTitle(title)

    def collectOscillationFailed(self,owner,state,message,*args):
        try:
            centring_state=self.stages[3]
        except KeyError:
            pass
        else:
            self.setStage(3,False)
        try:
            self.stages[4]
        except KeyError:
            pass
        else:
            self.setStage(4,False)

    def collectOscillationFinished(self,owner,state,message,*args):
        try:
            self.stages[4]
        except KeyError:
            pass
        else:
            self.setStage(4,True)

    def collectSpecStarted(self,number_images=0):
        status = True
        self.setStage(1,True)
        try:
            self.stages[3]
        except KeyError:
            pass
        else:
            self.setStage(3,True)
        if status:
            self.setStage(4,None)
        else:
            self.setStage(4,False)

    def collectValidateCentring(self, *args):
        self.setStage(3,None)

    def collectRejectCentring(self):
        self.setStage(3,False)

    def collectMountingSample(self,barcode,location,stage):
        self.setStage(1,True)
        self.setStage(2,stage)


    def clearStages(self,after_index=0):
        self.stages={}
        unknown_color=QWidget.paletteBackgroundColor(self)
        for index in range(5-after_index):
            i=1+index+after_index
            try:
                exec("self.pic%d.setPaletteBackgroundColor(unknown_color)" % (i))
                exec("self.label%d.setPaletteBackgroundColor(unknown_color)" % (i))
            except:
                pass

    def setStage(self,stage_index,state):
        self.stages[stage_index]=state
        exec("self.pic%d.setPaletteBackgroundColor(QColor('%s'))" % (stage_index,STAGE_COLORS[STATE_DICT[state]]))
        exec("self.label%d.setPaletteBackgroundColor(QColor('%s'))" % (stage_index,STAGE_COLORS[STATE_DICT[state]]))
