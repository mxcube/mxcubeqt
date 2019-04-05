from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
import logging
import sys
import pprint

__category__ = "mxCuBE_v3"


class DCGBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)
