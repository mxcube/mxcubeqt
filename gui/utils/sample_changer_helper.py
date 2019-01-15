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

from gui.utils import Colors
from HardwareRepository.HardwareObjects.abstract.AbstractSampleChanger import SampleChangerState, SampleChangerMode, SampleChanger


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


SC_STATE_COLOR = { SampleChangerState.Fault: Colors.LIGHT_RED,
                   SampleChangerState.Ready: Colors.LIGHT_GREEN,
                   SampleChangerState.StandBy: Colors.LIGHT_GREEN,
                   SampleChangerState.Moving: Colors.LIGHT_YELLOW,
                   SampleChangerState.Unloading: Colors.LIGHT_YELLOW,
                   SampleChangerState.Selecting: Colors.LIGHT_YELLOW,
                   SampleChangerState.Loading: Colors.LIGHT_YELLOW,
                   SampleChangerState.Scanning: Colors.LIGHT_YELLOW,
                   SampleChangerState.Resetting: Colors.LIGHT_YELLOW,
                   SampleChangerState.ChangingMode: Colors.LIGHT_YELLOW,
                   SampleChangerState.Initializing: Colors.LIGHT_YELLOW,
                   SampleChangerState.Closing: Colors.LIGHT_YELLOW,
                   SampleChangerState.Charging: Colors.LIGHT_GREEN,
                   SampleChangerState.Alarm: Colors.LIGHT_RED,
                   SampleChangerState.Disabled: Colors.LIGHT_RED,
                   SampleChangerState.Unknown: Colors.LIGHT_GRAY}

SC_STATE_GENERAL = { SampleChangerState.Ready: True,
                     SampleChangerState.Alarm: True }

SC_SAMPLE_COLOR = { "LOADED": Colors.LIGHT_GREEN,
                    "UNLOADED": Colors.DARK_GRAY,
                    "LOADING": Colors.LIGHT_YELLOW,
                    "UNLOADING": Colors.LIGHT_YELLOW,
                    "UNKNOWN": None }

SC_LOADED_COLOR = { -1: None,
                     0: Colors.WHITE,
                     1: Colors.GREEN}

