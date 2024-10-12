from PyQt5.QtCore import QPointF


class Keyframe:
    def __init__(self, frame, value, easing="linear"):
        self.frame = frame
        self.value = value  # Can be QPointF, float, etc.
        self.easing = easing

    def interpolate(self, other_keyframe, t):
        """Interpolate between this keyframe and another"""
        if isinstance(self.value, QPointF):
            return QPointF(
                self._ease(self.value.x(), other_keyframe.value.x(), t),
                self._ease(self.value.y(), other_keyframe.value.y(), t),
            )
        elif isinstance(self.value, (int, float)):
            return self._ease(self.value, other_keyframe.value, t)

    def _ease(self, start, end, t):
        """Apply easing function"""
        if self.easing == "linear":
            return start + (end - start) * t
        elif self.easing == "ease_in":
            return start + (end - start) * (t * t)
        elif self.easing == "ease_out":
            return start + (end - start) * (1 - (1 - t) * (1 - t))
        # Add more easing functions as needed
