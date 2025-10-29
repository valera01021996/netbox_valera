from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apk', '0001_initial'),  # замените на имя предыдущей миграции, если отличается
    ]

    operations = [
        migrations.CreateModel(
            name='APKType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='types', to='apk.apkservice')),
            ],
            options={
                'verbose_name': 'APK Type',
                'verbose_name_plural': 'APK Types',
                'ordering': ['service', 'name'],
                'unique_together': {('service', 'name')},
            },
        ),
    ]
