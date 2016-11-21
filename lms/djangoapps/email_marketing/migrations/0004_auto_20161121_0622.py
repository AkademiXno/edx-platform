# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_marketing', '0003_auto_20160715_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmarketingconfiguration',
            name='sailthru_new_user_list',
            field=models.CharField(help_text='Sailthru list name to add new users to. ', max_length=512),
        ),
    ]
