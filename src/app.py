"""
   Sample list
  
   Image 
"""

import time
import os
import sys
import json
import socket

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

mxcube = bottle.Bottle()
mxcube_app = SessionMiddleware(mxcube, session_opts)

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
      hwr.connect()

      mxcube.new_frame = gevent.event.AsyncResult()
      mxcube.bl_setup = hwr.getHardwareObject("/beamline-setup")

      mxcube.video = hwr.getHardwareObject("/camera")
      mxcube.video.connect("imageReceived", new_sample_video_frame_received)
 
  return json.dumps(bl_state())

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
    mxcube.video.setLive(True)
    bottle.response.content_type = 'multipart/x-mixed-replace; boundary="!>"'
    while True:
        mxcube.new_frame.wait()
        frame = mxcube.new_frame.get()
        yield 'Content-type: image/jpg\n\n'+frame+"\n--!>" 

@mxcube.get("/centring")
def do_centring():
  x = int(bottle.request.GET["X"])
  y = int(bottle.request.GET["Y"])

  if mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure is None:
      mxcube.bl_setup.diffractometer_hwobj.startCentringMethod(mxcube.bl_setup.diffractometer_hwobj.MANUAL3CLICK_MODE)
  time.sleep(0.01)
  mxcube.bl_setup.diffractometer_hwobj.imageClicked(x,y,0,0)
  time.sleep(0.1)
  # wait until motors finished moving
  while not mxcube.bl_setup.diffractometer_hwobj.isReady():
       time.sleep(0.05)
  if mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure is None or mxcube.bl_setup.diffractometer_hwobj.currentCentringProcedure.ready():
    return json.dumps({ "continue": False })
  else:
    return json.dumps({ "continue": True })

@mxcube.get('/samples')
def return_samples():
    return json.dumps(eval(samples_info))

@mxcube.post('/sample_field_update')
def sample_field_update():
    print "Sample field updated"
    print request.POST.items()
    return 

@mxcube.get("/")
@mxcube.get("/login")
def login():
    if 'proposal' in request.GET.keys() and request.GET['proposal'] != "":
        if True: #remhost  in ['localhost', localhost]:
             successful_login(request.GET)
             response.status=303
             response.set_header("location","/mxcube")
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
   run(app=mxcube_app, host="", port="8080",server=GeventServer)
