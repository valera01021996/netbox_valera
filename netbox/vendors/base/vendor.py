import time

import requests


class BaseProvider:

    def __init__(self, ip_address: str, username: str, password: str):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.base_url = f"https://{ip_address}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False

    def _get(self, path, retry=2, delay=0.3):
        """
        Вспомогательный метод для GET запросов
        Работает и с /redfish/v1 и с /rest/v1

        Args:
            path: путь API (например, "/redfish/v1/Systems/1")
            retry: количество повторных попыток
            delay: задержка между запросами

        Returns:
            dict: JSON ответ от сервера или None при ошибке
        """
        url = f"{self.base_url}{path}"

        for attempt in range(retry):
            try:
                if attempt > 0:
                    time.sleep(delay * (attempt + 1))

                response = self.session.get(url, timeout=30)

                # 404 - ресурс не найден, это нормально
                if response.status_code == 404:
                    return None

                response.raise_for_status()
                time.sleep(delay)  # Задержка чтобы не перегружать iLO

                return response.json() if response.content else None

            except requests.exceptions.ConnectionError as e:
                if attempt < retry - 1:
                    print(f"   ⚠️ Attempt {attempt + 1}/{retry}, reconnecting...")
                    self._recreate_session()
                else:
                    # После всех попыток выбрасываем исключение, чтобы задача могла его обработать
                    raise requests.exceptions.ConnectionError(
                        f"Failed to connect to {self.ip_address} after {retry} attempts: {str(e)}"
                    ) from e
            except Exception:
                if attempt < retry - 1:
                    continue
                return None

        return None

    def _recreate_session(self):
        """Пересоздает сессию при проблемах"""
        try:
            self.session.close()
        except:
            pass
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = False

    def get_all_inventory(self, *args, **kwargs) -> dict:
        raise NotImplemented
