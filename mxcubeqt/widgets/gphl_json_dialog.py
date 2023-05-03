#! /usr/bin/env python
# encoding: utf-8
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

"""GPhL runtime-set parameter input widget. """
import logging

from mxcubecore.utils import conversion

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.utils.jsonparamsgui import create_widgets

__copyright__ = """ Copyright © 2016 - 2022 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


class GphlJsonDialog(qt_import.QDialog):

    continueClickedSignal = qt_import.pyqtSignal()

    def __init__(self, parent=None, name=None, fl=0):
        qt_import.QDialog.__init__(self, parent, qt_import.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)

        # Internal variables --------------------------------------------------
        # AsyncResult to return values
        self._async_result = None

        # Layout
        qt_import.QVBoxLayout(self)
        main_layout = self.layout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(6, 6, 6, 6)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

        self.setWindowTitle("GPhL Workflow parameters")

        # Parameter box
        self.parameter_gbox = qt_import.QGroupBox(self)
        parameter_vbox =  qt_import.QVBoxLayout()
        self.parameter_gbox.setLayout(parameter_vbox)
        main_layout.addWidget(self.parameter_gbox, stretch=1)
        self.parameter_gbox.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.params_widget = None

        # Button bar
        self.button_widget = qt_import.QWidget(self)
        button_layout = qt_import.QHBoxLayout(None)
        self.button_widget.setLayout(button_layout)
        hspacer = qt_import.QSpacerItem(
            1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum
        )
        button_layout.addItem(hspacer)
        self.continue_button = qt_import.QPushButton("Continue", self)
        button_layout.addWidget(self.continue_button)
        self.cancel_button = qt_import.QPushButton("Abort", self)
        button_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.button_widget)

        self.continue_button.clicked.connect(self.continue_button_click)
        self.cancel_button.clicked.connect(self.cancel_button_click)

        self.resize(qt_import.QSize(1200, 578).expandedTo(self.minimumSizeHint()))

    def keyPressEvent(self, event):
        """This should disable having Qt interpret [Return] as [Continue] """
        if ((not event.modifiers() and
             event.key() == qt_import.Qt.Key_Return) or
            (event.modifiers() == qt_import.Qt.KeypadModifier and
             event.key() == qt_import.Qt.Key_Enter)):
            event.accept()
        else:
            super(qt_import.QDialog, self).keyPressEvent(event)

    def continue_button_click(self):
        result = {}
        result.update(self.params_widget.get_values_map())
        self.accept()
        self._async_result.set(result)
        self._async_result = None

    def cancel_button_click(self):
        logging.getLogger("HWR").debug("GPhL Data dialog abort pressed.")
        self.reject()
        self._async_result.set(StopIteration)
        self._async_result = None

    def open_dialog(self, schema, ui_schema, async_result):

        msg = "GPhL Workflow waiting for input, verify parameters and press continue."
        logging.getLogger("user_level_log").info(msg)

        self._async_result = async_result

        # print ('@~@~ open_dialog, schemas')
        # for item in sorted(schema.items()):
        #     print(item)
        # for item in sorted(ui_schema.items()):
        #     print(item)
        # print ('@~@~ end schemas')

        # parameters widget
        if self.params_widget is not None:
            self.params_widget.close()
            self.params_widget = None


        params_widget = self.params_widget = create_widgets(
            schema, ui_schema, parent_widget=self
        )
        self.parameter_gbox.layout().addWidget(params_widget, stretch=8)
        self.parameter_gbox.show()
        self.show()
        self.setEnabled(True)
        self.update()
