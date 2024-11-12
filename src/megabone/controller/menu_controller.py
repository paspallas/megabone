from collections import OrderedDict
from enum import Enum, auto
from typing import OrderedDict

from PyQt5.QtWidgets import QMenuBar

from megabone.builder import MenuBuilder
from megabone.manager import DocumentManager

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
        self._menus: OrderedDict[MenuType, MenuBuilder] = OrderedDict()

        self.create_menus()

        # Connect to signals
        self.documents.addedDocument.connect(self._on_document_created)

    def create_menus(self):
        self._menus[MenuType.FILE] = (
            MenuBuilder("File")
            .action("New", self.documents.create_document, "Ctrl+N")
            .action("Open...", self.documents.open_document, "Ctrl+O")
            .submenu("Open Recent")
            .disable()
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
            .action("Undo", self.controller.on_undo, "Ctrl+Z")
            .action("Redo", self.controller.on_redo, "Ctrl+Y")
            .disable_items("Undo", "Redo")
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
                menubar.addMenu(self._menus.get(menu).build())

    def get_builder(self, name: str) -> MenuBuilder:
        return self._menus.get(name, None)

    def _on_document_created(self):
        self._menus.get(MenuType.FILE).enable_items(
            "Save", "Save As...", "Close Editor"
        )
