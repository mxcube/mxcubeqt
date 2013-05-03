from scdatamodel import SCDataModel
# TODO: Refactor perform_on_children
from q_data_list_item import QDataListItem, ITEM_TYPES, perform_on_children, print_text, get_keys, do_if_checked
from position_history_widget import COLLECTION_TYPE, COLLECTION_TYPE_NAME
from qt import *
from qttable import QTable, QTableItem
from copy import deepcopy
import pprint
import logging
pp = pprint.PrettyPrinter(indent=4, depth=10)
pp.isrecursive(dict)

class DataCollectTree(QWidget):
    def __init__(self, parent = None, name = "data_collect", 
                 selection_changed=None):
        QWidget.__init__(self, parent, name)
        
        self.data_model = SCDataModel()
        self.selection_changed_cb = None

        self.up_button = QPushButton(self, "up_button")
        self.delete_button = QPushButton(self, "delete_button")
        self.delete_button.setDisabled(True)
        self.down_button = QPushButton(self, "down_button")
        
        self.run_button = QPushButton(self, "run_button")

        self.sample_list_view = QListView(self, "sample_list_view")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Expanding))   
        self.sample_list_view.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                        QSizePolicy.Expanding)) 
    
        self.sample_list_view.setSorting(-1)
        self.sample_list_view.addColumn(QString.null, 250)
        self.sample_list_view.addColumn("Sample code", -1)
        self.sample_list_view.header()\
            .setClickEnabled(0,self.sample_list_view.header().count() - 1)
        self.sample_list_view.header()\
            .setResizeEnabled(0,self.sample_list_view.header().count() - 1)
        self.sample_list_view.header().hide()

        self.sample_list_view.setFrameShape(QListView.StyledPanel)
        self.sample_list_view.setFrameShadow(QListView.Sunken)
        self.sample_list_view.setRootIsDecorated(1)
        self.sample_list_view.setSelected(self.sample_list_view.firstChild(), True)
        
        self.languageChange()

        layout = QVBoxLayout(self)
        layout.addWidget(self.sample_list_view)
        self.buttons_grid_layout = QGridLayout(self, 2, 5)
        layout.addLayout(self.buttons_grid_layout)
        self.buttons_grid_layout.addWidget(self.up_button,0, 0)
        self.buttons_grid_layout.addWidget(self.down_button,0, 1)
        self.buttons_grid_layout.addWidget(self.delete_button, 0, 4)
        self.buttons_grid_layout.addWidget(self.run_button, 1, 0)
        
        self.clearWState(Qt.WState_Polished)

        QObject.connect(self.up_button, SIGNAL("clicked()"),
                        self.__up_click)

        QObject.connect(self.down_button, SIGNAL("clicked()"),
                         self.__down_click)

        QObject.connect(self.delete_button, SIGNAL("clicked()"),
                        self.__delete_click)
        
        QObject.connect(self.run_button, SIGNAL("clicked()"),
                        self.__run)

        QObject.connect(self.sample_list_view, 
                        SIGNAL("selectionChanged(QListViewItem*)"),
                        self.__sample_list_view_selection)

                        
    def __sample_list_view_selection(self, item):
        
        if type(item) is QDataListItem and \
                item.node_type == ITEM_TYPES.SAMPLE or \
                item.node_type == ITEM_TYPES.DCG:
            pass
            #self.add_button.setDisabled(False)

        current_dc = {}

        if type(item) is QDataListItem and \
                item.node_type == ITEM_TYPES.DC:

            #self.add_button.setDisabled(True)

            current_dc = self.data_model.\
                get_data_collection(item.parent().parent().data_key,
                                    item.parent().data_key,
                                    item.data_key)

            current_dc = current_dc['parameters']
            
        if type(item) is QDataListItem and \
               ( item.node_type == ITEM_TYPES.DCG or \
                 item.node_type == ITEM_TYPES.DC ):

            self.delete_button.setDisabled(False)
        else:
            self.delete_button.setDisabled(True)

        self.selection_changed_cb(item, current_dc)
        

    def __get_group_count(self, parent, collection_type):
        child_it = QListViewItemIterator(parent.firstChild())

        result = 0

        if(type(parent) is not QListView):
            sibling = parent.nextSibling()
        else:
            sibling = None

        while child_it.current():
            child = child_it.current()
            
            if(child == sibling):
                break
            elif type(child) is QDataListItem :
                if str(child.text(0)).find(COLLECTION_TYPE_NAME[collection_type]) != -1:
                    result += 1

            child_it += 1

        return result


    def __add_dg(self, parent_node, collection_type):
        group_num = str(self.__get_group_count(parent_node, collection_type) + 1)
        group_key = parent_node.data_key + ':' + group_num
        
        self.data_model.add_data_collection_group(parent_node.data_key,
                                                  group_key, {})
        
        group = QDataListItem(parent_node,
                              COLLECTION_TYPE_NAME[collection_type] + ' ' + group_num, 
                              QCheckListItem.CheckBox)
        group.node_type = ITEM_TYPES.DCG
        group.data_key = group_key
        group.setOpen(True)

        return group


    def __add_dc(self, parent_node, parameters):
        collection_num = str(parent_node.childCount() + 1)
        group_key = parent_node.data_key
        sample_key = parent_node.parent().data_key
        collection_key = group_key + ':' + collection_num

        self.data_model.add_data_collection(sample_key, group_key, 
                                            collection_key, 
                                            deepcopy(parameters))
                
        collection = QDataListItem(parent_node,
                                   'Data collection ' + collection_num,
                                           QCheckListItem.CheckBox)
        collection.node_type = ITEM_TYPES.DC
        collection.data_key = collection_key
        

    def add_data_collection(self, parameters, collection_type):
        selected_item = self.sample_list_view.selectedItem()
        
        if selected_item != 0 and type(selected_item) is QDataListItem:

            if selected_item.node_type == ITEM_TYPES.SAMPLE:          
                group_node = self.__add_dg(selected_item, collection_type)
                self.__add_dc(group_node, parameters)
                

            if selected_item.node_type == ITEM_TYPES.DCG:
                self.__add_dc(selected_item, parameters)
                
            selected_item.setOpen(True)
            pp.pprint(self.data_model)


    def get_selected_item(self):
        return self.sample_list_view.selectedItem()
    
    def __run(self):
        #perform_on_children(self.sample_list_view, print_text, do_if_checked)
        return self.get_checked_collections()


    def get_checked_collections(self):
        keys = perform_on_children(self.sample_list_view, get_keys, do_if_checked)
        
        if len(keys) > 2:
            c = []
            sample_key = keys[0]
            group_key = keys[1]

            for key in keys[2:]:
                c.append(self.data_model.get_data_collection(sample_key,
                                                             group_key,
                                                             key))
        return c
        

    def __delete_click(self):
        selected_item = self.sample_list_view.selectedItem()

        if(selected_item != 0 and type(selected_item) is QDataListItem):
           
           if selected_item.node_type == ITEM_TYPES.DCG:
               sample_key = selected_item.parent().data_key
               group_key = selected_item.data_key

               self.data_model.remove_data_collection_group(sample_key, 
                                                               group_key)

           if selected_item.node_type == ITEM_TYPES.DC:
               sample_key = selected_item.parent().parent().data_key
               group_key = selected_item.parent().data_key
               collection_key = selected_item.data_key

               self.data_model.remove_data_collection(sample_key, 
                                                         group_key,
                                                         collection_key)                   
                   
           selected_item.parent().takeItem(selected_item)

           pp.pprint(self.data_model)

    def __down_click(self):
        selected_item = self.sample_list_view.selectedItem()

        if(selected_item != 0 and type(selected_item) is QDataListItem):
            if selected_item.nextSibling() != 0 :
                selected_item.moveItem(selected_item.nextSibling())


    def __previous_sibling(self, item):
        if item.parent():
            first_child = item.parent().firstChild()
        else:
            first_child = item.listView().firstChild() 

        if first_child is not item :
            sibling = first_child.nextSibling()   
        
            while sibling:           
                if sibling is item :
                    return first_child
                elif sibling.nextSibling() is item:
                    return sibling
                else:
                    sibling = sibling.nextSibling()
        else :
            return None
        

    def __up_click(self):
        selected_item = self.sample_list_view.selectedItem()

        if(selected_item != 0 and type(selected_item) is QDataListItem):
            older_sibling = self.__previous_sibling(selected_item)
        
            if older_sibling :
                older_sibling.moveItem(selected_item)
        

    def languageChange(self):
        self.setCaption(self.__tr("Data collect"))
        self.up_button.setText(self.__tr("UP"))
        self.delete_button.setText(self.__tr("DEL"))
        self.down_button.setText(self.__tr("DN"))
        self.run_button.setText(self.__tr("Run"))
        self.sample_list_view.header().setLabel(0,QString.null)
    
            
    def init_with_sc_content(self, sc_content):

        self.sample_list_view.clear()
        
        for sample_info in sc_content:

            self.data_model.add_sample(str(sample_info[1]) + ':' + \
                                         str(sample_info[2])  ,sample_info)

            item = QDataListItem(self.sample_list_view, 
                                 str(sample_info[1]) + ':' + \
                                     str(sample_info[2]), 
                                 QCheckListItem.CheckBox)

            item.setText(1, str(sample_info[0]))
            item.node_type = ITEM_TYPES.SAMPLE
            item.data_key = str(sample_info[1]) + ':' + str(sample_info[2])


    def init_with_sample(self, data):

        self.sample_list_view.clear()
        
        for sample_info in data:

            self.data_model.add_sample(str(sample_info[1]), sample_info)

            item = QDataListItem(self.sample_list_view, 
                                 str(sample_info[0]), 
                                 QCheckListItem.CheckBox)

            item.node_type = ITEM_TYPES.SAMPLE
            item.data_key = str(sample_info[1])


    def init_with_ispyb_data(self, data):
        self.sample_list_view.clear()


    def __select_mounted_sample(self, sc_data):

        k = 0
        for sample_info in sc_data:
            if sample_info[4] == 16:
                return k
            k += 1

            
    def __tr(self,s,c = None):
        return qApp.translate("data_collect", s, c)

#def ispyb_create_list_items(node, parent_list_view):
#    if type(node) is dict :
#        for child_key in node :
#            create_list_items(node[child_key], 
#                              QDataListItem(parent_list_view, child_key,
#                                  QCheckListItem.CheckBox))    

# ispyb_content = {
#     'ProtA' : {
#         'xtal1':'',
#         'xtal2': '',
#         'xtal3': '',
#         },
#     'ProtB' : {
#         'xtal1':'',
#         'xtal2': '',
#         'xtal3': '',        
#         },
#     'ProtC' : { 
#         'xtal1':'',
#         'xtal2': '',
#         'xtal3': '',
#         }
#     }
