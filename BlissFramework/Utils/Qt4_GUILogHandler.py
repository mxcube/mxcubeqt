#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
import weakref

from PyQt4 import QtCore

_logHandler = None
_timer = None


#class LogEvent(QtCore.QCustomEvent):
class LogEvent(QtCore.QEvent):
    def __init__(self, record):
        #QCustomEvent.__init__(self, QEvent.User)
        QtCore.Event.__init__(self, QtCore.QEvent.User)

        self.record = record
        

def processLogMessages():
    i = 0
    while i < 10:
        if len(_logHandler.buffer) <= i:
            break
        
        record = _logHandler.buffer[i]
        
        for viewer in _logHandler.registeredViewers:
            #viewer.appendLogRecord(record)
            QtGui.QApplication.postEvent(viewer, LogEvent(record))
            
        i += 1
        
    del _logHandler.buffer[0:i]
    

def GUILogHandler():
    global _logHandler
    global _timer

    if _logHandler is None:
        _logHandler = __GUILogHandler()

        _timer = QtCore.QTimer()
        QtCore.QObject.connect(_timer, QtCore.SIGNAL("timeout()"), processLogMessages)
        print "timer - fix"
        _timer.start(10)

    return _logHandler


class LogRecord:
    def __init__(self, record):
        self.name = record.name
        self.levelno = record.levelno
        self.levelname = record.levelname
        self.time = record.created
        self.message = record.getMessage()


    def getName(self):
        return self.name
        

    def getLevel(self):
        return self.levelno


    def getLevelName(self):
        return self.levelname


    def getDate(self):
        return time.strftime('%Y-%m-%d', time.localtime(self.time))

    
    def getTime(self):
        return time.strftime('%H:%M:%S', time.localtime(self.time))

    
    def getMessage(self):
        return self.message
    

class __GUILogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        
        self.buffer = []

        self.registeredViewers = weakref.WeakKeyDictionary()
        

    def register(self, viewer):
        self.registeredViewers[viewer] = ''

        for rec in self.buffer:
            viewer.appendLogRecord(rec)
                    
    
    def emit(self, record):
        self.buffer.append(LogRecord(record))














