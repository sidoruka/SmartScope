# Generated by Django 4.0.5 on 2022-12-07 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0008_highmagmodel_selected_alter_microscope_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='selector',
            name='value',
            field=models.FloatField(null=True),
        ),
    ]
