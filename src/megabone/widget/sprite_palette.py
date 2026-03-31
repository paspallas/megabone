from megabone.dialog import FileDialog
from megabone.dialog.sprite_sheet_dialog import SpriteSheetDialog
from megabone.event_filter import PanControl, ZoomControl
from megabone.manager.resource import ResourceManager
from megabone.model.sprite import FrameData, SpriteSheetData
from megabone.qt import (
    QAction,
    QDialog,
    QDrag,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QMimeData,
    QPixmap,
    QSizePolicy,
    QSplitter,
    Qt,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class SpritePalettePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sheets: dict[str, SpriteSheetData] = {}  # path → sheet

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Top: sheet list ---
        sheet_panel = QWidget()
        sheet_layout = QVBoxLayout(sheet_panel)
        sheet_layout.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        header.addWidget(QLabel("Spritesheets"))
        header.addStretch()

        self._add_btn = QToolButton()
        self._add_btn.setText("+")
        self._add_btn.setToolTip("Import spritesheet")
        self._add_btn.clicked.connect(self._import_png)
        header.addWidget(self._add_btn)

        self._remove_btn = QToolButton()
        self._remove_btn.setText("−")
        self._remove_btn.setToolTip("Remove selected spritesheet")
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._remove_sheet)
        header.addWidget(self._remove_btn)

        sheet_layout.addLayout(header)

        self._sheet_list = QListWidget()
        self._sheet_list.setMaximumHeight(120)
        self._sheet_list.currentItemChanged.connect(self._on_sheet_selected)
        self._sheet_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._sheet_list.customContextMenuRequested.connect(self._sheet_context_menu)
        sheet_layout.addWidget(self._sheet_list)

        splitter.addWidget(sheet_panel)

        # --- Bottom: frame scene ---
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene)
        self._configure_view()
        splitter.addWidget(self._view)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def _configure_view(self) -> None:
        self._view.centerOn(0, 0)
        self._view.setContentsMargins(0, 0, 0, 0)
        self._view.setMouseTracking(True)
        self._view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self._view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._view.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self._view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self._view.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self._view.setFrameStyle(QFrame.Shape.NoFrame)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._view.setDragMode(QGraphicsView.DragMode.NoDrag)
        ZoomControl(self._view)
        PanControl(self._view)

    def _import_png(self) -> None:
        path = FileDialog.open_image()
        if not path:
            return

        path_str = str(path)
        if path_str in self._sheets:
            # Sheet already loaded — just select it
            self._select_sheet(path_str)
            return

        dialog = SpriteSheetDialog(path)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        sprites = dialog.get_sprites()
        if not sprites:
            QMessageBox.warning(self, "No Sprites", "No non-transparent frames found.")
            return

        sheet = SpriteSheetData(
            path=path_str,
            frame_width=dialog.frame_size.w,
            frame_height=dialog.frame_size.h,
            frames=[FrameData(index=i, pixmap=px) for i, px in enumerate(sprites)],
        )
        ResourceManager.register_sheet(sheet)
        self._add_sheet(sheet)

    def _add_sheet(self, sheet: SpriteSheetData) -> None:
        self._sheets[sheet.path] = sheet

        name = sheet.path.split("/")[-1]
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, sheet.path)
        item.setToolTip(sheet.path)
        self._sheet_list.addItem(item)
        self._sheet_list.setCurrentItem(item)

    def _remove_sheet(self) -> None:
        current = self._sheet_list.currentItem()
        if not current:
            return

        path = current.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Remove Sheet",
            f"Remove '{current.text()}' from the palette?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self._sheets.pop(path, None)
        ResourceManager.unregister_sheet(path)
        self._sheet_list.takeItem(self._sheet_list.row(current))

        # Show next sheet or clear
        if self._sheet_list.count() > 0:
            self._sheet_list.setCurrentRow(0)
        else:
            self._scene.clear()
            self._remove_btn.setEnabled(False)

    def _select_sheet(self, path: str) -> None:
        for i in range(self._sheet_list.count()):
            item = self._sheet_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == path:
                self._sheet_list.setCurrentItem(item)
                return

    def _on_sheet_selected(
        self, current: QListWidgetItem, _previous: QListWidgetItem
    ) -> None:
        if not current:
            return
        path = current.data(Qt.ItemDataRole.UserRole)
        sheet = self._sheets.get(path)
        if sheet:
            self._remove_btn.setEnabled(True)
            self._populate(sheet)

    def _sheet_context_menu(self, pos) -> None:
        item = self._sheet_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self._remove_sheet)
        menu.addAction(remove_action)
        menu.exec(self._sheet_list.mapToGlobal(pos))

    def _populate(self, sheet: SpriteSheetData) -> None:
        self._scene.clear()
        padding = 4
        cols = 2

        for i, frame in enumerate(sheet.frames):
            col = i % cols
            row = i // cols
            x = col * (sheet.frame_width + padding)
            y = row * (sheet.frame_height + padding)

            item = PaletteFrameItem(frame.pixmap, sheet.path, frame.index)
            item.setPos(x, y)
            self._scene.addItem(item)


class PaletteFrameItem(QGraphicsPixmapItem):
    def __init__(
        self,
        pixmap: QPixmap,
        path: str,
        index: int,
    ):
        super().__init__(None)
        self.setPixmap(pixmap)
        self._path = path
        self._index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_drag(event)
        super().mousePressEvent(event)

    def _start_drag(self, event) -> None:
        mime = QMimeData()
        mime.setData(
            "application/x-megabone-sprite", f"{self._path}|{self._index}".encode()
        )

        drag = QDrag(event.widget())
        drag.setMimeData(mime)
        thumb = self.pixmap().scaled(
            64,
            64,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        drag.setPixmap(thumb)
        drag.setHotSpot(thumb.rect().center())
        drag.exec(Qt.DropAction.CopyAction)
        drag = None

    def hoverEnterEvent(self, event) -> None:
        self.setOpacity(0.75)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setOpacity(1.0)
        super().hoverLeaveEvent(event)
