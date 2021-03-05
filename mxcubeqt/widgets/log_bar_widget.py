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

import time
import gevent

from mxcubeqt.utils import colors, qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class LogBarWidget(qt_import.QWidget):
    def __init__(self, parent=None, name="log_bar_widget", fl=0):
        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        self.text_edit = qt_import.QTextEdit(self)
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontWeight(qt_import.QFont.Bold)

        _main_hlayout = qt_import.QHBoxLayout(self)
        _main_hlayout.addWidget(self.text_edit)
        _main_hlayout.setSpacing(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

    def toggle_background_color(self):
        gevent.spawn(self._toggle_background_color)

    def _toggle_background_color(self):
        for i in range(0, 3):
            self.set_background_color(colors.LIGHT_RED)
            time.sleep(0.1)
            self.set_background_color(colors.WHITE)
            time.sleep(0.1)

    def set_background_color(self, color):
        palette = self.text_edit.palette()
        palette.setColor(qt_import.QPalette.Base, color)
        self.text_edit.setPalette(palette)

    def set_fixed_height(self, height):
        self.text_edit.setFixedHeight(height)
