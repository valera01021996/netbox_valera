from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0007_delete_apkdrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='apk',
            name='avg_traffic',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='apk',
            name='retention_period',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

