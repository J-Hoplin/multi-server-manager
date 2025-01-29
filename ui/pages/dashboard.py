import os
import socket
import paramiko
from PyQt5.QtWidgets import (
    QProgressBar,
    QLabel,
    QSizePolicy,
    QPushButton,
    QMainWindow,
    QToolBar,
    QWidget,
    QVBoxLayout,
)
from manager.state.manager import ApplicationStateManger
from ui.stylesheets.toolbar import STYLE_TOOLBAR_BTN, STYLE_TOOLBAR
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from backend.system import SystemCommands
from ui.components.dashboard import SystemMonitorWidget


class SSHConnectionThread(QThread):
    finished = pyqtSignal(object, str)

    def __init__(self, host, port, username, password=None, key_file=None):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file

    def run(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.key_file:
                ssh_key = paramiko.RSAKey.from_private_key_file(self.key_file)
                ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=ssh_key,
                    timeout=15,
                )
            else:
                ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=15,
                )
            self.finished.emit(ssh_client, "")
        except paramiko.AuthenticationException:
            self.finished.emit(None, "Authentication failed")
        except paramiko.SSHException:
            self.finished.emit(None, "SSH Connection failed")
        except socket.error:
            self.finished.emit(None, "Out of Socket Connection")
        except Exception as e:
            self.finished.emit(None, f"{str(e)}")


class DashboardToolbar(QToolBar):
    def __init__(self):
        super().__init__()
        self.state_manager = ApplicationStateManger().get_manager()
        self.setStyleSheet(STYLE_TOOLBAR)
        self.setMovable(False)

    def render_dashboard_main_toolbar(self):
        self.clear()
        # Home Button
        home_btn = QPushButton()
        home_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/home.svg"))
        home_btn.setToolTip("Home")
        home_btn.setFixedSize(32, 32)
        home_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        home_btn.clicked.connect(self.home_btn_clicked)
        terminal_btn = QPushButton()
        terminal_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/terminal.svg"))
        terminal_btn.setToolTip("Open Terminal")
        terminal_btn.setFixedSize(32, 32)
        terminal_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        self.addWidget(home_btn)
        self.addWidget(terminal_btn)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        # Server Info Label
        self.server_info_label = QLabel()
        self.server_info_label.setStyleSheet(
            """
            color: #666;
            min-width: 300px;
        """
        )
        self.server_info_label.setFixedHeight(40)
        self.server_info_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.addWidget(self.server_info_label)

        # Interval 1s
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_server_info)
        self.timer.start(1000)
        self.update_server_info()

    def update_server_info(self):
        try:
            ssh = self.state_manager.get_state("ssh_connection")
            server_time = SystemCommands.get_server_time(ssh)
            ping = SystemCommands.get_ping(ssh)
            tz = SystemCommands.get_timezone(ssh)

            info_text = f"Server Time: ({tz}) {server_time}\nPing: {ping:.3f}ms"
            self.server_info_label.setText(info_text)
        except Exception as e:
            repr(e)
            self.server_info_label.setText("Unable to fetch server info")

    def home_btn_clicked(self):
        self.timer.stop()
        dashboard = self.state_manager.get_state("dashboard_main")
        dashboard.close()
        from ui.pages.root import ConnectionManager

        ConnectionManager().show()
        self.state_manager.remove_state("dashboard_main")


class MainDashboard(QMainWindow):
    def __init__(self, host, port, username, connection_type, password, key_file):
        super().__init__()
        self.state_manager = ApplicationStateManger().get_manager()
        self.state_manager.set_state("dashboard_main", self)

        self.setWindowTitle("Connecting...")
        self.setMinimumSize(450, 350)
        self.show_loading_screen()
        self.connection_thread = SSHConnectionThread(
            host, port, username, password, key_file
        )
        self.connection_thread.finished.connect(self.handle_connection_result)
        self.connection_thread.start()

    def show_loading_screen(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        loading_label = QLabel("Establishing SSH Connection...")
        loading_label.setStyleSheet(
            """
            QLabel {
                color: #2196F3;
                font-size: 16px;
                margin-bottom: 10px;
            }
        """
        )
        loading_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid rgba(33, 37, 43, 180);
                border-radius: 5px;
                text-align: center;
                background-color: rgba(33, 37, 43, 180);
                color: black;
            }
            QProgressBar::chunk {
                background-color: #FFD700;
            }
        """
        )
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFixedSize(300, 20)

        layout.addStretch()
        layout.addWidget(loading_label)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        layout.addStretch()

    def show_error_message(self, message):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        error_label = QLabel(f"Fail to make SSH connection:\n{message}")
        error_label.setStyleSheet(
            """
            QLabel {
                color: #ff0000;
                font-size: 16px;
                padding: 20px;
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
            }
        """
        )
        error_label.setAlignment(Qt.AlignCenter)
        home_button = QPushButton("Back to connection list")
        home_button.setStyleSheet(
            """
            QPushButton {
                background-color: gray;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
        """
        )
        home_button.clicked.connect(self.return_to_home)
        layout.addStretch()
        layout.addWidget(error_label)
        layout.addWidget(home_button, alignment=Qt.AlignCenter)
        layout.addStretch()

    def handle_connection_result(self, ssh_client, error_message):
        if ssh_client:
            self.state_manager.set_state("ssh_connection", ssh_client)
            self.ui_init()
        else:
            self.show_error_message(error_message)

    def return_to_home(self):
        self.close()
        from ui.pages.root import ConnectionManager

        ConnectionManager().show()

    def ui_init(self):
        # Dashboard UI settings
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(850, 650)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Toolbar settings
        self.toolbar = DashboardToolbar()
        self.addToolBar(self.toolbar)
        self.toolbar.render_dashboard_main_toolbar()

        # Create and add system monitor
        self.system_monitor = SystemMonitorWidget(
            self.state_manager.get_state("ssh_connection")
        )
        main_layout.addWidget(self.system_monitor)

        # Set dark theme stylesheet
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """
        )
