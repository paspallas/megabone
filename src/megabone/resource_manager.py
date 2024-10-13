from typing import Dict
from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication


class ResourceManager:
    _icon_cache: Dict[str, QIcon] = {}
    _pixmap_cache: Dict[str, QPixmap] = {}

    @staticmethod
    def get_icon(name: str) -> QIcon:
        if name not in ResourceManager._icon_cache:
            ResourceManager._icon_cache[name] = QIcon(f":icons/{name}")
        return ResourceManager._icon_cache[name]

    @staticmethod
    def get_scaled_icon(name: str, size: int) -> QIcon:
        icon = ResourceManager._icon_cache[name]
        if icon:
            pixmap = icon.pixmap(size)
            return QIcon(
                pixmap.scaled(size * QApplication.instance().devicePixelRatio())
            )
        return None

    @staticmethod
    def get_pixmap(name: str) -> QPixmap:
        if name not in ResourceManager._pixmap_cache:
            ResourceManager._pixmap_cache[name] = QPixmap(f"f:images/{name}")
        return ResourceManager._pixmap_cache[name]

    @staticmethod
    def get_stylesheet(name: str) -> str:
        file = QFile(f"styles/{name}")
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            return str(file.readAll(), encoding="utf-8")
        return ""

    @staticmethod
    def preload_resources(resources: str) -> None:
        pass
