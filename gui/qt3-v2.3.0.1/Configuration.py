import logging
import imp
import types
import pprint
import cPickle
from BlissFramework.Utils import PropertyBag
from BlissFramework import BaseLayoutItems
from BlissFramework.BaseComponents import NullBrick


def loadModule(brickName):
    fp = None
    try:
        fp, pathname, description = imp.find_module(brickName, None)

        mod = imp.load_module(brickName, fp, pathname, description)
    except BaseException:
        if fp:
            fp.close()

        logging.getLogger().exception('Cannot import module %s', brickName)

        return None
    else:
        return mod


def loadBrick(brick_type, brick_name):
    module = loadModule(brick_type)

    if module is not None:
        try:
            classObj = getattr(module, brick_type)
        except AttributeError:
            logging.getLogger().error(
                'Cannot load brick %s : cannot found class %s in module',
                brick_name,
                brick_type)
            return NullBrick(None, brick_name)
        else:
            try:
                newInstance = classObj(None, brick_name)
            except BaseException:
                logging.getLogger().exception('Cannot load brick %s : initialization failed', brick_name)
                return NullBrick(None, brick_name)
            else:
                newInstance._BlissWidget__stop()
                return newInstance
    else:
        logging.getLogger().error("Cannot load brick %s : module could not be loaded.", brick_name)
        return NullBrick(None, brick_name)


class Configuration:
    classes = {"hbox": BaseLayoutItems.ContainerCfg,
               "vbox": BaseLayoutItems.ContainerCfg,
               "vgroupbox": BaseLayoutItems.ContainerCfg,
               "hgroupbox": BaseLayoutItems.ContainerCfg,
               "hspacer": BaseLayoutItems.SpacerCfg,
               "vspacer": BaseLayoutItems.SpacerCfg,
               "label": BaseLayoutItems.LabelCfg,
               "icon": BaseLayoutItems.IconCfg,
               "tab": BaseLayoutItems.TabCfg,
               "hsplitter": BaseLayoutItems.SplitterCfg,
               "vsplitter": BaseLayoutItems.SplitterCfg}

    def __init__(self, config=None):
        self.hasChanged = False

        if config is None:
            self.windows_list = []
            self.windows = {}
            self.bricks = {}
            self.items = {}
        else:
            self.load(config)

    def findContainer(self, container_name):
        try:
            parent = self.windows[container_name]
        except KeyError:
            try:
                parent = self.items[container_name]
            except KeyError:
                return
        return parent

    def addWindow(self):
        i = sum([x.startswith("window") and 1 or 0 for x in self.windows])
        window_name = "window%d" % i
        while window_name in self.windows:
            i += 1
            window_name = "window%d" % i

        self.windows_list.append(BaseLayoutItems.WindowCfg(window_name))

        self.windows[window_name] = self.windows_list[-1]

        self.hasChanged = True

        return self.windows_list[-1]

    def addItem(self, item_type, parent):
        if parent is None:
            logging.getLogger().error("Invalid parent container")
            return

        if item_type in Configuration.classes:
            i = sum([x.startswith(item_type) and 1 or 0 for x in self.items])
            item_name = "%s%d" % (item_type, i)
            while item_name in self.items:
                i += 1
                item_name = "%s%d" % (item_type, i)

            cfgClass = Configuration.classes[item_type]
            error = parent.addChild(cfgClass(item_name, item_type))
            if len(error) == 0:
                self.items[item_name] = parent["children"][-1]

                self.hasChanged = True

                return parent["children"][-1]
            else:
                return error
        else:
            logging.getLogger().error("Item of this type (%s) does not exist.", item_type)

    def addBrick(self, brick_type, parent):
        i = sum([x.startswith(brick_type) and 1 or 0 for x in self.bricks])
        brick_name = "%s%d" % (brick_type, i)
        while brick_name in self.bricks:
            i += 1
            brick_name = "%s%d" % (brick_type, i)

        brick = loadBrick(brick_type, brick_name)

        error = parent.addChild(BaseLayoutItems.BrickCfg(brick_name, brick_type, brick))

        if len(error) == 0:
            self.bricks[brick_name] = parent["children"][-1]

            self.hasChanged = True

            return parent["children"][-1]
        else:
            brick.close(True)

            return error

    def findParent(self, item_name, nodeset=[], parent=None):
        i = 0
        for item in nodeset:
            if item["name"] == item_name:
                return (parent, i)
            else:
                p, index = self.findParent(
                    item_name, nodeset=item["children"], parent=item)
                if p is not None:
                    return (p, index)
            i += 1

        return (None, -1)

    def findAllChildren(self, parent_item):
        return parent_item["children"] + sum([self.findAllChildren(child)
                                              for child in parent_item["children"]], [])

    def findItem(self, item_name, nodeset=None):
        if nodeset is None:
            nodeset = self.windows_list

        for item in nodeset:
            if item["name"] == item_name:
                return item
            else:
                _item = self.findItem(item_name, item["children"])
                if _item is not None:
                    return _item

    def findAllChildrenWType(self, item_type, parent_item):
        """valid types are: brick, container, splitter..."""
        try:
            t = getattr(BaseLayoutItems, "%sCfg" % str(item_type).title())
        except AttributeError:
            return {}

        def findChildrenWType(item_type, item):
            children = {}

            for child in item["children"]:
                if isinstance(child, t):
                    children[child["name"]] = child
                children.update(findChildrenWType(item_type, child))

            return children

        return findChildrenWType(item_type, parent_item)

    def rename(self, parent_item_name, child_pos, new_item_name):
        parent_item = self.findItem(parent_item_name)

        if parent_item is None:
            # window
            item = self.windows_list[child_pos]
        else:
            item = parent_item["children"][child_pos]

        old_item_name = item["name"]

        if new_item_name == old_item_name:
            return None

        if self.findItem(new_item_name):
            # new name conflicts with existing item !
            return old_item_name
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

            for item in all_items.itervalues():
                for c in item.connections:
                    if c[recv] == old_item_name:
                        print "receiver item %s in %s has been changed to %s" % (
                            old_item_name, item.name, new_item_name)
                        c[recv] = new_item_name

            self.hasChanged = True

    def remove(self, item_name):
        parent, i = self.findParent(item_name, self.windows_list)

        if parent is not None:
            try:
                del self.items[item_name]
            except KeyError:
                try:
                    del self.bricks[item_name]
                except KeyError:
                    pass

            parent.removeChild(i)

            self.hasChanged = True

            return True
        else:
            try:
                window = self.windows[item_name]
            except KeyError:
                return False
            else:
                self.windows_list.remove(window)

                del self.windows[item_name]

                self.hasChanged = True

                return True

    def moveUp(self, item_name):
        """Move an item up in the hierarchy

        Return the name of the new item's parent
        """
        parent, index = self.findParent(item_name, self.windows_list)

        #print item_name, parent["name"], index

        if parent is None:
            return None

        item = parent["children"][index]

        assert item["name"] == item_name

        if index == 0:
            # cannot move
            return None
        else:
            #print 'previous is :', parent["children"][index-1]["name"]
            del parent["children"][index]
            parent["children"].insert(index - 1, item)
            self.hasChanged = True
            return parent["name"]

    def moveDown(self, item_name):
        """Move an item down in the hierarchy

        Return the name of its new parent item
        """
        parent, index = self.findParent(item_name, self.windows_list)

        #print item_name, parent["name"], index

        if parent is None:
            return None

        item = parent["children"][index]

        assert item["name"] == item_name

        try:
            nextItem = parent["children"][index + 1]
        except IndexError:
            return None
        else:
            #print 'next is :', nextItem["name"]
            del parent["children"][index]
            #print '1'
            parent["children"].insert(index + 1, item)
            #print '2'
            self.hasChanged = True
            return parent["name"]

    def moveItem(self, source_item_name, target_item_name):
        """Move an item to another place in the hierarchy

        Mainly useful for drag'n'drop on the list elements.
        """
        if source_item_name == target_item_name:
            return False

        source_parent_cfg, source_item_pos = self.findParent(
            source_item_name, self.windows_list)
        target_parent_cfg, target_item_pos = self.findParent(
            target_item_name, self.windows_list)

        if source_parent_cfg is None:
            # cannot drag an entire window
            return False
        else:
            source_item_cfg = source_parent_cfg["children"][source_item_pos]

        if target_parent_cfg is None:
            # we are dropping on a window
            target_item_cfg = self.windows[target_item_name]

            if not self.isContainer(source_item_cfg):
                return False
        else:
            target_item_cfg = target_parent_cfg["children"][target_item_pos]

        if target_item_cfg in self.findAllChildren(source_item_cfg):
            # cannot move a parent in a child
            return False

        del source_parent_cfg["children"][source_item_pos]

        if self.isContainer(target_item_cfg):
            target_item_cfg["children"].insert(0, source_item_cfg)
            #print [x["name"] for x in target_item_cfg["children"]]
        else:
            target_parent_cfg["children"].insert(target_item_pos, source_item_cfg)

        self.hasChanged = True

        return True

# def change(self, item, new_type=None):
# if new_type is None:
# new_types = { "hbox": "vbox",
# "vbox": "hbox",
# "vspacer": "hspacer",
# "hspacer": "vspacer",
# "hsplitter": "vsplitter",
# "vsplitter": "hsplitter" }

# try:
##                 item["type"] = new_types[item["type"]]
# except KeyError:
# pass
# else:
##             item["type"] = new_type

    def dump(self):
        pprint.pprint(self.windows_list)

    def dump_tree(self):
        wl = []

        for window_cfg in self.windows_list:
            children = []

            def add_children(item_cfg):
                children = []

                for child in item_cfg["children"]:
                    children.append(
                        {"name": child["name"], "children": add_children(child)})

                return children

            wl.append({"name": window_cfg["name"],
                       "children": add_children(window_cfg)})

        pprint.pprint(wl)

    def save(self, filename):
        #print 'saving to', filename, 'id is', id(self)
        try:
            cfg = repr(self.windows_list)
        except BaseException:
            logging.getLogger().exception("panic: an exception occured while serializing GUI objects")
            return False
        else:
            try:
                config_file = open(filename, "w")
            except BaseException:
                logging.getLogger().exception("Cannot save configuration to %s", filename)
                return False
            else:
                config_file.write(cfg)
                config_file.close()

                self.hasChanged = False

            return True

    def load(self, config):
        self.windows_list = []
        self.windows = {}
        self.bricks = {}
        self.items = {}
        self.hasChanged = False

        self.windows_list = config

        def loadChildren(children):
            i = 0
            for child in children:
                newItem = None

                if "brick" in child:
                    b = loadBrick(child["type"], child["name"])
                    child["brick"] = b

                    newItem = BaseLayoutItems.BrickCfg(child["name"], child["type"])
                    newItem["brick"] = b
                    self.bricks[child["name"]] = newItem
                else:
                    if child["type"] == "window":
                        newItem = BaseLayoutItems.WindowCfg(child["name"])
                        self.windows[child["name"]] = newItem
                    else:
                        newItemClass = Configuration.classes[child["type"]]
                        newItem = newItemClass(child["name"], child["type"])
                        self.items[child["name"]] = newItem

                if newItem is not None:
                    if isinstance(child["properties"], types.StringType):
                        try:
                            #print "loading properties for %s" % child["name"]
                            newItem.setProperties(cPickle.loads(child["properties"]))
                        except BaseException:
                            logging.getLogger().exception(
                                "Error: could not load properties for %s", child["name"])
                            newItem.properties = PropertyBag.PropertyBag()
                    else:
                        newItem.setProperties(child["properties"])

                    child["properties"] = newItem.properties

                    newItem.__dict__ = child
                    children[i] = newItem

                    loadChildren(child["children"])
                i += 1

        loadChildren(self.windows_list)

    def isContainer(self, item):
        return isinstance(item, BaseLayoutItems.ContainerCfg)

    def isSpacer(self, item):
        return isinstance(item, BaseLayoutItems.SpacerCfg)

    def isWindow(self, item):
        return isinstance(item, BaseLayoutItems.WindowCfg)

    def isBrick(self, item):
        return isinstance(item, BaseLayoutItems.BrickCfg)

    def reload_brick(self, brick_cfg):
        if isinstance(brick_cfg, types.StringType):
            brick_cfg = self.findItem(brick_cfg)

        brick_name = brick_cfg["name"]
        brick_type = brick_cfg["type"]

        #print 'reloading', brick_name
        parent, index = self.findParent(brick_name, self.windows_list)

        if parent is not None:
            brick = loadBrick(brick_type, brick_name)

            old_brick_cfg = parent["children"][index]
            new_brick_cfg = BaseLayoutItems.BrickCfg(brick_name, brick_type, brick)
            parent["children"][index] = new_brick_cfg

            new_brick_cfg.setProperties(old_brick_cfg["properties"])

            return new_brick_cfg
