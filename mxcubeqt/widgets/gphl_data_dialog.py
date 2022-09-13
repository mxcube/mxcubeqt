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

from mxcubecore.utils import conversion

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
        for rowNum, text in enumerate(values):
            wdg = qt_import.QLineEdit(self)
            wdg.setFont(qt_import.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(conversion.text_type(text))
            if colours:
                colour = colours[rowNum]
                if colour:
                    colors.set_widget_color(
                        wdg, getattr(colors, colour), qt_import.QPalette.Base
                    )
                    # wdg.setBackground(getattr(qt_import.QColor, colour))
            self.setCellWidget(rowNum, colNum, wdg)

    def get_value(self):
        """Get value - list of cell contents for selected row"""
        row_id = self.currentRow()
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
        main_layout.setMargin(6)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

        self.setWindowTitle("GPhL Workflow parameters")

        # Info box
        self.info_gbox = qt_import.QGroupBox("Info", self)
        qt_import.QVBoxLayout(self.info_gbox)
        main_layout.addWidget(self.info_gbox)
        self.info_text = qt_import.QTextEdit(self.info_gbox)
        self.info_text.setFont(qt_import.QFont("Courier"))
        self.info_text.setReadOnly(True)
        self.info_gbox.layout().addWidget(self.info_text)

        # Special parameter box
        self.cplx_gbox = qt_import.QGroupBox("Indexing solution", self)
        qt_import.QVBoxLayout(self.cplx_gbox)
        main_layout.addWidget(self.cplx_gbox)
        self.cplx_gbox.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.cplx_widget = None

        # Parameter box
        self.parameter_gbox = qt_import.QGroupBox("Parameters", self)
        main_layout.addWidget(self.parameter_gbox)
        self.parameter_gbox.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.params_widget = None

        # Button bar
        button_layout = qt_import.QHBoxLayout(None)
        hspacer = qt_import.QSpacerItem(
            1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum
        )
        button_layout.addItem(hspacer)
        self.continue_button = qt_import.QPushButton("Continue", self)
        button_layout.addWidget(self.continue_button)
        self.cancel_button = qt_import.QPushButton("Abort", self)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.continue_button.clicked.connect(self.continue_button_click)
        self.cancel_button.clicked.connect(self.cancel_button_click)

        self.resize(qt_import.QSize(1018, 472).expandedTo(self.minimumSizeHint()))
        # self.clearWState(qt_import.WState_Polished)

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
        self.reject()
        HWR.beamline.gphl_workflow.abort("Manual abort")

    def open_dialog(self, field_list, async_result):

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
                self.cplx_gbox.layout().addWidget(self.cplx_widget)
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
            self.params_widget.close()
            self.params_widget = None
        if parameters:
            self.params_widget = FieldsWidget(
                fields=parameters, parent=self.parameter_gbox
            )

            values = {}
            for dd0 in field_list:
                name = dd0["variableName"]
                value = dd0.get("defaultValue")
                if value is not None:
                    dd0[name] = value
            self.params_widget.set_values(values)
            self.parameter_gbox.show()
        else:
            self.parameter_gbox.hide()

        self.show()
        self.setEnabled(True)
