from HardwareRepository.BaseHardwareObjects import Equipment
#from abstract_base import AbstractSampleChanger

LOADED_SAMPLES = [('', 1, 1, '', 1), ('', 1, 2, '', 1), ('', 1, 3, '', 1), 
                  ('', 1, 4,'', 1), ('', 1, 5, '', 1), ('', 1, 6, '', 1), 
                  ('', 1, 7, '', 1), ('', 1, 8, '', 1), ('', 1, 9, '', 1), 
                  ('', 1, 10, '', 1), ('', 2, 1, '', 18), ('', 2, 2, '', 18), 
                  ('', 2, 3, '', 1), ('', 2, 4, '', 1), ('', 2, 5, '', 1), 
                  ('', 2, 6, '', 18), ('', 2, 7, '', 18), ('', 2, 8, '', 18), 
                  ('', 2, 9, '', 1), ('', 2, 10, '', 1), ('', 3, 1, '', 1), 
                  ('', 3, 2, '', 18), ('', 3, 3, '', 18), ('', 3, 4, '', 18), 
                  ('', 3, 5, '', 1), ('', 3, 6, '', 1), ('', 3, 7, '', 18), 
                  ('', 3, 8, '', 18), ('', 3, 9, '', 1), ('', 3, 10, '', 1), 
                  ('', 4, 1, '', 18), ('', 4, 2, '', 18), ('', 4, 3, '', 18), 
                  ('', 4, 4, '', 18),('', 4, 5, '', 18), ('', 4, 6, '', 1), 
                  ('', 4, 7, '', 1), ('', 4, 8, '', 1), ('', 4, 9, '', 18), 
                  ('', 4, 10, '', 18), ('', 5, 1, '', 18), ('', 5, 2, '', 18), 
                  ('', 5, 3, '', 18), ('', 5, 4, '', 18), ('', 5, 5, '', 18), 
                  ('', 5, 6, '', 18), ('', 5, 7, '', 18), ('', 5, 8, '', 18), 
                  ('', 5, 9, '', 18), ('', 5, 10, '', 18)]


class SampleChangerMockup(Equipment):#, AbstractSampleChanger):
    def __init__(self, *args, **kwargs):
        Equipment.__init__(self, *args, **kwargs)
        self.current_sample = (1,1)

    def getMatrixCodes(self, codes = None):
        return LOADED_SAMPLES

    def sampleIsLoaded(self):
        if self.current_sample:
            return True
        else:
            return False

    def getSelectedSample(self):
        return None

    def getSelectedComponent(self):
        return None

    def hasLoadedSample(self):
        return self.getLoadedSample() is not None

    def getSampleList(self):
        return []

    def getComponents(self):
        return []

    def loadSample(self, holderLength, sample_id=None, sample_location=None, 
                   sampleIsLoadedCallback=None, failureCallback=None, 
                   prepareCentring=None, prepareCentringMotors={}, wait=False):

        if sample_location:
            requested_basket_num = sample_location[0]
            requested_sample_num = sample_location[1]


        for sample in LOADED_SAMPLES:
            if sample[1] == requested_basket_num and \
                    sample[2] == requested_sample_num:
                self.current_sample = sample
                break
                
    def getLoadedSampleLocation(self):
        if self.current_sample:
            return self.current_sample
        else:
            return (None, None)

    def getLoadedSample(self):
        #return self.current_sample
        return None

    def getLoadedSampleDataMatrix(self):
        return "Nice-little-matrix"

    def currentBasketDataMatrix(self):
        return "Nice-little-current-basket"

    def abort(self):
        return True

    def isMicrodiff(self):
        return False

    def getStatus(self):
        return 'READY'

    def getState(self):
        return 'READY'

    def sampleChangerInUse(self):
        return False

    def sampleChangerCanLoad(self):
        return True

    def is_mounted_sample(self, sample_model):
      if sample_model.location == self.getLoadedSampleLocation():
        return True
      else:
        return False

    def minidiffCanMove(self):
        return True

    def getBasketTransferMode(self):
       return False
