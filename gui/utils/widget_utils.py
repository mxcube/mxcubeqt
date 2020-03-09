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


from gui.utils import Colors, QtImport
from HardwareRepository.dispatcher import dispatcher
from HardwareRepository.ConvertUtils import string_types


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class DataModelInputBinder(object):
    def __init__(self, obj):
        object.__init__(self)
        self.__model = obj

        # Key - field name/attribute name of the persistant object.
        # Value - The tuple (widget, validator, type_fn)
        self.bindings = {}
        dispatcher.connect(self._update_widget, "model_update", dispatcher.Any)

    def __checkbox_update_value(self, field_name, new_value):
        setattr(self.__model, field_name, new_value)
        dispatcher.send("model_update", self.__model, field_name, self)

    def __combobox_update_value(self, field_name, new_value):
        setattr(self.__model, field_name, new_value)
        dispatcher.send("model_update", self.__model, field_name, self)

    def __ledit_update_value(self, field_name, widget, new_value, type_fn, validator):
        if not self.bindings[field_name][3]:
            origin_value = new_value
            if type_fn == float and validator:
                pattern = "%." + str(validator.decimals()) + "f"
                new_value = pattern % float(new_value)

            # fix validation if PyQt4 and sipapi 1 is used
            if isinstance(new_value, string_types):
                if "QString" in globals():
                    new_value = QtImport.QString(new_value)

            self.__validated(
                field_name, validator, self.bindings[field_name][0], new_value
            )
            if isinstance(widget, QtImport.QLineEdit):
                if type_fn is float and validator:
                    widget.setText(
                        "{:g}".format(
                            round(float(origin_value), validator.decimals())
                        )
                    )
            try:
                setattr(self.__model, field_name, type_fn(origin_value))
            except ValueError:
                if origin_value != "":
                    raise
            else:
                dispatcher.send("model_update", self.__model, field_name, self)

    def __ledit_text_edited(self, field_name, widget, new_value, type_fn, validator):
        self.bindings[field_name][3] = True
        if self.__validated(
            field_name, validator, self.bindings[field_name][0], new_value
        ):
            try:
                setattr(self.__model, field_name, type_fn(new_value))
            except ValueError:
                if new_value != "":
                    raise
            else:
                dispatcher.send("model_update", self.__model, field_name, self)

    def __validated(self, field_name, validator, widget, new_value):
        if validator:
            try:
                flt_value = float(new_value)
            except BaseException:
                Colors.set_widget_color(
                    widget, Colors.LIGHT_RED, QtImport.QPalette.Base
                )
                return False

            if flt_value >= min(
                validator.bottom(), validator.top()
            ) and flt_value <= max(validator.bottom(), validator.top()):
                # if validator.validate(new_value, widget.cursorPosition())[0] \
                #        == QValidator.Acceptable:
                if self.bindings[field_name][3]:
                    Colors.set_widget_color(
                        widget, Colors.LIGHT_YELLOW, QtImport.QPalette.Base
                    )
                else:
                    Colors.set_widget_color(
                        widget, Colors.WHITE, QtImport.QPalette.Base
                    )
                return True
            else:
                Colors.set_widget_color(
                    widget, Colors.LIGHT_RED, QtImport.QPalette.Base
                )
                return False
        else:
            if self.bindings[field_name][3]:
                Colors.set_widget_color(
                    widget, Colors.LIGHT_YELLOW, QtImport.QPalette.Base
                )
            else:
                Colors.set_widget_color(widget, Colors.WHITE, QtImport.QPalette.Base)
            return True

    def get_model(self):
        return self.__model

    def set_model(self, obj):
        self.__model = obj
        self.init_bindings()
        self.clear_edit()
        self.validate_all()

    def init_bindings(self):
        for field_name in self.bindings.keys():
            self._update_widget(field_name, None)

    def _update_widget(self, field_name, data_binder):

        if data_binder == self:
            return
        try:
            widget, validator, type_fn, edited = self.bindings[field_name]
        except KeyError:
            return

        try:
            widget.blockSignals(True)

            if isinstance(widget, QtImport.QLineEdit): 
                if type_fn is float and validator:
                    if getattr(self.__model, field_name):
                        value = float(getattr(self.__model, field_name))
                        widget.setText(
                            "{:g}".format(round(float(value), validator.decimals()))
                        )
                elif type_fn is int and validator:
                    value = int(getattr(self.__model, field_name))
                    widget.setText("%d" % value)
                else:
                    widget.setText(str(getattr(self.__model, field_name)))

            elif isinstance(widget, QtImport.QLabel):
                widget.setText(str(getattr(self.__model, field_name)))
            elif isinstance(widget, QtImport.QComboBox):
                widget.setCurrentIndex(int(getattr(self.__model, field_name)))
            elif isinstance(widget, QtImport.QCheckBox) or isinstance(
                widget, QtImport.QRadioButton
            ):
                widget.setChecked(bool(getattr(self.__model, field_name)))
        finally:
            widget.blockSignals(False)

    def bind_value_update(self, field_name, widget, type_fn, validator=None):
        self.bindings[field_name] = [widget, validator, type_fn, False]

        if isinstance(widget, QtImport.QLineEdit):
            widget.textChanged.connect(
                lambda new_value: self.__ledit_update_value(
                    field_name, widget, new_value, type_fn, validator
                )
            )
            widget.textEdited.connect(
                lambda new_value: self.__ledit_text_edited(
                    field_name, widget, new_value, type_fn, validator
                )
            )
            if type_fn is float and validator:
                pattern = "%." + str(validator.decimals()) + "f"
                if getattr(self.__model, field_name):
                    widget.setText(pattern % float(getattr(self.__model, field_name)))
            else:
                widget.setText(str(getattr(self.__model, field_name)))

        elif isinstance(widget, QtImport.QLabel):
            widget.setText(str(getattr(self.__model, field_name)))

        elif isinstance(widget, QtImport.QComboBox):
            widget.activated.connect(
                lambda new_value: self.__combobox_update_value(field_name, new_value)
            )

            widget.setCurrentIndex(int(getattr(self.__model, field_name)))

        elif isinstance(widget, QtImport.QCheckBox) or isinstance(
            widget, QtImport.QRadioButton
        ):
            widget.toggled.connect(
                lambda new_value: self.__checkbox_update_value(field_name, new_value)
            )

            widget.setChecked(bool(getattr(self.__model, field_name)))

        if validator and not widget.toolTip():
            if isinstance(validator, QtImport.QDoubleValidator):
                tooltip = "%s limits %.2f : %.2f" % (
                    field_name.replace("_", " ").capitalize(),
                    validator.bottom(),
                    validator.top(),
                )
            else:
                tooltip = "%s limits %d : %d" % (
                    field_name.replace("_", " ").capitalize(),
                    validator.bottom(),
                    validator.top(),
                )
            widget.setToolTip(tooltip)

    def validate_all(self):
        result = []

        for item in self.bindings.items():
            key = item[0]
            widget = item[1][0]
            validator = item[1][1]

            # if validator:
            if isinstance(widget, QtImport.QLineEdit):
                if not self.__validated(key, validator, widget, widget.text()):
                    result.append(key)
            elif isinstance(widget, QtImport.QComboBox):
                pass
            elif isinstance(widget, QtImport.QCheckBox) or isinstance(
                widget, QtImport.QRadioButton
            ):
                pass
        return result

    def clear_edit(self):
        for key in self.bindings.keys():
            self.bindings[key][3] = False
