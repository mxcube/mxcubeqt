import qt
import pprint
import types
from BlissFramework.Utils import PropertyBag


DEFAULT_MARGIN = 5
DEFAULT_SPACING = 5
DEFAULT_ALIGNMENT = "top center"


class _CfgItem:
    def __init__(self, name, item_type=""):
        self.name = name
        self.type = item_type
        self.children = []
        self.connections = []

        self.properties = PropertyBag.PropertyBag()
        self.properties.addProperty("alignment", "combo", ("none", "top center", "top left", "top right", "bottom center", "bottom left", "bottom right", "center", "hcenter", "vcenter", "left", "right"), "none")

        self.signals = {}
        self.slots = {}


    def setProperties(self, properties):
        """Set properties

        Add new properties (if any) and remove odd ones (if any)
        """
        for property in properties:
            #
            # persistent properties are set (took code from BlissWidget)
            #
            prop_name = property.getName()
            if prop_name in self.properties.properties:
                #print prop_name, property.getUserValue()
                self.properties.getProperty(prop_name).setValue(property.getUserValue())
            elif property.hidden:
                self.properties[property.getName()] = property
                
        
    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError, item


    def __setitem__(self, item, value):
        setattr(self, item, value)
    

    def __repr__(self):
        return repr(self.__dict__)
        #return pprint.pformat(self.__dict__)


    def rename(self, new_name):
        self.name = new_name
        

class ContainerCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)
        
        self.properties.addProperty("label", "string", "")
        self.properties.addProperty("icon", "string", "")
        self.properties.addProperty("spacing", "integer", DEFAULT_SPACING)
        self.properties.addProperty("margin", "integer", DEFAULT_MARGIN)
        self.properties.addProperty("color", "color", None)
        self.properties.addProperty("hsizepolicy", "combo", ("fixed", "expanding", "default"), "default")
        self.properties.addProperty("vsizepolicy", "combo", ("fixed", "expanding", "default"), "default")
        self.properties.addProperty("frameshape", "combo", ("box", "panel", "default"), "default")
        self.properties.addProperty("shadowstyle", "combo", ("plain", "raised", "sunken", "default"), "default")

    def addChild(self, item):
        self.children.append(item)
        return ""
    

    def childPropertyChanged(self, child_name, property, old_value, new_value):
        pass


    def removeChild(self, child_index):
        del self.children[child_index]


class MenuEditor(qt.QDialog):
    def __init__(self, parent, window_name):
        qt.QDialog.__init__(self, parent)

        self.window_name = window_name
        self.setModal(False)
        self.setCaption("Menu editor - %s" % window_name)

        qt.QVBoxLayout(self)
        self.layout().addWidget(qt.QLabel("<h2>feature to be implemented, sorry for the inconvenience</h2>", self))
        

    def __repr__(self):
        return "'<Menu Editor - %s>'" % self.window_name
    


class WindowCfg(ContainerCfg):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.type = "window"
        self._menuEditor = None
        
        self.properties.addProperty("caption", "string", "")
        self.properties.addProperty("show", "boolean", True)
        for suffix in ['','_%d' % qt.Qt.Key_F9,'_%d' % qt.Qt.Key_F10,'_%d' % qt.Qt.Key_F11,'_%d' % qt.Qt.Key_F12] :
            self.properties.addProperty("x%s" % suffix, "integer", 0) #, hidden=True)
            self.properties.addProperty("y%s" % suffix, "integer", 0) #, hidden=True)
            self.properties.addProperty("w%s" % suffix, "integer", 0) #, hidden=True)
            self.properties.addProperty("h%s" % suffix, "integer", 0) #, hidden=True)
        self.properties.addProperty("menubar", "boolean", False)
        self.properties.addProperty("statusbar", "boolean", False)
        self.properties.addProperty("menudata", "", {}, hidden=True)
        self.properties.addProperty("expertPwd", "string", "tonic")

        self.signals.update({ "isShown": (), "isHidden": (), "enableExpertMode": (), "quit":() })
        self.slots.update({ "show": (), "hide": (), "setCaption": (), "exitExpertMode": () })

    """
    def addChild(self, item):
        if len(self.children) > 0:
            # allow only one child
            return "Windows can only have one container child."

        if isinstance(item, ContainerCfg):
            return ContainerCfg.addChild(self, item)
        else:
            return "Windows can only have one container child."
    """
    def menuEditor(self):
        if not hasattr(self, "_menuEditor"):
            # backward compatibility!
            self._menuEditor=None
            
        if self._menuEditor is None or type(self._menuEditor)==types.StringType:
            self._menuEditor = MenuEditor(None, self.name)
            
        return self._menuEditor
    
        
class TabCfg(ContainerCfg):
    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)

        self.properties.addProperty("fontSize", "integer", 0)  
        self.signals.update({ "notebookPageChanged": ("pageName", ) })


    def __repr__(self):
        try:
            widget = self.widget
        except AttributeError:
            r = repr(self.__dict__)
        else:
            delattr(self,'widget')
            r = repr(self.__dict__)
            self.widget = widget
        """
        widget = self.widget
        delattr(self,'widget')
        r = repr(self.__dict__)
        self.widget = widget
        """
        return r


    def addChild(self, item):
        if isinstance(item, ContainerCfg):
            return ContainerCfg.addChild(self, item)
        else:
            return "Tabs can only have container children."
        

    def childPropertyChanged(self, child_name, property, old_value, new_value):
        if property == "label":
            self.updateSlots()
            

    def removeChild(self, child_index):
        ContainerCfg.removeChild(self, child_index)
        
        self.updateSlots()


    def updateSlots(self):
        self.slots = {}
        for child in self.children:
            if "label" in child["properties"].properties:
                slot_name="showPage_%s" % child["properties"]["label"]
                self.slots[slot_name.replace(" ", "_")]=()
                slot_name="enablePage_%s" % child["properties"]["label"]
                self.slots[slot_name.replace(" ", "_")]=()
                slot_name="enableTab_%s" % child["properties"]["label"]
                self.slots[slot_name.replace(" ", "_")]=()
                slot_name="incTabCount_%s" % child["properties"]["label"]
                self.slots[slot_name.replace(" ", "_")]=()
                slot_name="resetTabCount_%s" % child["properties"]["label"]
                self.slots[slot_name.replace(" ", "_")]=()


class SplitterCfg(ContainerCfg):
    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)

        self.properties.addProperty("sizes", "string", "[]", hidden=True)
        for key in [qt.Qt.Key_F9,qt.Qt.Key_F10,qt.Qt.Key_F11,qt.Qt.Key_F12] :
            self.properties.addProperty("sizes_%d" % key,"string","[]",hidden = True)


class SpacerCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("fixed_size", "boolean", False)
        self.properties.addProperty("size", "integer", 100)
        

class LabelCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("text", "string", "")
        self.properties.addProperty("fontSize", "integer", 0)


class IconCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("filename", "file", "")


class BrickCfg(_CfgItem):
    def __init__(self, name, brick_type, brick=None):
        _CfgItem.__init__(self, name, brick_type)

        self.brick = brick

        # bricks have their own thing for signals and slots
        del self.signals
        del self.slots

        # bricks have their own thing for properties
        if brick is not None:
            self.setProperties(brick.propertyBag)

        
    def setProperties(self, properties):
        self.brick.setPersistentPropertyBag(properties)

        self.properties = self.brick.propertyBag


    def rename(self, new_name):
        _CfgItem.rename(self, new_name)

        if self.brick is not None:
            self.brick.setName(new_name)
