from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apk',
            name='name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]


