import qt
from lxml import etree
import os.path
import logging
import sys

# copied from the motor brick
# can display decimal places
class SpinBox(qt.QSpinBox):
    CHANGED_COLOR = qt.QColor(255,165,0)
    def __init__(self, parent, options):
        qt.QSpinBox.__init__(self,parent)
        self.decimalPlaces=1
        self.colorGroupDict={}
        self.setValidator(qt.QDoubleValidator(self))
        self.editor().setAlignment(qt.QWidget.AlignLeft)
        qt.QObject.connect(self.editor(),qt.SIGNAL('textChanged(const QString &)'),self.inputFieldChanged)
        self.__name = options['variableName']
        if options.has_key('unit'):
            qt.QSpinBox.setSuffix(self, ' ' + options['unit'])
        if options.has_key('defaultValue'):
            val = float(options['defaultValue'])
            self.setValue(int(val * float(10**self.decimalPlaces)))
        if options.has_key('upperBound'):
            self.setMaxValue(float(options['upperBound']))
        else:
            qt.QSpinBox.setMaxValue(self, sys.maxint)
        if options.has_key('lowerBound'):
            self.setMinValue(float(options['lowerBound']))
        if options.has_key('tooltip'):
            qt.QToolTip.add(self, options['tooltip'])

    def inputFieldChanged(self,text):
        self.setEditorBackgroundColor(SpinBox.CHANGED_COLOR)
    def setDecimalPlaces(self,places):
        current_val=float(self.value())/float(10**self.decimalPlaces)
        current_step=self.lineStep()
        current_min=float(self.minValue())/float(10**self.decimalPlaces)
        current_max=float(self.maxValue())/float(10**self.decimalPlaces)
        self.decimalPlaces=places
        self.blockSignals(True)
        self.setMinValue(current_min)
        self.setMaxValue(current_max)
        self.setValue(current_val)
        self.blockSignals(False)
        self.setLineStep(current_step)
    def decimalPlaces(self):
        return self.decimalPlaces
    def setMinValue(self,value):
        try:
            qt.QSpinBox.setMinValue(self,int(value*(10**self.decimalPlaces)))
        except (TypeError,ValueError):
            logging.getLogger().error("MotorSpinBoxBrick: error setting minimum value (%d)" % value)
    def setMaxValue(self,value):
        try:
            qt.QSpinBox.setMaxValue(self,int(value*(10**self.decimalPlaces)))
        except (TypeError,ValueError):
            logging.getLogger().error("MotorSpinBoxBrick: error setting maximum value (%d)" % value)
    def mapValueToText(self,value):
        f=float(value)/float(10**self.decimalPlaces)
        return qt.QString(str(f))
    def mapTextToValue(self):
        t = str(self.text())
        try:
            ret = int(float(t)*(10**self.decimalPlaces))
        except:
            return (0, False)
        else:
            return (ret, True) 
    def setValue(self,value):
        if type(value)==type(0.0):
            value=int(value*(10**self.decimalPlaces))
        self.editor().blockSignals(True)
        qt.QSpinBox.setValue(self,value)
        self.editor().blockSignals(False)
    def lineStep(self):
        step=float(qt.QSpinBox.lineStep(self))/(10**self.decimalPlaces)
        return step
    def setLineStep(self,step):
        if type(step)==type(0.0):
            s=int(step*(10**self.decimalPlaces))
        else:
            s=step
        try:
            qt.QSpinBox.setLineStep(self,s)
        except (TypeError,ValueError):
            logging.getLogger().error("MotorSpinBoxBrick: error setting step value (%d)" % step)
    def eventFilter(self,obj,ev):
        if isinstance(ev,qt.QContextMenuEvent):
            self.emit(qt.PYSIGNAL("contextMenu"),())
            return True
        else:
            return qt.QSpinBox.eventFilter(self,obj,ev)
    def setEditorBackgroundColor(self,color):
        #print "SpinBox.setEditorBackgroundColor",color
        editor=self.editor()
        editor.setPaletteBackgroundColor(color)
        spinbox_palette=editor.palette()
        try:
            cg=self.colorGroupDict[color.rgb()]
        except KeyError:
            cg=qt.QColorGroup(spinbox_palette.disabled())
            cg.setColor(cg.Background,color)
            self.colorGroupDict[color.rgb()]=cg
        spinbox_palette.setDisabled(cg)

    def set_value(self, value):
        val = float(value)
        self.setValue(val)
    def get_value(self):
        val=float(self.value())/float(10**self.decimalPlaces)
        return str(val)
    def get_name(self):
        return self.__name

class LineEdit(qt.QLineEdit):
    def __init__(self, parent, options):
        qt.QLineEdit.__init__(self, parent)
        self.setAlignment(qt.Qt.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('defaultValue'):
            self.setText(options['defaultValue'])
        self.setAlignment(qt.Qt.AlignRight)
    def set_value(self, value):
        self.setText(value)
    def get_name(self):
        return self.__name
    def get_value(self):
        return str(self.text())

class Combo(qt.QComboBox):
    def __init__(self, parent, options):
        qt.QComboBox.__init__(self, parent)
        self.__name = options['variableName']
        if options.has_key('textChoices'):
            for val in options['textChoices']:
                self.insertItem(val)
        if options.has_key('defaultValue'):
            self.setCurrentText(options['defaultValue'])
    def set_value(self, value):
        self.setCurrentText(value)
    def get_value(self):
        return str(self.currentText())
    def get_name(self):
        return self.__name

class File(qt.QWidget):
    def __init__(self, parent, options):
        qt.QWidget.__init__(self, parent)

        # do not allow qt to stretch us vertically
        sp = self.sizePolicy()
        sp.setVerData(qt.QSizePolicy.Fixed)
        self.setSizePolicy(sp)
        
        qt.QHBoxLayout(self)
        self.__name = options['variableName']
        self.filepath = qt.QLineEdit(self)
        self.filepath.setAlignment(qt.Qt.AlignLeft)
        if options.has_key('defaultValue'):
            self.filepath.setText(options['defaultValue'])
        self.open_dialog_btn = qt.QPushButton('...', self)
        qt.QObject.connect(self.open_dialog_btn, qt.SIGNAL('clicked()'), self.open_file_dialog)

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
            start_path = qt.QString.null
        path = qt.QFileDialog.getOpenFileName(start_path, qt.QString.null, self)
        if not path.isNull():
            self.filepath.setText(path)


class IntSpinBox(qt.QSpinBox):
    CHANGED_COLOR = qt.QColor(255,165,0)
    def __init__(self, parent, options):
        qt.QSpinBox.__init__(self,parent)
        self.editor().setAlignment(qt.QWidget.AlignLeft)
        self.__name = options['variableName']
        if options.has_key('unit'):
            qt.QSpinBox.setSuffix(self, ' ' + options['unit'])
        if options.has_key('defaultValue'):
            val = int(options['defaultValue'])
            self.setValue(val)
        if options.has_key('upperBound'):
            self.setMaxValue(int(options['upperBound']))
        else:
            qt.QSpinBox.setMaxValue(self, sys.maxint)
        if options.has_key('lowerBound'):
            self.setMinValue(int(options['lowerBound']))
        if options.has_key('tooltip'):
            qt.QToolTip.add(self, options['tooltip'])

    def set_value(self, value):
        self.setValue(int(value))
    def get_value(self):
        val=int(self.value())
        return str(val)
    def get_name(self):
        return self.__name
    

class Message(qt.QWidget):
    def __init__(self, parent, options):
        qt.QWidget.__init__(self, parent)
        logging.debug('making message with options %r', options)
        qt.QHBoxLayout(self)
        icon = qt.QLabel(self)
        icon.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)

        # all the following stuff is there to get the standard icon
        # for our level directly from qt
        mapping = {
            'warning': qt.QMessageBox.Warning,
            'info': qt.QMessageBox.Information,
            'error': qt.QMessageBox.Critical,
            }
        level = mapping.get(options['level'])
        if level is not None:
            icon.setPixmap(qt.QMessageBox.standardIcon(level))
        
        text = qt.QLabel(options['text'], self)
        
        self.layout().addWidget(icon)
        self.layout().addWidget(text)
    # make the current code happy, temp hack
    def get_value(self):
        return 'no value'
    def get_name(self):
        return 'a message'
    def set_value(self, value):
        pass
        
        

WIDGET_CLASSES = {
    'combo': Combo,
    'spinbox': IntSpinBox,
    'text': LineEdit,
    'file': File,
    'message': Message,
}

def make_widget(parent, options):
    return WIDGET_CLASSES[options['type']](parent, options)


class FieldsWidget(qt.QWidget):
    def __init__(self, fields, parent=None):
        qt.QWidget.__init__(self, parent)
        self.field_widgets = list()
        

        qt.QVBoxLayout(self)
        grid = qt.QGridLayout()
#        button_box = qt.QHBoxLayout()

        current_row = 0
        for field in fields:
            # should not happen but lets just skip them
            if field['type'] != 'message' and not field.has_key('uiLabel'):
                continue

            # hack until the 'real' xml gets implemented server side and this mess gets rewritten
            if field['type'] == 'message':
                logging.debug('creating widget with options: %s', field)
                w = make_widget(self, field)
                # message will be alone in the layout so that will not fsck up the layout
                grid.addMultiCellWidget(w, current_row, current_row, 0, 1)
            else:
                label = qt.QLabel(field['uiLabel'], self)
                logging.debug('creating widget with options: %s', field)
                w = make_widget(self, field)
                self.field_widgets.append(w)
                grid.addWidget(label, current_row, 0)
                grid.addWidget(w, current_row, 1)
        
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

        self.layout().addLayout(grid)
#        self.layout().addLayout(button_box)

    def set_values(self, values):
        for field in self.field_widgets:
            if values.has_key(field.get_name()):
                field.set_value(values[field.get_name()])

    def __print_xml(self):
        print self.get_xml(True)

    def get_xml(self, olof=False):
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
