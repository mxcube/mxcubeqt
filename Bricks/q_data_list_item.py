import scdatamodel
from collections import namedtuple
from qt import QCheckListItem, QListViewItemIterator, QListView, QListViewItem
import pdb


ItemTypes = namedtuple('ItemTypes', ['SAMPLE', 'DCG', 'DC'])
ITEM_TYPES = ItemTypes(1, 2, 3)

class QDataListItem(QCheckListItem):


    def __init__(self, parent, text, _type):
        QCheckListItem.__init__(self, parent, text, _type)
        self.node_type = None
        self.data_key = None


    def activate(self):
        QCheckListItem.activate(self)
        
        if self.firstChild():
            perform_on_children(self, 
                                toggle_list_item_as_parent,
                                lambda node: True)

        if self.parent():
            parent = self.parent()

            if parent is not None:

                while not parent.isOn():
                    self.toggle_list_item_as_child(parent)
                    parent = parent.parent()
            

    def toggle_list_item_as_child(self, parent):    
        if parent:
            parent.setOn(self.isOn())


def toggle_list_item_as_parent(node):
    if node.parent():
        node.setOn(node.parent().isOn())


def do_if_checked(node):
    if type(node) is QListViewItem:
        return True
    elif type(node) is QListView:
        return True
    elif node.parent() is None:
        return node.isOn()
    elif type(node.parent()) is QListViewItem : 
        return node.isOn()
    elif node.parent().isOn() and node.isOn():
        return True


def print_text(node):
    print "Executing node: " + node.text()


def get_keys(node):
    return node.data_key


def perform_on_children(node, fun, cond):
    child_it = QListViewItemIterator(node.firstChild())

    result = []

    if(type(node) is not QListView):
        sibling = node.nextSibling()
    else:
        sibling = None

    while child_it.current():
        child = child_it.current()
    
        if(child == sibling):
            break
        elif type(child) is QDataListItem :
            if cond(child):
                result.append(fun(child))

        child_it += 1

    return result
