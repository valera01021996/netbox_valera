from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0003_alter_apk_ports_count_to_char'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apk',
            name='capacity',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]


