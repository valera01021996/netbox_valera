import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0215_rackreservation_status'),
        ('extras', '0133_make_cf_minmax_decimal'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceScan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('last_started', models.DateTimeField(blank=True, null=True)),
                ('last_finished', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('RUNNING', 'RUNNING'), ('OK', 'OK'), ('ERROR', 'ERROR')], default='PENDING', max_length=10)),
                ('attemts', models.IntegerField(default=0)),
                ('error', models.TextField(blank=True, null=True)),
                ('device', models.OneToOneField(on_delete=models.CASCADE, related_name='scan_status', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(blank=True, ordering=('weight', 'name'), through='extras.TaggedItem', to='extras.tag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]


