from PyQt5.QtWidgets import QFileDialog


class FileDialog:
    @staticmethod
    def open_file() -> str:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            "Open File",  # title
            "",  # Starting directory
            "Megabone Project File (*.mgb)",  # File types
            options=options,
        )

        if file_name:
            return file_name

    @staticmethod
    def save_file() -> str:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "Megabone Project File (*.mgb)", options=options
        )

        if file_name:
            # Check if the user provided a file extension
            if not file_name.endswith(".mgb"):
                file_name += ".mgb"  # Default extension
                return file_name

    @staticmethod
    def select_directory() -> str:
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if directory:
            return directory
