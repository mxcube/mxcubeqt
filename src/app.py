"""
   Sample list
  
   Image 
"""
import logging
import time
import os
import sys
import json
import socket
import math
import gevent
import gevent.event
from gevent import monkey; monkey.patch_all()
from gevent import sleep
 
from PIL import Image
import cStringIO
import base64
import numpy

from HardwareRepository import HardwareRepository

import bottle
from bottle import get, post, request, response, route, static_file, redirect
from bottle import GeventServer, run

from beaker.middleware import SessionMiddleware

samples_info= open(os.path.join(os.path.dirname(__file__), "sample_list.txt")).read()

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}

#default params for the dc discrete scan
#discrete_params = { "osc_range": 1.0, "osc_start": 0, "exp_time": 10.0, "n_mages": 1} 


mxcube = bottle.Bottle()
mxcube_app = SessionMiddleware(mxcube, session_opts)
#tango event queue
queue = gevent.queue.Queue(maxsize=16)
#sample list + experiment list, not queue for beaing able to replace elements
q_exp = []

def new_sample_video_frame_received(img, width, height, *args):
    if type(img) == str:
        jpeg_buffer = cStringIO.StringIO()
        jpeg_buffer.write(img)
    elif type(img) == cStringIO.OutputType:
        jpeg_buffer = img
    else:
        raw_data = img.bits().asstring(img.numBytes())  
        im = Image.fromstring("RGBX", (width,height), raw_data)
        b,g,r,x = im.split()
        rgb_im = Image.merge("RGB",(r,g,b))
        jpeg_buffer = cStringIO.StringIO()
        rgb_im.save(jpeg_buffer, "JPEG")  

    mxcube.new_frame.set(jpeg_buffer.getvalue())

def bl_state():
    return {}
    return {"resolution": str("%3.4f" % mxcube.bl_setup.resolution_hwobj.getPosition()),
           "energy": str("%2.4f" % mxcube.bl_setup.energy_hwobj.getCurrentEnergy()),
           "light": str("%1.2f" % mxcube.bl_setup.diffractometer_hwobj.lightMotor.getPosition()),
           "light_state": mxcube.bl_setup.diffractometer_hwobj.lightWago.getWagoState(),
           "transmission": str("%3.2f" % mxcube.bl_setup.transmission_hwobj.getAttFactor()),
           "zoom": 0,
           "pixelsPerMmY": mxcube.bl_setup.diffractometer_hwobj.pixelsPerMmY,
           "pixelsPerMmZ": mxcube.bl_setup.diffractometer_hwobj.pixelsPerMmZ }

def successful_login( getdict ):
    sess = request.environ.get('beaker.session')
    sess['proposal'] = getdict['proposal']
    sess.save()


@mxcube.get('/init')
def init():

    hwr_directory = os.environ["XML_FILES_PATH"]

    if not hasattr(mxcube, "bl_setup"):
        print "Loading hardware repository from ", os.path.abspath(hwr_directory)
        hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
        print '*******************************************************************'

        hwr.connect()
        mxcube.new_frame = gevent.event.AsyncResult()
        mxcube.bl_setup = hwr.getHardwareObject("/beamline-setup_sim")
        mxcube.detector = hwr.getHardwareObject("/detector_sim")
        
        #mxcube.camera = hwr.getHardwareObject("/md_camera")

        #loading nere frogak HWrekin
        #mxcube.motor = hwr.getHardwareObject("/motor")
        mxcube.energy = hwr.getHardwareObject("/motor_biomax_energy")
        mxcube.shutter = mxcube.bl_setup.shutter_hwobj

#         print mxcube.motor.getPosition()
#         print mxcube.motor.isMotorOk()
#         mxcube.motor.setPosition(2500)
#         #mxcube.motor.moveMotor(500)
#         #mxcube.motor.stopMotor()
        mxcube.energy.connect('motorPositionChanged',motor_handler)
        mxcube.energy.connect('motorStateChanged',motor_handler)
# #     
    
        #loading nere frogak sardana + HWrekin (bixente's code)
        #mxcube.sar = hwr.getHardwareObject("/motorscan")
        #mxcube.sar.scan()
        try:
            mxcube.diffractometer = mxcube.bl_setup.diffractometer_hwobj
            mxcube.video = mxcube.diffractometer.getObjectByRole("camera")
        except:
            mxcube.video = hwr.getHardwareObject("/camera")
        mxcube.diffractometer.getObjectByRole('kappa').connect('motorPositionChanged',motor_handler)
        mxcube.diffractometer.getObjectByRole('phi').connect('motorPositionChanged',motor_handler)
        mxcube.diffractometer.getObjectByRole('phiz').connect('motorPositionChanged',motor_handler)

        #mxcube.diffractometer.getObjectByRole('omega').connect('motorPositionChanged',motor_handler)

        mxcube.diffractometer.connect("imageReceived", new_sample_video_frame_received)
        
        # gevent.sleep(2)
        
        #mxcube.sar.scan('mot05','1 10 10 1') 
        #mxcube.sar.startMotorScan()
        #mxcube.sar.scan(mxcube.sar.motorname+' '+ mxcube.sar.params)  #this is the good one
        #mxcube.sar.scan1()
        #mxcube.sar.scan2()
    return json.dumps(bl_state())

def sse_pack(d):
    """Pack data in SSE format"""
    buffer = ''
    for k in ['retry','id','event','data']:
        if k in d.keys():
            buffer += '%s: %s\n' % (k, d[k])
    return buffer + '\n'

#nere frogak
def motor_handler(value, sig, origin):
    print value,sig, origin
    
    if sig == 'motorPositionChanged':
        print '******************* New motor position:.....', str(value), origin
    else:
        print '******************* New motor state:.....', str(value), origin
        
    try:
        queue.put({'name':sig,'value':str("%0.2f" %value), 'origin':origin})
        print "queuen sartua............"+str(("%0.2f" %value))
    except Exception:
        pass
        print "por aqui hemos petao"


@mxcube.route("/event")
def event():
    event_id = 0
    if 'Last-Event-Id' in request.headers:
        event_id = int(request.headers['Last-Event-Id']) + 1
    response.content_type = "text/event-stream"
    response.cache_control = 'no-cache'
    msg = {
        'retry': '1000'
    }
    response.headers['content-type'] = 'text/event-stream'
    response.headers['Access-Control-Allow-Origin'] = '*'
    #response.headers['Cache-Control']='no-cache'
    response.headers['CharacterEncoding'] = "utf-8"

    msg.update({
         'event': 'init',
         #'data' : json.dumps(get_current_shared_state()),
         'data' : json.dumps(0),
         'id'   : "event_id"
    })
    yield sse_pack(msg)
    event_id += 1            
    msg['event'] = 'message'
    while True:
        # block until you get new data (from a queue, pub/sub, zmq, etc.)
        msg.update({
             'event': 'message',
             'data' : json.dumps(queue.get()),
             'id'   : event_id
        })
        print "size:  "+str(queue.qsize())
    #print sse_pack(msg)
        try:    
            yield sse_pack(msg)
            event_id += 1
        except Exception:
                print "por aqui tambien hemos petao"
    print "Event Closed"

   

@mxcube.get("/state")
def state():
    return json.dumps(bl_state())

@mxcube.get("/set_light_level")
def set_light_level():
    light_level = float(bottle.request.GET["light_level"])
    light_level_changed_event = gevent.event.Event()
def set_level_changed(*args):
    light_level_changed_event.set()
    mxcube.bl_setup.diffractometer_hwobj.lightMotor.connect("moveDone", set_level_changed)
    mxcube.bl_setup.diffractometer_hwobj.lightMotor.move(light_level)
    light_level_changed_event.wait()
    mxcube.bl_setup.diffractometer_hwobj.lightMotor.disconnect("moveDone", set_level_changed)
    return json.dumps(bl_state())

@mxcube.get("/set_light")
def set_light():
    put_in = int(bottle.request.GET["put_in"])
    state_changed_event = gevent.event.Event()
    def set_state_changed(*args):
        state_changed_event.set()
        mxcube.bl_setup.diffractometer_hwobj.lightWago.connect("wagoStateChanged", set_state_changed)
        if put_in:
            mxcube.bl_setup.diffractometer_hwobj.lightWago.wagoIn()
        else:
            mxcube.bl_setup.diffractometer_hwobj.lightWago.wagoOut()
            state_changed_event.wait() 
            mxcube.bl_setup.diffractometer_hwobj.lightWago.disconnect("wagoStateChanged", set_state_changed)
        return json.dumps(bl_state())

@mxcube.get("/set_zoom")
def set_zoom():
    return json.dumps(bl_state())

@mxcube.get('/sample_video_stream')
def stream_video():
    #import pdb;pdb.set_trace()
    try:
        mxcube.video.setLive(True)
    except:
        pass
    bottle.response.content_type = 'multipart/x-mixed-replace; boundary="!>"'
    while True:
        mxcube.new_frame.wait()
        frame = mxcube.new_frame.get()
        yield 'Content-type: image/jpg\n\n'+frame+"\n--!>" 

@mxcube.get("/centring")
def do_centring():
    x = int(bottle.request.GET["X"])
    y = int(bottle.request.GET["Y"])
    logging.getLogger('HWR').info("Doing centring. Clicked position is x= %s, y= %s" %(str(x),str(y)))
    if mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure is None:
        mxcube.bl_setup.diffractometer_hwobj.startCentringMethod(mxcube.bl_setup.diffractometer_hwobj.MANUAL3CLICK_MODE)
    time.sleep(0.01)
    mxcube.bl_setup.diffractometer_hwobj.imageClicked(x,y,0,0)
    time.sleep(0.1)
    # wait until motors finished moving
    while not mxcube.bl_setup.diffractometer_hwobj.isReady():
        time.sleep(0.05)
    if mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure is None or mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure.ready():
        print "false"
        return json.dumps({ "continue": False })
    else:
        print "true"
        return json.dumps({ "continue": True })

@mxcube.get('/samples')
def return_samples():
    return json.dumps(eval(samples_info))

dc_mapping={"Oscillation range":"osc_range","Oscillation start":"osc_start","Exposure time":"exp_time","Number of images":"n_images"}

@mxcube.post('/sample_field_update')
def sample_field_update():
    data =dict(request.POST.items())
    
    if 'pk' not in data:
        data['qname']= "queue_item"+str(len(q_exp))
        q_exp.append(data)

    else:
        q_exp[int(data['pk'][-1])][dc_mapping[data['name']]]=data['value']
    logging.getLogger('HWR').info("Sample field updated. Data:  "+str(q_exp))

    return

@mxcube.post('/beam_line_update')
def beam_line_update():
    print "Beam line updated"
    ret = request.POST.items()
    print ret
    if ret[0][1]=='energy':
        mxcube.energy.setPosition(float(ret[2][1]))
    elif ret[0][1]=='omega':
        mxcube.diffractometer.getObjectByRole('phi').move(float(ret[2][1]))
    elif ret[0][1]=='kappa':
        mxcube.diffractometer.getObjectByRole('kappa').move(float(ret[2][1]))    
    elif ret[0][1]=='phitablezaxis':
        mxcube.diffractometer.getObjectByRole('phiz').move(float(ret[2][1]))
    elif ret[0][1]=='apert_hor':
        mxcube.diffractometer.getObjectByRole('apert_hor').move(float(ret[2][1]))
    

@mxcube.route("/run_queue", method='GET')
def run_queue():
    print "Run queue started"
    dict(request.GET)
        
    for i in q_exp:
        if i["Type"] == "Sample":
            print "Mounting sample......  "+ i['Name']
        #gevent.sleep(1)
        elif i["Type"]=="Discrete":
            print "*******************"
            print i
            #self.execute_command("prepare_acquisition", take_dark, start, osc_range, exptime, npass, comment)
            #def prepare_acquisition(self, take_dark, start, osc_range, exptime, npass, number_of_images, comment, energy, still):
            mxcube.detector.prepare_acquisition(0,i['osc_start'],i['osc_range'],i['exp_time'],1,4,'no comment', mxcube.energy.getPosition(),0)
            mxcube.diffractometer.prepare_oscillation(i['osc_start'],i['osc_range'],i['exp_time'],1)
            print mxcube.diffractometer.getPositions()
            #the shutter openning is not really needed since the diff will automatically handle it (the fast shutter)
            print "Openning shutter......"
            mxcube.shutter.setPosition(10)
            while mxcube.shutter.getPosition() != 10:
                time.sleep(0.1)
            print "Performing discrete scan......"
            mxcube.diffractometer.do_oscillation()#q_exp['osc_start'],q_exp['osc_end'],q_exp['exp_time'],1)
            time.sleep(1)
            #wait until ready
            print "Closing shutter......"
            mxcube.shutter.setPosition(0)
            while mxcube.shutter.getPosition() != 0:
                time.sleep(0.1)
            print "Collection ended......"
            
        #kappaMotor = mxcube.diffractometer.getObjectByRole('kappa')
        #    print kappaMotor.getPosition()
        #kappaMotor.move(42.42)
        #exp_time = ret_data['exp_time']
        #osc_start = ret_data['osc_start']
        #osc_end = ret_data['osc_range']
        #n_images = ret_data['n_images']
        #gevent.sleep(1)
        #mxcube.sar.startMotorScan(42,"sample-03",str(osc_start)+' '+str(osc_end)+' '+str(n_images)+' ' +str(exp_time))
        #print ret_data
        #startMotorScan(self,sessionid=None, sampleid=None, params = self.params):

@mxcube.get("/")
@mxcube.get("/login")
def login():
    if 'proposal' in request.GET.keys() and request.GET['proposal'] != "":
        if True: #remhost  in ['localhost', localhost]:
            successful_login(request.GET)
            redirect("/mxcube")
            #response.status=303
            #response.set_header("location","/mxcube")
            return

        remaddr = request.environ['REMOTE_ADDR']
        try:
            remhost = socket.gethostbyaddr( remaddr )[0]
            localhost = socket.gethostname() 
            if True: #remhost  in ['localhost', localhost]:
                successful_login(request.GET)
                response.status=303
                response.set_header("location","/mxcube")
                return
        except:
            sys.excepthook(*sys.exc_info())
        
        # exception or remote
        redirect('http://www.google.com')
    else:
        return static_file("login.html", os.path.dirname(__file__))

@mxcube.get("/login_ispyb")
def login_ispyb():
    """
    """
    password=bottle.request.GET["password"]
    username = bottle.request.GET["username"]
    i=0
    for c in username:
        if c.isdigit():
            proposal=username[:i]
            proposal_number=username[i:]
            break
        i+=1
        login_name = ispyb.translate(proposal,"ldap")+proposal_number 
        ok, msg=ldap.login(login_name,password)
        if not ok:
            return json.dumps({"ok":0,"err":msg.capitalize()})
        prop = ispyb.getProposal(proposal,proposal_number)
        return json.dumps({"ok":1 if prop['status']['code']=='ok' else 0, "err":"ISPyB problem"})

@mxcube.get("/logout")
def logout():
    sess = request.environ.get('beaker.session')
    sess.delete()
    response.status=303
    response.set_header("location","/login")

@mxcube.route("/mxcube/proposal")
def mxcube_proposal():
    sess = request.environ.get('beaker.session')
    return { "proposal": sess.get("proposal", "") }

@mxcube.route("/mxcube")
def mxcube_html():
    sess = request.environ.get('beaker.session')
    return static_file("mxcube.html", os.path.dirname(__file__))

@mxcube.route("/sample_list")
def sample_list():
    return static_file("samples_test.html", os.path.dirname(__file__))

@mxcube.route("/<url:path>")
def serve_static_file(url):
    return static_file(url, os.path.dirname(__file__))

if __name__ == '__main__':
    run(app=mxcube_app, host="", port="8080",server=GeventServer,debug=True, reloader=True)
