import pytest
import gevent.event
import time

@pytest.fixture
def omega(blsetup):
  diffractometer = blsetup.diffractometer_hwobj
  omega = diffractometer.getObjectByRole("phi")
  yield omega
  omega.init()

def test_ready(omega):
  assert omega.isReady()
  assert omega.getState() == omega.READY

def test_move(omega):  
  omega.move(100)
  assert omega.getState() == omega.MOVING
  omega.waitEndOfMove()  
  assert pytest.approx(omega.getPosition(), 100)
  assert omega.getState() == omega.READY

def test_sync_move(omega):
  omega.syncMove(100)
  assert omega.getState() == omega.READY
  assert pytest.approx(omega.getPosition(), 100)
  
def test_events_callbacks(omega):
  moving = gevent.event.Event()
  ready = gevent.event.Event()
  event_pos = 0
  t0 = time.time()
 
  def state_changed(state):
    if state == omega.READY:
      ready.set()
    elif state == omega.MOVING:
      moving.set()

  def position_changed(position):
    event_pos = position

  omega.connect("positionChanged", position_changed)
  omega.connect("stateChanged", state_changed)
  omega.move(100)

  moving.wait()
  ready.wait()
  assert pytest.approx(time.time() - t0, 1)
  assert pytest.approx(event_pos, 100) 
