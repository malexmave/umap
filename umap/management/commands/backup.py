import os
import tarfile
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup database (postgresql) and geojsons.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Location of the backups.')

    def archive(self, source, destination):
        try:
            archive = tarfile.open(str(destination), mode='w:gz')
            archive.add(str(source), arcname='./', recursive=True,
                        exclude=os.path.islink)
        except:  # NOQA
            raise
        finally:
            archive.close()

    def handle(self, *args, **options):
        today = date.today().isoformat()
        root = Path(options['path'])
        if not root.exists():
            root.mkdir()
        database_tmp = root.joinpath('database.{}.json'.format(today))
        with database_tmp.open('w') as out:
            call_command('dumpdata', format='json', stdout=out)
        self.archive(database_tmp,
                     root.joinpath('database.{}.tar.gz'.format(today)))
        self.archive(settings.MEDIA_ROOT,
                     root.joinpath('media.{}.tar.gz'.format(today)))
        os.unlink(str(database_tmp))