import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout


class AddToPlaylistApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Менеджер песен")
        self.setGeometry(100, 100, 400, 300)

        self.db_connection = sqlite3.connect("my_playlist.db")
        self.cursor = self.db_connection.cursor()

        # Добавляем кнопку создания плейлиста
        self.create_playlist_button = QPushButton("Создать плейлист", self)
        self.create_playlist_button.clicked.connect(self.create_playlist)

        # Создайте экземпляр QListWidget
        self.song_list = QListWidget(self)
        
        # Создайте layout для виджета, добавьте кнопку создания плейлиста и song_list
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_playlist_button)
        layout.addWidget(self.song_list)

        self.load_songs()

    def load_songs(self):
        try:
            self.cursor.execute("SELECT id, image_path, name_track, author, file_path FROM tracks")
            result = self.cursor.fetchall()

            for row in result:
                item = QListWidgetItem(self.song_list)
                widget = QWidget()
                layout_h = QHBoxLayout()  

                image_path = row[1]
                image_label = QLabel(self)
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio)
                image_label.setPixmap(pixmap)

                layout_v1 = QVBoxLayout()  
                layout_v1.addWidget(image_label)

                song_name = QLabel(f"{row[2]}", self)
                song_author = QLabel(f"{row[3]}", self)
                song_name.setAlignment(Qt.AlignLeft)
                song_author.setAlignment(Qt.AlignLeft)

                grid = QGridLayout()
                grid.addWidget(song_name, 0, 0, Qt.AlignLeft)
                grid.addWidget(song_author, 1, 0, Qt.AlignLeft)

                add_button = QPushButton("Add", self)
                add_button.setFixedSize(100, 40) 
                add_button.clicked.connect(lambda checked, file_path=row[4]: self.add_track_to_playlist(file_path))

                layout_h.addLayout(layout_v1)
                layout_h.addLayout(grid)
                layout_h.addWidget(add_button)
                
                widget.setLayout(layout_h)
                item.setSizeHint(widget.sizeHint())
                self.song_list.addItem(item)
                self.song_list.setItemWidget(item, widget)
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке песен: {e}")

    def create_playlist(self):
        playlist_name, ok = QInputDialog.getText(self, 'Создать плейлист', 'Введите имя плейлиста:')
        if ok:
            try:
                self.cursor.execute("INSERT INTO playlists (name) VALUES (?)", (playlist_name,))
            except sqlite3.Error as e:
                print(f"Ошибка при создании плейлиста: {e}")
            else:
                self.db_connection.commit()

    def add_track_to_playlist(self, track_path):
        self.cursor.execute("SELECT name, tracks FROM playlists")
        playlists_and_traks = self.cursor.fetchall()
        
        # Создаем два отдельных списка для имен плейлиста и треков
        playlists = [pl[0] for pl in playlists_and_traks]
        tracks = [pl[1].split(", ") if pl[1] is not None else [] for pl in playlists_and_traks]

        playlist_name, ok = QInputDialog.getItem(self, "Выберите плейлист", "Плейлисты", playlists, 0, False)
        if ok and playlist_name:
            # Получаем индекс выбранного плейлиста для получения его текущих треков
            playlist_index = playlists.index(playlist_name)
            if not track_path in tracks[playlist_index]:  # Если трека нет в плейлисте
                try:
                    # Добавляем трек в плейлист
                    new_tracks = tracks[playlist_index] + [track_path] if tracks[playlist_index] else [track_path]
                    self.cursor.execute("UPDATE playlists SET tracks=? WHERE name=?", (", ".join(new_tracks), playlist_name))
                    self.db_connection.commit()
                except sqlite3.Error as e:
                    print(f"Ошибка при добавлении песни в плейлист: {e}")
            else:
                print(f"Трек уже присутствует в этом плейлисте")

    def closeEvent(self, event):
        self.db_connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddToPlaylistApp()
    window.show()
    sys.exit(app.exec_())