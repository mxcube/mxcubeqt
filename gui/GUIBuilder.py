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

"""GUI Builder interface"""

import os
import re
import imp
import weakref
import logging
import subprocess

import gui
from gui import Configuration
from gui.utils import Icons, ConnectionEditor, PropertyEditor, GUIDisplay, QtImport
from gui.bricks import LogViewBrick
from gui.BaseLayoutItems import ContainerCfg

from HardwareRepository import HardwareRepository


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class HorizontalSpacer(QtImport.QWidget):
    """Horizontal spacer class"""

    def __init__(self, *args, **kwargs):
        """__init__
        """

        QtImport.QWidget.__init__(self, *args)

        h_size = kwargs.get("size", None)
        if h_size is not None:
            self.setFixedWidth(h_size)
            self.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)
        else:
            self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)


class CustomListWidget(QtImport.QListWidget):
    """Custom ListWidget
    """

    def __init__(self, *args):
        """__init__ method"""

        QtImport.QListWidget.__init__(self, *args)
        self.setVerticalScrollBarPolicy(QtImport.Qt.ScrollBarAsNeeded)
        self.setSelectionMode(QtImport.QAbstractItemView.SingleSelection)

    def addToolTip(self, item, text):
        """Sets tool tip"""

        self.setToolTip(text)


class GUITreeWidget(QtImport.QTreeWidget):
    """Gui config tree"""

    dragDropSignal = QtImport.pyqtSignal(object, object)

    def __init__(self, *args):
        """__init__ method"""

        QtImport.QTreeWidget.__init__(self, *args)

        self.setColumnCount(2)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.setHeaderLabels(["Element", "Type"])
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setSelectionMode(QtImport.QAbstractItemView.SingleSelection)
        self.setItemsExpandable(True)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Expanding)

        self.drag_source_item = None
        self.drag_target_item = None

    def dragEnterEvent(self, event):
        """Drag start event"""

        if self.drag_source_item is None:
            self.drag_source_item = self.selectedItems()[0]
        event.accept()

    def dropEvent(self, event):
        """Drop event"""

        self.drag_target_item = self.itemAt(event.pos())
        if self.drag_source_item and self.drag_target_item:
            self.dragDropSignal.emit(self.drag_source_item, self.drag_target_item)
            self.drag_source_item = None
        event.accept()


class ToolboxWidget(QtImport.QWidget):
    """Toolbox windget"""

    addBrickSignal = QtImport.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """Init"""

        QtImport.QWidget.__init__(self, *args)

        # Internal variables --------------------------------------------------
        self.bricks_tab_dict = {}
        self.bricks_dict = {}

        # Graphic elements ----------------------------------------------------
        _top_frame = QtImport.QFrame(self)
        _refresh_toolbutton = QtImport.QToolButton(_top_frame)
        _refresh_toolbutton.setIcon(Icons.load_icon("reload"))
        self._bricks_toolbox = QtImport.QToolBox(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(QtImport.QLabel("Available bricks", _top_frame))
        _main_vlayout.addWidget(_refresh_toolbutton)
        _main_vlayout.addWidget(self._bricks_toolbox)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        _refresh_toolbutton.clicked.connect(self.refresh_clicked)

        # Other ---------------------------------------------------------------
        self.setWindowTitle("Toolbox")
        self.setToolTip("refresh bricks list")

    def add_brick_tab(self, name):
        """Adds a new brick tab with a name

        :param name: name of the tab
        :type name: str
        :returns: list of bricks
        """

        new_bricks_list = CustomListWidget(self._bricks_toolbox)
        new_bricks_list.itemDoubleClicked.connect(self.brick_selected)
        self._bricks_toolbox.addItem(new_bricks_list, name)
        self.bricks_tab_dict[name] = new_bricks_list

        return new_bricks_list

    def refresh_clicked(self):
        """Refresh list of available bricks"""

        while self._bricks_toolbox.currentWidget():
            self._bricks_toolbox.removeItem(self._bricks_toolbox.currentIndex())

        self.bricks_dict = {}
        self.bricks_tab_dict = {}
        list(
            map(
                self.add_bricks,
                (gui.get_base_bricks_path(),) + tuple(gui.get_custom_bricks_dirs()),
            )
        )

    def get_brick_text_label(self, brick_name):
        """
        :returns: brick text
        """

        if brick_name.endswith("Brick"):
            brick_text_label = brick_name[:-5]
        else:
            brick_text_label = brick_name

        for index in range(len(brick_text_label)):
            if brick_text_label[index].isalpha() or brick_text_label[index].isdigit():
                if (
                    index > 0
                    and brick_text_label[index].isupper()
                    and brick_text_label[index - 1].islower()
                ):
                    brick_text_label = (
                        brick_text_label[0:index]
                        + " "
                        + brick_text_label[index].lower()
                        + brick_text_label[index + 1 :]
                    )
            else:
                brick_text_label = (
                    brick_text_label[0:index] + " " + brick_text_label[index + 1 :]
                )

        return brick_text_label

    def add_bricks(self, brickDir):
        """Add the bricks found in the 'brickDir' directory to the
           bricks tab widget
        """

        find_category_re = re.compile(r"^__category__\s*=\s*['\"](.*)['\"]$", re.M)
        find_docstring_re = re.compile('^"""(.*?)"""?$', re.M | re.S)
        full_filenames = []

        for file_or_dir in os.listdir(brickDir):
            full_path = os.path.join(brickDir, file_or_dir)
            if os.path.isdir(full_path):
                path_with_trunk = os.path.join(full_path, "trunk")
                if os.path.isdir(path_with_trunk):
                    full_path = path_with_trunk
                file_names = [
                    os.path.join(full_path, filename)
                    for filename in os.listdir(full_path)
                ]
                full_filenames.extend(file_names)
            else:
                full_filenames.append(full_path)

        full_filenames.sort()
        processed_bricks = []
        brick_categories = {}

        for full_filename in full_filenames:
            filename = os.path.basename(full_filename)

            if [x for x in [x[0] for x in imp.get_suffixes()] if filename.endswith(x)]:
                brick_name = filename[: filename.rfind(".")]

                if (
                    not brick_name.startswith("__")
                    and not "cpython" in brick_name
                    and not brick_name in processed_bricks
                ):
                    processed_bricks.append(brick_name)
                    directory_name = os.path.dirname(full_filename)
                    brick_module_file = None

                    try:
                        brick_module_file, path, description = imp.find_module(
                            brick_name, [directory_name]
                        )
                    except BaseException:
                        if brick_module_file:
                            brick_module_file.close()
                        continue
                    module_contents = brick_module_file.read()

                    check_if_it_Brick = re.compile(
                        "^\s*class\s+%s.+?:\s*$" % brick_name, re.M
                    )
                    if not check_if_it_Brick.search(module_contents):
                        continue

                    match = find_category_re.search(module_contents)
                    if match is None:
                        category = ""
                    else:
                        category = match.group(1)

                    match = find_docstring_re.search(module_contents)
                    if match is None:
                        description = ""
                    else:
                        description = match.group(1)

                    try:
                        brick_categories[category].append(
                            (brick_name, directory_name, description)
                        )
                    except KeyError:
                        brick_categories[category] = [
                            (brick_name, directory_name, description)
                        ]

        if len(brick_categories) == 0:
            return

        category_keys = sorted(brick_categories.keys())

        for category in category_keys:
            bricks_list = brick_categories[category]

            try:
                bricks_listwidget = self.bricks_tab_dict[category]
            except KeyError:
                bricks_listwidget = self.add_brick_tab(category)

            for brick_name, directory_name, description in bricks_list:
                brick_list_widget_item = QtImport.QListWidgetItem(
                    self.get_brick_text_label(brick_name), bricks_listwidget
                )
                bricks_listwidget.addToolTip(brick_list_widget_item, description)
                self.bricks_dict[id(brick_list_widget_item)] = (
                    directory_name,
                    brick_name,
                )

    def brick_selected(self, item):
        """Brick selected event"""

        dir_name, brick_name = self.bricks_dict[id(item)]
        self.addBrickSignal.emit(brick_name)


class PropertyEditorWindow(QtImport.QWidget):
    """Property editor window contains two tables:
       One for properties to link hardware objects (property name
       start with hwobj_) and the second one for all other properties
    """

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QWidget.__init__(self, *args)

        self.setWindowTitle("Properties")

        self.properties_table = PropertyEditor.ConfigurationTable(self)
        self.hwobj_properties_table = PropertyEditor.ConfigurationTable(self)

        self.__property_changed_cb = weakref.WeakKeyDictionary()

        self.properties_table.propertyChangedSignal.connect(self.property_changed)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.properties_table)
        _main_vlayout.addWidget(QtImport.QLabel("Hardware objects:", self))
        _main_vlayout.addWidget(self.hwobj_properties_table)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Minimum)

    def edit_properties(self, property_bag):
        """Edits property"""

        self.properties_table.set_property_bag(property_bag)
        self.hwobj_properties_table.set_property_bag(property_bag, display_hwobj=True)

    def property_changed(self, *args):
        """Property changed callback"""
        try:
            property_changed_cb = self.__property_changed_cb[
                self.properties_table.property_bag
            ]
        except KeyError as err:
            return
        else:
            property_changed_cb(*args)

    def add_properties(self, property_bag, property_changed_cb):
        """Adds properties"""

        self.__property_changed_cb[property_bag] = property_changed_cb
        self.edit_properties(property_bag)


class ToolButton(QtImport.QToolButton):
    """Custom ToolButton"""

    def __init__(self, parent, icon, text=None, callback=None, tooltip=None):
        """init"""

        QtImport.QToolButton.__init__(self, parent)

        self.setIcon(Icons.load_icon(icon))

        if not isinstance(text, bytes):
            tooltip = callback
            callback = text
        else:
            self.setTextLabel(text)
            self.setTextPosition(QtImport.QToolButton.BesideIcon)
            self.setUsesTextLabel(True)

        if callback is not None:
            self.clicked.connect(callback)

        if tooltip is not None:
            self.setToolTip(tooltip)
            # QtImport.QToolTip.add(self, tooltip)

        self.setSizePolicy(QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed)


class GUIEditorWindow(QtImport.QWidget):
    """Gui editor window"""

    editPropertiesSignal = QtImport.pyqtSignal(object)
    newItemSignal = QtImport.pyqtSignal(object, object)
    drawPreviewSignal = QtImport.pyqtSignal(object, int, list, object)
    updatePreviewSignal = QtImport.pyqtSignal(object, object, object, object)
    addWidgetSignal = QtImport.pyqtSignal(object, object)
    removeWidgetSignal = QtImport.pyqtSignal(object, object)
    moveWidgetSignal = QtImport.pyqtSignal(object, object)
    showProperyEditorWindowSignal = QtImport.pyqtSignal()
    hidePropertyEditorWindowSignal = QtImport.pyqtSignal()
    showPreviewSignal = QtImport.pyqtSignal()

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.configuration = Configuration.Configuration()

        # Graphic elements ----------------------------------------------------
        _tools_widget = QtImport.QWidget(self)
        _add_window_toolbutton = ToolButton(
            _tools_widget,
            "window_new",
            self.add_window_clicked,
            "Add a new window (container)",
        )
        _add_tab_toolbutton = ToolButton(
            _tools_widget, "tab", self.add_tab_clicked, "Add a new tab (container)"
        )
        _add_hbox_toolbutton = ToolButton(
            _tools_widget,
            "add_hbox",
            self.add_hbox_clicked,
            "Add a new horizontal box (container)",
        )
        _add_vbox_toolbutton = ToolButton(
            _tools_widget,
            "add_vbox",
            self.add_vbox_clicked,
            "Add a new vertical box (container)",
        )
        _add_hgroupbox_toolbutton = ToolButton(
            _tools_widget,
            "hgroupbox",
            self.add_hgroupbox_clicked,
            "add a new horizontal group box (container)",
        )
        _add_vgroupbox_toolbutton = ToolButton(
            _tools_widget,
            "vgroupbox",
            self.add_vgroupbox_clicked,
            "Add a new vertical group box (container)",
        )
        _add_hspacer_toolbutton = ToolButton(
            _tools_widget,
            "add_hspacer",
            self.add_hspacer_clicked,
            "Add a new horizontal spacer",
        )
        _add_vspacer_toolbutton = ToolButton(
            _tools_widget,
            "add_vspacer",
            self.add_vspacer_clicked,
            "add a new vertical spacer",
        )
        _add_hsplitter_toolbutton = ToolButton(
            _tools_widget,
            "hsplitter",
            self.add_hsplitter_clicked,
            "Add a new horizontal splitter (container)",
        )
        _add_vsplitter_toolbutton = ToolButton(
            _tools_widget,
            "vsplitter",
            self.add_vsplitter_clicked,
            "add a new vertical splitter (container)",
        )
        _add_icon_toolbutton = ToolButton(
            _tools_widget, "icon", self.add_icon_clicked, "add a new icon"
        )
        _add_label_toolbutton = ToolButton(
            _tools_widget, "label", self.add_label_clicked, "add a new label"
        )

        _tree_handling_widget = QtImport.QWidget(self)
        _show_connections_toolbutton = ToolButton(
            _tree_handling_widget,
            "connect_creating",
            self.show_connections_clicked,
            "Manage connections between items",
        )
        _move_up_toolbutton = ToolButton(
            _tree_handling_widget, "Up2", self.move_up_clicked, "move an item up"
        )
        _move_down_toolbutton = ToolButton(
            _tree_handling_widget, "Down2", self.move_down_clicked, "move an item down"
        )
        _remove_item_toolbutton = ToolButton(
            _tree_handling_widget,
            "delete_small",
            self.remove_item_clicked,
            "delete an item",
        )

        self.tree_widget = GUITreeWidget(self)
        self.root_element = QtImport.QTreeWidgetItem(self.tree_widget)
        self.root_element.setText(0, "GUI tree")
        self.root_element.setExpanded(True)

        self.connection_editor_window = ConnectionEditor.ConnectionEditor(
            self.configuration
        )

        # Layout --------------------------------------------------------------
        _toolbox_hlayout = QtImport.QHBoxLayout(_tools_widget)
        _toolbox_hlayout.addWidget(_add_window_toolbutton)
        _toolbox_hlayout.addWidget(_add_tab_toolbutton)
        _toolbox_hlayout.addWidget(_add_hbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_vbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_hgroupbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_vgroupbox_toolbutton)
        _toolbox_hlayout.addWidget(_add_hspacer_toolbutton)
        _toolbox_hlayout.addWidget(_add_vspacer_toolbutton)
        _toolbox_hlayout.addWidget(_add_hsplitter_toolbutton)
        _toolbox_hlayout.addWidget(_add_vsplitter_toolbutton)
        _toolbox_hlayout.addWidget(_add_icon_toolbutton)
        _toolbox_hlayout.addWidget(_add_label_toolbutton)
        _toolbox_hlayout.addStretch(0)
        _toolbox_hlayout.setSpacing(2)
        _toolbox_hlayout.setContentsMargins(2, 2, 2, 2)

        _tree_handling_widget_hlayout = QtImport.QHBoxLayout(_tree_handling_widget)
        _tree_handling_widget_hlayout.addWidget(_show_connections_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_move_up_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_move_down_toolbutton)
        _tree_handling_widget_hlayout.addWidget(_remove_item_toolbutton)
        _tree_handling_widget_hlayout.addStretch(0)
        _tree_handling_widget_hlayout.setSpacing(2)
        _tree_handling_widget_hlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(_tools_widget)
        _main_vlayout.addWidget(_tree_handling_widget)
        _main_vlayout.addWidget(self.tree_widget)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        _tools_widget.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)

        # Qt signal/slot connections ------------------------------------------
        self.tree_widget.itemSelectionChanged.connect(self.item_selected)
        self.tree_widget.itemDoubleClicked.connect(self.item_double_clicked)
        self.tree_widget.itemChanged.connect(self.item_changed)
        self.tree_widget.dragDropSignal.connect(self.item_drag_dropped)

        # Other ---------------------------------------------------------------
        self.item_rename_started = None
        self.setWindowTitle("GUI Editor")

    def create_action(
        self,
        text,
        slot=None,
        shortcut=None,
        icon=None,
        tip=None,
        checkable=False,
        signal="triggered()",
    ):
        """Creates an action"""

        action = QtImport.QAction(text, self)
        if icon is not None:
            action.setIcon(Icons.load_icon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.signal.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        """Adds action"""

        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def set_configuration(self, configuration):
        """Sets configuration
        """

        self.configuration = configuration
        self.tree_widget.blockSignals(True)
        self.hidePropertyEditorWindowSignal.emit()

        def add_children(children, parent_item):
            parent_name = str(parent_item.text(0))
            parent = self.configuration.find_container(parent_name)

            for child in children:
                if self.configuration.is_container(child):
                    new_list_item = self.append_item(
                        parent_item, child["name"], child["type"], icon=child["type"]
                    )
                    add_children(child["children"], new_list_item)
                    self.configuration.items[child["name"]].update_slots()
                elif self.configuration.is_spacer(child):
                    new_list_item = self.append_item(
                        parent_item, child["name"], "spacer", icon=child["type"]
                    )
                elif self.configuration.is_brick(child):
                    new_list_item = self.append_item(
                        parent_item, child["name"], child["type"], icon="brick"
                    )
                else:
                    new_list_item = self.append_item(
                        parent_item, child["name"], child["type"], icon=child["type"]
                    )
                self.connect_item(parent, child, new_list_item)

        for window in self.configuration.windows_list:
            parent_window_item = self.append_item(
                self.root_element, window.name, "window", icon="window_small"
            )
            self.connect_item(None, window, parent_window_item)
            add_children(window["children"], parent_window_item)

        self.tree_widget.blockSignals(False)
        # self.tree_widget.triggerUpdate()
        self.tree_widget.update()
        self.tree_widget.setCurrentItem(self.root_element.child(0))
        self.showProperyEditorWindowSignal.emit()

    def show_connections_clicked(self):
        """Show dialog with connection table between bricks"""

        self.connection_editor_window.show_connections(self.configuration)
        self.connection_editor_window.show()

    def update_properties(self, item_cfg):
        """Updates properties"""

        self.editPropertiesSignal.emit(item_cfg["properties"])

    def append_item(self, parent_item, column1_text, column2_text, icon=None):
        """Appends an item to the tree"""

        new_treewidget_item = QtImport.QTreeWidgetItem(parent_item)
        new_treewidget_item.setText(0, str(column1_text))
        new_treewidget_item.setText(1, str(column2_text))
        new_treewidget_item.setExpanded(True)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)

        if isinstance(icon, str):
            new_treewidget_item.setIcon(0, Icons.load_icon(icon))
        self.tree_widget.setCurrentItem(new_treewidget_item)
        self.tree_widget.scrollToItem(
            new_treewidget_item, QtImport.QAbstractItemView.EnsureVisible
        )

        return new_treewidget_item

    def remove_item_clicked(self):
        """Removes item from the config tree"""

        current_item = self.tree_widget.currentItem()
        if current_item:
            item_parent_name = str(current_item.parent().text(0))
            item_name = str(current_item.text(0))
            children_count = current_item.childCount()
            if children_count > 0:
                if (
                    QtImport.QMessageBox.warning(
                        self,
                        "Please confirm",
                        "Are you sure you want to remove %s ?\n" % item_name
                        + "%d children will be removed." % children_count,
                        QtImport.QMessageBox.Yes,
                        QtImport.QMessageBox.No,
                    )
                    == QtImport.QMessageBox.No
                ):
                    return

            item_cfg = self.configuration.find_item(item_name)

            children_name_list = []
            for child in item_cfg["children"]:
                children_name_list.append(child["name"])

            self.removeWidgetSignal.emit(item_name, children_name_list)

            if self.configuration.remove(item_name):
                root = self.tree_widget.invisibleRootItem()
                for item in self.tree_widget.selectedItems():
                    (item.parent() or root).removeChild(item)

    def draw_window_preview(self):
        """Draws GUI"""
        container_name = self.root_element.child(0).text(0)
        container_cfg, window_id, container_ids, selected_item = self.prepare_window_preview(
            container_name, None, ""
        )
        self.drawPreviewSignal.emit(
            container_cfg, window_id, container_ids, selected_item
        )

    def update_window_preview(
        self, container_name, container_cfg=None, selected_item=""
    ):
        """Refresh GUI"""

        upd_container_cfg, upd_window_id, upd_container_ids, upd_selected_item = self.prepare_window_preview(
            container_name, container_cfg, selected_item
        )
        self.updatePreviewSignal.emit(
            upd_container_cfg, upd_window_id, upd_container_ids, selected_item
        )

    def prepare_window_preview(self, item_name, item_cfg=None, selected_item=""):
        """Prepares window"""

        item_list = self.tree_widget.findItems(str(item_name), QtImport.Qt.MatchRecursive, 0)
        item = item_list[0]
        item_type = str(item.text(1))

        window_id = None
        if item_type == "window":
            window_id = str(item.text(0))
        else:
            # find parent window
            parent = item.parent()
            while parent:
                if str(parent.text(1)) == "window":
                    window_id = str(parent.text(0))
                    break
                parent = parent.parent()

        if item_type != "window" and item.childCount() == 0:
            item = item.parent()
            item_name = str(item.text(0))
            item_cfg = None

        if item_cfg is None:
            item_cfg = self.configuration.find_item(item_name)

        item_ids = []
        current_item = self.root_element
        while self.tree_widget.itemBelow(current_item):
            current_item = self.tree_widget.itemBelow(current_item)
            item_ids.append(str(current_item.text(0)))

        return item_cfg, window_id, item_ids, selected_item

    def connect_item(self, parent, new_item, new_list_item):
        """Connect item"""

        if self.configuration.is_brick(new_item):
            self.newItemSignal.emit(
                new_item["brick"].property_bag, new_item["brick"]._property_changed
            )
        else:
            if parent is not None:
                parent_ref = weakref.ref(parent)
            else:
                parent_ref = None

            def property_changed_cb(
                property_name,
                old_value,
                new_value,
                item_ref=weakref.ref(new_list_item),
                parent_ref=parent_ref,
            ):
                item = item_ref()
                if item is None:
                    return

                item_name = str(item.text(0))
                item_type = str(item.text(1))

                try:
                    item_class = Configuration.Configuration.classes[item_type]
                except KeyError:
                    self.update_window_preview(item_name)
                else:
                    if issubclass(item_class, ContainerCfg):
                        # we should update the container itself,
                        # not just its contents so we trigger an
                        # update of the parent instead
                        if parent_ref is not None:
                            parent = parent_ref()
                            if parent is not None:
                                self.update_window_preview(parent["name"], parent)
                    else:
                        self.update_window_preview(item_name)

                if parent_ref is not None:
                    parent = parent_ref()
                    if parent is None:
                        return
                    parent.childPropertyChanged(
                        item_name, property_name, old_value, new_value
                    )

            self.newItemSignal.emit(new_item["properties"], property_changed_cb)

    def add_window_clicked(self):
        """Adds window"""

        self._add_item(self.root_element, "window")

    def _add_item(self, parent_list_item, item_type, *args):
        """Adds item"""

        parent_name = str(parent_list_item.text(0))

        parent = self.configuration.find_container(parent_name)
        new_item = None
        new_list_item = None

        try:
            QtImport.QApplication.setOverrideCursor(QtImport.QCursor(QtImport.Qt.WaitCursor))

            if item_type == "window":
                new_item = self.configuration.add_window()

                if isinstance(new_item, bytes):
                    QtImport.QMessageBox.warning(
                        self, "Cannot add item", new_item, QtImport.QMessageBox.Ok
                    )
                else:
                    new_item["properties"].getProperty("w").setValue(
                        QtImport.QApplication.desktop().width()
                    )
                    new_item["properties"].getProperty("h").setValue(
                        QtImport.QApplication.desktop().height()
                    )
                    new_list_item = self.append_item(
                        parent_list_item,
                        new_item["name"],
                        "window",
                        icon="window_small",
                    )
            elif item_type == "brick":
                brick_type = args[0]
                new_item = self.configuration.add_brick(brick_type, parent)

                if isinstance(new_item, bytes):
                    QtImport.QMessageBox.warning(self, "Cannot add", new_item, QtImport.QMessageBox.Ok)
                else:
                    brick_name = new_item["name"]
                    brick = new_item["brick"]
                    new_list_item = self.append_item(
                        parent_list_item, brick_name, brick_type, icon="brick"
                    )
            elif item_type == "tab":
                new_item = self.configuration.add_item(item_type, parent)

                if isinstance(new_item, bytes):
                    QtImport.QMessageBox.warning(self, "Cannot add", new_item, QtImport.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]
                    new_list_item = self.append_item(
                        parent_list_item, item_name, item_type, icon=item_type
                    )
            else:
                item_subtype = args[0]
                new_item = self.configuration.add_item(item_subtype, parent)

                if isinstance(new_item, bytes):
                    QtImport.QMessageBox.warning(self, "Cannot add", new_item, QtImport.QMessageBox.Ok)
                else:
                    item_name = new_item["name"]
                    new_list_item = self.append_item(
                        parent_list_item, item_name, item_type, icon=item_subtype
                    )

            if not isinstance(new_item, bytes) and new_item is not None:
                self.connect_item(parent, new_item, new_list_item)
                self.addWidgetSignal.emit(new_item, parent)
        finally:
            QtImport.QApplication.restoreOverrideCursor()

    def add_brick(self, brick_type):
        """Adds bricks to the gui"""

        self.add_item("brick", str(brick_type))

    def add_container(self, container_type, container_subtype=None):
        """Adds container"""

        self.add_item(container_type, container_subtype)

    def add_item(self, item_type, item_subtype):
        """Adds item"""

        current_item = self.tree_widget.currentItem()
        if current_item:
            item_cfg = self.configuration.find_item(str(current_item.text(0)))

            try:
                if self.configuration.is_container(item_cfg):
                    self._add_item(current_item, item_type, item_subtype)
                else:
                    parent_item = current_item.parent()
                    self._add_item(parent_item, item_type, item_subtype)
            except BaseException:
                QtImport.QMessageBox.warning(
                    self,
                    "Cannot add %s" % item_type,
                    "Please select a suitable parent container",
                    QtImport.QMessageBox.Ok,
                )

    def add_hbox_clicked(self):
        """Adds horizontal box"""

        self.add_container("hbox", "hbox")

    def add_vbox_clicked(self):
        """Adds vertical box"""

        self.add_container("vbox", "vbox")

    def add_hgroupbox_clicked(self):
        """Adds horizontal groupbox"""

        self.add_container("hgroupbox", "hgroupbox")

    def add_vgroupbox_clicked(self):
        """Adds vertical groupbox"""

        self.add_container("vgroupbox", "vgroupbox")

    def add_hspacer_clicked(self):
        """Adds horizontal spacer"""

        self.add_item("hspacer", "hspacer")

    def add_vspacer_clicked(self):
        """Adds vertical spacer"""

        self.add_item("vspacer", "vspacer")

    def add_tab_clicked(self):
        """Adds tab"""

        self.add_container("tab")

    def add_vsplitter_clicked(self):
        """Adds vertical splitter"""

        self.add_container("vsplitter", "vsplitter")

    def add_hsplitter_clicked(self):
        """Adds horizontal splitter"""

        self.add_container("hsplitter", "hsplitter")

    def add_icon_clicked(self):
        """Adds icon"""

        self.add_item("icon", "icon")

    def add_label_clicked(self):
        """Adds label"""

        self.add_item("label", "label")

    def preview_item_clicked(self, item_name):
        """Event when user clicks on the widget:
           Changes color of widget to selected color and
           Refreshes property table
        """

        item = self.tree_widget.findItems(str(item_name), QtImport.Qt.MatchRecursive, 0)
        if item is not None:
            self.tree_widget.setCurrentItem(item[0])
            self.tree_widget.scrollToItem(item[0], QtImport.QAbstractItemView.EnsureVisible)

    def item_double_clicked(self, item, column):
        """Item double click event"""

        if item and column == 0:
            item_name = str(item.text(0))
            item_cfg = self.configuration.find_item(item_name)
            if item_cfg:
                item.setFlags(
                    QtImport.Qt.ItemIsSelectable | QtImport.Qt.ItemIsEnabled | QtImport.Qt.ItemIsEditable
                )
                self.item_rename_started = True
                self.tree_widget.editItem(item)
                item.setFlags(QtImport.Qt.ItemIsSelectable | QtImport.Qt.ItemIsEnabled)

    def item_selected(self):
        """Item selected"""

        self.item_rename_started = None
        item = self.tree_widget.currentItem()
        if not item == self.root_element:
            item_name = str(item.text(0))
            item_cfg = self.configuration.find_item(item_name)
            self.update_window_preview(item_name, item_cfg, selected_item=item_name)
            self.update_properties(item_cfg)
            self.showProperyEditorWindowSignal.emit()

    def item_changed(self, item, col):
        """Item changed even. Used when item text in column 0
           has been changed
        """

        if self.item_rename_started:
            item_parent_name = str(item.parent().text(0))
            new_item_name = str(item.text(0))
            old_name = self.configuration.rename(
                item_parent_name, item.parent().indexOfChild(item), new_item_name
            )
            if old_name is not None:
                item.setText(0, old_name)
                QtImport.QMessageBox.warning(
                    self,
                    "Cannot rename item",
                    "New name %s conflicts\nwith another item name." % new_item_name,
                    QtImport.QMessageBox.Ok,
                )

    def item_drag_dropped(self, source_item, target_item):
        """Drag and drop event"""

        dragged_item_name = source_item.text(0)
        dropped_on_item_name = target_item.text(0)

        source_item_parent_name = str(source_item.parent().text(0))
        target_item_parent_name = str(target_item.parent().text(0))

        # find common ancestor
        target_item_ancestors = [target_item.parent()]
        source_item_ancestors = [source_item.parent()]
        while target_item_ancestors[0]:
            target_item_ancestors.insert(0, target_item_ancestors[0].parent())
        while source_item_ancestors[0]:
            source_item_ancestors.insert(0, source_item_ancestors[0].parent())
        common_ancestor = zip(target_item_ancestors, source_item_ancestors)[-1][0]
        if common_ancestor != self.root_element:
            common_ancestor_name = str(common_ancestor.text(0))
        else:
            common_ancestor_name = ""

        # move item in configuration
        if not self.configuration.move_item(dragged_item_name, dropped_on_item_name):
            # self.tree_widget.setSelected(source_item, True)
            source_item.setSelected(True)
            self.tree_widget.setCurrentItem(source_item)
            return

        source_item.parent().takeChild(source_item.parent().indexOfChild(source_item))
        target_cfg_item = self.configuration.find_item(dropped_on_item_name)

        if self.configuration.is_container(target_cfg_item):
            # have to insert in the container
            target_item.addChild(source_item)
        else:
            target_item.parent().addChild(source_item)
            # source_item.moveItem(target_item)

        # if source_item_parent_name != target_item_parent_name:
        #    self.update_window_preview(source_item_parent_name)
        if len(common_ancestor_name):
            self.update_window_preview(common_ancestor_name)

        # source_item.setSelected(True)
        source_item.setSelected(True)
        self.tree_widget.setCurrentItem(source_item)
        self.tree_widget.scrollToItem(source_item, QtImport.QAbstractItemView.EnsureVisible)

    def move_item(self, direction):
        """Moves item

        :param direction: direction (up/down)
        :type direction: str
        """
        item = self.tree_widget.currentItem()

        if item:
            item_name = str(item.text(0))
            old_parent_item = item.parent()

            if direction == "up":
                new_parent = self.configuration.move_up(item_name)

                if new_parent is not None:
                    new_parent_item_list = self.tree_widget.findItems(
                        str(new_parent), QtImport.Qt.MatchRecursive, 0
                    )
                    new_parent_item = new_parent_item_list[0]

                    item_index = old_parent_item.indexOfChild(item)
                    old_parent_item.takeChild(item_index)
                    if new_parent_item == old_parent_item:
                        item_index -= 1
                        old_parent_item.insertChild(item_index, item)
                    else:
                        new_parent_item.insertChild(0, item)
            else:
                new_parent = self.configuration.move_down(item_name)

                if new_parent is not None:
                    new_parent_item_list = self.tree_widget.findItems(
                        str(new_parent), QtImport.Qt.MatchRecursive, 0
                    )
                    new_parent_item = new_parent_item_list[0]

                    item_index = old_parent_item.indexOfChild(item)
                    old_parent_item.takeChild(item_index)
                    if new_parent_item == old_parent_item:
                        item_index += 1
                        old_parent_item.insertChild(item_index, item)
                    else:
                        new_parent_item.addChild(item)

            if new_parent is not None:
                self.update_window_preview(new_parent)

            self.tree_widget.setCurrentItem(item)
            self.tree_widget.scrollToItem(item, QtImport.QAbstractItemView.EnsureVisible)
            self.moveWidgetSignal.emit(item_name, direction)

    def move_up_clicked(self):
        """Moves treewidget item up"""

        self.move_item("up")

    def move_down_clicked(self):
        """Moves treewidget item down"""
        self.move_item("down")


class GUIPreviewWindow(QtImport.QWidget):
    """Main Gui preview"""

    previewItemClickedSignal = QtImport.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QWidget.__init__(self, *args)

        self.setWindowTitle("GUI Preview")
        self.window_preview_box = QtImport.QGroupBox("Preview window", self)
        self.window_preview = GUIDisplay.WindowDisplayWidget(self.window_preview_box)

        self.window_preview_box_layout = QtImport.QVBoxLayout(self.window_preview_box)
        self.window_preview_box_layout.addWidget(self.window_preview)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.window_preview_box)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        _main_vlayout.setSpacing(2)

        self.window_preview.itemClickedSignal.connect(self.preview_item_clicked)
        self.resize(630, 480)

    def preview_item_clicked(self, item_name):
        """Item clicked"""

        self.previewItemClickedSignal.emit(item_name)

    def draw_window(self, container_cfg, window_id, container_ids, selected_item):
        """Draw gui"""

        if container_cfg["type"] == "window":
            caption = container_cfg["properties"]["caption"]
            title = caption and " - %s" % caption or ""
            self.window_preview_box.setTitle(
                "Window preview: %s%s" % (container_cfg["name"], title)
            )

        self.window_preview.draw_preview(
            container_cfg, window_id, container_ids, selected_item
        )

    def update_window(self, container_cfg, window_id, container_ids, selected_item):
        """Updates gui"""

        if container_cfg["type"] == "window":
            caption = container_cfg["properties"]["caption"]
            title = caption and " - %s" % caption or ""
            self.window_preview_box.setTitle(
                "Window preview: %s%s" % (container_cfg["name"], title)
            )

        self.window_preview.update_preview(
            container_cfg, window_id, container_ids, selected_item
        )

    def add_window_widget(self, window_cfg):
        """Refresh preview after adding a window"""

        self.window_preview.add_window(window_cfg)

    def remove_item_widget(self, item_widget, children_name_list):
        """Refresh preview after removing an item"""

        self.window_preview.remove_widget(item_widget, children_name_list)

    def add_item_widget(self, item_widget, parent_widget):
        """Refresh preview after adding an item"""

        self.window_preview.add_widget(item_widget, parent_widget)

    def move_item_widget(self, item_widget, direction):
        """Refresh preview after moving a widget"""

        self.window_preview.move_widget(item_widget, direction)


class GUIBuilder(QtImport.QMainWindow):
    """GUI Builder window"""

    def __init__(self, *args, **kwargs):
        """init"""

        QtImport.QMainWindow.__init__(self, *args)

        self.filename = None
        self.setWindowTitle("GUI Builder")

        self.main_widget = QtImport.QSplitter(self)
        self.setCentralWidget(self.main_widget)

        self.statusbar = self.statusBar()
        self.gui_editor_window = GUIEditorWindow(self.main_widget)
        self.toolbox_window = ToolboxWidget(self.main_widget)
        self.log_window = LogViewBrick.LogViewBrick(None)
        self.log_window.setWindowTitle("Log window")
        sw = QtImport.QApplication.desktop().screen().width()
        sh = QtImport.QApplication.desktop().screen().height()
        self.log_window.resize(QtImport.QSize(sw * 0.8, sh * 0.2))
        self.property_editor_window = PropertyEditorWindow(None)
        self.gui_preview_window = GUIPreviewWindow(None)
        self.configuration = self.gui_editor_window.configuration

        file_new_action = self.create_action(
            "&New...",
            self.new_clicked,
            QtImport.QKeySequence.New,
            icon="NewDocument",
            tip="Create new GUI",
        )
        file_open_action = self.create_action(
            "&Open...",
            self.open_clicked,
            QtImport.QKeySequence.Open,
            icon="OpenDoc2",
            tip="Open an existing GUI file",
        )
        file_save_action = self.create_action(
            "&Save",
            self.save_clicked,
            QtImport.QKeySequence.Save,
            icon="Save",
            tip="Save the gui file",
        )
        file_save_as_action = self.create_action(
            "Save &As...",
            self.save_as_clicked,
            icon="Save",
            tip="Save the gui file using a new name",
        )
        file_quit_action = self.create_action(
            "&Quit",
            self.quit_clicked,
            "Ctrl+Q",
            icon="Delete",
            tip="Close the application",
        )

        self.fileMenu = self.menuBar().addMenu("&File")
        self.file_menu_actions = (
            file_new_action,
            file_open_action,
            file_save_action,
            file_save_as_action,
            file_quit_action,
        )

        self.add_actions(self.fileMenu, self.file_menu_actions)

        show_propery_editor_windowAction = self.create_action(
            "Properties", self.show_property_editor_window, tip="Show properties"
        )
        show_gui_preview_action = self.create_action(
            "GUI preview", self.show_gui_preview_window, tip="GUI preview"
        )
        show_connections_action = self.create_action(
            "Connections", self.show_connection_editor, tip="Show connection editor"
        )

        show_log_windowAction = self.create_action(
            "Log", self.show_log_window, tip="Show log"
        )
        show_gui_action = self.create_action(
            "Launch GUI",
            self.launch_gui_clicked,
            tip="launch GUI (as a separate process)",
        )

        window_menu = self.menuBar().addMenu("&Window")
        window_menu_actions = (
            show_propery_editor_windowAction,
            show_gui_preview_action,
            show_connections_action,
            show_log_windowAction,
            show_gui_action,
        )
        self.add_actions(window_menu, window_menu_actions)

        self.toolbox_window.addBrickSignal.connect(self.gui_editor_window.add_brick)
        self.gui_editor_window.editPropertiesSignal.connect(
            self.property_editor_window.edit_properties
        )
        self.gui_editor_window.newItemSignal.connect(
            self.property_editor_window.add_properties
        )
        self.gui_editor_window.drawPreviewSignal.connect(
            self.gui_preview_window.draw_window
        )
        self.gui_editor_window.updatePreviewSignal.connect(
            self.gui_preview_window.update_window
        )
        self.gui_editor_window.addWidgetSignal.connect(
            self.gui_preview_window.add_item_widget
        )
        self.gui_editor_window.removeWidgetSignal.connect(
            self.gui_preview_window.remove_item_widget
        )
        self.gui_editor_window.moveWidgetSignal.connect(
            self.gui_preview_window.move_item_widget
        )
        self.gui_preview_window.previewItemClickedSignal.connect(
            self.gui_editor_window.preview_item_clicked
        )
        self.gui_editor_window.showProperyEditorWindowSignal.connect(
            self.show_property_editor_window
        )
        self.gui_editor_window.hidePropertyEditorWindowSignal.connect(
            self.hide_property_editor_window
        )
        self.gui_editor_window.showPreviewSignal.connect(self.show_gui_preview_window)

        self.toolbox_window.refresh_clicked()
        self.gui_preview_window.show()
        self.resize(480, 800)

    def create_action(
        self,
        text,
        slot=None,
        shortcut=None,
        icon=None,
        tip=None,
        checkable=False,
        signal="triggered",
    ):
        """Creates menu action"""

        action = QtImport.QAction(text, self)
        if icon is not None:
            action.setIcon(Icons.load_icon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
            # self.connect(action, QtImport.QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)

        return action

    def add_actions(self, target, actions):
        """Adds action"""

        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def new_clicked(self, filename=None):
        """Creates a new gui"""

        self.configuration = Configuration.Configuration()
        self.filename = filename

        if self.filename:
            self.setWindowTitle("GUI Builder - %s" % filename)
        else:
            self.setWindowTitle("GUI Builder")

        self.gui_editor_window.set_configuration(self.configuration)

    def open_clicked(self):
        """Open gui file"""

        filename = str(
            QtImport.QFileDialog.getOpenFileName(
                self,
                "Open file",
                os.environ["HOME"],
                "GUI file (*.gui)",
                "Choose a GUI file to open",
            )
        )

        if len(filename) > 0:
            try:
                gui_file = open(filename)
            except BaseException:
                logging.getLogger().exception("Cannot open file %s", filename)
                QtImport.QMessageBox.warning(
                    self, "Error", "Could not open file %s !" % filename, QtImport.QMessageBox.Ok
                )
            else:
                try:
                    raw_config = eval(gui_file.read())
                    try:
                        new_config = Configuration.Configuration(raw_config)
                    except BaseException:
                        logging.getLogger().exception(
                            "Cannot read configuration from file %s", filename
                        )
                        QtImport.QMessageBox.warning(
                            self,
                            "Error",
                            "\
                           Could not read configuration\nfrom file %s"
                            % filename,
                            QtImport.QMessageBox.Ok,
                        )
                    else:
                        self.filename = filename
                        self.configuration = new_config
                        self.setWindowTitle("GUI Builder - %s" % filename)
                        self.gui_editor_window.set_configuration(new_config)
                finally:
                    gui_file.close()

    def save_clicked(self):
        """Saves gui file"""

        QtImport.QApplication.setOverrideCursor(QtImport.QCursor(QtImport.Qt.WaitCursor))

        if self.filename is not None:
            if os.path.exists(self.filename):
                should_create_startup_script = False
            else:
                should_create_startup_script = True
            if self.configuration.save(self.filename):
                self.setWindowTitle("GUI Builder - %s" % self.filename)
                QtImport.QApplication.restoreOverrideCursor()
                QtImport.QMessageBox.information(
                    self,
                    "Success",
                    "Configuration have been saved "
                    + "successfully to\n%s" % self.filename,
                    QtImport.QMessageBox.Ok,
                )

                if should_create_startup_script:
                    if (
                        QtImport.QMessageBox.question(
                            self,
                            "Launch script",
                            "Do you want to create a startup script "
                            + "for the new GUI ?",
                            QtImport.QMessageBox.Yes,
                            QtImport.QMessageBox.No,
                        )
                        == QtImport.QMessageBox.Yes
                    ):
                        try:
                            hwr_server = (
                                HardwareRepository.getHardwareRepository().serverAddress
                            )
                        except BaseException:
                            hwr_server = ""
                        else:
                            pid = subprocess.Popen(
                                "newGUI --just-script %s %s"
                                % (self.filename, hwr_server),
                                shell=True,
                            ).pid
                return True
            else:
                QtImport.QApplication.restoreOverrideCursor()
                QtImport.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not save configuration to file %s !" % self.filename,
                    QtImport.QMessageBox.Ok,
                )
                return False
        else:
            QtImport.QApplication.restoreOverrideCursor()
            self.save_as_clicked()

    def save_as_clicked(self):
        """Saves gui file"""

        filename = self.filename
        name_filters = ["JSON (*.json)", "YAML (*.yml)", "PICKLE (*.gui)"]
        dialog = QtImport.QFileDialog()
        dialog.setFilter(dialog.filter() | QtImport.QDir.Hidden)
        dialog.setAcceptMode(QtImport.QFileDialog.AcceptSave)
        dialog.setNameFilters(name_filters)

        if dialog.exec_() == QtImport.QDialog.Accepted:
            self.filename = str(dialog.selectedFiles()[0])
            if not (
                self.filename.endswith(".json")
                or self.filename.endswith(".yml")
                or self.filename.endswith(".gui")
            ):

                self.filename += str(dialog.selectedNameFilter()).split("*")[1][:-1]

            return self.save_clicked()

    def quit_clicked(self):
        """Quit"""

        if (
            self.gui_editor_window.configuration.has_changed
            or self.gui_editor_window.connection_editor_window.has_changed
        ):
            if (
                QtImport.QMessageBox.warning(
                    self,
                    "Please confirm",
                    "Are you sure you want to quit ?\n" + "Your changes will be lost.",
                    QtImport.QMessageBox.Yes,
                    QtImport.QMessageBox.No,
                )
                == QtImport.QMessageBox.No
            ):
                return
        exit(0)

    def show_property_editor_window(self):
        """Shows property editor"""

        self.property_editor_window.show()

    def hide_property_editor_window(self):
        """Hides property editor"""

        self.property_editor_window.close()

    def show_gui_preview_window(self):
        """Shows gui preview"""

        self.gui_preview_window.show()

    def show_connection_editor(self):
        """Shows connection editor"""

        self.gui_editor_window.connection_editor_window.show_connections(
            self.configuration
        )
        self.gui_editor_window.connection_editor_window.show()

    def show_log_window(self):
        """Shows log"""

        self.log_window.show()

    def closeEvent(self, event):
        """Close event"""

        event.ignore()
        self.quit_clicked()

    def launch_gui_clicked(self):
        """Starts gui"""

        if self.gui_editor_window.configuration.has_changed or self.filename is None:
            if (
                QtImport.QMessageBox.warning(
                    self,
                    "GUI file not saved yet",
                    "Before starting the GUI, the file needs to "
                    + "be saved.\nContinue ?",
                    QtImport.QMessageBox.Yes,
                    QtImport.QMessageBox.No,
                )
                == QtImport.QMessageBox.No
            ):
                return

            self.save_clicked()

        terminal = os.environ["TERM"] or "xterm"

        try:
            hwr_server = HardwareRepository.getHardwareRepository().serverAddress
        except BaseException:
            logging.getLogger().error(
                "Sorry, could not find Hardware Repository server"
            )
        else:
            custom_bricks_dirs = os.path.pathsep.join(gui.get_custom_bricks_dirs())
            pid = subprocess.Popen(
                "%s -title " % terminal
                + "%s -e startGUI " % os.path.basename(self.filename)
                + "--bricksDirs=%s " % custom_bricks_dirs
                + "%s" % (hwr_server and "--hardwareRepository=%s " % hwr_server or "")
                + "%s" % self.filename,
                shell=True,
            ).pid

            logging.getLogger().debug("GUI launched, pid is %d", pid)


if __name__ == "__main__":
    app = QtImport.QApplication([])
    mainwin = GUIBuilder()
    app.setMainWidget(mainwin)
    mainwin.show()
    app.exec_loop()
