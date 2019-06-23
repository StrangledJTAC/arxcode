# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-15 20:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    def purge_the_things(apps, schema_editor):
        Domain = apps.get_model('dominion', 'Domain')
        Domain.objects.update(unassigned_serfs=0, lawlessness=0)

    dependencies = [
        ('dominion', '0044_auto_20190225_2014'),
    ]

    operations = [
        migrations.RunPython(purge_the_things)
    ]