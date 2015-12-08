############################################
How to install and run web version of MXCuBE
############################################

This page will describe the steps required to successfully install and launch the web version of MXCuBE, aka MXCuBE3.
Before installing packages it might be useful to have a look at configuring 
a virtual environment, so you do not change your system. For example `here <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_

Note that you need to install the pip tool, see `here <https://pypi.python.org/pypi/pip>`_; 
as well as Node v 4.2.2 see `here <https://nodejs.org/en/>`_, 
and the Node Package Manager (npm) v2.14.x `here <https://www.npmjs.com/package/npm>`_. 
Be very carefull with the version numbers, otherwise the client interface might not work at all.

*********************
Getting code from git
*********************

.. code-block:: bash

   git clone git@github.com:mxcube/mxcube3.git

Initialize the HardwareRepository and HardwareObjects submodules:

.. code-block:: bash

   cd mxcube3
   git submodule init
   git submodule update

So, at this point your local copy should contain the latest version 
of the repo and all the required mxcube internals. But before launching 
the application some python packages must be installed.

******************************
Installing python requirements
******************************

All the requirements are in **requirements.txt** file, which is a list of all 
the packages and their respective versions. So, just type the following:

.. code-block:: bash

   pip install -r requirements.txt

It will download and install all the missing python packages. 
Be carefull with the permissions if you are not using a virtual environment.

******************
Running the server
******************

Assuming that previous steps were successful, now it's time to launch the server. 
The repository already contains a mockup folder for the configuration of 
the hardware objects (**test/HardwareObjectsMockup.xml**). Just type:

.. code-block:: bash

   python mxcube3-server -r test/HardwareObjectsMockup.xml

.. code-block:: bash

   * Running on http://0.0.0.0:8082/
   * Restarting with reloader
   ERROR:HWR:Cannot load Hardware Object "/session" : file not found.
   WARNING:root:Could not find autocentring library, automatic centring is disabled
   INFO:HWR:initializing camera object
   INFO:HWR:going to poll images
   WARNING:HWR:MiniDiff: sample changer is not defined in minidiff equipment /minidiff-mockup
   WARNING:HWR:MiniDiff: wago light is not defined in minidiff equipment /minidiff-mockup

Now it's time to go to http://w-v-kitslab-mxcube-0:8082/ and have fun. 
You can change the port in **mxcube3-server:L8**, the **0.0.0.0** address means that 
the server is listening in all IP addresses on your local machine. 

*************
Running client
*************

It is also possible to test the web interface without worrying about the server. 
In this case, no mockups are needed and all the calls that are supposed to be sent 
to the server will not have any effect, but again, you can have a look at how 
the interface looks. We are using **webpack development server** for that purpose.

First you need to install the requirements for the web client, 
you can have a look at **package.json** if you are curious.

.. code-block:: bash

   npm install

And then, run webpack in development mode:

.. code-block:: bash

   npm start

And finally, open a web browser a go to http://localhost:8090. 
