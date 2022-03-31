Panopto python-soap
===================

A python 3 soap Panopto API client that wraps the zeep library for the heavy lifting

THIS REPOSITORY IS UNSUPPORTED
------------------------------
This repository is provided as-is for general developer guidance.

The Panopto team does not support this repository.

To use the examples, move them and the contents of src to the same directory.

Basic operations:
 - create an AuthenticatedClientFactory to use for creating endpoints to SOAP services.
     - see a list of services with *get_endpoint()*
     - get a client with *get_client(service_name)*
 - use a ClientWrapper (authenticated from the above factory) to make service calls.
     - see a list of available calls with *bound_operation()*
     - see the form of a service call with *bound_operation(operation_name)*
     - call the service with *call_service(operation_name, arguments...)*

License
-------

Copyright 2018 Panopto, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Updating dependencies
---------------------

.. code:: console

    $ python3 -m pip install -r requirements.txt


Pushing a new build of the package
----------------------------------

Make sure everything builds

.. code:: console

    $ tox

If that succeeds, then you can push a source package to artifactory
(This assumes that you've defined our local artifactory as "local" in
~/.pypirc).

.. code:: console

    $ python setup.py bdist_wheel --universal upload -r local
