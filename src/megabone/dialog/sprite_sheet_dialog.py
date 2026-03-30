from pathlib import Path

from megabone.qt import (
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QImage,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPixmap,
    QPoint,
    QPushButton,
    QRegularExpression,
    QRegularExpressionValidator,
    QSpinBox,
    Qt,
    QVBoxLayout,
)
from megabone.util.image import Image
from megabone.util.types import Point, Size
from megabone.widget.button import AlphaColorPickerButton
from megabone.widget.slider import RoundHandleSlider
from megabone.widget.viewer import ScrollImageViewer


class SpriteSheetDialog(QDialog):
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.image_path = image_path
        self.image = QImage(image_path.resolve().as_posix())

        # Cache checker board image
        self.checker = Image.checker_board(self.image.size(), 8)

        self.frame_size = Size(32, 32)  # Default size
        self.offset = Point(0, 0)
        self.spacing = Point(0, 0)

        self.setup_ui()

        self.update_display()

    def setup_ui(self):
        self.setWindowTitle("Extract Sprites")

        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        right_layout.addSpacing(20)
        left_layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        control_layout.addStretch()

        # Zoom level
        control_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = RoundHandleSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimumWidth(200)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(50)
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        control_layout.addWidget(self.zoom_slider)
        control_layout.addStretch()

        # Alpha channel
        control_layout.addWidget(QLabel("Alpha:"))
        self.alpha_btn = AlphaColorPickerButton(self)
        self.alpha_btn.setToolTip("Pick background color as transparent")
        control_layout.addWidget(self.alpha_btn)

        control_layout.addStretch()
        left_layout.addLayout(control_layout)

        self.img_viewer = ScrollImageViewer(self)
        self.img_viewer.clicked.connect(self.pick_alpha_color)
        self.img_viewer.zoomChanged.connect(
            lambda x: self.zoom_slider.setValue(int(x * 10))
        )
        left_layout.addWidget(self.img_viewer)

        # Image path info
        path_layout = QHBoxLayout()
        path_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        path_layout.addWidget(QLabel("Path:"))

        path_container = QFrame()
        path_container.setFrameStyle(QFrame.Shape.StyledPanel)
        container_layout = QHBoxLayout()
        container_layout.addWidget(QLabel(f"{self.image_path}"))
        path_container.setLayout(container_layout)
        path_layout.addWidget(path_container)

        left_layout.addLayout(path_layout)

        # Connect signals
        self.alpha_btn.clicked.connect(lambda clicked: self.pick_alpha())

        # Frame size input
        frame_size_group = QGroupBox("Size")
        size_layout = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(8, self.image.width())
        self.width_spin.setValue(self.frame_size.w)
        self.width_spin.setSingleStep(8)
        self.width_spin.valueChanged.connect(self.update_size)
        size_layout.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(8, self.image.height())
        self.height_spin.setValue(self.frame_size.h)
        self.height_spin.setSingleStep(8)
        self.height_spin.valueChanged.connect(self.update_size)
        size_layout.addRow("Height:", self.height_spin)

        frame_size_group.setLayout(size_layout)
        right_layout.addWidget(frame_size_group)

        # Offset input
        offset_group = QGroupBox("Offset")
        offset_layout = QFormLayout()

        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(0, self.image.width())
        self.offset_x_spin.setValue(self.offset.x)
        self.offset_x_spin.valueChanged.connect(self.update_size)
        offset_layout.addRow("X:", self.offset_x_spin)

        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(0, self.image.height())
        self.offset_y_spin.setValue(self.offset.y)
        self.offset_y_spin.valueChanged.connect(self.update_size)
        offset_layout.addRow("Y:", self.offset_y_spin)

        offset_group.setLayout(offset_layout)
        right_layout.addWidget(offset_group)

        # Spacing input
        spacing_group = QGroupBox("Spacing")
        spacing_layout = QFormLayout()

        self.spacing_x_spin = QSpinBox()
        self.spacing_x_spin.setRange(0, self.image.width())
        self.spacing_x_spin.setValue(self.spacing.x)
        self.spacing_x_spin.valueChanged.connect(self.update_size)
        spacing_layout.addRow("X:", self.spacing_x_spin)

        self.spacing_y_spin = QSpinBox()
        self.spacing_y_spin.setRange(0, self.image.height())
        self.spacing_y_spin.setValue(self.spacing.y)
        self.spacing_y_spin.valueChanged.connect(self.update_size)
        spacing_layout.addRow("Y:", self.spacing_y_spin)

        spacing_group.setLayout(spacing_layout)
        right_layout.addWidget(spacing_group)

        # Base name input
        name_group = QGroupBox("Name")
        name_layout = QHBoxLayout()

        self.base_name = QLineEdit("sprite")
        self.base_name.setValidator(
            QRegularExpressionValidator(QRegularExpression("[a-zA-Z0-9_()]*"))
        )
        name_layout.addWidget(self.base_name)
        name_group.setLayout(name_layout)
        right_layout.addWidget(name_group)
        right_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        extract_btn = QPushButton("Extract")
        extract_btn.clicked.connect(self.validate_extract)
        button_layout.addWidget(extract_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        right_layout.addLayout(button_layout)

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

    def update_zoom(self, value: int):
        zoom = value / 10.0
        self.img_viewer.set_zoom(zoom)

    def pick_alpha(self):
        self.img_viewer.toggle_click()

    def pick_alpha_color(self, pos: QPoint):
        self.img_viewer.toggle_click()
        color = self.image.pixelColor(pos.x(), pos.y())
        self.alpha_btn.set_color(color)

        # Update the image
        self.image = Image.remove_background(self.image, color)
        self.update_display()

    def update_size(self):
        self.frame_size = Size(self.width_spin.value(), self.height_spin.value())
        self.offset = Point(self.offset_x_spin.value(), self.offset_y_spin.value())
        self.spacing = Point(self.spacing_x_spin.value(), self.spacing_y_spin.value())
        self.update_display()

    def update_display(self):
        pixmap = QPixmap.fromImage(self.image)
        grid = Image.grid(
            pixmap.size(),
            self.frame_size.w,
            self.frame_size.h,
            self.offset.x,
            self.offset.y,
            self.spacing.x,
            self.spacing.y,
        )

        result = Image.flatten([self.checker, pixmap, grid], pixmap.size())
        self.img_viewer.setPixmap(result)

    def validate_extract(self):
        width = self.width_spin.value()
        height = self.height_spin.value()

        if self.image.width() % width != 0 or self.image.height() % height != 0:
            QMessageBox.warning(
                self,
                "Invalid Dimensions",
                "Image Dimensions must be a multiple of frame size!",
            )
            return

        self.accept()

    def get_sprites(self) -> list[QPixmap]:
        return Image.extract_sprites(
            self.image,
            self.frame_size.w,
            self.frame_size.h,
            self.offset.x,
            self.offset.y,
        )
