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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

from BlissFramework.Utils import Qt4_widget_colors


class OptimisationParametersWidgetLayout(QtGui.QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("OptimisationParametersWidgetLayout")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.opt_param_widget = uic.loadUi(os.path.join(os.path.dirname(__file__),
             "ui_files/Qt4_optimization_parameters_widget_layout.ui"))

        # Layout --------------------------------------------------------------
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.opt_param_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Size policies -------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.languageChange()
        #self.resize(QtCore.QSize(603,190).expandedTo(self.minimumSizeHint()))
        self.setAttribute(QtCore.Qt.WA_WState_Polished)

    def languageChange(self):
        self.setWindowTitle(self.__tr("OptimisationParametersWidget"))
        self.opt_param_widget.main_groupbox.\
             setTitle(self.__tr("Optimization parameters"))
        self.opt_param_widget.aimed_i_over_sigma_label.setText(\
              self.__trUtf8("\x41\x69\x6d\x65\x64\x20\x49\x2f\xcf\x83\x20" +\
                            "\x61\x74\x20\x68\x69\x67\x68\x65\x73\x74\x20" +\
                            "\x72\x65\x73\x6f\x6c\x75\x74\x69\x6f\x6e\x3a"))
        self.opt_param_widget.aimed_completeness_label.\
             setText(self.__tr("Aimed completeness:"))
        self.opt_param_widget.maximum_res_cbx.\
             setText(self.__tr("Maximum resolution:"))
        self.opt_param_widget.aimed_mult_cbx.\
             setText(self.__tr("Aimed multiplicity:"))
        self.opt_param_widget.strat_comp_label.\
             setText(self.__tr("Strategy complexity:"))
        self.opt_param_widget.start_comp_cbox.clear()
        self.opt_param_widget.start_comp_cbox.\
             addItem(self.__tr("Single subwedge"))
        self.opt_param_widget.start_comp_cbox.\
             addItem(self.__tr("Few subwedges"))
        self.opt_param_widget.start_comp_cbox.\
             addItem(self.__tr("Many subwedges"))
        self.opt_param_widget.permitted_range_cbx.\
             setText(self.__tr("Use permitted rotation range:"))
        self.opt_param_widget.phi_start_label.\
             setText(self.__trUtf8("\xcf\x89\x2d\x73\x74\x61\x72\x74\x3a"))
        self.opt_param_widget.phi_end_label.\
             setText(self.__trUtf8("\xcf\x89\x2d\x65\x6e\x64\x3a"))
        self.opt_param_widget.low_res_pass_cbx.\
             setText(self.__tr("Calculate low resolution pass strategy"))

    def __tr(self,s,c = None):
        return QtGui.QApplication.translate("OptimisationParametersWidgetLayout",s,c)

    def __trUtf8(self,s,c = None):
        return QtGui.QApplication.translate("OptimisationParametersWidgetLayout", s, c, \
                     QtGui.QApplication.UnicodeUTF8)
