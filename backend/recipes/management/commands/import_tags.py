from recipes.management.commands.import_json import BaseImportCommand
from recipes.models import Tag


class Command(BaseImportCommand):
    help = 'Импортирует теги из файла mytags.json'

    def handle(self, *args, **kwargs):
        return self.import_from_json(Tag, 'mytags.json')
