import time
import logging
import urllib3
from vendors.base.vendor import BaseProvider

# Отключаем предупреждения о небезопасном SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class HuaweiProvider(BaseProvider):
    """
    Класс для работы с Huawei сервером через Redfish API
    Поддерживает FusionServer серии
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
        Находит ID системы для Huawei серверов
        """
        systems_data = self._get("/redfish/v1/Systems")
        if not systems_data:
            return "1"  # Значение по умолчанию для Huawei
        
        members = systems_data.get("Members", [])
        if members:
            href = self._get_first_href(members[0])
            if href:
                # Извлекаем ID из пути типа /redfish/v1/Systems/1
                return href.split("/")[-1]
        
        return "1"
    
    def get_system_info(self):
        """
        Получение основной информации о системе
        
        Returns:
            dict: словарь с информацией о системе
        """
        logger.info("📊 Получение информации о системе...")
        
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
        logger.info("🖥️  Получение информации о процессорах...")
        
        processors = []
        system_id = self._find_system_id()
        
        data = self._get(f"/redfish/v1/Systems/{system_id}/Processors")
        
        if not data:
            logger.warning("⚠️  Не удалось получить информацию о процессорах")
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
        
        print(f"   ✅ Найдено процессоров: {len(processors)}")
        return processors
    
    def get_memory_info(self):
        """
        Получение информации о памяти
        
        Returns:
            dict: информация о памяти
        """
        print("\n💾 Получение информации о памяти...")
        
        memory_modules = []
        total_memory_gb = 0
        system_id = self._find_system_id()
        
        data = self._get(f"/redfish/v1/Systems/{system_id}/Memory")
        
        if not data:
            print("   ⚠️  Не удалось получить информацию о памяти")
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
        
        print(f"   ✅ Найдено модулей памяти: {len(memory_modules)}, всего: {round(total_memory_gb, 2)} GB")
        
        return {
            "Total_memory (GB)": round(total_memory_gb, 2),
            "Modules": memory_modules
        }
    
    def get_storage_info(self):
        """
        Получение информации о дисках
        Huawei использует путь /redfish/v1/Systems/{id}/Storages (с "s")
        
        Returns:
            list: список дисков
        """
        print("\n💿 Получение информации о хранилище...")
        
        drives = []
        system_id = self._find_system_id()
        
        # Метод 1: Huawei использует Storages (с "s") как ссылку из Systems
        system_data = self._get(f"/redfish/v1/Systems/{system_id}")
        if system_data and "Storage" in system_data:
            storage_ref = system_data["Storage"]
            if isinstance(storage_ref, dict) and "@odata.id" in storage_ref:
                storages_path = self._extract_path(storage_ref["@odata.id"])
                storages_data = self._get(storages_path)
                
                if storages_data and storages_data.get("Members"):
                    print("   ℹ️  Используем путь через Systems/Storages")
                    drives = self._get_drives_from_huawei_storages(storages_data)
        
        # Метод 2: Прямой путь к дискам через Chassis
        if not drives:
            chassis_data = self._get("/redfish/v1/Chassis")
            if chassis_data and chassis_data.get("Members"):
                chassis_href = self._get_first_href(chassis_data.get("Members", [])[0])
                chassis_id = chassis_href.split("/")[-1] if chassis_href else "1"
                
                drives_collection = self._get(f"/redfish/v1/Chassis/{chassis_id}/Drives")
                if drives_collection and drives_collection.get("Members"):
                    print("   ℹ️  Используем путь Chassis/Drives")
                    drives = self._get_drives_from_collection(drives_collection)
        
        if not drives:
            print("   ⚠️  Не удалось получить информацию о хранилище")
        else:
            print(f"   ✅ Найдено дисков: {len(drives)}")
        
        return drives
    
    def _get_drives_from_huawei_storages(self, storages_data):
        """Получение дисков из Huawei Storages коллекции"""
        drives = []
        
        for storage_member in storages_data.get("Members", []):
            storage_href = self._get_first_href(storage_member)
            if not storage_href:
                continue
            
            storage_path = self._extract_path(storage_href)
            storage = self._get(storage_path)
            if not storage:
                continue
            
            controller_name = storage.get("Id", "Unknown Controller")
            
            # В Huawei диски находятся в массиве Drives
            drives_list = storage.get("Drives", [])
            total_drives = len(drives_list)
            if total_drives > 0:
                print(f"   📀 Контроллер: {controller_name}, дисков: {total_drives}")
            
            for drive_ref in drives_list:
                drive_href = self._get_first_href(drive_ref)
                if not drive_href:
                    continue
                
                drive_path = self._extract_path(drive_href)
                drive_data = self._get(drive_path)
                
                if drive_data:
                    drive = self._normalize_drive(drive_data, controller_name)
                    if drive:
                        drives.append(drive)
        
        return drives
    
    
    def _get_drives_from_collection(self, drives_collection):
        """Получение дисков из прямой коллекции Drives"""
        drives = []
        
        for drive_member in drives_collection.get("Members", []):
            drive_href = self._get_first_href(drive_member)
            if not drive_href:
                continue
            
            drive_path = self._extract_path(drive_href)
            drive_data = self._get(drive_path)
            
            if drive_data:
                drive = self._normalize_drive(drive_data, "Unknown Controller")
                if drive:
                    drives.append(drive)
        
        return drives
    
    def _get_drives_from_huawei_oem(self, oem_data):
        """Получение дисков из Huawei OEM данных"""
        drives = []
        print(f"   🔍 Huawei OEM структура: {list(oem_data.keys())}")
        
        # Пробуем найти ссылки на диски в OEM данных
        if isinstance(oem_data, dict):
            # Ищем любые ссылки на диски
            for key, value in oem_data.items():
                if isinstance(value, dict):
                    # Рекурсивно ищем диски
                    if "Drives" in value or "PhysicalDrives" in value or "Disks" in value:
                        drives_list = value.get("Drives") or value.get("PhysicalDrives") or value.get("Disks", [])
                        if isinstance(drives_list, list):
                            for drive_ref in drives_list:
                                drive_href = self._get_first_href(drive_ref)
                                if drive_href:
                                    drive_path = self._extract_path(drive_href)
                                    drive_data = self._get(drive_path)
                                    if drive_data:
                                        drive = self._normalize_drive(drive_data, "Unknown Controller")
                                        if drive:
                                            drives.append(drive)
        
        return drives
    
    def _normalize_drive(self, drive_data, controller_name):
        """Нормализация данных диска из Redfish API"""
        # Пробуем разные варианты получения размера
        capacity_bytes = drive_data.get("CapacityBytes")
        capacity_mib = drive_data.get("CapacityMiB")
        
        if capacity_bytes:
            capacity_gb = capacity_bytes / (1024**3)
        elif capacity_mib:
            capacity_gb = capacity_mib / 1024
        else:
            # Если нет размера, все равно пытаемся вернуть диск
            capacity_gb = 0
        
        # Получаем Huawei-специфичные поля из Oem для расположения
        huawei_oem = drive_data.get("Oem", {}).get("Huawei", {})
        
        # Формируем расположение - пробуем разные варианты
        location_str = "N/A"
        
        # Вариант 1: Location как массив объектов (Huawei формат)
        location = drive_data.get("Location", [])
        if isinstance(location, list) and location:
            # Huawei использует массив объектов с полем Info
            location_parts = []
            for loc_item in location:
                if isinstance(loc_item, dict):
                    info = loc_item.get("Info", "")
                    if info:
                        location_parts.append(str(info))
                    else:
                        location_parts.append(str(loc_item))
                else:
                    location_parts.append(str(loc_item))
            if location_parts:
                location_str = ", ".join(location_parts)
        elif isinstance(location, dict):
            location_str = location.get("PartLocation", {}).get("ServiceLabel", "N/A")
        
        # Вариант 2: Из Huawei OEM
        if location_str == "N/A" and huawei_oem:
            location_str = huawei_oem.get("Position") or huawei_oem.get("Location", "N/A")
        
        # Вариант 3: Из стандартных полей
        if location_str == "N/A":
            location_str = (drive_data.get("DeviceLocator") or 
                           drive_data.get("Slot") or 
                           drive_data.get("Name") or
                           drive_data.get("Id", "N/A"))
        
        return {
            "ID": drive_data.get("Id", "N/A"),
            "Model": drive_data.get("Model", "N/A"),
            "Capacity": round(capacity_gb, 2) if capacity_gb > 0 else "N/A",
            "MediaType": drive_data.get("MediaType", "N/A"),
            "Protocol": drive_data.get("Protocol", "N/A"),
            "SerialNumber": drive_data.get("SerialNumber", "N/A"),
            "Location": location_str,
            "Controller": controller_name,
            "Status": drive_data.get("Status", {}).get("Health", "N/A"),
        }
    
    def get_raid_info(self):
        """
        Получение информации о RAID контроллерах и массивах
        Huawei использует путь /redfish/v1/Systems/{id}/Storages (с "s")
        
        Returns:
            dict: информация о контроллерах и томах
        """
        print("\n🔧 Получение информации о RAID...")
        
        controllers = []
        volumes = []
        system_id = self._find_system_id()
        
        # Получаем Storages через ссылку из Systems
        system_data = self._get(f"/redfish/v1/Systems/{system_id}")
        if system_data and "Storage" in system_data:
            storage_ref = system_data["Storage"]
            if isinstance(storage_ref, dict) and "@odata.id" in storage_ref:
                storages_path = self._extract_path(storage_ref["@odata.id"])
                storages_data = self._get(storages_path)
                
                if storages_data and storages_data.get("Members"):
                    print("   ℹ️  Используем путь через Systems/Storages для RAID")
                    result = self._get_raid_from_huawei_storages(storages_data)
                    controllers.extend(result["controllers"])
                    volumes.extend(result["volumes"])
        
        if not controllers and not volumes:
            print("   ⚠️  RAID информация недоступна")
        else:
            print(f"   ✅ Контроллеров: {len(controllers)}, RAID массивов: {len(volumes)}")
        
        return {"Controllers": controllers, "Тома": volumes}
    
    def _get_raid_from_huawei_storages(self, storages_data):
        """Получение RAID информации из Huawei Storages коллекции"""
        controllers = []
        volumes = []
        
        for storage_member in storages_data.get("Members", []):
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
                ctrl_data = storage_controllers[0]
                
                ctrl_info = {
                    "ID": storage.get("Id", "N/A"),
                    "Name": storage.get("Name", "N/A"),
                    "Model": ctrl_data.get("Model", "N/A"),
                    "SerialNumber": ctrl_data.get("SerialNumber", "N/A"),
                    "FirmwareVersion": {"VersionString": ctrl_data.get("FirmwareVersion", "N/A")},
                    "Status": ctrl_data.get("Status", {}).get("Health", "N/A"),
                }
                controllers.append(ctrl_info)
            
            # Получаем тома (RAID массивы) через ссылку Volumes
            volumes_ref = storage.get("Volumes")
            if volumes_ref and isinstance(volumes_ref, dict) and "@odata.id" in volumes_ref:
                volumes_path = self._extract_path(volumes_ref["@odata.id"])
                volumes_data = self._get(volumes_path)
                
                if volumes_data and volumes_data.get("Members"):
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
                            capacity_mib = vol_data.get("CapacityMiB")
                            
                            if capacity_bytes:
                                capacity_gb = capacity_bytes / (1024**3)
                            elif capacity_mib:
                                capacity_gb = capacity_mib / 1024
                            else:
                                capacity_gb = 0
                            
                            # RAID уровень из Huawei OEM
                            huawei_oem = vol_data.get("Oem", {}).get("Huawei", {})
                            raid_type = huawei_oem.get("VolumeRaidLevel", "N/A")
                            if raid_type and raid_type.startswith("RAID"):
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
        
        return {"controllers": controllers, "volumes": volumes}
    
    
    def _get_volumes_from_collection(self, volumes_collection):
        """Получение томов из прямой коллекции Volumes"""
        volumes = []
        
        for vol_member in volumes_collection.get("Members", []):
            vol_href = self._get_first_href(vol_member)
            if not vol_href:
                continue
            
            vol_path = self._extract_path(vol_href)
            vol_data = self._get(vol_path)
            
            if vol_data:
                # Размер
                capacity_bytes = vol_data.get("CapacityBytes")
                capacity_mib = vol_data.get("CapacityMiB")
                
                if capacity_bytes:
                    capacity_gb = capacity_bytes / (1024**3)
                elif capacity_mib:
                    capacity_gb = capacity_mib / 1024
                else:
                    capacity_gb = 0
                
                # RAID уровень
                raid_type = vol_data.get("RAIDType") or vol_data.get("VolumeType", "N/A")
                if raid_type and isinstance(raid_type, str) and raid_type.startswith("RAID"):
                    raid_type = raid_type.replace("RAID", "").strip()
                
                volume = {
                    "ID": vol_data.get("Id", "N/A"),
                    "Name": vol_data.get("Name", "N/A"),
                    "RAID": raid_type,
                    "Capacity": round(capacity_gb, 2),
                    "Controller": "N/A",
                    "Status": vol_data.get("Status", {}).get("Health", "N/A"),
                }
                volumes.append(volume)
        
        return volumes
    
    def get_power_supplies(self):
        """
        Получение информации о блоках питания
        
        Returns:
            list: список блоков питания
        """
        print("\n🔌 Получение информации о блоках питания...")
        
        power_supplies = []
        
        # Находим Chassis ID
        chassis_data = self._get("/redfish/v1/Chassis")
        if not chassis_data:
            print("   ⚠️  Информация о блоках питания недоступна")
            return power_supplies
        
        # Берем первый chassis
        chassis_members = chassis_data.get("Members", [])
        if not chassis_members:
            print("   ⚠️  Chassis не найден")
            return power_supplies
        
        chassis_href = self._get_first_href(chassis_members[0])
        chassis_id = chassis_href.split("/")[-1] if chassis_href else "1"
        
        # Получаем данные о питании из Chassis
        power_data = self._get(f"/redfish/v1/Chassis/{chassis_id}/Power")
        
        if not power_data:
            print("   ⚠️  Информация о блоках питания недоступна")
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
        
        print(f"   ✅ Найдено блоков питания: {len(power_supplies)}")
        
        return power_supplies
    
    def get_fans(self):
        """
        Получение информации о вентиляторах
        
        Returns:
            list: список вентиляторов
        """
        print("\n🌀 Получение информации о вентиляторах...")
        
        fans = []
        
        # Находим Chassis ID
        chassis_data = self._get("/redfish/v1/Chassis")
        if not chassis_data:
            print("   ⚠️  Информация о вентиляторах недоступна")
            return fans
        
        # Берем первый chassis
        chassis_members = chassis_data.get("Members", [])
        if not chassis_members:
            print("   ⚠️  Chassis не найден")
            return fans
        
        chassis_href = self._get_first_href(chassis_members[0])
        chassis_id = chassis_href.split("/")[-1] if chassis_href else "1"
        
        # Получаем термальные данные из Chassis
        thermal_data = self._get(f"/redfish/v1/Chassis/{chassis_id}/Thermal")
        
        if not thermal_data:
            print("   ⚠️  Информация о вентиляторах недоступна")
            return fans
        
        # Извлекаем вентиляторы
        for fan in thermal_data.get("Fans", []):
            if not isinstance(fan, dict):
                continue
            
            # Скорость
            rpm = fan.get("Reading")
            if fan.get("ReadingUnits") == "Percent":
                rpm = None
            
            fan_info = {
                "Name": fan.get("Name") or fan.get("FanName") or fan.get("MemberId") or fan.get("Id", "N/A"),
                "Speed": rpm if rpm else "N/A",
                "Percent": fan.get("Reading") if fan.get("ReadingUnits") == "Percent" else "N/A",
                "Location": fan.get("PhysicalContext", "N/A"),
                "Status": fan.get("Status", {}).get("Health", "N/A"),
                "State": fan.get("Status", {}).get("State", "N/A"),
            }
            fans.append(fan_info)
        
        print(f"   ✅ Найдено вентиляторов: {len(fans)}")
        
        return fans
    
    def get_all_inventory(self):
        """
        Собирает всю информацию о сервере
        
        Returns:
            dict: полный инвентарь сервера
        """
        print(f"\n🔍 Сбор информации о сервере Huawei {self.ip_address}...")
        
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

