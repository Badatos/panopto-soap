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


Mode d’emploi
=============

Pré-requis
----------
Dupliquez le fichier settings-dist.ini en settings.ini dans le dossier config, et indiquez-y vos infos.

.. code:: console

    $ cp config/settings-dist.ini config/settings.ini

Étape 1
-------
Créez une base de donnée locale.
Nous utilisons par exemple mysql.
Pour créer l'ensemble des tables nécessaires, lancez `make createDB`.
N'oubliez-pas d'indiquer dans votre settings.ini les infos de votre DB sous "[migration_DB]".


Étape 2
-------
Assurez-vous d'avoir rempli les infos [Panopto] de votre settings.ini
Lancez la commande `make import_sessions' pour remplir la BDD locale avec l'ensemble des session de Panopto.

Étape 3
-------
Lancer ensuite une premiere fois le script `make export_json` pour obtenir un fichier User.json des utilisateurs de Panopto.

Étape 4
-------
Rendez-vous sur Pod pour importer le json obtenu ci-dessus.
(suivez la doc https://www.esup-portail.org/wiki/display/ES/Reprise+de+l%27existant%2C+entre+la+version+1.x+et+2.x)

Étape 5
-------
À partir de là, c'est pas surper propre désolé ^^.
Maintenant qu'on a importé les utilisateurs dans Pod, il faut maj la base locale.
Appelez en python 'export2json.synchroPodUsers()'

Étape 6
-------
# Quand on est certains de tous nos ids utilisateurs, on exporte les vidéos
Appelez en python 'export2json.exportPods()'

Étape 7
-------
Retournez sur Pod pour importer le json obtenu ci-dessus.
