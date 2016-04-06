import time
import logging
import numpy
from scipy import optimize
import qt

from opencv import cv

from Qub.CTools.opencv import qtTools

#TRACE CODE (FOR DEBUGGING PURPOSE)
TRACE_MODE = False
PLOT_MODE = False
def print_trace(func) :
    if TRACE_MODE :
        def f(c,*args,**keys) :
            print(func.__name__,c.__class__.__name__,args,keys)
            return func(c,*args,**keys)
        return f
    else:
        return func

class _Plot:
    def __init__(self) :
        from Qub.Widget.Graph.QubGraph  import QubGraph
        from Qub.Widget.Graph.QubGraphCurve import QubGraphCurve
        self.graph = QubGraph()
        self.curve = QubGraphCurve()
        self.curve.attach(self.graph)

        self.__followCurve = self.curve.getCurvePointFollowMarked()
        self.graph.show()

        self._All = []

    def clear(self) :
        self._All = []
        
    def addPositionNFocus(self,position,focus) :
        self._All.append((position,focus))

        def _s(a,b) :
            if a > b: return 1
            elif a < b : return -1
            else: return 0
        self._All.sort(_s)
        AllPosition,Allfocus = list(zip(*self._All))
        self.curve.setData(numpy.array(AllPosition),numpy.array(Allfocus))
        self.graph.replot()

def _plot_clear(func) :
    if PLOT_MODE:
        def _pc(c,*args,**keys) :
            global _GraphPlot
            _GraphPlot.clear()
            return func(c,*args,**keys)
        return _pc
    else:
        return func
#for debug set this methode to evalCurrentImageGradient
def _add_point(func) :
    if PLOT_MODE:
        def _ap(c,*args,**keys) :
            focusQuality = func(c,*args,**keys)
            global _GraphPlot
            position = c._focusMotor.getPosition()
            _GraphPlot.addPositionNFocus(position,focusQuality)
            return focusQuality
        return _ap
    else:
        return func
if PLOT_MODE:
    _GraphPlot = _Plot()
#END TRACE

class FocusState:
    def __init__(self,cnt,focusMotor,limit = None) :
        self._cnt = cnt
        cnt.focusState = self
        self._focusMotor = focusMotor
        self._limit = limit
        
    @_plot_clear
    def start(self) :
        _FocusBeginState(self._cnt,self._focusMotor,self._limit)

    def endMovement(self,ver) :
        pass

    def newPosition(self,position) :
        pass
    def setLimit(self,limit) :
        self._limit = limit
        
    @_add_point
    def evalCurrentImageGradient(self) :
        key = {}
        try:
            self._cnt.emit(qt.PYSIGNAL("getImage"), (key,))
            qimage = key['image']
        except KeyError: return
        ##EVAL IMAGE GRADIENT
        x,y = self._cnt.focusPointSelected
        rectangleSize = self._cnt.focusRectangleSize
        im = qimage.copy(x,y,x+rectangleSize,y+rectangleSize)
        srcColorImage = qtTools.getImageOpencvFromQImage(im)

        if srcColorImage.nChannels > 1:
            srcImage = cv.cvCreateImage(cv.cvSize(srcColorImage.width,srcColorImage.height),
                                        srcColorImage.depth,1)
            cv.cvCvtColor(srcColorImage,srcImage,cv.CV_RGB2GRAY)
        else:                           # In Fact It's a grey image
            srcImage = srcColorImage

        destImage = cv.cvCreateImage(cv.cvSize(srcImage.width,srcImage.height),cv.IPL_DEPTH_16S,1)
        cv.cvSobel(srcImage,destImage,1,0,3)
        array = numpy.fromstring(destImage.imageData_get(),dtype=numpy.int16)
        focusQuality = array.std()
        return focusQuality
 

class _FocusBeginState(FocusState) :
    @print_trace
    def __init__(self,cnt,focusMotor,limit) :
        FocusState.__init__(self,cnt,focusMotor,limit)
        self.__focusQuality = self.evalCurrentImageGradient()
        self.__maxFocusQuality = self.__focusQuality
        self.__startPosition = self._focusMotor.getPosition()
        self.__maxFocusPosition = self.__startPosition
        minLim,maxLim = self._limit
        averageLimPosition = (minLim + maxLim) / 2.
        self.__lastMovement = averageLimPosition - self.__startPosition
        if abs(self.__lastMovement) < self._cnt.focusMinStep:
            self.__lastMovement = self._cnt.focusMinStep
        self._focusMotor.moveRelative(self.__lastMovement)
        
    def start(self) :
        pass
    
    @print_trace
    def newPosition(self,position) :
        diffPos = position - self.__maxFocusPosition
        if(diffPos >= 0 and self.__lastMovement >= 0 or diffPos < 0 and self.__lastMovement < 0) : # avoid backlash
            focusQuality = self.evalCurrentImageGradient()
            if focusQuality is None :
                self._focusMotor.move(self.__startPosition)
                FocusState(self._cnt,self._focusMotor,self._limit)
                logging.getLogger().error('CameraMotorToolsBrick: You Have to connect getImage signal!!!')
                return
            if focusQuality > self.__maxFocusQuality :
                self.__maxFocusQuality = focusQuality
                self.__maxFocusPosition = position
            elif focusQuality < (self.__maxFocusQuality * 0.9):
                self._focusMotor.stop()
                if self.__maxFocusQuality > self.__focusQuality: # we pass throw a maximum
                    _FocusBeginAfineState(self._cnt,self._focusMotor,self._limit,
                                          self.__maxFocusQuality,self.__maxFocusPosition)
                else:                       # other way
                    _FocusReverseState(self._cnt,self._focusMotor,self._limit,
                                       self.__focusQuality,self.__startPosition,self.__lastMovement)
    ##@brief endMovement motor focus
    #
    #If this methode is called, we are in the good way to focus
    @print_trace
    def endMovement(self,ver) :
        position = self._focusMotor.getPosition()
        if self.__lastMovement > 0:
            self.__lastMovement = self._limit[1] - position
            self._focusMotor.move(self._limit[1])
        elif self.__lastMovement < 0:
            self.__lastMovement = self._limit[0] - position
            self._focusMotor.move(self._limit[0])
        else:
            self._focusMotor.move(self.__startPosition) # Hooups can't focus may be due to limit
            FocusState(self._cnt,self._focusMotor,self._limit)

class _FocusReverseState(FocusState) :
    @print_trace
    def __init__(self,cnt,focusMotor,limit,focusQuality,startPosition,lastMovement) :
        FocusState.__init__(self,cnt,focusMotor,limit)
        self.__startPosition = startPosition
        self.__startFocusQuality = focusQuality
        self.__maxFocusPosition = startPosition
        self.__maxFocusQuality = focusQuality
        self.__lastMovement = -lastMovement
        if self.__lastMovement >= 0:
            self._focusMotor.move(self._limit[1])
        else:
            self._focusMotor.move(self._limit[0])

    def start(self) :
        pass

    @print_trace
    def newPosition(self,position) :
        diffPos = position - self.__maxFocusPosition
        if(diffPos >= 0 and self.__lastMovement >= 0 or diffPos < 0 and self.__lastMovement < 0) : # avoid backlash
            focusQuality = self.evalCurrentImageGradient()
            if focusQuality > self.__maxFocusQuality :
                self.__maxFocusQuality = focusQuality
                self.__maxFocusPosition = position
            else:
                self._focusMotor.stop()
                if self.__maxFocusPosition > self.__startFocusQuality:
                    _FocusBeginAfineState(self._cnt,self._focusMotor,self._limit,
                                          self.__maxFocusQuality,self.__maxFocusPosition)
                else:                   # go back to start
                    self._focusMotor.move(self.__startPosition)
                    FocusState(self._cnt,self._focusMotor,self._limit)
                    
class _FocusBeginAfineState(FocusState) :
    @print_trace
    def __init__(self,cnt,focusMotor,limit,localHighestFocusQuality,position) :
        FocusState.__init__(self,cnt,focusMotor,limit)
        self.__localHighestFocusQuality = localHighestFocusQuality
        self.__localHighestFocusPosition = position

    def start(self) :
        pass

    @print_trace
    def endMovement(self,ver) :
        time.sleep(1)
        position = self._focusMotor.getPosition()
        focusQuality = self.evalCurrentImageGradient()
        _FocusAfineState(self._cnt,self._focusMotor,self._limit,
                         self.__localHighestFocusQuality,self.__localHighestFocusPosition,
                         focusQuality,position)
        
        
class _FocusAfineState(FocusState) :
    @print_trace
    def __init__(self,cnt,focusMotor,limit,
                 localHighestFocusQuality,localHighestFocusPosition,
                 startFocusQuality,startPosition) :
        FocusState.__init__(self,cnt,focusMotor,limit)
        self.__localMiddlePointRefQuality = localHighestFocusQuality
        self.__localMiddlePointRefPosition = localHighestFocusPosition
        self.__startPosition = startPosition
        self.__startFocusQuality = startFocusQuality
        moveVector = 2 * (self.__localMiddlePointRefPosition - self.__startPosition)
        self._focusMotor.moveRelative(moveVector)
        self.__positions = [startPosition]
        self.__focus = [startFocusQuality]

        def fitfunc(p,x)  :
            if p[0] != 0 :
                return (1 / p[0]) * numpy.exp(-(x-p[1]) ** 2 / (2 * p[0] ** 2))
            else: 
                return numpy.inf
        self.__errfunc = lambda p,x,y: fitfunc(p,x) - y


    def start(self) :
        pass

    @print_trace
    def endMovement(self,ver) :
        time.sleep(1)
        position = self._focusMotor.getPosition()
        focusQuality = self.evalCurrentImageGradient()
        self.__positions.append(float(position))
        self.__focus.append(float(focusQuality))
        if(focusQuality > self.__startFocusQuality and
           focusQuality > self.__localMiddlePointRefQuality) : # Change middle
            self.__startPosition = (position + self.__localMiddlePointRefPosition) / 2.
            self.__startFocusQuality = (focusQuality + self.__localMiddlePointRefQuality) / 2. # approx linear
            self.__localMiddlePointRefPosition = position
            self.__localMiddlePointRefQuality = focusQuality
            moveVector = self.__localMiddlePointRefPosition - self.__startPosition
            if abs(moveVector) > self._cnt.focusMinStep :
                self._focusMotor.moveRelative(moveVector)
            else:                       # END
                FocusState(self._cnt,self._focusMotor,self._limit)
        else:
            self.__startFocusQuality = focusQuality
            self.__startPosition = position

            if len(self.__positions) < 3:
                positions = [self.__localMiddlePointRefPosition]
                positions.extend(self.__positions)
                focus = [self.__localMiddlePointRefQuality]
                focus.extend(self.__focus)
            else:
                positions,focus = self.__positions,self.__focus

            p1,sucess = optimize.leastsq(self.__errfunc,
                                         [1. / self.__localMiddlePointRefQuality,float(self.__localMiddlePointRefPosition)],
                                         args = (numpy.array(positions),numpy.array(focus)))
            if sucess:
                self.__localMiddlePointRefPosition = p1[1]
                self.__localMiddlePointRefQuality = 1 / p1[0]
                print(self.__localMiddlePointRefPosition,self.__localMiddlePointRefQuality)
                moveVector = self.__localMiddlePointRefPosition - position
                self.__startPosition = positions
                self.__startFocusQuality = focusQuality
                if abs(moveVector) > self._cnt.focusMinStep :
                    self._focusMotor.moveRelative(float(moveVector))
                else:
                    FocusState(self._cnt,self._focusMotor,self._limit)
            else:                       # PB ????
                FocusState(self._cnt,self._focusMotor,self._limit)
                
