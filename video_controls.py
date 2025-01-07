from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt

class VideoControls:
    def __init__(self, media_player):
        """
        Initialize the video controls.

        Args:
            media_player (QMediaPlayer): The media player object to control.
        """
        self.media_player = media_player

    def create_controls(self):
        """
        Create a play/pause button and a progress bar for video control.

        Returns:
            QVBoxLayout: A vertical layout containing the button and progress bar.
        """
        controls_layout = QVBoxLayout()

        # Play/Pause button
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_pause_button)

        # Progress bar
        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.setRange(0, 0)  # Initial range; updated dynamically
        self.progress_bar.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.progress_bar)

        # Connect media player signals to update progress bar
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)

        return controls_layout

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.media_player.state() == self.media_player.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")

    def update_position(self, position):
        """Update the progress bar position."""
        self.progress_bar.setValue(position)

    def update_duration(self, duration):
        """Update the progress bar range based on the video duration."""
        self.progress_bar.setRange(0, duration)

    def set_position(self, position):
        """Set the media player's position based on the slider."""
        self.media_player.setPosition(position)
