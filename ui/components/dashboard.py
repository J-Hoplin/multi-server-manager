from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPointF, QMargins, QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter, QColor
from backend.system import SystemCommands

"""
TODO

- Optimize thread management
- Logging 어떻게 할지 고민, Sentry연동은 굳이인거같고..
"""


class SystemMonitorThread(QThread):
    cpu_updated = pyqtSignal(float)
    memory_updated = pyqtSignal(float)
    disk_updated = pyqtSignal(float, float)
    network_updated = pyqtSignal(float, float)

    def __init__(self, ssh_client, system_type):
        super().__init__()
        self.ssh = ssh_client
        self.system_type = system_type
        self._is_running = True

    def run(self):
        while self._is_running:
            try:
                stdin, stdout, stderr = self.ssh.exec_command(
                    SystemCommands.get_cpu_command(self.system_type)
                )
                cpu_usage = float(stdout.read().decode().strip())
                self.cpu_updated.emit(cpu_usage)
                memory_usage = SystemCommands.parse_memory_output(
                    self.system_type, self.ssh
                )
                self.memory_updated.emit(memory_usage)
                read_bytes, write_bytes = SystemCommands.parse_disk_io(
                    self.system_type, self.ssh
                )
                self.disk_updated.emit(read_bytes, write_bytes)
                rx_bytes, tx_bytes = SystemCommands.parse_network_traffic(
                    self.system_type, self.ssh
                )
                self.network_updated.emit(rx_bytes, tx_bytes)

            except Exception as e:
                print(f"Error in monitoring thread: {str(e)}")
            self.msleep(1000)

    def stop(self):
        self._is_running = False


class SystemMonitorWidget(QWidget):
    def __init__(self, ssh_client):
        super().__init__()
        self.ssh = ssh_client
        self.system_type = SystemCommands.get_system_type(ssh_client)
        # Max Proctoring Time: 30s
        self.cpu_data = []
        self.memory_data = []
        self.max_data_points = 30

        self.ui_init()
        self.thread_init()

    def thread_init(self):
        self.monitor_thread = SystemMonitorThread(self.ssh, self.system_type)
        self.monitor_thread.cpu_updated.connect(self.update_cpu)
        self.monitor_thread.memory_updated.connect(self.update_memory)
        self.monitor_thread.disk_updated.connect(self.update_disk)
        self.monitor_thread.network_updated.connect(self.update_network)
        self.monitor_thread.start()

    def ui_init(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # CPU
        cpu_widget = self.create_monitor_widget("[ CPU Usage ]")
        self.cpu_series = QLineSeries()
        self.cpu_chart = self.setup_chart("", self.cpu_series)
        self.cpu_chart_view = QChartView(self.cpu_chart)
        self.cpu_chart_view.setRenderHint(QPainter.Antialiasing)
        self.cpu_chart_view.setStyleSheet("background: transparent;")
        self.cpu_label = QLabel("Current: 0%")
        self.cpu_label.setAlignment(Qt.AlignRight)
        cpu_widget.layout().addWidget(self.cpu_chart_view)
        cpu_widget.layout().addWidget(self.cpu_label)
        grid_layout.addWidget(cpu_widget, 0, 0)

        # RAM
        memory_widget = self.create_monitor_widget("[ Memory Usage ]")
        self.memory_series = QLineSeries()
        self.memory_chart = self.setup_chart("", self.memory_series)
        self.memory_chart_view = QChartView(self.memory_chart)
        self.memory_chart_view.setRenderHint(QPainter.Antialiasing)
        self.memory_chart_view.setStyleSheet("background: transparent;")
        self.memory_label = QLabel("Current: 0%")
        self.memory_label.setAlignment(Qt.AlignRight)

        memory_widget.layout().addWidget(self.memory_chart_view)
        memory_widget.layout().addWidget(self.memory_label)
        grid_layout.addWidget(memory_widget, 0, 1)

        # Disk
        disk_widget = self.create_monitor_widget("[ Disk I/O ]")
        self.disk_read = QLabel("Read: 0 B/s")
        self.disk_write = QLabel("Write: 0 B/s")
        disk_widget.layout().addWidget(self.disk_read)
        disk_widget.layout().addWidget(self.disk_write)
        grid_layout.addWidget(disk_widget, 1, 0)

        # Network
        network_widget = self.create_monitor_widget("[ Network Traffic ]")
        self.network_rx = QLabel("Download: 0 B/s")
        self.network_tx = QLabel("Upload: 0 B/s")
        network_widget.layout().addWidget(self.network_rx)
        network_widget.layout().addWidget(self.network_tx)
        grid_layout.addWidget(network_widget, 1, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    # Functions for updating states
    def update_cpu(self, value):
        self.cpu_label.setText(f"Current: {value:.1f}%")
        self.update_chart_data(self.cpu_series, self.cpu_data, value)

    def update_memory(self, value):
        self.memory_label.setText(f"Current: {value:.1f}%")
        self.update_chart_data(self.memory_series, self.memory_data, value)

    def update_disk(self, read_bytes, write_bytes):
        self.disk_read.setText(f"Read: {self.format_bytes(read_bytes)}")
        self.disk_write.setText(f"Write: {self.format_bytes(write_bytes)}")

    def update_network(self, rx_bytes, tx_bytes):
        self.network_rx.setText(f"Download: {self.format_bytes(rx_bytes)}")
        self.network_tx.setText(f"Upload: {self.format_bytes(tx_bytes)}")

    def setup_chart(self, title, series):
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setTheme(QChart.ChartThemeDark)
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))

        axisX = QValueAxis()
        axisX.setRange(0, self.max_data_points)
        axisX.setLabelFormat("%d")
        axisX.setTitleText("Time (s)")
        axisX.setGridLineVisible(False)
        axisX.setMinorGridLineVisible(False)

        axisY = QValueAxis()
        axisY.setRange(0, 100)
        axisY.setLabelFormat("%d")
        axisY.setTitleText("Usage (%)")
        axisY.setGridLineVisible(False)
        axisY.setMinorGridLineVisible(False)

        chart.addAxis(axisX, Qt.AlignBottom)
        chart.addAxis(axisY, Qt.AlignLeft)

        series.attachAxis(axisX)
        series.attachAxis(axisY)
        pen = series.pen()
        pen.setWidth(2)
        pen.setColor(QColor("#4CAF50"))
        series.setPen(pen)

        chart.legend().hide()
        return chart

    def create_monitor_widget(self, title):
        widget = QWidget()
        widget.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        widget.setLayout(layout)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            color: #e0e0e0;
            padding-bottom: 5px;
        """
        )
        layout.addWidget(title_label)

        return widget

    def format_bytes(self, bytes):
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}/s"
            bytes /= 1024
        return f"{bytes:.2f} TB/s"

    def update_chart_data(self, series, data_list, new_value):
        data_list.append(new_value)
        if len(data_list) > self.max_data_points:
            data_list.pop(0)
        points = [QPointF(i, value) for i, value in enumerate(data_list)]
        series.replace(points)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
