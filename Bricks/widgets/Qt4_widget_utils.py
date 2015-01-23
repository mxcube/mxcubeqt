from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework.Utils import Qt4_widget_colors
from HardwareRepository.dispatcher import dispatcher

class DataModelInputBinder(object):
    def __init__(self,  obj):
        object.__init__(self)
        self.__model = obj
        
        # Key - field name/attribute name of the persistant object.
        # Value - The tuple (widget, validator, type_fn)
        self.bindings = {}
        dispatcher.connect(self._update_widget, "model_update", dispatcher.Any)
                
    def __checkbox_update_value(self, field_name, new_value):
        setattr(self.__model, field_name, new_value)
        dispatcher.send("model_update", self.__model, field_name, self)
        
    def __combobox_update_value(self, field_name, new_value):
        setattr(self.__model, field_name, new_value)
        dispatcher.send("model_update", self.__model, field_name, self)

    def __ledit_update_value(self, field_name, new_value, type_fn, validator):
        if self.__validated(validator, self.bindings[field_name][0], 
                            new_value):
            try:
                setattr(self.__model, field_name, type_fn(new_value)) 
            except ValueError:
                if new_value != '':
                    raise
            else:
                dispatcher.send("model_update", self.__model, field_name, self)

    def __validated(self, validator, widget, new_value):
        if validator:
            if validator.validate(new_value, widget.cursorPosition())[0] \
                    == QtGui.QValidator.Acceptable:
                Qt4_widget_colors.set_widget_color(widget, QtCore.Qt.white) 
                return True
            else:
                Qt4_widget_colors.set_widget_color(widget, Qt4_widget_colors.LIGHT_RED)
                return False
        else:
            return True

    def get_model(self):
        return self.__model
    
    def set_model(self, obj):
        self.__model = obj
        self.init_bindings()
        self.validate_all()
   
    def init_bindings(self):
        for field_name in self.bindings.iterkeys():
            self._update_widget(field_name, None)

    def _update_widget(self, field_name, data_binder):
	if data_binder == self:
	    return
        try:
            widget, validator, type_fn = self.bindings[field_name]
        except KeyError:
            return
   
        try:
            widget.blockSignals(True)

            if isinstance(widget, QtGui.QLineEdit):
                if type_fn is float and validator:
                    pattern = "%." + str(validator.decimals()) + 'f'
                    widget.setText(pattern % float(getattr(self.__model, field_name)))
                else:
                    widget.setText(str(getattr(self.__model, field_name)))

                widget.setText(str(getattr(self.__model, field_name)))
            elif isinstance(widget, QtGui.QLabel):        
                widget.setText(str(getattr(self.__model, field_name)))
            elif isinstance(widget, QtGui.QComboBox):
                widget.setCurrentIndex(int(getattr(self.__model, field_name)))
            elif isinstance(widget, QtGui.QCheckBox) or \
                    isinstance(widget, QtGui.QRadioButton):
                widget.setChecked(bool(getattr(self.__model, field_name)))       
        finally:
            widget.blockSignals(False)
        

    def bind_value_update(self, field_name, widget, type_fn, validator = None):
        self.bindings[field_name] = (widget, validator, type_fn)
        
        if isinstance(widget, QtGui.QLineEdit):        
            QtCore.QObject.connect(widget, 
                            QtCore.SIGNAL("textChanged(const QString &)"), 
                            lambda new_value: \
                                self.__ledit_update_value(field_name,
                                                          new_value,
                                                          type_fn, 
                                                          validator))
            if type_fn is float and validator:
                pattern = "%." + str(validator.decimals()) + 'f'
                widget.setText(pattern % float(getattr(self.__model, field_name)))
            else:
                widget.setText(str(getattr(self.__model, field_name)))


        elif isinstance(widget, QtGui.QLabel):        
            widget.setText(str(getattr(self.__model, field_name)))

        elif isinstance(widget, QtGui.QComboBox):
            QtCore.QObject.connect(widget, 
                            QtCore.SIGNAL("activated(int)"), 
                            lambda new_value: \
                                self.__combobox_update_value(field_name,
                                                             new_value))

            widget.setCurrentIndex(int(getattr(self.__model, field_name)))

        elif isinstance(widget, QtGui.QCheckBox) or \
                isinstance(widget, QtGui.QRadioButton):
            QtCore.QObject.connect(widget, 
                            QtCore.SIGNAL("toggled(bool)"), 
                            lambda new_value: \
                                self.__checkbox_update_value(field_name,
                                                             new_value))

            widget.setChecked(bool(getattr(self.__model, field_name)))

    def validate_all(self):
        result = []

        for (key, value) in self.bindings.iteritems():
            widget = value[0]
            validator = value[1]
            
            if validator:
                if isinstance(widget, QtGui.QLineEdit):
                    if not self.__validated(validator,
                                            widget, 
                                            widget.text()):
                        result.append(key)
                elif isinstance(widget, QtGui.QComboBox):
                    pass
                elif isinstance(widget, QtGui.QCheckBox) or \
                        isinstance(widget, QtGui.QRadioButton):
                    pass

        return result
