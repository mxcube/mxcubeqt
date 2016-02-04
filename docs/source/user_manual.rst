Qt version user manual
#############################

This manual describes :ref:`graphical user interface <gui>` of MXCuBE
and basic operations how to run a necessary data collection (see :ref:`How to's section <howto>`).
GUI layout described in this manual could differ from the actual MXCuBE GUI at the beamline.

.. _gui:

***************************
1. Graphical User Interface
***************************

In this section  the graphical user interface is described.
:ref:`Main screen <figure_main_screen>` of MXCuBE is divided into areas:

1. :ref:`Login and proposal <login_and_proposal>`
2. :ref:`Sample list and data collection queue <sample_list_queue>`
3. :ref:`Sample video and centring <sample_video_centring>`
4. :ref:`Beam definition tools <beam_definition>`
5. :ref:`Collection methods <collection_methods>`
6. :ref:`Machine status <machine_status>`
7. :ref:`Logging and chat <logging_chat>`

.. _figure_main_screen:

.. figure:: images/manual_main_screen.png
   :scale: 30 %
   :alt: manual_main_screen

   Fig. 1. Main screen.

Further each area is described in details.

.. _login_and_proposal:

1.1. Login and proposal
=======================

Area is used to identify user and link ISPyB with MXCuBE. 
Depending on the beamline one of two authentication methods is possible:

1. User is authenticated automaticaly based on the computer login name. In this case MXCuBE retrieves all proposals associated with current user and populates combobox. Proposal that have a session on the current day is selected as active proposal.

.. figure:: images/manual_ispyb_proposal.png
   :scale: 80 %
   :alt: manual_ispyb_proposal

2. User manually has to enter user name and password.

After a **successfull login**:

* Proposal combobox becomes available and if several proposals are found then user canselect the neccessary proposal from combobox.
* Data collection methods and sample tree becomes available.
* The path where user's data are recorded will apper in the collection method area.

If **no proposal** is found then informations is not stored in ISPyB.

.. _sample_list_queue:

1.2 Sample list and data collection queue
=========================================

Screen area is used to choose sample mounting mode and control execution of the task queue.

1.2.1. Basic operations with sample entry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Select the sample mounting mode.

* Manually mounted
* Sample changer
* Plate
* Mounted sample

.. figure:: images/manual_sample_mount_mode.png
   :scale: 80 %
   :alt: manual_sample_mount_mode

Based on the beamline configuration sample changer availability and type could differ.

2. Select the default sample centring mode:

* Manual: manual 3 click centring procedure.
* Semi automatic: auto-loop centring requesting user validation (most common option).
* Fully automatic: auto-loop centring without user validation (for automatic pipelines).

.. figure:: images/manual_sample_centring_mode.png
   :scale: 80 %
   :alt: manual_sample_centring_mode

3. Show sample changer details.
4. Synchronize with ISPyB database to display a sample list.
5. In sample changer mode: sample list sorted by puck appears, 1:1 = puck1: sample1
6. Delete the selected collection(s).
7. Pause the running task queue.

.. figure:: images/manual_sample_tree_manual.png
   :scale: 80 %
   :alt: manual_sample_tree_manual

.. figure:: images/manual_sample_tree_sc.png
   :scale: 80 %
   :alt: manual_sample_tree_sc

1.2.2. Detailed information about the sample tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Sample list not updated with ISPyB content.
2. Sample list updated with ISPyB content.
3. Tick the box corresponding to:

* a puck, to collect every tasks for this puck when clicking on “collect queue”.
* a sample line, to collect every tasks for this sample when clicking on “collect queue”.
* a particular task, to collect only this task when clicking on “collect queue”.

.. figure:: images/manual_sample_tree_ispyb.png
   :scale: 80 %
   :alt: manual_sample_tree_ispyb

4. Sample status: 

* blue: mounted on the goniostat.
* black: selected.
* no color: not selected.

5. List of tasks done or to be performed.

* green: done
* red: failed
* yellow: done but no result
* no color: to be done

.. figure:: images/manual_sample_tree_colors.png
   :scale: 80 %
   :alt: manual_sample_tree_colors

6. Double click on the task to see the task plan/details (if not performed yet) 
or results (if performed).

.. figure:: images/manual_sc_brick.png
   :scale: 80 %
   :alt: manual_sc_brick

1.2.3. Sample changer controls
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _sample_video_centring:

1.3. Sample video and centring
==============================

Sample position is defined by diffractometer motors:

.. figure:: images/manual_motor_control.png
   :scale: 80 %
   :alt: manual_motor_control

1. Motor name.
2. Current value. To change it wite a new value and press Enter.
3. Move the current value op or down by a step.
4. Step definition.

1.3.1. Sample positioning tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: images/manual_sample_control.png
   :scale: 50 %
   :alt: manual_sample_control.png

1. Holder length
2. Front light
3. Back light
4. Zoom

1.3.2. Main tools
^^^^^^^^^^^^^^^^^

.. figure:: images/manual_main_tools.png
   :scale: 50 %
   :alt: manual_main_tools

1. Three click centering of the sample.
2. Save current centred position.
3. Create helical line (select two centring points to create a line).
4. Draw 2D mesh.
5. Autofocus.
6. Take a snapshot (automatically done at the data collection start)
7. Crystal visual realign.
8. Select all centring points.
9. Delete all centring points.
10. Auto centering of the sample.

The same functions are available via a popup menu. Do a right click on the screen to show tools options.

.. figure:: images/manual_left_click1.png
   :scale: 80 %
   :alt: manual_left_click1

.. figure:: images/manual_left_click2.png
   :scale: 80 %
   :alt: manual_left_click2

.. _beam_definition:

1.4. Beam definition tools
==========================

1. Select aperture.
2. Select horizontal and vertical slit size.
3. Select beam focusing mode (check if available at the beamline).
4. Final beam size at sample.

.. _collection_methods:

1.5. Collection methods
=======================


1. Collection method option (NB : For more information on the different options please refer to the “How to” section
).
2. Data location is a comman part for all collection methods:

* Folder/Subdirectories below the RAW_DATA directory of your session. Automatically filled with "Acronym-samplename" if a sample list from ISPyB is synchronised.
* Prefix of image: Automatically filled with “ACRONYM-samplename” if a sample list from ISPyB is synchronised

* Run number is incremented for each experiment from the same method.

3. For each collection method, once you have adjusted the parameters, "Add to queue" will add the collection to the selected sample(s) and display it in the queue of the sample list area. 

1.5.1. Standart collection
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the standard collection when you know your diffraction plan

.. figure:: images/manual_create_dc_parameters.png
   :scale: 60 %
   :alt: create_dc

1. Fill in the data collection parameters
2. Tick if you want to start the oscillation at a particula angle (default is current angle).
3. If kappa and phi angles are adjusted then a new centring task with selected kappa and phi will be added. See (How to's section for more information).
4. Tick if you want to use peak, inflection point and an energy from an energy scan.
5. Tick to collect in a shutterless mode (ticked by default).
6. If necessary adjust processing parameters and tick "Run autoprocessing" 
(not ticked by default) to run automatic EDNA processing.

1.5.2. Characterisation
^^^^^^^^^^^^^^^^^^^^^^^

Use the characterisation option when you want to automatically obtain a diffraction plan from EDNA.

.. figure:: images/manual_create_char_parameters.png
   :scale: 60 %
   :alt: create_char

1. Choose the number of images taken to characterise the crystal (1, 2 or 4).
2. Tick if you want to start the oscillation at a particular angle.
3. To do a data collection with the same parameters but at different kappa angles please see the “how to” section.
4. Select the complexity of the diffraction plan you accept (1 or multiple subwedges).
5. Tick if you want that EDNA takes the radiation damage into account (ticked by default).
6. Tick if you want a diffraction plan for anomalous phasing.
7. Force EDNA to use the space group you provide.
8. Provide vertical dimensions of your crystal (2 measures 90° apart, see “How to: measure a crystal” section). It will be used by RADDOSE for dose absorption prediction. 
9. Untick "Characterisation" group box to take reference images but not execute EDNA characterisation


1.5.3. Helical collection
^^^^^^^^^^^^^^^^^^^^^^^^^

Use the helical collection to collect along a specified line to minimize radiation damage

.. figure:: images/manual_create_helical.png
   :scale: 60 %
   :alt: create_helical

1. Add line(s) to define path of the helical collection (see how to section)
2. Fill in the different parameters from your diffraction plan
3. Tick if you want to start the oscillation at a particular angle
4. Tick if you want to perform MAD experiment
5. Tick to collect in shutterless mode (ticked by default)
6. Fill in if you want to force a particular space group in the EDNA auto-processing.

1.5.4. Energy scan
^^^^^^^^^^^^^^^^^^

Perform an energy scan if you expect your crystal to contain a particular element that might be excited (Selenium, Iron, Magnesium...)

.. figure:: images/manual_create_energyscan.png
   :scale: 60 %
   :alt: create_energyscan

1 Select an element in the periodic table and click on “Add to queue”.


1.5.5. XRF spectrum
^^^^^^^^^^^^^^^^^^^

.. figure:: images/manual_create_xrfspectrum.png
   :scale: 60 %
   :alt: create_xrf_spectrum

1 Enter the count time and add to queue.
2 and 2’ Tick the XRF spectrum parameters box and choose where to save your data (NB : to know more about XRF spectrum go to “how to” section).

1.5.6. Advanced
^^^^^^^^^^^^^^^

“Advanced” displays collection types made of task and decision series. Example: “X-ray centering” will center the best part of your crystal in the beam by doing a MESH scan followed by a line scan at 90° and will analyse the diffraction images
For more information on the different advanced options please refer to “How to” section

.. figure:: images/manual_create_advanced.png
   :scale: 60 %
   :alt: create_advanced

.. _machine_status:

1.6. Machine status
===================

1. Machine current and Synchrotron filling mode.
2. Photon flux at sample position (check if available).
3. Beamline energy. To adjust on tunable beamline: enter a value in the green box and press enter.
4. Maximum resolution recorded at the edge of the detector. To adjust: enter a value in the green box and press enter.
5. Beam transmission. To adjust: enter a value in the green box and press enter.
6. Unlock the hutch doors.
7. Open/ Close the safety shutter. Not accessible when the experimental hutch door is open. Open safety shutter when the hutch doors are interlocked.
8. Open/ Close the Fast shutter.
9. Information about detector: temperature, humidity and status.
10. Remote access menu (local contact only).

.. figure:: images/manual_mach_info.png
   :scale: 30 %
   :alt: mach_info

.. _logging_chat:

1.7. Log and chat
=================

Dialogue area : here MXCuBE indicates what it is doing or its status. It will flashes orange when a new information is displayed or when user input is required.


.. _howto:

***********
2. How to's
***********

2.1. Use the basics of MXCuBE
=============================

**In basic mode**:

1. Log-in in MXCuBE.
2. Select a sample.
3. Center it and save.
4. Select a collection method and add to queue.
5. Collect queue.

**In pipeline mode (semi or fully automatic)**:

1. Log-in MXCuBE.
2. Select the semi or fully automatic centring mode.
3. Select a list of sample: Press Ctrl key while clicking on sample name or Press shift key and select 1st and last sample name or Select the first sample name and drag to the last sample name.
4. Select a collection method, adjust parameters as required and add to queue.
5. Collect queue.


2.2. Link your samples with ISPyB
=================================

Why linking my samples from ISPyB to MXCuBE ?

This action will allow you to view your samples (described in IPSYB) in the MXCuBE sample list and link your samples to the data collections.
Facilitate your experiment (image prefix and directories are automatically filled in MXCuBE).

**In ISPyB**:

* Easy grouping of your data collections per sample.
* Easy searches by sample and/or by protein acronym to list all experiments performed over the various sessions.

1. Prepare experiment in ISPYB (as described in ISPYB manual).
2. Log-in in MXCuBE – Choose sample changer mode.
3. Synchronize with ISPyB.
4. View your sample list -> “1:1” becomes “1:1- Acronyme-sample1”.

2.3. Select a sample from sample changer and mount it
=====================================================

1. Click on a sample to select it. The sample name will be highlighted in black
2. Right click to access the sample changer mounting menu and click on mount
3. To un-mount manually a mounted sample, right click on the sample name to access the sample changer mounting menu then select un-mount

2.5. Create a new collection
============================

2.5.1. Center your sample and save a centring position
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Dialogue box : After auto loop-centring is finished you can save the current position or re-center.
2. To re-center, click 3 times on the point you want to center in the beam (red cross).
3. Save this position (mandatory to start a collection), a yellow circle with a number appears .
4. Once selected, the yellow crossed circle becomes bold green.

2.5.2. Create a task by using created centring position
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Having a sample selected and a position saved and selected for this sample (see previous page):

1. Fill in the parameters and Add to queue NB : If you did not center your sample or select the centered position before starting your collection, MXCuBE will automatically add a centring task to the queue.
2. The corresponding collection will be added to the queue on the sample list -> Click on “Collect queue” NB: In the queue, each task will be associated to the corresponding number of the selected position.
3. A confirmation message will appear -> Click continue. 
4. You can stop, pause or continue the process at any time (effective at the end of the current task).
5. When finished, sample list will become green (if successful), yellow or red. If results are expected (EDNA characterisation...) double click on the result line to view them.

2.5.3. Perform same collection method on several positions of one sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow this process to perform the same action on various parts of the same sample. 
Example: EDNA characterisation

1. On the mounted sample centre and save several positions (all numbered and yellow except the last one, bold and green).
2. Select all : press ctrl key + select each yellow ring on sample view.
3. Select a task to add (here EDNA characterisation) and press “Add to queue”.
4. Collect queue: in that particular case, an EDNA characterisation is performed on each. saved position and a diffraction plan is proposed for each position.

NB: It is possible at this level to rank the positions automatically within ISPyB (see ISPyB
manual) and to select the crystal part which is of best quality.

2.5.3. Perform same collection method on multiple samples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow this process to perform the same action(s) on each sample of a selected pool.
Example: EDNA characterisation on each sample to select the best suitable crystal of the pool.

1. Select the samples of interest in the sample list:

* by selecting the 1st one of the series and pressing shift key while selecting the last one.
* or by selecting all samples of interest one by one while pressing the Ctrl key.

2. Above sample list, select fully automatic or semi-automatic (Centring type).
3. Select a task to add (here EDNA characterisation...) and press “Add to queue”.
4. If semi-automatic centring was selected, a centring step is added to the queue. For each sample, press continue to accept the automatic centring or re-center. This is not the case in fully automatic mode.
5. “Collect queue” will collect all ticked tasks from the queue (untick a task if you do not want it to be performed straightaway).

2.5.3. Perform a helical data collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the helical data collection to collect along a specified axis along the spindle axis:

1. Save two positions at the two extremities of the axis on which  you want to perform helical data collection and select them (ctrl + click).
2. And Add a guiding line for the helical collection.
3. Fill in the parameters.
4. Add to queue.
5. Check that the corresponding box is ticked and collect Queue.

NB: The saved positions are numbered and the helical collection will start at the first selected point (here “10”).

2.5.4. Define a grid for a mesh scan or a X-ray centring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Click on this icon to start grid drawing.
2. To set the grid: click on the first corner (A) then drag until you obtain the desired shape (B).
3. Select the appropriate workflow in “Collection method/ Advanced” and “Add to queue”
4. Each node of the grid will be the location of a data collection.
5. It is possible to adjust spacing between beam within the grid before or after drawing the grid.

NB: You can draw several grid to work on different part of your crystal.

2.5.5. Perform a mesh scan
^^^^^^^^^^^^^^^^^^^^^^^^^^

2.5.6. Perform a X-ray centring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.5.8. Measure an energy scan (MAD/SAD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.5.9. Measure a X-ray fluorescence (XRF) spectrum
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.6. Measure distance, angle or area
====================================

2.7. Visualy re-orient crystal
==============================

*******************
3. Trouble shooting
*******************

.. note::
   Collection method is not available (all options are light grey): No sample is selected. 

* Select one or several samples from the sample list.

.. note::
    MXCuBE does not respond anymore.

* Kill MXCuBE and restart it.

.. note::
   My sample is not mounted/unmounted when I click on mount/unmount.

* Check sample changer status through a VNC to the sample changer interface. 
* Check that nothing is blocked on the path of the sample or underneath the arm of the sample changer.
* Manually turn the pin of your sample on the magnet by 20 °.
* Try to mount/unmount your sample again.
* After 2-3 times call your local contact.

.. note::
   The queue is interrupted because the sample changer failed to upload or download a sample.

* Select the tasks by ticking them in the queue after having fixed the problem and Collect queue again.

.. note::
   I added to the queue a wrong collection method.

* Tick the box corresponding to this collection and remove it by clicking on the red bin.

.. note::
   I started a wrong collection method.

* Click on the stop button (replacing the “Collect queue” button) and trash the method by clicking on the red bin.

.. note::
   I would like to change few parameters of a collection method already added to the queue.

* Click on the line corresponding to this method in the queue. This will open tab where you can edit parameters.

