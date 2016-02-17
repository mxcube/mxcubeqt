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

from PyQt4 import QtGui

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_log_bar_widget import LogBarWidget
from BlissFramework.Utils import Qt4_GUILogHandler


__category__ = 'Qt4_Log'


class Qt4_LogBarBrick(BlissWidget):
    """
    Descript. :
    """
    COLORS = {logging.NOTSET: 'lightgrey', logging.DEBUG: 'darkgreen', 
              logging.INFO: 'darkblue', logging.WARNING: 'orange', 
              logging.ERROR: 'red', logging.CRITICAL: 'black' }

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        self._status_bar_widget = LogBarWidget(self)
        _main_hlayout = QtGui.QHBoxLayout(self)
        _main_hlayout.addWidget(self._status_bar_widget)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_hlayout)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                           QtGui.QSizePolicy.Fixed)

        Qt4_GUILogHandler.GUILogHandler().register(self)

    def customEvent(self, event):
        """
        Descript. :
        """
        if self.isRunning():
            self.append_log_record(event.record)

    def append_log_record(self, record):
        """
        Descript. :
        """
        if record.name == 'user_level_log':
            msg = record.getMessage()#.replace('\n',' ').strip()
            level = record.getLevel()
            color = Qt4_LogBarBrick.COLORS[level]
            date_time = "%s %s" % (record.getDate(), record.getTime())

            self._status_bar_widget.text_edit.\
                append("<font color=%s>[%s]" % (color, date_time) + \
                           " "*5 + "<b>%s</b></font>" % msg)

            if level == logging.WARNING or level == logging.ERROR:
                self._status_bar_widget.toggle_background_color()

    appendLogRecord = append_log_record
