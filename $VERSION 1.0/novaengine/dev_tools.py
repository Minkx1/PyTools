"""===== DevTools ====="""

import os
import sys
import zipfile
import subprocess

def log(msg: str, sender="NovaEngine", error=False):
    import traceback
    """
    Log a message to console.

    Args:
        msg (str): The message to log.
        sender (str): The sender's name (default "NovaEngine").
        error (bool): If True, prefixes with 'Error:'.
    """
    prefix = f"[{sender}]"
    if error:
        print(f"{prefix} Error: {msg}")
    else:
        print(f"{prefix} {msg}")
    
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type is not None:
        traceback.print_exc()

def get_globals() -> dict:
    """
    Return the global variables of the script that started the call chain (script __main__).
    Works even if called inside a method of a class or engine.
    """
    import inspect

    frame = inspect.currentframe()
    while frame:
        globs = frame.f_globals
        if globs.get("__name__") == "__main__":
            return globs
        frame = frame.f_back
    return {}


class DevTools:
    """
    Developer utilities for packaging and testing.
    """

    @staticmethod
    def build_exe(
        main_file="main.py",
        name="game",
        icon_path="",
        onefile=True,
        noconsole=False,
        dist_path: str = "dist",
    ):
        """
        Build a Windows executable from a Python script using PyInstaller.

        Args:
            main_file (str): Path to the entry Python file.
            name (str): Name of the output exe.
            icon_path (str): Path to an icon file (*.ico).
            onefile (bool): Build as a single exe or as a folder.
            noconsole (bool): Hide console (GUI apps only).
            dist_path (str): Output directory (default = 'dist/').

        Notes:
            - Requires: pip install pyinstaller
            - Antivirus may give false positives.
            - Best used inside a clean venv.
        """

        flags = ["pyinstaller", f"--name={name}"]

        if onefile:
            flags.append("--onefile")
        if noconsole:
            flags.append("--noconsole")
        if icon_path:
            flags.append(f"--icon={icon_path}")
        if dist_path:
            flags.append(f"--distpath={dist_path}")

        flags.append(main_file)

        try:
            log("Running: " + " ".join(flags), sender="DevTools")
            subprocess.run(flags, check=True)
            out_dir = dist_path or "dist"
            log(
                f"✅ Build complete! File saved in '{out_dir}/{name}.exe'",
                sender="DevTools",
            )
        except subprocess.CalledProcessError as e:
            log(f"❌ Build failed: {e}", error=True, sender="DevTools")

    @staticmethod
    def build_archive(
        main_file="main.py",
        name="game",
        icon_path: str = None,
        onefile=True,
        noconsole=False,
        dist_path=None,
        sprite_dir="sprites",
        archive_dist="releases",
        archive_name: str = None,
    ):
        """
        Build exe and pack it with asset folder into a .zip archive.

        Args:
            main_file (str): entry file for PyInstaller
            name (str): exe name
            sprite_dir (str): folder with sprites/assets
            archive_dist (str): where to save archive (default = releases/)
            archive_name (str): name of archive (default = <name>.zip)
        """
        # 1. Спочатку збираємо exe
        DevTools.build_exe(
            main_file=main_file,
            name=name,
            icon_path=icon_path, # type: ignore
            onefile=onefile,
            noconsole=noconsole,
            dist_path=str(dist_path),
        )

        exe_path = os.path.join(dist_path or "dist", f"{name}.exe")
        if not os.path.exists(exe_path):
            log(f"❌ EXE not found at {exe_path}", error=True, sender="DevTools")
            return

        # 2. Готуємо архів
        os.makedirs(archive_dist, exist_ok=True)
        archive_name = archive_name or f"{name}.zip"
        archive_path = os.path.join(archive_dist, archive_name)

        try:
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Додаємо exe
                zipf.write(exe_path, arcname=os.path.basename(exe_path))

                # Додаємо папку з ассетами
                if os.path.isdir(sprite_dir):
                    for root, _, files in os.walk(sprite_dir):
                        for file in files:
                            filepath = os.path.join(root, file)
                            arcpath = os.path.relpath(
                                filepath, start=os.path.dirname(sprite_dir)
                            )
                            zipf.write(filepath, arcname=arcpath)

            log(f"✅ Archive built: {archive_path}", sender="DevTools")

        except Exception as e:
            log(f"❌ Archive build failed: {e}", error=True, sender="DevTools")