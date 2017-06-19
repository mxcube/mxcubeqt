from CameraBrick import CameraBrick
import logging

__category__ = 'SOLEIL'

class SoleilCameraBrick(CameraBrick):

    def __init__(self,*args):
        CameraBrick.__init__(self,*args)
        self.defineSlot("beamPositionChanged", ())

    def beamPositionChanged(self, pos):
        x = pos["xbeam"]
        y = pos["ybeam"]
        self.changeBeamPosition(x,y)


