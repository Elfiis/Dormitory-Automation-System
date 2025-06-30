import sys
from PyQt6.QtWidgets import QApplication
from arayuz import Pencere

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = Pencere()
    pencere.show()
    sys.exit(app.exec())
