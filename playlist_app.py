import sys
import sqlite3
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QListWidget, QSlider, QLabel
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QHBoxLayout

class PlaylistApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.playlist_list = QListWidget(self)

        self.load_button = QPushButton("Загрузить Плейлист", self)
        self.load_button.clicked.connect(self.load_playlist)

        self.album_cover_label = QLabel(self)
        self.album_cover_label.setFixedSize(300, 300)  # Устанавливаем размер
        self.album_cover_label.setAlignment(Qt.AlignCenter)

        self.play_button = QPushButton("Воспроизвести", self)
        self.play_button.clicked.connect(self.play_media)

        self.is_playing = False
        self.play_icon = QIcon('icons/play.png')
        self.pause_icon = QIcon('icons/pause.png')

        
        self.pause_resume_icon_label = QLabel(self)
        self.pause_resume_icon_label.setPixmap(QPixmap('icons/pause.png'))
        self.pause_resume_icon_label.setAlignment(Qt.AlignCenter)
        self.pause_resume_icon_label.mousePressEvent = self.toggle_pause_resume

        self.next_button = QLabel(self)
        next_icon = QPixmap('icons/next.png')
        self.next_button.setPixmap(next_icon)
        self.next_button.setAlignment(Qt.AlignCenter)
        self.next_button.mousePressEvent = self.play_next_song  # Привязываем обработчик события клика к функции play_next_song

        self.prev_button = QLabel(self)
        prev_icon = QPixmap('icons/last.png')
        self.prev_button.setPixmap(prev_icon)
        self.prev_button.setAlignment(Qt.AlignCenter)
        self.prev_button.mousePressEvent = self.play_previous_song  # Привязываем обработчик события клика к функции play_next_song

        self.volume_slider = QSlider(Qt.Vertical, self)
        self.seek_slider = QSlider(Qt.Horizontal, self)

        self.volume_slider.setObjectName("volume_slider")
        self.seek_slider.setObjectName("seek_slider")

       

        with open('styles.css', 'r') as file:
            self.setStyleSheet(file.read())
    
        self.current_time_label = QLabel("00:00", self)
        self.total_length_label = QLabel("00:00", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.playlist_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.album_cover_label)  # Добавляем QLabel с фото альбома

        # Создаём горизонтальный макет для размещения кнопок и обложки альбома
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.pause_resume_icon_label)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)  # Добавляем горизонтальный макет в вертикальный

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.current_time_label)
        slider_layout.addWidget(self.seek_slider)
        slider_layout.addWidget(self.total_length_label)
        slider_layout.addWidget(self.volume_slider)

        layout.addLayout(slider_layout)
        
        down_layout = QVBoxLayout()

        self.db_connection = sqlite3.connect("my_playlist.db")
        self.cursor = self.db_connection.cursor()

        self.is_playing = False
        self.media_player = QMediaPlayer(self)
        self.media_player.setVolume(50)

        self.media_timer = QTimer(self)
        self.media_timer.timeout.connect(self.update_seek_slider)

        self.current_song_index = 0
        self.media_player.durationChanged.connect(self.update_total_length)

        self.media_player.mediaStatusChanged.connect(self.handle_media_status_changed)  # Перенесено сюда

        self.volume_slider.valueChanged.connect(self.change_volume)

        self.seek_slider.sliderPressed.connect(self.seek_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.seek_slider_released)

        self.seek_slider.sliderMoved.connect(self.seek_media)

    def load_playlist(self):
        self.playlist_list.clear()
        try:
            self.cursor.execute("SELECT * FROM playlists")
            playlists = self.cursor.fetchall()
            for playlist in playlists:
                self.playlist_list.addItem(playlist[0])
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке плейлиста: {e}")

    def toggle_pause_resume(self, event):
        if self.is_playing:
            self.media_player.pause()
            self.pause_resume_icon_label.setPixmap(QPixmap('icons/play.png'))
        else:
            self.media_player.play()
            self.pause_resume_icon_label.setPixmap(QPixmap('icons/pause.png'))
        self.is_playing = not self.is_playing

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
                        if not self.is_playing:
                            # Останавливаем текущее воспроизведение и сбрасываем позицию
                            self.media_player.stop()
                            self.seek_slider.setValue(0)
                            self.playlist_list.clearSelection()
                            self.play_media_file(files[self.current_song_index])
                            self.is_playing = True
            except sqlite3.Error as e:
                print(f"Ошибка при загрузке плейлиста: {e}")

    def play_media_file(self, file_path):
        full_file_path = os.path.join(os.path.dirname(__file__), file_path)  # Получаем полный путь к файлу
        media_content = QMediaContent(QUrl.fromLocalFile(full_file_path))
        self.media_player.setMedia(media_content)

        self.update_seek_slider()  # Обновляем слайдер перемотки
        self.media_player.play()
        self.media_timer.start()

        # Здесь предполагается, что у трека есть поле image_path в базе данных
        self.cursor.execute("SELECT image_path FROM tracks WHERE file_path=?", (file_path,))
        track_image_path = self.cursor.fetchone()[0]

        pixmap = QPixmap(track_image_path)
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        self.album_cover_label.setPixmap(pixmap)
        self.album_cover_label.setFixedSize(300, 300)
        self.album_cover_label.setAlignment(Qt.AlignCenter)

        # Получаем информацию о текущем треке, включая путь к изображению
        selected_item = self.playlist_list.currentItem()
        if selected_item is not None:
            playlist_name = selected_item.text()
            try:
                self.cursor.execute("SELECT * FROM playlists WHERE name=?", (playlist_name,))
                playlist = self.cursor.fetchone()
                if playlist is not None:
                    files = playlist[1].split(", ")
                    current_track_file = files[self.current_song_index]

                    # Здесь предполагается, что у трека есть поле image_path в базе данных
                    self.cursor.execute("SELECT image_path FROM tracks WHERE file_path=?", (current_track_file,))
                    track_image_path = self.cursor.fetchone()[0]

                    # Устанавливаем изображение трека в QLabel
                    pixmap = QPixmap(track_image_path)
                    pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
                    self.album_cover_label.setPixmap(pixmap)
                    self.album_cover_label.setFixedSize(300, 300)

            except sqlite3.Error as e:
                print(f"Ошибка при загрузке информации о треке: {e}")

    def update_total_length(self, duration):
        if duration > 0:
            minutes, seconds = divmod(duration // 1000, 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.total_length_label.setText(time_str)  # Установите значение в QLabel

    def update_current_time(self, position):
        minutes, seconds = divmod(position / 1000, 60)
        time_str = f"{int(minutes):02d}:{int(seconds):02d}"
        self.current_time_label.setText(time_str)

    def next_song_clicked(self, event):
        self.play_next_song()

    def previous_song_clicked(self, event):
        self.play_previous_song()               

    def play_next_song(self, event=None):
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

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            # Текущий трек завершился, переключаемся на следующий
            self.play_next_song()            

    def play_previous_song(self, event=None):
        selected_item = self.playlist_list.currentItem()
        if selected_item is not None:
            playlist_name = selected_item.text()
            try:
                self.cursor.execute("SELECT * FROM playlists WHERE name=?", (playlist_name,))
                playlist = self.cursor.fetchone()
                if playlist is not None:
                    files = playlist[1].split(", ")
                    self.current_song_index = (self.current_song_index - 1) % len(files)

                    # Проверяем, стал ли индекс отрицательным
                    if self.current_song_index < 0:
                        self.current_song_index = len(files) - 1

                    self.play_media_file(files[self.current_song_index])
            except sqlite3.Error as e:
                print(f"Ошибка при загрузке плейлиста: {e}")
                      
    def seek_media(self):
        position = self.seek_slider.value()
        self.media_player.setPosition(position)

    def change_volume(self, value):
        self.media_player.setVolume(value)

    def seek_slider_pressed(self):
        self.media_timer.stop()

    def seek_slider_released(self):
        self.seek_media()
        self.media_timer.start()

    def update_seek_slider(self):
        if self.media_player.duration() > 0 and not self.seek_slider.isSliderDown() and self.media_player.state() == QMediaPlayer.PlayingState:
            duration = self.media_player.duration()
            position = self.media_player.position()
            self.seek_slider.setMaximum(duration)
            self.seek_slider.setValue(position)
            self.update_current_time(position)

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlaylistApp()
    window.show()
    sys.exit(app.exec_())