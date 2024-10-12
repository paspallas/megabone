from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QTreeWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QTreeWidgetItem,
    QVBoxLayout,
)


class AnimationPlayer(QWidget):
    frameChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = {}  # Dictionary of Animation objects
        self.current_animation = None
        self.playing = False
        self.frame_rate = 24

        self.setupUI()

        # Setup playback timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)

    def setupUI(self):
        layout = QVBoxLayout()

        # Animation controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.togglePlay)

        self.frame_spinbox = QSpinBox()
        self.frame_spinbox.valueChanged.connect(self.setFrame)

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(QLabel("Frame:"))
        controls_layout.addWidget(self.frame_spinbox)

        # Animation tracks tree
        self.tracks_tree = QTreeWidget()
        self.tracks_tree.setHeaderLabels(["Track", "Target", "Property"])

        layout.addLayout(controls_layout)
        layout.addWidget(self.tracks_tree)

        self.setLayout(layout)

    def createAnimation(self, name):
        animation = Animation(name)
        self.animations[name] = animation
        return animation

    def setAnimation(self, name):
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.updateUI()

    def togglePlay(self):
        self.playing = not self.playing

        if self.playing:
            self.play_button.setText("Stop")
            self.timer.start(1000 // self.frame_rate)
        else:
            self.play_button.setText("Play")
            self.timer.stop()

    def updateFrame(self):
        if not self.current_animation:
            return

        frame = self.current_animation.current_frame + 1
        if frame > self.current_animation.frame_end:
            frame = self.current_animation.frame_start

        self.setFrame(frame)

    def setFrame(self, frame):
        if not self.current_animation:
            return

        self.current_animation.update(frame)
        self.frame_spinbox.setValue(frame)
        self.frameChanged.emit(frame)

    def updateUI(self):
        if not self.current_animation:
            return

        self.tracks_tree.clear()

        for track in self.current_animation.tracks:
            item = QTreeWidgetItem()
            item.setText(0, f"Track {len(self.tracks_tree.topLevelItems())}")
            item.setText(1, track.target.__class__.__name__)
            item.setText(2, track.property_type.value)

            # Add keyframe children
            for keyframe in track.keyframes:
                kf_item = QTreeWidgetItem()
                kf_item.setText(0, f"Frame {keyframe.frame}")
                kf_item.setText(1, str(keyframe.value))
                kf_item.setText(2, keyframe.easing)
                item.addChild(kf_item)

            self.tracks_tree.addTopLevelItem(item)
