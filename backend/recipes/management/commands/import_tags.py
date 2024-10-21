from django.core.management.base import BaseCommand

from recipes.management.commands.import_json import import_from_json
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирует теги из файла mytags.json'

    def handle(self, *args, **kwargs):
        success, message = import_from_json(Tag, 'mytags.json')
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))
