"""
Encrypted SavesManager
"""
import json
import os
import base64
from cryptography.fernet import Fernet
from pathlib import Path
import platform
from .utils import log


class SavesManager:
    EXT = ".pgtsave"
    _KEY_PARTS = [b"qP3s9aLd82Hn",b"rTf0PpZ2QwErTy",b"UiOpAs"]

    @staticmethod
    def _get_key():
        raw = b"".join(SavesManager._KEY_PARTS)
        key = base64.urlsafe_b64encode(raw[:32])
        return key

    @staticmethod
    def _fullpath(name: str) -> str:
        path = f"{name}{SavesManager.EXT}"

        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        return path

    @staticmethod
    def get_appdata() -> str:

        system = platform.system().lower()

        # ----- WINDOWS -----
        if system == "windows":
            base = os.getenv("APPDATA")  # C:\Users\User\AppData\Roaming
            if not base:
                base = str(Path.home() / "AppData" / "Roaming")

            base = os.path.join(base, "JASG")
            os.makedirs(base, exist_ok=True)
            return str(base)

        # ----- MACOS -----
        if system == "darwin":
            base = os.path.join(str(Path.home()), "Library", "Application Support", "JASG")
            os.makedirs(base, exist_ok=True)
            return str(base)

        # ----- LINUX -----
        if system == "linux":
            base = os.path.join(str(Path.home()), ".local", "share", "JASG")
            os.makedirs(base, exist_ok=True)
            return str(base)
        return ""

    @staticmethod
    def save(name, data):
        path = SavesManager._fullpath(name)
        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")

        f = Fernet(SavesManager._get_key())
        encrypted = f.encrypt(json_bytes)

        with open(path, "wb") as ffile:
            ffile.write(encrypted)


    @staticmethod
    def load(name):
        path = SavesManager._fullpath(name)

        if not os.path.exists(path):
            log(f"Save file not found: {path}", sender="SaveManager", error=True)
            return {}

        try:
            with open(path, "rb") as ffile:
                encrypted = ffile.read()

            # Decrypt
            f = Fernet(SavesManager._get_key())
            decrypted = f.decrypt(encrypted)

            return json.loads(decrypted.decode("utf-8"))
        except Exception as e:
            log(f"Error decrypting save: {e}", sender="SaveManager", error=True)
            return {}
