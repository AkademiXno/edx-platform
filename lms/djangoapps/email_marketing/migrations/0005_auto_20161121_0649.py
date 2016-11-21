# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.db import migrations, models
from django.contrib.sites.models import Site
from email_marketing.models import EmailMarketingConfiguration


def add_sailthru_user_list(apps, schema_editor):
    email_config = EmailMarketingConfiguration.current()
    if email_config.enabled:
        sailthru_user_lists = get_user_list_json()
        config = EmailMarketingConfiguration(
            enabled=email_config.enabled,
            sailthru_key=email_config.sailthru_key,
            sailthru_secret=email_config.sailthru_secret,
            sailthru_new_user_list=sailthru_user_lists,
            sailthru_retry_interval=email_config.sailthru_retry_interval,
            sailthru_max_retries=email_config.sailthru_max_retries,
            sailthru_activation_template=email_config.sailthru_activation_template,
            sailthru_abandoned_cart_template=email_config.sailthru_abandoned_cart_template,
            sailthru_abandoned_cart_delay=email_config.sailthru_abandoned_cart_delay,
            sailthru_enroll_template=email_config.sailthru_enroll_template,
            sailthru_upgrade_template=email_config.sailthru_upgrade_template,
            sailthru_purchase_template=email_config.sailthru_purchase_template,
            sailthru_get_tags_from_sailthru=email_config.sailthru_get_tags_from_sailthru,
            sailthru_content_cache_age=email_config.sailthru_content_cache_age,
            sailthru_enroll_cost=email_config.sailthru_enroll_cost,
            sailthru_lms_url_override=email_config.sailthru_lms_url_override
            )
        config.save()


def remove_sailthru_user_list(apps, schema_editor):
    sailthru_user_lists = get_user_list_json()
    EmailMarketingConfiguration.objects.filter(sailthru_new_user_list=sailthru_user_lists, enabled=True).delete()


def get_user_list_json():
    sites = Site.objects.all()
    sailthru_user_lists = {sites[0].domain: 'All edX Users'}
    for site in sites[1:]:
        sailthru_user_lists[site.domain] = 'White Label Users'

    return json.dumps(sailthru_user_lists)


class Migration(migrations.Migration):

    dependencies = [
        ('email_marketing', '0004_auto_20161121_0622'),
    ]

    operations = [
        migrations.RunPython(add_sailthru_user_list, reverse_code=remove_sailthru_user_list),
    ]
