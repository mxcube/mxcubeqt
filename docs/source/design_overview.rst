Design Overview
###############
Hardware objects are located in two submodules:

* `HardwareObjects <https://github.com/mxcube/HardwareObjects.git>`_ stores all hardware objects that are used within MXCuBE. It contains directories for site specific hardware objects (`EMBL <https://github.com/mxcube/HardwareObjects/tree/master/EMBL>`_, `ESRF <https://github.com/mxcube/HardwareObjects/tree/master/ESRF>`_, `MAXLAB <https://github.com/mxcube/HardwareObjects/tree/master/MAXLAB>`_, `SOLEIL <https://github.com/mxcube/HardwareObjects/tree/master/SOLEIL>`_) and directories for `detectors <https://github.com/mxcube/HardwareObjects/tree/master/detectors>`_ and `sample_changer <https://github.com/mxcube/HardwareObjects/tree/master/sample_changer>`_.
* `HardwareObjects <https://github.com/mxcube/HardwareRepository/tree/master/HardwareObjects>`_ directory in `HardwareRepository <http://github.com/mxcube/HardwareRepository>`_ holds basic hardware objects, like motors, actuators and etc.

Hardware objects are managed by `HardwareRepository <http://github.com/mxcube/HardwareRepository>`_ and each of them has a xml configuration (more detailed information here: :doc:`packages/example_files`).

The figure below shows the principal communication paths between the Hardware Repository (Hardware Objects), GUI (Framework Bricks) and
clients using the XMLRPCServer feature.

.. image:: images/design_overview.png

Further main hardware objects are described.

Queue and QueueModel
********************

The :doc:`QueueModel <packages/HardwareObjects/QueueModel>` is a key component in MxCuBE. It handles the data model for the :doc:`Queue <packages/HardwareObjects/Queue>`. Each task in the queue, is a subclass of :doc:`QueueEntry <packages/HardwareObjects/queue_entry>`, and is associated with a model data node (:doc:`TaskNode <packages/HardwareObjects/queue_model_objects>`). 
The QueueModel and is designed to be part of a MVC like pattern, where the QueueModel acts as the **Controller**. The QueueModel has a reference to one or more :doc:`RootNode <packages/HardwareObjects/queue_model_objects>` objects which contain the model.
The TreeBrick and the Queue hardware objects behaves as **views** for the QueueModel. The TreeBrick is displaying the tasks for the user while the Queue represents the exectuable 'entity'. 
The Queue contains QueueEntry objects, which each holds a reference to to a TaskNode in the model. A mapping between TaskNodes and QueueEntries can be found at the end of the file HardwareObjecs/queue_entry.py. This makes it easy to add a new type of task. The only thing that is needed is: 

* Create a TaskNode that holds any data needed to perform the task.
* Implement the logic for the task, subclassing QueueEntry
* Add the mapping.

BeamlineSetup
*************
The :doc:`BeamlineSetup <packages/HardwareObjects/BeamlineSetup>` is used like a container for hardware objects. Within the code there is a tendency to keep all hardware objects in the beamline setup and call them from gui bricks, rather then defining all hardware objects in each brick.

Session
*******
:doc:`Session <packages/HardwareObjects/Session>` module defines current MXCuBE session. In the xml of it is possible to define: synchrotron name, endstation name, beamline name and information related to the experiment: file suffix, base directory, raw data folder name etc.

ShapeHistory and Qt4_GraphicsManager
************************************
In Qt3 version graphics are handled by :doc:`ShapeHistory <packages/HardwareObjects/ShapeHistory>`  hardware object and in Qt4 version :doc:`Qt4_GraphicsManager <packages/HardwareObjects/Qt4_GraphicsManager>` is used.

Other modules
*************
