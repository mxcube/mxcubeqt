"""

Simple demonstration of how to implement Server-sent events (SSE) in Python
using Bottle micro web-framework.
 
SSE require asynchronous request handling, but it's tricky with WSGI. One way
to achieve that is to use gevent library as shown here.
 
Usage: just start the script and open http://localhost:8080/ in your browser.
 
Based on:
- "Primer to Asynchronous Applications",
     http://bottlepy.org/docs/dev/async.html

- "Using server-sent events",
     https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events

"""
 
 
# Bottle requires gevent.monkey.patch_all() even if you don't like it.
import time, os,sys

from gevent import monkey; monkey.patch_all()
from gevent import sleep
 
from bottle import get, post, request, response, route
from bottle import GeventServer, run

# PATH settings

#APP_PATH = "/txo/Projects/MX/MXWEB/bottle/hwrep"
APP_PATH = "../hwrep"
HOPATH  = os.path.join(APP_PATH, "HardwareObjects")
XMLPATH = os.path.join(APP_PATH, "HardwareObjects.xml")


sys.path.append( APP_PATH )
sys.path.append( HOPATH )

from HardwareRepository import HardwareRepository
from HardwareRepository.dispatcher import dispatcher

hwr = HardwareRepository.HardwareRepository( XMLPATH )
hwr.connect()

devs = {
  'omega':  hwr.getHardwareObject("/omega")
}

def positionChanged( newval):
    print "newposition is ", newval

#dispatcher.connect(positionChanged, 'positionChanged', devs['omega'])

@route('/gui/<guiname>')
def guiMain(guiname):
   motor_page = open("%s.html" % guiname).read() 
   return motor_page

@route('/scripts/<script>')
def getJquery(script):
   motor_page = open("scripts/%s" % script).read()
   return motor_page

@post('/move')
def moveMotor():
    mne      = request.query['motor']
    position = request.query['to']
    print "moving  motor ",mne, " to position ", position

    motor = devs[mne]
    motor.move( float(position) )

@route('/motor/<mne>')
def getMotorInformation(mne):
    response.content_type = 'text/event-stream'
    response.cache_control = 'no-cache'
 
    print "getting information for motor ",mne

    motor = devs[mne]
    yield 'retry: 100\n\n'

    end = time.time() + 60
    while time.time() < end:
        yield 'data: mne:%s;position:%s;state:%s\n\n' % (mne, str(motor.getPosition()), str(motor.getState())) 
        sleep(0.2)

if __name__ == '__main__':
    run(host="192.168.241.205", port="8088",server=GeventServer)
