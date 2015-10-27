import cPickle

class Property:
    def __init__(self, propertyName, defaultValue = None):
        self.name = propertyName

        self.type = 'undefined'
        self.value = None
        self.oldValue = None
        self.hidden = False
        self._editor = None

        if defaultValue is None:
            self.defaultValue = None
        else:
            self.setDefaultValue(defaultValue, True)
        

    def __getstate__(self):
        dict = self.__dict__.copy() # copy the dict since we change it
        if hasattr(self, '_editor'):
            del dict['_editor']     # remove ref. to editor
        return dict
     

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        
        if not 'hidden' in dict:
            self.hidden = False
            
        self._editor = None
  

    def getName(self):
        return self.name


    def getType(self):
        return self.type

    
    def getUserValue(self):
        return self.getValue()
        

    def getValue(self):
        return self.value


    def getDefaultValue(self):
        return self.defaultValue


    def setValue(self, propertyValue):
        self.value = propertyValue


    def setDefaultValue(self, value, setAsValue = False):
        savedValue = self.value
        savedOldValue = self.oldValue
        
        try:
            self.setValue(value)
        except ValueError:
            raise ValueError, "cannot set default value to %s : incompatible types." % repr(value)

        self.defaultValue = self.value
        
        if not setAsValue: 
            self.value = savedValue
            self.oldValue = savedOldValue


class StringProperty(Property):
    def __init__(self, propertyName, defaultValue = ''):
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'string'
      

    def setValue(self, propertyValue):
        self.oldValue = self.value
        self.value = str(propertyValue)
        

class IntegerProperty(Property):
    def __init__(self, propertyName, defaultValue = None):
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'integer'


    def setValue(self, propertyValue):
        try:
            newValue = int(propertyValue)
        except ValueError:
            raise ValueError, "%s is not a valid integer value." % repr(propertyValue)

        self.oldValue = self.value
        self.value = newValue


class BooleanProperty(Property):
    def __init__(self, propertyName, defaultValue = False):
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'boolean'


    def setValue(self, propertyValue):
        self.oldValue = self.value
 
        if propertyValue:
            self.value = 1
        else:
            self.value = 0

        
class ComboProperty(Property):
    def __init__(self, propertyName, choices = [], defaultValue = None):
        self.setChoices(choices)

        Property.__init__(self, propertyName, defaultValue)
        self.type = 'combo'

    def addChoice(self, choice):
        self.choices.append(str(choice))

        
    def setChoices(self, choices):
        try:
            self.choices = list(choices)
        except:
            raise ValueError, "%s cannot be converted into a list" % repr(choices)


    def getChoices(self):
        return self.choices


    def setValue(self, propertyValue):
        strValue = str(propertyValue)
        
        for choice in self.choices:
            if strValue == choice:
                self.oldValue = self.value
                self.value = strValue
                return
        raise ValueError, "%s is not a valid choice for combo" % repr(str(propertyValue))


class FloatProperty(Property):
    def __init__(self, propertyName, defaultValue = None):
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'float'

        
    def setValue(self, propertyValue):
        try:
            newValue = float(propertyValue)
        except ValueError:
            raise ValueError, "%s is not a valid float value" % repr(propertyValue)
    
        self.oldValue = self.value
        self.value = newValue


class FileProperty(Property):
    def __init__(self, propertyName, filter = 'All (*.*)', defaultValue = None):
        Property.__init__(self, propertyName, defaultValue or '')

        self.type = 'file'
        self.filter = filter
        

    def setValue(self, propertyValue):
        import os.path
        
        newValue = os.path.abspath(str(propertyValue))
        
        self.oldValue = self.value
        self.value = newValue


    def getFilter(self):
        return self.filter


class ColorProperty(Property):
    def __init__(self, propertyName, defaultValue = None):
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'color'


    def setValue(self, propertyValue):
        self.oldValue = self.value
        self.value = propertyValue

       
class FormatStringProperty(Property):
    def __init__(self, propertyName, defaultValue = None):
        self.formatString = None
        self.formatStringLength = 0
        
        Property.__init__(self, propertyName, defaultValue)

        self.type = 'formatString'


    def setValue(self, format):
        self.oldValue = self.value
        self.value = str(format)

        if format.startswith('+'):
            prefix = '+'
            format = format[1:]
        elif format.startswith(' '):
            prefix = ''
            format = format[1:]
        else:
            prefix = ''
            
        parts = format.split('.')

        if len(parts) == 2:
            self.formatString = '%' + prefix + str(len(parts[0])) + '.' + str(len(parts[1])) + 'f'
        elif len(parts) == 1:
            self.formatString = '%' + prefix + str(len(parts[0])) + '.0f'
        else:
            raise ValueError

        self.formatStringLength = sum(map(len, parts))+1
        

    def getUserValue(self):
        return self.value


    def getValue(self):
        return self.formatString


    def getFormatLength(self):
        return self.formatStringLength
    

class PropertyBag:
    def __init__(self):
        self.properties = {}
    
        
    def addProperty(self, propertyName, propertyType, arg1 = None, arg2 = None, hidden = False):
        if propertyType == 'string':
            if arg1 is None:
                arg1 = ''
            newProperty = StringProperty(propertyName, arg1)
        elif propertyType == 'integer':
            newProperty = IntegerProperty(propertyName, arg1)
        elif propertyType == 'combo':
            if list(arg1):
                newProperty = ComboProperty(propertyName, arg1, arg2)
            else:
                newProperty = ComboProperty(propertyName, defaultValue = arg1)
        elif propertyType == 'boolean':
            newProperty = BooleanProperty(propertyName, arg1)
        elif propertyType == 'float':
            newProperty = FloatProperty(propertyName, arg1)
        elif propertyType == 'file':
            newProperty = FileProperty(propertyName, arg1, arg2)
        elif propertyType == 'color':
            newProperty = ColorProperty(propertyName, defaultValue=arg1)
        elif propertyType == 'formatString':
            newProperty = FormatStringProperty(propertyName, defaultValue = arg1)
        else:
            newProperty = Property(propertyName, arg1)

        newProperty.hidden = hidden
        self.properties[propertyName] = newProperty

        self.updateEditor()


    def updateEditor(self):
        for propname, prop in self.properties.iteritems():
            if prop._editor is not None:
                # the properties are being edited,
                # refresh property editor
                editor = prop._editor()
              
                if editor is not None:
                    editor.setPropertyBag(self)
                break
                    

    def delProperty(self, propertyName):
        ed = None
        for propname, prop in self.properties.iteritems():
            ed = prop._editor
            break

        try:
            del self.properties[propertyName]
        except KeyError:
            pass
        else:
            try:
                editor = ed()
                if editor is not None:
                    editor.setPropertyBag(self)
            except TypeError:
                pass
            
        
    def getProperty(self, propertyName):
        try:
            return self.properties[propertyName]
        except KeyError:
            return Property('')
            

    def hideProperty(self, propertyName):
        prop = self.properties.get(propertyName, None)
        if prop is not None and not prop.hidden:
            prop.hidden=True
            if prop._editor is not None:
                editor = prop._editor()
                if editor is not None:
                    editor.setPropertyBag(self)


    def showProperty(self, propertyName):
        prop = self.properties.get(propertyName, None)
        if prop is not None and prop.hidden:
            prop.hidden=False
            if prop._editor is not None:
                editor = prop._editor()
                if editor is not None:
                    editor.setPropertyBag(self)


    def __repr__(self):
        return repr(cPickle.dumps(self))


    def __str__(self):
        return "<PropertyBag instance>"
        

    def __iter__(self):
        keys = self.properties.keys()
        keys.sort()

        for key in keys:
            yield self.properties[key]


    def __len__(self):
        return len(self.properties)


    def __getitem__(self, propertyKey):
        item = self.properties.get(propertyKey)
        if item is not None: 
            return self.properties[propertyKey].getValue()
                

    def __setitem__(self, propertyName, property):
        self.properties[propertyName] = property
            
    
    def isEmpty(self):
        return len(self.properties) == 0


    def hasProperty(self, name):
        return name in self.properties
    





















