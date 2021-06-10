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

from mxcubecore import ConvertUtils

from mxcubeqt.utils import qt_import, colors


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class LineEdit(qt_import.QLineEdit):
    """Standard LineEdit widget"""

    def __init__(self, parent, options):
        qt_import.QLineEdit.__init__(self, parent)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variableName"]
        if "defaultValue" in options:
            self.set_value(options["defaultValue"])
        self.setAlignment(qt_import.Qt.AlignRight)
        if options.get("readOnly"):
            self.setReadOnly(True)
            self.setEnabled(False)

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return ConvertUtils.text_type(self.text())

    def input_field_changed(self):
        """UI update function triggered by field value changes"""
        valid = self.is_valid()
        if valid:
            colors.set_widget_color(
                self, colors.LINE_EDIT_CHANGED, qt_import.QPalette.Base
            )
            if self.update_function is not None:
                self.update_function(self.parent())
        else:
            colors.set_widget_color(
                self, colors.LINE_EDIT_ERROR, qt_import.QPalette.Base
            )
        #
        self.parent().parametersValidSignal.emit(valid)


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
        val = options.get("lowerBound")
        if val is not None:
            self.validator.setBottom(val)
        val = options.get("upperBound")
        if val is not None:
            self.validator.setTop(val)
        self.update_function = options.get("update_function")

        self.textEdited.connect(self.input_field_changed)

    def set_value(self, value):
        self.setText(self.formatstr % value)

    def is_valid(self):
        if self.validator:
            return (
                self.validator.validate(self.text(), 0)[0]
                == qt_import.QValidator.Acceptable
            )
        else:
            return True


class TextEdit(qt_import.QTextEdit):
    """Standard text edit widget (multiline text)"""

    def __init__(self, parent, options):
        qt_import.QTextEdit.__init__(self, parent)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variableName"]
        if "defaultValue" in options:
            self.set_value(options["defaultValue"])
        self.setAlignment(qt_import.Qt.AlignRight)
        if options.get("readOnly"):
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
        return ConvertUtils.text_type(self.text())


class Combo(qt_import.QComboBox):
    """Standard ComboBox (pulldown) widget"""

    def __init__(self, parent, options):
        qt_import.QComboBox.__init__(self, parent)
        self.__name = options["variableName"]
        if "textChoices" in options:
            for val in options["textChoices"]:
                self.addItem(val)
        if "defaultValue" in options:
            self.set_value(options["defaultValue"])

        self.update_function = options.get("update_function")
        self.currentIndexChanged.connect(self.input_field_changed)

    def input_field_changed(self, input_field_text):
        """UI update function triggered by field value changes"""
        if self.update_function is not None:
            self.update_function(self.parent())

    def set_value(self, value):
        self.setCurrentIndex(self.findText(value))

    def get_value(self):
        return ConvertUtils.text_type(self.currentText())

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
        self.__name = options["variableName"]
        self.filepath = qt_import.QLineEdit(self)
        self.filepath.setAlignment(qt_import.Qt.AlignLeft)
        if "defaultValue" in options:
            self.filepath.setText(options["defaultValue"])
        self.open_dialog_btn = qt_import.QPushButton("...", self)
        self.open_dialog_btn.clicked.connect(self.open_file_dialog)

        self.layout().addWidget(self.filepath)
        self.layout().addWidget(self.open_dialog_btn)

    def set_value(self, value):
        self.filepath.setText(value)

    def get_value(self):
        return ConvertUtils.text_type(self.filepath.text())

    def get_name(self):
        return self.__name

    def open_file_dialog(self):
        start_path = os.path.dirname(ConvertUtils.text_type(self.filepath.text()))
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
        self.__name = options["variableName"]
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "defaultValue" in options:
            val = int(options["defaultValue"])
            self.setValue(val)
        if "upperBound" in options:
            self.setMaximum(int(options["upperBound"]))
        else:
            self.setMaximum(sys.maxsize)
        if "lowerBound" in options:
            self.setMinimum(int(options["lowerBound"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])

    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        val = int(self.value())
        return ConvertUtils.text_type(val)

    def get_name(self):
        return self.__name


class DoubleSpinBox(qt_import.QDoubleSpinBox):
    """Standard float/double (spinbox) widget"""

    CHANGED_COLOR = colors.LINE_EDIT_CHANGED

    def __init__(self, parent, options):
        qt_import.QDoubleSpinBox.__init__(self, parent)
        self.lineEdit().setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variableName"]
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "defaultValue" in options:
            val = float(options["defaultValue"])
            self.setValue(val)
        if "upperBound" in options:
            self.setMaximum(float(options["upperBound"]))
        else:
            self.setMaximum(sys.maxsize)
        if "lowerBound" in options:
            self.setMinimum(float(options["lowerBound"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])

    def set_value(self, value):
        self.setValue(int(value))

    def get_value(self):
        val = int(self.value())
        return ConvertUtils.text_type(val)

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
        qt_import.QCheckBox.__init__(self, options.get("uiLabel", "CheckBox"), parent)
        # self.setAlignment(qt_import.Qt.AlignLeft)
        self.__name = options["variableName"]
        state = (
            qt_import.Qt.Checked
            if options.get("defaultValue")
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


# Mapping of type fields to Classes
WIDGET_CLASSES = {
    "combo": Combo,
    "dblcombo": Combo,
    "spinbox": IntSpinBox,
    "text": LineEdit,
    "floatstring": FloatString,
    "file": File,
    "message": Message,
    "boolean": CheckBox,
    "float": DoubleSpinBox,
    "textarea": TextEdit,
}


def make_widget(parent, options):
    return WIDGET_CLASSES[options["type"]](parent, options)


class FieldsWidget(qt_import.QWidget):
    """Collection-of-widgets widget for parameter query"""
    parametersValidSignal = qt_import.pyqtSignal(bool)

    def __init__(self, fields, parent=None):
        qt_import.QWidget.__init__(self, parent)
        self.field_widgets = list()

        qt_import.QGridLayout(self)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )

        current_row = 0
        col_incr = 0
        # pad1: width of empty separating columns
        pad1 = " " * 4
        # Extra padding in front of columns 2, 3, ...
        # to offset space for boolean widgets
        pad2 = ""
        for field in fields:
            # should not happen but lets just skip them
            if (
                field["type"] != "message"
                and "uiLabel" not in field
                and not field["type"].startswith("dbl")
            ):
                continue

            # hack until the 'real' xml gets implemented server side
            # and this mess gets rewritten
            if field["type"] == "message":
                logging.debug("creating widget with options: %s", field)
                widget = make_widget(self, field)
                # message will be alone in the layout
                # so that will not fsck up the layout
                self.layout().addWidget(widget, current_row, current_row, 0, 1)
            else:
                logging.debug("creating widget with options: %s", field)
                widget = make_widget(self, field)
                # Temporary (like this brick ...) hack to get a nicer UI
                if isinstance(widget, TextEdit):
                    widget.setSizePolicy(
                        qt_import.QSizePolicy.MinimumExpanding,
                        qt_import.QSizePolicy.Minimum,
                    )
                else:
                    widget.setSizePolicy(
                        qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed
                    )
                self.field_widgets.append(widget)
                col = col_incr
                if field["type"] == "boolean":
                    self.layout().addWidget(
                        widget, current_row, col, 1, 2, qt_import.Qt.AlignLeft
                    )
                elif field["type"].startswith("dbl"):
                    # Double width widget, no label
                    self.layout().addWidget(
                        widget, current_row, col, 1, 2, qt_import.Qt.AlignLeft
                    )
                else:
                    pad = pad2 if col_incr else ""
                    label = qt_import.QLabel(pad + field["uiLabel"], self)
                    self.layout().addWidget(
                        label, current_row, col, qt_import.Qt.AlignLeft
                    )
                    self.layout().addWidget(
                        widget, current_row, 1 + col, qt_import.Qt.AlignLeft
                    )
                    # Add empty column, for separation purposes

                    hspacer = qt_import.QSpacerItem(
                        10,
                        20,
                        qt_import.QSizePolicy.MinimumExpanding,
                        qt_import.QSizePolicy.Minimum
                    )
                    # empty = qt_import.QLabel(pad1, self)
                    self.layout().addItem(
                        hspacer, current_row, col + 2, qt_import.Qt.AlignLeft
                    )

            current_row += 1
            if field.pop("NEW_COLUMN", False):
                current_row = 0
                # Increment column
                col_incr += 3

    def set_values(self, **values):
        """Set values for all fields from values dictionary"""
        for field in self.field_widgets:
            if field.get_name() in values:
                field.set_value(values[field.get_name()])

    def get_parameters_map(self):
        """Get paramer values dictionary for all fields"""
        return dict((w.get_name(), w.get_value()) for w in self.field_widgets)

    def invalid_fields(self):
        invalids = []

        for widget in self.field_widgets:
            if isinstance(widget, LineEdit):
                if not widget.is_valid():
                    invalids.append(widget.get_name())
        return invalids
