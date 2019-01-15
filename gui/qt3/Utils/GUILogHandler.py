import logging
import time
import weakref

from qt import *

_logHandler = None
_timer = None


class LogEvent(QCustomEvent):
    def __init__(self, record):
        QCustomEvent.__init__(self, QEvent.User)

        self.record = record
        

def processLogMessages():
    i = 0
    while i < 10:
        if len(_logHandler.buffer) <= i:
            break
        
        record = _logHandler.buffer[i]
        
        for viewer in _logHandler.registeredViewers:
            #viewer.appendLogRecord(record)
            qApp.postEvent(viewer, LogEvent(record))
            
        i += 1
        
    del _logHandler.buffer[0:i]
    

def GUILogHandler():
    global _logHandler
    global _timer

    if _logHandler is None:
        _logHandler = __GUILogHandler()

        _timer = QTimer()
        QObject.connect(_timer, SIGNAL("timeout()"), processLogMessages)
        _timer.start(0)

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














