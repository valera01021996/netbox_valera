from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apkentry',
            name='capacity_mbps',
            field=models.IntegerField('Ёмкость лицензии', default=0),
        ),
        migrations.AlterField(
            model_name='apkentry',
            name='specs',
            field=models.CharField('ТТХ', max_length=200),
        ),
        migrations.AlterField(
            model_name='apkentry',
            name='ports_type',
            field=models.CharField('Тип портов', max_length=20),
        ),
    ]