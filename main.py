import sys
from ui.pages.root import ConnectionManager
from PyQt5.QtWidgets import QApplication
from ui.stylesheets.app_global import STYLE_GLOBAL

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_GLOBAL)
    ui = ConnectionManager()
    ui.show()
    sys.exit(app.exec_())
