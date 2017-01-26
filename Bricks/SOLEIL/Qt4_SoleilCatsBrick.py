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

import os
import logging

from QtImport import *
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'SOLEIL'
__author__ = 'Laurent GADEA'
__version__ = '1.0'


class Qt4_SoleilCatsBrick(BlissWidget):
    """
    Descript. :
    """
    
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)
        
        pathfile = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "."))
        self.widget = loadUi(os.path.join(os.path.dirname(__file__),
                                 "widgets/ui_files/Qt4_soleil_cats_widget.ui"))
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.widget)
        
        # Hardware objects ----------------------------------------------------
        self._hwobj = None
        # Internal values -----------------------------------------------------
        # Properties ----------------------------------------------------------
        self.addProperty("hwobj", "string", "")
        self.addProperty('mnemonic', 'string', '')
        # Signals -------------------------------------------------------------
    
        # Slots ---------------------------------------------------------------
    
        # Connect -------------------------------------------------------------
        
        
    def setValue(self):
        pass
    

    def propertyChanged(self,propertyname,oldValue,newValue):
        #logging.getLogger("user_level_log").info("QT4_CatsMaint property Changed: " + str(property) + " = " + str(newValue))
        BlissWidget.propertyChanged(self,propertyname,oldValue,newValue)
    
    
        
   
