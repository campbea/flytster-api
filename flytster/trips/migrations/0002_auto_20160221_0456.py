# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-21 04:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='meal',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='mileage',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='ontime_percent',
        ),
    ]
