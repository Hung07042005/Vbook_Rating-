# Generated by Django 5.2.4 on 2025-07-11 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0017_author_tieu_su_alter_author_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='birth_year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Năm sinh'),
        ),
        migrations.AddField(
            model_name='author',
            name='home_town',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Quê quán'),
        ),
    ]
