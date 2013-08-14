Design Overview
===============
The figure below shows the principal communication paths between the
Hardware Repository (Hardware Objects), GUI (Framework Bricks) and 
clients using the XMLRPCServer feature.

.. image:: images/design_overview.png

Queue and QueueModel
--------------------

The :doc:`QueueModel <packages/HardwareObjects/QueueModel>` is a key component in
MxCuBE. It handles the data model for the :doc:`Queue <packages/HardwareObjects/Queue>`.
Each task in the queue, is a subclass of :doc:`QueueEntry <packages/HardwareObjects/queue_entry>`,
and is associated with a model data node (:doc:`TaskNode <packages/HardwareObjects/queue_model_objects>`).

The QueueModel and is designed to be part of a MVC like pattern, where
the QueueModel acts as the **Controller**. The QueueModel has a
reference to one or more :doc:`RootNode <packages/HardwareObjects/queue_model_objects>`
objects which contain the model.

The TreeBrick and the Queue hardware objects behaves as **views** for the
QueueModel. The TreeBrick is displaying the tasks for the user while 
the Queue represents the exectuable 'entity'.

The Queue contains QueueEntry objects, which each holds a reference to
to a TaskNode in the model. A mapping between TaskNodes and QueueEntries
can be found at the end of the file HardwareObjecs/queue_entry.py. This
makes it easy to add a new type of task. The only thing that is needed
is: 

* Create a TaskNode that holds any data needed to perform the task.
* Implement the logic for the task, subclassing QueueEntry
* Add the mapping.


BeamlineSetup
-------------
