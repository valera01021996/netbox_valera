import requests
import json
import os
import time

from vendors.base.vendor import BaseProvider


class HPProvider(BaseProvider):
    """
    Класс для работы с HP сервером через Redfish API
    Поддерживает и Gen9 (через REST v1) и Gen10+ (через Redfish v1)
    """
    #
    # def __init__(self, ip_address, username, password):
    #     super().__init__(ip_address, username, password)

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
            return value.get("@odata.id") or value.get("href")
        if isinstance(value, list) and value:
            for item in value:
                if isinstance(item, dict):
                    href = item.get("@odata.id") or item.get("href")
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

    def get_system_info(self):
        print("\n📊 Получение информации о системе...")

        data = self._get("/redfish/v1/Systems/1")
        if not data:
            return {}

        system_info = {
            "Manufacturer": data.get("Manufacturer", "N/A"),
            "Model": data.get("Model", "N/A"),
            "SerialNumber": data.get("SerialNumber", "N/A"),
            "SKU": data.get("SKU", "N/A"),
            "BIOSVersion": data.get("BiosVersion", "N/A"),
            "PowerState": data.get("PowerState", "N/A"),
            "Status": data.get("Status", {}).get("Health", "N/A"),
        }

        return system_info

    def get_processor_info(self):
        """
        Получение информации о процессорах
        Пробует разные пути API для разных поколений HP серверов

        Returns:
            list: список процессоров
        """
        print("\n🖥️  Получение информации о процессорах...")

        processors = []

        # Список путей для попыток (от новых к старым)
        paths_to_try = [
            "/redfish/v1/Systems/1/Processors",  # Gen10+
            "/rest/v1/Systems/1/Processors",  # Gen9 вариант 1
            "/rest/v1/systems/1/processors",  # Gen9 вариант 2 (lowercase)
        ]

        data = None
        for path in paths_to_try:
            data = self._get(path)
            if data and data.get("Members"):
                print(f"   ℹ️  Используем путь: {path}")
                break

        if not data:
            print("   ⚠️  Не удалось получить информацию о процессорах")
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

            # Проверяем что процессор установлен (может быть Enabled, Present, или другое)
            state = proc_data.get("Status", {}).get("State", "")
            # Для Gen9 может не быть поля State или оно может быть другим
            if state and state not in ["Enabled", "Present", "OK"]:
                continue

            processor = {
                "ID": proc_data.get("Id", "N/A"),
                "Model": proc_data.get("Model") or proc_data.get("Name") or "N/A",
                "Manufacturer": proc_data.get("Manufacturer", "N/A"),
                "TotalCores": proc_data.get("TotalCores") or proc_data.get("CoreCount") or "N/A",
                "TotalThreads": proc_data.get("TotalThreads") or proc_data.get("ThreadCount") or "N/A",
                "MaxSpeed (MHz)": proc_data.get("MaxSpeedMHz") or proc_data.get("MaximumFrequencyMHz") or "N/A",
                "Status": proc_data.get("Status", {}).get("Health", "N/A"),
            }
            processors.append(processor)

        print(f"   ✅ Найдено процессоров: {len(processors)}")
        return processors

    def get_memory_info(self):
        """
        Получение информации о памяти
        Пробует разные пути API для разных поколений HP серверов

        Returns:
            dict: информация о памяти
        """
        print("\n💾 Получение информации о памяти...")

        memory_modules = []
        total_memory_gb = 0

        # Список путей для попыток (от новых к старым)
        paths_to_try = [
            "/redfish/v1/Systems/1/Memory",  # Gen10+
            "/rest/v1/Systems/1/Memory",  # Gen9 вариант 1
            "/rest/v1/systems/1/memory",  # Gen9 вариант 2 (lowercase)
        ]

        data = None
        for path in paths_to_try:
            data = self._get(path)
            if data and data.get("Members"):
                print(f"   ℹ️  Используем путь: {path}")
                break

        if not data:
            print("   ⚠️  Не удалось получить информацию о памяти")
            return {"Total_memory (GB)": 0, "Modules": []}

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
            # Для Gen9 может не быть поля State или оно может быть другим
            state = mem_data.get("Status", {}).get("State", "")
            if state and state not in ["Enabled", "Present", "OK", "Populated"]:
                continue

            # Размер может быть в разных полях
            capacity_mib = mem_data.get("CapacityMiB") or mem_data.get("SizeMB")
            if not capacity_mib:
                # Если нет размера, значит слот пустой
                continue

            capacity_gb = capacity_mib / 1024
            total_memory_gb += capacity_gb

            module = {
                "DeviceLocator": mem_data.get("DeviceLocator") or mem_data.get("Device") or mem_data.get(
                    "SocketLocator") or mem_data.get("Id", "N/A"),
                "Capacity (GB)": round(capacity_gb, 2),
                "MemoryDeviceType": mem_data.get("MemoryDeviceType") or mem_data.get("Type") or mem_data.get("DIMMType") or "N/A",
                "OperatingSpeedMhz": mem_data.get("OperatingSpeedMhz") or mem_data.get("SpeedMHz") or mem_data.get(
                    "DIMMTechnology") or "N/A",
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
        Для Gen9 использует SmartStorage API

        Returns:
            list: список дисков
        """
        print("\n💿 Получение информации о хранилище...")

        drives = []

        # Попытка 1: Стандартный Redfish Storage (Gen10+)
        data = self._get("/redfish/v1/Systems/1/Storage")

        if data and data.get("Members"):
            print("   ℹ️  Используем стандартный Redfish Storage API")
            drives = self._get_storage_redfish(data)
        else:
            # Попытка 2: SmartStorage для Gen9
            print("   ℹ️  Используем SmartStorage API (HP Gen9)")
            drives = self._get_storage_smartstorage()

        print(f"   ✅ Найдено дисков: {len(drives)}")
        return drives

    def _get_storage_redfish(self, storage_data):
        """Получение дисков через стандартный Redfish Storage"""
        drives = []

        for storage_member in storage_data.get("Members", []):
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
            for drive_ref in drives_list:
                drive_href = self._get_first_href(drive_ref)
                if not drive_href:
                    continue

                drive_path = self._extract_path(drive_href)
                drive_data = self._get(drive_path)

                if drive_data:
                    drive = self._normalize_drive(drive_data)
                    if drive:
                        drive["Controller"] = controller_name
                        drives.append(drive)

        return drives

    def _get_storage_smartstorage(self):
        """
        Получение дисков через HP SmartStorage API (Gen9)
        Это упрощенная версия из provider.py для понимания junior'ом
        """
        drives = []

        # Шаг 1: Получаем SmartStorage корень
        smartstorage = self._get("/redfish/v1/Systems/1/SmartStorage")
        if not smartstorage:
            print("   ⚠️  SmartStorage API недоступен")
            return drives

        # Шаг 2: Получаем ссылку на ArrayControllers
        links = smartstorage.get("Links") or smartstorage.get("links") or {}
        array_controllers_ref = links.get("ArrayControllers")

        if not array_controllers_ref:
            print("   ⚠️  ArrayControllers не найдены")
            return drives

        # Шаг 3: Получаем список контроллеров
        ac_href = self._get_first_href(array_controllers_ref)
        ac_path = self._extract_path(ac_href)
        controllers_data = self._get(ac_path)

        if not controllers_data:
            print("   ⚠️  Не удалось получить контроллеры")
            return drives

        # Шаг 4: Для каждого контроллера получаем физические диски
        for controller_member in controllers_data.get("Members", []):
            controller_href = self._get_first_href(controller_member)
            if not controller_href:
                continue

            controller_path = self._extract_path(controller_href)
            controller = self._get(controller_path)

            if not controller:
                continue

            ctrl_id = controller.get("Id", "Unknown")

            # Получаем ссылку на физические диски
            ctrl_links = controller.get("Links") or controller.get("links") or {}
            physical_drives_ref = ctrl_links.get("PhysicalDrives")

            if not physical_drives_ref:
                continue

            pd_href = self._get_first_href(physical_drives_ref)
            pd_path = self._extract_path(pd_href)

            # Важно для Gen9! Пробуем с параметром ?page=1&count=ALL
            # Это заставляет iLO вернуть все диски сразу
            drives_collection = self._get(f"{pd_path}?page=1&count=ALL")

            # Если не получилось, пробуем без параметров
            if not drives_collection:
                drives_collection = self._get(pd_path)

            if not drives_collection:
                continue

            # Получаем каждый диск
            for drive_member in drives_collection.get("Members", []):
                drive_href = self._get_first_href(drive_member)
                if not drive_href:
                    continue

                drive_path = self._extract_path(drive_href)
                drive_data = self._get(drive_path)

                if drive_data:
                    drive = self._normalize_drive_gen9(drive_data, ctrl_id)
                    if drive:
                        drives.append(drive)

        return drives

    def _normalize_drive(self, drive_data):
        """Нормализация данных диска из Redfish API"""
        capacity_bytes = drive_data.get("CapacityBytes")
        if not capacity_bytes:
            return None

        capacity_gb = capacity_bytes / (1024 ** 3)

        return {
            "ID": drive_data.get("Id", "N/A"),
            "Model": drive_data.get("Model", "N/A"),
            "Capacity": round(capacity_gb, 2),
            "MediaType": drive_data.get("MediaType", "N/A"),
            "Protocol": drive_data.get("Protocol", "N/A"),
            "SerialNumber": drive_data.get("SerialNumber", "N/A"),
            "Location": "N/A",  # HP не всегда предоставляет Location
            "Controller": "N/A",  # Будет заполнено из вызывающего кода
            "Status": drive_data.get("Status", {}).get("Health", "N/A"),
        }

    def _normalize_drive_gen9(self, drive_data, controller_id):
        """Нормализация данных диска из SmartStorage API (Gen9)"""
        # Gen9 использует CapacityMiB или CapacityGB
        capacity_mib = drive_data.get("CapacityMiB")
        capacity_gb_raw = drive_data.get("CapacityGB")

        if capacity_mib:
            capacity_gb = capacity_mib / 1024
        elif capacity_gb_raw:
            capacity_gb = float(capacity_gb_raw)
        else:
            return None

        # Слот может быть в разных полях
        slot = None
        port = drive_data.get("Port")
        box = drive_data.get("Box")
        bay = drive_data.get("Bay")

        if port is not None and box is not None and bay is not None:
            slot = f"Port:{port} Box:{box} Bay:{bay}"
        else:
            slot = drive_data.get("Location") or drive_data.get("Id", "N/A")

        return {
            "ID": drive_data.get("Id", "N/A"),
            "Model": drive_data.get("Model", "N/A"),
            "Capacity": round(capacity_gb, 2),
            "MediaType": drive_data.get("MediaType", "N/A"),
            "Protocol": drive_data.get("InterfaceType", "N/A"),
            "SerialNumber": drive_data.get("SerialNumber", "N/A"),
            "Location": slot,
            "Controller": controller_id,
            "Status": drive_data.get("Status", {}).get("Health", "N/A"),
        }

    def get_raid_info(self):
        """
        Получение информации о RAID контроллерах и массивах
        Для Gen9 использует SmartStorage API

        Returns:
            dict: информация о контроллерах и томах
        """
        print("\n🔧 Получение информации о RAID...")

        controllers = []
        volumes = []

        # Для Gen9 используем SmartStorage
        smartstorage = self._get("/redfish/v1/Systems/1/SmartStorage")
        if not smartstorage:
            print("   ⚠️  RAID информация недоступна")
            return {"Controllers": controllers, "Тома": volumes}

        # Получаем ArrayControllers
        links = smartstorage.get("Links") or smartstorage.get("links") or {}
        array_controllers_ref = links.get("ArrayControllers")

        if not array_controllers_ref:
            return {"Controllers": controllers, "Тома": volumes}

        ac_href = self._get_first_href(array_controllers_ref)
        ac_path = self._extract_path(ac_href)
        controllers_data = self._get(ac_path)

        if not controllers_data:
            return {"Controllers": controllers, "Тома": volumes}

        # Для каждого контроллера
        for controller_member in controllers_data.get("Members", []):
            controller_href = self._get_first_href(controller_member)
            if not controller_href:
                continue

            controller_path = self._extract_path(controller_href)
            controller = self._get(controller_path)

            if not controller:
                continue

            # Информация о контроллере
            ctrl_info = {
                "ID": controller.get("Id", "N/A"),
                "Name": controller.get("Name", "N/A"),
                "Model": controller.get("Model", "N/A"),
                "SerialNumber": controller.get("SerialNumber", "N/A"),
                "FirmwareVersion": controller.get("FirmwareVersion", {}).get("Current", "N/A"),
                "Status": controller.get("Status", {}).get("Health", "N/A"),
            }
            controllers.append(ctrl_info)

            # Получаем логические диски (RAID массивы)
            ctrl_links = controller.get("Links") or controller.get("links") or {}
            logical_drives_ref = ctrl_links.get("LogicalDrives")

            if not logical_drives_ref:
                continue

            ld_href = self._get_first_href(logical_drives_ref)
            ld_path = self._extract_path(ld_href)

            # Пробуем с параметром count=ALL для Gen9
            logical_drives_data = self._get(f"{ld_path}?page=1&count=ALL")
            if not logical_drives_data:
                logical_drives_data = self._get(ld_path)

            if not logical_drives_data:
                continue

            # Для каждого логического диска
            for ld_member in logical_drives_data.get("Members", []):
                ld_href = self._get_first_href(ld_member)
                if not ld_href:
                    continue

                ld_path = self._extract_path(ld_href)
                ld_data = self._get(ld_path)

                if ld_data:
                    # Размер
                    capacity_mib = ld_data.get("CapacityMiB")
                    capacity_gb = capacity_mib / 1024 if capacity_mib else 0

                    # RAID уровень
                    raid_type = ld_data.get("Raid") or ld_data.get("RaidType", "N/A")

                    volume = {
                        "ID": ld_data.get("Id") or ld_data.get("LogicalDriveNumber", "N/A"),
                        "Name": ld_data.get("LogicalDriveName") or ld_data.get("Name", "N/A"),
                        "RAID": raid_type,
                        "Capacity": round(capacity_gb, 2),
                        "Controller": ctrl_info["ID"],
                        "Status": ld_data.get("Status", {}).get("Health", "N/A"),
                    }
                    volumes.append(volume)

        print(f"   ✅ Controllers: {len(controllers)}, RAID массивов: {len(volumes)}")

        return {"Controllers": controllers, "Тома": volumes}

    def get_power_supplies(self):
        """
        Получение информации о блоках питания

        Returns:
            list: список блоков питания
        """
        print("\n🔌 Получение информации о блоках питания...")

        power_supplies = []

        # Получаем данные о питании из Chassis
        power_data = self._get("/redfish/v1/Chassis/1/Power")

        # Если не работает через Redfish, пробуем REST API (Gen9)
        if not power_data:
            power_data = self._get("/rest/v1/Chassis/1/Power")

        if not power_data:
            print("   ⚠️  Информация о блоках питания недоступна")
            return power_supplies

        # Извлекаем блоки питания
        for psu in power_data.get("PowerSupplies", []):
            if not isinstance(psu, dict):
                continue

            # Мощность
            capacity_watts = psu.get("PowerCapacityWatts") or psu.get("RatedInputWattage")
            output_watts = psu.get("LastPowerOutputWatts") or psu.get("PowerOutputWatts")

            supply = {
                "Name": psu.get("Name") or psu.get("MemberId") or psu.get("Id", "N/A"),
                "Model": psu.get("Model", "N/A"),
                "SerialNumber": psu.get("SerialNumber", "N/A"),
                "Manufacturer": psu.get("Manufacturer", "N/A"),
                "Capacity (W)": capacity_watts or "N/A",
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

        # Получаем термальные данные из Chassis
        thermal_data = self._get("/redfish/v1/Chassis/1/Thermal")

        # Если не работает через Redfish, пробуем REST API (Gen9)
        if not thermal_data:
            thermal_data = self._get("/rest/v1/Chassis/1/Thermal")

        if not thermal_data:
            print("   ⚠️  Информация о вентиляторах недоступна")
            return fans

        # Извлекаем вентиляторы
        for fan in thermal_data.get("Fans", []):
            if not isinstance(fan, dict):
                continue

            # Скорость может быть в разных полях
            rpm = fan.get("ReadingRPM") or fan.get("CurrentReading")
            if rpm is None and str(fan.get("ReadingUnits", "")).lower() == "rpm":
                rpm = fan.get("Reading")

            fan_info = {
                "Name": fan.get("Name") or fan.get("FanName") or fan.get("MemberId") or fan.get("Id", "N/A"),
                "Speed (RPM)": rpm or "N/A",
                "Percent": fan.get("Reading") if fan.get("ReadingUnits") == "Percent" else "N/A",
                "Location": fan.get("PhysicalContext") or fan.get("Location", "N/A"),
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
        print(f"\n🔍 Сбор информации о сервере {self.ip_address}...")

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

    def close(self):
        """Закрытие сессии"""
        self.session.close()
