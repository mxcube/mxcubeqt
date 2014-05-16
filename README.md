# mxCuBE web application - preliminary study

This branch contains an embryo mxCuBE web server, embedding
a mxCuBE application. The code was first demonstrated at the
3rd mxCuBE meeting in April, 2013.

## How to run it

*disclaimer: code will only work with Firefox > 6. Chrome, Safari or IE are **not supported.***

Once branch is checked out and additional dependencies (see below) are satisfied:

    ./bin/mxcube-server <path to Hardware Repository XML files>
    
Then, go to the [http://localhost:8080](http://localhost:8080) URL within your Firefox web browser.

The code is compatible with mxCuBE 2; you need to have a well-defined
**beamline-setup.xml** file in your XML files repository.

## Additional dependencies

[bottle](http://bottlepy.org) micro-framework is used for the web application.
It needs to be installed, follow instructions on the Bottle website.

## Technology stack

Client part built on top of:
* Twitter Bootstrap
* JQuery

Server part built on top of:
* mxCuBE 2 (including gevent)
* bottle

At the moment, sample video relies on the Camera Hardware Object, which can
rely in turn on Qub for frames decoding. So for the moment Qub is still
needed. This is just a temporary situation.
