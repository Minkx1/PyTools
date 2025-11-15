"""===== saves.py ====="""

import json, os
from pathlib import Path
from cryptography.fernet import Fernet

class SaveManager:
    """
    A secure manager class for saving and loading object attributes to JSON.
    Data is encrypted to prevent manual modification.
    """

    SECRET_KEY = b'pEOjQ1gZ9beUbv4GPGVg3PnOj-2gCJn513DlLVazk9Q=' 

    def __init__(self, appdata: bool = True, path:str = None, name:str = "data"):
        from .engine import NovaEngine
        self.engine = NovaEngine.Engine
        self.path = path
        self.name = name
        self.cipher = Fernet(self.SECRET_KEY)

        if self.path is None:
            self.path = self.engine.app_name

        if appdata:
            if os.name == "nt":  # Windows
                app_data_path = os.getenv("APPDATA")
                self.main_dir = os.path.join(app_data_path, path)
            else:
                self.main_dir = os.path.join(Path.home(), f".{self.path}")
        else:
            self.main_dir = self.path

        os.makedirs(self.main_dir, exist_ok=True)
        self.data_file = os.path.join(self.main_dir, f"{name}.novasave")

        self.vars: list[str] = []

    def _get_globals(self) -> dict:
        from .dev_tools import get_globals
        return get_globals()

    def set_vars(self, vars: list[str]):
        self.vars = vars
        return self

    def save(self) -> dict:
        g = self._get_globals()
        values = {}

        for key in self.vars:
            parts = key.split(".")
            if len(parts) == 1:
                if parts[0] in g:
                    values[key] = g[parts[0]]
            else:
                obj = g.get(parts[0])
                if obj is None:
                    continue
                for attr in parts[1:]:
                    obj = getattr(obj, attr, None)
                    if obj is None:
                        break
                if obj is not None:
                    values[key] = obj

        json_bytes = json.dumps(values).encode("utf-8")
        encrypted = self.cipher.encrypt(json_bytes)

        with open(self.data_file, "wb") as f:
            f.write(encrypted)

        return values

    def load(self) -> dict:
        if not os.path.exists(self.data_file):
            return {}

        with open(self.data_file, "rb") as f:
            encrypted = f.read()

        try:
            json_bytes = self.cipher.decrypt(encrypted)
            values = json.loads(json_bytes)
        except Exception as e:
            print("Помилка завантаження або файл змінено:", e)
            return {}

        g = self._get_globals()
        for key in self.vars:
            if key not in values:
                continue

            parts = key.split(".")
            if len(parts) == 1:
                g[parts[0]] = values[key]
            else:
                obj = g.get(parts[0])
                if obj is None:
                    continue
                for attr in parts[1:-1]:
                    obj = getattr(obj, attr, None)
                    if obj is None:
                        break
                if obj is not None:
                    setattr(obj, parts[-1], values[key])

        return values

    def get_value(self, var: str):
        if not os.path.exists(self.data_file):
            return None
        with open(self.data_file, "rb") as f:
            encrypted = f.read()
        try:
            json_bytes = self.cipher.decrypt(encrypted)
            values = json.loads(json_bytes)
        except Exception as e:
            print("Помилка читання або файл змінено:", e)
            return None
        return values.get(var, None)
