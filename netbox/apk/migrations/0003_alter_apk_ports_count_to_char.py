from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0002_alter_apk_name_blank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apk',
            name='ports_count',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]