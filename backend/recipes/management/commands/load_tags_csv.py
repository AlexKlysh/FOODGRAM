import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags.csv data into Tag Model'

    def handle(self, *args, **kwargs):
        with open('data/tags.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Tag.objects.get_or_create(
                    name=row['name'],
                    slug=row['slug'],
                    color=row['color']
                )
        print('Tags uploaded')
