from pathlib import Path

import megabone.util.constants as c
from megabone.qt import QDialog, QFileDialog

from .image_file_dialog import ImageFileDialog


class FileDialog:
    @staticmethod
    def open_file() -> Path | None:
        options = QFileDialog.Option.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(
            None,
            "Open File...",
            "",
            c._DEFAULT_DESCRIPTOR,
            options=options,
        )

        if file:
            return Path(file)

    @staticmethod
    def save_file() -> Path | None:
        options = QFileDialog.Option.DontUseNativeDialog
        file, _ = QFileDialog.getSaveFileName(
            None,
            "Save File As...",
            "",
            c._DEFAULT_DESCRIPTOR,
            options=options,
        )

        if file:
            if not file.endswith(c._DEFAULT_FILE_EXT):
                file += c._DEFAULT_FILE_EXT

            return Path(file)

    @staticmethod
    def select_directory() -> Path | None:
        folder = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )

        if folder:
            return Path(folder)

    @staticmethod
    def open_image() -> Path | None:
        dialog = ImageFileDialog(
            None, "Open Sprite Sheet Image...", "", "Image Files (*.png)"
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            file = dialog.get_file_selected()

            assert file is not None
            return Path(file)
