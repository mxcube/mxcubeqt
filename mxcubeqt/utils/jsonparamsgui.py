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

from mxcubecore.utils import conversion

from mxcubeqt.utils import qt_import, colors


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class LineEdit(qt_import.QLineEdit):
    """Standard LineEdit widget"""

    def __init__(self, parent, options):
        qt_import.QLineEdit.__init__(self, parent)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "default" in options:
            self.set_value(options["default"])
        self.setAlignment(qt_import.Qt.AlignRight)
        if options.get("readonly"):
            self.setReadOnly(True)
            self.setEnabled(False)

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return conversion.text_type(self.text())

    def input_field_changed(self):
        """UI update function triggered by field value changes"""
        self.parent().validate_fields()
        valid = self.is_valid()
        if valid:
            if self.update_function is not None:
                self.update_function(self.parent())
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

class HiddenWidget(LineEdit):
    """Widget for hidden, non-editable attribtues,used for storing values only.
    Treated as string value

    This is a bit of a kludge, but it is simpler to treat all widgets the same"""

    def __init__(self, parent, options):
        qt_import.QLineEdit.__init__(self, parent)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "default" in options:
            self.setText(str(options["default"]))
        self.setAlignment(qt_import.Qt.AlignRight)
        self.setReadOnly(True)
        self.setEnabled(False)
        self.hide()

    def set_value(self, value):
        raise TypeError("Cannot set valule for a hidden attribute")

    def get_name(self):
        return self.__name

    def get_value(self):
        return conversion.text_type(self.text())

    def input_field_changed(self):
        """UI update function triggered by field value changes"""
        pass

    def color_by_error(self, warning=False):
        pass

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
        self.update_function = options.get("update_function")
        extra_validator = options.get("extra_validator")
        if extra_validator is not None:
            self.extra_validator = extra_validator

        self.textEdited.connect(self.input_field_changed)

    def set_value(self, value):
        self.setText(self.formatstr % value)

    def is_valid(self):

        if (
            self.validator.validate(self.text(), 0)[0]
            != qt_import.QValidator.Acceptable
        ):
            return False

        if hasattr(self, "extra_validator"):
            return self.extra_validator(self)
        else:
            return True


class TextEdit(qt_import.QTextEdit):
    """Standard text edit widget (multiline text)"""

    def __init__(self, parent, options):
        qt_import.QTextEdit.__init__(self, parent)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variable_name"]
        if "default" in options:
            self.set_value(options["default"])
        self.setAlignment(qt_import.Qt.AlignRight)
        if options.get("readonly"):
            self.setReadOnly(True)
            self.setEnabled(False)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return conversion.text_type(self.text())


class Combo(qt_import.QComboBox):
    """Standard ComboBox (pulldown) widget"""

    def __init__(self, parent, options):
        qt_import.QComboBox.__init__(self, parent)
        self.__name = options["variable_name"]
        self.value_dict = options["value_dict"]
        for val in self.value_dict:
            self.addItem(str(val))
        if "default" in options:
            self.set_value(options["default"])

        self.update_function = options.get("update_function")
        self.currentIndexChanged.connect(self.input_field_changed)

    def input_field_changed(self, input_field_text):
        """UI update function triggered by field value changes"""
        if self.update_function is not None:
            self.update_function(self.parent())
        self.parent().input_field_changed()

    def set_value(self, value):
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
        else:
            self.setMaximum(sys.maxsize)
        if "minimum" in options:
            self.setMinimum(int(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])

    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        val = int(self.value())
        return conversion.text_type(val)

    def get_name(self):
        return self.__name


class DoubleSpinBox(qt_import.QDoubleSpinBox):
    """Standard float/double (spinbox) widget"""

    CHANGED_COLOR = colors.LINE_EDIT_CHANGED

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
        else:
            self.setMaximum(sys.maxsize)
        if "minimum" in options:
            self.setMinimum(float(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])

    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        val = int(self.value())
        return conversion.text_type(val)

    def get_name(self):
        return self.__name


class Message(qt_import.QWidget):
    """Message display widget"""

    def __init__(self, parent, options):
        qt_import.QWidget.__init__(self, parent)
        logging.debug("making message with options %r", options)
        qt_import.QHBoxLayout(self)
        icon = qt_import.QLabel(self)
        icon.setSizePolicy(qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed)

        # all the following stuff is there to get the standard icon
        # for our level directly from qt
        mapping = {
            "warning": qt_import.QMessageBox.Warning,
            "info": qt_import.QMessageBox.Information,
            "error": qt_import.QMessageBox.Critical,
        }
        level = mapping.get(options["level"])
        if level is not None:
            icon.setPixmap(qt_import.QMessageBox.standardIcon(level))

        text = qt_import.QLabel(options["text"], self)

        self.layout().addWidget(icon)
        self.layout().addWidget(text)

    # make the current code happy, temp hack

    def get_value(self):
        return "no value"

    def get_name(self):
        return "a message"

    def set_value(self, value):
        pass


class CheckBox(qt_import.QCheckBox):
    """Standard Boolean (CheckBox) widget"""

    def __init__(self, parent, options):
        qt_import.QCheckBox.__init__(self, options.get("uiLabel"), parent)
        # self.setAlignment(qt_import.Qt.AlignLeft)
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


def make_widget(parent, options):
    return WIDGET_CLASSES[options["type"]](parent, options)

def create_widgets(
    schema, ui_schema, field_name=None, parent_widget=None, parameter_widgets=None
):
    """Recursive widget creation function

    Args:
        schema (dict):  jsonschema
        ui_schema (dict): ui:schema dictionary for widget being created
        field_name (str): Unique name of field (or container) being created.
                          Equal to tag in ui_schema, and used as variable)_name
        parent_widget(qt_import.QWidget): parent widget
        parameter_widgets (dict): variable_name:widget dictionary

    Returns (qt_import.QWidget):

    NB the input data structures differ from standard ui:schema usage
    fields and layout are taken from the ui:schema, so the schema order is mandatory
    there are grouping constructs correspondign to columns and boxes in the ui:schema
    that do not match any object in the jsonschema.
    """
    default_container_name = "vertical_box"

    fields = schema["properties"]
    definitions = schema["definitions"]

    field_data = fields.get(field_name)
    if field_data:
        # This is an actual data field
        widget_name = ui_schema.get("ui:widget") or field_data.get("type")
        options = field_data.copy()
        options["variable_name"] = field_name

        pathstr = field_data.get("$ref")
        if pathstr:
            if not widget_name:
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
        widget = WIDGET_CLASSES[widget_name](parent_widget, options)
        parameter_widgets[widget_name] = widget
    else:
        # This is a container field
        title = ui_schema.get("ui:title")
        widget_name = ui_schema.get("ui:widget") or default_container_name
        if parent_widget is None:
            # Top of schema
            widget = LayoutWidget(parameter_widgets=parameter_widgets)
        elif title:
            widget = qt_import.QGroupBox(title, parent=parent_widget)
        else:
            widget = qt_import.QWidget(parent=parent_widget)
        layout_class = WIDGET_CLASSES[widget_name]
        layout = layout_class(widget)
        layout.setSpacing(6)
        widget.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        layout.populate_widget(
            schema, ui_schema, field_name, parameter_widgets
        )

        # if widget_name == "column_grid":
        #     for colnum, colname in enumerate(
        #         (ui_schema["ui:order"])
        #         or list(x for x in ui_schema if not x.startswith("ui:"))
        #     ):
        #         column = ui_schema[colname]
        #         for rownum, rowname in  enumerate(
        #             (column["ui:order"])
        #             or list(x for x in column if not x.startswith("ui:"))
        #         ):
        #             new_widget = create_widgets(
        #                 fields, column[rowname], rowname, widget, parameter_widgets
        #             )
        #             layout.addWidget(
        #                 new_widget, rowname, column[rowname], colnum, rownum
        #             )
        # else:
        #
        #     for field_name in order:
        #         use_ui_schema = ui_schema.get(field_name, {})
        #         new_widget = create_widgets(
        #             fields, use_ui_schema, field_name, widget, parameter_widgets
        #         )
        #         layout.addWidget(new_widget, fields.get(field_name), use_ui_schema)
    #
    return widget

class ColumnGridWidget (qt_import.QGridLayout):
    """Gridded layout, content specified by column"""

    col_spacing = " " * 4

    def __init__(self, parent):
        """
        Args:
            parent (qtimport.QtWidget:
        """
        super().__init__(parent)

    def populate_widget(
        self, schema, ui_schema, field_name, parameter_widgets
    ):
        fields = schema["properties"]
        for colnum, colname in enumerate(
            (ui_schema["ui:order"])
            or list(x for x in ui_schema if not x.startswith("ui:"))
        ):
            column = ui_schema[colname]
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
                    rowname, self.parent(),
                    parameter_widgets
                )
                if field:
                    widget_type = ui_field.get("ui:widget") or field.get(type, "string")
                    title = field.get("title") or ui_schema.get("ui:title")
                    if title:
                        if widget_type == "textarea":
                            # Special case - title goes above
                            outer_box = qt_import.QGroupBox(title, parent=self.parent())
                            self.addWidget(
                                outer_box,
                                rownum,
                                col2,
                                1,
                                2,
                                qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop,
                            )
                            outer_layout = qt_import.QVBoxLayout()
                            outer_box.setLayout(outer_layout)
                            outer_layout.addWidget(new_widget)
                        elif widget_type != "hidden":
                            if col1:
                                # Add spacing to columns after the first
                                title = self.col_spacing + title
                            label =  qt_import.QLabel(title, self.parent())
                            self.addWidget(
                                label,
                                rownum,
                                col1,
                                qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
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
                            col2,
                            1,
                            2,
                            qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )
                else:
                    title = ui_schema.get("ui:title")
                    if title:
                        outer_box = qt_import.QGroupBox(title, parent=self.parent())
                        self.addWidget(
                            outer_box,
                            rownum,
                            col2,
                            1,
                            2,
                            qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop,
                            )
                        outer_layout = qt_import.QVBoxLayout()
                        outer_box.setLayout(outer_layout)
                        outer_layout.addWidget(
                            new_widget,
                            0,
                            qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )
                    else:
                        self.addWidget(
                            new_widget,
                            rownum,
                            col2,
                            1,
                            2,
                            qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop
                        )

class VerticalBox(ColumnGridWidget):
    """Treated as a single column gridded box, with input not grouped in columns"""

    def populate_widget(
        self, schema, ui_schema, field_name, parameter_widgets
    ):
        fields = schema["properties"]
        wrap_schema = {
        }
        col_schema = wrap_schema["column"] = {}
        for tag, val in ui_schema.items():
            if tag.startswith("ui:"):
                wrap_schema[tag] = val
            else:
                col_schema[tag] = val
        col_schema["ui:order"] = wrap_schema["ui:order"]
        wrap_schema["ui:order"] = ("column",)
        #
        super().populate_widget(schema, wrap_schema, field_name, parameter_widgets)

class HorizontalBox(qt_import.QHBoxLayout):
    def __init__(self):
        raise NotImplementedError()

class LayoutWidget(qt_import.QWidget):
    """Collection-of-widgets widget for parameter query"""
    parametersValidSignal = qt_import.pyqtSignal(bool)

    def __init__(self, parameter_widgets):

        self.parameter_widgets = parameter_widgets
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
        for field in self.field_widgets:
            if field.get_name() in values:
                field.set_value(values[field.get_name()])
        for tag, val in values.items():
            self.parameter_widgets[tag].set_value(val)

    def input_field_changed(self):
        """Placeholder function, can be overridden in individual instances

        Executed at the end of all input_field_changed functions """
        pass

    def get_parameters_map(self):
        """Get parameter values dictionary for all fields"""
        return dict(self.parameter_widgets)

    def validate_fields(self):
        all_valid = True
        for widget in self.parameter_widgets.values():
            # The two functions should go in parallel, but for precision, ...
            if hasattr(widget, "color_by_error"):
                widget.color_by_error()
            if hasattr(widget, "is_valid"):
                if not widget.is_valid():
                    all_valid = False
                    print (
                        "WARNING, invalid value %s for %s"
                        % (widget.get_value(), widget.get_name())
                    )
        self.parametersValidSignal.emit(all_valid)


# Class is selectde from ui:widget or, failing that, from type
WIDGET_CLASSES = {
    "number": FloatString,
    "string": LineEdit,
    "boolean": CheckBox,
    "integer": FloatString,
    "textarea": TextEdit,
    "select": Combo,
    "column_grid": ColumnGridWidget,
    "horizontal_box": HorizontalBox,
    "vertical_box": VerticalBox,
    "hidden": HiddenWidget,
}
