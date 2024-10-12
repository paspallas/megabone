from .keyframe import Keyframe


class AnimationTrack:
    def __init__(self, target, property_type):
        self.target = target  # Bone, IKHandle, or Sprite
        self.property_type = property_type
        self.keyframes = []  # List of Keyframe objects
        self.enabled = True

    def addKeyframe(self, frame, value, easing="linear"):
        """Add a keyframe at the specified frame"""
        # Remove existing keyframe at this frame if it exists
        self.keyframes = [k for k in self.keyframes if k.frame != frame]

        # Add new keyframe
        keyframe = Keyframe(frame, value, easing)
        self.keyframes.append(keyframe)
        # Sort keyframes by frame number
        self.keyframes.sort(key=lambda k: k.frame)

    def getValue(self, frame):
        """Get interpolated value at the specified frame"""
        if not self.keyframes:
            return None

        # Find surrounding keyframes
        prev_keyframe = None
        next_keyframe = None

        for keyframe in self.keyframes:
            if keyframe.frame <= frame:
                prev_keyframe = keyframe
            else:
                next_keyframe = keyframe
                break

        if not prev_keyframe:
            return self.keyframes[0].value
        if not next_keyframe:
            return prev_keyframe.value

        # Interpolate between keyframes
        t = (frame - prev_keyframe.frame) / (next_keyframe.frame - prev_keyframe.frame)
        return prev_keyframe.interpolate(next_keyframe, t)
