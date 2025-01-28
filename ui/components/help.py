from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog


class HelpItem(QDialog):
    def __init__(self):
        super().__init__()
        self.ui_init()

    def ui_init(self):
        self.setWindowTitle("Contact here for help")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        message = QLabel(
            "If you need some help or need to report bug please contact here."
        )
        message.setWordWrap(True)
        message.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #2c3e50;
            }
        """
        )
        layout.addWidget(message)
        email_label = QLabel("Email: hoplin.dev@gmail.com")
        email_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                background-color: transparent;
            }
        """
        )
        layout.addWidget(email_label)
        github_link = QLabel()
        github_link.setText('<a href="https://github.com/J-Hoplin">Github</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #2980b9;
                background-color: transparent;
            }
            QLabel:hover {
                color: #3498db;
            }
        """
        )
        layout.addWidget(github_link)
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet(
            """
            QDialog {
                background-color: white;
                border: 1px solid #3498db;
            }
        """
        )
