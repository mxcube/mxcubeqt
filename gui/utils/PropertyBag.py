#
#  Project: MXCuBE
#  https://github.com/mxcube.
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

import pickle


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class Property:
    def __init__(self, property_name, default_value=None):
        self.name = property_name

        self.type = "undefined"
        self.value = None
        self.old_value = None
        self.hidden = False
        self._editor = None
        self.comment = ""

        if default_value is None:
            self.default_value = None
        else:
            self.set_default_value(default_value, True)

    def __getstate__(self):
        dict = self.__dict__.copy()  # copy the dict since we change it
        if hasattr(self, "_editor"):
            del dict["_editor"]  # remove ref. to editor
        return dict

    def __setstate__(self, dict):
        self.__dict__.update(dict)

        if not "hidden" in dict:
            self.hidden = False

        self._editor = None

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_user_value(self):
        return self.get_value()

    def get_value(self):
        return self.value

    def get_default_value(self):
        return self.default_value

    def set_value(self, property_value):
        self.value = property_value

    def set_default_value(self, value, set_as_value=False):
        saved_value = self.value
        saved_old_value = self.old_value

        try:
            self.set_value(value)
        except ValueError:
            raise ValueError(
                "cannot set default value to %s : incompatible types." % str(value)
            )

        self.default_value = self.value

        if not set_as_value:
            self.value = saved_value
            self.old_value = saved_old_value

    def set_comment(self, comment):
        self.comment = comment

    def get_comment(self):
        return comment

    def as_dict(self):
        return {"type": self.type, "value": self.value}

    def set_from_dict(self, property_dict):
        self.type = property_dict["type"]
        self.value = property_dict["value"]


class StringProperty(Property):
    def __init__(self, property_name, default_value=""):
        Property.__init__(self, property_name, default_value)

        self.type = "string"

    def set_value(self, property_value):
        self.old_value = self.value
        self.value = str(property_value)


class IntegerProperty(Property):
    def __init__(self, property_name, default_value=None):
        Property.__init__(self, property_name, default_value)

        self.type = "integer"

    def set_value(self, property_value):
        try:
            newValue = int(property_value)
        except ValueError:
            raise ValueError("%s is not a valid integer value." % repr(property_value))

        self.old_value = self.value
        self.value = newValue


class BooleanProperty(Property):
    def __init__(self, property_name, default_value=False):
        Property.__init__(self, property_name, default_value)

        self.type = "boolean"

    def set_value(self, property_value):
        self.old_value = self.value

        if property_value:
            self.value = 1
        else:
            self.value = 0


class ComboProperty(Property):
    def __init__(self, property_name, choices=[], default_value=None):
        self.set_choices(choices)

        Property.__init__(self, property_name, default_value)
        self.type = "combo"

    def add_choice(self, choice):
        self.choices.append(str(choice))

    def set_choices(self, choices):
        try:
            self.choices = list(choices)
        except BaseException:
            raise ValueError("%s cannot be converted into a list" % repr(choices))

    def get_choices(self):
        return self.choices

    def set_value(self, property_value):
        strValue = str(property_value)

        for choice in self.choices:
            if strValue == choice:
                self.old_value = self.value
                self.value = strValue
                return
        raise ValueError(
            "%s is not a valid choice for combo" % repr(str(property_value))
        )


class FloatProperty(Property):
    def __init__(self, property_name, default_value=None):
        Property.__init__(self, property_name, default_value)

        self.type = "float"

    def set_value(self, property_value):
        try:
            newValue = float(property_value)
        except ValueError:
            raise ValueError("%s is not a valid float value" % repr(property_value))

        self.old_value = self.value
        self.value = newValue


class FileProperty(Property):
    def __init__(self, property_name, filter="All (*.*)", default_value=None):
        Property.__init__(self, property_name, default_value or "")

        self.type = "file"
        self.filter = filter

    def set_value(self, property_value):
        import os.path

        newValue = os.path.abspath(str(property_value))

        self.old_value = self.value
        self.value = newValue

    def get_filter(self):
        return self.filter


class ColorProperty(Property):
    def __init__(self, property_name, default_value=None):
        Property.__init__(self, property_name, default_value)

        self.type = "color"

    def set_value(self, property_value):
        self.old_value = self.value
        self.value = property_value


class FormatStringProperty(Property):
    def __init__(self, property_name, default_value=None):
        self.format_string = None
        self.format_string_length = 0

        Property.__init__(self, property_name, default_value)

        self.type = "formatString"

    def set_value(self, format):
        self.old_value = self.value
        self.value = str(format)

        if format.startswith("+"):
            prefix = "+"
            format = format[1:]
        elif format.startswith(" "):
            prefix = ""
            format = format[1:]
        else:
            prefix = ""

        parts = format.split(".")

        if len(parts) == 2:
            self.format_string = (
                "%" + prefix + str(len(parts[0])) + "." + str(len(parts[1])) + "f"
            )
        elif len(parts) == 1:
            self.format_string = "%" + prefix + str(len(parts[0])) + ".0f"
        else:
            raise ValueError

        self.format_string_length = sum(map(len, parts)) + 1

    def get_user_value(self):
        return self.value

    def get_value(self):
        return self.format_string

    def get_format_length(self):
        return self.format_string_length


class PropertyBag:
    def __init__(self):
        self.properties = {}

    def add_property(
        self,
        property_name,
        property_type,
        arg1=None,
        arg2=None,
        comment="",
        hidden=False,
    ):
        if property_type == "string":
            if arg1 is None:
                arg1 = ""
            new_property = StringProperty(property_name, arg1)
        elif property_type == "integer":
            new_property = IntegerProperty(property_name, arg1)
        elif property_type == "combo":
            if list(arg1):
                new_property = ComboProperty(property_name, arg1, arg2)
            else:
                new_property = ComboProperty(property_name, default_value=arg1)
        elif property_type == "boolean":
            new_property = BooleanProperty(property_name, arg1)
        elif property_type == "float":
            new_property = FloatProperty(property_name, arg1)
        elif property_type == "file":
            new_property = FileProperty(property_name, arg1, arg2)
        elif property_type == "color":
            new_property = ColorProperty(property_name, default_value=arg1)
        elif property_type == "formatString":
            new_property = FormatStringProperty(property_name, default_value=arg1)
        else:
            new_property = Property(property_name, arg1)

        new_property.comment = comment
        new_property.hidden = hidden

        self.properties[property_name] = new_property

        self.update_editor()

    def update_editor(self):
        for propname, prop in self.properties.items():
            if prop._editor is not None:
                # the properties are being edited,
                # refresh property editor
                editor = prop._editor()

                if editor is not None:
                    editor.set_property_bag(self)
                break

    def del_property(self, property_name):
        ed = None
        for propname, prop in self.properties.items():
            ed = prop._editor
            break

        try:
            del self.properties[property_name]
        except KeyError:
            pass
        else:
            try:
                editor = ed()
                if editor is not None:
                    editor.set_property_bag(self)
            except TypeError:
                pass

    def get_property(self, property_name):
        try:
            return self.properties[property_name]
        except KeyError:
            return Property("")

    def hide_property(self, property_name):
        prop = self.properties.get(property_name, None)
        if prop is not None and not prop.hidden:
            prop.hidden = True
            if prop._editor is not None:
                editor = prop._editor()
                if editor is not None:
                    editor.set_property_bag(self)

    def show_property(self, property_name):
        prop = self.properties.get(property_name, None)
        if prop is not None and prop.hidden:
            prop.hidden = False
            if prop._editor is not None:
                editor = prop._editor()
                if editor is not None:
                    editor.set_property_bag(self)

    def __repr__(self):
        return repr(pickle.dumps(self))

    def __str__(self):
        return "<PropertyBag instance>"

    def __iter__(self):
        keys = sorted(self.properties.keys())

        for key in keys:
            yield self.properties[key]

    def __len__(self):
        return len(self.properties)

    def __getitem__(self, propertyKey):
        item = self.properties.get(propertyKey)
        if item is not None:
            return self.properties[propertyKey].get_value()

    def __setitem__(self, property_name, property):
        self.properties[property_name] = property

    def is_empty(self):
        return len(self.properties) == 0

    def has_property(self, name):
        return name in self.properties
