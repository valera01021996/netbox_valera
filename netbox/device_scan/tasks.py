from celery import shared_task
from django.utils import timezone
from dcim.models import Device
from .models import DeviceScan
from .inventory_mapper import map_data_to_inventory
from vendors.dell.vendor import DellProvider
from vendors.hp.vendor import HPProvider
from vendors.huawei.vendor import HuaweiProvider


PROVIDERS = {
    "dell": DellProvider,
    "hp": HPProvider,
    "huawei": HuaweiProvider,
}


VENDOR_CREDENTIALS = {
    "dell": {"username": "root", "password": "UzMaster2021"},
    "hp": {"username": "Administrator", "password": "Uzmaster2021@"},
    "huawei": {"username": "root", "password": "Uzmaster2021@"},
}




@shared_task
def scan_device_task(device_id):
    device = Device.objects.get(pk=device_id)
    scan, _ = DeviceScan.objects.get_or_create(device=device)

    scan.status = "RUNNING"
    scan.last_started = timezone.now()
    scan.attemts += 1
    scan.error = ""
    scan.save()


    try:
        ip = None
        if device.oob_ip:
            ip = str(device.oob_ip.address.ip)
        if not ip:
            raise Exception("OOB IP is not found")

        manufacturer = (device.device_type.manufacturer.name or "").lower()
        provider_class = None

        for key, cls in PROVIDERS.items():
            if key in manufacturer:
                provider_class = cls
                break
        if not provider_class:
            raise Exception(f"Provider for {manufacturer} is not found")

        print(f"Using {manufacturer} provider")

        creds = VENDOR_CREDENTIALS.get(manufacturer, {})
        username = creds.get("username")
        password = creds.get("password")


        provider = provider_class(ip, username, password)
        # provider = DellProvider(ip, "root", "UzMaster2021")
        data = provider.get_all_inventory()
        map_data_to_inventory(device, data)
        scan.status = "OK"

    except Exception as e:
        scan.status = "ERROR"
        scan.error = str(e)

    finally:
        scan.last_finished = timezone.now()
        scan.save()


@shared_task
def scan_all_devices_task():
    devices = Device.objects.all()
    total = 0
    launched = 0

    for dev in devices:
        total += 1

        ip = None
        if dev.oob_ip:
            ip = str(dev.oob_ip.address.ip)
        if not ip:
            continue

        DeviceScan.objects.update_or_create(
            device=dev,
            defaults = {"status": "PENDING", "error": ""}
        )

        scan_device_task.delay(dev.id)
        launched += 1

    return {
        "total": total,
        "launched": launched,
    }

