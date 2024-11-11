from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from .base_modal import BaseModalDialog


class NameInputModalDialog(BaseModalDialog):
    def __init__(
        self,
        parent=None,
        prompt="Input Name:",
    ):
        super().__init__(parent)

        # Create layout
        layout = QVBoxLayout(self)

        # Add prompt label
        self.label = QLabel(prompt)
        layout.addWidget(self.label)

        # Add line edit
        self.name_input = QLineEdit(self)
        self.name_input.setText("")
        self.name_input.selectAll()
        layout.addWidget(self.name_input)

        # Add buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect text changed signal to validation
        self.name_input.textChanged.connect(self.validate_input)

        # Set focus to line edit
        self.name_input.setFocus()

        # Initialize validation state
        self.validate_input("")

    def validate_input(self, text):
        text = text.strip()
        is_valid = True

        # Check for empty string
        if not text:
            is_valid = False

        self.ok_button.setEnabled(is_valid)

    def get_name(self):
        """Return the entered name (stripped of whitespace)"""
        return self.name_input.text().strip()
