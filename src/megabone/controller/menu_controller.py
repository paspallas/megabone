from collections import OrderedDict
from enum import Enum, auto

from megabone.builder import MenuBuilder
from megabone.manager.document import DocumentManager
from megabone.manager.recent_files import RecentFilesManager
from megabone.qt import QKeySequence, QMenuBar

from .main_controller import MainController


class MenuType(Enum):
    FILE = auto()
    EDIT = auto()
    VIEW = auto()
    HELP = auto()


class MainMenuController:
    def __init__(self, controller: MainController, documents: DocumentManager) -> None:
        self.controller = controller
        self.documents = documents

        self.undo_action = self.documents.undo_group.createUndoAction(
            self.controller, "Undo"
        )
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)

        self.redo_action = self.documents.undo_group.createRedoAction(
            self.controller, "Redo"
        )
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)

        self._menus: OrderedDict[MenuType, MenuBuilder] = OrderedDict()

        self.recent_files = RecentFilesManager()
        self.recent_files.recentFileOPen.connect(self.documents.load_document)
        self.create_menus()

        # Connect signals
        self.documents.addedDocument.connect(self._on_document_created)
        self.documents.openedDocument.connect(
            lambda doc, path: self.recent_files.add_recent_file(path)
        )

    def create_menus(self):
        self._menus[MenuType.FILE] = (
            MenuBuilder("File")
            .action("New", self.documents.create_document, "Ctrl+N")
            .action("Open...", self.documents.open_document, "Ctrl+O")
            .submenu("Recent Files")
            .back()
            .separator()
            .action("Save", self.documents.save_document, "Ctrl+S")
            .action(
                "Save As...",
                self.documents.save_document_as,
                "Ctrl+Shift+S",
            )
            .separator()
            .action("Close Editor", self.documents.close_document, "Ctrl+F4")
            .separator()
            .submenu("Export")
            .action("As Sprite Sheet")
            .disable()
            .back()
            .separator()
            .action("Exit", self.controller.on_quit, "Ctrl+Q")
            .disable_items("Save", "Save As...", "Close Editor")
        )

        self._menus[MenuType.EDIT] = (
            MenuBuilder("Edit")
            .qaction("Undo", self.undo_action)
            .qaction("Redo", self.redo_action)
        )

        self._menus[MenuType.VIEW] = (
            MenuBuilder("View")
            .action("Full Screen", self.controller.on_full_screen, "F11")
            .action("Zen Mode", self.controller.on_zen_mode, "Ctrl+Shift+Z")
            .separator()
            .submenu("Show")
            .back()
        )

        self._menus[MenuType.HELP] = (
            MenuBuilder("Help")
            .action("Documentation")
            .separator()
            .action("About", self.controller.on_about)
        )

    def populate_menu_bar(self, menubar: QMenuBar, *menus: MenuType) -> None:
        if len(menus) == 0:
            for menu in self._menus.values():
                menubar.addMenu(menu.build())
        else:
            for menu in menus:
                menubar.addMenu(self._menus[menu].build())

        self.recent_files.set_menu(
            self._menus[MenuType.FILE].get_submenu("Recent Files")
        )
        self.recent_files.update_menu()

    def get_builder(self, name: MenuType) -> MenuBuilder:
        return self._menus[name]

    def _on_document_created(self):
        self._menus[MenuType.FILE].enable_items("Save", "Save As...", "Close Editor")
