MxCuBE-2.0 Documentation
========================
MxCuBE stands for macromolecular xtallography customized beamline environment;
the project started in 2005 at `ESRF <http://www.esrf.eu>`_, since then it has
been adopted by other institutes in Europe. In 2010, a collaboration
agreement has been signed for the development of mxCuBE with the following
partners:

* ESRF
* `Soleil <http://www.synchrotron-soleil.fr/>`_
* `Max lab <https://www.maxlab.lu.se/>`_
* `HZB <http://www.helmholtz-berlin.de/>`_
* `EMBL <http://www.embl.org/>`_
* `Global Phasing Ltd. <http://www.globalphasing.com/>`_

MxCuBE consist of 2 main parts:

* A graphical user interface
* Data acquisition control layer

.. rubric:: Graphical user interface

MxCuBE GUI is built on top of the `Bliss Framework-2 <http://github.com/mxcube/BlissFramework>`_,
a tool developed at ESRF for building graphical interfaces based on Python 2.x
and the Qt 3 toolkit, especially designed for beamline experiment control applications.

.. rubric:: Data acquisition control

Data acquisition control is made of Hardware Objects. Hardware Objects are Python
classes associated with a configuration XML file. Hardware Objects are instanciated
by the `Hardare Repository <http://github.com/mxcube/HardwareRepository>`_.

Each Hardware Object should be based on an abstract class, defining a common API
for MxCuBE. Then, implementation differs at each site depending on hardware and
beamline specificities.

See the :doc:`design_overview` for more details


Tutorials and Examples
----------------------
* :doc:`installation_instructions`
* :doc:`packages/example_files`

API
---
.. toctree::
   :maxdepth: 1
   :glob:

   packages/*

Other information
----------------------
* :doc:`mxcube_meetings`

Indices and tables
------------------
* :ref:`modindex`
* :ref:`search`

