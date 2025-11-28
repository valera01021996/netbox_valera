import time
import logging
import urllib3
from vendors.base.vendor import BaseProvider

# Отключаем предупреждения о небезопасном SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class DellProvider(BaseProvider):
    """
    Класс для работы с Dell сервером через Redfish API
    Поддерживает iDRAC 7, 8, 9 и новее
    """
    
    def _get_first_href(self, value):
        """
        Извлекает ссылку из разных форматов
        Может быть строка, dict с @odata.id, или список
        """
        if not value:
            return None
        if isinstance(value, str):
            return value.strip() or None
        if isinstance(value, dict):
            return value.get("@odata.id")
        if isinstance(value, list) and value:
            for item in value:
                if isinstance(item, dict):
                    href = item.get("@odata.id")
                    if href:
                        return href
        return None
    
    def _extract_path(self, url_or_path):
        """Извлекает путь из полного URL"""
        if not url_or_path:
            return None
        if isinstance(url_or_path, str):
            if url_or_path.startswith(self.base_url):
                return url_or_path[len(self.base_url):]
            if url_or_path.startswith("http"):
                # Полный URL от другого хоста - берем только путь
                return "/" + "/".join(url_or_path.split("/")[3:])
            return url_or_path
        return None
    
    def _find_system_id(self):
        """
        Находит ID системы (обычно System.Embedded.1)
        """
        systems_data = self._get("/redfish/v1/Systems")
        if not systems_data:
            return "System.Embedded.1"  # Значение по умолчанию для Dell
        
        members = systems_data.get("Members", [])
        if members:
            href = self._get_first_href(members[0])
            if href:
                # Извлекаем ID из пути типа /redfish/v1/Systems/System.Embedded.1
                return href.split("/")[-1]
        
        return "System.Embedded.1"
    
    def get_system_info(self):
        """
        Получение основной информации о системе
        
        Returns:
            dict: словарь с информацией о системе
        """
        logger.info(f"📊 Получение информации о системе host {self.ip_address}")
        
        system_id = self._find_system_id()
        data = self._get(f"/redfish/v1/Systems/{system_id}")
        if not data:
            return {}
        
        system_info = {
            "Manufacturer": data.get("Manufacturer", "N/A"),
            "Model": data.get("Model", "N/A"),
            "SerialNumber": data.get("SerialNumber", "N/A"),
            "SKU": data.get("SKU", "N/A"),
            "BiosVersion": data.get("BiosVersion", "N/A"),
            "PowerState": data.get("PowerState", "N/A"),
            "Status": data.get("Status", {}).get("Health", "N/A"),
        }
        
        return system_info
    
    def get_processor_info(self):
        """
        Получение информации о процессорах
        
        Returns:
            list: список процессоров
        """
        logger.info(f"🖥️  Получение информации о процессорах... host {self.ip_address}")
        
        processors = []
        system_id = self._find_system_id()
        
        data = self._get(f"/redfish/v1/Systems/{system_id}/Processors")
        
        if not data:
            logger.warning(f"⚠️  Не удалось получить информацию о процессорах host {self.ip_address}")
            return processors
        
        # Получаем список процессоров
        members = data.get("Members", [])
        
        for member in members:
            # Получаем ссылку на процессор
            href = self._get_first_href(member)
            if not href:
                continue
            
            # Извлекаем путь
            path = self._extract_path(href)
            if not path:
                continue
            
            # Получаем данные процессора
            proc_data = self._get(path)
            if not proc_data:
                continue
            
            # Проверяем что процессор установлен
            state = proc_data.get("Status", {}).get("State", "")
            if state and state not in ["Enabled", "Present", "OK"]:
                continue
            
            processor = {
                "ID": proc_data.get("Id", "N/A"),
                "Model": proc_data.get("Model", "N/A"),
                "Manufacturer": proc_data.get("Manufacturer", "N/A"),
                "TotalCores": proc_data.get("TotalCores", "N/A"),
                "TotalThreads": proc_data.get("TotalThreads", "N/A"),
                "MaxSpeed (MHz)": proc_data.get("MaxSpeedMHz", "N/A"),
                "Status": proc_data.get("Status", {}).get("Health", "N/A"),
            }
            processors.append(processor)
        
        print(f"   ✅ Найдено процессоров: {len(processors)} host {self.ip_address}")
        return processors
    
    def get_memory_info(self):
        """
        Получение информации о памяти
        
        Returns:
            dict: информация о памяти
        """
        print(f"\n💾 Получение информации о памяти host {self.ip_address}")
        
        memory_modules = []
        total_memory_gb = 0
        system_id = self._find_system_id()
        
        data = self._get(f"/redfish/v1/Systems/{system_id}/Memory")
        
        if not data:
            print(f"   ⚠️  Не удалось получить информацию о памяти host {self.ip_address}")
            return {"Всего памяти (GB)": 0, "Модули": []}
        
        members = data.get("Members", [])
        
        for member in members:
            href = self._get_first_href(member)
            if not href:
                continue
            
            path = self._extract_path(href)
            if not path:
                continue
            
            mem_data = self._get(path)
            if not mem_data:
                continue
            
            # Проверяем что модуль установлен
            state = mem_data.get("Status", {}).get("State", "")
            if state and state not in ["Enabled", "Present", "OK"]:
                continue
            
            # Размер может быть в разных полях
            capacity_mib = mem_data.get("CapacityMiB")
            if not capacity_mib:
                # Если нет размера, значит слот пустой
                continue
            
            capacity_gb = capacity_mib / 1024
            total_memory_gb += capacity_gb
            
            module = {
                "DeviceLocator": mem_data.get("DeviceLocator") or mem_data.get("SocketLocator") or mem_data.get("Id", "N/A"),
                "Capacity (GB)": round(capacity_gb, 2),
                "MemoryDeviceType": mem_data.get("MemoryDeviceType", "N/A"),
                "OperatingSpeedMhz": mem_data.get("OperatingSpeedMhz", "N/A"),
                "Manufacturer": mem_data.get("Manufacturer", "N/A"),
                "Status": mem_data.get("Status", {}).get("Health", "N/A"),
            }
            memory_modules.append(module)
        
        print(f"   ✅ Найдено модулей памяти: {len(memory_modules)}, всего: {round(total_memory_gb, 2)} GB host {self.ip_address}")
        
        return {
            "Total_memory (GB)": round(total_memory_gb, 2),
            "Modules": memory_modules
        }
    
    def get_storage_info(self):
        """
        Получение информации о дисках
        
        Returns:
            list: список дисков
        """
        print(f"\n💿 Получение информации о хранилище host {self.ip_address}")
        
        drives = []
        system_id = self._find_system_id()
        
        # Получаем Storage контроллеры
        data = self._get(f"/redfish/v1/Systems/{system_id}/Storage")
        
        if not data or not data.get("Members"):
            print(f"   ⚠️  Не удалось получить информацию о хранилище host {self.ip_address}")
            return drives
        
        for storage_member in data.get("Members", []):
            storage_href = self._get_first_href(storage_member)
            if not storage_href:
                continue
            
            storage_path = self._extract_path(storage_href)
            storage = self._get(storage_path)
            if not storage:
                continue
            
            controller_name = storage.get("Id", "Unknown Controller")
            
            # Получаем диски
            drives_list = storage.get("Drives", [])
            total_drives = len(drives_list)
            if total_drives > 0:
                print(f"   📀 Контроллер: {controller_name}, дисков: {total_drives} host {self.ip_address}")
            
            for idx, drive_ref in enumerate(drives_list, 1):
                drive_href = self._get_first_href(drive_ref)
                if not drive_href:
                    continue
                
                drive_path = self._extract_path(drive_href)
                drive_data = self._get(drive_path)
                
                if drive_data:
                    drive = self._normalize_drive(drive_data, controller_name)
                    if drive:
                        drives.append(drive)
        
        print(f"   ✅ Найдено дисков: {len(drives)} host {self.ip_address}")
        return drives
    
    def _normalize_drive(self, drive_data, controller_name):
        """Нормализация данных диска из Redfish API"""
        capacity_bytes = drive_data.get("CapacityBytes")
        if not capacity_bytes:
            return None
        
        capacity_gb = capacity_bytes / (1024**3)
        
        # Получаем Dell-специфичные поля из Oem для расположения
        dell_oem = drive_data.get("Oem", {}).get("Dell", {}).get("DellPhysicalDisk", {})
        
        # Формируем расположение из Slot
        slot = dell_oem.get("Slot", "N/A")
        location = f"Slot:{slot}" if slot != "N/A" else drive_data.get("Id", "N/A")
        
        return {
            "ID": drive_data.get("Id", "N/A"),
            "Model": drive_data.get("Model", "N/A"),
            "Capacity": round(capacity_gb, 2),
            "MediaType": drive_data.get("MediaType", "N/A"),
            "Protocol": drive_data.get("Protocol", "N/A"),
            "SerialNumber": drive_data.get("SerialNumber", "N/A"),
            "Location": location,
            "Controller": controller_name,
            "Status": drive_data.get("Status", {}).get("Health", "N/A"),
        }
    
    def get_raid_info(self):
        """
        Получение информации о RAID контроллерах и массивах
        
        Returns:
            dict: информация о контроллерах и томах
        """
        print(f"\n🔧 Получение информации о RAID... host {self.ip_address}")
        
        controllers = []
        volumes = []
        system_id = self._find_system_id()
        
        # Получаем Storage контроллеры
        storage_data = self._get(f"/redfish/v1/Systems/{system_id}/Storage")
        
        if not storage_data:
            print("   ⚠️  RAID информация недоступна")
            return {"Контроллеры": controllers, "Тома": volumes}
        
        for storage_member in storage_data.get("Members", []):
            storage_href = self._get_first_href(storage_member)
            if not storage_href:
                continue
            
            storage_path = self._extract_path(storage_href)
            storage = self._get(storage_path)
            
            if not storage:
                continue
            
            # Информация о контроллере
            storage_controllers = storage.get("StorageControllers", [])
            if storage_controllers:
                ctrl_data = storage_controllers[0]  # Берем первый контроллер
                
                ctrl_info = {
                    "ID": storage.get("Id", "N/A"),
                    "Name": storage.get("Name", "N/A"),
                    "Model": ctrl_data.get("Model", "N/A"),
                    "SerialNumber": ctrl_data.get("SerialNumber", "N/A"),
                    "FirmwareVersion": {"VersionString": ctrl_data.get("FirmwareVersion", "N/A")},
                    "Status": ctrl_data.get("Status", {}).get("Health", "N/A"),
                }
                controllers.append(ctrl_info)
            
            # Получаем тома (RAID массивы)
            volumes_ref = storage.get("Volumes")
            if not volumes_ref:
                continue
            
            volumes_href = self._get_first_href(volumes_ref)
            if not volumes_href:
                continue
            
            volumes_path = self._extract_path(volumes_href)
            volumes_data = self._get(volumes_path)
            
            if not volumes_data:
                continue
            
            # Для каждого тома
            for vol_member in volumes_data.get("Members", []):
                vol_href = self._get_first_href(vol_member)
                if not vol_href:
                    continue
                
                vol_path = self._extract_path(vol_href)
                vol_data = self._get(vol_path)
                
                if vol_data:
                    # Размер
                    capacity_bytes = vol_data.get("CapacityBytes")
                    capacity_gb = capacity_bytes / (1024**3) if capacity_bytes else 0
                    
                    # RAID уровень - убираем "RAID" префикс если есть
                    raid_type = vol_data.get("RAIDType") or vol_data.get("VolumeType", "N/A")
                    if raid_type.startswith("RAID"):
                        raid_type = raid_type.replace("RAID", "").strip()
                    
                    volume = {
                        "ID": vol_data.get("Id", "N/A"),
                        "Name": vol_data.get("Name", "N/A"),
                        "RAID": raid_type,
                        "Capacity": round(capacity_gb, 2),
                        "Controller": storage.get("Id", "N/A"),
                        "Status": vol_data.get("Status", {}).get("Health", "N/A"),
                    }
                    volumes.append(volume)
        
        print(f"   ✅ Контроллеров: {len(controllers)}, RAID массивов: {len(volumes)} host {self.ip_address}")
        
        return {"Controllers": controllers, "Volumes": volumes}
    
    def get_power_supplies(self):
        """
        Получение информации о блоках питания
        
        Returns:
            list: список блоков питания
        """
        print(f"\n🔌 Получение информации о блоках питания host {self.ip_address}")
        
        power_supplies = []
        
        # Получаем данные о питании из Chassis
        power_data = self._get("/redfish/v1/Chassis/System.Embedded.1/Power")
        
        if not power_data:
            print(f"   ⚠️  Информация о блоках питания недоступна {self.ip_address}")
            return power_supplies
        
        # Извлекаем блоки питания
        for psu in power_data.get("PowerSupplies", []):
            if not isinstance(psu, dict):
                continue
            
            # Мощность
            capacity_watts = psu.get("PowerCapacityWatts")
            output_watts = psu.get("LastPowerOutputWatts") or psu.get("PowerOutputWatts")
            
            supply = {
                "Name": psu.get("Name") or psu.get("MemberId") or psu.get("Id", "N/A"),
                "Model": psu.get("Model", "N/A"),
                "SerialNumber": psu.get("SerialNumber", "N/A"),
                "Manufacturer": psu.get("Manufacturer", "N/A"),
                "Capacity": capacity_watts or "N/A",
                "Output": output_watts or "N/A",
                "FirmwareVersion": psu.get("FirmwareVersion", "N/A"),
                "Status": psu.get("Status", {}).get("Health", "N/A"),
                "State": psu.get("Status", {}).get("State", "N/A"),
            }
            power_supplies.append(supply)
        
        print(f"   ✅ Найдено блоков питания: {len(power_supplies)} host {self.ip_address}")
        
        return power_supplies
    
    def get_fans(self):
        """
        Получение информации о вентиляторах
        
        Returns:
            list: список вентиляторов
        """
        print(f"\n🌀 Получение информации о вентиляторах host {self.ip_address}")
        
        fans = []
        
        # Получаем термальные данные из Chassis
        thermal_data = self._get("/redfish/v1/Chassis/System.Embedded.1/Thermal")
        
        if not thermal_data:
            print(f"   ⚠️  Информация о вентиляторах недоступна host {self.ip_address}")
            return fans
        
        # Извлекаем вентиляторы
        for fan in thermal_data.get("Fans", []):
            if not isinstance(fan, dict):
                continue
            
            # Скорость
            rpm = fan.get("Reading")
            
            fan_info = {
                "Name": fan.get("Name") or fan.get("FanName") or fan.get("MemberId") or fan.get("Id", "N/A"),
                "Speed": rpm if rpm else "N/A",
                "Percent": "N/A",  # Dell обычно не предоставляет процент
                "Location": fan.get("PhysicalContext", "N/A"),
                "Status": fan.get("Status", {}).get("Health", "N/A"),
                "State": fan.get("Status", {}).get("State", "N/A"),
            }
            fans.append(fan_info)
        
        print(f"   ✅ Найдено вентиляторов: {len(fans)} host {self.ip_address}")
        
        return fans
    
    def get_all_inventory(self):
        """
        Собирает всю информацию о сервере
        
        Returns:
            dict: полный инвентарь сервера
        """
        print(f"\n🔍 Сбор информации о сервере Dell host {self.ip_address}...")
        
        inventory = {
            "ip_address": self.ip_address,
            "System": self.get_system_info(),
            "Processors": self.get_processor_info(),
            "Memory": self.get_memory_info(),
            "RAID": self.get_raid_info(),
            "Storage": self.get_storage_info(),
            "PSUs": self.get_power_supplies(),
            "FANS": self.get_fans(),
        }
        
        return inventory
