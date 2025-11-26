from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0004_alter_apk_capacity_to_char'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apk',
            name='avg_traffic',
        ),
        migrations.RemoveField(
            model_name='apk',
            name='retention_period',
        ),
    ]

