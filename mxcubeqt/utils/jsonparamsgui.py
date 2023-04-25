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


"""PyQt GUI for runtiem queries - port of paramsgui - rhfogh Jan 2018

Incorporates additions for GPhL workflow code"""
from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import os.path
import logging
import sys

from mxcubecore.utils import conversion, ui_communication

from mxcubecore import HardwareRepository as HWR

from mxcubeqt.utils import qt_import, colors


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class LineEdit(qt_import.QLineEdit):
    """Standard LineEdit widget"""

    def __init__(self, parent, options):
        qt_import.QLineEdit.__init__(self, parent)
        self.is_hidden = options.get("hidden")
        # self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "default" in options:
            self.set_value(options["default"])
        self.setAlignment(qt_import.Qt.AlignRight)
        if self.is_hidden or options.get("readOnly"):
            self.setReadOnly(True)
            self.setEnabled(False)

    def set_value(self, value):
        try:
            print ('@~@~ LineEdit set_value', self.__name, value)
        except:
            pass
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return conversion.text_type(self.text())

    def input_field_changed(self):
        """UI update function triggered by field value changes"""
        # print ('@~@~ input_field_changed')
        # for item in self.parent().gui_root_widget.get_values_map().items():
        #     print (' ---> %s: %s' % item)
        self.parent().validate_fields()
        valid = self.is_valid()
        if valid:
            if self.update_function is not None:
                self.update_function(self.parent().gui_root_widget)
            colors.set_widget_color(
                self, colors.LINE_EDIT_CHANGED, qt_import.QPalette.Base
            )
        self.parent().input_field_changed()

    def color_by_error(self, warning=False):
        if self.is_valid():
            if warning:
                colors.set_widget_color(
                    self, colors.LIGHT_ORANGE, qt_import.QPalette.Base
                )
            else:
                colors.set_widget_color(
                    self, colors.WHITE, qt_import.QPalette.Base
                )
        else:
            colors.set_widget_color(
                self, colors.LINE_EDIT_ERROR, qt_import.QPalette.Base
            )

    def is_valid(self):
        return True

class FloatString(LineEdit):
    """LineEdit widget with validators and formatting for floating point numbers"""

    def __init__(self, parent, options):
        decimals = options.get("decimals")
        # NB We do NOT enforce a maximum number of decimals in edited text,
        # Only in set values.
        if decimals is None:
            self.formatstr = "%s"
        else:
            self.formatstr = "%%.%sf" % decimals
        LineEdit.__init__(self, parent, options)
        self.validator = qt_import.QDoubleValidator(self)
        val = options.get("minimum")
        if val is not None:
            self.validator.setBottom(val)
        val = options.get("maximum")
        if val is not None:
            self.validator.setTop(val)
        fname = options.get("update_function")
        self.update_function = fname and getattr(HWR.beamline.gphl_workflow, fname)
        # extra_validator = options.get("extra_validator")
        # if extra_validator is not None:
        #     self.extra_validator = extra_validator

        self.textEdited.connect(self.input_field_changed)

    def set_value(self, value):
        try:
            print ('@~@~ FLoatString set_value', self.__name, repr(value))
        except:
            pass
        self.setText(self.formatstr % value)

    def get_value(self):
        val = self.text().strip()
        if val:
            return float(val)
        else:
            return None

    def is_valid(self):

        if (
            self.validator.validate(self.text(), 0)[0]
            != qt_import.QValidator.Acceptable
        ):
            return False
        return True

        # if hasattr(self, "extra_validator"):
        #     return self.extra_validator(self)
        # else:
        #     return True


class TextEdit(qt_import.QTextEdit):
    """Standard text edit widget (multiline text)"""

    def __init__(self, parent, options):
        qt_import.QTextEdit.__init__(self, parent)
        self.is_hidden = options.get("hidden")
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.setFont(qt_import.QFont("Courier"))
        self.__name = options["variable_name"]
        if "default" in options:
            self.set_value(options["default"])
        # self.setAlignment(qt_import.Qt.AlignRight)
        if self.is_hidden or options.get("readOnly"):
            self.setReadOnly(True)
            # self.setEnabled(False)
        # self.setSizePolicy(
        #     qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        # )

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return conversion.text_type(self.toPlainText())


class Combo(qt_import.QComboBox):
    """Standard ComboBox (pulldown) widget"""

    def __init__(self, parent, options):
        qt_import.QComboBox.__init__(self, parent)
        self.__name = options["variable_name"]
        self.is_hidden = options.get("hidden")
        self.value_dict = options["value_dict"]
        for val in self.value_dict:
            self.addItem(str(val))
        if "default" in options:
            self.set_value(options["default"])
        fname = options.get("update_function")
        self.update_function = fname and getattr(HWR.beamline.gphl_workflow, fname)
        self.currentIndexChanged.connect(self.input_field_changed)

    def input_field_changed(self, input_field_text):
        """UI update function triggered by field value changes"""
        print ('@~@~ Combo input_field_changed', input_field_text, self.update_function)
        if self.update_function is not None:
            self.update_function(self.parent().gui_root_widget)
        self.parent().input_field_changed()
        print ('@~@~ currentINdex, Text ', self.currentIndex(), self.currentText())

    def set_value(self, value):
        try:
            print ('@~@~ combo set_value', self.__name, repr(value))
        except:
            pass
        self.setCurrentIndex(self.findText(value))

    def get_value(self):
        return self.value_dict.get(conversion.text_type(self.currentText()))

    def get_name(self):
        return self.__name


class File(qt_import.QWidget):
    """Standard file selection widget"""

    def __init__(self, parent, options):
        qt_import.QWidget.__init__(self, parent)

        # do not allow qt to stretch us vertically
        policy = self.sizePolicy()
        policy.setVerticalPolicy(qt_import.QSizePolicy.Fixed)
        self.setSizePolicy(policy)

        qt_import.QHBoxLayout(self)
        self.__name = options["variable_name"]
        self.filepath = qt_import.QLineEdit(self)
        self.filepath.setAlignment(qt_import.Qt.AlignLeft)
        if "default" in options:
            self.filepath.setText(options["default"])
        self.open_dialog_btn = qt_import.QPushButton("...", self)
        self.open_dialog_btn.clicked.connect(self.open_file_dialog)

        self.layout().addWidget(self.filepath)
        self.layout().addWidget(self.open_dialog_btn)

    def set_value(self, value):
        self.filepath.setText(value)

    def get_value(self):
        return conversion.text_type(self.filepath.text())

    def get_name(self):
        return self.__name

    def open_file_dialog(self):
        start_path = os.path.dirname(conversion.text_type(self.filepath.text()))
        if not os.path.exists(start_path):
            start_path = ""
        path = qt_import.QFileDialog(self).getOpenFileName(directory=start_path)
        if not path.isNull():
            self.filepath.setText(path)


class IntSpinBox(qt_import.QSpinBox):
    """Standard integer (spinbox) widget"""

    CHANGED_COLOR = qt_import.QColor(255, 165, 0)

    def __init__(self, parent, options):
        qt_import.QSpinBox.__init__(self, parent)
        self.lineEdit().setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "default" in options:
            val = int(options["default"])
            self.setValue(val)
        if "maximum" in options:
            self.setMaximum(int(options["maximum"]))
        if "minimum" in options:
            self.setMinimum(int(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])
        self.is_hidden = options.get("hidden")

    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        val = self.value()
        if val:
            return int(val)
        else:
            return None

    def get_name(self):
        return self.__name

class DoubleSpinBox(qt_import.QDoubleSpinBox):
    """Standard float (spinbox) widget"""

    CHANGED_COLOR = qt_import.QColor(255, 165, 0)

    def __init__(self, parent, options):
        qt_import.QDoubleSpinBox.__init__(self, parent)
        self.lineEdit().setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "default" in options:
            val = float(options["default"])
            self.setValue(val)
        if "maximum" in options:
            self.setMaximum(float(options["maximum"]))
        if "minimum" in options:
            self.setMinimum(float(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])
        self.is_hidden = options.get("hidden")

    def set_value(self, value):
        self.setValue(float(value))

    def get_value(self):
        val = self.value()
        if val:
            return float(val)
        else:
            return None

    def get_name(self):
        return self.__name

class CheckBox(qt_import.QCheckBox):
    """Standard Boolean (CheckBox) widget"""

    def __init__(self, parent, options):
        qt_import.QCheckBox.__init__(self, options.get("uiLabel"), parent)
        # self.setAlignment(qt_import.Qt.AlignLeft)
        self.is_hidden = options.get("hidden")
        self.__name = options["variable_name"]
        state = (
            qt_import.Qt.Checked
            if options.get("default")
            else qt_import.Qt.Unchecked
        )
        self.setCheckState(state)
        # self.setAlignment(qt_import.Qt.AlignRight)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

    def set_value(self, value):
        self.setChecked(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.isChecked()

class UIContainer:

    @property
    def gui_root_widget(self):
        root = self
        while isinstance(root, UIContainer):
            root = root.parent()
        return root

    def input_field_changed(self):
        self.parent().input_field_changed()

    def validate_fields(self):
        self.parent().validate_fields()

class LocalQGroupbox(qt_import.QGroupBox, UIContainer):
    is_hidden = False

    pass

# def make_widget(parent, options):
#     return WIDGET_CLASSES[options["type"]](parent, options)

def create_widgets(
    schema, ui_schema, field_name=None, parent_widget=None, gui_root_widget=None
):
    """Recursive widget creation function

    Args:
        schema (dict):  jsonschema
        ui_schema (dict): ui:schema dictionary for widget being created
        field_name (str): Unique name of field (or container) being created.
                          Equal to tag in ui_schema, and used as variable)_name
        parent_widget(qt_import.QWidget): parent widget
        gui_root_widget (dict): root (layoutWidget) widget

    Returns (qt_import.QWidget):

    NB the input data structures differ from standard ui:schema usage
    fields and layout are taken from the ui:schema, so the schema order is mandatory
    there are grouping constructs corresponding to columns and boxes in the ui:schema
    that do not match any object in the jsonschema.
    """

    is_top_object = (gui_root_widget is None)

    default_container_name = "vertical_box"

    fields = schema["properties"]
    # definitions = schema["definitions"]

    field_data = fields.get(field_name)
    if field_data:
        # This is an actual data field
        widget_name = ui_schema.get("ui:widget")
        if not widget_name:
            widget_name = field_data.get("type")
        options = field_data.copy()
        options["variable_name"] = field_name

        pathstr = field_data.get("$ref")
        if pathstr:
            if not ui_schema.get("ui:widget"):
                widget_name = "select"
            tags = pathstr.split("/")[1:]
            dd0 = schema
            for tag in tags:
                dd0 = dd0[tag]
            enums = dd0
            options["value_dict"] = dict(
                (dd1["title"], dd1["enum"][0]) for dd1 in enums
            )

        options.update(ui_schema.get("ui:options", {}))
        if ui_schema.get("ui:readonly"):
            options["readOnly"] = True
        widget = WIDGET_CLASSES[widget_name](parent_widget, options)
        widget.widget_name = widget_name  # @~@~
        if widget.is_hidden:
            widget.setReadOnly(True)
            widget.setEnabled(False)
            widget.hide()
        gui_root_widget.parameter_widgets[field_name] = widget
    else:
        # This is a container field
        title = ui_schema.get("ui:title")
        widget_name = ui_schema.get("ui:widget") or default_container_name
        if is_top_object:
            # Top of schema
            widget = gui_root_widget = LayoutWidget()
        elif title:
            widget = LocalQGroupbox(title, parent=parent_widget)
        else:
            widget = LocalQGroupbox(parent=parent_widget)
        layout_class = WIDGET_CLASSES[widget_name]
        layout = layout_class(widget)
        layout.setSpacing(6)
        widget.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        layout.populate_widget(
            schema, ui_schema, field_name, gui_root_widget
        )
    if is_top_object:
        # This is the root widget
        # Now everything is populated, put the hidden widgets in as data holders
        for field_name, field in fields.items():
            if field_name not in gui_root_widget.parameter_widgets:
                if field.get("hidden"):
                    create_widgets(
                        schema,
                        field,
                        field_name,
                        parent_widget=gui_root_widget,
                        gui_root_widget=gui_root_widget
                    )
                else:
                    raise RuntimeError(
                        "Coding error: UI fields %s is neither hidden nor displayed"
                        % field_name
                    )

    #
    return widget

class ColumnGridWidget (qt_import.QGridLayout):
    """Gridded layout, content specified by column"""

    col_spacing = " " * 7

    def __init__(self, parent):
        """
        Args:
            parent (qtimport.QtWidget:
        """
        super().__init__(parent)
        self.is_hidden = False

    def populate_widget(
        self, schema, ui_schema, field_name, gui_root_widget
    ):
        print ('@~@~ populate grid widget', field_name, ui_schema["ui:order"])
        fields = schema["properties"]
        maxrownum = 0
        for colnum, colname in enumerate(
            (ui_schema["ui:order"])
            or list(x for x in ui_schema if not x.startswith("ui:"))
        ):
            column = ui_schema[colname]
            print ('@~@~ column', column["ui:order"])
            col1 = 2 * colnum
            col2 = col1 + 1
            for rownum, rowname in  enumerate(
                (column["ui:order"])
                or list(x for x in column if not x.startswith("ui:"))
            ):
                field = fields.get(rowname)
                ui_field = column.get(rowname) or field
                new_widget = create_widgets(
                    schema,
                    ui_field,
                    rowname,
                    self.parent(),
                    gui_root_widget,
                )
                if field:
                    widget_type = ui_field.get("ui:widget") or field.get(type, "string")
                    title = field.get("title") or ui_field.get("ui:title")
                    if title:
                        if widget_type in ("textarea", "selection_table"):
                            new_widget.setSizePolicy(
                                qt_import.QSizePolicy.MinimumExpanding,
                                qt_import.QSizePolicy.Minimum,
                            )
                            # Special case - title goes above
                            outer_box = qt_import.QGroupBox(title, parent=self.parent())
                            self.addWidget(
                                outer_box,
                                rownum,
                                col1,
                                1,
                                2,
                                # qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop,
                            )
                            outer_layout = qt_import.QVBoxLayout()
                            outer_box.setLayout(outer_layout)
                            outer_layout.addWidget(new_widget)
                            # outer_layout.setStretch(0, 8)
                        elif not new_widget.is_hidden:
                            new_widget.setSizePolicy(
                                qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed
                            )
                            if col1:
                                # Add spacing to columns after the first
                                title = self.col_spacing + title
                            label =  qt_import.QLabel(title, self.parent())
                            self.addWidget(
                                label,
                                rownum,
                                col1,
                                qt_import.Qt.AlignRight | qt_import.Qt.AlignTop
                            )
                            self.addWidget(
                                new_widget,
                                rownum,
                                col2,
                                qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                            )
                    else:
                        self.addWidget(
                            new_widget,
                            rownum,
                            col1,
                            1,
                            2,
                            # qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )
                    # if widget_type == "text_area":
                    #     self.setRowStretch(rownum, 8)
                    #     self.setColumnStretch(col2, 8)
                else:
                    title = ui_schema.get("ui:title")
                    if title:
                        outer_box = qt_import.QGroupBox(title, parent=self.parent())
                        self.addWidget(
                            outer_box,
                            rownum,
                            col1,
                            1,
                            2,
                            # qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop,
                            )
                        outer_layout = qt_import.QVBoxLayout()
                        outer_box.setLayout(outer_layout)
                        outer_layout.addWidget(
                            new_widget,
                            0,
                            # qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )
                        # outer_layout.setStretch(0, 8)
                    else:
                        self.addWidget(
                            new_widget,
                            rownum,
                            col1,
                            1,
                            2,
                            # qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )
                    # self.setRowStretch(rownum, 8)
                    # self.setColumnStretch(col2, 8)
            else:
                maxrownum = max(maxrownum, rownum)
        # Add spacer to compress layout
        spacerItem = qt_import.QSpacerItem(
            6,
            6,
            qt_import.QSizePolicy.Expanding,
            qt_import.QSizePolicy.Expanding,
        )
        self.addItem(
            spacerItem,
            maxrownum + 1,
            col2 + 1
        )

class VerticalBox(ColumnGridWidget):
    """Treated as a single column gridded box, with input not grouped in columns"""

    def populate_widget(
        self, schema, ui_schema, field_name, gui_root_widget
    ):
        print ('@~@~ populate vbox widget', field_name)
        wrap_schema = {
        }
        col_schema = wrap_schema["column"] = {}
        self.is_hidden = False
        for tag, val in ui_schema.items():
            if tag.startswith("ui:"):
                wrap_schema[tag] = val
            else:
                col_schema[tag] = val
        col_schema["ui:order"] = wrap_schema["ui:order"]
        wrap_schema["ui:order"] = ("column",)
        #
        super().populate_widget(schema, wrap_schema, field_name, gui_root_widget)

class HorizontalBox(qt_import.QHBoxLayout):
    def __init__(self):
        self.is_hidden = False
        raise NotImplementedError()

class LayoutWidget(qt_import.QWidget, ui_communication.AbstractValuesMap):
    """Collection-of-widgets widget for parameter query"""
    parametersValidSignal = qt_import.pyqtSignal(bool)

    def __init__(self):

        self.parameter_widgets = {}
        qt_import.QWidget.__init__(self)

        # current_row = 0
        # col_incr = 0
        # # pad1: width of empty separating columns
        # pad1 = " " * 4
        # # Extra padding in front of columns 2, 3, ...
        # # to offset space for boolean widgets
        # pad2 = ""
        # for field in fields:
        #     # should not happen but lets just skip them
        #     if (
        #         field["type"] != "message"
        #         and "uiLabel" not in field
        #         and not field["type"].startswith("dbl")
        #     ):
        #         continue
        #
        #     # hack until the 'real' xml gets implemented server side
        #     # and this mess gets rewritten
        #     if field["type"] == "message":
        #         logging.debug("creating widget with options: %s", field)
        #         widget = make_widget(self, field)
        #         # message will be alone in the layout
        #         # so that will not fsck up the layout
        #         self.layout().addWidget(widget, current_row, current_row, 0, 1)
        #     else:
        #         logging.debug("creating widget with options: %s", field)
        #         widget = make_widget(self, field)
        #         # Temporary (like this brick ...) hack to get a nicer UI
        #         if isinstance(widget, TextEdit):
        #             widget.setSizePolicy(
        #                 qt_import.QSizePolicy.MinimumExpanding,
        #                 qt_import.QSizePolicy.Minimum,
        #             )
        #         else:
        #             widget.setSizePolicy(
        #                 qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed
        #             )
        #         self.field_widgets.append(widget)
        #         col = col_incr
        #         if field["type"] == "boolean":
        #             self.layout().addWidget(
        #                 widget, current_row, col, 1, 2, qt_import.Qt.AlignLeft
        #             )
        #         elif field["type"].startswith("dbl"):
        #             # Double width widget, no label
        #             self.layout().addWidget(
        #                 widget, current_row, col, 1, 2, qt_import.Qt.AlignLeft
        #             )
        #         else:
        #             pad = pad2 if col_incr else ""
        #             label = qt_import.QLabel(pad + field["uiLabel"], self)
        #             self.layout().addWidget(
        #                 label, current_row, col, qt_import.Qt.AlignLeft
        #             )
        #             self.layout().addWidget(
        #                 widget, current_row, 1 + col, qt_import.Qt.AlignLeft
        #             )
        #             # Add empty column, for separation purposes
        #
        #             hspacer = qt_import.QSpacerItem(
        #                 10,
        #                 20,
        #                 qt_import.QSizePolicy.MinimumExpanding,
        #                 qt_import.QSizePolicy.Minimum
        #             )
        #             # empty = qt_import.QLabel(pad1, self)
        #             self.layout().addItem(
        #                 hspacer, current_row, col + 2, qt_import.Qt.AlignLeft
        #             )
        #
        #     current_row += 1
        #     if field.pop("NEW_COLUMN", False):
        #         current_row = 0
        #         # Increment column
        #         col_incr += 3

    def set_values(self, **values):
        """Set values for all fields from values dictionary"""
        for tag, val in values.items():
            print ('@~@~ setting', tag, val)
            self.parameter_widgets[tag].set_value(val)

    def input_field_changed(self):
        """Placeholder function, can be overridden in individual instances

        Executed at the end of all input_field_changed functions """
        self.get_values_map()

    def get_values_map(self):
        """Get parameter values dictionary for all fields"""
        for tag, value in self.parameter_widgets.items():
            print (' ----> %s: %s' % (tag, value.get_value()))
        return dict(
            (tag, val.get_value()) for tag, val in self.parameter_widgets.items()
        )

    def validate_fields(self):
        all_valid = True
        for field_name, widget in self.parameter_widgets.items():
            # The two functions should go in parallel, but for precision, ...
            if hasattr(widget, "color_by_error"):
                widget.color_by_error()
            if hasattr(widget, "is_valid"):
                if not widget.is_valid():
                    all_valid = False
                    print (
                        "WARNING, invalid value %s for %s"
                        % (widget.get_value(),field_name)
                    )
        self.parametersValidSignal.emit(all_valid)


class SelectionTable(qt_import.QTableWidget):
    """Read-only table for data display and selection"""

    def __init__(self, parent, options):
        qt_import.QTableWidget.__init__(self, parent)
        header = options["header"]

        self.is_hidden = options.get("hidden")

        # self.setObjectName(name)
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

        colouring = options.get("colouring")
        for ii, data in enumerate(options["content"]):
            self.populateColumn(ii, data, colouring)

    def resizeData(self, ii):
        """Dummy method, recommended by docs when not using std cell widgets"""
        pass

    def populateColumn(self, colNum, values, colouring=None):
        """Fill values into column, extending if necessary"""
        if len(values) > self.rowCount():
            self.setRowCount(len(values))
        selectRow = None
        if colouring and any(colouring):
            colour = getattr(colors,"LIGHT_GREEN")
        else:
            colour = None
        for rowNum, text in enumerate(values):
            wdg = qt_import.QLineEdit(self)
            wdg.setFont(qt_import.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(conversion.text_type(text))
            if colour and colouring[rowNum]:
                colors.set_widget_color(wdg, colour, qt_import.QPalette.Base)
            self.setCellWidget(rowNum, colNum, wdg)
            if "*" in text and (colouring[rowNum] or not colour):
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



# Class is selected from ui:widget or, failing that, from type
WIDGET_CLASSES = {
    "number": FloatString,
    "string": LineEdit,
    "boolean": CheckBox,
    "integer": FloatString,
    "textarea": TextEdit,
    "spinbox": IntSpinBox,
    "float": DoubleSpinBox,
    "select": Combo,
    "column_grid": ColumnGridWidget,
    "horizontal_box": HorizontalBox,
    "vertical_box": VerticalBox,
    "selection_table": SelectionTable,
}
