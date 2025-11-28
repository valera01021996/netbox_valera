from dcim.models import InventoryItem, Manufacturer
from django.utils.text import slugify
from pprint import pprint
from django.db import transaction

def get_or_create_manufacturer(name):
    if not name or name in ("N/A", "None", ""):
        return None
    name = str(name).strip()
    slug = slugify(name)[:50]
    manufacturer = Manufacturer.objects.filter(name__iexact=name).first()

    if manufacturer:
        return manufacturer

    manufacturer = Manufacturer.objects.create(name=name, slug=slug)
    return manufacturer



def upsert_item(device, name, description="", manufacturer=None, serial=""):
    try:
        with transaction.atomic():
            item, _ = InventoryItem.objects.update_or_create(device=device, name=name)
            item.description = description
            if manufacturer:
                item.manufacturer = manufacturer
            if serial:
                item.serial = serial
            item.save()
    except Exception as e:
        print(f"❌ Ошибка в upsert_item: {e}")

def map_data_to_inventory(device, data):
    try:
        # print("-> FANS")
        for fan in data.get("FANS", []):
            if not isinstance(fan, dict):
                continue
            name = fan.get("Name", "Fan")
            upsert_item(device, name)
    except Exception as e:
        print(f"❌ Ошибка в FANS: {e}")
    


    try:
        # print("-> MEMORY")
        memory = data.get("Memory", {})
        for mod in memory.get("Modules", []):
            if not isinstance(mod, dict):
                continue
            name = f"RAM {mod.get('DeviceLocator', 'Unknown')}"
            desc = f"{mod.get('Capacity (GB)')} GB \n {mod.get('MemoryDeviceType')} \n {mod.get('OperatingSpeedMhz')} MHz"
            manufacturer = get_or_create_manufacturer(mod.get('Manufacturer'))
            upsert_item(device, name, description=desc, manufacturer=manufacturer)
    except Exception as e:
        print(f"❌ Ошибка в MEMORY: {e}")


    try:
        # print("-> PSUs")
        i = 1
        for psu in data.get('PSUs', []):
            if not isinstance(psu, dict):
                continue
            name = f"{i}.PSU {psu.get('Name')}"
            desc = f"FirmwareVersion: {psu.get('FirmwareVersion')} \n Model: {psu.get('Model')} \n Capacity: {psu.get('Capacity')} Watts"
            serial_number = psu.get('SerialNumber')
            manufacturer = get_or_create_manufacturer(psu.get('Manufacturer'))
            upsert_item(device, name, description=desc, manufacturer=manufacturer, serial=serial_number)
            i += 1
    except Exception as e:
        print(f"❌ Ошибка в PSUs: {e}")

    try:
        # print("-> Processors")
        for cpu in data.get('Processors', []):
            if not isinstance(cpu, dict):
                continue
            name = f"CPU {cpu.get('ID')}"
            desc = f"Model: {cpu.get('Model')} \n Total Cores: {cpu.get('TotalCores')} \n Total Threads: {cpu.get('TotalThreads')} \n MaxSpeed: {cpu.get('MaxSpeed (MHz)')}"
            manufacturer = get_or_create_manufacturer(cpu.get('Manufacturer'))
            upsert_item(device, name, description=desc, manufacturer=manufacturer)
    except Exception as e:
        print(f"❌ Ошибка в Processors: {e}")

    try:
        # print("-> RAID Controllers")
        for controller in data.get('RAID', {}).get('Controllers', []):
            if not isinstance(controller, dict):
                continue
            name = f"RAID Controller {controller.get('Name')}"
            if 'ahci' in name.lower() or 'sata' in name.lower():
                continue
            desc = f"Model: {controller.get('Model')} \n FirmwareVersion: {controller.get('FirmwareVersion', {}).get('VersionString', 'N/A')}"
            upsert_item(device, name, description=desc)
    except Exception as e:
        print(f"❌ Ошибка в RAID Controllers: {e}")

    try:
        # print("-> RAID Volumes")
        for volume in data.get('RAID', {}).get('Volumes', []):
            if not isinstance(volume, dict):
                continue
            name = f"RAID Volume {volume.get('Name')}"
            desc = f"Size: {volume.get('Capacity')} GB \n Type: {volume.get('RAID')} \n Status: {volume.get('Status')}"
            upsert_item(device, name, description=desc)
    except Exception as e:
        print(f"❌ Ошибка в RAID Volumes: {e}")

    try:
        # print("-> Storage")
        for disk in data.get('Storage', []):
            if not isinstance(disk, dict):
                continue
            name = f"{disk.get('MediaType')} {disk.get('ID')}"
            desc = f"Model: {disk.get('Model')} \n Protocol: {disk.get('Protocol')} \n Capacity: {disk.get('Capacity')} GB"
            serial_number = disk.get('SerialNumber')
            upsert_item(device, name, description=desc, serial=serial_number)
    except Exception as e:
        print(f"❌ Ошибка в Storage: {e}")

    try:
        system_info = data.get('System', {})
        serial_number = system_info.get('SerialNumber')
        if serial_number and serial_number not in ("N/A", "", None):
            if device.serial != serial_number:
                device.serial = serial_number
                device.save()
    except Exception as e:
        print(f"❌ Ошибка в System: {e}")


        

