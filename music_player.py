import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QObject, pyqtSlot

class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 400, 200)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play_music)
        
        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.play_next_song)
        
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.play_previous_song)
        
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.play_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        
        self.media_player = QMediaPlayer()
        self.playlist = []  # Создаем пустой плейлист
        self.current_song_index = 0

    @pyqtSlot(list)  # Добавляем декоратор для принятия сигнала с плейлистом
    def receive_playlist(self, playlist):
        self.playlist = playlist
        self.current_song_index = 0
        self.play_song(self.current_song_index)
    
    def play_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            if self.media_player.state() == QMediaPlayer.PausedState:
                self.media_player.play()
            else:
                self.play_song(self.current_song_index)
            self.play_button.setText("Pause")
    
    def play_next_song(self):
        if self.playlist:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.stop()  # Остановить текущий трек
                self.media_player.stateChanged.connect(self.start_next_song)  # Подключаем слот для начала следующей песни
            else:
                self.start_next_song()

    def start_next_song(self):
        self.media_player.stateChanged.disconnect(self.start_next_song)  # Отключаем слот перед началом следующей песни
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.play_song(self.current_song_index)
    
    def play_previous_song(self):
        if self.playlist:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.stop()  # Остановить текущий трек
                self.media_player.stateChanged.connect(self.start_previous_song)  # Подключаем слот для начала предыдущей песни
            else:
                self.start_previous_song()

    def start_previous_song(self):
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.play_song(self.current_song_index)
        self.media_player.stateChanged.disconnect(self.start_previous_song)  # Отключаем слот после начала предыдущей песни

    def play_song(self, file):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()  # Остановка текущей песни, если она играет
        if isinstance(file, str):  # Проверяем, что file является строкой
            media_content = QMediaContent(QUrl.fromLocalFile(file))
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.play_button.setText("Pause")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayerApp()
    window.show()
    sys.exit(app.exec_())