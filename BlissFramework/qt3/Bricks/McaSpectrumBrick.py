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

__category__ = 'MCA'


import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from PyMca import McaAdvancedFit
import numpy
try:
    from PyMca5.PyMca import ConfigDict
except ImportError:
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

            if data[0].size == 2:
                x = numpy.array(data[:,0]) * 1.0
                y = numpy.array(data[:,1])
            else:
                x = data[0] *1.0
                y = data[1]

            xmin = float(config["min"])
            xmax = float(config["max"])

            calib = numpy.ravel(calib).tolist()
            kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib
            self.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax, calibration=calib)
            self.mcafit._energyAxis = False
            self.mcafit.toggleEnergyAxis()

            result = self._fit()

            self.mcafit.refreshWidgets()
            #pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            try:
                outdir = config['htmldir']
            except:
                outdir,_ = config['legend'].split("//")
            sourcename = config['legend']

            if configured and result:
                report = McaAdvancedFit.QtMcaAdvancedFitReport.\
                         QtMcaAdvancedFitReport(None, outfile=outfile, 
                                                outdir=outdir,fitresult=result, 
                                                sourcename=sourcename, 
                                                plotdict = {'logy' : False})

                text = report.getText()
                report.writeReport(text=text)
        except:
            logging.getLogger().exception('McaSpectrumBrick: problem fitting %s %s %s' % (str(data),str(calib),str(config)))
            raise

    def _fit(self):
        if self.mcafit.isHidden():
            self.mcafit.show()
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
        x = numpy.array([0])
        y = numpy.array([0])
        self.mcafit.setdata(x, y)
        
