from netbox.plugins import PluginConfig


class DeviceScanConfig(PluginConfig):
    name = "device_scan"
    verbose_name = "Device Scan"
    description = "Device scan status tracking"
    version = "1.0.0"
    author = "Valeriy Kim"
    author_email = "vkim@tashsoftcom.uz"
    base_url = "device-scan"
    required_settings = []
    default_settings = {}
    caching_config = {}


config = DeviceScanConfig

