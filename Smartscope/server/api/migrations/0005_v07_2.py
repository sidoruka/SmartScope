# Generated by Django 4.0.5 on 2022-07-12 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0004_v07'),
    ]

    operations = [
        migrations.AddField(
            model_name='highmagmodel',
            name='shape_x',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='highmagmodel',
            name='shape_y',
            field=models.IntegerField(null=True),
        ),
    ]
