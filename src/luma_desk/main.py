# $env:PYTHONPATH = "$PWD\src"
# python -m luma_desk.main

from PySide6.QtWidgets import QApplication

from luma_desk.ui.main_window import MainWindow
from luma_desk.utils.fonts import load_fonts

def main():
    app = QApplication([])

    # Load font files
    load_fonts()

    window = MainWindow() 
    window.showMaximized()

    # Start event loop
    app.exec()

if __name__ == "__main__":
    main()