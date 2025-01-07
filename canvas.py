from PyQt5.QtWidgets import QWidget, QFileDialog, QComboBox,QPushButton,QMenu
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt5.QtCore import QRect, Qt, QPointF, QPoint, pyqtSignal
from video_player import VideoPlayer
from sequence_player import SequencePlayer



class Canvas(QWidget):
    sequence_info_updated = pyqtSignal()  # Signal to notify when connections are updated

    def __init__(self):
        super().__init__()
        self.squares = []  # List to store the position of squares and their IDs
        self.dragging_square = None  # Currently dragged square
        self.drag_offset = QPoint()
        self.dragging_dot = None  # Currently dragging a dot
        self.connections = []  # List of connections between dots
        self.temp_line = None  # Temporary line while dragging
        self.selected_square = None  # Currently selected square
        self.square_files = {}  # Mapping of square IDs to file paths
        self.video_player = VideoPlayer()
        self.sequence_names = {}  # Map sequence names to video paths
        self.setMouseTracking(True)
        self.sequence_player = SequencePlayer()
        self.setFocusPolicy(Qt.StrongFocus)


    def add_square(self):
        size = 50  # Size of the square
        padding = 10  # Padding between squares
        x = len(self.squares) * (size + padding) + padding
        y = padding
        square_id = len(self.squares) + 1  # Unique ID for the square
        self.squares.append([x, y, size, square_id])  # Store as mutable list for updates
        self.update()  # Trigger a repaint

    def play_sequence(self, sequence_name):
        if sequence_name not in self.sequence_names:
            print(f"Sequence {sequence_name} not found!")
            return

        # Collect video file paths
        video_paths = [
            path for _, path in self.sequence_names[sequence_name].items() if path
        ]
        print(f"Playing video paths: {video_paths}")  # Debug here
        if not video_paths:
            print("No videos to play in the sequence.")
            return

        self.sequence_player.play_sequence(video_paths)
        self.sequence_player.show()
        # Play the sequence using the video player
        #self.video_player.play_sequence(video_paths)
        #self.video_player.show()



    def update_sequences(self):
        self.sequence_names = {}
        print(f"Square files: {self.square_files}")
        for route in self.generate_routes():
            sequence_name = f"Sequence {len(self.sequence_names) + 1}"
            self.sequence_names[sequence_name] = {
                int(node): self.square_files.get(int(node), None) for node in route.split(" -> ")
            }
            print(f"Updated sequence {sequence_name}: {self.sequence_names[sequence_name]}")
        return list(self.sequence_names.keys())





    def generate_routes(self):
        routes = []
        graph = {square[3]: [] for square in self.squares}
        for start_square, end_square in self.connections:
            start_id = start_square[3]
            end_id = end_square[3]
            graph[start_id].append(end_id)

        def dfs(node, path):
            if not graph[node]:
                routes.append(" -> ".join(map(str, path)))
                return
            for neighbor in graph[node]:
                dfs(neighbor, path + [neighbor])

        visited = set()
        for square in self.squares:
            square_id = square[3]
            if square_id not in visited:
                dfs(square_id, [square_id])
                visited.add(square_id)

        final_routes = []
        for route in routes:
            if not any(route != r and route in r for r in routes):
                final_routes.append(route)
                
        #print("Generated routes:", final_routes)

        return final_routes

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw connections
        painter.setPen(QPen(QColor("white"), 2))
        for conn in self.connections:
            start_square, end_square = conn
            start_x, start_y, size, _ = start_square
            end_x, end_y, size, _ = end_square
            start_dot = QPointF(start_x + size, start_y)
            end_dot = QPointF(end_x + size, end_y)
            painter.drawLine(start_dot, end_dot)
            self.draw_arrow(painter, start_dot, end_dot)

        # Draw the temporary line if dragging
        if self.temp_line:
            painter.setPen(QPen(QColor("white"), 2, Qt.DashLine))
            painter.drawLine(self.temp_line[0], self.temp_line[1])

        # Draw squares and dots
        for square in self.squares:
            x, y, size, square_id = square
            painter.setBrush(QColor("pink") if square == self.selected_square else QColor("lightblue"))
            painter.setPen(QPen(QColor("black"), 2))
            painter.drawRect(QRect(x, y, size, size))

            dot_size = 10
            dot_x = x + size - dot_size // 2
            dot_y = y - dot_size // 2
            painter.setBrush(QColor("red"))
            painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
            painter.setPen(QPen(QColor("black"), 1))
            painter.drawText(QRect(x, y, size, size), Qt.AlignCenter, str(square_id))

        # Display the file name and path for the selected square
        if self.selected_square:
            square_id = self.selected_square[3]
            if square_id in self.square_files:
                file_path = self.square_files[square_id]
                file_name = file_path.split('/')[-1]
                painter.setPen(QPen(QColor("white"), 1))
                painter.drawText(self.width() // 2 - 150, self.height() // 2 - 20, f"File: {file_name}")
                painter.drawText(self.width() // 2 - 150, self.height() // 2, f"Path: {file_path}")

        # Display connection sequences
        painter.setPen(QPen(QColor("white"), 1))
        y_offset = self.height() - 20
        for idx, route in enumerate(self.generate_routes()):
            painter.drawText(10, y_offset - idx * 20, route)

    def draw_arrow(self, painter, start, end):
        arrow_size = 10
        line_vector = end - start
        length = (line_vector.x() ** 2 + line_vector.y() ** 2) ** 0.5
        if length == 0:
            return
        unit_vector = QPointF(line_vector.x() / length, line_vector.y() / length)
        perp_vector = QPointF(-unit_vector.y(), unit_vector.x())
        arrow_point1 = end - arrow_size * unit_vector + arrow_size * perp_vector
        arrow_point2 = end - arrow_size * unit_vector - arrow_size * perp_vector
        polygon = QPolygonF([end, arrow_point1, arrow_point2])
        painter.setBrush(QColor("white"))
        painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        """print("Dot clicked, starting drag")"""
        for square in self.squares:
            x, y, size, square_id = square
            dot_size = 10
            dot_x = x + size - dot_size // 2
            dot_y = y - dot_size // 2
            dot_rect = QRect(dot_x, dot_y, dot_size, dot_size)
            if dot_rect.contains(event.pos()):
                self.dragging_dot = (square, QPointF(dot_x + dot_size // 2, dot_y + dot_size // 2))
                self.temp_line = (self.dragging_dot[1], event.pos())
                return

        for square in self.squares:
            x, y, size, square_id = square
            if QRect(x, y, size, size).contains(event.pos()):
                self.dragging_square = square
                self.selected_square = square
                self.drag_offset = event.pos() - QPoint(x, y)
                self.update()
                return

        self.selected_square = None
        self.update()

## Mouse Events--------------------------

    def mouseReleaseEvent(self, event):
        event.accept()  # Explicitly accept the event
        super().mouseReleaseEvent(event)  # Call the parent class implementation
        """print("mouseReleaseEvent triggered")"""

        if self.dragging_square:
            self.dragging_square = None

        if self.dragging_dot:
            start_square, start_dot = self.dragging_dot
            for square in self.squares:
                x, y, size, square_id = square
                dot_size = 10
                dot_x = x + size - dot_size // 2
                dot_y = y - dot_size // 2
                dot_rect = QRect(dot_x, dot_y, dot_size, dot_size)

                if dot_rect.contains(event.pos()):  # Check if the mouse release is on a dot
                    print(f"Connecting {start_square} to {square}")
                    self.connections.append((start_square, square))  # Add the connection
                    self.sequence_info_updated.emit()  # Update sequence info
                    break

            self.dragging_dot = None
            self.temp_line = None
            self.update()

    def mouseDoubleClickEvent(self, event):
        for square in self.squares:
            x, y, size, square_id = square
            if QRect(x, y, size, size).contains(event.pos()):
                if square_id in self.square_files:
                    # Reset and show the video player
                    file_path = self.square_files[square_id]
                    print(f"File path for square {square_id}: {file_path}")
                    self.video_player.media_player.stop()  # Ensure previous playback is stopped
                    self.video_player.play_video(file_path)
                    self.video_player.show()
                else:
                    # Prompt to select a video file
                    file_path, _ = QFileDialog.getOpenFileName(self, "Select MP4 File", "", "MP4 Files (*.mp4)")
                    if file_path:
                        self.square_files[square_id] = file_path
                        print(f"Assigned file path for square {square_id}: {file_path}")
                        self.sequence_info_updated.emit()  # Trigger sequence update
                self.update()
                return


    def mouseMoveEvent(self, event):
        if self.dragging_square:
            new_pos = event.pos() - self.drag_offset
            self.dragging_square[0] = new_pos.x()
            self.dragging_square[1] = new_pos.y()
            self.update()

        if self.dragging_dot:
            self.temp_line = (self.dragging_dot[1], event.pos())
            self.update()
            
    # short cut
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_square()
            
    # right click menu----
            
    def contextMenuEvent(self, event):
        # Check if right-click is within a square
        for square in self.squares:
            x, y, size, square_id = square
            if QRect(x, y, size, size).contains(event.pos()):  # Check if the right-click is inside this square
                self.selected_square = square  # Automatically select this square
                self.update()  # Update canvas to reflect the selection visually
                
                # Show the context menu
                context_menu = QMenu(self)
                upload_action = context_menu.addAction("Upload/Replace Video")
                action = context_menu.exec_(self.mapToGlobal(event.pos()))
                
                if action == upload_action:
                    self.upload_or_replace_video()  # Handle video upload/replacement
                #防止鼠标粘连
                self.dragging_square = None
                return  # Exit after handling the menu

    def upload_or_replace_video(self):
        square_id = self.selected_square[3]

        # If the square already has a video, prompt to replace
        if square_id in self.square_files:
            print(f"Replacing video for square {square_id}.")
        
        # Prompt for video file upload
        file_path, _ = QFileDialog.getOpenFileName(self, "Select MP4 File", "", "MP4 Files (*.mp4)")
        if file_path:
            self.square_files[square_id] = file_path
            print(f"Assigned/replaced file for square {square_id}: {file_path}")
            self.update_sequences()  # Update sequences to reflect the new video
            self.update()  # Refresh the canvas
            
# Save and Load---------------------------

    def save_canvas(self, file_path):
        import json
        data = {
            "squares": self.squares,  # List of squares and their positions
            "square_files": {int(k): v for k, v in self.square_files.items()},  # Ensure keys are integerspaths
            "connections": [
            (start[3], end[3]) for start, end in self.connections],  # Save only square IDs
        }
        with open(file_path, 'w') as file:
            json.dump(data, file)
        print("Canvas saved to", file_path)


    def load_canvas(self, file_path):
        import json
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Restore squares and file associations
        self.squares = data.get("squares", [])
        self.square_files = {int(k): v for k, v in data.get("square_files", {}).items()}
        connections_data = data.get("connections", [])

        # Clear previous state
        self.connections = []
        self.selected_square = None
        self.dragging_square = None
        self.dragging_dot = None
        self.temp_line = None

        # Restore connections
        for start_id, end_id in connections_data:
            self.connect_squares(start_id, end_id)

        # Update canvas and sequences
        self.update_sequences()
        self.update()
        self.sequence_info_updated.emit()

        print("Canvas loaded from", file_path)



    def connect_squares(self, square_id_1, square_id_2):
        """
        Automatically create a connection between two squares based on their IDs.
        """
        square_1 = next((square for square in self.squares if square[3] == square_id_1), None)
        square_2 = next((square for square in self.squares if square[3] == square_id_2), None)

        if not square_1 or not square_2:
            print(f"Cannot connect: One or both square IDs {square_id_1}, {square_id_2} do not exist.")
            return

        # Add the connection to self.connections
        self.connections.append((square_1, square_2))
        print(f"Connected square {square_id_1} to square {square_id_2}.")

        # Update sequences and refresh the canvas
        self.update_sequences()
        self.update()
        
    def delete_square(self):
            """
            Delete the currently selected square and its associated connections and files.
            """
            if not self.selected_square:
                print("No square selected to delete.")
                return

            square_id = self.selected_square[3]

            # Remove the square
            self.squares = [square for square in self.squares if square[3] != square_id]

            # Remove associated connections
            self.connections = [
                conn for conn in self.connections
                if conn[0][3] != square_id and conn[1][3] != square_id
            ]

            # Remove associated file
            if square_id in self.square_files:
                del self.square_files[square_id]

            # Clear selection
            self.selected_square = None

            # Update sequences and refresh the canvas
            self.update_sequences()
            self.update()
            print(f"Deleted square {square_id} and updated connections and sequences.")
            
