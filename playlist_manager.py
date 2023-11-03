import sys
import sqlite3
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QFileDialog, QInputDialog

class PlaylistManagerApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Менеджер плейлистов")
        self.setGeometry(100, 100, 400, 300)

        self.db_connection = sqlite3.connect("my_playlist.db")
        self.cursor = self.db_connection.cursor()

        self.playlist_list = QListWidget(self)
        self.playlist_list.itemClicked.connect(self.load_playlist)

        self.create_button = QPushButton("Создать Плейлист", self)
        self.create_button.clicked.connect(self.create_playlist)

        self.track_list = QListWidget(self)

        self.add_track_button = QPushButton("Добавить трек в плейлист", self)
        self.add_track_button.clicked.connect(self.add_track_to_playlist)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_list)
        layout.addWidget(self.create_button)
        layout.addWidget(self.track_list)
        layout.addWidget(self.add_track_button)
        self.setLayout(layout)

        self.load_playlists()

    def load_playlists(self):
        self.playlist_list.clear()
        try:
            self.cursor.execute("SELECT name FROM playlists")
            playlists = self.cursor.fetchall()
            for playlist in playlists:
                self.playlist_list.addItem(playlist[0])
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке плейлистов: {e}")

    def create_playlist(self):
        playlist_name, ok = self.get_playlist_name()
        if ok and playlist_name:
            try:
                # Создаем запись в таблице playlists
                self.cursor.execute("INSERT INTO playlists (name, tracks) VALUES (?, ?)", (playlist_name, ""))
                
                # Создаем запись в таблице tracks
                self.cursor.execute("INSERT INTO tracks (file_path, image_path, playlist_name) VALUES (?, ?, ?)",
                                    ("", "", playlist_name))
                
                self.db_connection.commit()
                self.load_playlists()
            except sqlite3.Error as e:
                print(f"Ошибка при создании плейлиста: {e}")

    def get_playlist_name(self):
        name, ok = QInputDialog.getText(self, "Введите название плейлиста", "Название плейлиста:")
        return name, ok

    def load_playlist(self, item):
        self.current_playlist = item.text()
        self.load_tracks()

    def load_tracks(self):
        self.track_list.clear()
        try:
            self.cursor.execute("SELECT tracks FROM playlists WHERE name=?", (self.current_playlist,))
            playlist = self.cursor.fetchone()
            if playlist:
                tracks = playlist[0].split(", ")
                for track in tracks:
                    self.track_list.addItem(track)
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке треков плейлиста: {e}")

    def add_track_to_playlist(self):
        track_path, _ = QFileDialog.getOpenFileName(self, "Выберите трек", "", "Audio Files (*.mp3 *.wav);;All Files (*)")
        if track_path:
            self.track_list.addItem(track_path)
            self.save_tracks()

    def save_tracks(self):
        tracks = [self.track_list.item(i).text() for i in range(self.track_list.count())]
        tracks_str = ", ".join(tracks)
        try:
            # Обновляем запись в таблице playlists
            self.cursor.execute("UPDATE playlists SET tracks=? WHERE name=?", (tracks_str, self.current_playlist))
            
            # Обновляем запись в таблице tracks
            self.cursor.execute("UPDATE tracks SET file_path=? WHERE id=?", (tracks_str, self.current_playlist))
            
            self.db_connection.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении треков плейлиста: {e}")

    def closeEvent(self, event):
        self.db_connection.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlaylistManagerApp()
    window.show()
    sys.exit(app.exec_())