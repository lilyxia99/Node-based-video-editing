import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QWidget,QFileDialog
from canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canvas with Squares")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.canvas = Canvas()
        layout.addWidget(self.canvas)

        controls_layout = QHBoxLayout()

        add_button = QPushButton("+")
        add_button.clicked.connect(self.canvas.add_square)
        controls_layout.addWidget(add_button)

        self.sequence_dropdown = QComboBox()
        controls_layout.addWidget(self.sequence_dropdown)

        ## play sequence button
        play_button = QPushButton("Play Sequence")
        play_button.clicked.connect(self.play_selected_sequence)
        controls_layout.addWidget(play_button)
        
        ##Save and Load
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_canvas_state)
        controls_layout.addWidget(save_button)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_canvas_state)
        controls_layout.addWidget(load_button)
        
        #test connect square buttons
        connect_button = QPushButton("Connect Squares")
        connect_button.clicked.connect(lambda: self.canvas.connect_squares(1, 2))  # Connect square 1 and square 2
        controls_layout.addWidget(connect_button)

        #delete button
        delete_button = QPushButton("Delete Square")
        delete_button.clicked.connect(self.canvas.delete_square)
        controls_layout.addWidget(delete_button)

        layout.addLayout(controls_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Bind to sequence update
        self.canvas.sequence_info_updated.connect(self.update_sequences)

    def update_sequences(self):
        self.sequence_dropdown.clear()
        sequences = self.canvas.update_sequences()
        formatted_sequences = [" -> ".join(str(node) for node in sequence.split(" -> ")) for sequence in sequences]
        self.sequence_dropdown.addItems(formatted_sequences)


    def play_selected_sequence(self):
        sequence_name = self.sequence_dropdown.currentText()
        if sequence_name:
            self.canvas.play_sequence(sequence_name)
            
    def save_canvas_state(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Canvas", "", "JSON Files (*.json)")
        if file_path:
            self.canvas.save_canvas(file_path)

    def load_canvas_state(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Canvas", "", "JSON Files (*.json)")
        if file_path:
            self.canvas.load_canvas(file_path)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())