from django.db import migrations, models
import django.db.models.deletion
import utilities.json  # для CustomFieldJSONEncoder


class Migration(migrations.Migration):

    # Если это первая миграция приложения apk:
    initial = True

    dependencies = [
        # Укажи актуальную начальную миграцию tenancy (пример ниже может отличаться от твоей версии)
        ('tenancy', '0001_initial'),
        # Если у тебя уже есть миграция apk с APKService (и т.п.), замени на ('apk', 'XXXX_previous')
        # Если extras требуется раньше — добавь сюда зависимости на extras
        # ('extras', '0001_initial'),
    ]

    operations = [
        # APKName
        migrations.CreateModel(
            name='APKName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField('Название АПК', max_length=100, unique=True)),
                ('description', models.TextField('Описание', blank=True)),
            ],
            options={
                'verbose_name': 'APK Name',
                'verbose_name_plural': 'APK Names',
                'ordering': ['name'],
            },
        ),

        # APKEntry
        migrations.CreateModel(
            name='APKEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),

                ('apk_type', models.CharField('Тип АПК', max_length=100)),
                ('contract', models.CharField('Договор', max_length=200, blank=True)),
                ('ports_count', models.IntegerField('Кол-во портов', default=0)),
                ('capacity_mbps', models.IntegerField('Ёмкость (Мбит/с)', default=0)),
                ('ports_type', models.CharField(
                    'Тип портов',
                    max_length=20,
                    choices=[('10g-lr', '10G-LR'), ('100g-lr4', '100G-LR4')],
                    default='10g-lr',
                )),
                ('specs', models.TextField('ТТХ', blank=True)),

                ('apk_name', models.ForeignKey(
                    to='apk.apkname',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='entries',
                    verbose_name='APK Name',
                )),
                ('operator', models.ForeignKey(
                    to='tenancy.tenant',
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='apk_entries',
                    verbose_name='Оператор',
                )),
            ],
            options={
                'verbose_name': 'APK Entry',
                'verbose_name_plural': 'APK Entries',
                # В коде модели сейчас стоит ordering по полям 'apk' и 'operator';
                # корректный ordering с учётом твоих полей — по 'apk_type', 'apk_name', 'operator'
                'ordering': ['apk_type', 'apk_name', 'operator'],
            },
        ),
    ]