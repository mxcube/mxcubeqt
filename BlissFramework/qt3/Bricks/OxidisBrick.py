'''
OxidisBrick

[Description]

This brick embed oxidis in framework
'''

import os,signal
import qt

from BlissFramework.BaseComponents import BlissWidget
from Qub.CTools import qttools

__category__ = 'GuiUtils'

class OxidisBrick(BlissWidget) :
    def __init__(self,*args) :
        BlissWidget.__init__(self,*args)
        self.__pid = -1
        self.__startIdle = qt.QTimer(self)
        qt.QObject.connect(self.__startIdle,qt.SIGNAL('timeout()'),self.__idleRun)

        self.__container = qttools.QtXEmbedContainer(self)
        qt.QObject.connect(self.__container, qt.SIGNAL('clientClosed()'), self.run)
        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__container)
        self.__container.setSizePolicy(qt.QSizePolicy.Expanding,qt.QSizePolicy.Expanding)

        qt.QObject.connect(qt.qApp,qt.SIGNAL('aboutToQuit()'),self.__killOxidis)
        
    def __del__(self) :
        self.__killOxidis()

    def __killOxidis(self) :
        qt.QObject.disconnect(self.__container,qt.SIGNAL('clientClosed()'), self.run)
        if self.__pid > 0:
            os.kill(self.__pid,signal.SIGHUP)
            self.__pid = -1

    def run(self) :
        if self.__pid >= 0:
            os.waitpid(self.__pid,os.WNOHANG)
            self.__pid = -1
        self.__startIdle.start(0)

    def __idleRun(self) :
        self.__startIdle.stop()

        self.__pid = os.fork()
        if not self.__pid:
            cmd = ['/usr/bin/env','env','oxidis','--into','%d' % self.__container.winId()]
            os.execl(*cmd)
            os.exit(-1)
