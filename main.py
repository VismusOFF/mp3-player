from PyQt5.QtWidgets import QApplication
from playlist_app import PlaylistApp
from music_player import MusicPlayerApp

if __name__ == "__main__":
    app = QApplication([])

    playlist_app = PlaylistApp()
    music_player_app = MusicPlayerApp()

    # Подключаем сигнал и слот
    playlist_app.playlist_selected.connect(music_player_app.receive_playlist)

    playlist_app.show()
    music_player_app.show()

    app.exec_()