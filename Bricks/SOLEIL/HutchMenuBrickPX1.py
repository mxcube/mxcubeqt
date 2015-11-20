
import logging
import HutchMenuBrick

__category__ = 'SOLEIL'

###
### Sample centring brick
###
class HutchMenuBrickPX1(HutchMenuBrick.HutchMenuBrick):

    def __init__(self, *args):
        HutchMenuBrick.HutchMenuBrick.__init__(self, *args)

    def updateBeam(self,force=False):
        if self["displayBeam"]:
              if not self.minidiff.isReady(): time.sleep(0.2)
              beam_x = self.minidiff.getBeamPosX()
              beam_y = self.minidiff.getBeamPosY()
              try:
                 self.__rectangularBeam.set_xMid_yMid(beam_x,beam_y)
              except AttributeError:
                 pass
              try:
                self.__beam.move(beam_x, beam_y)
                try:
                  get_beam_info = self.minidiff.getBeamInfo #getCommandObject("getBeamInfo")
                  if force or get_beam_info: #.isSpecReady():
                      self._updateBeam({"size_x":0.045, "size_y":0.025, "shape": "rectangular"})
                except:
                  logging.getLogger().exception("Could not get beam size: cannot display beam")
                  self.__beam.hide()
              except AttributeError:
                pass


