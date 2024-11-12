from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QFileDialog

import megabone.util.constants as c


class FileDialog:
    @staticmethod
    def open_file() -> Optional[Path]:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
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
    def save_file() -> Optional[Path]:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
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
    def select_directory() -> Optional[Path]:
        folder = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if folder:
            return Path(folder)
