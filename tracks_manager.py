import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sqlite3

class SongViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Connect to the database
        conn = sqlite3.connect('my_playlist.db')
        cursor = conn.cursor()

        # Get data from tracks table
        cursor.execute('SELECT id, image_path, name_track, author, file_path FROM tracks')
        result = cursor.fetchall()

        # Create GUI
        self.setWindowTitle('Song Viewer')
        self.setGeometry(100, 100, 700, 400)
        self.setStyleSheet("background-color: black; color: white;") # set the background color to black and text color to white
        
        # Create grid container
        layout = QVBoxLayout()
        widget = QWidget(self)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: black; color: white;") # set the background color to black and text color of the container to white

        # a scroll area is introduced
        scroll_area = QScrollArea(self)
        self.setCentralWidget(scroll_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)
        scroll_area.setStyleSheet("background-color: white;") # change scroll area background color to white

        for i, row in enumerate(result):
            h_box = QHBoxLayout()
            
            song_id = QLabel(f'{row[0]}', self)
            song_id.setContentsMargins(0, 0, 10, 0)
            song_id.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            song_id.setFixedWidth(30)
            h_box.addWidget(song_id)

            image_path = row[1]
            image_label = QLabel(self)
            image_label.setContentsMargins(15, 0, 0, 0)
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
            h_box.addWidget(image_label)

            song_name = QLabel(f"{row[2]}", self)
            song_name.setStyleSheet("color: white;")  # set the text color to white
            song_name.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            song_author = QLabel(f"{row[3]}", self)
            song_author.setStyleSheet("color: white;") # set the text color to white
            song_author.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            v_box = QVBoxLayout() # Create QVBoxLayout to store song name and author vertically
            v_box.addWidget(song_name) 
            v_box.addWidget(song_author)

            h_box.addLayout(v_box)

            h_box.addStretch(1)
            layout.addLayout(h_box)

        # Close database connection
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SongViewer()
    window.show()
    sys.exit(app.exec_())