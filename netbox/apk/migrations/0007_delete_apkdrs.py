from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0006_create_apkdrs'),
    ]

    operations = [
        migrations.DeleteModel(
            name='APKDRS',
        ),
    ]

