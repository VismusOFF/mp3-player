from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from playlist_app import PlaylistApp
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("ZXCmusic")
        self.setWindowIcon(QIcon('icons/main.png'))
        self.setGeometry(100, 100, 300, 300)

        self.playlist_app = PlaylistApp(self)

        self.setCentralWidget(self.playlist_app)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    css_file = open('styles.css', 'r')  # Открываем CSS файл
    style = css_file.read()            # Читаем содержимое файла
    css_file.close()                   # Закрываем файл

    app.setStyleSheet(style)           # Применяем стили из CSS файла ко всему приложению

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())