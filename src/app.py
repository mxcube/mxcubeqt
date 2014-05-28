import os
import sys
import gevent
import gevent.event
import bottle
import json
import time
import Image
import cStringIO
import base64
import numpy
import zlib
from HardwareRepository import HardwareRepository

mxcube = bottle.Bottle()
bl_setup = None
new_frame = None

@mxcube.route('/')
def mxcube_application():
  return bottle.static_file("mxcube.html", root=os.path.dirname(__file__))

@mxcube.route('/:filename')
def send_static(filename):
  return bottle.static_file(filename, root=os.path.dirname(__file__))
@mxcube.route('/css/:filename')
def send_static_css(filename):
  return bottle.static_file(filename, root=os.path.join(os.path.dirname(__file__), 'css'))
@mxcube.route('/js/:filename')
def send_static_js(filename):
  return bottle.static_file(filename, root=os.path.join(os.path.dirname(__file__), 'js'))
@mxcube.route('/img/:filename')
def send_static_img(filename):
  return bottle.static_file(filename, root=os.path.join(os.path.dirname(__file__), 'img'))

def new_sample_video_frame_received(img, width, height, *args):
  global new_frame
  raw_data = img.bits().asstring(img.numBytes())  
  im = Image.fromstring("RGBX", (width,height), raw_data)
  b,g,r,x = im.split()
  rgb_im = Image.merge("RGB",(r,g,b))
  jpeg_buffer = cStringIO.StringIO()
  rgb_im.save(jpeg_buffer, "JPEG")  
  t0=time.time()
  data=base64.b64encode(jpeg_buffer.getvalue())
  #print 'size=',len(data), 'encoded in', time.time()-t0, "seconds"
  new_frame.set(data)

def bl_state():
  return {"resolution": str("%3.4f" % bl_setup.resolution_hwobj.getPosition()),
           "energy": str("%2.4f" % bl_setup.energy_hwobj.getCurrentEnergy()),
           "light": str("%1.2f" % bl_setup.diffractometer_hwobj.lightMotor.getPosition()),
           "light_state": bl_setup.diffractometer_hwobj.lightWago.getWagoState(),
           "transmission": str("%3.2f" % bl_setup.transmission_hwobj.getAttFactor()),
           "zoom": 0,
           "pixelsPerMmY": bl_setup.diffractometer_hwobj.pixelsPerMmY,
           "pixelsPerMmZ": bl_setup.diffractometer_hwobj.pixelsPerMmZ }

@mxcube.get('/init')
def init():
  global bl_setup
  global new_frame

  cmdline_args = bottle._cmd_args[1:]
  hwr_directory = cmdline_args[0]

  if not bl_setup:
      hwr = HardwareRepository.HardwareRepository(hwr_directory)
      hwr.connect()

      new_frame = gevent.event.AsyncResult()
      bl_setup = hwr.getHardwareObject("/beamline-setup")
      bl_setup.diffractometer_hwobj.camera.connect("imageReceived", new_sample_video_frame_received)
      bl_setup.diffractometer_hwobj.camera.setLive(True)
 
  return json.dumps(bl_state())

@mxcube.get("/state")
def state():
  return json.dumps(bl_state())

@mxcube.get("/login")
def login():
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

@mxcube.get("/set_light_level")
def set_light_level():
  light_level = float(bottle.request.GET["light_level"])
  light_level_changed_event = gevent.event.Event()
  def set_level_changed(*args):
    light_level_changed_event.set()
  bl_setup.diffractometer_hwobj.lightMotor.connect("moveDone", set_level_changed)
  bl_setup.diffractometer_hwobj.lightMotor.move(light_level)
  light_level_changed_event.wait()
  bl_setup.diffractometer_hwobj.lightMotor.disconnect("moveDone", set_level_changed)
  return json.dumps(bl_state())

@mxcube.get("/set_light")
def set_light():
  put_in = int(bottle.request.GET["put_in"])
  state_changed_event = gevent.event.Event()
  def set_state_changed(*args):
    state_changed_event.set()
  bl_setup.diffractometer_hwobj.lightWago.connect("wagoStateChanged", set_state_changed)
  if put_in:
    bl_setup.diffractometer_hwobj.lightWago.wagoIn()
  else:
    bl_setup.diffractometer_hwobj.lightWago.wagoOut()
  state_changed_event.wait() 
  bl_setup.diffractometer_hwobj.lightWago.disconnect("wagoStateChanged", set_state_changed)
  return json.dumps(bl_state())

@mxcube.get("/set_zoom")
def set_zoom():
  return json.dumps(bl_state())

@mxcube.get('/sample_video_stream')
def stream_video():
  compressor = zlib.compressobj()
  bottle.response.content_type = "text/event-stream"
  bottle.response.add_header("Connection", "keep-alive")
  bottle.response.add_header("Cache-Control", "no-cache, must-revalidate")
  bottle.response.add_header("Content-Encoding", "deflate")
  bottle.response.add_header("Transfer-Encoding", "chunked")
  while True:
      jpeg_data = new_frame.get()
      yield compressor.compress("data: %s\n\n" % jpeg_data)
      yield compressor.flush(zlib.Z_SYNC_FLUSH)

@mxcube.get("/centring")
def do_centring():
  x = int(bottle.request.GET["X"])
  y = int(bottle.request.GET["Y"])

  if bl_setup.diffractometer_hwobj.currentCentringProcedure is None:
      bl_setup.diffractometer_hwobj.startCentringMethod(bl_setup.diffractometer_hwobj.MANUAL3CLICK_MODE)
  time.sleep(0.01)
  bl_setup.diffractometer_hwobj.imageClicked(x,y,0,0)
  time.sleep(0.1)
  # wait until motors finished moving
  while not bl_setup.diffractometer_hwobj.isReady():
       time.sleep(0.05)
  if bl_setup.diffractometer_hwobj.currentCentringProcedure is None or bl_setup.diffractometer_hwobj.currentCentringProcedure.ready():
    return json.dumps({ "continue": False })
  else:
    return json.dumps({ "continue": True })
