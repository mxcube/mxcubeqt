#$Id: RunStopPanel.py,v 1.1 2004/08/10 10:05:41 guijarro Exp $
from qt import *

from BlissFramework import Icons

class RunStopPanel(QHBox):
    def __init__(self, parent):
        QHBox.__init__(self, parent)

        self.setMargin(10)
        self.setSpacing(10)

        self.cmdLaunch = QToolButton(self)
        self.cmdStop = QToolButton(self)
        self.cmdLaunch.setIconSet(QIconSet(Icons.load('launch'))) #QPixmap(Icons.runXPM)))
        self.cmdStop.setIconSet(QIconSet(Icons.load('stop'))) #QPixmap(Icons.stopXPM)))
        self.cmdLaunch.setTextLabel('Go')
        self.cmdStop.setTextLabel('Stop')
        self.cmdLaunch.setTextPosition(QToolButton.BelowIcon)
        self.cmdStop.setTextPosition(QToolButton.BelowIcon)
        self.cmdLaunch.setUsesTextLabel(True)
        self.cmdStop.setUsesTextLabel(True)

        self.connect(self.cmdLaunch, SIGNAL('clicked()'), PYSIGNAL('launch'))
        self.connect(self.cmdStop, SIGNAL('clicked()'), PYSIGNAL('stop'))
       
        self.disableStop()
    

    def disableStop(self):
        self.cmdStop.setEnabled(False)


    def disableStart(self):
        self.cmdLaunch.setEnabled(False)


    def enableStop(self):
        self.cmdStop.setEnabled(True)


    def enableStart(self):
        self.cmdLaunch.setEnabled(True)
