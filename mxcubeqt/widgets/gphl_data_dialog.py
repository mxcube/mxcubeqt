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
from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import logging

from mxcubecore import ConvertUtils

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.utils.paramsgui import FieldsWidget

from mxcubecore import HardwareRepository as HWR

__copyright__ = """ Copyright © 2016 - 2019 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


class SelectionTable(qt_import.QTableWidget):
    """Read-only table for data display and selection"""

    def __init__(self, parent=None, name="selection_table", header=None):
        qt_import.QTableWidget.__init__(self, parent)
        if not header:
            raise ValueError("DisplayTable must be initialised with header")

        self.setObjectName(name)
        self.setFrameShape(qt_import.QFrame.StyledPanel)
        self.setFrameShadow(qt_import.QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(len(header))
        self.setSelectionMode(qt_import.QTableWidget.SingleSelection)
        self.setHorizontalHeaderLabels(header)
        self.horizontalHeader().setDefaultAlignment(qt_import.Qt.AlignLeft)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.setFont(qt_import.QFont("Courier"))

        hdr = self.horizontalHeader()
        hdr.setResizeMode(0, qt_import.QHeaderView.Stretch)
        for ii in range(1, len(header)):
            hdr.setResizeMode(ii, qt_import.QHeaderView.ResizeToContents)

    def resizeData(self, ii):
        """Dummy method, recommended by docs when not using std cell widgets"""
        pass

    def populateColumn(self, colNum, values, colours=None):
        """Fill values into column, extending if necessary"""
        if len(values) > self.rowCount():
            self.setRowCount(len(values))
        selectRow = None
        no_colours = not colours or not any(colours)
        colour = None
        for rowNum, text in enumerate(values):
            wdg = qt_import.QLineEdit(self)
            wdg.setFont(qt_import.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(ConvertUtils.text_type(text))
            if colours:
                colour = colours[rowNum]
                if colour:
                    colors.set_widget_color(
                        wdg, getattr(colors, colour), qt_import.QPalette.Base
                    )
            self.setCellWidget(rowNum, colNum, wdg)
            if "*" in text and colour or no_colours:
                selectRow = rowNum
        if selectRow is not None:
            self.setCurrentCell(selectRow, 0)


    def get_value(self):
        """Get value - list of cell contents for selected row"""
        row_id = self.currentRow()
        if not self.cellWidget(row_id, 0):
            logging.getLogger("user_log").warning(
                "Select a row of the table, and then press [Continue]"
            )
        return [self.cellWidget(row_id, ii).text() for ii in range(self.columnCount())]


class GphlDataDialog(qt_import.QDialog):

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

        # Info box
        self.info_gbox = qt_import.QGroupBox("Info", self)
        info_vbox = qt_import.QVBoxLayout()
        self.info_gbox.setLayout(info_vbox)
        main_layout.addWidget(self.info_gbox, stretch=8)
        self.info_text = qt_import.QTextEdit(self.info_gbox)
        self.info_text.setFont(qt_import.QFont("Courier"))
        self.info_text.setReadOnly(True)
        info_vbox.addWidget(self.info_text, stretch=8)

        # Special parameter box
        self.cplx_gbox = qt_import.QGroupBox("Indexing solution", self)
        cplx_vbox = qt_import.QVBoxLayout()
        self.cplx_gbox.setLayout(cplx_vbox)
        main_layout.addWidget(self.cplx_gbox, stretch=8)
        self.cplx_gbox.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.cplx_widget = None

        # Parameter box
        self.parameter_gbox = qt_import.QGroupBox("Parameters", self)
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
        """This should disable having Qt interpret {Return] as [Continue] """
        if ((not event.modifiers() and
             event.key() == qt_import.Qt.Key_Return) or
            (event.modifiers() == qt_import.Qt.KeypadModifier and
             event.key() == qt_import.Qt.Key_Enter)):
            event.accept()
        else:
            super(qt_import.Dialog, self).keyPressEvent(event)

    def continue_button_click(self):
        result = {}
        if self.parameter_gbox.isVisible():
            result.update(self.params_widget.get_parameters_map())
        if self.cplx_gbox.isVisible():
            result["_cplx"] = self.cplx_widget.get_value()
        self.accept()
        self._async_result.set(result)
        self._async_result = None

    def cancel_button_click(self):
        logging.getLogger("HWR").debug("GPhL Data dialog abort pressed.")
        self.reject()
        self._async_result.set(StopIteration)
        self._async_result = None

    def open_dialog(self, field_list, async_result, parameter_update_function):

        msg = "GPhL Workflow waiting for input, verify parameters and press continue."
        logging.getLogger("user_level_log").info(msg)

        self._async_result = async_result

        # get special parameters
        parameters = []
        info = None
        cplx = None
        for dd0 in field_list:
            if info is None and dd0.get("variableName") == "_info":
                # Info text - goes to info_gbox
                info = dd0
            elif cplx is None and dd0.get("variableName") == "_cplx":
                # Complex parameter - goes to cplx_gbox
                cplx = dd0
            else:
                parameters.append(dd0)

        # Info box
        if info is None:
            self.info_text.setText("")
            self.info_gbox.setTitle("Info")
            self.info_gbox.hide()
        else:
            self.info_text.setText(info.get("defaultValue"))
            self.info_gbox.setTitle(info.get("uiLabel"))
            self.info_gbox.show()

        # Complex box
        if self.cplx_widget:
            self.cplx_widget.close()
        if cplx is None:
            self.cplx_gbox.hide()
        else:
            if cplx.get("type") == "selection_table":
                self.cplx_widget = SelectionTable(
                    self.cplx_gbox, "cplx_widget", cplx["header"]
                )
                self.cplx_widget.setSizePolicy(
                    qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
                )
                self.cplx_gbox.layout().addWidget(self.cplx_widget, stretch=8)
                self.cplx_gbox.setTitle(cplx.get("uiLabel"))
                for ii, values in enumerate(cplx["defaultValue"]):
                    self.cplx_widget.populateColumn(
                        ii, values, colours=cplx.get("colours")
                    )
                self.cplx_gbox.show()

            else:
                raise NotImplementedError(
                    "GPhL complex widget type %s not recognised for parameter _cplx"
                    % repr(cplx.get("type"))
                )

        # parameters widget
        if self.params_widget is not None:
            self.params_widget.parametersValidSignal.disconnect(
                self.continue_button.setEnabled
            )
            self.params_widget.close()
            self.params_widget = None
        if parameters:
            params_widget = self.params_widget = FieldsWidget(fields=parameters)
            self.parameter_gbox.layout().addWidget(params_widget, stretch=1)
            if parameter_update_function:
                parameter_update_function(params_widget)
            self.parameter_gbox.show()
            params_widget.parametersValidSignal.connect(self.continue_button.setEnabled)
            self.continue_button.setEnabled(not params_widget.invalid_fields())
        else:
            self.parameter_gbox.hide()

        self.show()
        self.setEnabled(True)
        self.update()
