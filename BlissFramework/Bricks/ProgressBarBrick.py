from BlissFramework.BaseComponents import BlissWidget
from qt import *
import time

'''
Doc please...
'''

# ?
__category__ = 'GuiUtils'

class ProgressBarBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.runningState=False

        self.timer=QTimer(self)
        QObject.connect(self.timer,SIGNAL('timeout()'),self.cmdClock)

        self.containerBox=QHGroupBox(self)
        self.containerBox.setInsideMargin(4)
        self.containerBox.setInsideSpacing(2)

        self.labElapsed=QLabel('Elapsed:',self.containerBox)
        self.labTimeSpent=QLabel('??:??:??',self.containerBox)

        self.progressBar=QProgressBar(self.containerBox)
        self.progressBar.setCenterIndicator(True)

        self.labRemaining=QLabel('Remaining:',self.containerBox)
        self.labTimeLeft=QLabel('??:??:??',self.containerBox)
    
        QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        self.layout().addWidget(self.containerBox)

        self.defineSlot('barStop',()) 
        self.defineSlot('barStart',())
        self.defineSlot('barReset',())
        self.defineSlot('barTotalSteps',())
        self.defineSlot('barProgress',())       

        self.addProperty('appearance','combo',('simple', 'normal'),'normal')
        self.addProperty('title', 'string','')
        self.addProperty('timeSpentFormat','string','%H:%M:%S')
        self.addProperty('timeLeftFormat','string','%H:%M:%S')

        #self.instanceSynchronize("")

        self.setEnabled(False)

    def run(self):
        self.barReset()

    # Slot to stop the progress bar (keeping timers and bar)
    def barStop(self):
        self.timer.stop()
        self.runningState=False
        self.setEnabled(False)

    # Slot to start the progress bar (starts the timer)
    def barStart(self):
        self.setEnabled(True)
        self.runningState=True
        self.timer.start(1000)
        self.startTime=time.time()

    # Slot to reset the progress bar (cleans bar and resets timers)
    def barReset(self):
        self.progressBar.reset()
        self.labTimeSpent.setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time.gmtime(0.0))))
        self.labTimeLeft.setText(str(time.strftime(self.getProperty('timeLeftFormat').getValue(),time.gmtime(0.0))))
        self.emitWidgetSynchronize()
    
    # Slot to set the number of total steps
    def barTotalSteps(self,steps):
        s=int(str(steps))
        self.progressBar.setTotalSteps(s)

    # Slot to set the current progress (a value between 0 and total steps)
    def barProgress(self,progress):
        #print "barProgress",progress
        if self.runningState==True:
            p=int(str(progress))
            self.progressBar.setProgress(p)
            if p==0:
                self.labTimeSpent.setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time.gmtime(0.0))))
                self.labTimeLeft.setText("??:??:??")
            elif p==self.progressBar.totalSteps():
                self.labTimeLeft.setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time.gmtime(0.0))))
            else:
                time_spent=time.time()-self.startTime
                time_spent_per_image=time_spent/p
                images_left=self.progressBar.totalSteps()-p
                time_left=time_spent_per_image*images_left
                time_left3=time.gmtime(time_left)
                self.labTimeLeft.setText(str(time.strftime(self.getProperty('timeLeftFormat').getValue(),time_left3)))
            self.emitWidgetSynchronize()

    # Event called every second when timer is running
    def cmdClock(self):
        time_spent=time.time()-self.startTime
        time_spent2=time.gmtime(time_spent)
        self.labTimeSpent.setText(str(time.strftime(self.getProperty('timeSpentFormat').getValue(),time_spent2)))
        self.emitWidgetSynchronize()

    def emitWidgetSynchronize(self):
        total_steps=self.progressBar.totalSteps()
        time_spent=str(self.labTimeSpent.text())
        time_left=str(self.labTimeLeft.text())
        progress=self.progressBar.progress()
        self.emit(PYSIGNAL("widgetSynchronize"),( (progress,total_steps,time_spent,time_left), ))

    def widgetSynchronize(self,state):
        progress=state[0]
        total_steps=state[1]
        time_spent=state[2]
        time_left=state[3]
        self.progressBar.setProgress(progress,total_steps)
        self.labTimeSpent.setText(time_spent)
        self.labTimeLeft.setText(time_left)

    def propertyChanged(self, propertyName, oldValue, newValue):
        #print propertyName,oldValue,newValue
        if propertyName=='appearance':
            if newValue=='simple':
                self.containerBox.setFrameShape(self.containerBox.NoFrame)
                self.containerBox.setInsideMargin(0)
                self.containerBox.setInsideSpacing(0)            
                self.labElapsed.hide()
                self.labTimeSpent.hide()
                self.labRemaining.hide()
                self.labTimeLeft.hide()
            elif newValue=='normal':
                self.containerBox.setFrameShape(self.containerBox.GroupBoxPanel)
                self.containerBox.setInsideMargin(4)
                self.containerBox.setInsideSpacing(2)
                self.labElapsed.show()
                self.labTimeSpent.show()
                self.labRemaining.show()
                self.labTimeLeft.show()
        if propertyName=='title':
            if newValue!="":
                self.containerBox.setTitle(newValue)
                self.updateGeometry()      
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
