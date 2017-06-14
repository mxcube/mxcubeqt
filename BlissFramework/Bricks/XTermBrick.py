# -*- coding: latin-1 -*-
"""
[Name] XTermBrick

[Description]

This brick is a simple xterm. With it you can start a command in local or remote

[Properties]
----------------------------------------------------------------------
| name                | type     | description
----------------------------------------------------------------------
| command             | string   | the command you want to execute (if empty -> simple terminal)
| users@host          | string   | the user and the host you want (if empty -> the command will be local with the same user)
| font                | string   | the terminal font
----------------------------------------------------------------------
"""

__category__ = 'GuiUtils'
__version__  = 1.0
__author__   = 'Sébastien Petitdemange'


import os,signal

import qt

from BlissFramework.BaseComponents import BlissWidget

from Qub.CTools import qttools

### Brick to display a xterm
class XTermBrick(BlissWidget) :
    def __init__(self,*args) :
        BlissWidget.__init__(self,*args)
        self.__pid = -1
        self.__cmd = None
        self.__userHost = None
        self.__stringFont = None
        self.__startIdle = qt.QTimer(self)
        qt.QObject.connect(self.__startIdle,qt.SIGNAL('timeout()'),self.__idleRun)
        
        self.__container = qttools.QtXEmbedContainer(self)
        qt.QObject.connect(self.__container, qt.SIGNAL('clientClosed()'), self.run)
        layout = qt.QVBoxLayout(self)
        layout.addWidget(self.__container)
        self.__container.setSizePolicy(qt.QSizePolicy.Expanding,qt.QSizePolicy.Expanding)
        self.__container.setSizeIncrement(1,12)
        qt.QObject.connect(qt.qApp,qt.SIGNAL('aboutToQuit()'),self.__killTerm)
        
                       ####### PROPERTY #######
        self.addProperty("command", "string", "")
        self.addProperty("users@host","string","")
        self.addProperty('font','string','')
        
    def __del__(self) :
        self.__killTerm()

    def __killTerm(self) :
        qt.QObject.disconnect(self.__container,qt.SIGNAL('clientClosed()'), self.run)
        if self.__pid > 0:
            os.kill(self.__pid,signal.SIGTERM)
            self.__pid = -1
            
    def propertyChanged(self, property, oldValue, newValue):
        if property == "command":
            self.__cmd = newValue
        elif property == "users@host":
            self.__userHost = newValue
        elif property == 'font':
            self.__stringFont = newValue
            
    def run(self) :
        if self.__pid >= 0:
            os.waitpid(self.__pid,os.WNOHANG)
            self.__pid = -1
        self.__startIdle.start(0)

    def __idleRun(self) :
        self.__startIdle.stop()
        
        self.__pid = os.fork()
        if not self.__pid:
            cmd = ['/usr/bin/env','env','xterm','-into','%d' % self.__container.winId()]
            if self.__stringFont:
                cmd.extend(['-fn',self.__stringFont])
            if self.__cmd:
                cmd.append('-e')
                if self.__userHost :
                    tmpcmd = ['ssh','-X','-t',self.__userHost,'.','~/.profile',';']
                    cmd.extend(tmpcmd)
                tmpcmd = self.__cmd.split()
                cmd.extend(tmpcmd)
            os.execl(*cmd)
            os.exit(-1)
