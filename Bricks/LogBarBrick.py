import qt
import logging

from BlissFramework import BaseComponents
from widgets.log_bar_widget import LogBarWidget
from BlissFramework.Utils import GUILogHandler

__category__ = 'mxCuBE_v3'

class LogBarBrick(BaseComponents.BlissWidget):
    COLORS = { logging.NOTSET: 'lightgrey', logging.DEBUG: 'darkgreen', 
               logging.INFO: 'darkblue', logging.WARNING: 'orange', 
               logging.ERROR: 'red', logging.CRITICAL: 'black' }

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        # Layout
        self._status_bar_widget = LogBarWidget(self)
        main_layout = qt.QHBoxLayout(self)
        main_layout.addWidget(self._status_bar_widget)

        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, 
                           qt.QSizePolicy.Fixed)

        GUILogHandler.GUILogHandler().register(self)
        logger = logging.getLogger("user_level_log")
        logger.info('Ready')


    def customEvent(self, event):
        if self.isRunning():
            self.append_log_record(event.record)


    def append_log_record(self, record):
        if record.name == 'user_level_log':
            msg = record.getMessage()#.replace('\n',' ').strip()
            level = record.getLevel()
            color = LogBarBrick.COLORS[level]
            date_time = "%s %s" % (record.getDate(), record.getTime())

            self._status_bar_widget.text_edit.\
                append("[<font color=%s>%s]</font>" % (color, date_time) + \
                           " "*5 + "%s" % msg)


    appendLogRecord = append_log_record
