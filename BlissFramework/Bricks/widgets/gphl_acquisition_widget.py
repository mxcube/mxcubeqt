"""GPhL bespoke input widget. Built from DataCollectParametersWidget"""


from qt import *
import time
import os
# from BlissFramework import Icons
from BlissFramework.Bricks.DataCollectParametersWidget import CheckBoxInput
# from BlissFramework.Bricks.DataCollectParametersWidget import ComboBoxInput
from BlissFramework.Bricks.DataCollectParametersWidget import LineEditInput
from BlissFramework.Bricks.DataCollectParametersWidget import HorizontalSpacer
import logging

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class GphlAcquisitionWidget(QWidget):

    _energy_tags = ('energy_1', 'energy_2', 'energy_3', 'energy_4',)

    PARAMETERS = {
        # "detector_resolution":("Detector resolution (A) ", 0, 0, 0, LineEditInput,
        #                      (), QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
        "expected_resolution":("Expected resolution (A) ", 0, 0, 0, LineEditInput,
                             (), QWidget.AlignLeft, (QDoubleValidator,0.01), ()),
        # "char_energy":("Characterisation ", 3, 0, 0, LineEditInput,(),
        #                QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
        "energy_1":("First beam energy", 2, 0, 0, LineEditInput, (),
              QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
        "energy_2":("Second beam energy", 3, 0, 0, LineEditInput, (),
              QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
        "energy_3":("Third beam energy", 4, 0, 0, LineEditInput, (),
               QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
        "energy_4":("Fourth beam energy", 5, 0, 0, LineEditInput, (),
               QWidget.AlignLeft, (QDoubleValidator,0.0), ()),
    }

    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        self._parameter_box = QWidget(parent)
        QGridLayout(self._parameter_box, 8, 3)
        self._parameter_box.layout().setColStretch(2, 1)

        self._label_dict = {}
        self._parameter_dict = {}
        self._beam_energy_map = OrderedDict()
        # self.setup_parameter_widget('detector_resolution',
        #                             self.PARAMETERS['detector_resolution'])
        wdg = self.setup_parameter_widget(
            'expected_resolution', self.PARAMETERS['expected_resolution']
        )
        wdg.setText('0.0')
        label = QLabel("Beam energies (keV):", self._parameter_box)
        self._parameter_box.layout().addWidget(label, 1, 0,)
        self._label_dict['_beam_energies_label'] = label
        # self.setup_parameter_widget('char_energy',
        #                             self.PARAMETERS['char_energy'])
        for tag in self._energy_tags:
            self._beam_energy_map[tag] = None
            self.setup_parameter_widget(tag, self.PARAMETERS[tag])

    def setup_parameter_widget(self, param_id, values):
        param_label=values[0]
        param_row=values[1]
        param_column=values[2]
        param_span=values[3]
        param_class=values[4]
        param_class_args=list(values[5])
        param_class_align=values[6]
        param_class_validator=values[7]
        connect_signals=values[8]

        if param_label:
            label=QLabel("%s:" % param_label, self._parameter_box)
            self._parameter_box.layout().addWidget(label, param_row, param_column)
            self._label_dict[param_id]=label
        param_class_args.append(self._parameter_box)
        input_widget=param_class(*param_class_args)
        if param_class_align is not None:
            input_widget.setAlignment(param_class_align)
        if param_class_validator is not None:
            class_validator=param_class_validator[0]
            validator=class_validator(input_widget)
            try:
                validator_bottom=param_class_validator[1]
            except IndexError:
                pass
            else:
                validator.setBottom(validator_bottom)
            input_widget.setValidator(validator)
        self._parameter_box.layout().addMultiCellWidget(input_widget, param_row, param_row, param_column + 1, param_column + 1 + param_span)
        self._parameter_dict[param_id]=input_widget

        try:
            connect_on_changed=connect_signals[0]
        except IndexError:
            connect_on_changed=None
        if connect_on_changed=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('textChanged(const QString &)'), self.%sChanged)" % param_id)
        elif connect_on_changed=="PYSIGNAL":
            exec("QObject.connect(input_widget, PYSIGNAL('textChanged'), self.%sChanged)" % param_id)
        try:
            connect_on_return=connect_signals[1]
        except IndexError:
            connect_on_return=None
        if connect_on_return=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('returnPressed()'), self.%sPressed)" % param_id)
        elif connect_on_return=="PYSIGNAL":
            exec("QObject.connect(input_widget, PYSIGNAL('returnPressed'), self.%sPressed)" % param_id)
        try:
            connect_on_activated=connect_signals[2]
        except IndexError:
            connect_on_activated=None
        if connect_on_activated=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('activated(int)'), self.%sActivated)" % param_id)
        elif connect_on_activated=="PYSIGNAL":
            exec("QObject.connect(input_widget, PYSIGNAL('activated'), self.%sActivated)" % param_id)
        try:
            connect_on_toggled=connect_signals[3]
        except IndexError:
            connect_on_toggled=None
        if connect_on_toggled=="SIGNAL":
            exec("QObject.connect(input_widget, SIGNAL('toggled(bool)'), self.%sToggled)" % param_id)
        elif connect_on_toggled=="PYSIGNAL":
            exec("QObject.connect(input_widget, PYSIGNAL('toggled'), self.%sToggled)" % param_id)

        return input_widget

    #
    def get_parameter_value(self, param_id):
        try:
            param=self._parameter_dict[param_id]
        except KeyError:
            return None
        if param.isVisible():
            return param.text()
        else:
            return None

    def setEnabled(self, value):
        super(GphlAcquisitionWidget, self).setEnabled(value)
        for widget in self._parameter_dict.values():
            widget.setEnabled(value)

    def set_parameter_enabled(self, tag, value):
        param = self._parameter_dict.get(tag)
        if param:
            if hasattr(param, 'setReadOnly'):
                param.setReadOnly(not(value))
            else:
                param.setEnabled(value)
        else:
            raise ValueError("GPhL: No parameter widget called %s" % tag)

    def display_energy_widgets(self, energies_dict):
        """energies is a role:value ORDERED dictionary"""
        tuples = tuple(energies_dict.items())
        for ii, tag in enumerate(self._beam_energy_map):


            if ii < len(energies_dict):
                role, energy = tuples[ii]
                self._beam_energy_map[tag] = role
                label = self._label_dict[tag]
                label.setText("      %s energy:" % role)
                param = self._parameter_dict[tag]
                param.setText(str(energy))
                label.show()
                param.show()
            else:
                self._beam_energy_map[tag] = None
                self._parameter_dict[tag].hide()
                self._label_dict[tag].hide()
        if energies_dict:
            self._label_dict['_beam_energies_label'].show()
        else:
            self._label_dict['_beam_energies_label'].hide()


    def get_parameter_dict(self):
        params={}
        for param_id in self.PARAMETERS:
            param = self._parameter_dict[param_id]
            if param.isVisible():
                if param.hasAcceptableInput():
                    text=self._parameter_dict[param_id].text()
                else:
                    text=None
                params[param_id]=text
        return params

    def get_validation_dict(self):
        params={}
        for param_id in self.PARAMETERS:
            if self._parameter_dict[param_id].hasAcceptableInput():
                valid=True
            else:
                valid=False
            params[param_id]=valid
        return params

    def set_param_value(self, name, value):
        param = self._parameter_dict.get(name)
        if param is None:
            raise ValueError(
                "GPhL acquisition widget has no parameter named %s" % name
            )
        elif isinstance(param, LineEditInput):
            if value is None:
                value = ''
            param.setText(str(value))
        elif isinstance(param, CheckBoxInput):
            is_on, label, text = value
            param.setInputText(text)
            param.setLabelText(label)
            param.setChecked(is_on)
        else:
            raise NotImplementedError(
                "Parameter value setting not implemented for %s"
                % param.__class__.__name__)

