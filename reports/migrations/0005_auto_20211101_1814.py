# Generated by Django 3.2.8 on 2021-11-01 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20211101_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lab',
            name='footer',
            field=models.ImageField(null=True, upload_to='footers', verbose_name='Footer'),
        ),
        migrations.AlterField(
            model_name='lab',
            name='header',
            field=models.ImageField(null=True, upload_to='headers', verbose_name='Header'),
        ),
    ]
