import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0005_remove_apk_avg_traffic_retention_period'),
        ('extras', '0133_make_cf_minmax_decimal'),
    ]

    operations = [
        migrations.CreateModel(
            name='APKDRS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(blank=True, max_length=255)),
                ('operator', models.CharField(blank=True, max_length=255)),
                ('region', models.CharField(blank=True, max_length=255)),
                ('contract', models.CharField(blank=True, max_length=255)),
                ('avg_traffic', models.CharField(blank=True, max_length=255, null=True)),
                ('retention_period', models.CharField(blank=True, max_length=255, null=True)),
                ('tags', taggit.managers.TaggableManager(blank=True, ordering=('weight', 'name'), through='extras.TaggedItem', to='extras.tag')),
            ],
            options={
                'ordering': ('name', 'pk'),
            },
        ),
    ]

