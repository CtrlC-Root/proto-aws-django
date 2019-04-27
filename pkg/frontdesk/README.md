# frontdesk

A Django-based application for tracking shipped packages.

## Development

Create a Python virtualenv, install the project's dependencies, and link the
project for development.

```bash
pip install -r requirements.txt
python setup.py develop
```

Use the provided `frontdesk` script in place of the usual `manage.py`:

```bash
frontdesk migrate
frontdesk createsuperuser
frontdesk runserver
```
