import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0133_make_cf_minmax_decimal'),
    ]

    operations = [
        migrations.CreateModel(
            name='APK',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(blank=True, max_length=255)),
                ('operator', models.CharField(blank=True, max_length=255)),
                ('region', models.CharField(blank=True, max_length=255)),
                ('contract', models.CharField(blank=True, max_length=255)),
                ('ttx', models.CharField(blank=True, max_length=255)),
                ('port_type', models.CharField(blank=True, max_length=255)),
                ('ports_count', models.PositiveIntegerField(blank=True, null=True)),
                ('capacity', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('avg_traffic', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('retention_period', models.CharField(blank=True, max_length=255)),
                ('tags', taggit.managers.TaggableManager(blank=True, ordering=('weight', 'name'), through='extras.TaggedItem', to='extras.tag')),
            ],
        ),
    ]


