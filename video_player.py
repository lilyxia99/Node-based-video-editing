from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        # Video widget
        self.video_widget = QVideoWidget(self)

        # Media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Play/Pause Button
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderPressed.connect(self.pause_slider_updates)
        self.slider.sliderReleased.connect(self.resume_slider_updates)
        self.slider.sliderMoved.connect(self.set_position)

        # Labels for video info
        self.file_label = QLabel("No video selected")
        self.current_time_label = QLabel("0:00")
        self.total_time_label = QLabel("0:00")

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

        # Layout
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.video_widget)
        controls_layout.addWidget(self.file_label)

        control_bar_layout = QVBoxLayout()
        control_bar_layout.addWidget(self.play_pause_button)
        control_bar_layout.addWidget(self.slider)
        control_bar_layout.addWidget(self.current_time_label)
        control_bar_layout.addWidget(self.total_time_label)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(control_bar_layout)
        self.setLayout(main_layout)

        self.slider_updates_paused = False
        self.video_queue = []  # List to store queued video paths
        self.current_video_index = 0  # Track the current video in the queue

        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

    def play_sequence(self, file_paths):
        """Play a sequence of videos."""
        self.video_queue = file_paths
        self.current_video_index = 0
        if self.video_queue:
            self.play_next_video()

    def play_next_video(self):
        """Play the next video in the queue."""
        if self.current_video_index < len(self.video_queue):
            file_path = self.video_queue[self.current_video_index]
            self.current_video_index += 1
            self.play_video(file_path)
        else:
            self.close()  # Close the player when all videos are played

    def handle_media_status(self, status):
        """Handle media player status to play the next video."""
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_video()

    def play_video(self, file_path):
        """Play the selected video file."""
        self.reset_player()  # Reset media player and video widget
        self.file_label.setText(f"Playing: {file_path}")
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.media_player.play()
        self.play_pause_button.setText("Pause")
        self.show()  # Ensure the video player window is visible

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")

    def set_position(self, position):
        """Set the media position."""
        self.media_player.setPosition(position)

    def update_duration(self, duration):
        """Update the slider range based on the video duration."""
        self.slider.setRange(0, duration)
        self.total_time_label.setText(self.format_time(duration))

    def update_position(self, position):
        """Update the slider and current time label."""
        if not self.slider_updates_paused:
            self.slider.setValue(position)
        self.current_time_label.setText(self.format_time(position))

    def pause_slider_updates(self):
        """Pause slider updates while the user is dragging."""
        self.slider_updates_paused = True

    def resume_slider_updates(self):
        """Resume slider updates after the user finishes dragging."""
        self.slider_updates_paused = False
        self.set_position(self.slider.value())

    def reset_player(self):
        """Reset the media player and video widget."""
        self.media_player.stop()
        self.media_player.setVideoOutput(None)  # Detach the video output
        self.media_player.setVideoOutput(self.video_widget)  # Reattach the video output
        self.video_widget.update()  # Refresh the video widget

    @staticmethod
    def format_time(ms):
        """Format milliseconds to mm:ss."""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes}:{seconds:02}"

    def closeEvent(self, event):
        """Handle video player window close."""
        self.media_player.pause()  # Pause playback instead of stopping it
        self.hide()  # Hide the video player window instead of fully closing it
        event.ignore()  # Prevent the window from being destroyed
