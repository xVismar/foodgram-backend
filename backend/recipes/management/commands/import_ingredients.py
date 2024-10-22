from recipes.management.commands.import_json import BaseImportCommand
from recipes.models import Ingredient


class Command(BaseImportCommand):
    help = 'Импортирует ингредиенты из файла ingredients.json'

    def handle(self, *args, **kwargs):
        return self.import_from_json(Ingredient, 'ingredients.json')
