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

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from widgets.Qt4_data_path_widget import DataPathWidget


class ReferenceImageWidget(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("ReferenceImageWidget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QGroupBox("Reference images", self)
        self.tool_box = QToolBox(self.group_box)
        self.page_widget = QWidget(self.tool_box)
        self.path_widget = DataPathWidget(self.page_widget)
        self.acq_widget = AcquisitionWidget(self.page_widget, 'horizontal')
        self.acq_widget.acq_widget_layout.shutterless_cbx.hide()
        #self.acq_widget.acq_widget_layout.setFixedHeight(130)
        self.tool_box.addItem(self.page_widget, "Acquisition parameters")

        # Layout --------------------------------------------------------------
        _page_widget_layout = QVBoxLayout(self.page_widget)
        _page_widget_layout.addWidget(self.path_widget)
        _page_widget_layout.addWidget(self.acq_widget)
        _page_widget_layout.addStretch(0)
        _page_widget_layout.setSpacing(0)
        _page_widget_layout.setContentsMargins(0, 0, 0, 0)  
        
        _group_box_vlayout = QVBoxLayout(self.group_box)
        _group_box_vlayout.addWidget(self.tool_box)
        _group_box_vlayout.setSpacing(0)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
