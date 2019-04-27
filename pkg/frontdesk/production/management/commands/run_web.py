import os
import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.wsgi import get_wsgi_application
from gunicorn.app.base import BaseApplication
from gunicorn import debug


class DjangoApplication(BaseApplication):
    def load_config(self):
        # called automatically as part of BaseApplication.__init__() so not
        # very useful because at that point we haven't set up the Django
        # parser or gotten the parsed arguments back from it
        pass

    def add_arguments(self, parser):
        # retrieve the configuration options in sorted order ignoring any we
        # do not want the user to have access to
        keys = sorted(self.cfg.settings, key=self.cfg.settings.__getitem__)
        keys.remove('check_config') # already know the wsgi app will load
        keys.remove('config')       # do not want to parse config file
        keys.remove('paste')        # do not want to parse paste config file
        keys.remove('pythonpath')   # conflicts with django argument
        keys.remove('daemon')       # do not want this in production
        keys.remove('reload')       # do not want this in production
        keys.remove('reload_engine')
        keys.remove('reload_extra_files')

        # add parser arguments for selected configuration options
        for key in keys:
            self.cfg.settings[key].add_option(parser)

    def load_config_from_args(self, args):
        for key, value in args.items():
            if key in self.cfg.settings and value:
                self.cfg.set(key.lower(), value)

    def load(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontdesk.settings')
        return get_wsgi_application()

    def run(self):
        # enable detailed debug logging
        if self.cfg.spew:
            debug.spew()

        # change working directory
        os.chdir(self.cfg.chdir)

        # run gunicorn
        super().run()


class Command(BaseCommand):
    help = 'Runs the web application using Gunicorn'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = DjangoApplication()

    def add_arguments(self, parser):
        self._app.add_arguments(parser)

    def handle(self, *args, **options):
        self._app.load_config_from_args(options)
        sys.exit(self._app.run())
