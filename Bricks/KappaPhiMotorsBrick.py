import qt
import logging

from BlissFramework import Icons
from BlissFramework.BaseComponents import BlissWidget

from BlissFramework.Utils import widget_colors


__category__ = 'Motor'


class KappaPhiMotorsBrick(BlissWidget):

    STATE_COLORS = (widget_colors.LIGHT_RED, 
                    widget_colors.DARK_GRAY,
                    widget_colors.LIGHT_GREEN,
                    widget_colors.LIGHT_YELLOW,  
                    widget_colors.LIGHT_YELLOW,
                    widget_colors.LIGHT_YELLOW)

    MAX_HISTORY = 20

    def __init__(self,*args):
        BlissWidget.__init__(self,*args)

        self.diffractometer_hwobj=None

        self.addProperty('mnemonic','string','')
        self.addProperty('label','string','')
        self.addProperty('showLabel', 'boolean', True)
        self.addProperty('showBox', 'boolean', True)
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('icons', 'string', '')

        self.container_hbox = qt.QHGroupBox(self)
        self.container_hbox.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)

        self.label_hbox = qt.QHBox(self.container_hbox)
        self.motor_hbox = qt.QHBox(self.container_hbox)

        self.label = qt.QLabel(self.label_hbox)

        self.kappa_value_edit = qt.QLineEdit(self.motor_hbox)
        self.kappa_value_edit.setFixedSize(qt.QSize(55,25))
        self.kappa_value_edit.setValidator(qt.QDoubleValidator(0, 180, 2, self))
        self.kappa_value_edit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.kappa_value_edit.setAlignment(qt.QWidget.AlignRight)
        self.phi_value_edit = qt.QLineEdit(self.motor_hbox)
        self.phi_value_edit.setFixedSize(qt.QSize(55,25))
        self.phi_value_edit.setValidator(qt.QDoubleValidator(0, 180, 2, self))
        self.phi_value_edit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.phi_value_edit.setAlignment(qt.QWidget.AlignRight)

        self.move_motors_button = qt.QPushButton("Apply", self.motor_hbox)  
        self.stop_motors_button = qt.QPushButton(self.motor_hbox)
        self.stop_motors_button.setPixmap(Icons.load('stop_small'))
        self.stop_motors_button.setEnabled(False)

        self.connect(self.kappa_value_edit, qt.SIGNAL('textChanged(const QString &)'), self.kappa_edit_input_changed)
        self.connect(self.phi_value_edit, qt.SIGNAL('textChanged(const QString &)'), self.phi_edit_input_changed)
        self.connect(self.move_motors_button, qt.SIGNAL('clicked()'), self.move_motors_button_clicked)
        self.connect(self.stop_motors_button, qt.SIGNAL('clicked()'), self.stop_motors_button_clicked)  
       
        self.stop_motors_button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Minimum)
        self.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)
        qt.QVBoxLayout(self)
        self.layout().addWidget(self.container_hbox)
        
    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='mnemonic':
            if self.diffractometer_hwobj is not None:
                self.disconnect(self.diffractometer_hwobj, qt.PYSIGNAL("kappaMoved"), self.kappa_value_changed) 
                self.disconnect(self.diffractometer_hwobj, qt.PYSIGNAL("kappPhiMoved"), self.phi_value_changed)
            self.diffractometer_hwobj = self.getHardwareObject(newValue)
            if self.diffractometer_hwobj is not None:
                self.connect(self.diffractometer_hwobj, qt.PYSIGNAL("kappaMoved"), self.kappa_value_changed)            
                self.connect(self.diffractometer_hwobj, qt.PYSIGNAL("kappaPhiMoved"), self.phi_value_changed)
        elif propertyName=='label':
            self.setLabel(newValue)
        elif propertyName=='showLabel':
            if newValue:
                self.setLabel(self['label'])
            else:
                self.setLabel(None)
        elif propertyName=='showStop':
            if newValue:
                self.stop_motors_button.show()
            else:
                self.stop_motors_button.hide()
        elif propertyName=='showBox':
            if newValue:
                self.container_hbox.setFrameShape(self.container_hbox.GroupBoxPanel)
                self.container_hbox.setInsideMargin(4)
                self.container_hbox.setInsideSpacing(0)
            else:
                self.container_hbox.setFrameShape(self.container_hbox.NoFrame)
                self.container_hbox.setInsideMargin(0)
                self.container_hbox.setInsideSpacing(0)            
            self.setLabel(self['label'])
        elif propertyName=='icons':
            icons_list=newValue.split()
            try:
                self.move_motors_button.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass                
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def stop_motors_button_clicked(self):
        self.diffractometer_hwobj.stop_kappa_phi()

    def move_motors_button_clicked(self):
        kappa_value = float(self.kappa_value_edit.text())
        phi_value = float(self.phi_value_edit.text())
        self.diffractometer_hwobj.move_kappa_phi(kappa_value, phi_value)

        self.kappa_value_edit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.kappa_value_edit.clearFocus()
        self.phi_value_edit.setPaletteBackgroundColor(widget_colors.LIGHT_GREEN)
        self.phi_value_edit.clearFocus()

    def kappa_edit_input_changed(self, new_text):
        self.kappa_value_edit.setPaletteBackgroundColor(qt.QColor(255,165,0))

    def phi_edit_input_changed(self, new_text):
        self.phi_value_edit.setPaletteBackgroundColor(qt.QColor(255,165,0))

    def kappa_value_changed(self, value):
        self.kappa_value_edit.blockSignals(True)
        txt = '?' if value is None else '%s' %\
              str(self['formatString'] % value)
        self.kappa_value_edit.setText(txt)
        self.kappa_value_edit.blockSignals(False)
    
    def phi_value_changed(self, value):
        self.phi_value_edit.blockSignals(True)
        txt = '?' if value is None else '%s' %\
              str(self['formatString'] % value)
        self.phi_value_edit.setText(txt)
        self.phi_value_edit.blockSignals(False)

    def setLabel(self,label):
        if not self['showLabel']:
            label=None

        if label is None:
            self.label_hbox.hide()
            self.container_hbox.setTitle("")
            return

        if self['showBox']:
            self.label_hbox.hide()
            self.container_hbox.setTitle(label)
        else:
            if label!="":
                label+=": "
            self.container_hbox.setTitle("")
            self.label.setText(label)
            self.label_hbox.show()

