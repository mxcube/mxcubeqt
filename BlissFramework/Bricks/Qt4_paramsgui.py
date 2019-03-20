"""Qt4 port of paramsgui - rhfogh Jan 2018

Incorporates additions for GPhL workflow code"""

from PyQt4 import QtCore
from PyQt4 import QtGui
# from lxml import etree
import os.path
import logging
import sys

class LineEdit(QtGui.QLineEdit):
    def __init__(self, parent, options):
        QtGui.QLineEdit.__init__(self, parent)
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('defaultValue'):
            self.setText(options['defaultValue'])
        self.setAlignment(QtCore.Qt.AlignRight)
        if options.get('readOnly'):
            self.setReadOnly(True)
            self.setEnabled(False)
    def set_value(self, value):
        self.setText(value)
    def get_name(self):
        return self.__name
    def get_value(self):
        return str(self.text())

class TextEdit(QtGui.QTextEdit):
    def __init__(self, parent, options):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('defaultValue'):
            self.setText(options['defaultValue'])
        self.setAlignment(QtCore.Qt.AlignRight)
        if options.get('readOnly'):
            self.setReadOnly(True)
            self.setEnabled(False)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
    def set_value(self, value):
        self.setText(value)
    def get_name(self):
        return self.__name
    def get_value(self):
        return str(self.text())

class Combo(QtGui.QComboBox):
    def __init__(self, parent, options):
        QtGui.QComboBox.__init__(self, parent)
        self.__name = options['variableName']
        if options.has_key('textChoices'):
            for val in options['textChoices']:
                self.addItem(val)
        if options.has_key('defaultValue'):
            self.set_value(options['defaultValue'])
    def set_value(self, value):
        self.setCurrentIndex(self.findText(value))
    def get_value(self):
        return str(self.currentText())
    def get_name(self):
        return self.__name

class File(QtGui.QWidget):
    def __init__(self, parent, options):
        QtGui.QWidget.__init__(self, parent)

        # do not allow qt to stretch us vertically
        sp = self.sizePolicy()
        sp.setVerData(QtGui.QSizePolicy.Fixed)
        self.setSizePolicy(sp)

        QtGui.QHBoxLayout(self)
        self.__name = options['variableName']
        self.filepath = QtGui.QLineEdit(self)
        self.filepath.setAlignment(QtCore.Qt.AlignLeft)
        if options.has_key('defaultValue'):
            self.filepath.setText(options['defaultValue'])
        self.open_dialog_btn = QtGui.QPushButton('...', self)
        QtCore.QObject.connect(self.open_dialog_btn, QtCore.SIGNAL('clicked()'),
                               self.open_file_dialog)

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
            start_path = ''
        path = QtGui.QFileDialog(self).getOpenFileName(directory=start_path)
        if not path.isNull():
            self.filepath.setText(path)


class IntSpinBox(QtGui.QSpinBox):
    CHANGED_COLOR = QtGui.QColor(255,165,0)
    def __init__(self, parent, options):
        QtGui.QSpinBox.__init__(self,parent)
        self.lineEdit().setAlignment(QtCore.Qt.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('unit'):
            self.setSuffix(' ' + options['unit'])
        if options.has_key('defaultValue'):
            val = int(options['defaultValue'])
            self.setValue(val)
        if options.has_key('upperBound'):
            self.setMaximum(int(options['upperBound']))
        else:
            self.setMaximum(sys.maxint)
        if options.has_key('lowerBound'):
            self.setMinimum(int(options['lowerBound']))
        if options.has_key('tooltip'):
            self.setToolTip(options['tooltip'])

    def set_value(self, value):
        self.setValue(int(value))
    def get_value(self):
        val=int(self.value())
        return str(val)
    def get_name(self):
        return self.__name


class DoubleSpinBox(QtGui.QDoubleSpinBox):
    CHANGED_COLOR = QtGui.QColor(255,165,0)
    def __init__(self, parent, options):
        QtGui.QDoubleSpinBox.__init__(self,parent)
        self.lineEdit().setAlignment(QtGui.QWidget.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('unit'):
            self.setSuffix(' ' + options['unit'])
        if options.has_key('defaultValue'):
            val = float(options['defaultValue'])
            self.setValue(val)
        if options.has_key('upperBound'):
            self.setMaximum(float(options['upperBound']))
        else:
            self.setMaximum(sys.maxint)
        if options.has_key('lowerBound'):
            self.setMinimum(float(options['lowerBound']))
        if options.has_key('tooltip'):
            self.setToolTip(options['tooltip'])

    def set_value(self, value):
        self.setValue(int(value))
    def get_value(self):
        val=int(self.value())
        return str(val)
    def get_name(self):
        return self.__name
    

class Message(QtGui.QWidget):
    def __init__(self, parent, options):
        QtGui.QWidget.__init__(self, parent)
        logging.debug('making message with options %r', options)
        QtGui.QHBoxLayout(self)
        icon = QtGui.QLabel(self)
        icon.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # all the following stuff is there to get the standard icon
        # for our level directly from qt
        mapping = {
            'warning': QtGui.QMessageBox.Warning,
            'info': QtGui.QMessageBox.Information,
            'error': QtGui.QMessageBox.Critical,
            }
        level = mapping.get(options['level'])
        if level is not None:
            icon.setPixmap(QtGui.QMessageBox.standardIcon(level))
        
        text = QtGui.QLabel(options['text'], self)
        
        self.layout().addWidget(icon)
        self.layout().addWidget(text)
    # make the current code happy, temp hack
    def get_value(self):
        return 'no value'
    def get_name(self):
        return 'a message'
    def set_value(self, value):
        pass
        
class CheckBox(QtGui.QCheckBox):
    def __init__(self, parent, options):
        QtGui.QCheckBox.__init__(self, options.get('uiLabel','CheckBox'), parent)
        # self.setAlignment(QtCore.Qt.AlignLeft)
        self.__name = options['variableName']
        state = (QtCore.Qt.Checked if options.get('defaultValue')
                 else QtCore.Qt.Unchecked)
        self.setCheckState(state)
        # self.setAlignment(QtCore.Qt.AlignRight)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
    def set_value(self, value):
        self.setChecked(value)
    def get_name(self):
        return self.__name
    def get_value(self):
        return self.isChecked()

WIDGET_CLASSES = {
    'combo': Combo,
    'spinbox': IntSpinBox,
    'text': LineEdit,
    'file': File,
    'message': Message,
    'boolean' : CheckBox,

    'float':DoubleSpinBox,
    'textarea':TextEdit
}

def make_widget(parent, options):
    return WIDGET_CLASSES[options['type']](parent, options)


class FieldsWidget(QtGui.QWidget):

    def __init__(self, fields, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.field_widgets = list()
        

#        qt.QVBoxLayout(self)
#        grid = qt.QGridLayout()
        QtGui.QGridLayout(self)
#        button_box = qt.QHBoxLayout()
#         # We're trying to pack everything together on the lower left corner
#         self.setSizePolicy(QtGui.QSizePolicy.Fixed,
#                            QtGui.QSizePolicy.Fixed)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        current_row = 0
        col_incr = 0
        pad = ''
        for field in fields:
            # should not happen but lets just skip them
            if field['type'] != 'message' and not field.has_key('uiLabel'):
                continue

            # hack until the 'real' xml gets implemented server side
            # and this mess gets rewritten
            if field['type'] == 'message':
                # NBNB This will NOT work with NEW_COLUMN
                logging.debug('creating widget with options: %s', field)
                w = make_widget(self, field)
                # message will be alone in the layout
                # so that will not fsck up the layout
                self.layout().addWidget(w, current_row, current_row,
                                                 0, 1)
            else:
                logging.debug('creating widget with options: %s', field)
                w = make_widget(self, field)
                # Temporary (like this brick ...) hack to get a nicer UI
                if isinstance(w, TextEdit):
                    w.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                    QtGui.QSizePolicy.Minimum)
                else:
                    w.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
                self.field_widgets.append(w)
                if field['type'] == 'boolean':
                    self.layout().addWidget(w, current_row, 0 + col_incr, 1, 2,
                                            QtCore.Qt.AlignLeft)
                else:
                    label = QtGui.QLabel(pad + field['uiLabel'], self)
                    self.layout().addWidget(label, current_row, 0 + col_incr,
                                            QtCore.Qt.AlignLeft)
                    self.layout().addWidget(w, current_row, 1 + col_incr,
                                            QtCore.Qt.AlignLeft)
        
            current_row += 1
            if field.pop('NEW_COLUMN', False):
                # Increment column
                col_incr += 2
                current_row = 0
                pad = ' ' * 5

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
            if values.has_key(field.get_name()):
                field.set_value(values[field.get_name()])

    def __print_xml(self):
        print (self.get_xml(True))

    def get_xml(self, olof=False):
        from lxml import etree
        root = etree.Element('parameters')
        for w in self.field_widgets:
            name = w.get_name()
            value = w.get_value()
            if not olof:
                param = etree.SubElement(root, w.get_name())
                param.text = w.get_value()
            else:
                param = etree.SubElement(root, 'parameter')
                name_tag = etree.SubElement(param, 'name')
                value_tag = etree.SubElement(param, 'value')
                name_tag.text = name
                value_tag.text = value

        return etree.tostring(root, pretty_print=True)

    def get_parameters_map(self):
        return dict((w.get_name(), w.get_value()) for w in self.field_widgets)

        #ret = dict()
        #for w in self.field_widgets:
        #    ret[w.get_name()] = w.get_value()
        #return ret
