# Generated by Django 3.0.3 on 2021-02-16 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TeaData', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='County',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.SET_DEFAULT, to='TeaData.County'),
        ),
        migrations.AlterField(
            model_name='person',
            name='city',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.SET_DEFAULT, to='TeaData.City'),
        ),
    ]