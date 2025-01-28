import os
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from ui.stylesheets.fonts import (
    STYLE_PASS_MESSAGE,
    STYLE_ERROR_MESSAGE,
    STYLE_PENDING_MESSAGE,
)
from backend.connections import test_ssh_connection, save_connection


class CreateNewConnectionPage(QWidget):
    save_success_signal = pyqtSignal()

    def __init__(self, parent):
        super(CreateNewConnectionPage, self).__init__(parent)
        self.ui_init()

    def ui_init(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setSpacing(7)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Base Connection Information: Name, Host, Port, Username
        self.connection_name = QLineEdit()
        self.host = QLineEdit()
        self.port = QLineEdit()
        self.port.setPlaceholderText("Default port is 22")
        self.username = QLineEdit()

        # Connection Type
        self.connection_type = QComboBox()
        self.connection_type.addItems(["password", "key"])
        self.connection_type.currentTextChanged.connect(self.on_connection_type_changed)

        # Password Field
        self.password_container = QWidget()
        self.password_layout = QHBoxLayout(self.password_container)
        self.password_layout.setContentsMargins(0, 0, 0, 0)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password_visibility_btn = QPushButton()
        self.password_visibility_btn.setIcon(
            QIcon(f"{os.getcwd()}/assets/icons/visible.svg")
        )
        self.password_visibility_btn.setFixedSize(32, 32)
        self.password_visibility_btn.clicked.connect(self.toggle_password_visibility)
        self.password_layout.addWidget(self.password)
        self.password_layout.addWidget(self.password_visibility_btn)

        # Key file selection
        self.key_file_container = QWidget()
        key_file_layout = QHBoxLayout(self.key_file_container)
        key_file_layout.setContentsMargins(0, 0, 0, 0)
        self.key_file_display = QLineEdit()
        self.key_file_display.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_key_file)
        key_file_layout.addWidget(self.key_file_display)
        key_file_layout.addWidget(self.browse_button)
        self.key_file_container.hide()

        # Labels and forms layout
        label_alignment_rule = Qt.AlignRight | Qt.AlignVCenter
        fields = [
            ("Connection Name", self.connection_name),
            ("Host", self.host),
            ("Port", self.port),
            ("Username", self.username),
            ("Connection Type", self.connection_type),
        ]

        for row, (label_text, widget) in enumerate(fields):
            label = QLabel(label_text)
            label.setAlignment(label_alignment_rule)
            label.setStyleSheet(
                """
                QLabel {
                    font-weight: bold;
                    font-size: 13px;
                }
            """
            )
            self.main_layout.addWidget(label, row, 0)
            self.main_layout.addWidget(widget, row, 1)

        # Password, Keyfile container
        self.password_label = QLabel("Password")
        self.password_label.setStyleSheet(
            """
                QLabel {
                    font-weight: bold;
                    font-size: 13px;
                }
        """
        )
        self.password_label.setAlignment(label_alignment_rule)
        self.key_file_label = QLabel("Key File")
        self.key_file_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 13px;
            }
        """
        )
        self.key_file_label.setAlignment(label_alignment_rule)
        self.key_file_label.hide()

        # Password/Key File
        self.main_layout.addWidget(self.password_label, 5, 0)
        self.main_layout.addWidget(self.password_container, 5, 1)
        self.main_layout.addWidget(self.key_file_label, 5, 0)
        self.main_layout.addWidget(self.key_file_container, 5, 1)

        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(5)
        # Test Connection
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_connection)

        # Save Connection
        self.save_btn = QPushButton("Save Connection")
        self.save_btn.clicked.connect(self.save_connection)

        # Add buttons to layout
        self.buttons_layout.addWidget(self.test_connection_btn)
        self.buttons_layout.addWidget(self.save_btn)

        # Error Message Container
        self.message_container = QWidget()
        self.message_container.hide()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(0, 0, 0, 0)
        self.message_layout.setSpacing(5)
        self.message_label = QLabel("Message")
        self.message_label.setWordWrap(True)
        self.message_layout.addWidget(self.message_label)

        spacer = QWidget()
        spacer.setMinimumHeight(20)
        self.main_layout.addWidget(spacer, 6, 0, 1, 2)
        self.main_layout.addWidget(self.buttons_container, 7, 0, 1, 2)
        self.main_layout.addWidget(self.message_container, 8, 0, 1, 2)
        self.main_layout.setColumnStretch(1, 1)

    def on_connection_type_changed(self, connection_type):
        if connection_type == "password":
            self.password_container.show()
            self.password_label.show()
            self.key_file_label.hide()
            self.key_file_container.hide()
        else:
            self.password_container.hide()
            self.password_label.hide()
            self.key_file_label.show()
            self.key_file_container.show()

    def toggle_password_visibility(self):
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.password_visibility_btn.setIcon(
                QIcon(f"{os.getcwd()}/assets/icons/non-visible.svg")
            )
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.password_visibility_btn.setIcon(
                QIcon(f"{os.getcwd()}/assets/icons/visible.svg")
            )

    def browse_key_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select SSH Key File")
        if file_name:
            self.key_file_display.setText(os.path.basename(file_name))
            self.key_file_display.setProperty("full_path", file_name)

    def set_message_text(self, message, status):
        if status == "error":
            self.message_label.setStyleSheet(STYLE_ERROR_MESSAGE)
        elif status == "pass":
            self.message_label.setStyleSheet(STYLE_PASS_MESSAGE)
        else:  # Pending
            self.message_label.setStyleSheet(STYLE_PENDING_MESSAGE)
        self.message_label.setText(message)
        self.message_container.show()

    def parse_form(self):
        name = self.connection_name.text()
        host = self.host.text()
        port = self.port.text() if self.port.text() else 22
        username = self.username.text()
        connection_type = self.connection_type.currentText()
        password = self.password.text() if connection_type == "password" else None
        key_file = (
            self.key_file_display.property("full_path")
            if connection_type == "key"
            else None
        )

        non_empty_fields = [
            {"field": "Connection Name", "value": name},
            {"field": "Host", "value": host},
            {"field": "Port", "value": port},
            {"field": "Username", "value": username},
        ]
        if connection_type == "password":
            non_empty_fields.append({"field": "Password", "value": password})
        else:
            non_empty_fields.append({"field": "Key File", "value": key_file})
        empty_fields = []
        for field in non_empty_fields:
            if not field["value"]:
                empty_fields.append(field["field"])
        if empty_fields:
            self.set_message_text(
                f"Validation Fail: {', '.join(empty_fields)} should not be empty",
                "error",
            )
            return None
        return {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "connection_type": connection_type,
            "password": password,
            "key_file": key_file,
        }

    def test_connection(self):
        connection_data = self.parse_form()
        if not connection_data:
            return
        test_result, message = test_ssh_connection(
            host=connection_data["host"],
            port=connection_data["port"],
            username=connection_data["username"],
            password=connection_data["password"],
            key_file=connection_data["key_file"],
        )
        if test_result:
            self.set_message_text("Connection Successful!", "pass")
        else:
            self.set_message_text(f"Connection Failed: {message}", "error")

    def save_connection(self):
        connection_data = self.parse_form()
        if not connection_data:
            return
        save_connection(
            connection_data["name"],
            connection_data["host"],
            connection_data["port"],
            connection_data["username"],
            connection_data["connection_type"],
            connection_data["password"],
            connection_data["key_file"],
        )
        self.save_success_signal.emit()
