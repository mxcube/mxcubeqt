from qt import *
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
            #if isinstance(validator, QDoubleValidator):
            #    format_str =  "%." + str(validator.decimals()) + "f"
            #    new_value = format_str % type_fn(new_value)
            #    setattr(self.__pobj, field_name, new_value) 
            #else:
            try:
                setattr(self.__pobj, field_name, type_fn(new_value)) 
            except ValueError:
                if new_value != '':
                    raise


    def __validated(self, validator, widget, new_value):
        if validator:
            if validator.validate(new_value, widget.cursorPosition())[0] \
                    == QValidator.Acceptable:
                widget.setPaletteBackgroundColor(QWidget.white)
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
            if isinstance(value[0], QLineEdit):
                value[0].setText(str(getattr(self.__pobj, key)))
            elif isinstance(value[0], QLabel):        
                value[0].setText(str(getattr(self.__pobj, key)))
            elif isinstance(value[0], QComboBox):
                value[0].setCurrentItem(int(getattr(self.__pobj, key)))
            elif isinstance(value[0], QCheckBox) or \
                    isinstance(value[0], QRadioButton):
                value[0].setChecked(bool(getattr(self.__pobj, key)))


    def bind_value_update(self, field_name, widget, type_fn, validator = None):
        self.bindings[field_name] = (widget, validator, type_fn)

        if isinstance(widget, QLineEdit):        
            QObject.connect(widget, 
                            SIGNAL("textChanged(const QString &)"), 
                            lambda new_value: \
                                self.__ledit_update_value(field_name,
                                                          new_value,
                                                          type_fn, 
                                                          validator))
            
            widget.setText(str(getattr(self.__pobj, field_name)))


        elif isinstance(widget, QLabel):        
            widget.setText(str(getattr(self.__pobj, field_name)))

        elif isinstance(widget, QComboBox):
            QObject.connect(widget, 
                            SIGNAL("activated(int)"), 
                            lambda new_value: \
                                self.__combobox_update_value(field_name,
                                                             new_value))

            widget.setCurrentItem(int(getattr(self.__pobj, field_name)))

        elif isinstance(widget, QCheckBox) or \
                isinstance(widget, QRadioButton):
            QObject.connect(widget, 
                            SIGNAL("toggled(bool)"), 
                            lambda new_value: \
                                self.__checkbox_update_value(field_name,
                                                             new_value))

            widget.setChecked(bool(getattr(self.__pobj, field_name)))


    def validate_all(self):
        result = []

        for (key, value) in self.bindings.iteritems():
            
            widget = value[0]
            validator = value[1]
            type_fn = value[2]
            
            if validator:
                if isinstance(widget, QLineEdit):
                    if not self.__validated(validator,
                                            widget, 
                                            widget.text()):
                        result.append(key)
                elif isinstance(widget, QComboBox):
                    pass
                elif isinstance(widget, QCheckBox) or \
                        isinstance(widget, QRadioButton):
                    pass

        return result


def next_free_name(names, starts_with):
    heads = []
    nums = []
    tails = []
    
    for name in names:
        try:
            (head, num) = name.split('-')
            #(num, tail) = temp.split(')')

            if head.startswith(starts_with):
                heads.append(head)
                nums.append(int(num))
                #tails.append(tail)
        except:
            pass

    return next_free_num(nums)


def next_free_num(nums):
    next_free = 1
    nums.sort()

    if not len(nums):
        next_free = 1

    if len(nums) == 1:
        if nums[0] == 1:
            next_free = 2
        else:
            next_free = 1

    for i in range(1, len(nums)):
        diff = nums[i] - nums[i-1]
        if diff > 1:
            next_free = nums[i-1] + 1
            break

    if len(nums) > 1 and next_free == 1:
        next_free = len(nums) + 1

    return next_free
        
        
        
        



