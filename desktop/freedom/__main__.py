import sys

from freedom import engine_update

# Prima di qualunque import di yt_dlp: l'eventuale motore aggiornato ha la precedenza su quello incluso.
engine_update.bootstrap()


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from freedom.theme import Fonts, app_icon, stylesheet
    from freedom.ui import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Freedom")
    app.setOrganizationName("Freedom")
    app.setDesktopFileName("freedom")
    app.setWindowIcon(app_icon())
    Fonts.load()
    app.setStyleSheet(stylesheet())
    win = MainWindow()
    win.show()
    for arg in sys.argv[1:]:
        if arg.startswith(("http://", "https://")):
            win.download_page.add_urls(arg)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
