from PyQt5.QtWidgets import QMainWindow

from megabone.widget import MenuBuilder

from .main_controller import MainController


class MainMenuController:
    def __init__(self, controller: MainController, window: QMainWindow) -> None:
        self.controller = controller
        self.window = window

        self.create_menus()

        # Connect to signals
        self.controller.documentCreated.connect(self._on_document_created)

    def create_menus(self):
        self.file = (
            MenuBuilder("File", self.window)
            .add_action(
                "new", "New...", shortcut="Ctrl+N", triggered=self.controller.new
            )
            .add_action(
                "open",
                "Open...",
                shortcut="Ctrl+O",
                triggered=self.controller.open,
            )
            .add_action(
                "save", "Save", shortcut="Ctrl+S", triggered=self.controller.save
            )
            .add_action(
                "save_as",
                "Save As...",
                shortcut="Ctrl+Shift+S",
                triggered=self.controller.save,
            )
            .add_separator()
            .begin_submenu("Export")
            .add_action("sprite_sheet", "As Sprite Sheet")
            .end_submenu()
            .add_separator()
            .add_action(
                "exit", "Exit", shortcut="Ctrl+Q", triggered=self.controller.quit
            )
        )

        self.edit = (
            MenuBuilder("Edit", self.window)
            .add_action(
                "undo", "Undo", shortcut="Ctrl+Z", triggered=self.controller.undo
            )
            .add_action(
                "redo", "Redo", shortcut="Ctrl+Y", triggered=self.controller.redo
            )
        )

        self.help = (
            MenuBuilder("Help", self.window)
            .add_action("docs", "Documentation")
            .add_separator()
            .add_action("about", "About", triggered=self.controller.about)
        )

        self.view = MenuBuilder("View", self.window)

        self.window.menuBar().addMenu(self.file.build())
        self.window.menuBar().addMenu(self.edit.build())
        self.window.menuBar().addMenu(self.view.build())
        self.window.menuBar().addMenu(self.help.build())

        # Disable menus until a document is created
        self.file.disable_items("save", "save_as")
        self.edit.disable_items("undo", "redo")

    def _on_document_created(self):
        self.file.enable_items("save", "save_as")
