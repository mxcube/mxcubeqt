from BlissFramework.Utils import widget_colors
from sample_changer.GenericSampleChanger import SampleChangerState, SampleChangerMode, SampleChanger

SC_STATE_COLOR = { SampleChangerState.Fault: widget_colors.LIGHT_RED,
                   SampleChangerState.Ready: widget_colors.LIGHT_GREEN,
                   "Ready": widget_colors.LIGHT_GREEN,
                   "Running": widget_colors.LIGHT_YELLOW,
                   "Closing": widget_colors.LIGHT_RED,
                   "Alarm": widget_colors.LIGHT_RED,
                   "Unusable": widget_colors.LIGHT_RED,
                   SampleChangerState.StandBy: widget_colors.LIGHT_GREEN,
                   SampleChangerState.Moving: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Unloading: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Selecting: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Loading: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Scanning: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Resetting: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.ChangingMode: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Initializing: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Closing: widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Charging: widget_colors.LIGHT_GREEN,
                   SampleChangerState.Alarm: widget_colors.LIGHT_RED,
                   SampleChangerState.Disabled: None,
                   SampleChangerState.Unknown: None}

SC_STATE_GENERAL = { SampleChangerState.Ready: True,
                     SampleChangerState.Alarm: True,
                     "Ready": True }

SC_SAMPLE_COLOR = { "LOADED": widget_colors.LIGHT_GREEN,
                    "UNLOADED": widget_colors.DARK_GRAY,
                    "LOADING": widget_colors.LIGHT_YELLOW,
                    "UNLOADING": widget_colors.LIGHT_YELLOW,
                    "UNKNOWN": None }

SC_LOADED_COLOR = { -1: None,
                     0: widget_colors.WHITE,
                     1: widget_colors.GREEN}

