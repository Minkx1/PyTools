"""===== saves.py ====="""

import json, os
from pathlib import Path
import inspect

class SaveManager:
    """
    A manager class for saving and loading object attributes to JSON.

    Example usage:
        save_manager = SaveManager()
        save_manager.set_vars(["player.hp", "player.money"])
        save_manager.save()
        save_manager.load()
    """

    def __init__(self, appdata: bool = True, path:str = None, name:str = "data"):
        """
        Initialize SaveManager.

        Args:
            appdata (bool): If True, saves data in OS-specific appdata folder.
                            If False, saves in current working directory.
            path (str): If $appdata$ is False, SaveManager will create folder with saves in $path$ directory. 
                  If $appdata$ is True, then in AppData folder will be created $path$.
            name (str): the name of save file.

        """
        from .core import NovaEngine

        self.engine = NovaEngine.Engine
        self.path = path
        self.name = name

        if self.path is None: 
            self.path = self.engine.app_name

        # Choose directory depending on OS
        if appdata:
            if os.name == "nt":  # Windows
                self.app_data_path = os.getenv("APPDATA")
                self.main_dir = os.path.join(self.app_data_path, path)
            else:  # Linux / macOS
                self.main_dir = os.path.join(Path.home(), f".{self.path}")
        else:
            self.main_dir = self.path

        os.makedirs(self.main_dir, exist_ok=True)
        
        if self.name:
            self.data_file = os.path.join(self.main_dir, f"{name}.novasave")
        else:
            self.data_file = os.path.join(self.main_dir, "data.json")

        self.vars: list[str] = []
    
    def _get_globals(self) -> dict:
        """
        Get the caller's global variables.
        Used to resolve object references like 'player.hp'.

        Returns:
            dict: The global scope of the caller.
        """
        from .utils import get_globals
        return get_globals()

    def set_vars(self, vars: list[str]):
        """
        Set which attributes should be saved/loaded.

        Args:
            vars (list[str]): A list of attribute paths (e.g. ["player.hp", "player.money"])
        """
        self.vars = vars
        return self

    def save(self) -> dict:
        """
        Save selected attributes to JSON.

        Example:
            self.vars = ["player.hp", "player.money"]
            -> creates JSON file like:
               {"player.hp": 100, "player.money": 250}

        Returns:
            dict: The dictionary of saved values.
        """
        g = self._get_globals()
        values = {}

        for key in self.vars:
            parts = key.split(".")
            if len(parts) == 1:
                # просто змінна у глобалах
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

        json_str = json.dumps(values)
        hex_str = json_str.encode("utf-8").hex()

        with open(self.data_file, "w") as f:
            f.write(hex_str)

        return values

    def load(self) -> dict:
        """
        Load saved attributes from JSON and apply them to objects.

        Example:
            self.vars = ["player.hp", "player.money"]
            -> modifies player.hp and player.money values in memory.

        Returns:
            dict: The dictionary of loaded values.
        """
        if not os.path.exists(self.data_file):
            return {}

        with open(self.data_file, "r") as f:
            hex_str = f.read().strip()

        try:
            json_str = bytes.fromhex(hex_str).decode("utf-8")
            values = json.loads(json_str)
        except Exception as e:
            print("Помилка завантаження:", e)
            return

        g = self._get_globals()
        for key in self.vars:
            if key not in values:
                continue

            parts = key.split(".")
            if len(parts) == 1:
                # просто змінна
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
    
    def get_value(self, var:str):
        if not os.path.exists(self.data_file):
            return None
        with open(self.data_file, "r", encoding="utf-8") as f:
            values = json.load(f)

        if var not in values: return None
            
        return values.get(var, None)