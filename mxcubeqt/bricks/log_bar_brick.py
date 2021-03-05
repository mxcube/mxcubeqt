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

from mxcubeqt.utils import gui_log_handler, qt_import
from mxcubeqt.widgets.log_bar_widget import LogBarWidget
from mxcubeqt.base_components import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Log"


class LogBarBrick(BaseWidget):
    COLORS = {
        logging.NOTSET: qt_import.Qt.lightGray,
        logging.DEBUG: qt_import.Qt.darkGreen,
        logging.INFO: qt_import.Qt.darkBlue,
        logging.WARNING: qt_import.QColor(255, 185, 56),
        logging.ERROR: qt_import.Qt.red,
        logging.CRITICAL: qt_import.Qt.red,
    }

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.max_log_lines = -1
        self.test_mode = False

        # Properties ----------------------------------------------------------
        self.add_property("maxLogLines", "integer", -1)

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self._status_bar_widget = LogBarWidget(self)

        # Layout --------------------------------------------------------------
        _main_hlayout = qt_import.QHBoxLayout(self)
        _main_hlayout.addWidget(self._status_bar_widget)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        gui_log_handler.GUILogHandler().register(self)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "maxLogLines":
            self.max_log_lines = new_value
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def test(self):
        self.test_mode = True

    def customEvent(self, event):
        """Event to add a new log record"""
        self.append_log_record(event.record)

    def append_log_record(self, record):
        """Appends a new log line to the text edit
        """
        if self.is_running() and record.name in ("user_level_log", "GUI"):
            msg = record.getMessage()
            level = record.getLevel()
            self._status_bar_widget.text_edit.setTextColor(LogBarBrick.COLORS[level])
            self._status_bar_widget.text_edit.append(
                "[%s %s]  %s" % (record.getDate(), record.getTime(), msg)
            )

            # if level == logging.WARNING or level == logging.ERROR:
            #    self._status_bar_widget.toggle_background_color()
            text_document = self._status_bar_widget.text_edit.document()
            if (
                self.max_log_lines > -1
                and text_document.blockCount() > self.max_log_lines
            ):
                cursor = qt_import.QTextCursor(text_document.firstBlock())
                cursor.select(qt_import.QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()

            if level == logging.ERROR:
                self._status_bar_widget.toggle_background_color()
                if self.test_mode:
                    assert False, msg
