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

from mxcubeqt.utils import colors
from mxcubecore.HardwareObjects.abstract.AbstractSampleChanger import (
    SampleChangerState,
    SampleChangerMode,
    SampleChanger,
)
# NBNB SampleChangerMode and SampleChanger are not use here but are REIMPORTED elsewhere
# This is generally bad practice, but there are pragmatic reasons.
# Do NOT remove these imports without checking all uses of this file


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


SC_STATE_COLOR = {
    SampleChangerState.Fault: colors.LIGHT_RED,
    SampleChangerState.Ready: colors.LIGHT_GREEN,
    SampleChangerState.StandBy: colors.LIGHT_GREEN,
    SampleChangerState.Moving: colors.LIGHT_YELLOW,
    SampleChangerState.Unloading: colors.LIGHT_YELLOW,
    SampleChangerState.Selecting: colors.LIGHT_YELLOW,
    SampleChangerState.Loading: colors.LIGHT_YELLOW,
    SampleChangerState.Scanning: colors.LIGHT_YELLOW,
    SampleChangerState.Resetting: colors.LIGHT_YELLOW,
    SampleChangerState.ChangingMode: colors.LIGHT_YELLOW,
    SampleChangerState.Initializing: colors.LIGHT_YELLOW,
    SampleChangerState.Closing: colors.LIGHT_YELLOW,
    SampleChangerState.Charging: colors.LIGHT_GREEN,
    SampleChangerState.Alarm: colors.LIGHT_RED,
    SampleChangerState.Disabled: colors.LIGHT_RED,
    SampleChangerState.Unknown: colors.LIGHT_GRAY,
}

SC_STATE_GENERAL = {SampleChangerState.Ready: True, SampleChangerState.Alarm: True}

SC_SAMPLE_COLOR = {
    "LOADED": colors.LIGHT_GREEN,
    "UNLOADED": colors.DARK_GRAY,
    "LOADING": colors.LIGHT_YELLOW,
    "UNLOADING": colors.LIGHT_YELLOW,
    "UNKNOWN": None,
}

SC_LOADED_COLOR = {-1: None, 0: colors.WHITE, 1: colors.GREEN}
