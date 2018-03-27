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

"""Configuration
"""

import json
import yaml
import logging
import imp
import pprint
import pickle
from BlissFramework.Utils import PropertyBag
from BlissFramework import Qt4_BaseLayoutItems
from BlissFramework.Qt4_BaseComponents import NullBrick


def loadModule(brick_name):
    """Loads module"""
    fp = None
    try:
        fp, path_name, description = imp.find_module(brick_name)
        mod = imp.load_module(brick_name, fp, path_name, description)
    except:
        if fp:
            fp.close()
        logging.getLogger().exception('Cannot import module %s', brick_name)
        return None
    else:
        return mod


def load_brick(brick_type, brick_name):
    """Loads brick"""
    module = loadModule(brick_type)

    if module is not None:
        try:
            #classObj = getattr(module, brick_type)
            class_obj = getattr(module, brick_type)
        except AttributeError:
            logging.getLogger().error(\
                  "Cannot load brick %s : " % brick_name + \
                  "cannot found class %s in module" % brick_type)
            return NullBrick(None, brick_name)
        else:
            try:
                new_instance = class_obj(None, brick_name)
            except:
                logging.getLogger().exception(\
                   "Cannot load brick %s : initialization failed", brick_name)
                return NullBrick(None, brick_name)
            else:
                new_instance._BlissWidget__stop()
                return new_instance
    else:
        logging.getLogger().error("Cannot load brick %s : " % brick_name + \
                                  "module could not be loaded.")
        return NullBrick(None, brick_name)


class Configuration:
    """Configuration of a BlissWidget"""
    classes = {"hbox": Qt4_BaseLayoutItems.ContainerCfg,
               "vbox": Qt4_BaseLayoutItems.ContainerCfg,
               "vgroupbox": Qt4_BaseLayoutItems.ContainerCfg,
               "hgroupbox": Qt4_BaseLayoutItems.ContainerCfg,
               "hspacer": Qt4_BaseLayoutItems.SpacerCfg,
               "vspacer": Qt4_BaseLayoutItems.SpacerCfg,
               "label": Qt4_BaseLayoutItems.LabelCfg,
               "icon": Qt4_BaseLayoutItems.IconCfg,
               "tab": Qt4_BaseLayoutItems.TabCfg,
               "hsplitter": Qt4_BaseLayoutItems.SplitterCfg,
               "vsplitter": Qt4_BaseLayoutItems.SplitterCfg}


    def __init__(self, config=None, load_from_dict=None):
        """__init__ method"""
        self.has_changed = False

        if config is None:
            self.windows_list = []
            self.windows = {}
            self.bricks = {}
            self.items = {}
        else:
            self.load(config, load_from_dict)

    def find_container(self, container_name):
        """Returns container

        :param container_name: name of container
        :type container_name: str
        """
        try:
            parent = self.windows[container_name]
        except KeyError:
            try:
                parent = self.items[container_name]
            except KeyError:
                return
        return parent

    def add_window(self):
        """Adds window to the list of windows

        :returns: added Window
        """
        i = sum([x.startswith("window") and 1 or 0 for x in self.windows])
        window_name = "window%d" % i
        while window_name in self.windows:
            i += 1
            window_name = "window%d" % i

        self.windows_list.append(Qt4_BaseLayoutItems.WindowCfg(window_name))
        self.windows[window_name] = self.windows_list[-1]
        self.has_changed = True

        return self.windows_list[-1]

    def add_item(self, item_type, parent):
        """Adds item to the gui

        :param item_type: config class of the item
        :type item_type: class
        :param parent: parent
        :type parent: widget
        """
        if parent is None:
            logging.getLogger().error("Invalid parent container")
            return

        if item_type in Configuration.classes:
            i = sum([x.startswith(item_type) and 1 or 0 for x in self.items])
            item_name = "%s%d" % (item_type, i)
            while item_name in self.items:
                i += 1
                item_name = "%s%d" % (item_type, i)

            cfg_class = Configuration.classes[item_type]
            error = parent.addChild(cfg_class(item_name, item_type))
            if len(error) == 0:
                self.items[item_name] = parent["children"][-1]
                self.has_changed = True
                return parent["children"][-1]
            else:
                return error
        else:
            logging.getLogger().error(\
                "Item of this type (%s) does not exist.", item_type)

    def add_brick(self, brick_type, parent):
        """Adds brick to the gui

        :param brick_type: brick type
        :type brick_type: class
        :param parent: parent
        :type parent: widget
        """
        i = sum([x.startswith(brick_type) and 1 or 0 for x in self.bricks])
        brick_name = "%s%d" % (brick_type, i)
        while brick_name in self.bricks:
            i += 1
            brick_name = "%s%d" % (brick_type, i)

        brick = load_brick(brick_type, brick_name)
        error = parent.addChild(Qt4_BaseLayoutItems.BrickCfg(brick_name,
                                                             brick_type,
                                                             brick))

        if len(error) == 0:
            self.bricks[brick_name] = parent["children"][-1]
            self.has_changed = True
            return parent["children"][-1]
        else:
            brick.close(True)
            return error

    def find_parent(self, item_name, nodeset=[], parent=None):
        """Finds parent of an item
        """
        iter_index = 0
        for item in nodeset:
            if item["name"] == item_name:
                return (parent, iter_index)
            else:
                parent_item, item_index = self.find_parent(\
                    item_name, nodeset=item["children"], parent=item)
                if parent_item is not None:
                    return (parent_item, item_index)
            iter_index += 1

        return (None, -1)

    def find_all_children(self, parent_item):
        """Returns a list of all children
        """
        return parent_item["children"] + sum([self.find_all_children(child) for child in parent_item["children"]], [])

    def find_item(self, item_name, nodeset=None):
        """
        Descript. :
        """
        if nodeset is None:
            nodeset = self.windows_list

        for item in nodeset:
            if item["name"] == item_name:
                return item
            else:
                _item = self.find_item(item_name, item["children"])

                if _item is not None:
                    return _item

    def find_all_children_by_type(self, item_type, parent_item):
        """Find all children with w type
           Valid types are: brick, container, splitter...
        """
        try:
            t = getattr(Qt4_BaseLayoutItems, "%sCfg" % str(item_type).title())
        except AttributeError:
            return {}

        def find_children_by_type(item_type, item):
            children = {}

            for child in item["children"]:
                if isinstance(child, t):
                    children[child["name"]] = child
                children.update(find_children_by_type(item_type, child))

            return children

        return find_children_by_type(item_type, parent_item)

    def rename(self, parent_item_name, child_pos, new_item_name):
        """Renames item"""
        parent_item = self.find_item(parent_item_name)

        if parent_item is None:
            item = self.windows_list[child_pos]
        else:
            item = parent_item["children"][child_pos]

        old_item_name = item["name"]

        if new_item_name == old_item_name:
            return None

        if self.find_item(new_item_name):
            # new name conflicts with existing item !
            return old_item_name
        else:
            if isinstance(item, dict):
                item["name"] = new_item_name
            else:
                item.rename(new_item_name)

            recv = "receiver"
            if old_item_name in self.items:
                del self.items[old_item_name]
                self.items[new_item_name] = item
            elif old_item_name in self.bricks:
                del self.bricks[old_item_name]
                self.bricks[new_item_name] = item
            elif old_item_name in self.windows:
                del self.windows[old_item_name]
                self.windows[new_item_name] = item
                recv = "receiverWindow"

            all_items = {}
            all_items.update(self.windows)
            all_items.update(self.bricks)
            all_items.update(self.items)

            for item in all_items.values():
                if isinstance(item, dict):
                    connections = item["connections"]
                else:
                    connections = item.connections
                for connection in connections:
                    if connection[recv] == old_item_name:
                        logging.getLogger().debug(\
                           "Receiver item %s in "  % old_item_name + \
                           "%s has been changed to " % item.name + \
                           "%s" % new_item_name)
                        connection[recv] = new_item_name

            self.has_changed = True

    def remove(self, item_name):
        """Removes item"""

        parent, index = self.find_parent(item_name, self.windows_list)

        if parent is not None:
            try:
                del self.items[item_name]
            except KeyError:
                del self.bricks[item_name]

            parent.removeChild(index)
            self.has_changed = True

            return True
        else:
            try:
                window = self.windows[item_name]
            except KeyError:
                return False
            else:
                self.windows_list.remove(window)
                del self.windows[item_name]
                self.has_changed = True
                return True

    def move_up(self, item_name):
        """Moves an item up in the hierarchy

        :returns: The name of the new item's parent
        """
        parent, index = self.find_parent(item_name, self.windows_list)

        if parent is None:
            return None

        item = parent["children"][index]
        assert item["name"] == item_name
        if index == 0:
            # cannot move
            return None
        else:
            del parent["children"][index]
            parent["children"].insert(index - 1, item)
            self.has_changed = True

            return parent["name"]

    def move_down(self, item_name):
        """Move an item down in the hierarchy
        :returns: the name of its new parent item
        """
        parent, index = self.find_parent(item_name, self.windows_list)
        if parent is None:
            return None

        item = parent["children"][index]
        assert item["name"] == item_name

        try:
            next_item = parent["children"][index + 1]
        except IndexError:
            return None
        else:
            del parent["children"][index]
            parent["children"].insert(index + 1, item)
            self.has_changed = True

            return parent["name"]

    def move_item(self, source_item_name, target_item_name):
        """Move an item to another place in the hierarchy
           Mainly useful for drag'n'drop on the tree.
        """
        if source_item_name == target_item_name:
            return False

        source_parent_cfg, source_item_pos = \
            self.find_parent(source_item_name, self.windows_list)
        target_parent_cfg, target_item_pos = \
            self.find_parent(target_item_name, self.windows_list)

        if source_parent_cfg is None:
            # cannot drag an entire window
            return False
        else:
            source_item_cfg = source_parent_cfg["children"][source_item_pos]

        if target_parent_cfg is None:
            # we are dropping on a window
            target_item_cfg = self.windows[target_item_name]

            if not self.is_container(source_item_cfg):
                return False
        else:
            target_item_cfg = target_parent_cfg["children"][target_item_pos]

        if target_item_cfg in self.find_all_children(source_item_cfg):
            # cannot move a parent in a child
            return False

        del source_parent_cfg["children"][source_item_pos]

        if self.is_container(target_item_cfg):
            target_item_cfg["children"].insert(0, source_item_cfg)
        else:
            target_parent_cfg["children"].insert(target_item_pos,
                                                 source_item_cfg)

        self.has_changed = True

        return True

    def dump(self):
        """Prints config"""
        pprint.pprint(self.windows_list)

    def dump_tree(self):
        """Prints window list"""
        wl = []
        for window_cfg in self.windows_list:
            window_cfg_dict = {"type": "window",
                               "name": window_cfg["name"],
                               "properties": [],
                               "signals": window_cfg.signals,
                               "connections": window_cfg.connections}
            for prop in window_cfg.properties:
                window_cfg_dict["properties"].append(prop.__getstate__())

            children = []

            def add_children(item_cfg):
                children = []

                for child in item_cfg["children"]:
                    child_prop_dict = {"name": child["name"],
                                       "type": child.type,
                                       "properties": [],
                                       "children": [],
                                       "connections": child.connections}
                    for prop in child.properties:
                        child_prop_dict["properties"].append(prop.__getstate__())
                    if hasattr(child, "brick"):
                        child_prop_dict["brick"] = {"name": str(child.brick.objectName())}
                        child_prop_dict["brick"]["class"] = child.brick.__class__.__name__
                        #child_prop_dict["brick"]["signals"] = child.brick._Connectable__signal
                        #child_prop_dict["brick"]["slots"] = child.brick._Connectable__slot
                    #else:
                    #    child["signals"] = child.signals
                    #    child["slots"] = child.slots

                    child_prop_dict["children"] = add_children(child)
                    children.append(child_prop_dict)

                return children

            window_cfg_dict["children"] = add_children(window_cfg)

            wl.append(window_cfg_dict)
        return wl
        #pprint.pprint(wl)

    def save(self, filename):
        """Saves config"""

        if filename.endswith(".json"):
            json_dict = self.dump_tree()
            with open(filename, 'w') as outfile:
                  json.dump(json_dict, outfile)
            outfile.close()
            self.has_changed = False

            return True
        elif filename.endswith(".yml"):
            try:
                yaml_dict = self.dump_tree()
                with open(filename, 'w') as outfile:
                      yaml.dump(yaml_dict, outfile)
                outfile.close()
                self.has_changed = False

                return True
            except Exception as ex:
                logging.getLogger("HWR").exception(\
                   "Could not save configuration to %s:" % filename + \
                   str(ex))
                return False
        else:
            try:
                cfg = repr(self.windows_list)
            except:
                logging.getLogger().exception("An exception occured " + \
                                          "while serializing GUI objects")
                return False
            else:
                try:
                    config_file = open(filename, "w")
                except:
                    logging.getLogger().exception(\
                        "Cannot save configuration to %s" % filename)
                    return False
                else:
                    config_file.write(cfg)
                    config_file.close()
                    self.has_changed = False

                return True

    def load(self, config, as_json):
        """Loads config"""
        self.windows_list = []
        self.windows = {}
        self.bricks = {}
        self.items = {}
        self.has_changed = False
        self.windows_list = config

        def load_children(children):
            """Loads children"""
            index = 0
            for child in children:
                new_item = None

                if "brick" in child:
                    brick = load_brick(child["type"], child["name"])
                    child["brick"] = brick

                    new_item = Qt4_BaseLayoutItems.BrickCfg(child["name"],
                                                            child["type"])

                    new_item["brick"] = brick
                    self.bricks[child["name"]] = new_item
                else:
                    if child["type"] == "window":
                        new_item = Qt4_BaseLayoutItems.WindowCfg(child["name"])
                        self.windows[child["name"]] = new_item
                    else:
                        NewItemClass = Configuration.classes[child["type"]]
                        new_item = NewItemClass(child["name"],
                                                child["type"])
                        self.items[child["name"]] = new_item

                if new_item is not None:
                    if type(child["properties"]) == bytes:
                    #if type(child["properties"]) == str:
                        try:
                            new_item.setProperties(pickle.loads(child["properties"]))
                            #newItem.setProperties(pickle.loads(child["properties"].encode('utf8')))
                        except:
                            logging.getLogger().exception(\
                                "Error: could not load properties " + \
                                "for %s", child["name"])
                            new_item.properties = PropertyBag.PropertyBag()
                    else:
                        new_item.setProperties(child["properties"])

                    child["properties"] = new_item.properties
                    new_item.__dict__ = child

                    #try:
                    #    new_item_signals = new_item["signals"]
                    #    new_item_slots = new_item["slots"]
                    #except:
                    #    new_item.__dict__ = child
                    #else:
                    #    new_item.__dict__ = child
                    #    new_item.slots = new_item_slots
                    #    new_item.signals = new_item_signals
                    #    children[index] = new_item
                    children[index] = new_item
                    load_children(child["children"])
                index += 1
        load_children(self.windows_list)

    def is_container(self, item):
        """
        :returns: True if item is container
        """
        return isinstance(item, Qt4_BaseLayoutItems.ContainerCfg)

    def is_spacer(self, item):
        """
        :returns: True if item is a spacer
        """
        return isinstance(item, Qt4_BaseLayoutItems.SpacerCfg)

    def is_window(self, item):
        """
        :returns: True if item is a window
        """
        return isinstance(item, Qt4_BaseLayoutItems.WindowCfg)

    def is_brick(self, item):
        """
        :returns: True if item is a brick
        """
        return isinstance(item, Qt4_BaseLayoutItems.BrickCfg)

    def reload_brick(self, brick_cfg):
        """Reloads brick
        """
        if type(brick_cfg) == bytes:
            brick_cfg = self.find_item(brick_cfg)

        brick_name = brick_cfg["name"]
        brick_type = brick_cfg["type"]

        parent, index = self.find_parent(brick_name, self.windows_list)

        if parent is not None:
            brick = load_brick(brick_type, brick_name)

            old_brick_cfg = parent["children"][index]
            new_brick_cfg = Qt4_BaseLayoutItems.BrickCfg(brick_name,
                                                         brick_type,
                                                         brick)
            parent["children"][index] = new_brick_cfg
            new_brick_cfg.setProperties(old_brick_cfg["properties"])

            return new_brick_cfg
