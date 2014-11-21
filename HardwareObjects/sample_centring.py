from scipy import optimize
import numpy
import gevent.event
import math
import time
import logging
import os
import tempfile

try:
  import lucid
except ImportError:
  logging.warning("lucid cannot load: automatic centring is disabled")


def multiPointCentre(z,phis) :
    fitfunc = lambda p,x: p[0] * numpy.sin(x+p[1]) + p[2]
    errfunc = lambda p,x,y: fitfunc(p,x) - y
    p1, success = optimize.leastsq(errfunc,[1.,0.,0.],args = (phis,z))
    return p1

USER_CLICKED_EVENT = None
CURRENT_CENTRING = None
SAVED_INITIAL_POSITIONS = {}
READY_FOR_NEXT_POINT = gevent.event.Event()

class CentringMotor:
  def __init__(self, motor, reference_position=None, direction=1):
    self.motor = motor
    self.direction = direction
    self.reference_position = reference_position
  def __getattr__(self, attr):
    # delegate to motor object
    if attr.startswith("__"):
      raise AttributeError(attr)
    else:
      return getattr(self.motor, attr)
  
def prepare(centring_motors_dict):
  global SAVED_INITIAL_POSITIONS

  if CURRENT_CENTRING and not CURRENT_CENTRING.ready():
    raise RuntimeError("Cannot start new centring while centring in progress")
  
  global USER_CLICKED_EVENT
  USER_CLICKED_EVENT = gevent.event.AsyncResult()  

  motors_to_move = dict()
  for m in centring_motors_dict.itervalues():
    if m.reference_position is not None:
      motors_to_move[m.motor] = m.reference_position
  move_motors(motors_to_move)

  SAVED_INITIAL_POSITIONS = dict([(m.motor, m.motor.getPosition()) for m in centring_motors_dict.itervalues()])

  phi = centring_motors_dict["phi"]
  phiy = centring_motors_dict["phiy"]
  sampx = centring_motors_dict["sampx"]
  sampy = centring_motors_dict["sampy"] 
  phiz = centring_motors_dict["phiz"]

  return phi, phiy, phiz, sampx, sampy
  
def start(centring_motors_dict,
          pixelsPerMm_Hor, pixelsPerMm_Ver, 
          beam_xc, beam_yc,
          chi_angle = 0,
          n_points = 3):
  global CURRENT_CENTRING

  phi, phiy, phiz, sampx, sampy = prepare(centring_motors_dict)

  CURRENT_CENTRING = gevent.spawn(center, 
                                  phi,
                                  phiy,
                                  phiz,
                                  sampx, 
                                  sampy, 
                                  pixelsPerMm_Hor, pixelsPerMm_Ver, 
                                  beam_xc, beam_yc,
                                  chi_angle,
                                  n_points)
  return CURRENT_CENTRING

def ready(*motors):
  return not any([m.motorIsMoving() for m in motors])

def move_motors(motor_positions_dict):
  #import pdb; pdb.set_trace()
  def wait_ready(timeout=None):
    with gevent.Timeout(timeout):
      while not ready(*motor_positions_dict.keys()):
        time.sleep(0.1)

  wait_ready(timeout=30)

  if not ready(*motor_positions_dict.keys()):
    raise RuntimeError("Motors not ready")

  for motor, position in motor_positions_dict.iteritems():
    motor.move(position)
  
  wait_ready()
  
def user_click(x,y, wait=False):
  READY_FOR_NEXT_POINT.clear()
  USER_CLICKED_EVENT.set((x,y))
  if wait:
    READY_FOR_NEXT_POINT.wait()
  
def center(phi, phiy, phiz,
           sampx, sampy, 
           pixelsPerMm_Hor, pixelsPerMm_Ver, 
           beam_xc, beam_yc,
           chi_angle,
           n_points):
  global USER_CLICKED_EVENT
  X, Y, phi_positions = [], [], []

  phi_angle = 180.0/(n_points-1)

  try:
    i = 0
    while i < n_points:
      try:
          x, y = USER_CLICKED_EVENT.get()
      except:
          raise RuntimeError("Aborted while waiting for point selection")
      USER_CLICKED_EVENT = gevent.event.AsyncResult()
      X.append(x / float(pixelsPerMm_Hor))
      Y.append(y / float(pixelsPerMm_Ver))
      phi_positions.append(phi.direction*math.radians(phi.getPosition()))
      phi.syncMoveRelative(phi.direction*phi_angle)
      READY_FOR_NEXT_POINT.set()
      i += 1
  except:
    logging.exception("Exception while centring")
    move_motors(SAVED_INITIAL_POSITIONS)
    raise

  #logging.info("X=%s,Y=%s", X, Y)
  chi_angle = math.radians(chi_angle)
  chiRotMatrix = numpy.matrix([[math.cos(chi_angle), -math.sin(chi_angle)],
                               [math.sin(chi_angle), math.cos(chi_angle)]])
  Z = chiRotMatrix*numpy.matrix([X,Y])
  z = Z[1]; avg_pos = Z[0].mean()

  r, a, offset = multiPointCentre(numpy.array(z).flatten(), phi_positions)
  dy = r * numpy.sin(a)
  dx = r * numpy.cos(a)
  
  d = chiRotMatrix.transpose()*numpy.matrix([[avg_pos],
                                             [offset]])

  d_horizontal =  d[0] - (beam_xc / float(pixelsPerMm_Hor))
  d_vertical =  d[1] - (beam_yc / float(pixelsPerMm_Ver))


  phi_pos = math.radians(phi.direction*phi.getPosition())
  phiRotMatrix = numpy.matrix([[math.cos(phi_pos), -math.sin(phi_pos)],
                               [math.sin(phi_pos), math.cos(phi_pos)]])
  vertical_move = phiRotMatrix*numpy.matrix([[0],d_vertical])
  
  centred_pos = SAVED_INITIAL_POSITIONS.copy()
  if phiz.reference_position is None:
      centred_pos.update({ sampx.motor: float(sampx.getPosition() + sampx.direction*dx),
                           sampy.motor: float(sampy.getPosition() + sampy.direction*dy),
                           phiz.motor: float(phiz.getPosition() + phiz.direction*d_vertical[0,0]),
                           phiy.motor: float(phiy.getPosition() + phiy.direction*d_horizontal[0,0]) })
  else:
      centred_pos.update({ sampx.motor: float(sampx.getPosition() + sampx.direction*(dx + vertical_move[0,0])),
                           sampy.motor: float(sampy.getPosition() + sampy.direction*(dy + vertical_move[1,0])),
                           phiy.motor: float(phiy.getPosition() + phiy.direction*d_horizontal[0,0]) })
  return centred_pos

def end(centred_pos=None):
  if centred_pos is None:
      centred_pos = CURRENT_CENTRING.get()
  try:
    move_motors(centred_pos)
  except:
    move_motors(SAVED_INITIAL_POSITIONS)
    raise

def start_auto(camera,  centring_motors_dict,
               pixelsPerMm_Hor, pixelsPerMm_Ver, 
               beam_xc, beam_yc,
               chi_angle = 0,
               n_points = 3,
               msg_cb=None,
               new_point_cb=None):    
    global CURRENT_CENTRING

    phi, phiy, phiz, sampx, sampy = prepare(centring_motors_dict)

    CURRENT_CENTRING = gevent.spawn(auto_center, 
                                    camera, 
                                    phi, phiy, phiz,
                                    sampx, sampy, 
                                    pixelsPerMm_Hor, pixelsPerMm_Ver, 
                                    beam_xc, beam_yc, 
                                    chi_angle,
                                    n_points,
                                    msg_cb, new_point_cb)
    return CURRENT_CENTRING

def find_loop(camera, pixelsPerMm_Hor, chi_angle, msg_cb, new_point_cb):
  snapshot_filename = os.path.join(tempfile.gettempdir(), "mxcube_sample_snapshot.png")
  camera.takeSnapshot(snapshot_filename, bw=True)

  info, x, y = lucid.find_loop(snapshot_filename, debug=False,pixels_per_mm_horizontal=pixelsPerMm_Hor, chi_angle=chi_angle)
  
  if callable(msg_cb):
    msg_cb("Loop found: %s (%d, %d)" % (info, x, y))
  if callable(new_point_cb):
    new_point_cb((x,y))
        
  return x, y

def auto_center(camera, 
                phi, phiy, phiz,
                sampx, sampy, 
                pixelsPerMm_Hor, pixelsPerMm_Ver, 
                beam_xc, beam_yc, 
                chi_angle, 
                n_points,
                msg_cb, new_point_cb):
    imgWidth = camera.getWidth()
    imgHeight = camera.getHeight()
 
    #check if loop is there at the beginning
    i = 0
    while -1 in find_loop(camera, pixelsPerMm_Hor, chi_angle, msg_cb, new_point_cb):
        phi.syncMoveRelative(90)
        i+=1
        if i>4:
            if callable(msg_cb):
                msg_cb("No loop detected, aborting")
            return
    
    for k in range(2):
      if callable(msg_cb):
            msg_cb("Doing automatic centring")
            
      centring_greenlet = gevent.spawn(center,
                                       phi, phiy, phiz,
                                       sampx, sampy, 
                                       pixelsPerMm_Hor, pixelsPerMm_Ver, 
                                       beam_xc, beam_yc, 
                                       chi_angle, 
                                       n_points)

      for a in range(n_points):
            x, y = find_loop(camera, pixelsPerMm_Hor, chi_angle, msg_cb, new_point_cb) 
            #logging.info("in autocentre, x=%f, y=%f",x,y)
            if x < 0 or y < 0:
              for i in range(1,5):
                logging.debug("loop not found - moving back")
                phi.syncMoveRelative(-20)
                xold, yold = x, y
                x, y = find_loop(camera, pixelsPerMm_Hor, chi_angle, msg_cb, new_point_cb)
                if x >=0:
                  if y < imgHeight/2:
                    y = 0
                    if callable(new_point_cb):
                        new_point_cb((x,y))
                    user_click(x,y,wait=True)
                    break
                  else:
                    y = imgHeight
                    if callable(new_point_cb):
                        new_point_cb((x,y))
                    user_click(x,y,wait=True)
                    break
                if i == 4:
                  logging.debug("loop not found - trying with last coordinates")
                  if callable(new_point_cb):
                      new_point_cb((xold,yold))
                  user_click(xold, yold, wait=True)
              phi.syncMoveRelative(i*20)
            else:
              user_click(x,y,wait=True)

      centred_pos = centring_greenlet.get()
      end(centred_pos)
                 
    return centred_pos
    
