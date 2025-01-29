import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
)
from typing import List
from manager.state.manager import ApplicationStateManger
from backend.connections import delete_connection
from ui.stylesheets.toolbar import STYLE_TOOLBAR_BTN
from PyQt5.QtGui import QIcon
from ui.pages.update_connection import UpdateConnectionPage


class ConnectionItem(QWidget):
    render_update_signal = pyqtSignal(str)
    update_success_signal = pyqtSignal()
    delete_success_signal = pyqtSignal()

    def __init__(self, connections: List, parent_layout):
        super().__init__()
        self.connections = connections
        self.state_manager = ApplicationStateManger()
        self.ui_init()

    def ui_init(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        if self.connections:
            layout = QVBoxLayout()
            layout.setContentsMargins(7, 7, 7, 7)
            layout.setSpacing(7)

            for connection in self.connections:
                # Single Component Container
                self.connection_container = QWidget()
                self.connection_container.setStyleSheet(
                    """
                    QWidget {
                        background-color: gray;
                        border-radius: 8px;
                    }
                """
                )

                # Horizontal Layout for Inner Layouts
                connection_layout = QHBoxLayout()
                connection_layout.setContentsMargins(12, 12, 12, 12)
                connection_layout.setSpacing(7)

                # Left Side Layout
                info_layout = QVBoxLayout()

                # Connection Alias Label
                connection_alias_label = QLabel(connection[1])
                connection_alias_label.setStyleSheet(
                    """
                    QLabel {
                        font-weight: bold;
                        font-size: 18px;
                    }
                """
                )
                info_layout.addWidget(connection_alias_label)

                # Conatiner, Last Connected Container. Last Connected should invisible in case of no last connection
                connection_info_container = QWidget()
                connection_info_layout = QHBoxLayout(connection_info_container)
                connection_info_layout.setContentsMargins(0, 5, 0, 0)
                connection_info_layout.setSpacing(5)

                # Host 정보
                host_label = QLabel(f"Host: {connection[2]}")
                host_label.setStyleSheet(
                    """
                    QLabel {
                        font-size: 12px;
                        color: #d6d2ce;
                    }
                """
                )
                connection_info_layout.addWidget(host_label)

                # Last Connection 정보
                if connection[8]:
                    last_connection_label = QLabel(f"| Last Connected: {connection[8]}")
                    last_connection_label.setStyleSheet(
                        """
                        QLabel {
                            font-size: 12px;
                            color: #d6d2ce;
                        }
                    """
                    )
                    last_connection_label.setFixedWidth(150)
                    connection_info_layout.addWidget(last_connection_label)

                connection_info_layout.addStretch()
                info_layout.addWidget(connection_info_container)

                connection_layout.addLayout(info_layout)

                # Right Side Layout
                util_btn_layout = QHBoxLayout()
                util_btn_layout.setSpacing(5)

                # Play Button
                play_btn = QPushButton()
                play_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/play.svg"))
                play_btn.setToolTip("Connect")
                play_btn.setProperty("connection", connection)
                play_btn.setFixedSize(32, 32)
                play_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
                play_btn.clicked.connect(self.start_dashboard)
                util_btn_layout.addWidget(play_btn)

                # Edit button
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/edit.svg"))
                edit_btn.setToolTip("Edit Connection Info")
                edit_btn.setProperty("connection", connection)
                edit_btn.setFixedSize(32, 32)
                edit_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
                edit_btn.clicked.connect(self.render_update)
                util_btn_layout.addWidget(edit_btn)

                # Delete Button
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/delete.svg"))
                delete_btn.setToolTip("Delete Connection")
                delete_btn.setProperty("connection", connection)
                delete_btn.setFixedSize(32, 32)
                delete_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
                delete_btn.clicked.connect(self.delete_connection_info)
                util_btn_layout.addWidget(delete_btn)

                connection_layout.addLayout(util_btn_layout)

                self.connection_container.setLayout(connection_layout)
                layout.addWidget(self.connection_container)
            self.setLayout(layout)
        else:
            layout = QVBoxLayout()
            message_box = QLabel("No connections available")
            message_box.setAlignment(Qt.AlignCenter)
            message_box.setStyleSheet(
                """
                QLabel {
                    font-size: 16px;
                    color: #666;
                    margin: 20px;
                }
            """
            )
            layout.addWidget(message_box)
            layout.addStretch()
            self.setLayout(layout)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.setLayout(layout)

    def start_dashboard(self):
        btn = self.sender()
        connection_data = btn.property("connection")
        main = self.state_manager.get_state("application_main")
        main.close_and_render_dashboard(
            connection_data[2],
            connection_data[3],
            connection_data[4],
            connection_data[5],
            connection_data[6],
            connection_data[7],
        )

    def render_update(self):
        btn = self.sender()
        connection_id = btn.property("connection")[0]
        main = self.state_manager.get_state("application_main")
        update_page = UpdateConnectionPage(main, connection_id)
        main.render_update_page(update_page)

    def delete_connection_info(self):
        btn = self.sender()
        main = self.state_manager.get_state("application_main")
        connection_data = btn.property("connection")
        if connection_data:
            delete_connection(connection_data[0])
            main.rerender_page()
