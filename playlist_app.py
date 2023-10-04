import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QListWidget, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt

class PlaylistApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZXCmusic")
        self.setGeometry(100, 100, 400, 300)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.playlist_list = QListWidget(self)
        
        self.load_button = QPushButton("Загрузить Плейлист", self)
        self.load_button.clicked.connect(self.load_playlist)
        
        self.play_button = QPushButton("Воспроизвести", self)
        self.play_button.clicked.connect(self.play_media)
        
        self.pause_resume_button = QPushButton("Пауза", self)
        self.pause_resume_button.clicked.connect(self.toggle_pause_resume)
        
        self.next_button = QPushButton("Следующая", self)
        self.next_button.clicked.connect(self.play_next_song)
        
        self.prev_button = QPushButton("Предыдущая", self)
        self.prev_button.clicked.connect(self.play_previous_song)
        
        self.volume_slider = QSlider(self)
        self.volume_slider.setOrientation(Qt.Horizontal)
        
        self.seek_slider = QSlider(Qt.Horizontal, self)
        self.seek_slider.valueChanged.connect(self.seek_media)
        
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.playlist_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_resume_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.seek_slider)
        
        self.db_connection = sqlite3.connect("my_playlist.db")
        self.cursor = self.db_connection.cursor()
        
        self.current_media_player = QMediaPlayer()
        self.current_media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.current_media_player.positionChanged.connect(self.update_seek_slider)
        self.current_media_player.durationChanged.connect(self.setup_seek_slider)
        
        self.current_song_index = 0
    
        self.volume_slider.valueChanged.connect(self.change_volume)
    
    def load_playlist(self):
        self.playlist_list.clear()
        try:
            self.cursor.execute("SELECT * FROM playlists")
            playlists = self.cursor.fetchall()
            for playlist in playlists:
                self.playlist_list.addItem(playlist[0])
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке плейлиста: {e}")

    def toggle_pause_resume(self):
        if self.current_media_player.state() == QMediaPlayer.PlayingState:
            self.current_media_player.pause()
            self.pause_resume_button.setText("Продолжить")
        else:
            self.current_media_player.play()
            self.pause_resume_button.setText("Пауза")

    def play_media(self):
        selected_item = self.playlist_list.currentItem()
        if selected_item is not None:
            playlist_name = selected_item.text()
            try:
                self.cursor.execute("SELECT * FROM playlists WHERE name=?", (playlist_name,))
                playlist = self.cursor.fetchone()
                if playlist is not None:
                    files = playlist[1].split(", ")
                    if files:
                        self.play_media_file(files[self.current_song_index])
            except sqlite3.Error as e:
                print(f"Ошибка при загрузке плейлиста: {e}")

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_song()

    def play_media_file(self, file_path):
        media_content = QMediaContent(QUrl.fromLocalFile(file_path))
        self.current_media_player.setMedia(media_content)
        self.current_media_player.play()
        self.seek_slider.setValue(0)

    def play_next_song(self):
        selected_item = self.playlist_list.currentItem()
        if selected_item is not None:
            playlist_name = selected_item.text()
            try:
                self.cursor.execute("SELECT * FROM playlists WHERE name=?", (playlist_name,))
                playlist = self.cursor.fetchone()
                if playlist is not None:
                    files = playlist[1].split(", ")
                    self.current_song_index = (self.current_song_index + 1) % len(files)
                    self.play_media_file(files[self.current_song_index])
            except sqlite3.Error as e:
                print(f"Ошибка при загрузке плейлиста: {e}")

    def setup_seek_slider(self, duration):
        self.seek_slider.setMaximum(duration)
        self.seek_slider.setValue(0)
    
    def update_seek_slider(self, position):
        self.seek_slider.setValue(position)            

    def seek_media(self, position):
        self.current_media_player.setPosition(position)

    def play_previous_song(self):
        selected_item = self.playlist_list.currentItem()
        if selected_item is not None:
            playlist_name = selected_item.text()
            try:
                self.cursor.execute("SELECT * FROM playlists WHERE name=?", (playlist_name,))
                playlist = self.cursor.fetchone()
                if playlist is not None:
                    files = playlist[1].split(", ")
                    self.current_song_index = (self.current_song_index - 1) % len(files)
                    self.play_media_file(files[self.current_song_index])
            except sqlite3.Error as e:
                print(f"Ошибка при загрузке плейлиста: {e}")

    def change_volume(self, value):
        self.current_media_player.setVolume(value)

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlaylistApp()
    window.show()
    sys.exit(app.exec_())