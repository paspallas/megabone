from megabone.qt import QApplication, QIcon, QPixmap


class ResourceManager:
    _icon_cache: dict[str, QIcon] = {}
    _pixmap_cache: dict[str, QPixmap] = {}

    @staticmethod
    def get_icon(name: str) -> QIcon:
        if name not in ResourceManager._icon_cache:
            ResourceManager._icon_cache[name] = QIcon(f":icons/{name}")
        return ResourceManager._icon_cache[name]

    @staticmethod
    def get_scaled_icon(name: str, size: int) -> QIcon | None:
        icon = ResourceManager.get_icon(name)
        if icon:
            pixmap = icon.pixmap(size)

            instance = QApplication.instance()
            assert instance is not None

            return QIcon(pixmap.scaled(size * instance.devicePixelRatio()))
        return None

    @staticmethod
    def get_pixmap(name: str) -> QPixmap:
        if name not in ResourceManager._pixmap_cache:
            ResourceManager._pixmap_cache[name] = QPixmap(f":images/{name}")
        return ResourceManager._pixmap_cache[name]

    @staticmethod
    def preload_resources(resources: str) -> None:
        pass
