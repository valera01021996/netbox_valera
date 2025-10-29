from netbox.plugins import PluginConfig

class ApkConfig(PluginConfig):
    name = 'apk'
    verbose_name = 'APK'
    description = 'APK plugin'
    version = '1.0.0'
    author = 'Valeriy Kim'
    author_email = 'vkim@tashsoftcom.uz'
    base_url = 'apk'

config = ApkConfig
