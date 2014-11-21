from HardwareRepository.BaseHardwareObjects import HardwareObject
from AbstractEnergyScan import *
from gevent.event import AsyncResult
import logging
import time
import os
import httplib
import math
import calc_gaps
import PyChooch
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


class FixedEnergy:

    @task
    def get_energy(self):
        return self._tunable_bl.energy_obj.getPosition()


class TunableEnergy:

    @task
    def get_energy(self):
        return self._tunable_bl.energy_obj.getCurrentEnergy()

    @task
    def move_energy(self, energy):
        return self._tunable_bl.energy_obj.startMoveEnergy(energy, wait=True)

    
class GetStaticParameters:
    def __init__(self, element, edge):
        self.element = element
        self.edge = edge
        config_file = "/users/blissadm/local/spec/userconf/EdgeScan.dat"
        self.STATICPARS_DICT = {}
        self.STATICPARS_DICT = self._readParamsFromFile(config_file)

    def _readParamsFromFile(self, config_file):
        try:
            f = open(config_file)
            array = []
            for line in f:
                if not line.startswith('#'):
                    array.append(line.split())
                else:
                    pass
        except:
            return []
        else:
            larr = []
            for k in range(len(array)):
                if self.element == array[k][1] and self.edge[0] == array[k][2]:
                    larr = map(float,array[k][3:13])
                    larr.append(float(array[k][17]))
            if self.edge == "K":
                to_delete = [1,2,3,4,5,6,7]
            else:
                try:
                    if int(self.edge[1]) == 1:
                        to_delete = [0,1,2,4,5,6,7]
                    elif int(self.edge[1]) == 2:
                        to_delete = [0,1,2,3,5,6,7]
                    else:
                        to_delete = [0,1,2,3,4,6,7]
                except:
                    to_delete = [0,1,2,3,4,6,7]
            for ii in sorted(to_delete, reverse=True):
                del larr[ii]

            static_pars = {}
            larr[0] /= 1000
            static_pars["edgeEnergy"] = larr[0]
            static_pars["startEnergy"] = larr[0] - 0.05
            static_pars["endEnergy"] = larr[0] + 0.05
            static_pars["findattEnergy"] = larr[0] + 0.03
            static_pars["remoteEnergy"] = larr[0] + 1
            static_pars["eroi_min"] = larr[1]
            static_pars["eroi_max"] = larr[2]
            
            return static_pars
        
class ESRFEnergyScan(AbstractEnergyScan, HardwareObject):
    def __init__(self, name, tunable_bl):
        AbstractEnergyScan.__init__(self)
        HardwareObject.__init__(self, name)
        self._tunable_bl = tunable_bl
        
    def execute_command(self, command_name, *args, **kwargs): 
        wait = kwargs.get("wait", True)
        cmd_obj = self.getCommandObject(command_name)
        return cmd_obj(*args, wait=wait)

    def init(self):
        self.energy_obj =  self.getObjectByRole("energy")
        self.safety_shutter = self.getObjectByRole("safety_shutter")
        #check if beamsize is a HO
        try:
            self.beamsize = self.getObjectByRole("beamsize")
        except:
            self.beamsize = None
        self.transmission = self.getObjectByRole("transmission")
        self.ready_event = gevent.event.Event()
        self.dbConnection=self.getObjectByRole("dbserver")
        if self.dbConnection is None:
            logging.getLogger("HWR").warning('EnergyScan: you should specify the database hardware object')
        self.scanInfo=None
        self._tunable_bl.energy_obj = self.energy_obj

    def isConnected(self):
        return True

    @task
    def get_static_parameters(self, element, edge):

        pars = GetStaticParameters(element, edge).STATICPARS_DICT
        
        offset_keV = self.getProperty("offset_keV")
        pars["startEnergy"] += offset_keV
        pars["endEnergy"] += offset_keV
        pars["element"] = element

        #next to tell spec which energy
        self.getChannelObject("ae_rcm").setValue(pars)
        self.execute_command("setRcmValues")
        
        return pars

    @task
    def open_safety_shutter(self):
        self.safety_shutter.openShutter()
        while self.safety_shutter.getShutterState() == 'closed':
            time.sleep(0.1)


    @task
    def close_safety_shutter(self):
        self.safety_shutter.closeShutter()
        while self.safety_shutter.getShutterState() == 'opened':
            time.sleep(0.1)

    @task
    def escan_prepare(self):
        self.execute_command("presetScan")
        if self.beamsize:
            bsX = self.beamsize.getCurrentPositionName()
            bsY = bsX
        else:
            bsX = self.execute_command("get_beam_size_x") * 1000.
            bsY = self.execute_command("get_beam_size_y") * 1000.
        self.energy_scan_parameters["beamSizeHorizontal"] = bsX
        self.energy_scan_parameters["beamSizeVertical"] = bsY

    @task
    def escan_postscan(self):
        self.execute_command("cleanScan")
        
    @task
    def escan_cleanup(self):
        self.close_fast_shutter()
        self.close_safety_shutter()
        self.execute_command("cleanScan")
        self.emit("energyScanFailed", ())
        self.ready_event.set()

    @task
    def close_fast_shutter(self):
        self.execute_command("close_fast_shutter")

    @task
    def open_fast_shutter(self):
        self.execute_command("open_fast_shutter")

    @task
    def move_energy(self, energy):
        try:
            self._tunable_bl.energy_obj.move_energy(energy)
        except:
            self.emit("energyScanFailed", ())
            raise RuntimeError("Cannot move energy")

    # Elements commands
    def getElements(self):
        elements=[]
        try:
            for el in self["elements"]:
                elements.append({"symbol":el.symbol, "energy":el.energy})
        except IndexError:
            pass

        return elements

    def storeEnergyScan(self):
        if self.dbConnection is None:
            return
        try:
            session_id=int(self.energy_scan_parameters['sessionId'])
        except:
            return

        #remove unnecessary for ISPyB fields:
        self.energy_scan_parameters.pop('prefix')
        self.energy_scan_parameters.pop('eroi_min')
        self.energy_scan_parameters.pop('eroi_max')
        self.energy_scan_parameters.pop('findattEnergy')
        self.energy_scan_parameters.pop('edge')
        self.energy_scan_parameters.pop('directory')

        gevent.spawn(StoreEnergyScanThread, self.dbConnection,self.energy_scan_parameters)

    def doChooch(self, elt, edge, scanArchiveFilePrefix, scanFilePrefix):
        symbol = "_".join((elt, edge))
        scanArchiveFilePrefix = "_".join((scanArchiveFilePrefix, symbol))

        i = 1
        while os.path.isfile(os.path.extsep.join((scanArchiveFilePrefix + str(i), "raw"))):
            i = i + 1

        scanArchiveFilePrefix = scanArchiveFilePrefix + str(i) 
        archiveRawScanFile=os.path.extsep.join((scanArchiveFilePrefix, "raw"))
        rawScanFile=os.path.extsep.join((scanFilePrefix, "raw"))
        scanFile=os.path.extsep.join((scanFilePrefix, "efs"))

        if not os.path.exists(os.path.dirname(scanArchiveFilePrefix)):
            os.makedirs(os.path.dirname(scanArchiveFilePrefix))
        
        try:
            f=open(rawScanFile, "w")
            pyarch_f=open(archiveRawScanFile, "w")
        except:
            logging.getLogger("HWR").exception("could not create raw scan files")
            self.storeEnergyScan()
            self.emit("energyScanFailed", ())
            return
        else:
            scanData = []
            
            raw_data_file = os.path.join(os.path.dirname(scanFilePrefix), 'data.raw')
            try:
                raw_file = open(raw_data_file, 'r')
            except:
                self.storeEnergyScan()
                self.emit("energyScanFailed", ())
                return

            for line in raw_file.readlines()[2:]:
                (x, y) = line.split('\t')
                x = float(x.strip())
                y = float(y.strip())
                #x = x < 1000 and x*1000.0 or x
                scanData.append((x, y))
                f.write("%f,%f\r\n" % (x, y))
                pyarch_f.write("%f,%f\r\n"% (x, y))


            f.close()
            pyarch_f.close()
            self.energy_scan_parameters["scanFileFullPath"]=str(archiveRawScanFile)

        pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, chooch_graph_data = PyChooch.calc(scanData, elt, edge, scanFile)
        rm=(pk+30)/1000.0
        pk=pk/1000.0
        savpk = pk
        ip=ip/1000.0
        comm = ""
        self.thEdge = self.energy_scan_parameters['edgeEnergy']
        logging.getLogger("HWR").info("th. Edge %s ; chooch results are pk=%f, ip=%f, rm=%f" % (self.thEdge, pk,ip,rm))

        #should be better, but OK for time being
        self.thEdgeThreshold = 0.01
        if math.fabs(self.thEdge - ip) > self.thEdgeThreshold:
          pk = 0
          ip = 0
          rm = self.thEdge + 0.03
          comm = 'Calculated peak (%f) is more that 10eV away from the theoretical value (%f). Please check your scan' % (savpk, self.thEdge)
   
          logging.getLogger("HWR").warning('EnergyScan: calculated peak (%f) is more that 20eV %s the theoretical value (%f). Please check your scan and choose the energies manually' % (savpk, (self.thEdge - ip) > 0.02 and "below" or "above", self.thEdge))

        archiveEfsFile=os.path.extsep.join((scanArchiveFilePrefix, "efs"))
        try:
          fi=open(scanFile)
          fo=open(archiveEfsFile, "w")
        except:
          self.storeEnergyScan()
          self.emit("energyScanFailed", ())
          return
        else:
          fo.write(fi.read())
          fi.close()
          fo.close()

        self.energy_scan_parameters["peakEnergy"]=pk
        self.energy_scan_parameters["inflectionEnergy"]=ip
        self.energy_scan_parameters["remoteEnergy"]=rm
        self.energy_scan_parameters["peakFPrime"]=fpPeak
        self.energy_scan_parameters["peakFDoublePrime"]=fppPeak
        self.energy_scan_parameters["inflectionFPrime"]=fpInfl
        self.energy_scan_parameters["inflectionFDoublePrime"]=fppInfl
        self.energy_scan_parameters["comments"] = comm

        chooch_graph_x, chooch_graph_y1, chooch_graph_y2 = zip(*chooch_graph_data)
        chooch_graph_x = list(chooch_graph_x)
        for i in range(len(chooch_graph_x)):
          chooch_graph_x[i]=chooch_graph_x[i]/1000.0

        logging.getLogger("HWR").info("<chooch> Saving png" )
        # prepare to save png files
        title="%10s  %6s  %6s\n%10s  %6.2f  %6.2f\n%10s  %6.2f  %6.2f" % ("energy", "f'", "f''", pk, fpPeak, fppPeak, ip, fpInfl, fppInfl) 
        fig=Figure(figsize=(15, 11))
        ax=fig.add_subplot(211)
        ax.set_title("%s\n%s" % (scanFile, title))
        ax.grid(True)
        ax.plot(*(zip(*scanData)), **{"color":'black'})
        ax.set_xlabel("Energy")
        ax.set_ylabel("MCA counts")
        ax2=fig.add_subplot(212)
        ax2.grid(True)
        ax2.set_xlabel("Energy")
        ax2.set_ylabel("")
        handles = []
        handles.append(ax2.plot(chooch_graph_x, chooch_graph_y1, color='blue'))
        handles.append(ax2.plot(chooch_graph_x, chooch_graph_y2, color='red'))
        canvas=FigureCanvasAgg(fig)

        escan_png = os.path.extsep.join((scanFilePrefix, "png"))
        escan_archivepng = os.path.extsep.join((scanArchiveFilePrefix, "png")) 
        self.energy_scan_parameters["jpegChoochFileFullPath"]=str(escan_archivepng)
        try:
          logging.getLogger("HWR").info("Rendering energy scan and Chooch graphs to PNG file : %s", escan_png)
          canvas.print_figure(escan_png, dpi=80)
        except:
          logging.getLogger("HWR").exception("could not print figure")
        try:
          logging.getLogger("HWR").info("Saving energy scan to archive directory for ISPyB : %s", escan_archivepng)
          canvas.print_figure(escan_archivepng, dpi=80)
        except:
          logging.getLogger("HWR").exception("could not save figure")

        self.energy_scan_parameters['endTime']=time.strftime("%Y-%m-%d %H:%M:%S")
        self.storeEnergyScan()

        logging.getLogger("HWR").info("<chooch> returning" )
        self.emit('chooch_finished', (pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title))
        return pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title

def StoreEnergyScanThread(db_conn, scan_info):
    scanInfo = dict(scan_info)
    dbConnection = db_conn

    blsampleid = scanInfo['blSampleId']
    scanInfo.pop('blSampleId')
    db_status=dbConnection.storeEnergyScan(scanInfo)
    if blsampleid is not None:
        try:
            energyscanid=int(db_status['energyScanId'])
        except:
            pass
        else:
            asoc={'blSampleId':blsampleid, 'energyScanId':energyscanid}
            dbConnection.associateBLSampleAndEnergyScan(asoc)
 
