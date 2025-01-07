from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel,QFileDialog,QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from moviepy.editor import VideoFileClip, concatenate_videoclips
from video_controls import VideoControls
import os



class SequencePlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Player")
        self.setGeometry(200, 200, 800, 600)

        # Video player components
        self.video_widget = QVideoWidget(self)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Controls and info
        self.info_label = QLabel("Playing sequence...")
        layout = QVBoxLayout()
        
        # VideoControls for play/pause button and progress bar
        self.video_controls = VideoControls(self.media_player)

        # Next and export buttons
        self.next_button = QPushButton("Next Video")
        self.next_button.clicked.connect(self.play_next_video)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.info_label)
        
        self.export_button = QPushButton("Export Video")
        self.export_button.clicked.connect(self.export_sequence)
        layout.addWidget(self.export_button)
        
        # Export to EDL Button
        self.export_del_button = QPushButton("Export to EDL")
        self.export_del_button.clicked.connect(self.export_to_edl)
        layout.addWidget(self.export_del_button)
        
        
        
        # Add video controls (play/pause button and progress bar)
        controls_layout = self.video_controls.create_controls()
        layout.addLayout(controls_layout)
        
        # Add other buttons
        layout.addWidget(self.next_button)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

        # Video sequence
        self.video_paths = []
        self.current_index = 0

        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)




    def play_sequence(self, video_paths):
        """Initialize and play a sequence of videos."""
        self.video_paths = video_paths
        self.current_index = 0
        if self.video_paths:
            self.play_next_video()

    def play_next_video(self):
        """Play the next video in the sequence."""
        if self.current_index < len(self.video_paths):
            video_path = self.video_paths[self.current_index]
            self.current_index += 1
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.info_label.setText(f"Playing: {video_path}")
            self.media_player.play()

            # Update the play/pause button state in VideoControls
            self.video_controls.play_pause_button.setText("Pause")
        else:
            self.info_label.setText("Sequence finished!")
            self.media_player.stop()

            # Reset the play/pause button state
            self.video_controls.play_pause_button.setText("Play")


    def toggle_play_pause(self):
        """Toggle play/pause state."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")

    def handle_media_status(self, status):
        """Handle end of media to play the next video."""
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_video()
            
    def closeEvent(self, event):
        """Handle window close event by hiding the window."""
        self.media_player.pause()  # Pause playback instead of stopping it
        self.hide()  # Hide the window instead of closing it
        event.ignore()  # Prevent the window from being destroyed
        
    def export_sequence(self):
        """Export the sequence of videos into a single video."""
        if not self.video_paths:
            self.info_label.setText("No videos to export.")
            return

        try:
            # Load video clips
            clips = [VideoFileClip(path) for path in self.video_paths]

            # Resize all clips to the size of the first clip
            first_clip_size = clips[0].size
            resized_clips = [clip.resize(newsize=first_clip_size) for clip in clips]

            # Concatenate clips
            final_clip = concatenate_videoclips(resized_clips, method="compose")

            # Save the final video
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Exported Video", "", "MP4 Files (*.mp4)")
            if save_path:
                final_clip.write_videofile(save_path, codec="libx264", audio_codec="aac")
                self.info_label.setText(f"Video exported to {save_path}")
            else:
                self.info_label.setText("Export canceled.")

        except Exception as e:
            self.info_label.setText(f"Error exporting video: {str(e)}")
            
    def export_to_edl(self):
        """
        Export the sequence of videos to an EDL (Edit Decision List) format.
        """
        if not self.video_paths:
            QMessageBox.critical(self, "Error", "No videos loaded to export.")
            return

        # Generate EDL content
        edl_content = "TITLE: Exported Sequence\nFCM: NON-DROP FRAME\n"
        current_timecode = 0

        for i, video_path in enumerate(self.video_paths):
            clip = VideoFileClip(video_path)
            duration = clip.duration  # Duration in seconds

            # Normalize and format file paths
            normalized_path = os.path.abspath(video_path).replace("\\", "/")
            clip_name = os.path.basename(video_path).replace(" ", "_")

            edl_content += (
                f"\n{str(i + 1).zfill(3)}  AX       V     C        "
                f"{self.format_timecode(current_timecode)} {self.format_timecode(current_timecode + duration)} "
                f"{self.format_timecode(current_timecode)} {self.format_timecode(current_timecode + duration)}\n"
                f"* FROM CLIP NAME: {clip_name}\n"
                f"* MEDIA FILE: {normalized_path}\n"
            )
            current_timecode += duration

        # Save EDL to file
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save EDL", "", "EDL Files (*.edl);;All Files (*)", options=options)

        if save_path:
            with open(save_path, 'w') as edl_file:
                edl_file.write(edl_content)

            QMessageBox.information(self, "Success", f"EDL exported to: {save_path}")



    def format_timecode(self, seconds):
        """
        Convert seconds to EDL timecode format (HH:MM:SS:FF).

        Args:
            seconds (float): Time in seconds.

        Returns:
            str: Timecode in HH:MM:SS:FF format.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds - int(seconds)) * 24)  # Assuming 24 fps
        return f"{hours:02}:{minutes:02}:{secs:02}:{frames:02}"