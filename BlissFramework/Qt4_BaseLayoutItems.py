#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from QtImport import *

from BlissFramework.Utils import PropertyBag

DEFAULT_MARGIN = 2
DEFAULT_SPACING = 2
DEFAULT_ALIGNMENT = "top center"


class _CfgItem:
    """
    Descript. :
    """

    def __init__(self, name, item_type=""):
        """
        Descript. :
        """
        self.name = name
        self.type = item_type
        self.children = []
        self.connections = []

        self.properties = PropertyBag.PropertyBag()
        self.properties.addProperty("alignment", "combo", ("none",
                                    "top center", "top left", "top right",
                                    "bottom center", "bottom left",
                                    "bottom right", "center", "hcenter",
                                    "vcenter", "left", "right"), "none")
        self.signals = {}
        self.slots = {}

    def setProperties(self, properties):
        """Set properties
           Add new properties (if any) and remove odd ones (if any)
        """
        for item_property in properties:
            if hasattr(item_property, "getName"):
                prop_name = item_property.getName()
                if prop_name in self.properties.properties:
                    self.properties.getProperty(prop_name).setValue(\
                         item_property.getUserValue())
                elif item_property.hidden or prop_name.startswith("closable_"):
                    self.properties[prop_name] = item_property
                elif item_property.hidden or prop_name.startswith("newdialog_"):
                    self.properties[prop_name] = item_property
            else:
                if item_property["type"] == "combo":
                    arg1 = item_property["choices"]
                else:
                    arg1 = item_property["value"]
                arg2 = item_property["defaultValue"]
                self.properties.addProperty(propertyName=item_property["name"],
                                            propertyType=item_property["type"],
                                            arg1=arg1,
                                            arg2=arg2,
                                            comment=item_property["comment"],
                                            hidden=item_property["hidden"])

    def __getitem__(self, item):
        """
        Descript. :
        """
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def __setitem__(self, item, value):
        """
        Descript. :
        """
        setattr(self, item, value)

    def __repr__(self):
        """
        Descript. :
        """
        return repr(self.__dict__)

    def rename(self, new_name):
        """
        Descript. :
        """
        self.name = new_name

class ContainerCfg(_CfgItem):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        _CfgItem.__init__(self, *args)
 
        self.properties.addProperty("label", "string", "")
        self.properties.addProperty("icon", "string", "")
        self.properties.addProperty("spacing", "integer", DEFAULT_SPACING)
        self.properties.addProperty("margin", "integer", DEFAULT_MARGIN)
        self.properties.addProperty("color", "color", None)
        self.properties.addProperty("hsizepolicy", "combo",
                                    ("fixed", "expanding", "default"),
                                    "default")
        self.properties.addProperty("vsizepolicy", "combo",
                                    ("fixed", "expanding", "default"),
                                    "default")
        self.properties.addProperty("frameshape", "combo",
                                    ("Box", "Panel", "StyledPanel", "HLine",
                                     "VLine", "default"),
                                    "default")
        self.properties.addProperty("shadowstyle", "combo",
                                    ("plain", "raised", "sunken", "default"),
                                    "default")
        self.properties.addProperty("fixedwidth", "integer", -1)
        self.properties.addProperty("fixedheight", "integer", -1)

    def addChild(self, item):
        """
        Descript. :
        """
        self.children.append(item)
        return ""

    def childPropertyChanged(self, child_name, property_name,
                             old_value, new_value):
        """
        Descript. :
        """
        pass

    def updateSlots(self):
        """
        Descript. :
        """
        pass

    def removeChild(self, child_index):
        """
        Descript. :
        """
        del self.children[child_index]


class WindowCfg(ContainerCfg):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        _CfgItem.__init__(self, *args)

        self.type = "window"
        self.properties.addProperty("caption", "string", "")
        self.properties.addProperty("show", "boolean", True)
        self.properties.addProperty("closeOnExit", "boolean", True)
        self.properties.addProperty("menubar", "boolean", False)
        self.properties.addProperty("statusbar", "boolean", False)
        self.properties.addProperty("menudata", "", {}, hidden=True)
        self.properties.addProperty("expertPwd", "string", "tonic")

        self.signals.update({"isShown": (),
                             "isHidden": (),
                             "enableExpertMode": (),
                             "quit":()})
        self.slots.update({"show": (),
                           "hide": (),
                           "setCaption": (),
                           "exitExpertMode": ()})

 
class TabCfg(ContainerCfg):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        ContainerCfg.__init__(self, *args)

        self.properties.addProperty("fontSize", "integer", 0)
        self.signals.update({"notebookPageChanged": "pageName"})

    def __repr__(self):
        """
        Descript. :
        """
        try:
            widget = self.widget
        except AttributeError:
            r = repr(self.__dict__)
        else:
            delattr(self, 'widget')
            r = repr(self.__dict__)
            self.widget = widget
        return r

    def addChild(self, item):
        """
        Descript. :
        """
        if isinstance(item, ContainerCfg):
            return ContainerCfg.addChild(self, item)
        else:
            return "Tabs can only have container children."

    def childPropertyChanged(self, child_name, property_name,
                             old_value, new_value):
        """
        Descript. :
        """
        if property_name == "label":
            self.updateSlots()
 
    def removeChild(self, child_index):
        """
        Descript. :
        """
        ContainerCfg.removeChild(self, child_index)
        self.updateSlots()

    def updateSlots(self):
        """
        Descript. :
        """
        closable_props = {}
        new_dialog_props = {}
        for prop in self.properties:
            if hasattr(prop, "name"):
                if prop.name.startswith("closable_"):
                    closable_props[prop.name] = prop.getValue()
                elif prop.name.startswith("newdialog_"):
                    closable_props[prop.name] = prop.getValue()
            else:
                if prop["name"].startswith("closable_"):
                    closable_props[prop["name"]] = prop["value"]
                if prop["name"].startswith("newdialog_"):
                    closable_props[prop["name"]] = prop["value"]

        for prop_name in closable_props.keys():
            self.properties.delProperty(prop_name)
        for prop_name in new_dialog_props.keys():
            self.properties.delProperty(prop_name)

        self.slots = {}
        for child in self.children:
            if "label" in child["properties"].properties:
                child_lbl = child["properties"]["label"]
                child_lbl = child_lbl.replace(" ", "_")
                self.properties.addProperty("closable_%s" % child_lbl,
                     "boolean", closable_props.get("closable_%s" % child_lbl,
                     False))
                self.properties.addProperty("newdialog_%s" % child_lbl,
                     "boolean", closable_props.get("newdialog_%s" % child_lbl,
                     False))
                slot_name = "showPage_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()
                slot_name = "hidePage_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()
                slot_name = "enablePage_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()
                slot_name = "enableTab_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()
                slot_name = "incTabCount_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()
                slot_name = "resetTabCount_%s" % child_lbl
                self.slots[slot_name.replace(" ", "_")] = ()

    def notebook_page_changed(self, new_tab_label):
        """
        Descript. :
        """
        new_tab_label = new_tab_label.replace(" ", "_")
        if self.properties.getProperty("closable_%s" % new_tab_label).getValue():
            self.widget.close_tab_button.show()
        else:
            self.widget.close_tab_button.hide()
        if self.properties.getProperty("newdialog_%s" % new_tab_label).getValue():
            self.widget.open_in_dialog_button.show()
        else:
            self.widget.open_in_dialog_button.hide()


class SplitterCfg(ContainerCfg):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        ContainerCfg.__init__(self, *args)

        self.properties.addProperty("sizes", "string", "[]",
                                    hidden=True)
        for key in [Qt.Key_F9,
                    Qt.Key_F10,
                    Qt.Key_F11,
                    Qt.Key_F12]:
            self.properties.addProperty("sizes_%d" % key,
                                        "string",
                                        "[]",
                                        hidden=True)


class SpacerCfg(_CfgItem):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("fixed_size", "boolean", False)
        self.properties.addProperty("size", "integer", 100)
 

class LabelCfg(_CfgItem):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("text", "string", "")
        self.properties.addProperty("fontSize", "integer", 0)


class IconCfg(_CfgItem):
    """
    Descript. :
    """

    def __init__(self, *args):
        """
        Descript. :
        """
        _CfgItem.__init__(self, *args)

        self.properties.addProperty("filename", "file", "")


class BrickCfg(_CfgItem):
    """
    Descript. :
    """

    def __init__(self, name, brick_type, brick=None):
        """
        Descript. :
        """
        _CfgItem.__init__(self, name, brick_type)

        self.name = name
        self.type = brick_type

        self.brick = brick

        # bricks have their own thing for signals and slots
        del self.signals
        del self.slots

        # bricks have their own thing for properties
        if brick is not None:
            self.setProperties(brick.property_bag)
 
    def setProperties(self, properties):
        """
        Descript. :
        """
        self.brick.setPersistentPropertyBag(properties)
        self.properties = self.brick.property_bag

    def rename(self, new_name):
        """
        Descript. :
        """
        _CfgItem.rename(self, new_name)

        if self.brick is not None:
            self.brick.setObjectName(new_name)
