try:
    from PyQt6.QtCore import *
except ImportError:
    from PySide6.QtCore import *

try:
    from PyQt6.QtCore import pyqtSignal as Signal
except ImportError:
    from PySide6.QtCore import Signal

try:
    from PyQt6.QtCore import pyqtSlot as Slot
except ImportError:
    from PySide6.QtCore import Slot
