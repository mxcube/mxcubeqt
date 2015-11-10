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

from PyQt4 import QtCore
from PyQt4 import QtGui

import sys


class ConfirmDialogWidgetVerticalLayout(QtGui.QWidget):
    """
    Descript. :
    """

    def __init__(self, parent = None, name = None, fl = 0):
        """
        Descript. :
        """
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("ConfirmDialogWidgetVerticalLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.snapshots_list = [0, 1, 2, 4]

        # Graphic elements ----------------------------------------------------
        self.summary_gbox = QtGui.QGroupBox(self)
        self.summary_label = QtGui.QLabel(self.summary_gbox)
        self.file_exists_label = QtGui.QLabel("Existing files that will be overwritten:", self.summary_gbox)
        self.cbx_widget = QtGui.QWidget(self.summary_gbox)
        self.force_dark_cbx = QtGui.QCheckBox(self.cbx_widget)
        self.skip_existing_images_cbx = QtGui.QCheckBox(self.cbx_widget)
        self.take_snapshots_widget = QtGui.QWidget(self.cbx_widget)
        self.take_snapshots_label = QtGui.QLabel(self.take_snapshots_widget)
        self.take_snapshots_cbox = QtGui.QComboBox(self.take_snapshots_widget)
        self.missing_one_cbx = QtGui.QCheckBox(self.cbx_widget)
        self.missing_two_cbx = QtGui.QCheckBox(self.cbx_widget)
        self.interleave_widget = QtGui.QWidget(self.cbx_widget)
        self.interleave_cbx = QtGui.QCheckBox(self.interleave_widget)
        self.interleave_image_num = QtGui.QLineEdit(self.interleave_widget)
        self.interleave_image_num.setFixedWidth(70)

        self.file_tree_widget = QtGui.QTreeWidget(self)
        self.file_tree_widget.setColumnCount(3)
        self.file_tree_widget.setHeaderLabels([self.__tr("Sample"), 
                                               self.__tr("Directory"),
                                               self.__tr("File name")]) 
        #self.file_tree_widget.header().setClickEnabled(0, self.file_list_view.header().count() - 1)
        self.file_tree_widget.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Expanding))

        self.button_widget = QtGui.QWidget(self) 
        self.continue_button = QtGui.QPushButton(self)
        self.continue_button.setText("continue_button")
        self.cancel_button = QtGui.QPushButton(self)
        self.cancel_button.setText("cancel_button")

        # Layout --------------------------------------------------------------
        take_snapshots_layout = QtGui.QHBoxLayout(self.take_snapshots_widget)
        take_snapshots_layout.addWidget(self.take_snapshots_label)
        take_snapshots_layout.addWidget(self.take_snapshots_cbox)
        take_snapshots_layout.addStretch(0)
        take_snapshots_layout.setContentsMargins(0, 0, 0, 0)
        take_snapshots_layout.setSpacing(2)

        _interleave_hlayout = QtGui.QHBoxLayout(self.interleave_widget)
        _interleave_hlayout.addWidget(self.interleave_cbx)
        _interleave_hlayout.addWidget(self.interleave_image_num)
        _interleave_hlayout.addStretch(0)
        _interleave_hlayout.setSpacing(2)
        _interleave_hlayout.setContentsMargins(0, 0, 0, 0)

        cbx_layout = QtGui.QVBoxLayout(self.cbx_widget)
        cbx_layout.addWidget(self.force_dark_cbx)
        cbx_layout.addWidget(self.skip_existing_images_cbx)
        cbx_layout.addWidget(self.interleave_widget)
        cbx_layout.addWidget(self.take_snapshots_widget)
        cbx_layout.addWidget(self.missing_one_cbx)
        cbx_layout.addWidget(self.missing_two_cbx)
        cbx_layout.setContentsMargins(0, 0, 0, 0)
        cbx_layout.setSpacing(2)

        button_layout = QtGui.QHBoxLayout(self.button_widget)
        button_layout.addStretch(0)
        button_layout.addWidget(self.continue_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)

        _summary_gbox_layout = QtGui.QVBoxLayout(self.summary_gbox)
        _summary_gbox_layout.addWidget(self.summary_label)
        _summary_gbox_layout.addWidget(self.file_exists_label)
        _summary_gbox_layout.addWidget(self.file_tree_widget)
        _summary_gbox_layout.addWidget(self.cbx_widget)
        _summary_gbox_layout.addWidget(self.button_widget)
        _summary_gbox_layout.setContentsMargins(0, 4, 4, 0)
        _summary_gbox_layout.setSpacing(6)

        main_layout = QtGui.QVBoxLayout(self) 
        main_layout.addWidget(self.summary_gbox)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)

        self.languageChange()
        self.resize(QtCore.QSize(1018, 472).expandedTo(self.minimumSizeHint()))
        self.setAttribute(QtCore.Qt.WA_WState_Polished)

    def languageChange(self):
        """
        Descript. :
        """
        self.setWindowTitle(self.__tr("Confirm collect"))
        self.summary_gbox.setTitle(self.__tr("Summary"))
        self.summary_label.setText(self.__tr("<summary label>"))
        self.force_dark_cbx.setText(self.__tr("Force dark current"))
        self.skip_existing_images_cbx.setText(self.__tr("Skip already collected images"))
        self.take_snapshots_label.setText(self.__tr("Number of crystal snapshots:"))
        self.interleave_cbx.setText(self.__tr("Interleave"))

        self.take_snapshots_cbox.clear()
        for i in self.snapshots_list: 
            self.take_snapshots_cbox.addItem(self.__tr(str(i)))
		
        self.missing_one_cbx.setText(self.__tr("Missing box one"))
        self.missing_two_cbx.setText(self.__tr("Missing box two"))
        self.file_tree_widget.setHeaderLabels([self.__tr("Sample"), 
                                               self.__tr("Directory"),
                                               self.__tr("File name")]) 
        self.continue_button.setText(self.__tr("Continue"))
        self.cancel_button.setText(self.__tr("Cancel"))

    def __tr(self, s, c = None):
        """
        Descript. :
        """
        return QtGui.QApplication.translate("ConfirmDialogWidgetVerticalLayout", s, c)
