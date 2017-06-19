from McaSpectrumBrick import McaSpectrumBrick
import logging

from PyMca import McaAdvancedFit
import numpy.oldnumeric as Numeric

__category__ = 'SOLEIL'

class SoleilMcaSpectrumBrick(McaSpectrumBrick):


    def setData(self, data, calib, config):
        print 'McaSpectrumBrick: setData'
        print 'data', data
        print 'calib', calib
        print 'config', config
        #calib = [0, 10, 0]
        try:
            #if config["file"]:
                #self._configure(config)
            x = Numeric.array(data[0]).astype(Numeric.Float)
            y = Numeric.array(data[1]).astype(Numeric.Float)
            xmin = x[0] #float(config["min"])
            xmax = x[-1] #float(config["max"])

            #x = Numeric.array(data[:,0]).astype(Numeric.Float)
            #y = Numeric.array(data[:,1]).astype(Numeric.Float)
            #xmin = float(config["min"])
            #xmax = float(config["max"])
            self.mcafit.refreshWidgets()
            calib = Numeric.ravel(calib).tolist()
            kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib
            self.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax, calibration=calib)
            self.mcafit._energyAxis = False
            self.mcafit.toggleEnergyAxis()
            result = self._fit()
            #pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            outdir = config['htmldir']
            sourcename = config['legend']
            report = McaAdvancedFit.QtMcaAdvancedFitReport.QtMcaAdvancedFitReport(None, outfile=outfile, outdir=outdir,fitresult=result, sourcename=sourcename, plotdict={'logy':False}, table=2)

            text = report.getText()
            report.writeReport(text=text)
  
        except:
            logging.getLogger().exception('McaSpectrumBrick: problem fitting %s %s %s' % (str(data),str(calib),str(config)))
            raise

