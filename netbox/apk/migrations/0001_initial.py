# Generated manually for APK plugin
from django.db import migrations, models
import netbox.models.features


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),  # базовая зависимость NetBox
    ]

    operations = [
        migrations.CreateModel(
            name='APKService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'APK Service',
                'verbose_name_plural': 'APK Services',
            },
            bases=(netbox.models.features.ChangeLoggingMixin, netbox.models.features.CustomFieldsMixin, models.Model),
        ),
    ]
