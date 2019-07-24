import os
import sys

from django.core.management.base import BaseCommand, CommandError

from celery.bin.celery import main as celery_main

class Command(BaseCommand):
    help = 'Runs the task worker using Celery'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        celery_main(argv=['celery', '-A', 'frontdesk', 'worker', '-l', 'info'])
