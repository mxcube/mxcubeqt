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

"""Module contains classes defining graphical objects in MXCuBE"""

from gui.utils import PropertyBag, QtImport

DEFAULT_MARGIN = 2
DEFAULT_SPACING = 2
DEFAULT_ALIGNMENT = "top center"


__license__ = "LGPLv3+"


class _CfgItem(object):
    """Configuration item base class"""

    def __init__(self, name=None, item_type=""):
        self.name = name
        self.type = item_type
        self.children = []
        self.connections = []

        self.signals = {}
        self.slots = {}

        self.properties = PropertyBag.PropertyBag()
        self.properties.add_property(
            "alignment",
            "combo",
            (
                "none",
                "top center",
                "top left",
                "top right",
                "bottom center",
                "bottom left",
                "bottom right",
                "center",
                "hcenter",
                "vcenter",
                "left",
                "right",
            ),
            "none",
        )

    def set_properties(self, properties):
        """Set properties
           Add new properties (if any) and remove odd ones (if any)
        """
        for item_property in properties:
            if hasattr(item_property, "get_name"):
                prop_name = item_property.get_name()
                if prop_name in self.properties.properties:
                    self.properties.get_property(prop_name).set_value(
                        item_property.get_user_value()
                    )
                elif item_property.hidden or prop_name.startswith("closable_"):
                    self.properties[prop_name] = item_property
                elif item_property.hidden or prop_name.startswith("newdialog_"):
                    self.properties[prop_name] = item_property
            else:
                if item_property["type"] == "combo":
                    arg1 = item_property["choices"]
                else:
                    arg1 = item_property["value"]
                arg2 = item_property["default_value"]
                self.properties.add_property(
                    property_name=item_property["name"],
                    property_type=item_property["type"],
                    arg1=arg1,
                    arg2=arg2,
                    comment=item_property["comment"],
                    hidden=item_property["hidden"],
                )

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def __repr__(self):
        return repr(self.__dict__)

    def rename(self, new_name):
        self.name = new_name


class ContainerCfg(_CfgItem):
    """Container configuration"""

    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.add_property("label", "string", "")
        self.properties.add_property("icon", "string", "")
        self.properties.add_property("spacing", "integer", DEFAULT_SPACING)
        self.properties.add_property("margin", "integer", DEFAULT_MARGIN)
        self.properties.add_property("color", "color", None)
        self.properties.add_property(
            "hsizepolicy", "combo", ("fixed", "expanding", "default"), "default"
        )
        self.properties.add_property(
            "vsizepolicy", "combo", ("fixed", "expanding", "default"), "default"
        )
        self.properties.add_property(
            "frameshape",
            "combo",
            ("Box", "Panel", "StyledPanel", "HLine", "VLine", "default"),
            "default",
        )
        self.properties.add_property(
            "shadowstyle", "combo", ("plain", "raised", "sunken", "default"), "default"
        )
        self.properties.add_property("fixedwidth", "integer", -1)
        self.properties.add_property("fixedheight", "integer", -1)

    def add_child(self, item):
        self.children.append(item)
        return ""

    def child_property_changed(self, child_name, property_name, old_value, new_value):
        pass

    def update_slots(self):
        pass

    def remove_child(self, child_index):
        del self.children[child_index]


class WindowCfg(ContainerCfg):
    """Window configuration item. Contains extra properties to customize window"""

    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)

        self.type = "window"
        self.properties.add_property("caption", "string", "")
        self.properties.add_property("show", "boolean", True)
        self.properties.add_property("closeOnExit", "boolean", True)
        self.properties.add_property("keepOpen", "boolean", False)
        self.properties.add_property("menubar", "boolean", False)
        self.properties.add_property("statusbar", "boolean", False)
        self.properties.add_property("menudata", "", {}, hidden=True)
        self.properties.add_property("expertPwd", "string", "tonic")
        self.properties.add_property("fontSize", "integer", 12)

        self.signals.update(
            {"isShown": (), "isHidden": (), "enableExpertMode": (), "quit": ()}
        )
        self.slots.update(
            {"show": (), "hide": (), "setCaption": (), "exitExpertMode": ()}
        )


class TabCfg(ContainerCfg):
    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)
        self.widget = None

        self.properties.add_property("fontSize", "integer", 0)
        self.signals.update({"notebookPageChanged": "pageName"})

    def __repr__(self):
        if hasattr(self, "widget"):
            widget = getattr(self, "widget")
        else:  
            r = repr(self.__dict__)

        delattr(self, "widget")
        r = repr(self.__dict__)
        self.widget = widget
        return r

    def add_child(self, item):
        if isinstance(item, ContainerCfg):
            return ContainerCfg.add_child(self, item)
        else:
            return "Tabs can only have container children."

    def child_property_changed(self, child_name, property_name, old_value, new_value):
        if property_name == "label":
            self.update_slots()

    def remove_child(self, child_index):
        ContainerCfg.remove_child(self, child_index)
        self.update_slots()

    def update_slots(self):
        closable_props = {}
        new_dialog_props = {}
        for prop in self.properties:
            if hasattr(prop, "name"):
                if prop.name.startswith("closable_"):
                    closable_props[prop.name] = prop.get_value()
                elif prop.name.startswith("newdialog_"):
                    closable_props[prop.name] = prop.get_value()
            else:
                if prop["name"].startswith("closable_"):
                    closable_props[prop["name"]] = prop["value"]
                if prop["name"].startswith("newdialog_"):
                    closable_props[prop["name"]] = prop["value"]

        for prop_name in closable_props.keys():
            self.properties.del_property(prop_name)
        for prop_name in new_dialog_props.keys():
            self.properties.del_property(prop_name)

        self.slots = {}
        for child in self.children:
            if "label" in child["properties"].properties:
                child_lbl = child["properties"]["label"]
                child_lbl = child_lbl.replace(" ", "_")
                self.properties.add_property(
                    "closable_%s" % child_lbl,
                    "boolean",
                    closable_props.get("closable_%s" % child_lbl, False),
                )
                self.properties.add_property(
                    "newdialog_%s" % child_lbl,
                    "boolean",
                    closable_props.get("newdialog_%s" % child_lbl, False),
                )
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
        new_tab_label = new_tab_label.replace(" ", "_")
        if self.properties.get_property("closable_%s" % new_tab_label).get_value():
            self.widget.close_tab_button.show()
        else:
            self.widget.close_tab_button.hide()
        if self.properties.get_property("newdialog_%s" % new_tab_label).get_value():
            self.widget.open_in_dialog_button.show()
        else:
            self.widget.open_in_dialog_button.hide()


class SplitterCfg(ContainerCfg):
    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)

        self.properties.add_property("sizes", "string", "[]", hidden=True)
        for key in [
            QtImport.Qt.Key_F9,
            QtImport.Qt.Key_F10,
            QtImport.Qt.Key_F11,
            QtImport.Qt.Key_F12,
        ]:
            self.properties.add_property("sizes_%d" % key, "string", "[]", hidden=True)


class GroupBoxCfg(ContainerCfg):
    def __init__(self, *args):
        ContainerCfg.__init__(self, *args)

        self.properties.add_property("checkable", "boolean", False)
        self.properties.add_property("checked", "boolean", False)


class SpacerCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.add_property("fixed_size", "boolean", False)
        self.properties.add_property("size", "integer", 100)


class LabelCfg(_CfgItem):
    def __init__(self, *args):

        _CfgItem.__init__(self, *args)

        self.properties.add_property("text", "string", "")
        self.properties.add_property("fontSize", "integer", 0)


class IconCfg(_CfgItem):
    def __init__(self, *args):
        _CfgItem.__init__(self, *args)

        self.properties.add_property("filename", "file", "")


class BrickCfg(_CfgItem):
    def __init__(self, name, brick_type, brick=None):

        _CfgItem.__init__(self, name, brick_type)

        self.name = name
        self.type = brick_type

        self.brick = brick

        # bricks have their own thing for signals and slots
        del self.signals
        del self.slots

        # bricks have their own thing for properties
        if brick is not None:
            self.set_properties(brick.property_bag)

    def set_properties(self, properties):
        self.brick.set_persistent_property_bag(properties)
        self.properties = self.brick.property_bag

    def rename(self, new_name):
        _CfgItem.rename(self, new_name)

        if self.brick is not None:
            self.brick.setObjectName(new_name)
