# Generated by Django 3.2.3 on 2024-01-30 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IngredientRecipe',
            new_name='IngredientInRecipe',
        ),
    ]
