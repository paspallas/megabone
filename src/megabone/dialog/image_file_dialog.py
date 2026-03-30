import os

from megabone.qt import QFileDialog, QGridLayout, QLabel, QPixmap, Qt, QVBoxLayout


class ImageFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)

        self.preview_label = QLabel("Preview")
        self.preview_label.setMinimumSize(256, 256)
        self.preview_label.setMaximumSize(256, 256)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #444;")

        # Grab the existing layout and add a right-side column
        grid: QGridLayout = self.layout()
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()
        grid.addLayout(preview_layout, 0, grid.columnCount(), grid.rowCount(), 1)

        self.setMinimumWidth(self.minimumWidth() + 256)

        self.currentChanged.connect(self.show_preview)
        self.fileSelected.connect(self._on_file_selected)
        self.filesSelected.connect(self._on_files_selected)

        self._file_selected: str | None = None
        self._files_selected: list[str] | None = None

    def _on_file_selected(self, file: str):
        self.file_selected = file

    def _on_files_selected(self, files: list[str]):
        self.files_selected = files

    def show_preview(self, path: str):
        if os.path.isfile(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    256,
                    256,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                )
                self.preview_label.setPixmap(scaled_pixmap)
            else:
                self.preview_label.setText("Not an image")
        else:
            self.preview_label.setText("Preview")

    def get_file_selected(self) -> str | None:
        return self.file_selected

    def get_files_selected(self) -> list[str]:
        return self.files_selected or []
