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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from mxcubeqt.utils import qt_import

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CommentsWidget(qt_import.QWidget):

    def __init__(self, parent=None, name=None, fl=0, data_model=None):

        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))
        if name is not None:
            self.setObjectName(name)

        main_gbox = qt_import.QGroupBox("Comments", self)
        self.comment_textbox = qt_import.QTextEdit(main_gbox)

        main_gbox_vbox = qt_import.QVBoxLayout(main_gbox)
        main_gbox_vbox.addWidget(self.comment_textbox)
        main_gbox_vbox.setSpacing(0)
        main_gbox_vbox.setContentsMargins(0, 0, 0, 0)

        self.main_layout = qt_import.QVBoxLayout(self)
        self.main_layout.addWidget(main_gbox)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def get_comment_text(self):
        return str(self.comment_textbox.toPlainText())
