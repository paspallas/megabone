try:
    from PySide6.QtCore import *
except ImportError:
    from PyQt6.QtCore import *

try:
    from PySide6.QtCore import Signal
except ImportError:
    from PyQt6.QtCore import pyqtSignal as Signal

try:
    from PySide6.QtCore import Slot
except ImportError:
    from PyQt6.QtCore import pyqtSlot as Slot
