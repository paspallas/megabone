from megabone.model.sprite import FrameData, SpriteSheetData
from megabone.qt import QApplication, QGuiApplication, QIcon, QPixmap, QSize


class ResourceManager:
    _icon_cache: dict[str, QIcon] = {}
    _pixmap_cache: dict[str, QPixmap] = {}
    _sheet_cache: dict[tuple[str, int, int], SpriteSheetData] = {}
    _frame_cache: dict[tuple[str, int], QPixmap] = {}

    @classmethod
    def get_icon(cls, name: str) -> QIcon:
        if name not in cls._icon_cache:
            cls._icon_cache[name] = QIcon(f":icons/{name}")
        return cls._icon_cache[name]

    @classmethod
    def get_scaled_icon(cls, name: str, size: int) -> QIcon | None:
        icon = cls.get_icon(name)
        if icon:
            pixmap = icon.pixmap(size)

            instance = QApplication.instance()
            assert isinstance(instance, QGuiApplication)

            width = size * int(instance.devicePixelRatio())
            return QIcon(pixmap.scaled(QSize(width, width)))
        return None

    @classmethod
    def get_pixmap(cls, name: str) -> QPixmap:
        if name not in cls._pixmap_cache:
            cls._pixmap_cache[name] = QPixmap(f":images/{name}")
        return cls._pixmap_cache[name]

    @classmethod
    def register_sheet(cls, sheet: SpriteSheetData) -> None:
        key = (sheet.path, sheet.frame_width, sheet.frame_height)
        cls._sheet_cache[key] = sheet

        for frame in sheet.frames:
            cls._frame_cache[(sheet.path, frame.index)] = frame.pixmap

    @classmethod
    def unregister_sheet(cls, path: str) -> None:
        keys_to_remove = [k for k in cls._sheet_cache if k[0] == path]
        for k in keys_to_remove:
            cls._sheet_cache.pop(k, None)

        frame_keys = [k for k in cls._frame_cache if k[0] == path]
        for k in frame_keys:
            cls._frame_cache.pop(k, None)

    @classmethod
    def load_sheet(cls, path: str, fw: int, fh: int) -> SpriteSheetData:
        key = (path, fw, fh)
        if key in cls._sheet_cache:
            return cls._sheet_cache[key]

        source = QPixmap(path)
        cols = source.width() // fw
        rows = source.height() // fh

        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = source.copy(col * fw, row * fh, fw, fh)
                if not cls._is_empty(frame):
                    frames.append(FrameData(index=len(frames), pixmap=frame))

        sheet = SpriteSheetData(path, fw, fh, frames)
        cls._sheet_cache[key] = sheet
        return sheet

    @classmethod
    def _is_empty(cls, pixmap: QPixmap) -> bool:
        image = pixmap.toImage()

        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixel(x, y) >> 24 != 0:  # non-transparent pixel
                    return False
        return True
