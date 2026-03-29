from enum import Enum, auto

from megabone.qt import QWidget

from .base_modal import BaseModalDialog
from .name_input_modal import NameInputModalDialog


class DialogType(Enum):
    NAME_INPUT = auto()


class ModalDialogFactory:
    @staticmethod
    def create_dialog(
        dialog_type: DialogType, parent: QWidget, **kwargs
    ) -> BaseModalDialog:
        match dialog_type:
            case DialogType.NAME_INPUT:
                return NameInputModalDialog(parent, prompt=kwargs["prompt"])
