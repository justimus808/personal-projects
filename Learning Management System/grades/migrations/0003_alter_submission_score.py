# Generated by Django 4.2.4 on 2023-10-28 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0002_alter_submission_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]