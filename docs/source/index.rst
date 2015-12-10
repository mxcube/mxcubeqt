########################
MxCuBE Documentation
########################

MXCuBE stands for Macromolecular Xtallography CUstomized Beamline Environment.
The project started in 2005 at `ESRF <http://www.esrf.eu>`_, since then it has
been adopted by other institutes in Europe. In 2010, a collaboration
agreement has been signed for the development of MXCuBE with the following
partners:

* `ESRF <http://www.esrf.eu>`_
* `Soleil <http://www.synchrotron-soleil.fr/>`_
* `Max lab <https://www.maxlab.lu.se/>`_
* `HZB <http://www.helmholtz-berlin.de/>`_
* `EMBL <http://www.embl.org/>`_
* `Global Phasing Ltd. <http://www.globalphasing.com/>`_
* `ALBA <https://www.cells.es/en>`_
* `DESY <https://www.desy.de>`_

MXCuBE consist of 2 main parts:

* Data acquisition control layer
* Graphical user interface

.. rubric:: Data acquisition control

Data acquisition control is made of Hardware Objects. Hardware Objects are Python classes associated with a configuration XML file. Hardware Objects are instanciated by the `Hardare Repository <http://github.com/mxcube/HardwareRepository>`_.
Each Hardware Object should be based on an abstract class, defining a common API for MxCuBE. Then, implementation differs at each site depending on hardware and beamline specificities.

See the :doc:`design_overview` for more details

.. rubric:: Graphical user interface

MXCuBE has two graphical user interfaces:

* :doc:`qt_framework_overview` 
* :doc:`web_framework_overview` 

***********************************
Tutorials, examples and user manual
***********************************
* :doc:`installation_instructions_qt4`
* :doc:`installation_instructions_web`
* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
* :doc:`feature_overview`
* :doc:`packages/example_files`
* :doc:`user_manual`

***
API
***

.. toctree::
   :maxdepth: 1
   :glob:

   packages/*

*****************
Other information
*****************

* If you cite MXCuBE, please use reference:
.. note:: 
   Gabadinho, J. et al. (2010). MxCuBE: a synchrotron beamline control environment customized for macromolecular crystallography experiments. J. Synchrotron Rad. 17, 700-707

* `Full article <http://www.ncbi.nlm.nih.gov/pubmed/20724792>`_
* :doc:`mxcube_meetings`

******************
Indices and tables
******************
* :ref:`modindex`
* :ref:`search`

