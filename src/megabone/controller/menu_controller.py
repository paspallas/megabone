from enum import Enum, auto
from typing import Dict

from PyQt5.QtWidgets import QMenuBar

from megabone.builder import MenuBuilder

from .main_controller import MainController


class MenuType(Enum):
    FILE = auto()
    EDIT = auto()
    VIEW = auto()
    HELP = auto()


class MainMenuController:
    def __init__(self, controller: MainController) -> None:
        self.controller = controller
        self._menus: Dict[MenuType, MenuBuilder] = {}

        self.create_menus()

        # Connect to signals
        self.controller.documentCreated.connect(self._on_document_created)

    def create_menus(self):
        self._menus[MenuType.FILE] = (
            MenuBuilder("File")
            .action("New", self.controller.on_new, "Ctrl+N")
            .action(
                "Open...",
                shortcut="Ctrl+O",
                callback=self.controller.on_open,
            )
            .submenu("Open Recent")
            .disable()
            .back()
            .separator()
            .action("Save", self.controller.on_save, "Ctrl+S")
            .action(
                "Save As...",
                self.controller.on_save,
                "Ctrl+Shift+S",
            )
            .separator()
            .submenu("Export")
            .action("As Sprite Sheet")
            .disable()
            .back()
            .separator()
            .action("Exit", self.controller.on_quit, "Ctrl+Q")
            .disable_items("Save", "Save As...")
        )

        self._menus[MenuType.EDIT] = (
            MenuBuilder("Edit")
            .action("Undo", self.controller.on_undo, "Ctrl+Z")
            .action("Redo", self.controller.on_redo, "Ctrl+Y")
            .disable_items("Undo", "Redo")
        )

        self._menus[MenuType.HELP] = (
            MenuBuilder("Help")
            .action("Documentation")
            .separator()
            .action("About", callback=self.controller.on_about)
        )

        self._menus[MenuType.VIEW] = (
            MenuBuilder("View")
            .action("Full Screen", self.controller.on_full_screen, "F11")
            .action("Zen Mode", self.controller.on_zen_mode, "Ctrl+Shift+Z")
            .separator()
            .submenu("Show")
            .back()
        )

    def populate_menu_bar(self, menubar: QMenuBar, *menus: MenuType) -> None:
        for menu in menus:
            menubar.addMenu(self._menus.get(menu).build())

    def get_builder(self, name: str) -> MenuBuilder:
        return self._menus.get(name, None)

    def _on_document_created(self):
        self._menus.get(MenuType.FILE).enable_items("Save", "Save As...")
