import os
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QToolBar, QPushButton
from manager.state.manager import ApplicationStateManger
from PyQt5.QtGui import QIcon
from ui.stylesheets.toolbar import STYLE_TOOLBAR_BTN, STYLE_TOOLBAR
from ui.components.help import HelpItem
from ui.pages.create_connection import CreateNewConnectionPage
from ui.pages.connection_list import ConnectionListPage
from ui.pages.dashboard import MainDashboard


class ConnectionManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state_manager = ApplicationStateManger.get_manager()
        self.state_manager.set_state("application_main", self)
        self.state_manager.set_state("asset_path", f"{os.getcwd()}/assets")
        self.ui_init()

    def ui_init(self):
        self.setWindowTitle("Connections")
        self.setMinimumSize(450, 350)
        self.application_stack = QStackedWidget()
        self.setCentralWidget(self.application_stack)

        # Tool Bar in main page
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet(STYLE_TOOLBAR)
        self.addToolBar(self.toolbar)

        main_page_toolbar = self.render_main_page_toolbar()
        self.toolbar.clear()
        for btn in main_page_toolbar:
            self.toolbar.addWidget(btn)
        # Create New Connection Page
        self.connection_list_page = ConnectionListPage(self)
        self.create_new_connection_page = CreateNewConnectionPage(self)

        # Add pages to stack
        self.application_stack.addWidget(self.connection_list_page)
        self.application_stack.addWidget(self.create_new_connection_page)
        self.application_stack.setCurrentIndex(0)

    def open_help_popup(self):
        help_popup = HelpItem()
        help_popup.exec_()

    def render_main_page_toolbar(self):
        add_btn = QPushButton()
        add_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/add_box.svg"))
        add_btn.setToolTip("Add new connection")
        add_btn.setFixedSize(32, 32)
        add_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        add_btn.clicked.connect(self.create_connection)

        # Help Button
        help_btn = QPushButton()
        help_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/help.svg"))
        help_btn.setToolTip("Help")
        help_btn.setFixedSize(32, 32)
        help_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        help_btn.clicked.connect(self.open_help_popup)
        return [add_btn, help_btn]

    def render_create_edit_connection_toolbar(self):
        back_btn = QPushButton()
        back_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/back.svg"))
        back_btn.setToolTip("Back")
        back_btn.setFixedSize(32, 32)
        back_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        back_btn.clicked.connect(self.back_to_main_page)

        help_btn = QPushButton()
        help_btn.setIcon(QIcon(f"{os.getcwd()}/assets/icons/help.svg"))
        help_btn.setToolTip("Help")
        help_btn.setFixedSize(32, 32)
        help_btn.setStyleSheet(STYLE_TOOLBAR_BTN)
        help_btn.clicked.connect(self.open_help_popup)
        return [back_btn, help_btn]

    def render_update_page(self, update_page):
        for i in range(2, self.application_stack.count()):
            if isinstance(self.application_stack.widget(i), update_page.__class__):
                self.application_stack.removeWidget(self.application_stack.widget(i))
        self.toolbar.clear()
        for btn in self.render_create_edit_connection_toolbar():
            self.toolbar.addWidget(btn)
        self.update_page = update_page
        index = self.application_stack.addWidget(self.update_page)
        self.application_stack.setCurrentIndex(index)

    def create_connection(self):
        if self.application_stack.currentIndex() == 0:
            self.setWindowTitle("Create New Connection")
            self.toolbar.clear()
            for btn in self.render_create_edit_connection_toolbar():
                self.toolbar.addWidget(btn)
            self.application_stack.setCurrentIndex(1)

    def back_to_main_page(self):
        self.toolbar.clear()
        for btn in self.render_main_page_toolbar():
            self.toolbar.addWidget(btn)
        self.application_stack.setCurrentIndex(0)

    def rerender_page(self):
        # Signal Emit Function for connection save
        self.application_stack.setCurrentIndex(0)
        self.toolbar.clear()
        for btn in self.render_main_page_toolbar():
            self.toolbar.addWidget(btn)
        self.connection_list_page.refresh_connections()

    def close_and_render_dashboard(
        self, host, port, username, connection_type, password, key_file
    ):
        self.close()
        self.main_dashboard = MainDashboard(
            host, port, username, connection_type, password, key_file
        )
        # Remove state for illeagal access
        self.state_manager.remove_state("application_main")
        self.main_dashboard.show()
