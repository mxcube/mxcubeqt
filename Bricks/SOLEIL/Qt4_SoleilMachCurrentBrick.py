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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = 'SOLEIL'



class Qt4_SoleilMachCurrentBrick(BlissWidget):
    """
    Descript. :
    """
    STATES = {
        'unknown': Qt4_widget_colors.GRAY,
        'ready': Qt4_widget_colors.LIGHT_BLUE,
        'error': Qt4_widget_colors.LIGHT_RED
        }
    
    UND_STATES = {
        'SLOW': Qt4_widget_colors.GREEN,
        'FAST': QtGui.QColor("#ff8c00"),  # orange
        'SCANNING': Qt4_widget_colors.RED,
        'ERROR': Qt4_widget_colors.RED,
        'UNKNOWN': Qt4_widget_colors.DARK_GRAY,
    }

    UND_TIPS = {
        'SLOW': "Undulator is in SLOW variation Mode\n\nThis is the standard mode for data collection",
        'FAST':  "Undulator current FAST variation Mode\n\n Big intensity fluctuations COULD affect your data quality", 
        'SCANNING': "Undulator is being SCANNED.\n\nBig intensity fluctuations will CERTAINLY affect your data quality",
        'ERROR': "Undulator error detected while reading",  
        'UNKNOWN':  "Cannot get undulator information",
    }
          
    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.mach_info_hwobj = None
        self.machCurrent=None
        self.undulator=None

        # Internal values -----------------------------------------------------
        self.last_value = None

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '###.#')
        self.addProperty('diskThreshold', 'float', '200')
                
        self.addProperty('undulator','string','')

        self.addProperty('currentThreshold', 'float', 1.0)
        self.defineSignal('operatorMessage',())

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('setColDir', ())
        pathfile = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
        self.mac_widget = uic.loadUi(os.path.join(pathfile,
                               "widgets/ui_files/Qt4_soleil_machine_current.ui"))
        """
        self.containerBox=QtGui.QGroupBox("Soleil machine current",self)

        self.current=QtGui.QLabel(self.containerBox)
        self.current.setAlignment(QtGui.QLabel.AlignCenter)
        self.current.setStyleSheet(_fromUtf8("background-color: rgb(255, 0, 0);\n"
            "color: rgb(255, 255, 255);"))
        #font=self.current.font()
        #font.setStyleHint(QtGui.QFont.OldEnglish)
        #self.current.setFont(font)
        self.mode=QtGui.QLabel(self.containerBox)
        self.mode.setAlignment(QtCore.Qt.AlignCenter)
        self.mode.setStyleSheet(_fromUtf8("background-color: rgb(85, 255, 255);"))

        self.refillCountdown=QtGui.QLabel(self.containerBox)
        self.refillCountdown.setAlignment(QtCore.Qt.AlignCenter)
        #self.refillCountdown.setFont(bold_font)
        #self.refillCountdown.setSegmentStyle(QLCDNumber.Flat)

        #self.containerBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.minimum, QtGui.QSizePolicy.Fixed))
        
        QtGui.QVBoxLayout(self)
        self.layout().addWidget(self.containerBox)
        """
        self.mac_widget.current.setToolTip("Current machine current")
        self.mac_widget.mode.setToolTip("Fill mode")
        self.mac_widget.refillCountdown.setToolTip("Life time")
        
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addWidget(self.mac_widget)
        

    def setValue(self,value,opmsg,fillmode,refill):
        #logging.getLogger().info(" new value for machine current is: \n\t%s\n\t%s\n\t%s\n\t%s " % (str(value), str(opmsg), str(fillmode), str(refill)))
        if value is None:
            value=self.lastValue
        else:
            self.lastValue=value

        self.mac_widget.current.setText("")
        if value is None:
            self.setStateColor('unknown')
            self.mac_widget.current.setText("???.? mA")
        else:
            if value<self['currentThreshold']:
                self.setStateColor('error')
            else:
                self.setStateColor('ready')
            svalue = '<b>%s</b> mA' % str(self['formatString'] % value)
            self.mac_widget.current.setText(svalue)

        if fillmode is not None and fillmode!="":
            self.mac_widget.mode.setText("<i>%s</i>" % fillmode)

        #<modif pierre.L 18.03.08
	#try:
        #    refill_secs=int(refill)
        #    if refill_secs>=0:
        #        ts=time.gmtime(refill_secs)
        #        txt=time.strftime("%H:%M",ts)
        #    else:
        #        txt="00:00"
        #    self.refillCountdown.display(txt)
        #except TypeError,ValueError:
        #    pass
        #>modif pierre.L 18.03.08        
        #<modif pierre.L 23.03.10
        #try:
        #    lifetime_h=int(refill)
        #    lifetime_m=(refill-lifetime_h)*100
        #    if refill>=0:
        #        txt="%d:%d" % (lifetime_h,lifetime_m)
        #    else:
        #        txt="00:00"
        #    self.refillCountdown.display(txt)
        #except TypeError,ValueError:
        #    pass
        #<modif pierre.L 23.03.10
        try:
            #self.refillCountdown.display(str(refill))
            self.mac_widget.refillCountdown.setText(refill)
        except TypeError,ValueError:
            pass        
        
        if opmsg is not None and opmsg!="" and opmsg!="unknown":
            self.mac_widget.current.setToolTip(opmsg)
            #self.emit(PYSIGNAL("operatorMessage"),(opmsg[:10],))

    def setStateColor(self,state):
        color=self.STATES[state]
        #self.current.setPaletteBackgroundColor(QColor(color))

    def fontChange(self,oldFont):
        font=self.font()
        size=font.pointSize()
        font.setPointSize(2*size)
        self.mac_widget.current.setFont(font)
    
    def updateUndulator(self,und_state,scanning):

        if scanning: 
           state = "SCANNING"
        else:
           state = und_state


        if state not in self.UND_STATES:
           state = "UNKNOWN"

        label = state
         
        tip = self.UND_TIPS[state]
        color = self.UND_STATES[state]

        self.mac_widget.undulator_label.setText(label)
        Qt4_widget_colors.set_widget_color(self.mac_widget.undulator_label,
                                           color)
        #self.undulator_label.setPaletteBackgroundColor(QColor(color))
        self.mac_widget.undulator_label.setToolTip(tip)
        
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.machCurrent is not None:
                self.disconnect(self.machCurrent,'valueChanged',self.setValue)
                #self.disconnect(self.machCurrent,PYSIGNAL('timeout'),self.setValue)

            self.machCurrent=self.getHardwareObject(newValue)

            if self.machCurrent is not None:
                ret = self.machCurrent.updatedValue()
                if ret:
                    mach, opmsg, fillmode, refill  = ret
                    self.setValue(value=mach, opmsg=opmsg, fillmode=fillmode, refill=refill)

                #self.containerBox.setEnabled(True)
                self.connect(self.machCurrent,'valueChanged',self.setValue)
                #self.connect(self.machCurrent,PYSIGNAL('timeout'),self.setValue)
            else:
                pass
                #self.containerBox.setEnabled(False)
        elif propertyName=='undulator':
            if self.undulator is not None:
                self.disconnect(self.undulator,'valueChanged',self.updateUndulator)

            self.undulator=self.getHardwareObject(newValue)

            if self.undulator is not None:
                self.connect(self.undulator,'valueChanged',self.updateUndulator)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)