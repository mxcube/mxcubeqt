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

from QtImport import *

from BlissFramework.Qt4_BaseComponents import BlissWidget
from widgets.Qt4_log_bar_widget import LogBarWidget
from BlissFramework.Utils import Qt4_GUILogHandler


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.3"
__category__ = "Log"


class Qt4_LogBarBrick(BlissWidget):
    """
    Descript. :
    """
    COLORS = {logging.NOTSET: 'lightgrey',
              logging.DEBUG: 'darkgreen', 
              logging.INFO: 'darkblue',
              logging.WARNING: 'orange', 
              logging.ERROR: 'red',
              logging.CRITICAL: 'black'}

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.max_log_lines = -1

        # Properties ----------------------------------------------------------
        self.addProperty('maxLogLines', 'integer', -1)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self._status_bar_widget = LogBarWidget(self)

        # Layout --------------------------------------------------------------
        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(self._status_bar_widget)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        #self.setSizePolicy(QSizePolicy.MinimumExpanding, 
        #                   QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        Qt4_GUILogHandler.GUILogHandler().register(self)

    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'maxLogLines':
            self.max_log_lines = new_value
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def customEvent(self, event):
        """Event to add a new log record"""
        self.append_log_record(event.record)

    def append_log_record(self, record):
        """Appends a new log line to the text edit
        """
        if self.isRunning() and record.name in ('user_level_log', 'GUI'):
            msg = record.getMessage()#.replace('\n',' ').strip()
            level = record.getLevel()
            color = Qt4_LogBarBrick.COLORS[level]
            date_time = "%s %s" % (record.getDate(), record.getTime())

            self._status_bar_widget.text_edit.\
                append("<font color=%s>[%s]" % (color, date_time) + \
                           " "*5 + "<b>%s</b></font>" % msg)

            if level == logging.WARNING or level == logging.ERROR:
                self._status_bar_widget.toggle_background_color()
            text_document = self._status_bar_widget.text_edit.document()
            if self.max_log_lines > -1 and \
               text_document.blockCount() > self.max_log_lines:
                cursor = QTextCursor(text_document.firstBlock())
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
