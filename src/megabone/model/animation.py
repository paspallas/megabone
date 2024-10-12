from .animation_track import AnimationTrack
from .property import PropertyType


class Animation:
    def __init__(self, name):
        self.name = name
        self.tracks = []  # List of AnimationTrack objects
        self.frame_start = 0
        self.frame_end = 100
        self.current_frame = 0

    def addTrack(self, target, property_type):
        track = AnimationTrack(target, property_type)
        self.tracks.append(track)
        return track

    def update(self, frame):
        """Update all targets to specified frame"""
        self.current_frame = frame

        for track in self.tracks:
            if not track.enabled:
                continue

            value = track.getValue(frame)
            if value is None:
                continue

            # Apply value based on property type
            if track.property_type == PropertyType.POSITION:
                track.target.setPos(value)
            elif track.property_type == PropertyType.ROTATION:
                track.target.setRotation(value)
            elif track.property_type == PropertyType.IK_TARGET:
                track.target.target.setPos(value)
                track.target.chain.solve(value)
            elif track.property_type == PropertyType.IK_POLE:
                track.target.pole.setPos(value)
                track.target.pole.updateChainWithPoleVector()
            elif track.property_type == PropertyType.SPRITE_OFFSET:
                track.target.bone_offset = value
                # Update sprite position
                bone = track.target.attached_bone
                if bone:
                    new_pos = bone.end_point + value
                    track.target.setPos(new_pos)
