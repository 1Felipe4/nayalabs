# Generated by Django 3.2.8 on 2021-11-02 17:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20211101_1814'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='date',
            new_name='print_date',
        ),
        migrations.RenameField(
            model_name='report',
            old_name='type',
            new_name='test_request',
        ),
        migrations.AddField(
            model_name='report',
            name='branch_no',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='collect_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='report',
            name='company',
            field=models.CharField(default='OCCUPATIONAL HEALTH SOLUTIONS', max_length=512),
        ),
        migrations.AddField(
            model_name='report',
            name='department',
            field=models.CharField(default='IMMUNO', max_length=255),
        ),
        migrations.AddField(
            model_name='report',
            name='doc_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='doctor',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='insurance',
            field=models.CharField(default='PARTICULAR', max_length=255),
        ),
        migrations.AddField(
            model_name='report',
            name='order_type',
            field=models.CharField(default='EXTERNAL', max_length=255),
        ),
        migrations.AddField(
            model_name='report',
            name='unit_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
