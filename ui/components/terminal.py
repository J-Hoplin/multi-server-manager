from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication
from PyQt5.QtCore import QTimer, Qt, QEvent
from PyQt5.QtGui import QTextCursor
import socket
import re
import threading
import queue

"""
Code are so messed up...

Also I need some additional knowlede
"""


class TerminalWidget(QWidget):
    def __init__(self, ssh_client):
        super().__init__()
        self.ssh_client = ssh_client
        self.channel = None
        self.output_queue = queue.Queue()
        self.running = False
        self.terminal_size = (80, 24)
        self.clipboard = QApplication.clipboard()
        self.setup_ui()
        self.setup_terminal()

    def copy_selection(self):
        selected_text = self.terminal.textCursor().selectedText()
        if selected_text:
            self.clipboard.setText(selected_text)

    def paste_clipboard(self):
        text = self.clipboard.text()
        if text and self.channel:
            for line in text.splitlines():
                self.channel.send(line.encode("utf-8"))
                self.channel.send(b"\r")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.terminal = QTextEdit()
        self.terminal.setFontPointSize(11)
        self.terminal.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                padding: 5px;
            }
        """
        )
        self.terminal.setLineWrapMode(QTextEdit.NoWrap)
        self.terminal.setCursorWidth(8)
        layout.addWidget(self.terminal)

        self.terminal.installEventFilter(self)

        self.output_timer = QTimer()
        self.output_timer.timeout.connect(self.process_output_queue)
        self.output_timer.start(50)

        self.terminal.setFocus()

    def setup_terminal(self):
        try:
            cols, rows = self.terminal_size
            self.channel = self.ssh_client.invoke_shell(
                term="xterm-256color", width=cols, height=rows
            )
            self.channel.settimeout(0.1)

            # SSH Pseudo Channel Configs
            init_commands = [
                "export TERM=xterm-256color",
                "export LANG=en_US.UTF-8",
                "export LC_ALL=en_US.UTF-8",
                f"stty columns {cols} rows {rows}",
                "stty -icanon -echo",
                "export PS1='\\u@\\h:\\w\\$ '",
            ]

            for cmd in init_commands:
                self.channel.send(f"{cmd}\n".encode("utf-8"))

            self.running = True
            self.output_thread = threading.Thread(target=self.read_output)
            self.output_thread.daemon = True
            self.output_thread.start()

        except Exception as e:
            self.terminal.append(f"Error setting up terminal: {str(e)}")

    def eventFilter(self, obj, event):
        if obj == self.terminal and event.type() == QEvent.KeyPress:
            if (
                not self.channel
                or not self.channel.get_transport()
                or not self.channel.get_transport().is_active()
            ):
                return True
            key = event.key()
            modifiers = event.modifiers()
            text = event.text()
            if modifiers & Qt.ControlModifier:
                if key == Qt.Key_C and self.terminal.textCursor().hasSelection():
                    self.copy_selection()
                    return True
                elif key == Qt.Key_V:
                    self.paste_clipboard()
                    return True
                """
                1. SIGINT
                2. EOF
                3. SIGTSTP
                4. SIGQUIT
                """
                ctrl_chars = {
                    Qt.Key_C: b"\x03",
                    Qt.Key_D: b"\x04",
                    Qt.Key_Z: b"\x1a",
                    Qt.Key_Backslash: b"\x1c",
                }
                if key in ctrl_chars:
                    self.channel.send(ctrl_chars[key])
                    return True

            # Special Character Handler
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self.channel.send(b"\r")
                return True
            elif key == Qt.Key_Backspace:
                self.channel.send(b"\x7f")
                cursor = self.terminal.textCursor()
                cursor.deletePreviousChar()
                return True
            elif key == Qt.Key_Tab:
                self.channel.send(b"\t")
                return True
            elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left):
                direction_keys = {
                    Qt.Key_Up: b"\x1b[A",
                    Qt.Key_Down: b"\x1b[B",
                    Qt.Key_Right: b"\x1b[C",
                    Qt.Key_Left: b"\x1b[D",
                }
                self.channel.send(direction_keys[key])
                return True

            # Command Input
            if text and not modifiers & (Qt.ControlModifier | Qt.AltModifier):
                self.channel.send(text.encode("utf-8"))
                # Display typed text locally in the terminal widget
                cursor = self.terminal.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(text)
                self.terminal.setTextCursor(cursor)
                return True

            return True

        return super().eventFilter(obj, event)

    def process_output_queue(self):
        while not self.output_queue.empty():
            output = self.output_queue.get_nowait()
            try:
                decoded_output = output.decode("utf-8", errors="replace")

                # Clear terminal
                if (
                    "\x1b[H\x1b[2J" in decoded_output
                    or "\x1b[2J" in decoded_output
                    or "\x0c" in decoded_output
                ):
                    self.terminal.clear()
                    continue
                # ANSI format escape
                ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
                cleaned_output = ansi_escape.sub("", decoded_output)
                # Terminal Output
                cursor = self.terminal.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertText(cleaned_output)
                self.terminal.setTextCursor(cursor)
                self.terminal.ensureCursorVisible()

            except Exception as e:
                print(f"Error processing output: {str(e)}")

    def read_output(self):
        while self.running:
            if self.channel and self.channel.recv_ready():
                try:
                    output = self.channel.recv(4096)
                    if output:
                        self.output_queue.put(output)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.output_queue.put(f"Error reading output: {str(e)}".encode())
                    break
            threading.Event().wait(0.05)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if (
            self.channel
            and self.channel.get_transport()
            and self.channel.get_transport().is_active()
        ):
            try:
                font_metrics = self.terminal.fontMetrics()
                char_width = font_metrics.averageCharWidth()
                char_height = font_metrics.height()

                cols = max(80, self.terminal.width() // char_width)
                rows = max(24, self.terminal.height() // char_height)

                self.terminal_size = (cols, rows)
                self.channel.resize_pty(width=cols, height=rows)
                self.channel.send(f"stty cols {cols} rows {rows}\n".encode("utf-8"))
            except Exception as e:
                print(f"Error resizing terminal: {str(e)}")

    def closeEvent(self, event):
        self.running = False
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=1.0)
        if self.channel:
            self.channel.close()
        super().closeEvent(event)

    def clear(self):
        # Event Handler for clear tty
        self.terminal.clear()
