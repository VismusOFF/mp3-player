from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QTabBar, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from playlist_app import PlaylistApp
from playlist_manager import PlaylistManagerApp
from tracks_manager import SongViewer
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("ZXCmusic")
        self.setWindowIcon(QIcon('icons/main.png'))
        self.setGeometry(100, 100, 400, 700)

        tab_widget = QTabWidget(self)

        self.playlist_app = PlaylistApp(self)
        self.playlistmanager = PlaylistManagerApp(self)
        self.songviewer = SongViewer(self)  # New SongViewer instance

        icon_home = QIcon('icons/home.png')
        icon_home.addPixmap(icon_home.pixmap(50, 50))  # Set icon size

        icon_playlist = QIcon('icons/playlist.png')
        icon_playlist.addPixmap(icon_playlist.pixmap(50, 50))  # Set icon size

        icon_search = QIcon('icons/search.png')  # New icon for the search tab
        icon_search.addPixmap(icon_search.pixmap(50, 50))  # Set icon size

        tab_widget.addTab(self.playlist_app, "")
        tab_widget.addTab(self.playlistmanager, "")
        tab_widget.addTab(self.songviewer, "")  # New tab added

        tab_bar = tab_widget.tabBar()
        tab_bar.setIconSize(icon_home.availableSizes()[0])

        tab_widget.setTabIcon(0, icon_home)
        tab_widget.setTabIcon(1, icon_playlist)
        tab_widget.setTabIcon(2, icon_search)  # Set icon for the new tab

        tab_bar.setStyleSheet("QTabBar::tab {background: black; color: white;} QTabBar::tab:selected {background: black;}")
        tab_widget.setStyleSheet("QTabWidget::pane {background: black;}")

        self.setCentralWidget(tab_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    css_file = open('styles.css', 'r')
    style = css_file.read()
    css_file.close()

    app.setStyleSheet(style)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())