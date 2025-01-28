from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from backend.connections import get_connections
from ui.components.connection_items import ConnectionItem


class ConnectionListPage(QWidget):
    def __init__(self, parent):
        super(ConnectionListPage, self).__init__(parent)
        self.ui_init()

    def ui_init(self):
        self.main_layout = QVBoxLayout(self)  # Should connect layout to widget itself
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # Scroll Area for connections
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)
        # Connection Items
        connections = get_connections()
        self.scroll_widget = QWidget()
        self.connection_layout = QVBoxLayout(self.scroll_widget)
        self.connection_layout.setAlignment(Qt.AlignTop)
        self.connection_layout.setContentsMargins(0, 0, 0, 0)
        self.connection_layout.setSpacing(7)
        self.connection_items = ConnectionItem(connections, self.connection_layout)
        self.connection_layout.addWidget(self.connection_items)
        self.scroll_area.setWidget(self.scroll_widget)

    def refresh_connections(self):
        self.connection_items = ConnectionItem(
            get_connections(), self.connection_layout
        )
