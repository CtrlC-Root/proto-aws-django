:colorscheme shirotelin
:StartPresenting
:Goyo 80%x100%

pex requests
pex youtube-dl -o youtube.pex -c youtube-dl
pex -v pkg/frontdesk/ -r pkg/frontdesk/requirements.txt --disable-cache -c frontdesk -o example.pex

frontdesk runserver
frontdesk run_web -w 2 -b 0.0.0.0:8000
frontdesk run_worker

~~~~

Django in Production with PEX
=============================

Alexandru Barbur

~~~~

About Me
========

* Past:
  * Software Engineer
  * DevOps Engineer

* Current:
  * Senior DevOps Engineer
  * Nimbis Services, Inc.

~~~~

Background
==========

* Python Packaging
* Django Framework

~~~~

Outline
=======

* Packaging Tools
* Django Integration
* Production Deployment
* Extras

~~~~

Packaging Tools: Virtualenv
===========================

* Not Portable
* Requires Build Tools
* Multiple Entry Points

~~~~

Packaging Tools: PEX
====================

* Portable
* Requires Python Interpreter
* Single Entry Point

~~~~

Django Integration
==================

* Entry Point
* Management Commands
  * Gunicorn Web Server
  * Celery Task Worker

~~~~

Production Deployment
=====================

* Django Settings
* Services
  * Gunicorn Web Server
  * Celery Task Worker

~~~~

Extras
======

* Django Management Commands
  * Database Migrations (`migrate`)
  * Database Console (`dbshell`)
  * Debug Shell (`shell_plus`)

~~~~

Contact
=======

https://github.com/CtrlC-Root/proto-aws-django

Personal: `alex@ctrlc.name`
Work: `alexandru.barbur@nimbisservices.com`
