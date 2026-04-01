from megabone.qt import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
)


class ShortcutHint(QWidget):
    def __init__(self, keys: str, description: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        key_label = QLabel(keys)
        key_label.setObjectName("shortcutKey")
        key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_label.setFixedWidth(80)

        desc_label = QLabel(description)
        desc_label.setObjectName("shortcutDesc")

        layout.addWidget(key_label)
        layout.addWidget(desc_label)
        layout.addStretch()


class WelcomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("MegaBone")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Skeletal Animation Editor")
        subtitle.setObjectName("welcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        root.addSpacing(48)

        hints_container = QWidget()
        hints_layout = QVBoxLayout(hints_container)
        hints_layout.setSpacing(12)

        hints = [
            ("Ctrl+N", "Create a new document"),
            ("Ctrl+O", "Open an existing document"),
        ]
        for keys, desc in hints:
            hints_layout.addWidget(ShortcutHint(keys, desc))

        root.addWidget(hints_container)

        self.setStyleSheet("""
            WelcomeWidget {
                background-color: palette(base);
            }
            #welcomeTitle {
                font-size: 28px;
                font-weight: bold;
                color: palette(text);
            }
            #welcomeSubtitle {
                font-size: 14px;
                color: palette(mid);
            }
            #shortcutKey {
                font-family: monospace;
                font-size: 12px;
                font-weight: bold;
                color: palette(button-text);
                background: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 2px 6px;
            }
            #shortcutDesc {
                font-size: 13px;
                color: palette(text);
            }
        """)
