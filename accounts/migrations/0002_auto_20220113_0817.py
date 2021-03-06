# Generated by Django 4.0 on 2022-01-13 08:17
import csv

from django.db import migrations


def import_from_csv(apps, file_name: str):
    """
    Import regions from csv to database
    :param file_name:
    :return:
    """
    Region = apps.get_model('accounts', 'Region')
    with open(file_name) as file:
        reader = csv.reader(file)
        return Region.objects.bulk_create(
            [Region(region=row[2], country='Россия') for row in reader][1:],
            ignore_conflicts=True
        )


def upload_regions(apps, schema_editor):
    Region = apps.get_model('accounts', 'Region')
    db_alias = schema_editor.connection.alias
    import_from_csv(apps, 'accounts/region.csv')


def delete_regions(apps, schema_editor):
    Region = apps.get_model('accounts', 'Region')
    db_alias = schema_editor.connection.alias
    Region.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(upload_regions, delete_regions),
    ]
