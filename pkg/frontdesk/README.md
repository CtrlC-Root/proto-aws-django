# frontdesk

A Django-based application for tracking shipped packages.

## Development

Create a Python virtualenv, install the project's dependencies, and link the
project for development.

```bash
virtualenv -p $(which python3) env
source env/bin/activate
pip install -r requirements.txt
python setup.py develop
```

Configure development settings:

```bash
export DEBUG="True"
export SECURE_KEY="insecure_local_dev"
```

Use the provided `frontdesk` script in place of the usual `manage.py`:

```bash
frontdesk migrate
frontdesk createsuperuser
frontdesk runserver
```

## Production

Configure production settings:

```bash
export SECURE_KEY="something_secure"
export ALLOWED_HOSTS="example.com,example.net"
```

The `production` application provides several management commands accessible
through the `frontdesk` script that can be useful in production. Run the web
application using gunicorn through the `run_web` command which accepts most of
the flags `gunicorn` provides. The Django settings module and WSGI application
are automatically configured and do not need to be specified.

```bash
frontdesk run_web -w 4 -b 0.0.0.0
```

## References

* [Django Management Commands](https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/)
