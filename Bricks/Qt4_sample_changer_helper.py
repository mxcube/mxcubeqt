from BlissFramework.Utils import Qt4_widget_colors
from sample_changer.GenericSampleChanger import SampleChangerState, SampleChangerMode, SampleChanger

SC_STATE_COLOR = { SampleChangerState.Fault: Qt4_widget_colors.LIGHT_RED,
                   SampleChangerState.Ready: Qt4_widget_colors.LIGHT_GREEN,
                   SampleChangerState.StandBy: Qt4_widget_colors.LIGHT_GREEN,
                   SampleChangerState.Moving: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Unloading: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Selecting: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Loading: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Scanning: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Resetting: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.ChangingMode: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Initializing: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Closing: Qt4_widget_colors.LIGHT_YELLOW,
                   SampleChangerState.Charging: Qt4_widget_colors.LIGHT_GREEN,
                   SampleChangerState.Alarm: Qt4_widget_colors.LIGHT_RED,
                   SampleChangerState.Disabled: Qt4_widget_colors.LIGHT_RED,
                   SampleChangerState.Unknown: Qt4_widget_colors.LIGHT_GRAY}

SC_STATE_GENERAL = { SampleChangerState.Ready: True,
                     SampleChangerState.Alarm: True }

SC_SAMPLE_COLOR = { "LOADED": Qt4_widget_colors.LIGHT_GREEN,
                    "UNLOADED": Qt4_widget_colors.DARK_GRAY,
                    "LOADING": Qt4_widget_colors.LIGHT_YELLOW,
                    "UNLOADING": Qt4_widget_colors.LIGHT_YELLOW,
                    "UNKNOWN": None }

SC_LOADED_COLOR = { -1: None,
                     0: Qt4_widget_colors.WHITE,
                     1: Qt4_widget_colors.GREEN}

