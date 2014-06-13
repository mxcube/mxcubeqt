from BlissFramework.BaseComponents import BlissWidget
from qt import *
import time
from datetime import timedelta

class ProgressBarBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

	self.collectHO = None	

	self.addProperty('mnemonic', 'string', '')

        self.runningState=False
	self.time_total_sec = 0
	self.time_remaining_sec = 0
	self.time_format = None

        self.timer=QTimer(self)
        QObject.connect(self.timer,SIGNAL('timeout()'),self.cmdClock)

        self.containerBox=QHGroupBox(self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(2)

        self.time_total_label=QLabel('Total:',self.containerBox)
        self.time_total=QLabel('??:??:??',self.containerBox)

        self.progressBar=QProgressBar(self.containerBox)
        self.progressBar.setCenterIndicator(True)
	self.progressBar.setEnabled(False)

        self.time_remaining_label=QLabel('Remaining:',self.containerBox)
	self.time_remaining_label.setEnabled(False)
        self.time_remaining=QLabel('??:??:??',self.containerBox)
	self.time_remaining.setEnabled(False)
	
    
        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.layout().addWidget(self.containerBox)

        self.addProperty('appearance','combo',('simple', 'normal'),'normal')
        self.addProperty('title', 'string','')
        self.addProperty('timeFormat','string','%H:%M:%S')

        self.instanceSynchronize("")

    def run(self):
        self.barReset()

    # Slot to stop the progress bar (keeping timers and bar)
    def barStop(self, *args):
        self.timer.stop()
        self.runningState=False
	self.barReset()
	self.progressBar.setEnabled(False)
	self.time_remaining_label.setEnabled(False)
	self.time_remaining.setEnabled(False)

    # Slot to start the progress bar (starts the timer)
    def barStart(self, *args):
	self.setEnabled(True)
        self.runningState=True
        self.timer.start(1000)
	self.barReset()
	self.progressBar.setEnabled(True)
        self.time_remaining_label.setEnabled(True)
        self.time_remaining.setEnabled(True)
	
    # Slot to reset the progress bar (cleans bar and resets timers)
    def barReset(self):
        self.progressBar.reset()
	self.time_total.setText(str(timedelta(seconds=0)))
        self.time_remaining.setText(str(timedelta(seconds=0)))
        #self.emitWidgetSynchronize()
    
    # Slot to set the number of total steps
    def barTotalSteps(self,steps, time_sec):
	self.barReset()
        self.progressBar.setTotalSteps(time_sec)
	self.time_remaining_sec = time_sec
	self.time_total_sec = time_sec
	self.time_total.setText(str(timedelta(seconds = time_sec)))
	
    # Slot to set the current progress (a value between 0 and total steps)
    """def barProgress(self,progress):
        #print "barProgress",progress
        if self.runningState==True:
            p=int(str(progress))
            self.progressBar.setProgress(p)
            if p==0:
                #self..setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time.gmtime(0.0))))
                self.time_remaining.setText("??:??:??")
            elif p==self.progressBar.totalSteps():
                self.time_remaining.setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time.gmtime(0.0))))
            else:
                time_spent=time.time()-self.startTime
                time_spent_per_image=time_spent/p
                images_left=self.progressBar.totalSteps()-p
                time_left=time_spent_per_image*images_left
                time_left3=time.gmtime(time_left)
                self.time_remaining.setText(str(time.strftime(self.getProperty('timeLeftFormat').getValue(),time_left3)))
            self.emitWidgetSynchronize()"""

    # Event called every second when timer is running
    def cmdClock(self):
	self.time_remaining_sec = self.time_remaining_sec -1
	if self.time_remaining_sec > -1:
	    self.progressBar.setProgress(self.time_total_sec- self.time_remaining_sec)
	    self.time_remaining.setText(str(timedelta(seconds = int(self.time_remaining_sec))))
        #self.emitWidgetSynchronize()

    """def emitWidgetSynchronize(self):
        total_steps=self.progressBar.totalSteps()
        time_spent=str(self.time_total.text())
        time_left=str(self.time_remaining.text())
        progress=self.progressBar.progress()
        self.emit(PYSIGNAL("widgetSynchronize"),( (progress,total_steps,time_spent,time_left), ))

    def widgetSynchronize(self,state):
        progress=state[0]
        total_steps=state[1]
        time_spent=state[2]
        time_left=state[3]
        self.progressBar.setProgress(progress,total_steps)
        #self.labTi.setText(time_spent)
        self.time_remaining.setText(time_left)"""

    def propertyChanged(self, propertyName, oldValue, newValue):
        #print propertyName,oldValue,newValue
        if propertyName=='appearance':
            if newValue=='simple':
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                self.containerBox.setInsideMargin(0)
                self.containerBox.setInsideSpacing(0)            
                self.time_total_label.hide()
                self.time_total.hide()
                self.time_remaining_label.hide()
                self.time_remaining.hide()
            elif newValue=='normal':
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
                self.containerBox.setInsideSpacing(2)
                self.time_total_label.show()
                self.time_total.show()
                self.time_remaining_label.show()
                self.time_remaining.show()
        elif propertyName == 'title':
            if newValue!="":
                self.containerBox.setTitle(newValue)
                self.updateGeometry()      
	elif propertyName == 'timeFormat':
	    self.time_format=newValue
        elif propertyName == "mnemonic":
            if self.collectHO is not None:
		self.disconnect(self.collectHO, PYSIGNAL('collectOverallFramesTime'), self.barTotalSteps)
		self.disconnect(self.collectHO, PYSIGNAL('collectStarted'), self.barStart)
		self.disconnect(self.collectHO, PYSIGNAL('collectEnded'), self.barStop) 
	        #self.disconnect(self.collectHO, PYSIGNAL('collectImageTaken'), self.barProgress)
            self.collectHO = self.getHardwareObject(newValue)
            if self.collectHO is not None:
		self.connect(self.collectHO, PYSIGNAL('collectOverallFramesTime'), self.barTotalSteps)
                self.connect(self.collectHO, PYSIGNAL('collectStarted'), self.barStart)
                self.connect(self.collectHO, PYSIGNAL('collectEnded'), self.barStop)
                #self.connect(self.collectHO, PYSIGNAL('collectImageTaken'), self.barProgress)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
