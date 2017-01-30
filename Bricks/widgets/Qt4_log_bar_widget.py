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

import time
import gevent

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors


class LogBarWidget(QWidget):

    def __init__(self, parent=None, name="log_bar_widget", fl=0):
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        self.text_edit = QTextEdit(self)
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setReadOnly(True)

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(self.text_edit)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_hlayout) 

    def toggle_background_color(self):
        gevent.spawn(self._toggle_background_color)

    def _toggle_background_color(self):
        for i in range(0, 3):
            self.set_background_color(Qt4_widget_colors.LIGHT_RED)
            time.sleep(0.1)
            self.set_background_color(Qt4_widget_colors.WHITE)
            time.sleep(0.1)

    def set_background_color(self, qt_color):
        self.text_edit.setTextBackgroundColor(qt_color) 

    def set_fixed_height(self, height):
        self.text_edit.setFixedHeight(height)            
