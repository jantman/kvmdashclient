kvmdash
=======

**Note this code is VERY alpha right now. Expect it to change a lot and maybe
  not work.**

This is the Python client (data collector) application for `kvmdash <http://github.com/jantman/kvmdash>`_

Testing
=======

Testing this client app requires libvirt-python (aka python-libvirt in some
distribution packaging systems), and the underlying libvirt libraries. The
only (as of the time of writing) version of libvirt-python on pypi is 1.2.0;
prior to this release, it was just a collection of python scripts and shared
libraries that an OS package management system dropped into site-packackages/,
not a real python package. libvirt-python requires libvirt >= 0.9.11. If that
isn't available, tox won't even be able to install dependencies, let alone
test anything.

Travis-ci is currently running on Ubuntu 12.04 LTS (precise), which has
python-libvirt 0.9.8. 
