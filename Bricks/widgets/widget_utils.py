import qt
from BlissFramework.Utils import widget_colors

class DataModelInputBinder(object):
    def __init__(self,  obj):
        object.__init__(self)
        self.__pobj = obj
        
        # Key - Attribute name of the persistant object.
        # Value - The tuple (widget, validator, type_fn)
        self.bindings = {}
                
    def __checkbox_update_value(self, field_name, new_value):
        setattr(self.__pobj, field_name, new_value)   

    def __combobox_update_value(self, field_name, new_value):
        setattr(self.__pobj, field_name, new_value)

    def __ledit_update_value(self, field_name, new_value, type_fn, validator):
        if self.__validated(validator, self.bindings[field_name][0], 
                            new_value):
            try:
                setattr(self.__pobj, field_name, type_fn(new_value)) 
            except ValueError:
                if new_value != '':
                    raise

    def __validated(self, validator, widget, new_value):
        if validator:
            if validator.validate(new_value, widget.cursorPosition())[0] \
                    == qt.QValidator.Acceptable:
                widget.setPaletteBackgroundColor(qt.QWidget.white)
                return True
            else:
                widget.setPaletteBackgroundColor(widget_colors.LIGHT_RED)
                return False
        else:
            return True

    def get_model(self):
        return self.__pobj
    
    def set_model(self, obj):
        self.__pobj = obj
        self.init_bindings()
        self.validate_all()
   
    def init_bindings(self):
        for (key, value) in self.bindings.iteritems():
            if isinstance(value[0], qt.QLineEdit):
                value[0].setText(str(getattr(self.__pobj, key)))
            elif isinstance(value[0], qt.QLabel):        
                value[0].setText(str(getattr(self.__pobj, key)))
            elif isinstance(value[0], qt.QComboBox):
                value[0].setCurrentItem(int(getattr(self.__pobj, key)))
            elif isinstance(value[0], qt.QCheckBox) or \
                    isinstance(value[0], qt.QRadioButton):
                value[0].setChecked(bool(getattr(self.__pobj, key)))

    def bind_value_update(self, field_name, widget, type_fn, validator = None):
        self.bindings[field_name] = (widget, validator, type_fn)

        if isinstance(widget, qt.QLineEdit):        
            qt.QObject.connect(widget, 
                            qt.SIGNAL("textChanged(const QString &)"), 
                            lambda new_value: \
                                self.__ledit_update_value(field_name,
                                                          new_value,
                                                          type_fn, 
                                                          validator))
            
            widget.setText(str(getattr(self.__pobj, field_name)))


        elif isinstance(widget, qt.QLabel):        
            widget.setText(str(getattr(self.__pobj, field_name)))

        elif isinstance(widget, qt.QComboBox):
            qt.QObject.connect(widget, 
                            qt.SIGNAL("activated(int)"), 
                            lambda new_value: \
                                self.__combobox_update_value(field_name,
                                                             new_value))

            widget.setCurrentItem(int(getattr(self.__pobj, field_name)))

        elif isinstance(widget, qt.QCheckBox) or \
                isinstance(widget, qt.QRadioButton):
            qt.QObject.connect(widget, 
                            qt.SIGNAL("toggled(bool)"), 
                            lambda new_value: \
                                self.__checkbox_update_value(field_name,
                                                             new_value))

            widget.setChecked(bool(getattr(self.__pobj, field_name)))

    def validate_all(self):
        result = []

        for (key, value) in self.bindings.iteritems():
            widget = value[0]
            validator = value[1]
            
            if validator:
                if isinstance(widget, qt.QLineEdit):
                    if not self.__validated(validator,
                                            widget, 
                                            widget.text()):
                        result.append(key)
                elif isinstance(widget, qt.QComboBox):
                    pass
                elif isinstance(widget, qt.QCheckBox) or \
                        isinstance(widget, qt.QRadioButton):
                    pass

        return result
        
        
        



