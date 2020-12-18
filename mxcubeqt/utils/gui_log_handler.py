#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
import weakref
import gevent

from mxcubeqt.utils import QtImport

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


GUI_LOG_HANDLER = None
TIMER = None


class LogEvent(QtImport.QEvent):

    def __init__(self, record):

        QtImport.QEvent.__init__(self, QtImport.QEvent.User)
        self.record = record

def process_log_messages():
    i = 0
    while i < 10:
        if len(GUI_LOG_HANDLER.buffer) <= i:
            break

        record = GUI_LOG_HANDLER.buffer[i]

        for viewer in GUI_LOG_HANDLER.registeredViewers:
            QtImport.QApplication.postEvent(viewer, LogEvent(record))

        i += 1

    del GUI_LOG_HANDLER.buffer[0:i]


def do_process_log_messages(sleep_time):
    while True:
        process_log_messages()
        time.sleep(sleep_time)


def GUILogHandler():

    global GUI_LOG_HANDLER
    global TIMER

    if GUI_LOG_HANDLER is None:
        GUI_LOG_HANDLER = __GUILogHandler()

        TIMER = gevent.spawn(do_process_log_messages, 0.2)
        # _timer = QtImport.QtCore.QTimer()
        # QtCore.QObject.connect(_timer, QtCore.SIGNAL("timeout()"), processLogMessages)
        # _timer.start(10)

    return GUI_LOG_HANDLER


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
        return time.strftime("%Y-%m-%d", time.localtime(self.time))

    def getTime(self):
        return time.strftime("%H:%M:%S", time.localtime(self.time))

    def getMessage(self):
        return self.message


class __GUILogHandler(logging.Handler):


    def __init__(self):
        logging.Handler.__init__(self)

        self.buffer = []
        self.registeredViewers = weakref.WeakKeyDictionary()

    def register(self, viewer):
        self.registeredViewers[viewer] = ""
        for rec in self.buffer:
            viewer.append_log_record(rec)

    def emit(self, record):
        self.buffer.append(LogRecord(record))
