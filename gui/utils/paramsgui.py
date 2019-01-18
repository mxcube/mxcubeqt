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

import os.path
import logging
import sys

import QtImport


"""port of paramsgui - rhfogh Jan 2018

Incorporates additions for GPhL workflow code"""


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class LineEdit(QtImport.QLineEdit):
    def __init__(self, parent, options):
        QtImport.QLineEdit.__init__(self, parent)
        self.setAlignment(QtImport.Qt.AlignLeft)
        self.__name = options["variableName"]
        if "defaultValue" in options:
            self.setText(options["defaultValue"])
        self.setAlignment(QtImport.Qt.AlignRight)
        if options.get("readOnly"):
            self.setReadOnly(True)
            self.setEnabled(False)

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return str(self.text())


class TextEdit(QtImport.QTextEdit):
    def __init__(self, parent, options):
        QtImport.QTextEdit.__init__(self, parent)
        self.setAlignment(QtImport.Qt.AlignLeft)
        self.__name = options["variableName"]
        if "defaultValue" in options:
            self.setText(options["defaultValue"])
        self.setAlignment(QtImport.Qt.AlignRight)
        if options.get("readOnly"):
            self.setReadOnly(True)
            self.setEnabled(False)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding)

    def set_value(self, value):
        self.setText(value)

    def get_name(self):
        return self.__name

    def get_value(self):
        return str(self.text())


class Combo(QtImport.QComboBox):
    def __init__(self, parent, options):
        QtImport.QComboBox.__init__(self, parent)
        self.__name = options["variableName"]
        if "textChoices" in options:
            for val in options["textChoices"]:
                self.addItem(val)
        if "defaultValue" in options:
            self.set_value(options["defaultValue"])

    def set_value(self, value):
        self.setCurrentIndex(self.findText(value))

    def get_value(self):
        return str(self.currentText())

    def get_name(self):
        return self.__name


class File(QtImport.QWidget):
    def __init__(self, parent, options):
        QtImport.QWidget.__init__(self, parent)

        # do not allow qt to stretch us vertically
        sp = self.sizePolicy()
        sp.setVerData(QtImport.QSizePolicy.Fixed)
        self.setSizePolicy(sp)

        QtImport.QHBoxLayout(self)
        self.__name = options["variableName"]
        self.filepath = QtImport.QLineEdit(self)
        self.filepath.setAlignment(QtImport.Qt.AlignLeft)
        if "defaultValue" in options:
            self.filepath.setText(options["defaultValue"])
        self.open_dialog_btn = QtImport.QPushButton("...", self)
        QtImport.QObject.connect(
            self.open_dialog_btn, QtImport.SIGNAL("clicked()"), self.open_file_dialog
        )

        self.layout().addWidget(self.filepath)
        self.layout().addWidget(self.open_dialog_btn)

    def set_value(self, value):
        self.filepath.setText(value)

    def get_value(self):
        return str(self.filepath.text())

    def get_name(self):
        return self.__name

    def open_file_dialog(self):
        start_path = os.path.dirname(str(self.filepath.text()))
        if not os.path.exists(start_path):
            start_path = ""
        path = QtImport.QFileDialog(self).getOpenFileName(directory=start_path)
        if not path.isNull():
            self.filepath.setText(path)


class IntSpinBox(QtImport.QSpinBox):
    CHANGED_COLOR = QtImport.QColor(255, 165, 0)

    def __init__(self, parent, options):
        QtImport.QSpinBox.__init__(self, parent)
        self.lineEdit().setAlignment(QtImport.Qt.AlignLeft)
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
        return str(val)

    def get_name(self):
        return self.__name


class DoubleSpinBox(QtImport.QDoubleSpinBox):
    CHANGED_COLOR = QtImport.QColor(255, 165, 0)

    def __init__(self, parent, options):
        QtImport.QDoubleSpinBox.__init__(self, parent)
        self.lineEdit().setAlignment(QtImport.QWidget.AlignLeft)
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
        return str(val)

    def get_name(self):
        return self.__name


class Message(QtImport.QWidget):
    def __init__(self, parent, options):
        QtImport.QWidget.__init__(self, parent)
        logging.debug("making message with options %r", options)
        QtImport.QHBoxLayout(self)
        icon = QtImport.QLabel(self)
        icon.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)

        # all the following stuff is there to get the standard icon
        # for our level directly from qt
        mapping = {
            "warning": QtImport.QMessageBox.Warning,
            "info": QtImport.QMessageBox.Information,
            "error": QtImport.QMessageBox.Critical,
        }
        level = mapping.get(options["level"])
        if level is not None:
            icon.setPixmap(QtImport.QMessageBox.standardIcon(level))

        text = QtImport.QLabel(options["text"], self)

        self.layout().addWidget(icon)
        self.layout().addWidget(text)

    # make the current code happy, temp hack

    def get_value(self):
        return "no value"

    def get_name(self):
        return "a message"

    def set_value(self, value):
        pass


WIDGET_CLASSES = {
    "combo": Combo,
    "spinbox": IntSpinBox,
    "text": LineEdit,
    "file": File,
    "message": Message,
    "float": DoubleSpinBox,
    "textarea": TextEdit,
}


def make_widget(parent, options):
    return WIDGET_CLASSES[options["type"]](parent, options)


class FieldsWidget(QtImport.QWidget):
    def __init__(self, fields, parent=None):
        QtImport.QWidget.__init__(self, parent)
        self.field_widgets = list()

        #        qt.QVBoxLayout(self)
        #        grid = qt.QGridLayout()
        QtImport.QGridLayout(self)
        #        button_box = qt.QHBoxLayout()
        #         # We're trying to pack everything together on the lower left corner
        #         self.setSizePolicy(QtImport.QSizePolicy.Fixed,
        #                            QtImport.QSizePolicy.Fixed)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding)

        current_row = 0
        for field in fields:
            # should not happen but lets just skip them
            if field["type"] != "message" and "uiLabel" not in field:
                continue

            # hack until the 'real' xml gets implemented server side
            # and this mess gets rewritten
            if field["type"] == "message":
                logging.debug("creating widget with options: %s", field)
                w = make_widget(self, field)
                # message will be alone in the layout
                # so that will not fsck up the layout
                self.layout().addWidget(w, current_row, current_row, 0, 1)
            else:
                label = QtImport.QLabel(field["uiLabel"], self)
                logging.debug("creating widget with options: %s", field)
                w = make_widget(self, field)
                # Temporary (like this brick ...) hack to get a nicer UI
                if isinstance(w, TextEdit):
                    w.setSizePolicy(
                        QtImport.QSizePolicy.MinimumExpanding, QtImport.QSizePolicy.Minimum
                    )
                else:
                    w.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)
                self.field_widgets.append(w)
                self.layout().addWidget(label, current_row, 0, QtImport.Qt.AlignLeft)
                self.layout().addWidget(w, current_row, 1, QtImport.Qt.AlignLeft)

            current_row += 1

    #        ok_button = qt.QPushButton("OK", self)
    #        cancel_button = qt.QPushButton('Cancel', self)
    #
    #        #XXX:testing
    #        qt.QObject.connect(ok_button, qt.SIGNAL('clicked()'),
    #                           self.__print_xml)
    #
    #        button_box.addWidget(ok_button)
    #        button_box.addWidget(cancel_button)

    #        self.layout().addLayout(button_box)

    def set_values(self, values):
        for field in self.field_widgets:
            if field.get_name() in values:
                field.set_value(values[field.get_name()])

    def __print_xml(self):
        print(self.get_xml(True))

    def get_xml(self, olof=False):
        from lxml import etree

        root = etree.Element("parameters")
        for w in self.field_widgets:
            name = w.get_name()
            value = w.get_value()
            if not olof:
                param = etree.SubElement(root, w.get_name())
                param.text = w.get_value()
            else:
                param = etree.SubElement(root, "parameter")
                name_tag = etree.SubElement(param, "name")
                value_tag = etree.SubElement(param, "value")
                name_tag.text = name
                value_tag.text = value

        return etree.tostring(root, pretty_print=True)

    def get_parameters_map(self):
        return dict((w.get_name(), w.get_value()) for w in self.field_widgets)

        # ret = dict()
        # for w in self.field_widgets:
        #    ret[w.get_name()] = w.get_value()
        # return ret
