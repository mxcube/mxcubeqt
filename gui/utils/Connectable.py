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


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


class Connectable(object):
    def __init__(self):
        self.__signal = {}
        self.__slot = {}

    def define_signal(self, signal_name, signal_args):
        try:
            args = tuple(signal_args)
        except BaseException:
            print("'", signal_args, "' is not a valid arguments tuple.")
            raise ValueError

        self.__signal[str(signal_name)] = args

    def define_slot(self, slot_name, slot_args):
        try:
            args = tuple(slot_args)
        except BaseException:
            print("'", slot_args, "' is not a valid arguments tuple.")
            raise ValueError

        self.__slot[str(slot_name)] = args

    def reset_signals(self):
        self.__signal = {}

    def reset_slots(self):
        self.__slot = {}

    def remove_signal(self, signal_name):
        try:
            del self.__signal[str(signal_name)]
        except KeyError:
            pass

    def remove_slot(self, slot_name):
        try:
            del self.__slot[str(slot_name)]
        except KeyError:
            pass

    def has_signal(self, signal_name):
        return signal_name in self.__signal

    def has_slot(self, slot_name):
        return slot_name in self.__slot

    def get_signals(self):
        return self.__signal

    def get_slots(self):
        return self.__slot
