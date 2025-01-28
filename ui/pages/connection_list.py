from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from backend.connections import get_connections
from ui.components.connection_items import ConnectionItem


class ConnectionListPage(QWidget):
    reload_main_page_signal = pyqtSignal()

    def __init__(self, parent):
        super(ConnectionListPage, self).__init__(parent)
        self.ui_init()

    def ui_init(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # Scroll Area for connections
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)
        self.setup_connections()

    def setup_connections(self):
        # Connection Items
        connections = get_connections()
        self.scroll_widget = QWidget()
        self.connection_layout = QVBoxLayout(self.scroll_widget)
        self.connection_layout.setAlignment(Qt.AlignTop)
        self.connection_layout.setContentsMargins(0, 0, 0, 0)
        self.connection_layout.setSpacing(7)
        self.connection_items = ConnectionItem(connections, self.connection_layout)
        # Signal for delete success
        self.connection_items.delete_success_signal.connect(self.refresh_connections)
        self.connection_layout.addWidget(self.connection_items)
        self.scroll_area.setWidget(self.scroll_widget)

    def refresh_connections(self):
        # 기존 scroll widget 제거
        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        # 새로운 connection 설정
        self.setup_connections()

    def on_main_page_reload(self):
        self.reload_main_page_signal.emit()
