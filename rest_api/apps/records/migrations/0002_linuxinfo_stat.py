# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-03-01 12:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linuxinfo',
            name='stat',
            field=models.TextField(default='null', help_text='stat', verbose_name='stat'),
        ),
    ]
