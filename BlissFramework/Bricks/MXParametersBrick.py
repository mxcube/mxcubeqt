from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
import parameter_table_widget
import logging
import sys
import pprint
pp = pprint.PrettyPrinter(indent=4, depth=10)

__category__ = 'mxCuBE'

class MXParametersBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        reload(parameter_table_widget)
    
##         self.defineSignal("add_data_collection", {})
##         self.defineSlot("create_collection",())
        self.defineSlot("populate_parameter_table",({}))
        
        self.parameters_table = parameter_table_widget.ParametersTable(self)
##        self.parameters_table.add_dc_cb = self.add_data_collection
        self.parameters_table.collection_type = None

        QVBoxLayout(self)
        self.layout().addWidget(self.parameters_table)


    def populate_parameter_table(self, parameters):
        self.parameters_table.populate_parameter_table(parameters)


##     def add_data_collection(self, parameters, collection_type):
##         self.emit(PYSIGNAL("add_data_collection"), (parameters,
##                                                     self.parameters_table.collection_type))
        

##     def create_collection(self, positions, collection_type):
##         self.parameters_table.collection_type = collection_type
##         f_pos = pp.pformat(positions)
##         self.parameters_table.position_label.\
##             setText("Positions used: " + f_pos)
##         self.parameters_table.add_positions(positions)
