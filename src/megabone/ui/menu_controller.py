from typing import Dict

from PyQt5.QtWidgets import QMenuBar

from megabone.widget import MenuBuilder

from .main_controller import MainController


class MainMenuController:
    def __init__(self, controller: MainController) -> None:
        self.controller = controller
        self._menus: Dict[str, MenuBuilder] = {}

        self.create_menus()

        # Connect to signals
        self.controller.documentCreated.connect(self._on_document_created)

    def create_menus(self):
        self._menus["File"] = (
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

        self._menus["Edit"] = (
            MenuBuilder("Edit")
            .action("Undo", self.controller.on_undo, "Ctrl+Z")
            .action("Redo", self.controller.on_redo, "Ctrl+Y")
            .disable_items("Undo", "Redo")
        )

        self._menus["Help"] = (
            MenuBuilder("Help")
            .action("Documentation")
            .separator()
            .action("About", callback=self.controller.on_about)
        )

        self._menus["View"] = (
            MenuBuilder("View")
            .action("Full Screen", self.controller.on_full_screen, "F11")
            .action("Zen Mode", self.controller.on_zen_mode, "Ctrl+Shift+Z")
            .separator()
            .submenu("Show")
            .back()
        )

    def populate_menu_bar(self, bar: QMenuBar, *menus: str) -> None:
        for menu in menus:
            bar.addMenu(self._menus.get(menu).build())

    def get_builder(self, name: str) -> MenuBuilder:
        return self._menus.get(name, None)

    def _on_document_created(self):
        self.file.enable_items("Save", "Save As...")
