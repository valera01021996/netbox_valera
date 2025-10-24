from netbox.plugins import PluginConfig

class NbAutomationConfig(PluginConfig):
    name = 'nb_automation'
    verbose_name = 'Excel Automation'
    description = 'Import devices from Excel'
    version = '1.0.0'
    author = 'Valeriy Kim'
    author_email = 'vkim@tashsoftcom.uz'
    base_url = 'nb-automation'

config = NbAutomationConfig
