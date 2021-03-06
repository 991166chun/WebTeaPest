# Generated by Django 3.0.3 on 2021-02-16 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TeaData', '0002_auto_20210216_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='County',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='TeaData.County'),
        ),
        migrations.AlterField(
            model_name='person',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='TeaData.City'),
        ),
    ]
