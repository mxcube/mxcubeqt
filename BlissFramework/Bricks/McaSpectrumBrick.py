#$Log: McaSpectrumBrick.py,v $
#Revision 1.3  2007/06/20 09:42:59  beteva
#changed Numeric to numpy & forceUpdate() to refreshWidgets()
#
#Revision 1.2  2007/06/06 09:13:32  beteva
#added more config parameters. Forced the display on energy.
#
#Revision 1.1  2007/06/04 14:58:27  beteva
#Initial revision
#
"""
[Name] McaSpectrumBrick

[Description]
The McaSpectrumBrick allows to display Mca Spectrum obtained in SPEC.
If configured, it will take into account the energy calibration factors and
the fit configuration file well as 

[Properties]

[Signals]

[Slots]
-------------------------------------------------------------
| name     | arguments | description
-------------------------------------------------------------
| setData  | data      | numeric array (x, y)
           | calib     | dictionary with the calibration factors (a,b,c)
           | config    | dictionary with the fit parameters



[HardwareObjects]

"""

__category__ = 'Spec'


import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
#from BlissFramework import Icons
#import Icons
#print Icons.__file__
from PyMca import McaAdvancedFit
import numpy.oldnumeric as Numeric
from PyMca import ConfigDict

class McaSpectrumBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSlot('setData',())
        
        self.mcafit = McaAdvancedFit.McaAdvancedFit(self)
        self.mcafit.dismissButton.hide()
        QVBoxLayout(self)        
        self.layout().addWidget(self.mcafit)

    def setData(self, data, calib, config):
        try:
            configured = False
            if config["file"] is not None:
                self._configure(config)
                configured = True
            #TODO what is the data format? 
            data = Numeric.array(data)

            x = Numeric.array(data[:,0]).astype(Numeric.Float)
            y = Numeric.array(data[:,1]).astype(Numeric.Float)
            xmin = float(config["min"])
            xmax = float(config["max"])

            #self.mcafit.refreshWidgets()
            calib = Numeric.ravel(calib).tolist()
            kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib
            self.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax, calibration=calib)
            self.mcafit._energyAxis = False
            self.mcafit.toggleEnergyAxis()

            #Not sure how to use this
            #It is not necessary to fit after each setData            
            #result = self._fit()

            #pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            outdir = config['htmldir']
            sourcename = config['legend']

            if configured:
                report = McaAdvancedFit.QtMcaAdvancedFitReport.\
                         QtMcaAdvancedFitReport(None, outfile=outfile, 
                                                outdir=outdir,fitresult=result, 
                                                sourcename=sourcename, 
                                                plotdict = {'logy' : False}, 
                                                table=2)

                text = report.getText()
                report.writeReport(text=text)
        except:
            logging.getLogger().exception('McaSpectrumBrick: problem fitting %s %s %s' % (str(data),str(calib),str(config)))
            raise

    def _fit(self):
        return self.mcafit.fit()

    def _configure(self,config):
        d = ConfigDict.ConfigDict()
        d.read(config["file"])
        if not d.has_key('concentrations'):
            d['concentrations']= {}
        if not d.has_key('attenuators'):
            d['attenuators']= {}
            d['attenuators']['Matrix'] = [1, 'Water', 1.0, 0.01, 45.0, 45.0]
        if config.has_key('flux'):
            d['concentrations']['flux'] = float(config['flux'])
        if config.has_key('time'):
            d['concentrations']['time'] = float(config['time'])
        self.mcafit.mcafit.configure(d)

    def clear(self):
        x = Numeric.array([0]).astype(Numeric.Float)
        y = Numeric.array([0]).astype(Numeric.Float)
        self.mcafit.setdata(x, y)
        
